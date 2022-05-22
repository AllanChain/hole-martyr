import asyncio
import json
import time

import httpx
from loguru import logger
from sqlalchemy.dialects.sqlite import insert

from .database import database, holes
from .settings import settings

UA_STRING = "Mozilla/5.0 (X11; Linux x86_64; rv:100.0) Gecko/20100101 Firefox/100.0"


async def fetch_page(page: int):
    async with httpx.AsyncClient() as client:
        r = await client.get(
            "https://pkuhelper.pku.edu.cn/services/pkuhole/api.php",
            params={
                "action": "getlist",
                "p": page,
                "PKUHelperAPI": "3.0",
                "jsapiver": "201027113050-459074",
                "user_token": settings.user_token,
            },
            headers={
                "Referer": "https://pkuhelper.pku.edu.cn/hole/",
                "User-Agent": UA_STRING,
            },
        )
        try:
            return [
                {
                    "pid": int(hole["pid"]),
                    "text": hole["text"],
                    "created_at": int(hole["timestamp"]),
                    "like_count": int(hole["likenum"]),
                    "reply_count": int(hole["reply"]),
                    "image": hole["url"],
                }
                for hole in r.json()["data"]
            ]
        except json.decoder.JSONDecodeError as e:
            if "502" in r.text:  # Server is busy
                await asyncio.sleep(1)
                return await fetch_page(page)
            logger.error("Cannot decode json: {}", r.text)
            raise e from None


async def store_pages():
    update_deleted_query = insert(holes)
    update_deleted_query = update_deleted_query.on_conflict_do_update(
        index_elements=[holes.c.pid],
        set_={
            "like_count": update_deleted_query.excluded.like_count,
            "reply_count": update_deleted_query.excluded.reply_count,
        },
    )
    all_values = []
    for page in range(1, settings.scan_page + 1):
        values = await fetch_page(page)

        await database.execute_many(update_deleted_query, values)
        all_values.extend(values)

    # Scan all_values to find discontinuous hole pids which means deletion
    previous_pid = all_values[0]["pid"]
    deleted_pids = []
    for hole in all_values:
        current_pid = hole["pid"]
        if previous_pid - current_pid > 1:
            deleted_pids.extend(range(current_pid + 1, previous_pid))
        previous_pid = current_pid

    # Update deleted_at field of deleted_pids if they haven't been marked
    deleted_at = int(time.time())
    await database.execute_many(
        insert(holes).on_conflict_do_update(
            index_elements=[holes.c.pid],
            set_={"deleted_at": deleted_at},
            where=holes.c.deleted_at == None,
        ),
        [{"pid": pid, "deleted_at": deleted_at} for pid in deleted_pids],
    )

    newly_deleted = await database.fetch_all(
        holes.select().where(holes.c.deleted_at == deleted_at)
    )
    newly_deleted = [dict(h) for h in newly_deleted]
    return newly_deleted

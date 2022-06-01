import asyncio
import json
import time

import httpx
from loguru import logger
from sqlalchemy import func, select
from sqlalchemy.dialects.sqlite import insert

from .database import comments_table, database, holes_table
from .dynamic_settings import dynamic_settings
from .settings import settings

API_URL = "https://pkuhelper.pku.edu.cn/services/pkuhole/api.php"
UA_STRING = "Mozilla/5.0 (X11; Linux x86_64; rv:100.0) Gecko/20100101 Firefox/100.0"
COMMON_PARAMS = {
    "PKUHelperAPI": "3.0",
    "jsapiver": "201027113050-459074",
    "user_token": settings.user_token,
}
HEADERS = {
    "Referer": "https://pkuhelper.pku.edu.cn/hole/",
    "User-Agent": UA_STRING,
}


async def fetch_page(page: int):
    async with httpx.AsyncClient() as client:
        r = await client.get(
            API_URL,
            params={"action": "getlist", "p": page, **COMMON_PARAMS},
            headers=HEADERS,
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


async def fetch_comments(pid: int):
    async with httpx.AsyncClient() as client:
        r = await client.get(
            API_URL,
            params={"action": "getcomment", "pid": pid, **COMMON_PARAMS},
            headers=HEADERS,
        )
        try:
            return [
                {
                    "cid": int(comment["cid"]),
                    "pid": int(comment["pid"]),
                    "text": comment["text"],
                    "created_at": int(comment["timestamp"]),
                }
                for comment in r.json()["data"]
            ]
        except json.decoder.JSONDecodeError as e:
            if "502" in r.text:  # Server is busy
                await asyncio.sleep(1)
                return await fetch_comments(pid)
            logger.error("Cannot decode json: {}", r.text)
            raise e from None


async def store_pages():
    insert_query = insert(holes_table)
    insert_query = insert_query.on_conflict_do_update(
        index_elements=[holes_table.c.pid],
        set_={
            "like_count": insert_query.excluded.like_count,
            "reply_count": insert_query.excluded.reply_count,
        },
    )
    all_values = []
    for page in range(1, dynamic_settings.scan_page + 1):
        values = await fetch_page(page)

        await database.execute_many(insert_query, values)
        all_values.extend(values)

    # Fetch comments for holes with more than 10 replies
    for hole in all_values:
        if hole["reply_count"] >= 10:
            try:
                fetched_reply_count = (
                    await database.fetch_one(
                        select(func.count())
                        .select_from(comments_table)
                        .where(comments_table.c.pid == hole["pid"])
                    )
                )[0]
                if (
                    fetched_reply_count is None
                    or hole["reply_count"] - fetched_reply_count > 10
                ):
                    await database.execute_many(
                        insert(comments_table).on_conflict_do_nothing(
                            index_elements=[comments_table.c.cid]
                        ),
                        await fetch_comments(hole["pid"]),
                    )
            except Exception as e:
                logger.error("Fail to fetch replies from {}: {}", hole.get("pid"), e)

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
        insert(holes_table).on_conflict_do_update(
            index_elements=[holes_table.c.pid],
            set_={"deleted_at": deleted_at},
            where=holes_table.c.deleted_at == None,
        ),
        [{"pid": pid, "deleted_at": deleted_at} for pid in deleted_pids],
    )

    newly_deleted = await database.fetch_all(
        holes_table.select().where(holes_table.c.deleted_at == deleted_at)
    )
    newly_deleted = [dict(h) for h in newly_deleted]
    return newly_deleted

import asyncio
import json
import os
import random
import sys
import time

import httpx
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from loguru import logger
from pydantic import BaseModel
from sse_starlette.sse import EventSourceResponse, ServerSentEvent

from .database import comments, database, engine, holes, metadata
from .fetcher import store_pages
from .message import MessageAnnouncer
from .settings import settings

app = FastAPI()
announcer = MessageAnnouncer()

allowed_origin = "http://localhost:3000"
app.add_middleware(
    CORSMiddleware,
    allow_origins=[allowed_origin],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

metadata.create_all(engine)
logger.remove()
logger.add(
    sys.stderr,
    colorize=True,
    format="<lvl>{level:9}</lvl> <blue>{time:HH:mm:ss.SS}</blue> {message}",
    level="INFO",
)


schedule_next = time.time() + settings.initial_delay


@app.on_event("startup")
async def startup():
    await database.connect()
    logger.info("App started")


@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()


@app.on_event("startup")
async def bg_task() -> None:
    async def loop():
        global schedule_next
        await asyncio.sleep(settings.initial_delay)
        interval = settings.initial_interval
        while True:
            announcer.announce({"event": "scanstart"})
            try:
                newly_deleted = await store_pages()
            except httpx.ConnectTimeout:
                announcer.announce({"event": "fetcherror", "data": "timeout"})
                await asyncio.sleep(1)
                continue
            except asyncio.CancelledError:
                pass
            except:
                import traceback

                announcer.announce(
                    {"event": "fetcherror", "data": traceback.format_exc()}
                )
                traceback.print_exc()
                await asyncio.sleep(1)
                continue

            uncaught_deletion = 0
            for hole in newly_deleted:
                if hole["text"] is None:
                    uncaught_deletion += 1
                announcer.announce({"event": "deletion", "data": {"hole": hole}})

            upper_gap = settings.max_interval - interval
            lower_gap = interval - settings.min_interval
            if uncaught_deletion or len(newly_deleted) > 3:
                interval -= random.uniform(lower_gap / 5, lower_gap / 4)
            else:
                interval += random.uniform(-lower_gap / 8, upper_gap / 6)

            announcer.announce(
                {"event": "scandone", "data": {"next": time.time() + interval}}
            )
            logger.debug("Done scan")
            schedule_next = time.time() + interval
            await asyncio.sleep(interval)

    asyncio.ensure_future(loop())


@app.get("/stream")
async def sse(request: Request):
    async def event_source():
        messages = announcer.listen()
        try:
            while True:
                disconnected = await request.is_disconnected()
                if disconnected:
                    logger.debug("Stream disconnecting")
                    break
                msg = await messages.get()
                logger.info("Sending {}", str(msg))
                yield ServerSentEvent(
                    json.dumps(msg.get("data")), event=msg.get("event")
                )
            logger.debug("Stream disconnected")
        except asyncio.CancelledError:
            logger.debug("Stream cancelled")

    return EventSourceResponse(event_source())


class NextResponse(BaseModel):
    next: float


@app.get("/next", response_model=NextResponse)
async def next_scan():
    return {"next": schedule_next}


@app.get("/recent-deletions")
async def recent_deletions():
    deletions = await database.fetch_all(
        holes.select()
        .where(holes.c.deleted_at != None)
        .order_by(holes.c.pid.desc())
        .limit(10)
    )
    return [dict(d) for d in deletions]


@app.get("/hole/{pid}/comments")
async def hole_comments(pid: int):
    replies = await database.fetch_all(comments.select().where(comments.c.pid == pid))
    return [dict(c) for c in replies]


if os.path.exists("dist"):
    app.mount("/", StaticFiles(directory="dist", html=True), name="static")

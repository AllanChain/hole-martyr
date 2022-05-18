import asyncio
import json
import random
import time

import httpx
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sse_starlette.sse import EventSourceResponse, ServerSentEvent

from api.fetcher import store_pages

from .database import database, engine, holes, metadata
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

schedule_next = time.time() + settings.initial_delay


@app.on_event("startup")
async def startup():
    await database.connect()


@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()


@app.get("/")
async def root():
    return {"message": "Hello World"}


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
            if uncaught_deletion:
                interval -= random.uniform(lower_gap / 5, lower_gap / 4)
            else:
                interval += random.uniform(-lower_gap / 8, upper_gap / 6)

            announcer.announce(
                {"event": "scandone", "data": {"next": time.time() + interval}}
            )
            print("Done scan", flush=True)
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
                print(disconnected, flush=True)
                if disconnected:
                    print("Disconnecting", flush=True)
                    break
                msg = await messages.get()
                print(msg, flush=True)
                yield ServerSentEvent(
                    json.dumps(msg.get("data")), event=msg.get("event")
                )
            print("Disconnected", flush=True)
        except asyncio.CancelledError:
            print("Cancelled", flush=True)

    return EventSourceResponse(
        event_source(),
        headers={
            "Access-Control-Allow-Origin": allowed_origin,
            "Access-Control-Allow-Methods": "*",
            "Access-Control-Allow-Headers": "*",
        },
    )


class NextResponse(BaseModel):
    next: float


@app.get("/next", response_model=NextResponse)
async def next_scan():
    return {"next": schedule_next}


@app.get("/recent-deletions")
async def recent_deletions():
    deletions = await database.fetch_all(
        holes.select().order_by(holes.c.deleted_at.desc()).limit(10)
    )
    return [dict(d) for d in deletions]

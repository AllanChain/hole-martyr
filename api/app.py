import asyncio
import json
import random
import time

from fastapi import FastAPI, Request
from pydantic import BaseModel
from sse_starlette.sse import EventSourceResponse, ServerSentEvent

from api.fetcher import store_pages

from .database import database, engine, metadata
from .message import MessageAnnouncer
from .settings import settings

app = FastAPI()
announcer = MessageAnnouncer()

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
            except:
                import traceback

                announcer.announce({"event": "error", "data": traceback.format_exc()})
                traceback.print_exc()
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
            while not await request.is_disconnected():
                msg = await messages.get()
                print(msg, flush=True)
                yield ServerSentEvent(
                    json.dumps(msg.get("data")), event=msg.get("event")
                )
            print("Disconnected", flush=True)
        except asyncio.CancelledError:
            print("Cancelled", flush=True)

    return EventSourceResponse(event_source())


class NextResponse(BaseModel):
    next: float


@app.get("/next", response_model=NextResponse)
async def next_scan():
    return {"next": schedule_next}

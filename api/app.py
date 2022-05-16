import asyncio
import random

from fastapi import FastAPI, Request
from sse_starlette.sse import EventSourceResponse

from api.fetcher import store_pages

from .database import database, engine, metadata
from .message import MessageAnnouncer
from .settings import settings

app = FastAPI()
announcer = MessageAnnouncer()

metadata.create_all(engine)


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
# @repeat_every(seconds=settings.scan_interval)
async def bg_task() -> None:
    async def loop():
        await asyncio.sleep(1)
        interval = settings.initial_interval
        while True:
            announcer.announce({"type": "scan-start"})
            try:
                newly_deleted = await store_pages()
            except:
                import traceback

                announcer.announce(traceback.format_exc())

            uncaught_deletion = 0
            for hole in newly_deleted:
                if hole["text"] is None:
                    uncaught_deletion += 1
                announcer.announce({"type": "deletion", "hole": hole})
            if uncaught_deletion:
                gap = interval - settings.min_interval
                interval -= random.uniform(gap / 5, gap / 4)
            else:
                gap = settings.max_interval - interval
                interval += random.uniform(-gap / 8, gap / 6)

            announcer.announce({"type": "scan-done", "next": interval})
            await asyncio.sleep(interval)

    asyncio.ensure_future(loop())


@app.get("/stream")
async def sse(request: Request):
    async def event_source():
        messages = announcer.listen()
        while True:
            msg = await messages.get()
            yield msg

    return EventSourceResponse(event_source())

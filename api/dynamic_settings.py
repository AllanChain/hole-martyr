from loguru import logger
from pydantic import BaseModel
from sqlalchemy.dialects.sqlite import insert

from .database import database, settings_table


class DynamicSettings(BaseModel):
    scan_page: int
    "Pages to scan"

    initial_delay: int
    "Wait several seconds before first fetch"

    initial_interval: int
    "Initial interval between fetches"

    max_interval: int
    "Maximum interval between fetches"

    min_interval: int
    "Minimum interval between fetches"

    reply_count_threshold: int
    "Reply count threshold to fetch comments"

    increment_reply_count: int
    "Fetch more comments if new reply count is greater than this value"


dynamic_settings = DynamicSettings(
    scan_page=4,
    initial_delay=10,
    initial_interval=30,
    max_interval=300,
    min_interval=10,
    reply_count_threshold=10,
    increment_reply_count=10,
)


async def load_settings():
    stored_settings = await database.fetch_all(settings_table.select())
    logger.info("Loaded dynamic settings: {}", stored_settings)
    for key, value in stored_settings:
        if key not in dynamic_settings.__fields_set__:
            continue
        setattr(dynamic_settings, key, value)


async def save_settings():
    entries = list({"key": k, "value": v} for k, v in dynamic_settings.dict().items())
    insert_query = insert(settings_table)
    await database.execute_many(
        insert_query.on_conflict_do_update(
            index_elements=[settings_table.c.key],
            set_={"value": insert_query.excluded.value},
        ),
        values=entries,
    )

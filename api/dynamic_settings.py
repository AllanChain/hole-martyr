from loguru import logger
from pydantic import BaseModel, Field
from sqlalchemy.dialects.sqlite import insert

from .database import database, settings_table


class DynamicSettings(BaseModel):
    scan_page: int = Field(
        4,
        description="Page to scan",
    )
    initial_delay: int = Field(
        10,
        description="Wait several seconds before first fetch",
    )
    initial_interval: int = Field(
        30,
        description="Initial interval between fetches",
    )
    max_interval: int = Field(
        300,
        description="Maximum interval between fetches",
    )
    min_interval: int = Field(
        10,
        description="Minimum interval between fetches",
    )
    page_interval: int = Field(
        1,
        description="Interval between page fetches",
    )
    reply_count_threshold: int = Field(
        10,
        description="Reply count threshold to fetch comments",
    )
    increment_reply_count: int = Field(
        10,
        description="Fetch more comments if new reply count is greater than this value",
    )
    grace_before_relaxation: int = Field(
        5,
        description="Number of loops without newly deleted posts before relaxing the interval",
    )


dynamic_settings = DynamicSettings()


async def load_settings():
    stored_settings = await database.fetch_all(settings_table.select())
    logger.info("Loaded dynamic settings: {}", stored_settings)
    for key, value in stored_settings:
        if key not in dynamic_settings.__fields__:
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

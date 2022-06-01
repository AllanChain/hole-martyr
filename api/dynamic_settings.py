from loguru import logger
from pydantic import BaseModel
from sqlalchemy.dialects.sqlite import insert

from .database import database, settings_table


class DynamicSettings(BaseModel):
    scan_page: int
    initial_delay: int
    initial_interval: int
    max_interval: int
    min_interval: int


dynamic_settings = DynamicSettings(
    scan_page=4,
    initial_delay=10,
    initial_interval=30,
    max_interval=300,
    min_interval=10,
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

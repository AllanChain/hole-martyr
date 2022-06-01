from pydantic import BaseModel
from sqlalchemy.dialects.sqlite import insert

from .database import database, settings_table


class DynamicSettings(BaseModel):
    scan_page: int | None = 4
    initial_delay: int | None = 10
    initial_interval: int | None = 30
    max_interval: int | None = 300
    min_interval: int | None = 10


dynamic_settings = DynamicSettings()


async def load_settings():
    stored_settings = await database.fetch_all(settings_table.select())
    for key, value in stored_settings:
        if key not in dynamic_settings:
            continue
        dynamic_settings[key] = value


async def save_settings():
    entries = list(dynamic_settings.dict().items())
    insert_query = insert(settings_table)
    await database.execute_many(
        insert_query.on_conflict_do_update(
            index_elements=[settings_table.c.key],
            set_={"value": insert_query.excluded.value},
        ),
    ).values(entries)

import databases
import sqlalchemy
from sqlalchemy.orm import relationship

from .settings import settings

database = databases.Database(settings.database_url)
metadata = sqlalchemy.MetaData()
holes = sqlalchemy.Table(
    "holes",
    metadata,
    sqlalchemy.Column("pid", sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column("text", sqlalchemy.String),
    sqlalchemy.Column("created_at", sqlalchemy.Integer),
    sqlalchemy.Column("deleted_at", sqlalchemy.Integer),
    sqlalchemy.Column("reply_count", sqlalchemy.Integer),
    sqlalchemy.Column("like_count", sqlalchemy.Integer),
    sqlalchemy.Column("image", sqlalchemy.String),
)
comments = sqlalchemy.Table(
    "comments",
    metadata,
    sqlalchemy.Column("cid", sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column("pid", sqlalchemy.Integer, nullable=False),
    sqlalchemy.Column("created_at", sqlalchemy.Integer, nullable=False),
    sqlalchemy.Column("text", sqlalchemy.String, nullable=False),
)
engine = sqlalchemy.create_engine(
    settings.database_url, connect_args={"check_same_thread": False}
)

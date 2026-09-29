from collections.abc import Iterator

from sqlalchemy import event
from sqlalchemy.engine import Engine
from sqlmodel import Session, SQLModel, create_engine

from config import settings

# SQLite checks the thread a connection was created on by default, but FastAPI
# runs sync endpoints in a worker threadpool, so connections get handed across
# threads. check_same_thread=False turns that check off; a fresh Session per
# request keeps it safe.
connect_args = (
    {"check_same_thread": False} if settings.database_url.startswith("sqlite") else {}
)

engine = create_engine(
    settings.database_url,
    echo=settings.sql_echo,
    connect_args=connect_args,
)


@event.listens_for(Engine, "connect")
def _enable_sqlite_foreign_keys(dbapi_connection, connection_record):
    """SQLite ignores foreign keys unless asked, so delete protections do nothing."""
    if settings.database_url.startswith("sqlite"):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()


def create_db_and_tables() -> None:
    # Importing the models registers them on SQLModel.metadata before create_all.
    import models  # noqa: F401

    SQLModel.metadata.create_all(engine)


def get_session() -> Iterator[Session]:
    with Session(engine) as session:
        yield session

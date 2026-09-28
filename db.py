from sqlmodel import Session,engine,SQLModel

db_url = "sqlite:///kitaab.db"


engine = create_engine(db_url, echo=True)


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


def get_session():
    with Session(engine) as session:
        yield session


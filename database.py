from datetime import datetime
from typing import Optional

from pydantic import root_validator
from sqlmodel import Field, SQLModel, create_engine


DB_FILE = 'db.sqlite3'
engine = create_engine('sqlite:///' + DB_FILE, echo=True)

class TrackModel(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str
    artist: str
    duration: float
    last_play: datetime


def create_tables():
    # Create the tables registered with SQLModel.metadata (classes with table=True)
    SQLModel.metadata.create_all(engine)


if __name__ == '__main__':
    # creates the tables if the file is run independently as a script
    create_tables()
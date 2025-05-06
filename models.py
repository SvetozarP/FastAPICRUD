from datetime import datetime
from pydantic import BaseModel
from typing import Optional


class Track(BaseModel):
    id: Optional[int] = None
    title: str
    artist: str
    duration: float
    last_play: datetime
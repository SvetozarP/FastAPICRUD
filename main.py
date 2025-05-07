import json
import pathlib
from datetime import datetime
from typing import List, Union
from fastapi import FastAPI, Response, Depends
from sqlmodel import Session, select
from starlette import status
from database import TrackModel, engine

from models import Track

app = FastAPI()

data = []

@app.on_event("startup")
async def startup_event():
    datapath = pathlib.Path() / "data" / "tracks.json"
    session = Session(engine)
    # see if DB is populated
    stmt = select(TrackModel)
    result = session.exec(stmt).first()

    # if no results
    if result is None:
        with open(datapath, "r") as f:
            tracks = json.load(f)
            for track in tracks:
                if isinstance(track.get("last_play"), str):
                    track["last_play"] = datetime.fromisoformat(track["last_play"])
                session.add(TrackModel(**track))
        session.commit()
    session.close()


def get_session():
    with Session(engine) as session:
        yield session

@app.get("/tracks/", response_model=List[Track])
async def tracks(session: Session = Depends(get_session)):
    # select * from table
    stmt = select(TrackModel)
    result = session.exec(stmt).all()
    return result


@app.get("/tracks/{track_id}", response_model=Union[Track, str])
async def track(track_id: int, response: Response, session: Session = Depends(get_session)):
    # find track with given ID or none if none exists
    trck = session.get(TrackModel, track_id)

    if trck is None:
        response.status_code = 404
        return "Track not found"
    return trck


@app.post("/tracks/", response_model=Track, status_code=status.HTTP_201_CREATED)
async def create_track(trck: TrackModel, session: Session = Depends(get_session)):
    if isinstance(trck.last_play, str):
        trck.last_play = datetime.fromisoformat(trck.last_play)
    session.add(trck)
    session.commit()
    session.refresh(trck)
    return trck

@app.put("/tracks/{track_id}", response_model=Union[Track, str])
async def modify_track(track_id: int, updated_track: Track, response: Response, session: Session = Depends(get_session)):
    # find track with given ID or none if none exists
    trck = session.get(TrackModel, track_id)

    if trck is None:
        response.status_code = 404
        return "Track not found"

    track_dict = updated_track.model_dump(exclude_unset=True)
    for key, val in track_dict.items():
        setattr(trck, key, val)
    if isinstance(trck.last_play, str):
        trck.last_play = datetime.fromisoformat(trck.last_play)
    session.add(trck)
    session.commit()
    session.refresh(trck)
    return trck


@app.delete("/tracks/{track_id}")
async def delete_track(track_id: int, response: Response, session: Session = Depends(get_session)):
    # find track with given ID or none if none exists
    trck = session.get(TrackModel, track_id)

    if trck is None:
        response.status_code = 404
        return "Track not found"

    session.delete(trck)
    session.commit()
    return Response(status_code=200)


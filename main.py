import json
import pathlib
from datetime import datetime
from typing import List, Union
from fastapi import FastAPI, Response
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

@app.get("/tracks/", response_model=List[Track])
async def tracks():
    # select * from table
    with Session(engine) as session:
        stmt = select(TrackModel)
        result = session.exec(stmt).all()
        return result


@app.get("/tracks/{track_id}", response_model=Union[Track, str])
async def track(track_id: int, response: Response):
    # find track with given ID or none if none exists
    with Session(engine) as session:
        trck = session.get(TrackModel, track_id)

        if trck is None:
            response.status_code = 404
            return "Track not found"
        return trck


@app.post("/tracks/", response_model=Track, status_code=status.HTTP_201_CREATED)
async def create_track(track: Track):
    track_dict = track.dict()
    track_dict['id'] = max(data, key=lambda x: x['id']).get('id') + 1
    data.append(track_dict)
    return track_dict


@app.put("/tracks/{track_id}", response_model=Union[Track, str])
async def modify_track(track_id: int, updated_track: Track, response: Response):
    # find track with given ID or none if none exists
    track = None
    for t in data:
        if t['id'] == track_id:
            track = t
            break

    if track is None:
        response.status_code = 404
        return "Track not found"

    for key, val in updated_track.dict().items():
        if key != 'id':
            track[key] = val
    return track


@app.delete("/tracks/{track_id}")
async def delete_track(track_id: int, response: Response):
    # find track with given ID or none if none exists
    track_index = None
    for idx, t in enumerate(data):
        if t['id'] == track_id:
            track_index = idx
            break

    if track_index is None:
        response.status_code = 404
        return "Track not found"

    del data[track_index]
    return Response(status_code=200)


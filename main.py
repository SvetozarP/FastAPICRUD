import json
import pathlib
from typing import List, Union
from fastapi import FastAPI, Response
from starlette import status

from models import Track

app = FastAPI()

data = []

@app.on_event("startup")
async def startup_event():
    datapath = pathlib.Path() / "data" / "tracks.json"
    with open(datapath, 'r') as f:
        tracks = json.load(f)
        for track in tracks:
            data.append(Track(**track).dict())

@app.get("/tracks/", response_model=List[Track])
async def tracks():
    return data


@app.get("/tracks/{track_id}", response_model=Union[Track, str])
async def track(track_id: int, response: Response):
    # find track with given ID or none if none exists
    track = None
    for t in data:
        if t['id'] == track_id:
            track = t
            break

    if track is None:
        response.status_code = 404
        return "Track not found"
    return track


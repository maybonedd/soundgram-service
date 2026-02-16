from pydantic import BaseModel
from typing import List, Optional

class TrackSchema(BaseModel):
    title: str
    artists: List[str]
    cover_url: Optional[str]
    iframe_code: str

class PlaylistResponse(BaseModel):
    title: str
    owner: str
    tracks: List[TrackSchema]

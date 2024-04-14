from dataclasses import dataclass


@dataclass
class Image:
    location: str
    height: int
    width: int


@dataclass
class Song:
    title: str
    album: str
    artist: str
    isrc: str


@dataclass
class Playlist:
    id: str
    images: [Image]
    title: str
    description: str
    songs: [Song]

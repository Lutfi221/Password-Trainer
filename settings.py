from typing import TypedDict


class HashingSettings(TypedDict):
    algorithm: str
    arguments: dict[str, int | str]


class Settings(TypedDict):
    hashing: HashingSettings

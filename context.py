import json
import os
from typing import TypedDict


class HashingSettings(TypedDict):
    algorithm: str
    arguments: dict[str, int | str]


class TrainingEntry(TypedDict):
    prompt: str
    data: str
    """Hashed and salted password encoded in base64
    """
    salt: str
    hashing: HashingSettings


class Settings(TypedDict):
    hashing: HashingSettings


class AppContext:
    _settings_path: str
    _entries_path: str
    settings: Settings = {
        "hashing": {
            "algorithm": "scrypt",
            "arguments": {"n": 2, "r": 8, "p": 1, "maxmem": 0, "dklen": 64},
        }
    }
    entries: list[TrainingEntry] = []

    def __init__(
        self, settings_path="./settings.json", entries_path="./training-entries.json"
    ):
        self._settings_path = settings_path
        self._entries_path = entries_path

    def load_settings(self):
        if not os.path.isfile(self._settings_path):
            return
        with open(self._settings_path, "r") as f:
            loaded_settings = json.load(f)
        self.settings.update(loaded_settings)

    def load_entries(self):
        if not os.path.isfile(self._entries_path):
            return
        with open(self._entries_path, "r") as f:
            new_entries = json.load(f)
        self.entries = new_entries

    def save_entries(self):
        with open(self._entries_path, "w") as f:
            json.dump(self.entries, f, indent=4)

    def save_settings(self):
        with open(self._settings_path, "w") as f:
            json.dump(self.settings, f, indent=4)

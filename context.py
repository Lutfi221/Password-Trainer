import json
import os
from typing import Optional, TypedDict


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
    _entries: list[TrainingEntry] = []

    def __init__(
        self, settings_path="./settings.json", entries_path="./training-entries.json"
    ):
        self._settings_path = settings_path
        self._entries_path = entries_path

    def get_entries(self) -> list[TrainingEntry]:
        """Get unencrypted entries.

        Returns
        -------
        list[TrainingEntry]
            List of training entries
        """
        return self._entries

    def add_training_entry(self, entry: TrainingEntry):
        self._entries.append(entry)

    def load_settings(self):
        self.settings.update(self._read_json_file(self._settings_path, {}))

    def load_entries(self):
        self._entries = self._read_json_file(self._entries_path, [])

    def save_entries(self):
        self._save_json_file(self._entries_path, self._entries)

    def save_settings(self):
        self._save_json_file(self._settings_path, self.settings)

    def _read_json_file(self, path: str, default: Optional[any] = None) -> any:
        if not os.path.isfile(path):
            return default
        if os.stat(path).st_size == 0:
            return default
        try:
            with open(path, "r") as f:
                data = json.load(f)
        except json.decoder.JSONDecodeError as e:
            raise InvalidJsonFileError(path, e.lineno, e.colno)
        return data

    def _save_json_file(self, path: str, data: any):
        with open(path, "w") as f:
            json.dump(data, f, indent=4)


class InvalidJsonFileError(Exception):
    path: str
    lineno: int
    colno: int

    def __init__(self, path: str, lineno: int, colno: int):
        super().__init__(
            "Invalid JSON at `{}` line {} column {}".format(path, lineno, colno)
        )
        self.path = path
        self.lineno = lineno
        self.colno = colno

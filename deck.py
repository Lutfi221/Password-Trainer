from typing import Optional, TypedDict

from settings import HashingSettings


class DeckInfo(TypedDict):
    name: str
    path: str


class DeckEncryptionSettings(TypedDict):
    algorithm: str


class DeckEntry(TypedDict):
    prompt: str
    data: str
    """Hashed and salted password encoded in base64
    """
    salt: str


class DeckData(TypedDict):
    entries: list[DeckEntry]
    encryption: DeckEncryptionSettings
    hashing: HashingSettings


class DeckContext:
    name: str
    _entries: list[DeckEntry] = []
    _encryption: DeckEncryptionSettings = {}
    _hashing: HashingSettings

    def __init__(
        self,
        name: str,
        deck_data: DeckData,
        password: Optional[str] = None,
    ):
        self.name = name
        if deck_data is None:
            return
        if "entries" in deck_data:
            self._entries = deck_data["entries"]
        if "encryption" in deck_data:
            self._encryption = deck_data["encryption"]
        self._hashing = deck_data["hashing"]

    def get_entries(self) -> list[DeckEntry]:
        return self._entries

    def get_hashing(self) -> HashingSettings:
        return self._hashing

    def append_entry(self, entry: DeckEntry):
        self._entries.append(entry)

    def remove_entry():
        pass

    def set_entries():
        pass

    def generate_encrypted_deck_data(
        self,
        password: Optional[str] = None,
    ) -> DeckData:
        return {
            "entries": self._entries.copy(),
            "encryption": self._encryption.copy(),
            "hashing": self._hashing,
        }

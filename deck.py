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
    hashing: HashingSettings


class DeckData(TypedDict):
    entries: list[DeckEntry]
    encryption: DeckEncryptionSettings


class DeckContext:
    name: str
    _entries: list[DeckEntry] = []
    _encryption: DeckEncryptionSettings = {}

    def __init__(
        self,
        name: str,
        deck_data: Optional[DeckData] = None,
        password: Optional[str] = None,
    ):
        self.name = name
        if deck_data is None:
            return
        if "entries" in deck_data:
            self._entries = deck_data["entries"]
        if "encryption" in deck_data:
            self._encryption = deck_data["encryption"]

    def get_entries(self) -> list[DeckEntry]:
        return self._entries

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
        return {"entries": self._entries.copy(), "encryption": self._encryption.copy()}

import base64
import os
import logging
from typing import Optional, TypedDict
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

from settings import HashingSettings
from utils import base64_str_to_bytes, bytes_to_base64_str


l = logging.getLogger(__name__)


class DeckInfo(TypedDict):
    name: str
    path: str


class DeckEncryptionSettings(TypedDict):
    enabled: bool
    salt: str
    iterations: int


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
    _encryption: DeckEncryptionSettings
    _hashing: HashingSettings
    _password: Optional[str]

    def __init__(
        self,
        name: str,
        deck_data: DeckData,
        password: Optional[str] = None,
    ):
        self.name = name
        self._password = password
        if "encryption" in deck_data:
            self._encryption = deck_data["encryption"]
        else:
            self._encryption = generate_deck_encryption_settings(False)

        if "entries" in deck_data:
            if self._encryption["enabled"]:
                self._entries = decrypt_deck_entries(
                    deck_data["entries"], self._encryption, password
                )
            else:
                self._entries = deck_data["entries"]
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

    def generate_deck_data(self) -> DeckData:
        """Generate deck data (encrypted if encryption is enabled)

        Returns
        -------
        DeckData
            Deck data (encrypted if enabled)
        """
        deck_data = {
            "encryption": self._encryption.copy(),
            "hashing": self._hashing,
        }

        if not self._encryption["enabled"]:
            l.info("Encryption is not enabled for deck `%s`", self.name)
            deck_data["entries"] = self._entries.copy()
            return deck_data

        deck_data["entries"] = encrypt_deck_entries(
            self._entries, self._encryption, self._password
        )

        return deck_data


def encrypt_deck_entries(
    entries: list[DeckEntry], encryption: DeckEncryptionSettings, password: str
) -> list[DeckEntry]:
    """Encrypt deck entries. Does not mutate original list of entries.

    This function follows the example from the cryptography library documentation
    https://cryptography.io/en/latest/fernet/#using-passwords-with-fernet

    Parameters
    ----------
    entries : list[DeckEntry]
        List of unencrypted deck entries
    encryption : DeckEncryptionSettings
        Deck encryption settings
    password : str
        Password

    Returns
    -------
    list[DeckEntry]
        Encrypted deck entries
    """
    salt = base64_str_to_bytes(encryption["salt"])
    iterations = encryption["iterations"]
    f = create_fernet(password, salt, iterations)

    encrypted_entries: list[DeckEntry] = []
    for i, entry in enumerate(entries):
        l.debug("Encrypt entry of index %s", i)
        entry_prompt = bytes(entry["prompt"], "utf-8")
        enc_entry_prompt = bytes_to_base64_str(f.encrypt(entry_prompt))
        entry_pass = base64_str_to_bytes(entry["data"])
        enc_entry_pass = bytes_to_base64_str(f.encrypt(entry_pass))
        entry_salt = base64_str_to_bytes(entry["salt"])
        enc_entry_salt = bytes_to_base64_str(f.encrypt(entry_salt))
        encrypted_entries.append(
            {
                "data": enc_entry_pass,
                "prompt": enc_entry_prompt,
                "salt": enc_entry_salt,
            }
        )
    return encrypted_entries


def decrypt_deck_entries(
    entries: list[DeckEntry], encryption: DeckEncryptionSettings, password: str
) -> list[DeckEntry]:
    """Decrypt deck entries.

    Parameters
    ----------
    entries : list[DeckEntry]
        List of deck entries
    encryption : DeckEncryptionSettings
        Deck encryption settings
    password : str
        Password

    Returns
    -------
    list[DeckEntry]
        List of enencrypted deck entries
    """
    salt = base64.decodebytes(encryption["salt"].encode("ascii"))
    iterations = encryption["iterations"]
    f = create_fernet(password, salt, iterations)

    decrypted_entries: list[DeckEntry] = []
    for i, entry in enumerate(entries):
        l.debug("Decrypt entry of index %s", i)
        enc_entry_prompt = base64_str_to_bytes(entry["prompt"])
        entry_prompt = f.decrypt(enc_entry_prompt).decode("utf-8")
        enc_entry_pass = base64_str_to_bytes(entry["data"])
        entry_pass = bytes_to_base64_str(f.decrypt(enc_entry_pass))
        enc_entry_salt = base64_str_to_bytes(entry["salt"])
        entry_salt = bytes_to_base64_str(f.decrypt(enc_entry_salt))
        decrypted_entries.append(
            {
                "data": entry_pass,
                "prompt": entry_prompt,
                "salt": entry_salt,
            }
        )
    return decrypted_entries


def create_fernet(password: str, salt: bytes, iterations: int) -> Fernet:
    """Create a fernet instance.
    Using https://cryptography.io/en/latest/fernet/#using-passwords-with-fernet
    as reference

    Parameters
    ----------
    password : str
        Password
    salt : bytes
        Salt to give to kdf
    iterations : int
        Number of iterations

    Returns
    -------
    Fernet
        Fernet instance
    """
    l.debug(
        "Setup kdf with PBKDF2HMAC, SHA256, length=%s, salt=%s, iterations=%s",
        32,
        salt,
        iterations,
    )
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(), length=32, salt=salt, iterations=iterations
    )

    l.info("Derive key from password")
    key = base64.urlsafe_b64encode(kdf.derive(bytes(password, "utf-8")))
    f = Fernet(key)
    return f


def generate_deck_encryption_settings(enabled=True) -> DeckEncryptionSettings:
    return {
        "salt": bytes_to_base64_str(os.urandom(32)),
        "iterations": 480000,
        "enabled": enabled,
    }

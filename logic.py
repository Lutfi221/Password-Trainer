import base64
from hashlib import scrypt
import secrets
import logging

from app import AppContext
from deck import DeckEntry
from settings import HashingSettings

l = logging.getLogger(__name__)


def create_training_entry(prompt: str, password: str, ctx: AppContext) -> DeckEntry:
    settings = ctx.get_settings()
    entries = ctx.get_current_deck_context().get_entries()

    while True:
        salt: bytes = secrets.randbits(32 * 8).to_bytes(
            32, "big"
        )  # Generate a 32 byte salt
        hashed = hash_password(password, settings["hashing"], salt)
        hashed_b64 = base64.encodebytes(hashed).decode("ascii")

        duplicate_hash_found = False
        for entry in entries:
            if entry["data"] == hashed_b64:
                duplicate_hash_found = True
                l.info("Duplicate hash found, trying with another salt.")
                break

        if not duplicate_hash_found:
            return {
                "data": hashed_b64,
                "prompt": prompt,
                "salt": base64.encodebytes(salt).decode("ascii"),
                "hashing": settings["hashing"],
            }


def hash_password(password: str, hash_settings: HashingSettings, salt: bytes) -> bytes:
    if hash_settings["algorithm"].lower() != "scrypt":
        raise Exception("Only the `scrypt` hashing algorithm is currently supported.")
    l.info("Hash password with hash_settings: %s", hash_settings)
    return scrypt(
        bytes(password, encoding="utf-8"), salt=salt, **hash_settings["arguments"]
    )

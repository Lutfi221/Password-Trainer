import base64
from hashlib import scrypt
import secrets

from context import AppContext, TrainingEntry, HashingSettings


def create_training_entry(prompt: str, password: str, ctx: AppContext) -> TrainingEntry:
    while True:
        salt: bytes = secrets.randbits(32 * 8).to_bytes(
            32, "big"
        )  # Generate a 32 byte salt
        hashed = hash_password(password, ctx.settings["hashing"], salt)
        hashed_b64 = base64.encodebytes(hashed).decode("ascii")

        duplicate_hash_found = False
        for entry in ctx.get_entries():
            if entry["data"] == hashed_b64:
                duplicate_hash_found = True
                # Duplicate hash found.
                # Will try again using a different salt.
                break

        if not duplicate_hash_found:
            return {
                "data": hashed_b64,
                "prompt": prompt,
                "salt": base64.encodebytes(salt).decode("ascii"),
                "hashing": ctx.settings["hashing"],
            }


def hash_password(password: str, hash_settings: HashingSettings, salt: bytes) -> bytes:
    if hash_settings["algorithm"].lower() != "scrypt":
        raise Exception("Only the `scrypt` hashing algorithm is currently supported.")
    return scrypt(
        bytes(password, encoding="utf-8"), salt=salt, **hash_settings["arguments"]
    )

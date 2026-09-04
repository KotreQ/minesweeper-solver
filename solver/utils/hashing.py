import hashlib
import json


def hash_jsonable(value, *, digest_size=64) -> bytes:
    payload = json.dumps(
        value,
        ensure_ascii=False,
        separators=(",", ":"),
        sort_keys=True,
        indent=None
    ).encode("utf-8")

    return hashlib.blake2b(payload, digest_size=digest_size)

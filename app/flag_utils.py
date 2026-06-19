import hashlib


def hash_flag(flag: str) -> str:
    """Hash a flag using SHA-256 for secure storage."""
    return hashlib.sha256(flag.encode()).hexdigest()


def validate_flag(submitted_flag: str, stored_hash: str) -> bool:
    """Return True only if submitted_flag hashes to stored_hash (case-sensitive)."""
    return hash_flag(submitted_flag) == stored_hash

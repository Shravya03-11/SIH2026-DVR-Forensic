"""
utils/hasher.py — Cryptographic Hashing Utility
ASSIGNED TO: Member 2
YOUR TASKS:
  [ ] The functions here are complete — you can use them as-is
  [ ] Add a function to compare two hashes and return True/False
  [ ] Add a function to hash a file in chunks (for very large files)
"""

import hashlib
import datetime


def compute_hashes(file_bytes: bytes) -> dict:
    """
    Compute MD5 and SHA-256 hash of file bytes.
    Returns a dict with both hashes and timestamp.
    """
    md5_hash    = hashlib.md5(file_bytes).hexdigest()
    sha256_hash = hashlib.sha256(file_bytes).hexdigest()
    sha1_hash   = hashlib.sha1(file_bytes).hexdigest()

    return {
        "md5":       md5_hash,
        "sha256":    sha256_hash,
        "sha1":      sha1_hash,
        "computed_at": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "file_size_bytes": len(file_bytes),
    }


def verify_integrity(original_hash: str, current_bytes: bytes, algorithm: str = "sha256") -> bool:
    """
    Verify that a file has not been modified by comparing hashes.
    Returns True if file is intact, False if tampered.
    """
    # TODO (Member 2): Implement this function
    if algorithm == "md5":
        current_hash = hashlib.md5(current_bytes).hexdigest()
    elif algorithm == "sha256":
        current_hash = hashlib.sha256(current_bytes).hexdigest()
    else:
        raise ValueError(f"Unknown algorithm: {algorithm}")

    return original_hash.lower() == current_hash.lower()


def format_hash_display(hash_string: str, chars_per_line: int = 32) -> str:
    """Format a long hash string for display by breaking it into lines."""
    return "\n".join(
        hash_string[i:i + chars_per_line]
        for i in range(0, len(hash_string), chars_per_line)
    )

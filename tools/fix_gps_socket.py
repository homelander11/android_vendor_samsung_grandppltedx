#!/usr/bin/env python3
"""Move the pinned legacy GPS worker's stream socket to its GPS-owned directory.

Changes one NUL-terminated string slot only; file size, executable code, ELF
headers, dependencies and symbols remain identical. Unknown inputs are rejected.
"""
import argparse
import hashlib
from pathlib import Path
import sys

ORIGINAL = "9dea2246a148f6f60d0f3c9a69b7d9fe92da4a645abf7153c815ac73ead5befc"
PATCHED = "26810174325967eafe9a7292a3efb65c8700943d4189a1c37e08a52905c253cf"
OFFSET, SIZE = 84903, 131265
OLD = b"/data/misc/codec_sock\0"
NEW = b"/data/gps_mnl/codec\0"


def digest(data):
    return hashlib.sha256(data).hexdigest()


def corrected(data):
    if digest(data) == PATCHED:
        return data
    if digest(data) != ORIGINAL:
        raise ValueError("unknown GPS HAL SHA-256; refusing modification")
    if len(data) != SIZE or data[OFFSET:OFFSET + len(OLD)] != OLD or data.count(OLD) != 1:
        raise ValueError("unexpected GPS socket string size, offset or count")
    result = data[:OFFSET] + NEW.ljust(len(OLD), b"\0") + data[OFFSET + len(OLD):]
    if digest(result) != PATCHED:
        raise ValueError("corrected GPS HAL hash mismatch")
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("library", type=Path)
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()
    try:
        before = args.library.read_bytes()
        after = corrected(before)
        if args.apply and before != after:
            args.library.write_bytes(after)
        elif before != after:
            print("Original GPS HAL recognized; use --apply to relocate its worker socket.")
            return 0
    except (OSError, ValueError) as error:
        print("FAIL:", error, file=sys.stderr)
        return 1
    print("Corrected GPS worker socket verified:", PATCHED)
    return 0


if __name__ == "__main__":
    sys.exit(main())

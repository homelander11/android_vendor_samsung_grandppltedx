#!/usr/bin/env python3
"""Correct four pinned HD-recording NVRAM selectors, without accessing NVRAM."""
import argparse
import hashlib
from pathlib import Path
import sys

ORIGINAL = "d4f20563caa3d8a8c1eaab2ea0bf853baf1056ab8f03306793c0210867dc3690"
PATCHED = "f3fb7b40768fe76339c02b198474a2f6dffb262350fbbba20995747baec5fe8e"
SIZE = 36292
# ARM MOV r1, #LID. Getters and setters must select the same record.
CHANGES = ((13440, 65, 63), (13948, 65, 63),
           (14408, 66, 64), (14916, 66, 64))


def digest(data):
    return hashlib.sha256(data).hexdigest()


def corrected(data):
    if digest(data) == PATCHED:
        return data
    if len(data) != SIZE or digest(data) != ORIGINAL:
        raise ValueError("unknown audio parameter library; refusing modification")
    result = bytearray(data)
    for offset, old, new in CHANGES:
        before = bytes((old, 0x10, 0xa0, 0xe3))
        if result[offset:offset + 4] != before:
            raise ValueError("unexpected recording selector instruction")
        result[offset] = new
    if digest(result) != PATCHED:
        raise ValueError("corrected recording selector hash mismatch")
    return bytes(result)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("library", type=Path)
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()
    try:
        before = args.library.read_bytes()
        after = corrected(before)
        if before != after:
            if not args.apply:
                print("FAIL: incorrect recording selectors remain; use --apply", file=sys.stderr)
                return 1
            args.library.write_bytes(after)
    except (OSError, ValueError) as error:
        print("FAIL:", error, file=sys.stderr)
        return 1
    print("HD recording selectors verified:", PATCHED)
    return 0


if __name__ == "__main__":
    sys.exit(main())

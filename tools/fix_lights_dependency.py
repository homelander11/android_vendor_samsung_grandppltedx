#!/usr/bin/env python3
"""Remove one unused, unavailable DT_NEEDED entry from the pinned lights HAL.

No code, symbols, strings, section/program headers or file size change. The
remaining dynamic entries slide left by one slot and the final slot is zeroed.
Unknown input versions are rejected; repeated --apply is idempotent.
"""
import argparse
import hashlib
from pathlib import Path
import struct
import sys

ORIGINAL = "5150222ba0218d4dcc51dc81f616e7f9dbe5de15122518c8a49b283b62b45237"
PATCHED = "d83f7a9ed24076fc5d953ec964f5b2e698c342a4ac8acd18980feae60fe36be0"
DYNAMIC_START, DYNAMIC_SIZE, ENTRY = 20040, 280, 20152


def digest(data):
    return hashlib.sha256(data).hexdigest()


def corrected(data):
    if digest(data) == PATCHED:
        return data
    if digest(data) != ORIGINAL:
        raise ValueError("unknown lights HAL SHA-256; refusing modification")
    end = DYNAMIC_START + DYNAMIC_SIZE
    if len(data) != 22196 or struct.unpack_from("<I", data, ENTRY)[0] != 1:
        raise ValueError("unexpected ELF size or DT_NEEDED entry")
    if data[end - 8:end] != bytes(8):
        raise ValueError("unexpected dynamic-table padding")
    result = data[:ENTRY] + data[ENTRY + 8:end] + bytes(8) + data[end:]
    if digest(result) != PATCHED:
        raise ValueError("corrected lights HAL hash mismatch")
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("library", type=Path)
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()
    try:
        before = args.library.read_bytes()
        after = corrected(before)
        if args.apply and after != before:
            args.library.write_bytes(after)
        elif after != before:
            print("Original lights HAL recognized; use --apply to remove unused libsecril-client dependency.")
            return 0
    except (OSError, ValueError) as error:
        print("FAIL:", error, file=sys.stderr)
        return 1
    print("Corrected lights HAL verified:", PATCHED)
    return 0


if __name__ == "__main__":
    sys.exit(main())

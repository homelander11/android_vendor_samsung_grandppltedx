#!/usr/bin/env python3
"""Guard the pinned MNL mutex-destroy wrapper against repeated destruction."""
import argparse
import hashlib
from pathlib import Path
import sys

ORIGINAL = "a92487438cc305e2fa47f2ebd5c4cf80ec26a5fe7b1582ed9277435bd1682d80"
PATCHED = "84c2d44e51d6d0c43083175847cc624a6347f54e591b34ea0546d4cbc099f292"
SIZE, OFFSET = 2149272, 53306
BEFORE = bytes.fromhex("f8f728e9002814bf4ff0ff30002008bd00bf")
AFTER = bytes.fromhex("038801331b04f0d0f8f724e90028ecd108bd")


def corrected(data):
    digest = hashlib.sha256(data).hexdigest()
    if digest == PATCHED:
        return data
    if len(data) != SIZE or digest != ORIGINAL:
        raise ValueError("unknown MNL library; refusing modification")
    if data[OFFSET:OFFSET + len(BEFORE)] != BEFORE:
        raise ValueError("unexpected mutex-destroy instruction sequence")
    # Existing wrapper: r0 indexes its private 32-bit mutex table. Guard only
    # Bionic's 0xffff destroyed state, returning the existing -1 error path.
    # All other states still call pthread_mutex_destroy and normalize 0/-1.
    result = data[:OFFSET] + AFTER + data[OFFSET + len(BEFORE):]
    if hashlib.sha256(result).hexdigest() != PATCHED:
        raise ValueError("corrected MNL library checksum mismatch")
    return result


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
                print("Original mutex wrapper recognized; use --apply.")
                return 1
            args.library.write_bytes(after)
    except (OSError, ValueError) as error:
        print("FAIL:", error, file=sys.stderr)
        return 1
    print("MNL repeated-destroy guard verified:", PATCHED)
    return 0


if __name__ == "__main__":
    sys.exit(main())

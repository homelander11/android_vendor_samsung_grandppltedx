#!/usr/bin/env python3
"""Decode Android 11 grayscale BACKLIGHT color to a valid 0..255 brightness.

The pinned Samsung callback writes the entire ARGB word as a signed sysfs
integer. Replace its LDR with LDRB on this little-endian ARM module. Android
11 LightsService repeats the brightness byte in R/G/B, so this exactly decodes
all 256 framework backlight levels. Other light callbacks are unchanged.
"""
import argparse
import hashlib
from pathlib import Path
import sys

import fix_lights_dependency as dependency

BASE = "d83f7a9ed24076fc5d953ec964f5b2e698c342a4ac8acd18980feae60fe36be0"
PATCHED = "9d2a8737e6ee146cdf7e74b0233fc38efd614d0a9e6d79832688a2cce2b81b75"
OFFSET = 5736


def digest(data):
    return hashlib.sha256(data).hexdigest()


def corrected(data):
    if digest(data) == PATCHED:
        return data
    if digest(data) == dependency.ORIGINAL:
        data = dependency.corrected(data)
    if digest(data) != BASE or len(data) != 22196:
        raise ValueError("unknown lights HAL SHA-256; refusing modification")
    if data[OFFSET:OFFSET + 2] != b"\x0d\x68":
        raise ValueError("unexpected BACKLIGHT callback color-load instruction")
    result = data[:OFFSET] + b"\x0d\x78" + data[OFFSET + 2:]
    if digest(result) != PATCHED:
        raise ValueError("corrected brightness HAL hash mismatch")
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("library", type=Path)
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()
    try:
        before = args.library.read_bytes()
        after = corrected(before)
        if args.apply and after != before:
            args.library.write_bytes(after)
        elif before != after:
            print("Known lights HAL; use --apply for dependency and grayscale brightness corrections.")
            sys.exit(0)
    except (OSError, ValueError) as error:
        sys.exit("FAIL: " + str(error))
    print("Corrected lights brightness verified:", PATCHED)

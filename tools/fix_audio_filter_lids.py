#!/usr/bin/env python3
"""Check/apply the exact audio-filter LID correction; never touches NVRAM data."""
import argparse
import hashlib
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()
    provenance = json.loads((ROOT / "audio-filter-lid-provenance.json").read_text())
    image = ROOT / provenance["path"]
    original = image.read_bytes()
    digest = hashlib.sha256(original).hexdigest()
    if digest == provenance["patched_sha256"]:
        print("Audio-filter LID correction verified (already applied).")
        return 0
    if digest != provenance["original_sha256"]:
        print("FAIL: unexpected audio-filter library; refusing to patch", file=sys.stderr)
        return 1
    if not args.apply:
        print("FAIL: original mismatched LIDs remain; use --apply", file=sys.stderr)
        return 1
    result = bytearray(original)
    for change in provenance["changes"]:
        start = change["file_offset"]
        before = bytes.fromhex(change["before"])
        after = bytes.fromhex(change["after"])
        if len(before) != len(after) or result[start:start + len(before)] != before:
            print("FAIL: patch byte precondition failed", file=sys.stderr)
            return 1
        result[start:start + len(before)] = after
    if hashlib.sha256(result).hexdigest() != provenance["patched_sha256"]:
        print("FAIL: corrected library checksum differs", file=sys.stderr)
        return 1
    image.write_bytes(result)
    print("Applied audio-filter LID correction. No calibration files were accessed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())

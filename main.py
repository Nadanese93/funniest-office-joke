#!/usr/bin/env python3
"""Write the funniest-office-joke entry to $MAKEFUN_OUTPUT_DIR/entry.txt.

Reads the output directory from MAKEFUN_OUTPUT_DIR (default '/output'),
validates the entry against the contest gate (1-200 chars, not
whitespace-only, single line), and writes it atomically via a temp file
plus os.replace. No network, no dependencies.
"""

import os
import sys
import tempfile

ENTRY = (
    "My office badge worked on every door except my own office, so "
    "security gave me a visitor pass to my own desk \u2014 I've been a "
    "guest here for three years now."
)

MAX_CHARS = 200


def validate(text):
    if not text or not text.strip():
        raise ValueError("entry must not be empty or whitespace-only")
    if len(text) > MAX_CHARS:
        raise ValueError(
            "entry is %d chars, exceeds %d-char limit" % (len(text), MAX_CHARS)
        )
    if "\n" in text or "\r" in text:
        raise ValueError("entry must be a single line (no newline/CR)")


def main():
    validate(ENTRY)
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR") or "/output"
    os.makedirs(out_dir, exist_ok=True)
    target = os.path.join(out_dir, "entry.txt")
    data = ENTRY.encode("utf-8")
    fd, tmp_path = tempfile.mkstemp(prefix=".entry-", dir=out_dir)
    try:
        with os.fdopen(fd, "wb") as fh:
            fh.write(data)
            fh.flush()
            os.fsync(fh.fileno())
        os.replace(tmp_path, target)
        # Read-back verification: the bytes on disk must be exactly what
        # was written; a mismatch means the write did not land intact.
        with open(target, "rb") as fh:
            if fh.read() != data:
                raise IOError("read-back mismatch: entry.txt bytes differ")
    except BaseException:
        try:
            os.unlink(tmp_path)
        except OSError:
            pass
        raise
    sys.stdout.write("wrote %s (%d chars, %d bytes)\n" % (target, len(ENTRY), len(data)))
    return 0


if __name__ == "__main__":
    sys.exit(main())

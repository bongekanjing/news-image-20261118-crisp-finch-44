#!/usr/bin/env python3
"""Write the entry image to the output directory.

The picture is a file the repository carries, so this program only places it
where the grader looks, byte for byte: no drawing, no clock, no randomness,
so both runs write the same bytes.

It checks the file before it copies it, so a bad repository fails loudly here
rather than handing the grader an unreadable image: the PNG signature, the
width and height from the IHDR header, a closing IEND chunk, and the
competition's size caps.
"""

import os
import shutil
import struct
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SOURCE = os.path.join(HERE, "entry.png")
MAX_BYTES = 1048576
MAX_SIDE = 1024
PNG_MAGIC = b"\x89PNG\r\n\x1a\n"
IEND = b"IEND\xaeB`\x82"
# The image must be square-ish and small; the judge sees it at 1024 wide.
MIN_SIDE = 256


def output_dir():
    """The writable directory the grader gives us, or MAKEFUN_OUTPUT_DIR."""
    return os.environ.get("MAKEFUN_OUTPUT_DIR") or "/output"


def describe(data):
    """Read the PNG header: width, height and that the file opens and closes."""
    if not data.startswith(PNG_MAGIC):
        raise SystemExit("entry.png is not a PNG")
    if len(data) < 33 or data[12:16] != b"IHDR":
        raise SystemExit("entry.png has no IHDR header")
    width, height = struct.unpack(">II", data[16:24])
    if IEND not in data[-64:]:
        raise SystemExit("entry.png has no IEND chunk")
    return width, height


def validate(data, width, height):
    """Hold the image to the competition's caps before it is copied."""
    if not data:
        raise SystemExit("entry.png is empty")
    if len(data) > MAX_BYTES:
        raise SystemExit("entry.png is %d bytes, over the %d cap"
                         % (len(data), MAX_BYTES))
    if width > MAX_SIDE or height > MAX_SIDE:
        raise SystemExit("entry.png is %dx%d, over the %d cap"
                         % (width, height, MAX_SIDE))
    if width < MIN_SIDE or height < MIN_SIDE:
        raise SystemExit("entry.png is %dx%d, under the %d floor"
                         % (width, height, MIN_SIDE))
    if width != height:
        raise SystemExit("entry.png is %dx%d, not square"
                         % (width, height))


def write(data, target):
    """Copy the bytes to target, creating its directory if it is missing."""
    parent = os.path.dirname(target)
    if parent:
        os.makedirs(parent, exist_ok=True)
    shutil.copyfile(SOURCE, target)
    if os.path.getsize(target) != len(data):
        raise SystemExit("the copy is short: %d of %d bytes"
                         % (os.path.getsize(target), len(data)))


def main():
    with open(SOURCE, "rb") as handle:
        data = handle.read()
    width, height = describe(data)
    validate(data, width, height)

    target = os.path.join(output_dir(), "entry.png")
    write(data, target)
    print("wrote %s: %dx%d, %d bytes" % (target, width, height, len(data)))
    return 0


if __name__ == "__main__":
    sys.exit(main())

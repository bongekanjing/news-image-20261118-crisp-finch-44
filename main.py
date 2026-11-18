#!/usr/bin/env python3
"""Write the entry image to the output directory.

The picture is a file the repository carries, so this program only places it
where the grader looks, byte for byte: no drawing, no clock, no randomness,
so both runs write the same bytes.
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


def output_dir():
    """The writable directory the grader gives us, or MAKEFUN_OUTPUT_DIR."""
    return os.environ.get("MAKEFUN_OUTPUT_DIR") or "/output"


def describe(data):
    """Read the PNG header: width, height and that the file opens and closes."""
    if not data.startswith(PNG_MAGIC):
        raise SystemExit("entry.png is not a PNG")
    width, height = struct.unpack(">II", data[16:24])
    if not data.rstrip(b"\x00").endswith(b"IEND\xaeB`\x82"):
        raise SystemExit("entry.png has no IEND chunk")
    return width, height


def main():
    with open(SOURCE, "rb") as handle:
        data = handle.read()
    width, height = describe(data)
    if len(data) > MAX_BYTES:
        raise SystemExit("entry.png is %d bytes, over the %d cap"
                         % (len(data), MAX_BYTES))
    if width > MAX_SIDE or height > MAX_SIDE:
        raise SystemExit("entry.png is %dx%d, over the %d cap"
                         % (width, height, MAX_SIDE))

    target = os.path.join(output_dir(), "entry.png")
    os.makedirs(os.path.dirname(target) or ".", exist_ok=True)
    shutil.copyfile(SOURCE, target)
    print("wrote %s: %dx%d, %d bytes" % (target, width, height, len(data)))
    return 0


if __name__ == "__main__":
    sys.exit(main())

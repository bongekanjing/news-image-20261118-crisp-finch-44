#!/usr/bin/env python3
"""Write the entry image to the output directory.

The picture itself is a file the repository carries, so this program only
has to place it where the grader looks, byte for byte: no drawing, no clock,
no randomness, and the same bytes on every run.
"""

import os
import shutil
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SOURCE = os.path.join(HERE, "entry.png")


def output_dir():
    return os.environ.get("MAKEFUN_OUTPUT_DIR") or "/output"


def main():
    target = os.path.join(output_dir(), "entry.png")
    os.makedirs(os.path.dirname(target), exist_ok=True)
    shutil.copyfile(SOURCE, target)
    print("wrote", target, os.path.getsize(target), "bytes")
    return 0


if __name__ == "__main__":
    sys.exit(main())

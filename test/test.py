#!/usr/bin/env python3

"""Test module for the pyproject Palworld Transfer & Clean Save File."""

import os
from zipfile import ZipFile
from pathlib import Path

CURRENT_DIR: Path = Path(os.path.dirname(os.path.realpath(__file__)))
EXAMPLE_ZIP: Path = Path(os.path.join(CURRENT_DIR, "example.zip"))


def main() -> None:
    """The main method of the test file."""
    if EXAMPLE_ZIP.exists():
        with ZipFile(EXAMPLE_ZIP, "r") as zipObject:
            zipObject.extractall(CURRENT_DIR)

    import script as transfer_uuids

    transfer_uuids.main(CURRENT_DIR)


if __name__ == "__main__":
    main()

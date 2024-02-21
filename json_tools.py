#!/usr/env python3

"""Temporary Module Docstring."""

# pyright: reportUnknownMemberType=false, reportUnknownVariableType=false
# cSpell:ignore palworld gvas palsav paltypes

import json
from typing import Any
from pathlib import Path
from logger import pprint

from local_types import JsonType, CustomJsonReader, CustomJsonWriter

from palworld_save_tools.archive import UUID

def json_serialize(obj: Any) -> Any:
    """JSON serializer for objects not serializable by default json code"""
    if isinstance(obj, UUID):
        serial: str = str(obj)
        return serial

    return obj.__dict__


def parse_constant(obj: str) -> Any:
    """Parses string constants that are not able to be parsed normally into UUIDs."""
    try:
        pprint(f"Attempting to convert {obj} to UUID", indent=2)
        serial: UUID = UUID.from_str(obj)
        return serial
     # pylint: disable-next=W0718
    except BaseException as exception:
        pprint(str(exception), indent=2)

    return str(obj)


def load_json(json_path: str | Path, method: CustomJsonReader | None = None) -> JsonType:
    """A universal wrapper to load a json file from path into a type of ``JsonType``."""
    _path: Path
    _temp: JsonType

    if isinstance(json_path, str):
        _path = Path(json_path)
    else:
        _path = json_path

    try:
        if method is not None:
            _temp = method(str(_path))
        else:
            with _path.open("r", encoding="utf8") as f:
                _temp = json.loads(f.read())
    except BaseException as base_exception:
        raise base_exception

    return _temp


def write_json(json_data: JsonType, json_path: str | Path,
               method: CustomJsonWriter | None = None) -> None:
    """A universal wrapper to load a json file from path into a type of ``JsonType``."""
    _path: Path

    if isinstance(json_path, str):
        _path = Path(json_path)
    else:
        _path = json_path

    try:
        if method is not None:
            assert isinstance(json_data, dict)
            method(json_data, str(_path))
        else:
            with _path.open("w", encoding="utf8") as f:
                f.write(json.dumps(json_data))

    except BaseException as base_exception:
        raise base_exception

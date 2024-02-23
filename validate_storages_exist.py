#!/usr/env python3

"""Temporary Module Docstring."""

# pyright: reportUnknownMemberType=false, reportUnknownVariableType=false

import json
from re import Pattern
import re
from typing import Any

# from logger import pprint
from local_types import JsonType
from json_tools import json_serialize, parse_constant
from palworld_save_tools.archive import UUID


def list_transfer_uuid_to_str(_input: dict[str, UUID]) -> list[str]:
    """Transfers a dictionary of string and UUID to a list of strings that are the UUIDs."""
    output: list[str] = []
    for _, i in _input.items():
        output.append(str(i))
    return output


def get_all_storage_id(player_data: JsonType) -> dict[str, UUID]:
    """Gets all storage UUIDs in the player data."""
    output: dict[str, UUID] = {}
    save_data: dict[str, Any] = player_data["properties"]["SaveData"]["value"]
    for i, data in save_data.items():
        if i == "PalStorageContainerId":
            output[i] = data["value"]["ID"]["value"]
        elif i == "inventoryInfo":
            for j, info in data["value"].items():
                output[j] = info["value"]["ID"]["value"]
    #   output_str: list[str] = list_transfer_uuid_to_str(output)
    #   pprint(f"Got these storage ids: [ {', '.join(output_str)} ]", indent=3)
    return output


def validate_storages(level_data: JsonType, player_data: JsonType) -> bool:
    r"""
    Validates that all storages defined in ``player_data`` are also defined in ``level_data``.
    """
    returned: bool = False
    json_text: str = json.dumps(level_data, default=json_serialize)
    storage_ids: dict[str, UUID] = get_all_storage_id(player_data)

    for _, _id in storage_ids.items():
        regex: Pattern[str] = re.compile(re.escape(str(_id)))
        found: list[Any] = regex.findall(json_text)
        if len(found) > 0:
            #       if len(found) > 0:
            #           pprint(f"[green][bold]INFO:[/bold][/green] Found {len(found)} instances of the old "
            #                  f"GUID Unformatted: {str(_id)}", indent=3)
            #       else:
            #           pprint(f"[yellow][bold]WARN:[/bold][/yellow] No id found with string \"{str(_id)}\"",
            #                  indent=3)
            returned = True
    return returned


def update_storages(old_id: UUID, new_id: UUID, json_text: str) -> str:
    r"""Updates all storages in a collection defined in ``player_data``."""
    regex: Pattern[str] = re.compile(re.escape(str(old_id)))
    found: list[Any] = regex.findall(json_text)
    if len(found) > 0:
        json_text = json_text.replace(str(old_id), str(new_id))
    return json_text


def correct_storages(level_data: JsonType, new_player_data: JsonType, old_player_data: JsonType) -> tuple[bool, JsonType]:
    r"""
    Corrects missing storages that all storages defined in either,
    ``new_player_data`` or ``old_player_data``, to the other one that it is missing in.
    """
    out_data: JsonType = {}
    json_text: str = json.dumps(level_data, default=json_serialize)
    new_storage_ids: dict[str, UUID] = get_all_storage_id(new_player_data)
    old_storage_ids: dict[str, UUID] = get_all_storage_id(old_player_data)

    if validate_storages(level_data, new_player_data) and not validate_storages(level_data, old_player_data):
        for j, new_id in new_storage_ids.items():
            for k, old_id in old_storage_ids.items():
                if j == k:
                    json_text = update_storages(old_id, new_id, json_text)
    out_data = json.loads(json_text, parse_constant=parse_constant)
    out_bool: bool = validate_storages(out_data, new_player_data) and not validate_storages(out_data, old_player_data)

    return (out_bool, out_data)

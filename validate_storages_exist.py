#!/usr/env python3

"""Temporary Module Docstring."""

# pyright: reportUnknownMemberType=false, reportUnknownVariableType=false
# cSpell:ignore palworld gvas palsav paltypes

import json
from re import Pattern
import re
from typing import Any
#from logger import pprint
from json_tools import json_serialize
from palworld_save_tools.archive import UUID

def list_transfer_uuid_to_str(_input: dict[str, UUID]) -> list[str]:
    """Transfers a dictionary of string and UUID to a list of strings that are the UUIDs."""
    output: list[str] = []
    for _, i in _input.items():
        output.append(str(i))
    return output


def get_all_storage_id(player_data: dict[str, Any]) -> dict[str, UUID]:
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


def validate_storages(level_data: dict[str, Any], player_data: dict[str, Any]) -> bool:
    r"""
     Validates that all storages defined in ``player_data`` are also defined in ``level_data``.
     """
    returned: bool = True
    json_text: str = json.dumps(level_data, default=json_serialize)
    storage_ids: dict[str, UUID] = get_all_storage_id(player_data)

    for _, _id in storage_ids.items():
        regex: Pattern[str] = re.compile(re.escape(str(_id)))
        found: list[Any] = regex.findall(json_text)
        if len(found) <= 0:
#       if len(found) > 0:
#           pprint(f"[green][bold]INFO:[/bold][/green] Found {len(found)} instances of the old "
#                  f"GUID Unformatted: {str(_id)}", indent=3)
#       else:
#           pprint(f"[yellow][bold]WARN:[/bold][/yellow] No id found with string \"{str(_id)}\"",
#                  indent=3)
            returned = False
    return returned


def update_storages(_id: UUID, json_text: str, player_data: dict[str, Any], k: str) -> None:
    r"""Updates all storages in a collection defined in ``player_data``."""
    regex: Pattern[str] = re.compile(re.escape(str(_id)))
    found: list[Any] = regex.findall(json_text)
    if len(found) == 0:
        save_data: dict[str, Any] = player_data["properties"]["SaveData"]["value"]
        for i, data in save_data.items():
            if i == "PalStorageContainerId" and k == i:
#               pprint(f"[blue][bold]INFO:[/bold][/blue] Setting /properties/SaveData/value/{i}/"
#                      f"value/ID/value = {str(_id)}", indent=3)
                player_data["properties"]["SaveData"]["value"][i]["value"]["ID"] \
                           ["value"] = _id
            elif i == "inventoryInfo":
                for j, _ in data["value"].items():
                    if k == j:
#                       pprint(f"[blue][bold]INFO:[/bold][/blue] Setting /properties/SaveData/value"
#                              f"/{i}/value/{j}/value/ID/value = {str(_id)}", indent=3)
                        player_data["properties"]["SaveData"]["value"][i]["value"][j] \
                                   ["value"]["ID"]["value"] = _id


def correct_storages(level_data: dict[str, Any], new_player_data: dict[str, Any],
                     old_player_data: dict[str, Any]) -> bool:
    r"""
    Corrects missing storages that all storages defined in either,
    ``new_player_data`` or ``old_player_data``, to the other one that it is missing in.
    """
    json_text: str = json.dumps(level_data, default=json_serialize)
    new_storage_ids: dict[str, UUID] = get_all_storage_id(new_player_data)
    old_storage_ids: dict[str, UUID] = get_all_storage_id(old_player_data)

#   pprint("[blue][bold]INFO:[/bold][/blue] Validating new player data", indent=3)
    if not validate_storages(level_data, new_player_data):
        for k, _id in new_storage_ids.items():
            update_storages(_id, json_text, new_player_data, k)
#   pprint("[blue][bold]INFO:[/bold][/blue] Validating old player data", indent=3)
    if not validate_storages(level_data, old_player_data):
        for k, _id in old_storage_ids.items():
            update_storages(_id, json_text, old_player_data, k)

#   pprint("[blue][bold]INFO:[/bold][/blue] Validating both new and old player data", indent=3)
    return (validate_storages(level_data, new_player_data) and
            validate_storages(level_data, old_player_data))

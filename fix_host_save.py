#!/usr/env python3

"""Temporary Module Docstring."""

# pyright: reportUnknownMemberType=false, reportUnknownVariableType=false
# cSpell:ignore palworld gvas palsav paltypes

import json
import os
from shutil import SameFileError
import sys
import re
from typing import Any
from logger import pprint

from json_tools import json_serialize, parse_constant, load_json, write_json
from local_types import JsonType
from validate_storages_exist import correct_storages, validate_storages

from palworld_save_tools.archive import UUID
from palworld_save_tools.gvas import GvasFile
from palworld_save_tools.palsav import compress_gvas_to_sav, decompress_sav_to_gvas
from palworld_save_tools.paltypes import PALWORLD_CUSTOM_PROPERTIES, PALWORLD_TYPE_HINTS

def exit_with_message(message: str | BaseException, code: int = 0) -> None:
    """Exits the command line if running in main thread."""
    is_cli: bool = os.environ.get("is_cli") is not None and os.environ.get("is_cli") == "true"
    if is_cli:
        pprint(message, indent=1)
        sys.exit(code)
    else:
        if isinstance(message, str):
            raise Exception(message) # pylint: disable=W0719
        raise message


def json_text_operation(json_data: JsonType, new_guid_formatted: str, old_guid_formatted: str,
                        new_guid: str, old_guid: str, new_instance_id: UUID,
                        old_instance_id: UUID) -> None:
    r"""
    Finds all text in the json data that matches the old_guid and replaces it with the new_guid,
    along with ``old_guid_formatted`` to ``new_guid_formatted``, and ``new_instance_id`` to
    ``old_instance_id``
    """
    json_text: str = json.dumps(json_data, default=json_serialize)

    found: list[Any] = re.compile(re.escape(str(old_guid_formatted))).findall(json_text)

    if len(found) > 0:
        pprint(f"[green][bold]INFO:[/bold][/green] Found {len(found)} instances of the "
               f"old GUID Formatted: {old_guid_formatted}", indent=1)
        json_text = json_text.replace(old_guid_formatted, new_guid_formatted)
#   else:
#       pprint("[yellow][bold]WARN:[/bold][/yellow] No item found with string "
#             f"\"{old_guid_formatted}\"", indent=1)

    found = re.compile(re.escape(str(old_guid))).findall(json_text)

    if len(found) > 0:
        pprint(f"[green][bold]INFO:[/bold][/green] Found {len(found)} instances of the old "
               f"GUID Unformatted: {old_guid}", indent=1)
        json_text = json_text.replace(old_guid, new_guid)
#   else:
#       pprint("[yellow][bold]WARN:[/bold][/yellow] No item found with string "
#             f"\"{old_guid}\"", indent=1)

    found = re.compile(re.escape(str(old_instance_id))).findall(json_text)

    if len(found) > 0:
        pprint(f"[green][bold]INFO:[/bold][/green] Found {len(found)} instances of the old"
               f" Instance Id: {str(old_instance_id)}", indent=1)
        json_text = json_text.replace(str(old_instance_id), str(new_instance_id))
#   else:
#       pprint("[yellow][bold]WARN:[/bold][/yellow] No item found with string "
#             f"\"{old_instance_id}\"", indent=1)

    json_data = json.loads(json_text, parse_constant=parse_constant)


def guild_fix_method(level_json: JsonType, new_guid_formatted: str, old_guid_formatted: str,
                     old_instance_id: UUID) -> None:
    """Fixes the host save based on specified inputs."""
    group_ids_len = len(level_json['properties']['worldSaveData']['value']['GroupSaveDataMap'] \
                                  ['value'])
    for i in range(group_ids_len):
        group_id = level_json['properties']['worldSaveData']['value']['GroupSaveDataMap']['value'] \
                             [i]
        if group_id['value']['GroupType']['value']['value'] == 'EPalGroupType::Guild':
            group_data = group_id['value']['RawData']['value']
            if 'individual_character_handle_ids' in group_data:
                handle_ids = group_data['individual_character_handle_ids']
                for j, _ in enumerate(handle_ids):
                    if handle_ids[j]['instance_id'] == old_instance_id:
                        level_json['properties']['worldSaveData']['value']['GroupSaveDataMap'] \
                                  ['value'][i]['value']['RawData']['value'] \
                                  ['individual_character_handle_ids'][j] \
                                  ['guid'] = new_guid_formatted
            if 'admin_player_uid' in group_data:
                if old_guid_formatted == group_data['admin_player_uid']:
                    level_json['properties']['worldSaveData']['value']['GroupSaveDataMap'] \
                              ['value'][i]['value']['RawData']['value'] \
                              ['admin_player_uid'] = new_guid_formatted
            if 'players' in group_data:
                for j, _ in enumerate(group_data['players']):
                    if old_guid_formatted == group_data['players'][j]['player_uid']:
                        level_json['properties']['worldSaveData']['value']['GroupSaveDataMap'] \
                                  ['value'][i]['value']['RawData']['value']['players'][j] \
                                  ['player_uid'] = new_guid_formatted


def patch_old_save(new_json: JsonType, old_json: JsonType, level_json: JsonType,
                   new_guid_formatted: str) -> tuple[UUID, UUID]:
    """Fixes the host save based on specified inputs."""

    # Replace all instances of the old GUID with the new GUID.
    pprint("Modifying JSON save data...", end="\n", flush=True, indent=1)

    # Player data replacement.
    old_json["properties"]["SaveData"]["value"]["PlayerUId"]["value"] = new_guid_formatted
    old_json["properties"]["SaveData"]["value"]["IndividualId"]["value"]["PlayerUId"] \
            ["value"] = new_guid_formatted
    old_instance_id: UUID = old_json["properties"]["SaveData"]["value"]["IndividualId"]["value"] \
                                    ["InstanceId"]["value"]
    new_instance_id: UUID = new_json["properties"]["SaveData"]["value"]["IndividualId"]["value"] \
                                    ["InstanceId"]["value"]

    # Level data replacement.
    instance_ids_len: int = len(level_json["properties"]["worldSaveData"]["value"] \
                                          ["CharacterSaveParameterMap"]["value"])
    for i in range(instance_ids_len):
        instance_id: str = level_json["properties"]["worldSaveData"]["value"] \
                                     ["CharacterSaveParameterMap"]["value"][i] \
                                     ["key"]["InstanceId"]["value"]
        if instance_id == old_instance_id:
            level_json["properties"]["worldSaveData"]["value"]["CharacterSaveParameterMap"] \
                      ["value"][i]["key"]["PlayerUId"]["value"] = new_guid_formatted
            break

    return (new_instance_id, old_instance_id)

def fix_host_save(save_path: str, new_guid: str, old_guid: str, guild_fix: bool,
                  level_sav: JsonType | None = None) -> None:
    """Fixes the host save based on specified inputs."""

    is_cli: bool = os.environ.get("is_cli") is not None and os.environ.get("is_cli") == "true"

    # Users accidentally include the .sav file extension when copying the GUID over. Only the GUID
    # should be passed.
    if new_guid[-4:] == ".sav" or old_guid[-4:] == ".sav":
        exit_with_message(FileNotFoundError("It looks like you're providing the whole name "
                          "of the file instead of just the GUID. For example, instead of using "
                          "\"<GUID>.sav\" in the command, you should be using only the GUID."), 1)

    # Users accidentally remove characters from their GUIDs when copying it over. All GUIDs should
    # be 32 characters long.
    if len(new_guid) != 32:
        exit_with_message(SyntaxError("Your <new_guid> should be 32 characters long, but it is "
                         f"{str(len(new_guid))} characters long. Make sure you copied the exact "
                          "GUID."), 1)

    if len(old_guid) != 32:
        exit_with_message(SyntaxError("Your <old_guid> should be 32 characters long, but it is "
                         f"{str(len(new_guid))} characters long. Make sure you copied the exact "
                          "GUID."), 1)

    # Users accidentally pass the same GUID as the new_guid and old_guid. They should be different.
    if new_guid == old_guid:
        exit_with_message(SameFileError("ERROR: It looks like you're using the same GUID for both "
                          "the <new_guid> and <old_guid> argument. Remember, you're moving GUIDs so"
                          " you need your old one and your new one."), 1)

    # Apply expected formatting for the GUID.
    new_guid_formatted = (f"{new_guid[:8]}-{new_guid[8:12]}-{new_guid[12:16]}-{new_guid[16:20]}"
                          f"-{new_guid[20:]}").lower()
    old_guid_formatted = (f"{old_guid[:8]}-{old_guid[8:12]}-{old_guid[12:16]}-{old_guid[16:20]}"
                          f"-{old_guid[20:]}").lower()

    level_sav_path = f"{save_path}/Level.sav"
    old_sav_path = f"{save_path}/Players/{old_guid}.sav"
    new_sav_path = f"{save_path}/Players/{new_guid}.sav"
    # Unused variables:
    #level_json_path = f"{level_sav_path}.json"
    #old_json_path = f"{old_sav_path}.json"

    # save_path must exist in order to use it.
    if not os.path.exists(save_path):
        exit_with_message(FileNotFoundError(f"Your given <save_path> of \"{save_path}\" does not "
                          "exist. Did you enter the correct path to your save folder?"), 1)

    # The player needs to have created a character on the dedicated server and that save is used
    # for this script.
    if not os.path.exists(new_sav_path):
        exit_with_message(FileNotFoundError("Your player save does not exist. Did you enter the "
                          "correct new GUID of your player? It should look like "
                          "\"8E910AC2000000000000000000000000\".\nDid your player create their "
                          "character with the provided save? Once they create their character, a "
                         f"file called \"{new_sav_path}\" should appear. Look back over the steps "
                          "in the README on how to get your new GUID."), 1)

    if is_cli:
        # Warn the user about potential data loss.
        exit_with_message("[bold][yellow]WARNING:[/yellow][/bold] Running this script WILL change "
                          "your save files and could potentially corrupt your data. It is HIGHLY "
                          "recommended that you make a backup of your save folder before continuing"
                          ". Press enter if you would like to continue.")
        input("> ")

    # Convert save files to JSON so it is possible to edit them.
    level_json: JsonType = {}
    if level_sav is None:
        level_json = load_json(level_sav_path, sav_to_json)
    else:
        level_json = level_sav
    old_json: JsonType = load_json(old_sav_path, sav_to_json)
    new_json: JsonType = load_json(new_sav_path, sav_to_json)
    if old_guid.lower() == "81a80c0a000000000000000000000000":
        if validate_storages(level_json, old_json):
            pprint("[bold][green]SUCCESS:[/green][/bold] Storage validated successfully on old "
                   "player file", indent=1)
        else:
            pprint("[bold][red]FAILURE:[/red][/bold] Storage validated unsuccessfully on old "
                   "player file", indent=1)
            if not correct_storages(level_json, new_json, old_json):
                pprint("[bold][red]FAILURE:[/red][/bold] Storage corrected unsuccessfully on old "
                    "player file", indent=1)
            else:
                pprint("[bold][green]SUCCESS:[/green][/bold] Storage corrected successfully on old "
                    "player file", indent=1)
    if new_guid.lower() == "c8da11f6000000000000000000000000":
        if validate_storages(level_json, new_json):
            pprint("[bold][green]SUCCESS:[/green][/bold] Storage validated successfully on new "
                   "player file", indent=1)
        else:
            pprint("[bold][red]FAILURE:[/red][/bold] Storage validated unsuccessfully on new "
                   "player file", indent=1)
            if correct_storages(level_json, new_json, old_json):
                pprint("[bold][red]FAILURE:[/red][/bold] Storage corrected unsuccessfully on new "
                    "player file", indent=1)
            else:
                pprint("[bold][green]SUCCESS:[/green][/bold] Storage corrected successfully on new "
                    "player file", indent=1)
    new_instance_id: UUID
    old_instance_id: UUID
    output: tuple[UUID, UUID] = patch_old_save(new_json, old_json, level_json, new_guid_formatted)
    new_instance_id = output[0]
    old_instance_id = output[1]

    # Guild data replacement.
    if guild_fix:
        guild_fix_method(level_json, new_guid_formatted, old_guid_formatted, old_instance_id)

    json_text_operation(level_json, new_guid_formatted, old_guid_formatted, new_guid,
                        old_guid, new_instance_id, old_instance_id)

    pprint("Done!", flush=True, indent=1)

    # Convert JSON back to save files.
    if level_sav is None:
        write_json(level_json, level_sav_path, json_to_sav)
#   if Path(os.path.join(os.getcwd(), old_sav_path)).exists():
#       write_json(old_json, old_sav_path, json_to_sav)

    # We must rename the patched save file from the old GUID to the new GUID for the server to
    # recognize it.
#   if os.path.exists(new_sav_path):
#       os.remove(new_sav_path)
#   os.rename(old_sav_path, new_sav_path)


def sav_to_json(filepath: str) -> dict[str, Any]:
    """Transform the sav file data to json data"""
    pprint(f"Converting {filepath} to JSON...", end="\n", flush=True, indent=1)
    with open(filepath, "rb") as f:
        data = f.read()
        raw_gvas, _ = decompress_sav_to_gvas(data)
    gvas_file = GvasFile.read(raw_gvas, PALWORLD_TYPE_HINTS, PALWORLD_CUSTOM_PROPERTIES,
                              allow_nan=True)
    json_data = gvas_file.dump()
    pprint("Done!", flush=True, indent=1)
    return json_data


def json_to_sav(json_data: dict[str, Any], output_filepath: str) -> None:
    """Transform the json_data to a new sav file"""
    pprint(f"Converting JSON to {output_filepath}...", end="\n", flush=True, indent=1)
    gvas_file = GvasFile.load(json_data)
    if (("Pal.PalWorldSaveGame" in gvas_file.header.save_game_class_name)
        or ("Pal.PalLocalWorldSaveGame" in gvas_file.header.save_game_class_name)):
        save_type = 0x32
    else:
        save_type = 0x31
    sav_file = compress_gvas_to_sav(gvas_file.write(PALWORLD_CUSTOM_PROPERTIES), save_type)
    with open(output_filepath, "wb") as f:
        f.write(sav_file)
    pprint("Done!", flush=True, indent=1)


def main() -> None:
    """Main function from command line"""
    os.environ.setdefault("is_cli", "true")
    _guild_fix: bool = True
    if sys.argv[3].lower() == "true":
        _guild_fix = True
    elif sys.argv[3].lower() == "false":
        _guild_fix = False
    else:
        pprint("ERROR: Invalid <guild_fix> argument. It should be either \"True\" or \"False\".", indent=1)
        sys.exit(1)
    fix_host_save(sys.argv[0], sys.argv[1], sys.argv[2], _guild_fix)


if __name__ == "__main__":
    main()

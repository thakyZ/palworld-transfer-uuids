#!/usr/env python3

"""Temporary Module Docstring."""

# pyright: reportUnknownMemberType=false
# cSpell:ignore palworld gvas palsav paltypes

import os
from shutil import SameFileError
import sys
from typing import Any
from rich import print as pprint

from palworld_save_tools.gvas import GvasFile
from palworld_save_tools.palsav import compress_gvas_to_sav, decompress_sav_to_gvas
from palworld_save_tools.paltypes import PALWORLD_CUSTOM_PROPERTIES, PALWORLD_TYPE_HINTS

def exit_with_message(message: str | BaseException, code: int = 0) -> None:
    """Exits the command line if running in main thread."""
    is_cli: bool = os.environ.get("is_cli") is not None and os.environ.get("is_cli") == "true"
    if is_cli:
        pprint(message)
        sys.exit(code)
    else:
        if isinstance(message, str):
            raise Exception(message) # pylint: disable=W0719
        raise message


def fix_host_save(save_path: str, new_guid: str, old_guid: str, guild_fix: bool) -> None:
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
    old_guid_formatted = (f"{new_guid[:8]}-{new_guid[8:12]}-{new_guid[12:16]}-{new_guid[16:20]}"
                          f"-{new_guid[20:]}").lower()

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
        exit_with_message("WARNING: Running this script WILL change your save files and could "
                          "potentially corrupt your data. It is HIGHLY recommended that you make a "
                          "backup of your save folder before continuing. Press enter if you would "
                          "like to continue.")
        input("> ")

    # Convert save files to JSON so it is possible to edit them.
    level_json = sav_to_json(level_sav_path)
    old_json = sav_to_json(old_sav_path)

    # Replace all instances of the old GUID with the new GUID.
    pprint("Modifying JSON save data...", end="", flush=True)

    # Player data replacement.
    old_json["properties"]["SaveData"]["value"]["PlayerUId"]["value"] = new_guid_formatted
    old_json["properties"]["SaveData"]["value"]["IndividualId"]["value"]["PlayerUId"] \
            ["value"] = new_guid_formatted
    old_instance_id = old_json["properties"]["SaveData"]["value"]["IndividualId"]["value"] \
                              ["InstanceId"]["value"]

    # Level data replacement.
    instance_ids_len = len(level_json["properties"]["worldSaveData"]["value"] \
                                     ["CharacterSaveParameterMap"]["value"])
    for i in range(instance_ids_len):
        instance_id = level_json["properties"]["worldSaveData"]["value"] \
                                ["CharacterSaveParameterMap"]["value"][i] \
                                ["key"]["InstanceId"]["value"]
        if instance_id == old_instance_id:
            level_json["properties"]["worldSaveData"]["value"]["CharacterSaveParameterMap"] \
                      ["value"][i]["key"]["PlayerUId"]["value"] = new_guid_formatted
            break

    # Guild data replacement.
    if guild_fix:
        for i, _ in enumerate(level_json["properties"]["worldSaveData"]["value"] \
                                        ["GroupSaveDataMap"]["value"]):
            group_id = level_json["properties"]["worldSaveData"]["value"]["GroupSaveDataMap"] \
                                 ["value"][i]
            if group_id["value"]["GroupType"]["value"]["value"] == "EPalGroupType::Guild":
                group_data = group_id["value"]["RawData"]["value"]
                if "individual_character_handle_ids" in group_data:
                    handle_ids = group_data["individual_character_handle_ids"]
                    for j, _ in enumerate(handle_ids):
                        if handle_ids[j]["instance_id"] == old_instance_id:
                            handle_ids[j]["guid"] = new_guid_formatted
                if "admin_player_uid" in group_data:
                    if old_guid_formatted == group_data["admin_player_uid"]:
                        group_data["admin_player_uid"] = new_guid_formatted
                if "players" in group_data:
                    for j, _ in enumerate(group_data["players"]):
                        if old_guid_formatted == group_data["players"][j]["player_uid"]:
                            group_data["players"][j]["player_uid"] = new_guid_formatted
    pprint("Done!", flush=True)

    # Convert JSON back to save files.
    json_to_sav(level_json, level_sav_path)
    json_to_sav(old_json, old_sav_path)

    # We must rename the patched save file from the old GUID to the new GUID for the server to
    # recognize it.
    if os.path.exists(new_sav_path):
        os.remove(new_sav_path)
    os.rename(old_sav_path, new_sav_path)
    pprint("Fix has been applied! Have fun!")

def sav_to_json(filepath: str) -> dict[str, Any]:
    """Transform the sav file data to json data"""
    pprint(f"Converting {filepath} to JSON...", end="", flush=True)
    with open(filepath, "rb") as f:
        data = f.read()
        raw_gvas, _ = decompress_sav_to_gvas(data)
    gvas_file = GvasFile.read(raw_gvas, PALWORLD_TYPE_HINTS, PALWORLD_CUSTOM_PROPERTIES,
                              allow_nan=True)
    json_data = gvas_file.dump()
    pprint("Done!", flush=True)
    return json_data

def json_to_sav(json_data: dict[str, Any], output_filepath: str) -> None:
    """Transform the json_data to a new sav file"""
    pprint(f"Converting JSON to {output_filepath}...", end="", flush=True)
    gvas_file = GvasFile.load(json_data)
    if (("Pal.PalWorldSaveGame" in gvas_file.header.save_game_class_name)
        or ("Pal.PalLocalWorldSaveGame" in gvas_file.header.save_game_class_name)):
        save_type = 0x32
    else:
        save_type = 0x31
    sav_file = compress_gvas_to_sav(gvas_file.write(PALWORLD_CUSTOM_PROPERTIES), save_type)
    with open(output_filepath, "wb") as f:
        f.write(sav_file)
    pprint("Done!", flush=True)

def main() -> None:
    """Main function from command line"""
    os.environ.setdefault("is_cli", "true")
    _guild_fix: bool = True
    if sys.argv[3].lower() == "true":
        _guild_fix = True
    elif sys.argv[3].lower() == "false":
        _guild_fix = False
    else:
        pprint("ERROR: Invalid <guild_fix> argument. It should be either \"True\" or \"False\".")
        sys.exit(1)
    fix_host_save(sys.argv[0], sys.argv[1], sys.argv[2], _guild_fix)

if __name__ == "__main__":
    main()

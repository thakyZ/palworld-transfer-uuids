#!/usr/env python3

# pyright: reportUnknownMemberType=false
# cSpell:ignore palworld

"""Temporary Module Docstring."""

import os
import json
from pathlib import Path
from typing import TypeAlias
import re
from re import Match
from rich import print as pprint

from fix_host_save import fix_host_save

WhoJson: TypeAlias = dict[str, list[dict[str, int | str]]]

def transform_to_whole_name(_input: str) -> str:
    """Temporary Method Docstring."""
    expected_length: int = len("00000000000000000000000000000000")
    input_length: int = len(_input)
    difference_length: int = expected_length - input_length
    if difference_length < 0:
        raise ArithmeticError("Gotten length is longer than expected.")
    additional_zeros: str = "0" * difference_length
    return f"{_input.upper()}{additional_zeros}"

def find_save_dir(root: Path) -> str:
    """Finds the save directory locally"""
    for _root, directories, _ in os.walk(root):
        for _ in directories:
            level_sav: Path = Path(os.path.join(_root, "Level.sav"))
            if Path(_root).parent.name == root.name and level_sav.exists():
                return Path(_root).name

    raise FileNotFoundError("No save directory found.")

def main() -> None:
    """Temporary Method Docstring."""
    root: Path = Path(os.getcwd())
    sav_dir: str = find_save_dir(root)
    who_json: WhoJson = {}

    with Path(os.path.join(root, "who.json")).open("r", encoding="utf8") as who_read:
        who_json = json.loads(who_read.read())
        who_read.close()

    for index, item in enumerate(who_json["user_transfer"]):
        _from_int: str | int = item["from"]
        _to_int: str | int = item["to"]
        if isinstance(_from_int, int) and isinstance(_to_int, int):
            who_json["user_transfer"][index]["from"] = transform_to_whole_name(hex(_from_int)[2:])
            who_json["user_transfer"][index]["to"] = transform_to_whole_name(hex(_to_int)[2:])
        else:
            raise TypeError("_from or _to is not type of int.")

    for index, item in enumerate(who_json["user_transfer"]):
        _from_str: str | int = item["from"]
        _to_str: str | int = item["to"]

        if isinstance(_from_str, str) and isinstance(_to_str, str):
            if int(_to_str, base=16) == 0:
                pprint(f"[yellow][bold]WARN:[/bold][/yellow] [blue]{item["#comment"]}[/blue] has no"
                        " [magenta]to[/magenta] variable set.")
                continue
            if int(_from_str, base=16) == 0:
                pprint(f"[yellow][bold]WARN:[/bold][/yellow] [blue]{item["#comment"]}[/blue] has no"
                        " [magenta]from[/magenta] variable set.")
                continue
            try:
                fix_host_save(sav_dir, _to_str, _from_str, True)
            except FileNotFoundError as op_error:
                if "Your player save does not exist" in str(op_error):
                    gotten: Match[str] | None = re.match(r"Player\/([A-F0-9]+).sav\"",str(op_error))
                    if gotten is not None:
                        pprint("[yellow][bold]WARN:[/bold][/yellow] Failed to find player file with"
                              f" name {gotten.groups()}")
                    else:
                        pprint("[yellow][bold]WARN:[/bold][/yellow] Failed to find player file with"
                              f" name {_to_str} or {_from_str}")
                else:
                    raise op_error
            except Exception as error:
                raise error
        else:
            raise TypeError("_from or _to is not type of str.")


if __name__ == "__main__":
    main()

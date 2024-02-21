#!/usr/env python3

# pyright: reportUnknownMemberType=false
# cSpell:ignore palworld

"""Temporary Module Docstring."""

import os
from pathlib import Path
from typing import Any
import re
import sys
from re import Match

from fix_host_save import fix_host_save, sav_to_json
from logger import pprint
from who_config import WhoConfig, WhoConfigUser, load_who_config


def exit_with_message(message: str | BaseException, code: int = 0) -> Any:
    """Exits the command line if running in main thread."""
    is_cli: bool = os.environ.get("is_cli") is not None and os.environ.get("is_cli") == "true"
    if is_cli:
        if isinstance(message, str) and code == 0:
            pprint(f"[green]Completed:[/green] {message}", indent=0)
        elif isinstance(message, str) and code > 0:
            pprint(f"[bold][red]Error:[/red][/bold] {message}", indent=0)
        elif isinstance(message, BaseException):
            pprint(f"[bold][red]Error:[/red][/bold] {message}", indent=0)
        sys.exit(code)
    else:
        if isinstance(message, str):
            raise Exception(message) # pylint: disable=W0719
        raise message


def find_save_dir(root: Path) -> str:
    """Finds the save directory locally"""
    for _root, directories, _ in os.walk(root):
        for _ in directories:
            level_sav: Path = Path(os.path.join(_root, "Level.sav"))
            if Path(_root).parent.name == root.name and level_sav.exists():
                return Path(_root).name
    return exit_with_message(FileNotFoundError("No save directory found."), 1)


def enumerate_user_transfer(who_json: WhoConfig, sav_dir: str):
    """Temporary Method Docstring."""
    for _, _item in enumerate(who_json.user_transfer):
        item: WhoConfigUser = WhoConfigUser(_item)
        if isinstance(item.new, str) and isinstance(item.old, str):
            if int(item.old, base=16) == 0:
                pprint(f"[yellow][bold]WARN:[/bold][/yellow] [blue]{item.name}[/blue] has no"
                        " [magenta]to[/magenta] variable set.", indent=0)
                continue
            if int(item.new, base=16) == 0:
                pprint(f"[yellow][bold]WARN:[/bold][/yellow] [blue]{item.name}[/blue] has no"
                        " [magenta]from[/magenta] variable set.", indent=0)
                continue
            try:
                level_sav_path: str = f"{sav_dir}/Level.sav"
                level_json: dict[str, Any] = sav_to_json(level_sav_path)
                pprint(f"[green][bold]INFO:[/bold][/green] Modifying {item.name}.", indent=0)
                fix_host_save(sav_dir, item.new, item.old, True, level_json)
            except FileNotFoundError as op_error:
                if "Your player save does not exist" in str(op_error):
                    gotten: Match[str] | None = re.match(r"Player\/([A-F0-9]+).sav\"",str(op_error))
                    if gotten is not None:
                        pprint("[yellow][bold]WARN:[/bold][/yellow] Failed to find player file with"
                              f" name {gotten.groups()}", indent=0)
                    else:
                        pprint("[yellow][bold]WARN:[/bold][/yellow] Failed to find player file with"
                              f" name {item.old} or {item.new}", indent=0)
                else:
                    raise op_error
            except Exception as error:
                raise error
        else:
            raise TypeError("_new or _old is not type of str.")

def main() -> None:
    """Temporary Method Docstring."""
    root: Path = Path(os.getcwd())
    sav_dir: str = find_save_dir(root)
    who_json: WhoConfig = load_who_config(Path(os.path.join(root, "who.json")))

    enumerate_user_transfer(who_json, sav_dir)


if __name__ == "__main__":
    main()

#!/usr/env python3

"""Temporary Module Docstring."""

# pyright: reportUnknownMemberType=false, reportUnknownVariableType=false
# cSpell:ignore palworld gvas palsav paltypes

import os
import sys
#from typing import Any, Callable, Dict, List, Union
#JsonType = Union[None, int, str, bool, List["JsonType"], Dict[str, "JsonType"]]
from typing import Any, Callable, NoReturn
from logger import pprint
JsonType = dict[str, Any]
CustomJsonReader = Callable[[str], Any]
CustomJsonWriter = Callable[[dict[str, Any], str], Any]
Unknown = Any

def exit_with_message(message: str | BaseException, code: int = 0) -> NoReturn:
    """Exits the command line if running in main thread."""
    is_cli: bool = os.environ.get("is_cli") is not None and os.environ.get("is_cli") == "true"

    if is_cli:
        pprint(message, indent=1)
        sys.exit(code)
    else:
        if isinstance(message, str):
            raise Exception(message) # pylint: disable=W0719
        raise message

#!/usr/env python3

"""Temporary Module Docstring."""

# pyright: reportUnknownMemberType=false, reportUnknownVariableType=false
# cSpell:ignore palworld gvas palsav paltypes

#from typing import Any, Callable, Dict, List, Union
#JsonType = Union[None, int, str, bool, List["JsonType"], Dict[str, "JsonType"]]
from typing import Any, Callable
JsonType = dict[str, Any]
CustomJsonReader = Callable[[str], Any]
CustomJsonWriter = Callable[[dict[str, Any], str], Any]

#!/usr/env python3

"""Temporary Module Docstring."""

# pyright: reportUnknownMemberType=false, reportUnknownVariableType=false
# cSpell:ignore palworld gvas palsav paltypes

import json
from pathlib import Path
from typing import Any, Literal, Union

from local_types import JsonType

class WhoConfigUser():
    """Temporary Class Docstring."""
    _ValidConstructors = Union[None, dict[str, Any], JsonType, "WhoConfigUser"]
    _ValidConstructorsN = Union[dict[str, Any], JsonType, "WhoConfigUser"]
    _RealValues = Literal["name", "index", "comment", "old", "new"]
    _FakeValues = Literal["name", "#index", "#comment", "old", "new"]
    _basicList: list[_RealValues] = ["name", "index", "comment", "old", "new"]

    _name: str | None = None
    @property
    def name(self) -> str | None:
        """Display name of the user."""
        return self._name
    @name.setter
    def name(self, a: str | None):
        self._name = a


    _index: int | None = None
    @property
    def index(self) -> int | None:
        """Index of the user."""
        return self._index
    @index.setter
    def index(self, a: int | None):
        self._index = a


    _comment: str | None = None
    @property
    def comment(self) -> str | None:
        """Comments of the user."""
        return self._comment
    @comment.setter
    def comment(self, a: str | None):
        self._comment = a


    _old: str | int = 0
    @property
    def old(self) -> str | int:
        """Old UUID of the user."""
        return self._old
    @old.setter
    def old(self, a: str | int):
        self._old = a


    _new: str | int = 0
    @property
    def new(self) -> str | int:
        """New UUID of the user."""
        return self._new
    @new.setter
    def new(self, a: str | int):
        self._new = a


    def __getitem__(self, __key: str) -> str | int | None:
        if __key == "name":
            return self.name
        if __key in ["#comment", "comment"]:
            return self.comment
        if __key in ["#index", "index"]:
            return self.index
        if __key == "old":
            return self.old
        if __key == "new":
            return self.new
        raise KeyError

    def __get__(self, __instance: "WhoConfigUser", __key: str) -> str | int | None:
        return __instance.__getitem__(__key)


    def __setitem__(self, __key: str, __value: str | int | None) -> None:
        if __key == "name" and not isinstance(__value, int):
            self.name = __value
        elif __key in ["#comment", "comment"] and not isinstance(__value, int):
            self.comment = __value
        elif __key in ["#index", "index"] and not isinstance(__value, str):
            self.index = __value
        elif __key == "old" and __value is not None:
            self.old = __value
        elif __key == "new" and __value is not None:
            self.new = __value
        else:
            raise KeyError

    def __set__(self, __key: str, __value: str | int | None) -> None:
        return self.__setitem__(__key, __value)


    def keys(self) -> list[_RealValues]:
        """Gets the keys of this WhoConfigUser instance"""
        return self._basicList


    def __transform_pound_keys__(self, user_transfer_entry: _ValidConstructorsN) -> None:
        for key in user_transfer_entry.keys():
            if str(key) == "#comment":
                self["comment"] = user_transfer_entry[key]
            elif str(key) == "#index":
                self["index"] = user_transfer_entry[key]
            else:
                self[key] = user_transfer_entry[key]

    def __transform_uuid_values__(self):
        if isinstance(self._new, int) and isinstance(self._old, int):
            self._new = transform_old_whole_name(hex(self._new)[2:])
            self._old = transform_old_whole_name(hex(self._old)[2:])

    def __init__(self, arg: _ValidConstructors) -> None:
        if arg is not None:
            self.__transform_pound_keys__(arg)
        self.__transform_uuid_values__()


class WhoConfig():
    """Temporary Class Docstring."""
    _ValidConstructors = Union[None, dict[str, Any], JsonType, "WhoConfig"]
    _RealValues = Literal["user_transfer"]
    _basicList: list[_RealValues] = ["user_transfer"]

    _user_transfer: list[WhoConfigUser] = []
    @property
    def user_transfer(self) -> list[WhoConfigUser]:
        """New UUID of the user."""
        return self._user_transfer
    @user_transfer.setter
    def user_transfer(self, a: list[WhoConfigUser]):
        self._user_transfer = a


    def __getitem__(self, __key: _RealValues) -> list[WhoConfigUser] | None:
        if __key == "user_transfer":
            return self._user_transfer
        raise KeyError

    def __get__(self, __instance: "WhoConfig", __key: _RealValues) -> list[WhoConfigUser] | None:
        return __instance.__getitem__(__key)


    def __setitem__(self, __key: _RealValues, __value: list[WhoConfigUser]) -> None:
        if __key == "user_transfer" or __key == "_user_transfer":
            self._user_transfer = __value
        else:
            raise KeyError

    def __set__(self, __key: _RealValues, __value: list[WhoConfigUser]) -> None:
        return self.__setitem__(__key, __value)


    def keys(self) -> list[_RealValues]:
        """Gets the keys of this WhoConfigUser instance"""
        return self._basicList


    def __update_user_transfer_names__(self) -> None:
        for index, _item in enumerate(self.user_transfer):
            item: WhoConfigUser = WhoConfigUser(_item)
            if item.comment is not None:
                self.user_transfer[index]["name"] = item.comment
            elif item.index is not None:
                self.user_transfer[index]["name"] = f"#{item.index}"
            else:
                self.user_transfer[index]["name"] = f"index: {index}"


    def __init__(self, arg: _ValidConstructors) -> None:
        if arg is not None:
            for _, key in enumerate(self._basicList):
                item = arg[key]
                if item is not None and isinstance(item, list):
                    self[key] = item
        self.__update_user_transfer_names__()


def transform_old_whole_name(_input: str) -> str:
    """Temporary Method Docstring."""
    expected_length: int = len("00000000000000000000000000000000")
    input_length: int = len(_input)
    difference_length: int = expected_length - input_length

    if difference_length < 0:
        raise ArithmeticError("Gotten length is longer than expected.")

    additional_zeros: str = "0" * difference_length
    return f"{_input.upper()}{additional_zeros}"


def load_who_config(path: str | Path) -> WhoConfig:
    """Creates a who config from path."""
    _path: Path = Path(path)
    output: WhoConfig

    with _path.open("r", encoding="utf8") as read_who_config_file:
        output = WhoConfig(json.loads(read_who_config_file.read()))

    return output

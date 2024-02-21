#!/usr/env python3

# pyright: reportUnknownMemberType=false
# cSpell:ignore palworld

"""Temporary Module Docstring."""

from typing import Any, Iterable, Optional, Union
from rich.console import Console, JustifyMethod, OverflowMethod
from rich.style import Style
from rich.terminal_theme import TerminalTheme

TERM_THEME: TerminalTheme = TerminalTheme(
    background=( 19,  19,  19),
    foreground=(214, 219, 229),
    normal=[( 31,  31,  31), # Dark Black
            (248,  17,  24), # Dark Red
            ( 45, 197,  94), # Dark Green
            (236, 186,  15), # Dark Yellow
            ( 42, 132, 210), # Dark Blue
            ( 78,  90, 183), # Dark Purple
            ( 16, 129, 214), # Dark Cyan
            (214, 219, 229)],# Dark White
    bright=[(214, 219, 229), # Light Black
            (222,  53,  46), # Light Red
            ( 29, 211,  97), # Light Green
            (243, 189,   9), # Light Yellow
            ( 16, 129, 214), # Light Blue
            ( 83,  80, 185), # Light Purple
            ( 15, 125, 219), # Light Cyan
            (255, 255, 255)] # Light White
)

CONSOLE: Console = Console(color_system="256", force_terminal=True, force_jupyter=False,
                           force_interactive=True, soft_wrap=True)


def list_prepend(__list: Iterable[Any], __object: Any) -> Iterable[Any]:
    new_list_obj: list[Any] = []
    new_list_obj.append(__object)
    for item in __list:
        new_list_obj.append(item)
    return new_list_obj


def pprint(*objects: Any, indent: int = 0, sep: str = " ", end: str = "\n",
            style: Optional[Union[str, Style]] = None, justify: Optional[JustifyMethod] = None,
            overflow: Optional[OverflowMethod] = None, no_wrap: Optional[bool] = None,
            emoji: Optional[bool] = None, markup: Optional[bool] = None,
            highlight: Optional[bool] = None, width: Optional[int] = None,
            height: Optional[int] = None, crop: bool = True,
            soft_wrap: Optional[bool] = None, new_line_start: bool = False,
            # pylint: disable-next=W0613
            flush: bool = False) -> None:
    # pylint: disable=C0301
    """Print to the console.

    Args:
        objects (positional args): Objects to log to the terminal.
        indent (int, optional): Indent for the number of nested functions.
        sep (str, optional): String to write between print data. Defaults to " ".
        end (str, optional): String to write at end of print data. Defaults to "\\\\n".
        style (Union[str, Style], optional): A style to apply to output. Defaults to None.
        justify (str, optional): Justify method: "default", "left", "right", "center", or "full". Defaults to ``None``.
        overflow (str, optional): Overflow method: "ignore", "crop", "fold", or "ellipsis". Defaults to None.
        no_wrap (Optional[bool], optional): Disable word wrapping. Defaults to None.
        emoji (Optional[bool], optional): Enable emoji code, or ``None`` to use console default. Defaults to ``None``.
        markup (Optional[bool], optional): Enable markup, or ``None`` to use console default. Defaults to ``None``.
        highlight (Optional[bool], optional): Enable automatic highlighting, or ``None`` to use console default. Defaults to ``None``.
        width (Optional[int], optional): Width of output, or ``None`` to auto-detect. Defaults to ``None``.
        crop (Optional[bool], optional): Crop output to width of terminal. Defaults to True.
        soft_wrap (bool, optional): Enable soft wrap mode which disables word wrapping and cropping of text or ``None`` for
            Console default. Defaults to ``None``.
        new_line_start (bool, False): Insert a new line at the start if the output contains more than one line. Defaults to ``False``.
        flush (bool, False): Does nothing. Defaults to ``False``.
    """
    # pylint: enable=C0301
    new_objects: Iterable[Any] = tuple(objects)
    for _ in range(indent):
        new_objects = list_prepend(new_objects, "> ")
    new_str = " ".join(new_objects)

    CONSOLE.print(new_str, sep=sep, end=end, style=style, justify=justify, overflow=overflow,
                  no_wrap=no_wrap, emoji=emoji, markup=markup, highlight=highlight, width=width,
                  height=height, crop=crop, soft_wrap=soft_wrap, new_line_start=new_line_start)

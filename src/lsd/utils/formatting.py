#!usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright (c) 2025 OmegaDawn

"""Utilities for formatting data."""


from rich.text import Text
from numpy import clip, ndarray, uint8

from lsd.typing import is_img_data


def format_time(time: float, decimal_places: int = 2) -> str:
    """Converts a duration to its best suited unit.

    The **time** in seconds will be converted to the time unit that is
    best suited for that value. The conversion range is from nanoseconds
    to days.

    Parameters
    ----------
    time : float
        Time in [sec]
    decimal_places : int, optional
        Number of decimal places to show

    Returns
    -------
    str
        The converted time and its unit

    Examples
    --------
    >>> format_time(60)
    '1.00 min'
    >>> format_time(0.000000001234, 3)
    '1.234 ns'
    """

    units = [(86400.0, 'd'),
             (3600.0, 'h'),
             (60.0, 'min'),
             (1.0, 'sec'),
             (1e-3, 'ms'),
             (1e-6, 'µs'),
             (1e-9, 'ns'),]

    unit = 'sec'  # NOSONAR
    for factor, unit in units:
        if abs(time) >= factor:
            time /= factor
            break
    _time = round(time, decimal_places)
    return f'{_time:.{decimal_places}f} {unit}'


def img_to_text(img: ndarray, name: str = '', padding: int = 0,
                show_idx: bool = False) -> Text:
    """Converts an image array to a formatted string representation.

    Each pixel in **img** will be represented by a '█' character and
    colored according to its RGB values. A **name** can be provided that
    is displayed before the image. The **name** can be padded to a
    certain length for better alignment. If desired the pixel indices
    can be shown with **show_idx**.

    .. note::
        The string must be printed on a :class:`rich.console.Console` to
        be displayed with colors.

    Parameters
    ----------
    img : :class:`numpy.ndarray`
        Image array to convert
    name : str, optional
        Name for the image
    padding : int, optional
        Pads **name** to this length
    show_idx : bool, optional
        Shows an axis with pixel indices

    Returns
    -------
    :class:`rich.text.Text`
        String representation of the image

    Examples
    --------
    >>> img = array([[255, 0, 0], [0, 255, 0], [0, 0, 255]])
    >>> img_to_text(img, name='Image', padding=7)
    'Image  ███'
    """

    assert is_img_data(img), "'img' must be an iterable of RGB colors"

    img = clip(img, 0, 255).astype(uint8)

    # Image line
    str_img = Text(no_wrap=True)
    str_img.append(f"{name}".ljust(padding), style='bold')
    for pixel in img:
        r, g, b = pixel
        cvt_color = f"rgb({r},{g},{b})"
        str_img.append("█", style=cvt_color.replace(" ", ""))

    # Index line
    if show_idx:
        pixels = len(img)
        stride = 10 if len(img) > 1000 else 5
        arrow_line = '\n'.ljust(padding + 1) + '▲'
        arrow_line += (' ' * (stride - 1) + '▲') * ((pixels - 1) // stride)
        index_line = '\n' + '0'.rjust(padding + 1)
        for i in [idx for idx in range(0, pixels-stride, stride)]:
            index_line += f'{i + stride}'.rjust(stride)
        if (pixels - 1) % stride - 1 >= len(str(pixels - 1)):
            arrow_line += ' ' * ((pixels - 1) % stride - 1) + '▲'
            index_line += f'{pixels - 1}'.rjust((pixels - 1) % stride)
        str_img.append(arrow_line + index_line)

    return str_img

#!usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright (c) 2025 OmegaDawn

"""Defines types and type checkers."""


from numpy import ndarray, uint8, float32
from typing import Union, Any
from numbers import Number
from numpy.typing import NDArray
from collections.abc import Sequence

from lsd import FLOAT_PRECISION


uint8RGBColor = Union[NDArray[uint8],
                      tuple[int, int, int],
                      Sequence[int]]
"""Iterable with 3 RGB elements with values from ``0`` to ``255``."""

RGBColor = Union[uint8RGBColor,
                 NDArray[float32],
                 tuple[float, float, float],
                 Sequence[float]]
"""Iterable with 3 color channels containing float values.

The values of this type can be negative and out of the ``0`` to ``255``
8-bit RGB range.
"""


def is_color_value(obj: Any) -> bool:
    """Checks if the object can be interpreted a an RGB color.

    Essentially checks if the object is an iterable with 3 numeric
    elements. Will not check if the values are ``int`` or in RGB range.

    Parameters
    ----------
    obj : Any
        Object to check.

    Returns
    -------
    bool
        ``True`` if the **obj** is a color value

    See Also
    --------
    :func:`is_color()`
        Checks if the object is a :attr:`RGBColor`
    :func:`is_img_data()`
        Checks if the object can be interpreted as an image data

    Notes
    -----
    - For a boolean iterable ``True`` is returned.
    """

    try:
        if len(obj) != 3:
            return False
        for el in iter(obj):
            if not isinstance(el, Number):
                return False
        return True
    except (TypeError, AttributeError):
        return False


def is_color(obj: Any) -> bool:
    """Check if the object is of type :attr:`RGBColor`.

    Only :class:`numpy.ndarray` objects with 3 elements are considered
    colors.

    Parameters
    ----------
    obj : Any
        Object to check.

    Returns
    -------
    bool
        ``True`` if the **obj** is a color

    See Also
    --------
    :func:`is_color_value()`
        Checks if the object is an iterable with 3 numeric elements
    :func:`is_img_data()`
        Checks if the object can be interpreted as an image data

    Notes
    -----
    - A boolean data type is accepted as color.
    """

    return isinstance(obj, ndarray) and obj.ndim == 1 and obj.shape[0] == 3


def is_black_color(color: RGBColor) -> bool:
    """Checks if a color is black.

    The **color** is considered black if all color channels are below
    the :attr:`lsd.FLOAT_PRECISION` value.

    Parameters
    ----------
    color : RGBColor
        Object to check.

    Returns
    -------
    bool
        ``True`` if the **color** is black

    See Also
    --------
    :func:`is_color_value()`
        Checks if the object can be interpreted as a color
    :func:`is_color()`
        Checks if the object is a :attr:`RGBColor`
    """

    return (abs(color) < FLOAT_PRECISION).all(axis=0)  # type: ignore


def is_img_data(obj: Any) -> bool:
    """Checks if the object can be interpreted as an list of colors.

    The object must be an iterable with a


    Parameters
    ----------
    obj : Any
        Object to check

    Returns
    -------
    bool
        ``True`` if the **obj** is an image

    See Also
    --------
    :func:`is_color_value()`
        Checks if the object can be interpreted as a color
    :func:`is_color()`
        Checks if the object is a :attr:`RGBColor`
    """

    if isinstance(obj, ndarray):
        return obj.ndim == 2 and obj.shape[1] == 3
    try:
        for el in iter(obj):
            if not is_color_value(el):
                return False
        return True
    except TypeError:
        return False

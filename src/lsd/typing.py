#!usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright (c) 2025 OmegaDawn

"""Typing utilities."""


from typing import Union, Any
from numpy import ndarray, uint8, float32
from numpy.typing import NDArray


uint8RGBColor = Union[NDArray[uint8]]
"""Iterable with 3 RGB elements with values from ``0`` to ``255``."""

RGBColor = Union[uint8RGBColor, NDArray[float32]]
"""Iterable with 3 color channels containing float values.

The values of this type can be negative and out of the ``0`` to ``255``
8-bit RGB range.
"""


def is_color_value(obj: Any) -> bool:
    """Checks if the object can be interpreted a an RGB color.

    Essentially checks if the object is an iterable with 3 numeric
    elements.

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
    :func:`is_color`,
        Checks if the object is a :attr:`RGBColor`
    :func:`is_img_data`,
        Checks if the object can be interpreted as an image data
    """

    try:
        iter(obj)
    except TypeError:
        return False
    try:
        return len(obj) == 3
    except (TypeError, AttributeError):
        try:  # Fallback for iterables without __len__, e.g., generators
            return sum(1 for _ in obj) == 3
        except Exception:  # pylint: disable=W0718
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
    :func:`is_color_value`
        Checks if the object is an iterable with 3 numeric elements
    :func:`is_img_data`
        Checks if the object can be interpreted as an image data
    """

    return isinstance(obj, ndarray) and obj.ndim == 1 and obj.shape[0] == 3


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
    :func:`is_color_value`
        Checks if the object can be interpreted as a color
    :func:`is_color`
        Checks if the object is a :attr:`RGBColor`
    """

    if isinstance(obj, ndarray) and obj.ndim == 2 and obj.shape[1] == 3:
        return True
    try:
        for el in iter(obj):
            if not is_color_value(el):
                return False
        return True
    except TypeError:
        return False

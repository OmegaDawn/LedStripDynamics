#!usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright (c) 2025 OmegaDawn

"""Typing utilities."""


from numpy import uint8, float32
from numpy.typing import NDArray
from typing import TypeVar, Generic, Union, Tuple, List


T = TypeVar('T')
"Type variable for generic types."


class ArrLen3(Generic[T]):
    """Iterable with 3 elements."""

    def __len__(self) -> int:
        ...


RGBColor = Union[ArrLen3[uint8], Tuple[uint8, uint8, uint8], NDArray[uint8],
                 List[uint8]]
"""Iterable with 3 RGB elements with values from ``0`` to ``255``."""

RGBFloatColor = Union[ArrLen3[float32], Tuple[float32, float32, float32],
                      NDArray[float32], List[float32], RGBColor]
"""Iterable with 3 RGB elements with float values.

The values of this type can be negative and out of the ``0`` to ``255``
8-bit RGB range.
"""

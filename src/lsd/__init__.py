#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright (c) 2025 OmegaDawn

"""LedStripDynamics library for stunning LED strip animations."""


from importlib.metadata import version
from numpy import array, uint8
from numpy.random import default_rng
from rich.console import Console

from lsd.typing import uint8RGBColor


__version__ = version('ledstripdynamics')
__repo__ = "https://github.com/OmegaDawn/ledstripdynamics"
__author__ = "Laurenz Nitsche"


FLOAT_PRECISION: float = 1e-6
"""Precision of float value calculations."""
MAIN_COLOR: uint8RGBColor = array([0, 255, 180], dtype=uint8)
"""The default color for most visual effects."""
SEED = None
"""Start seed for generators."""
rng = default_rng(seed=SEED)
"""Random number generator from :mod:`numpy`."""
console = Console()
""":mod:`rich` Console for color output in the terminal."""

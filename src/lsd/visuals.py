#!usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright (c) 2025 OmegaDawn

"""Library of visual effect generators.

This module provides various generator functions for visual effects. The
effects generate image frames that can be shown on a LED strip. Placed
inside an :class:`lsd.strip.Animation` new frames will be continuously
displayed on the strip.

See Also
--------
:class:`lsd.strip.Animation`
    Container for showing visuals
"""


from typing import Generator

from lsd import MAIN_COLOR
from lsd.strip import Image
from lsd.typing import RGBColor


RUNNING = True
"""Flag indicating infinite visuals should keep running.

This can be set to ``False`` to stop infinite visuals from generating.
"""


def blink(leds: int,
          on: RGBColor = MAIN_COLOR, off: RGBColor = (0, 0, 0),
          on_opa: float = 1., off_opa: float = 0.,
          on_frames: int = 5, off_frames: int = 5,
          ) -> Generator[Image, None, None]:
    """Blink effect.

    Alternates between an 'on' and 'off' state indefinitely. Each state
    will be active for a certain amount of frames starting with the
    'on' state.

    Parameters
    ----------
    leds: int
        Size of the images to generate
    on : RGBColor, optional
        Color to use in 'on' state
    off : RGBColor, optional
        Color to use in 'off' state
    on_opa : float, optional
        Opacity to use in 'on' state
    off_opa : float, optional
        Opacity to use in 'off' state
    on_frames : int, optional
        Number of frames to hold the 'on' state
    off_frames : int, optional
        Number of frames to hold the 'off' state

    Yields
    ------
    Image
        Generated frame
    """

    on_img = Image(leds, opa=on_opa)
    off_img = Image(leds, opa=off_opa)
    on_img.fill(on)
    off_img.fill(off)
    while RUNNING:
        for _ in range(on_frames):
            yield on_img
        for _ in range(off_frames):
            yield off_img

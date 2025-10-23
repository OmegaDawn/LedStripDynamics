#!usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright (c) 2025 OmegaDawn

"""Library of visual effect generators.

This module provides various generator functions for visual effects. The
effects generate image frames that can be shown on a LED strip. Placed
inside an :class:`lsd.strip.Animation` new frames will be continuously
displayed on the strip. All visuals must have a ``'leds'`` parameter so
that the generated size can be set to the requirements of an
:class:`Animation`.

See Also
--------
:class:`lsd.strip.Animation`
    Container for showing visuals
"""


from typing import Generator

from numpy import arange

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
    """Infinite blink effect.

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


def rainbow_wave(leds: int, scale: float = 1, speed: float = 0.1
                 ) -> Generator[Image, None, None]:
    """Infinite rainbow wave effect.

    Generates a rainbow moving along the strip indefinitely. The rainbow
    is scaled to the number of **leds** so that the ^full RGB spectrum
    is visible. The rainbow can be scaled by changing the **scale**
    parameter. Larger   # TODO

    """

    from lsd.colors import rainbow_color

    img =  Image(leds, opa=1.)
    scale = 256 * 3 * scale / leds
    pos = 0

    while RUNNING:
        for i in range(leds):
            img[i] = rainbow_color((pos + i) * scale)
        pos = (pos + speed) % 256
        yield img


def runner(leds: int, color: RGBColor = MAIN_COLOR, width: float = 1,
           step_size: float = 0.10) -> Generator[Image, None, None]:
    """Colored block running to the other end of the strip.

    This finite visual shows a block of certain **width** that moves
    from the start to the end of the strip in steps of **step_size**.
    The full **width** is visible at the first frame and the animation
    ends when the block touches the end of the strip. So the total
    distance traveled is ``leds - width``. Everything apart the running
    block is transparent.

    Parameters
    ----------
    leds : int
        Size of the images to generate
    color : RGBColor, optional
        Color of the running block
    width : float, optional
        Pixel width of the running block
    step_size : float, optional
        Distance traveled per frame

    Notes
    -----
    - Use :func:`lsd.modifiers.reverse()` to change the direction of the
      visual in an :class:`lsd.strip.Animation`.
    """

    img = Image(leds, opa=0.)
    img.fill(color)
    for pos in arange(0, leds-width, step_size):
        if not RUNNING:
            break
        img.opa[:int(pos)] = 0.
        img.opa[int(pos)] = 1. - (pos % 1.)
        img.opa[int(pos + width)] = (pos + width) % 1.
        img.opa[int(pos + 1.):int(pos + width)] = 1.

        yield img


def comet(leds: int, color: RGBColor = MAIN_COLOR, width: float = 2,
          step_size: float = 0.1, fade_prob: float = 0.25,
          fade_amount: float = .1) -> Generator[Image, None, None]:
    """A comet-like block with a fading tail running to the other end.

    Generates a block of a certain **color** and pixel **width** that
    moves along the strip from start to end. The block has a tail in the
    same **color** that fades out gradually. The fading is controlled by
    a fade probability (**fade_prob**) and a fade amount
    (**fade_amount**). The generated frames are transparent apart from
    the comet and its tail, which is partly transparent. Once teh comet
    reaches the end of the strip, the visual stops and what is left of
    the tail remains visible.

    See Also
    --------
    :func:`lsd.visuals.runner()`
        Similar visual without fading tail
    """

    from numpy.random import random

    _fade = 1 - fade_amount
    img = Image(leds, opa=0.)
    img.fill(color)
    for pos in arange(0, leds - width, step_size):
        if not RUNNING:
            break

        # Fade
        for i in range(int(pos)):
            if random() < fade_prob:
                img.opa[i] *= _fade

       # Move comet
        img.opa[int(pos + width)] = (pos + width) % 1.
        img.opa[int(pos):int(pos + width)] = 1.

        yield img

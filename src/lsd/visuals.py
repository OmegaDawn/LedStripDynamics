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

from numpy import arange, array, zeros, exp
from numpy.random import random, randint

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
    :class:`lsd.strip.Image`
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
    is scaled to the number of **leds** so that the full RGB spectrum
    is visible. This can be adjusted if a different **scale** is
    desired. The change per frame can also be adjusted with the
    **speed** parameter.

    Parameters
    ----------
    leds : int
        Number of pixels in the generated images
    scale : float, optional
        Multiplier to scale the size of the rainbow
    speed : float, optional
        Change in position per frame

    Yields
    ------
    :class:`lsd.strip.Image`
        Generated frame
    """

    from lsd.colors import rainbow_color

    img = Image(leds, opa=1.)
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

    Yields
    ------
    :class:`lsd.strip.Image`
        Generated frame

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

    Parameters
    ----------
    leds : int
        Size of the images to generate
    color : RGBColor, optional
        Color of the comet and tail
    width : float, optional
        Pixel width of the comet
    step_size : float, optional
        Distance traveled per frame
    fade_prob : float, optional
        Probability for each pixel to fade each frame
    fade_amount : float, optional
        Percentage of the color of a pixel faded on a fade event

    Yields
    ------
    :class:`lsd.strip.Image`
        Generated frame

    See Also
    --------
    :func:`lsd.visuals.runner()`
        Similar visual without fading tail
    """

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


def sparkling(leds: int, color: RGBColor = MAIN_COLOR, sparks: int = 1,
              alive_frames: int = 1, fade_pct: float = .1
              ) -> Generator[Image, None, None]:
    """# TODO"""

    img = Image(leds, opa=0)
    _fade = 1 - fade_pct

    alive = zeros(leds, dtype=int)
    while RUNNING:
        # New sparks
        new_sparks = randint(0, leds, sparks)
        alive[new_sparks] = alive_frames

        # Render frame
        img.opa *= _fade
        img[new_sparks] = color
        img.opa[alive > 0] = 1.

        yield img

        alive -= 1


# ╭───────────────╮
# │ Physics based │
# ╰───────────────╯

def bouncing_ball(leds: int, color: RGBColor = MAIN_COLOR, tail: float = 2,
                  elasticity: float = 0.8, gravity: float = 0.1,
                  velocity: float = 0., pos: float = -1,
                  finite_generation: bool = True
                  ) -> Generator[Image, None, None]:
    """Simulates a bouncing ball effect.

    The one pixel wide ball of **color** starts at index **pos** in
    the image and moves with a initial **velocity** in pixels. The
    velocity can be negative to move to the "ground" (index ``0``) or
    positive to move the ball away from the ground. The velocity is
    affected by **gravity** (also in pixel units) which pulls the ball
    towards the ground. If the ball hits the ground it bounces back and
    moves upwards again. How much of the balls impulse remains is
    determined by the **elasticity** parameter. The ball has a fading
    tail that gets longer with more velocity. The tail can also be
    amplified by the **tail** parameter.
    By default the visual is finite and stops when the boll has no more
    energy or moves out of frame. The visual can be made infinite by
    setting **finite_generation** to ``False``.

    Parameters
    ----------
    leds : int
        Size of the images to generate
    color : RGBColor, optional
        Color of the ball and fade
    tail : float, optional
        Multiplier for the tail length
    elasticity : float, optional
        Bounciness of the ball
    gravity : float, optional
        Gravity affecting the ball
    velocity : float, optional
        Initial velocity of the ball
    pos : float, optional
        Initial position of the ball
    finite_generation : bool, optional
        Makes the generator finite or infinite

    Yields
    ------
    :class:`lsd.strip.Image`
        Generated frame

    Notes
    -----
    - Set **tai** to ``0`` to disable it.
    - The **elasticity** can be set ``>1`` for an interesting effect :)
    """

    if pos < 0:
        pos = leds + pos
    img = Image(leds, opa=0.)
    img.fill(color)

    while RUNNING:
        # Place ball pixel (subpixel)
        if pos + 1 < leds:
            img.opa[int(pos + 1)] = pos % 1
        if pos < leds:
            img.opa[int(pos)] = 1 - pos % 1

        # Fade
        if tail != 0:
            tail_vel_pos = int((pos - velocity * tail))
            tail_start_i = max(1, min(int(pos + 1), tail_vel_pos))
            tail_end_i = min(leds - 1, max(int(pos + 1), tail_vel_pos + 1))
            length = tail_end_i - tail_start_i
            for i, tail_i in enumerate(range(tail_start_i, tail_end_i)):
                if velocity < 0:
                    img.opa[tail_i] = 1 - i / length
                    continue
                img.opa[tail_i] = i / length

        yield img

        # Next frame calculation
        img.fill(opa=0.)
        if pos == 0.:
            velocity *= -elasticity
        velocity -= gravity
        pos += velocity
        if pos < 0.:
            pos = 0.

        # Stop conditions for finite generation
        if finite_generation \
        and (pos >= leds or pos == 0 and abs(velocity) < gravity / 2):  # noqa
            break


def flame(leds: int,  # pylint: disable=W0102
          cooling: float = 75,
          sparks: int = 3,
          spark_prob: float = 0.1,
          heat_kernel: list = [.25, .4, .25, .1]):
    """Infinite flame generator.

    This visual simulates a burning flame with a heat sport at the base
    and heat diffusion upwards. Each frame the base gets a random heat
    value and a number of new **sparks** appear near the base. Heat is
    diffused upwards using a **heat_kernel**. Pixels are also naturally
    **cooling** down each frame.

    Parameters
    ----------
    leds : int
        Size of the images to generate
    cooling : float, optional
        Cools each pixel by a random degree up to this amount
    sparks : int, optional
        Number of new sparks to attempt to create each frame
    spark_prob : float, optional
        Probability of each spark being created
    heat_kernel : list, optional
        Kernel used for heat diffusion

    Notes
    -----
    - :mod:`lsd.modifiers` can be used to change the color of the flame.
    """

    from lsd.colors import heat_color

    heat_kernel /= array(heat_kernel).sum()
    img = Image(leds, opa=0.)
    heat = zeros(leds)

    while RUNNING:

        # Cool off
        heat -= randint(0, cooling)  # type: ignore
        heat[heat < 0] = 0

        # Heat diffusion upward
        heat_origin = heat[0]
        for pos in range(leds - 1, -len(heat_kernel), -1):
            heat_val = heat[pos]
            if pos < 0:
                heat_val = heat_origin
            heat[pos] = 0
            for k_pos, k_val in enumerate(heat_kernel):
                if pos + k_pos < leds and pos + k_pos >= 0:
                    heat[pos + k_pos] += heat_val * k_val

        # New sparks
        heat[0] = randint(1000, 2000)
        for _ in range(sparks):
            if random() < spark_prob:
                spark_pos = randint(0, int(leds * 0.075))
                heat[spark_pos] += randint(1500, 3000)

        # Convert heat to color
        for i in range(len(img)):
            img[i] = heat_color(heat[i])
            img.opa[i] = 1 / (1 + exp(-10 * (heat[i] / 2500 - 0.25)))

        yield img

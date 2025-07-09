#!usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright (c) 2025 OmegaDawn

"""Collection of *RGB* colors and color generative functions."""


from typing import Tuple
from numpy import array, clip, interp, log, uint8, float32

from lsd import FLOAT_PRECISION, rng
from lsd.typing import RGBColor, uint8RGBColor


# ╭───────────────╮
# │ Static colors │
# ╰───────────────╯

red: uint8RGBColor = array([255, 0, 0], dtype=uint8)
green: uint8RGBColor = array([0, 255, 0], dtype=uint8)
blue: uint8RGBColor = array([0, 0, 255], dtype=uint8)
orange: uint8RGBColor = array([255, 127, 0], dtype=uint8)
yellow: uint8RGBColor = array([255, 255, 0], dtype=uint8)
lime: uint8RGBColor = array([127, 255, 0], dtype=uint8)
springgreen: uint8RGBColor = array([0, 255, 127], dtype=uint8)
cyan: uint8RGBColor = array([0, 255, 255], dtype=uint8)
azure: uint8RGBColor = array([0, 127, 255], dtype=uint8)
violet: uint8RGBColor = array([127, 0, 255], dtype=uint8)
magenta: uint8RGBColor = array([255, 0, 255], dtype=uint8)
pink: uint8RGBColor = array([255, 0, 127], dtype=uint8)
white: uint8RGBColor = array([255, 255, 255], dtype=uint8)
lightgray: RGBColor = array([191.25, 191.25, 191.25], dtype=float32)
gray: RGBColor = array([127.5, 127.5, 127.5], dtype=float32)
darkgray: RGBColor = array([63.75, 63.75, 63.75], dtype=float32)
black: uint8RGBColor = array([0, 0, 0], dtype=uint8)
R, G, B, off, on = red, green, blue, black, white
primary_colors: Tuple[uint8RGBColor, ...] = (
    red, green, blue)
"""The 3 primary colors in *RGB* format."""
secondary_colors: Tuple[uint8RGBColor, ...] = (
    red, yellow, green, cyan, blue, magenta)
"""The 6 secondary colors in *RGB* format."""
tertiary_colors: Tuple[uint8RGBColor, ...] = (
    red, orange, yellow, lime, green, springgreen, cyan, azure, blue,
    violet, magenta, pink)
"""The 12 tertiary colors in *RGB* format."""


# ╭───────────────────────╮
# │ Calculative functions │
# ╰───────────────────────╯

def clip_color(color: RGBColor | Tuple[float, float, float],
               as_int: bool = False) -> RGBColor:
    """Clips color to *RGB* bounds.

    The provided color get clipped to the range of ``0.0`` to
    ``255.0``.
    Optionally, the color can be converted to int with **as_int**.

    Parameters
    ----------
    color : :attr:`lsd.typing.RGBColor`
        Color to clip
    as_int : bool, optional
        Convert the color values to :attr:`numpy.uint8` values

    Returns
    -------
    :attr:`lsd.typing.RGBColor`
        Clipped color
    :attr:`lsd.typing.RGBColor`
        Clipped uint color if **as_int** is set
    """

    _color = clip(array(color, dtype=float32), 0.0, 255.0)
    if as_int:
        return _color.astype(uint8)
    return _color


def is_same_color(color1: RGBColor, color2: RGBColor,
                  precision: float = FLOAT_PRECISION) -> bool:
    """Checks if two colors are the same color.

    Checks if **color1** and **color2** can be called equal given that
    their``float`` color channels are within the given **precision**.

    Parameters
    ----------
    color1 : :attr:`lsd.typing.RGBColor`
        First color to compare
    color2 : :attr:`lsd.typing.RGBColor`
        Second color to compare
    precision : float, optional
        Precision of the comparison

    Returns
    -------
    bool
        ``True`` if the colors are the same
    """

    return all(abs(array(color1) - array(color2)) <= precision)


# ╭────────────────────────╮
# │ Random color functions │
# ╰────────────────────────╯

def rng_color() -> uint8RGBColor:
    """Generates a color with with a random value on each channel.

    See Also
    --------
    :func:`rng_gray_color()`
        Generates a random *RGB* 'gray' color
    :func:`random_primary()`
        Gives a random primary color
    :func:`random_secondary()`
        Gives a random secondary color
    :func:`random_tertiary()`
        Gives a random tertiary color
    """

    return array((rng.integers(0, 256),
                  rng.integers(0, 256),
                  rng.integers(0, 256)), dtype=uint8)


def rng_gray_color() -> uint8RGBColor:
    """Generates a color with the same value on all color channels.

    See Also
    --------
    :func:`rng_color()`
        Generates a random *RGB* color
    :func:`random_primary()`
        Gives a random primary color
    :func:`random_secondary()`
        Gives a random secondary color
    :func:`random_tertiary()`
        Gives a random tertiary color
    """

    return array([rng.integers(0, 256)] * 3, dtype=uint8)


def random_primary() -> uint8RGBColor:
    """Gives a random color from :attr:`primary_colors`.

    See Also
    --------
    :func:`rng_color()`
        Generates a random *RGB* color
    :func:`rng_gray_color()`
        Generates a random *RGB* 'gray' color
    :func:`random_secondary()`
        Gives a random secondary color
    :func:`random_tertiary()`
        Gives a random tertiary color
    """

    return primary_colors[rng.integers(0, 3)]


def random_secondary() -> uint8RGBColor:
    """Gives a random color from :attr:`secondary_colors`.

    See Also
    --------
    :func:`rng_color()`
        Generates a random *RGB* color
    :func:`rng_gray_color()`
        Generates a random *RGB* 'gray' color
    :func:`random_primary()`
        Gives a random primary color
    :func:`random_tertiary()`
        Gives a random tertiary color
    """

    return secondary_colors[rng.integers(0, 6)]


def random_tertiary() -> uint8RGBColor:
    """Gives a random color from :attr:`tertiary_colors`.

    See Also
    --------
    :func:`rng_color()`
        Generates a random *RGB* color
    :func:`rng_gray_color()`
        Generates a random *RGB* 'gray' color
    :func:`random_primary()`
        Gives a random primary color
    :func:`random_secondary()`
        Gives a random secondary color
    """

    return tertiary_colors[rng.integers(0, 12)]


# ╭───────────────────╮
# │ Convert functions │
# ╰───────────────────╯

def rainbow_color(pos: float) -> RGBColor:
    """Gets a rainbow color from a color wheel.

    The color wheel loops every :math:`255 * 3` positions. The **pos**
    can be negative.

    Parameters
    ----------
    pos : float
        Position on the color wheel.

    Returns
    -------
    :attr:`lsd.typing.RGBColor`
        Color on the color wheel
    """

    pos %= 255 * 3
    if pos < 0:
        pos = 255 * 3 - pos
    if pos < 255:
        _r = 255 - pos
        _g = pos
        _b = 0
    elif pos < 255 * 2:
        _r = 0
        _g = 255 * 2 - pos
        _b = pos - 255
    else:
        _r = pos - 255 * 2
        _g = 0
        _b = 255 * 3 - pos
    return array((_r, _g, _b))


def kelvin_color(kelvin: float) -> RGBColor:
    """Gives an RGB color for a kelvin temperature.

    Returns the RBG color for a kelvin temperature between *1000K* and
    **40000K**. The white point is around *~5500K*. Lower temperatures
    appear orange/reddish and higher temperatures blueish.

    Parameters
    ----------
    kelvin : float
        Temperature in kelvin

    Returns
    -------
    :attr:`lsd.typing.RGBColor`
        Color in *RGB* format
    """
    # https://gist.github.com/petrklus/b1f427accdf7438606a6

    kelvin = clip(kelvin, 1000, 40000) / 100
    if kelvin <= 66:
        _r = 255
        _g = 99.47 * log(kelvin) - 161.11
    else:
        _r = 329.69 * ((kelvin - 60) ** -0.13)
        _g = 288.12 * ((kelvin - 60) ** -0.07)
    if kelvin >= 66:
        _b = 255
    elif kelvin <= 19:
        _b = 0
    else:
        _b = 138.51 * log(kelvin - 10) - 305.04
    return clip_color((_r, _g, _b))


def heat_color(temp: float) -> RGBColor:
    """Black body radiation color for a temperature.

    A celsius **temp** between ``0`` and ``2500`` is converted to a
    black body radiation color that progresses from black to red to
    yellow to white with increasing temperature.

    Parameters
    ----------
    temp : float
        Celsius temperature value

    Returns
    -------
    :attr:`lsd.typing.RGBColor`
        Heat color
    """

    sca = array([0.0, 0.4, 0.6, 0.9, 1.0])
    col = array([(0, 0, 0), (180, 35, 35), (230, 105, 5), (230, 230, 55),
                 (255, 255, 255)])

    temp = min(max(temp, 0.), 2500.) / 2500.
    idx = max(0, min(sum(temp > sca) - 1, len(sca) - 2))

    _r = interp(temp, [sca[idx], sca[idx+1]], [col[idx][0], col[idx+1][0]])
    _g = interp(temp, [sca[idx], sca[idx+1]], [col[idx][1], col[idx+1][1]])
    _b = interp(temp, [sca[idx], sca[idx+1]], [col[idx][2], col[idx+1][2]])

    return clip_color((float(_r), float(_g), float(_b)))

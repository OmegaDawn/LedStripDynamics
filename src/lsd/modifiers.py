#!usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright (c) 2025 OmegaDawn

"""Image modifiers/filters.

This module defines various image manipulation modifiers. They can be
applied to images to change their appearance. Some modifiers may require
multiple arguments. These must be wrapped in a lambda function that only
takes one argument like in the example below. Alternatively
:func:`wrap()` can be used with the same result.

```python
img = Image(60, mods=[lambda a: channel_shift(a, 2)])
```

See Also
--------
:class:`lsd.strip.Image`
    Main class for RGB images
"""


from typing import Callable

from numpy import ndarray, roll, clip, zeros

from lsd.typing import RGBColor
from lsd.utils import track_runtime


def wrap(modifier: Callable, *args, **kwargs):
    """Wrapper for modifiers that require multiple arguments.

    Parameters
    ----------
    modifier : Callable
        Modifier function of :mod:`lsd.modifiers`

    Examples
    --------
    >>> wrap(lsd.modifiers.shift, 3)
    """

    def wrapper(leds):
        """Inner wrapper."""

        return modifier(leds, *args, **kwargs)

    return wrapper


def reverse(img: ndarray) -> ndarray:
    """Reverses the order of pixels thus flipping the image.

    Parameters
    ----------
    img : ndarray
        The input image to be modified.

    Examples
    --------
    >>> revert([red, green, blue])
    [blue, green, red]
    """

    return img[::-1]


def invert(img: ndarray) -> ndarray:
    """Inverts the colors of the image.

    Colors in **img** get clipped to RGB bounds (0-255) and inverted.

    Parameters
    ----------
    img : ndarray
        The input image to be modified.

    Returns
    -------
    ndarray
        The color-inverted image.

    Examples
    --------
    >>> invert([red, green, blue])
    [cyan, magenta, yellow]
    """

    return 255 - img


def mirror(img: ndarray) -> ndarray:
    """Mirrors the first half of the image onto the second half.

    It does not matter if the **img** is even or odd sized.

    Parameters
    ----------
    img : ndarray
        The input image to be modified.

    Returns
    -------
    ndarray
        The mirrored image.

    Examples
    --------
    >>> mirror([red, green, blue, cyan])
    [red, green, green, red]
    """

    mirror_img = img
    if len(img) > 1:
        mirror_img[(len(img) // 2):] = mirror_img[:-(len(img) // 2)][::-1]

    return mirror_img


def shift(img: ndarray, n: int) -> ndarray:
    """Shifts the image by n positions.

    Colors get shifted by **n** positions to the right. **n** can be
    negative for a left shift.

    Parameters
    ----------
    img : ndarray
        The input image to be modified
    n : int
        The number of positions to shift the image

    Returns
    -------
    ndarray
        The shifted image

    See Also
    --------
    :func:`channel_shift()`
        Shifts the channels of an image.

    Examples
    --------
    >>> shift([red, green, blue], 1)
    [blue, red, green]
    >>> shift([red, green, blue], -1)
    [green, blue, red]
    """

    return roll(img, n, axis=0)


def channel_shift(img: ndarray, n: int) -> ndarray:
    """Shifts the channels of the image by n positions.

    Colors get shifted by **n** positions to the right. **n** can be
    negative for a left shift. If **n** is a multiple of ``3`` then the
    original image is returned.

    Parameters
    ----------
    img : ndarray
        The input image to be modified
    n : int
        The number of positions to shift the channels

    Returns
    -------
    ndarray
        The channel-shifted image

    See Also
    --------
    :func:`shift()`
        Shifts the image
    :func:`invert()`
        Inverts the colors of an image

    Examples
    --------
    >>> channel_shift([red, green, blue], 1)
    [green, blue, red]
    >>> channel_shift([red, green, blue], -1)
    [blue, red, green]
    """

    return roll(img, n, axis=1)


def color_correct(img: ndarray, correction: RGBColor) -> ndarray:
    """Corrects the colors of the image by adding a correction value.

    Colors in **img** get corrected by adding the respective values from
    **correction**. The resulting color values are clipped to the RGB
    bounds and returned.

    Parameters
    ----------
    img : ndarray
        The input image to be modified
    correction : RGBColor
        The color correction to apply

    Returns
    -------
    ndarray
        The color-corrected image
    """

    img += correction
    img.clip(0, 255, out=img)

    return img


def reorder(img: ndarray, order: list[int]) -> ndarray:
    """Puts segments of the image back together in an different order.

    The **img** is split into n segments of equal size. The number of
    segments is determined by the length of **order**. The segments are
    then put back together in the order defined in **order**.

    Parameters
    ----------
    img : ndarray
        Input image to be reordered
    pieces : list[int]
        New order of the segments

    Returns
    -------
    ndarray
        Reordered image

    Notes
    -----
    - Segments can be left out or stated multiple times in **order**
      which might make the modifier more interesting.
    """

    # Checks
    if order == []:
        order = [1]
    if max(order) > len(order) - 1:
        raise ValueError("Order index larger than actual segments")
    piece_pixels = int(len(img) / len(order))

    new_img = zeros(img.shape)
    for i, piece in enumerate(order):
        old_start = piece * piece_pixels
        old_end = (piece + 1) * piece_pixels
        new_start = i * piece_pixels
        new_end = (i + 1) * piece_pixels
        new_img[new_start:new_end] = img[old_start:old_end]

    return new_img


@track_runtime
def glow(img: ndarray, intensity: float = 1, channels: list[int] = [0, 1, 2]):
    """Adds a glow effect to the image.

    The image gets modified to appear as if the pixels emit light onto
    its neighbors. The **intensity** of the glow can be controlled. The
    luminous effect is spread uniformly over these pixels

    Parameters
    ----------
    img : ndarray
        Input image to be modified
    intensity: float
        How far the glow spreads in [pixels]
    channels : list[int]
        Which channels (RGB) will glow

    Notes
    -----
    - A **intensity** of ``0`` results in teh original image.
    """

    glow_img = img.copy()
    n_leds = len(img)
    glow_pixels = int(intensity)

    for pos in range(n_leds):
        color = img[pos]
        for offset in range(-glow_pixels, glow_pixels + 1):
            if offset == 0:
                continue
            _pos = pos + offset
            if _pos > 0 and _pos < n_leds:
                glow_color = color * (1-abs(offset)/(glow_pixels+1))
                if 0 not in channels:
                    glow_color[0] = 0
                if 1 not in channels:
                    glow_color[1] = 0
                if 2 not in channels:
                    glow_color[2] = 0

                glow_img[_pos] += glow_color

    return clip(glow_img, 0, 255)

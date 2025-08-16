#!usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright (c) 2025 OmegaDawn

"""Image modifiers/filters.

This module defines various image manipulation modifiers. They can be
applied to images to change their appearance.

See Also
--------
:class:`lsd.strip.Image`
    Main class for RGB images
"""


from numpy import ndarray, roll


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

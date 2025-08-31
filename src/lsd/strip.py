#!usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright (c) 2025 OmegaDawn

"""Color frames to be displayed on LED strips.

Notes
-----
- In the context of this module colors are always
  :attr:`~lsd.typing.RGBColor` float values that can be negative and out
  of the RGB range.
"""


from time import sleep, perf_counter
from shutil import get_terminal_size
from numbers import Number
from rich.text import Text
from rich.panel import Panel
from numpy.typing import NDArray
from numpy import (
    ndarray, floating, float32,
    array, full, zeros, tile, column_stack, clip,
    multiply, add, ones)
from typing import Union, Any, Callable, Iterable, Generator
from collections.abc import Sequence

from lsd import FLOAT_PRECISION, console
from lsd.utils import is_package_installed
from lsd.colors import black
from lsd.typing import is_color_value, is_black_color, is_img_data, RGBColor
from lsd.utils.logging import logger
from lsd.utils.formatting import img_to_text


# Import strip driver or its emulation
if is_package_installed('neopixel'):
    from neopixel import NeoPixel  # type: ignore  # pylint: disable=E0401
else:
    from lsd.utils.emulation import NeoPixel


class Image(ndarray):
    """LED Strip image.

    The :class:`Image` is a one dimensional array of
    :attr:`~lsd.typing.RGBColor`. The :attr:`raw_img` data gets merged
    with a background (:attr:`bg`) based on an opacity (:attr:`opa`) to
    generate the final composite (:attr:`composite`) image that can be
    displayed. The background itself can be an :class:`Image`, making
    recursive stacked images possible. Color values can be floating and
    out of the RGB range. Before displaying the values are clipped to be
    in range of ``0``-``255``.

    The image also supports subpixels / floating point indices by
    interpolating the nearest pixels. For example ``Image(2)[0.4]``
    would get the subpixel at index ``0.4`` by taking *60%* of the value
    at index ``0`` and *40%* of the value at index ``1``.

    The image can be modified through :attr:`modifiers`. They are
    applied when calculating the image :attr:`composite` and change
    the appearance of the image in various ways.

    If it is too tedious to change the opacity from transparent to
    opaque each time then :meth:`auto_opa()` can be used which changes
    the opacity based on the pixels color values. Basically the opacity
    for black pixels will be set to transparent and colored pixels will
    become fully opaque. With enabled auto opacity mode the opacities
    are adjusted whenever the instance :attr:`composite` is calculated.
    The mode can be enabled with :meth:`set_auto_opa_mode()`.

    See Also
    --------
    :attr:`Image.bg`
        Background image
    :attr:`Image.raw`
        Raw color data of this image
    :attr:`Image.opa`
        Opacity values to blend :attr:`raw` and :attr:`bg`
    :attr:`Image.cmp`
        Real image with blended background
    :func:`Image.add_modifier()`
        Adds a modifier to the image
    :func:`Image.set_auto_opa_mode()`
        Sets the state of the auto opacity mode

    Examples
    --------
    >>> img = Image(4, bg=(80, 0, 80))
    >>> img[0] = [255, 255, 255]
    >>> img[1.5] = (100, 100, 100)  # Subpixel
    >>> img.set(3, col=(0, 180, 0), opa=0.5)
    >>> img.cmp
    [[255. 255. 255.],
     [ 50.  50.  50.],
     [ 50.  50.  50.],
     [ 40.  90.  40.]]
    """

    n: int
    """Number of pixels."""
    opa: NDArray[floating]
    """Opacity values for each pixel.

    Opacity controls the transparency and how much of the :attr:`bg` is
    visible. At ``1.0`` the pixel is fully opaque. At ``0.0`` the pixel
    is fully transparent.
    """
    _bg: Union['Image', ndarray]
    """Holds background object.

    .. note::
        Use through :attr:`bg` property.
    """
    _auto_opa_mode: bool
    """States that the auto opacity mode is enabled.

    See Also
    --------
    :meth:`set_auto_opa_mode()`
    """
    _modifiers: list[Callable]
    """Modifiers applied to :attr:`composite`."""

    def __new__(cls,  # pylint: disable=W0613
                pixels: Union[int, Sequence[RGBColor]] | None = None,
                bg: Union[RGBColor, 'Image', Sequence[RGBColor]] = black,
                opa: Union[float, Sequence[float]] = 1.,
                mods: list[Callable] | None = None,
                auto_opa: bool = False,
                **kwargs):
        """
        Parameters
        ----------
        pixels :  int or Iterable of :attr:`~.RGBColor`, optional
            Number of pixels in the image
        bg : :attr:`~.RGBColor` or Iterable of :attr:`~.RGBColor`, optional
            Background color or image
        opa : float or Iterable of float, optional
            Opacity values for all pixels
        mods : list[Callable], optional
            Modifiers to apply to the image :attr:`composite`
        auto_opa : bool, optional
            Automatically set opacity values

        Notes
        -----
        - :func:`__new__()` function is a requirement when subclassing
          :class:`numpy.ndarray` as stated here:
          https://numpy.org/doc/stable/user/basics.subclassing.html
        """

        # Infer number of pixels for other object
        if pixels is not None:
            pass  # NOSONAR
        elif is_img_data(bg):
            pixels = len(bg)
        elif isinstance(opa, Iterable):
            pixels = len(opa)
        else:
            raise ValueError(
                "Pixel count not specified and cannot be determined from"
                " background (bg) or opacity (opa)")

        # Image
        if isinstance(pixels, int):
            assert pixels > 0, "Image must have at least one pixel"
            obj = tile(array((0, 0, 0), float32), (pixels, 1)).view(cls)
        elif is_img_data(pixels):
            obj = array(pixels).view(cls)
        else:
            raise TypeError(
                f"'pixels' must be int or list of colors, not {type(pixels)}")
        obj.n = len(obj)

        # Background
        if isinstance(bg, Image):
            assert len(bg) == obj.n, \
                f"Background length differs image length ({len(bg)}, {obj.n})"
            obj.bg = bg
        elif is_color_value(bg):
            obj.bg = tile(array(bg, dtype=float32), (obj.n, 1))
        elif is_img_data(bg):
            assert len(bg) == obj.n, \
                f"Background length differs image length ({len(bg)}, {obj.n})"
            obj.bg = array(bg)
        else:
            raise TypeError(
                f"'bg' must be a color or array with colors, not {type(bg)}")

        # Opacity
        if isinstance(opa, (int, float)):
            obj.opa = full(obj.n, opa, dtype=float32)
        elif isinstance(opa, Sequence):
            assert len(opa) == obj.n, \
                f"Opacity length differs image length ({len(opa)}, {obj.n})"
            obj.opa = array(opa)
        else:
            raise TypeError(
                f"'opa' must be float or sequence of floats, not {type(opa)}")

        # Modifiers
        obj._modifiers = []
        if mods is not None:
            obj._modifiers = mods

        obj._auto_opa_mode = auto_opa

        return obj

    def __array_finalize__(self, obj: NDArray[float32] | None):
        """
        Notes
        -----
        - https://numpy.org/devdocs/user/basics.subclassing.html
        """

        if obj is None:
            return

        self._bg = getattr(obj, 'bg', array([black] * self.size))
        self.opa = getattr(obj, 'opa', ones(self.size, dtype=float))

    def __repr__(self):
        return (self.__class__.__name__ + "(\n"
                + str(column_stack((self[:], self.opa))) + ")")

    def __getitem__(self, key: Any) -> Any:
        """Retrieve (color) items from the instance.

        Allows :class:`numpy.ndarray`-like indexing and indexing with
        ``float`` values. Using ``float`` values will return a
        'subpixel' value that is calculated through linear interpolation
        between the two closest pixels.

        Parameters
        ----------
        key : int, float, slice, or array-like
            Index or indices to retrieve from the instance

        Returns
        -------
        :class:`numpy.ndarray`
            Single color value
        :class:`Image`
            A slice of the instance

        See Also
        --------
        :meth:`__getsubitem__()` : Retrieves a subitem value
        """

        if isinstance(key, float):
            return self.__getsubitem__(key)
        values = super(Image, self).__getitem__(key)
        if isinstance(key, int) or isinstance(key, tuple):
            values = values.view(ndarray)
        elif isinstance(key, slice):
            values = values.view(Image)
            values.bg = self.bg[key]
            values.opa = self.opa[key]
        return values

    def __getsubitem__(self, idx: float) -> RGBColor:
        """Gets a value interpolated between two pixels.

        The **idx** is a float value in between two pixels. The values
        of the two pixels are retrieved and interpolated to get and
        return the value of the subitem.

        Parameters
        ----------
        idx : float
            Index on the image

        Returns
        -------
        :class:`~.RGBColor`
            Interpolated color value
        """

        _idx = clip(idx + (1 if idx >= 0 else -1), -self.n, self.n-1)
        if int(idx) == int(_idx) or int(idx) == idx:
            return super().__getitem__(int(idx)).view(ndarray)
        return add(super().__getitem__(int(idx)) * abs(1 - idx % 1),
                   super().__getitem__(int(_idx)) * abs(idx % 1)).view(ndarray)

    def __setitem__(self, key: Any, value: Any):
        """Sets values to the instance.

        Accepts :class:`numpy.ndarray`-like **key** and **value** pairs.
        Additionally **key** can be a ``float``. The color **value** is
        then applied as a subpixel to the neighboring pixels.

        Parameters
        ----------
        key : int, float, slice, or array-like
            Index or indices to set in the instance

        See Also
        --------
        :meth:`__setsubitem__()`
            Sets a subitem value
        """

        if isinstance(key, float):
            self.__setsubitem__(key, value)
            return
        super().__setitem__(key, value)  # type: ignore[return-value]

    def __setsubitem__(self, idx: float, value: Any):
        """Sets a subitem value.

        The :class:`~.RGBColor` **value** is applied as a subpixel
        to the neighboring pixels. The value will be applied
        percentage-wise to the two closest pixels.

        Parameters
        ----------
        idx : float
            Index on the image
        value : :class:`~.RGBColor`
            Color value to set at the subpixel index
        """

        int_idx = int(idx)
        if int_idx == idx:
            super().__setitem__(int_idx, value)
            return

        int_i_idx = int(clip(idx + (1 if idx >= 0 else -1), -self.n, self.n-1))
        pct_idx = abs(idx % 1)
        pct_i_idx = 1. - pct_idx

        # Opacity change if auto opacity mode is enabled
        if self._auto_opa_mode:
            if is_black_color(value):
                self.opa[int_idx] = pct_idx
                self.opa[int_i_idx] = pct_i_idx
                return
            if is_black_color(super().__getitem__(int_idx)):
                super().__setitem__(int_idx, value)
                self.opa[int_idx] = pct_i_idx
            if is_black_color(super().__getitem__(int_i_idx)):
                super().__setitem__(int_i_idx, value)
                self.opa[int_i_idx] = pct_idx

        # Normal behavior
        super().__setitem__(
            int_idx,
            super().__getitem__(int_idx) * pct_idx
            + array(value) * pct_i_idx)
        super().__setitem__(
            int_i_idx,
            super().__getitem__(int_i_idx) * pct_i_idx
            + array(value) * pct_idx)

    def __next_frame__(self):
        """Propagates a frame update signal to background instances.

        Used to signal lower levels of an image stack to update the
        image. This only has an effect on interactive objects like
        :class:`Animation`.

        See Also
        --------
        :class:`lsd.strip.Animation`
        """

        if isinstance(self.bg, Image):
            self.bg.__next_frame__()

    @property
    def bg(self):
        """Background image of the instance.

        This :class:`Image` or color data is the background of the
        image. Multiple images can be stacked together if they are
        assigned as backgrounds of each other. Circulations in the stack
        are prevented and will raise an error when assigning.

        See Also
        --------
        :meth:`Image.raw_img`
            Raw image data without background influence
        :meth:`Image.composite`
            Composite of raw data with background image
        """

        return self._bg

    @bg.setter
    def bg(self, bg_instance: Union['Image', ndarray]):
        """Sets the background image.

        Raises
        ------
        ValueError
            A circulation in the background stack was detected
        """

        # Check if new background stack would cause issues
        if isinstance(bg_instance, Image):
            if any(self is bg for bg in bg_instance.bg_stack()):
                raise ValueError("Can not assign a background that would cause"
                                 " a circular background stack")
            elif any(isinstance(bg, Strip) for bg in bg_instance.bg_stack()):
                raise ValueError(f"A {Strip.__name__} object can not be in the"
                                 " background")

        self._bg = bg_instance

    @property
    def raw_img(self) -> ndarray:
        """Image data of this instance without background or opacity.

        Returns
        -------
        :class:`numpy.ndarray`
            Copy of the instances image data

        See Also
        --------
        :meth:`Image.bg`
            Background entity of the image
        :meth:`Image.composite`
            Composite of raw data with background image

        Notes
        -----
        - This is the same as calling ``self[:]``.
        """

        return array(self)

    @property
    def raw(self) -> ndarray:
        """Alias for :meth:`raw_img`"""

        return self.raw_img

    @property
    def composite(self) -> ndarray:
        """Composite image with background influence.

        The :attr:`Image.raw_img` data of this instance is taken and
        combined with the :attr:`Image.bg` and :attr:`Image.opa` to
        get the real displayed image. If the :attr:`Image.bg` object
        itself has a background, the image is calculated recursively.
        With the auto opacity mode enabled the opacity values are
        changed before the image is calculated.

        Returns
        -------
        :class:`numpy.ndarray`
            Real image data of the instance

        See Also
        --------
        :meth:`Image.raw_img`
            Raw image data without background influence
        :meth:`Image.bg`
            Background entity of the object
        :meth:`Image.opa`
            Opacity values of the object
        :meth:Image.auto_opa()`
            Automatically set opacity values
        """

        # Calculate opacity values
        if self._auto_opa_mode:
            self.auto_opa()

        # Calculate color data
        _opa_reshape = self.opa.reshape(self.n, 1)
        bg_img = self.bg.composite if isinstance(self.bg, Image) else self.bg
        real_img = add(multiply(self[:], _opa_reshape),
                       multiply(bg_img, (1 - _opa_reshape)))

        # Apply modifiers
        for mod in self._modifiers:
            try:
                real_img = mod(real_img)
            except Exception as e:  # pylint: disable=W0718
                logger.error(
                    "Failed to apply modifier '%s': %s", mod.__name__, str(e))

        return array(real_img)

    @property
    def cmp(self) -> ndarray:
        """Alias for :meth:`composite`"""

        return self.composite

    def clear(self):
        """Resets the image data.

        Sets all pixels to black and opacity to ``1.0``.
        """

        self[:] = black
        self.opa[:] = 1.0

    def fill(self, color: RGBColor | None = None,  # type: ignore
             opa: float | None = None):
        """Sets a **color** and **opa** to all pixels.

        .. warning::
            This overwrites :meth:`numpy.ndarray.fill()`.

        A **color** and/or **opa** city can be set. If no arguments are
        provided, the color and opacity are not changed.

        Parameters
        ----------
        color : :attr:`lsd.typing.RGBColor`, optional
            Color to apply to all pixels
        opa : float, optional
            Opacity to apply to all pixels

        Notes
        -----
        - The **opa** gets clipped to range ``0.0``-``1.0``.
        """

        assert is_color_value(color), \
            f"Expected an RGB color value, got {type(color)}"
        assert isinstance(opa, Union[Number, None]), \
            f"Expected a float value for opacity, got {type(opa)}"

        if color is not None:
            self[:] = array(color)
        if opa is not None:
            self.opa[:] = clip(opa, 0., 1.)

    def set(self, idx: int, col: RGBColor | None = None,
            opa: float | None = None):
        """Sets a color and opacity to a pixel.

        Parameters
        ----------
        idx : int
            Pixel index
        col : :attr:`lsd.typing.RGBColor`, optional
            Color to set at the pixel index
        opa : float, optional
            Opacity to set at the pixel index

        Notes
        -----
        - Subpixels are not supported here.
        """

        assert is_color_value(col), \
            f"Expected an RGB color value not {type(col)}"
        assert isinstance(opa, Union[Number, None]), \
            f"Expected a float value for opacity not {type(opa)}"

        if col is not None:
            self[idx] = array(col)
        if opa is not None:
            self.opa[idx] = clip(opa, 0., 1.)

    def auto_opa(self):
        """Changes the current opacity values based on colors.

        Black / off pixels will be set to full transparency while fully
        transparent pixels with a color will be set to full opacity.
        Intermediate opacities are not changed. The new opacity values
        are directly set to :attr:`Image.opa`.

        See Also
        --------
        :meth:`set_auto_opa_mode()`
            Enables or disables the automatic opacity mode

        Notes
        -----
        - The :attr:`lsd.FLOAT_PRECISION` constant determines if a float
          color is regarded as black or not.

        Examples
        --------
        >>> img = Image([black, red, black, red, black], opa=[1, 1, 0, 0, 0.8])
        >>> img.auto_opa()
        >>> img.opa
        array([0., 1., 0., 1., 0.8])
        """

        to_1_mask = (abs(self) > FLOAT_PRECISION).any(axis=1)
        to_1_mask &= self.opa < FLOAT_PRECISION
        to_0_mask = (abs(self) < FLOAT_PRECISION).all(axis=1)
        self.opa[to_1_mask] = 1.
        self.opa[to_0_mask] = 0.

    def set_auto_opa_mode(self, enabled: bool = True):
        """Changes the state of the automatic opacity mode.

        With enabled auto opacity mode the :func:`auto_opa()` will be
        applied automatically whenever the :attr:`composite` is
        calculated. Note that the auto opacity mode changes the behavior
        of setting subpixels slightly.

        Parameters
        ----------
        enabled : bool, optional
            Enable or disable the automatic opacity mode

        See Also
        --------
        :meth:`auto_opa()`
            Sets the opacity values based on its colors.

        Notes
        -----
        - Setting a black subpixel only changes the opacity
          according to the subpixel. The color values remain.
        - Setting a colored subpixel onto black pixels makes the
          pixels transparent according to the subpixel position. The
          color is fully assigned to both pixels.
        """

        self._auto_opa_mode = enabled

    def add_modifier(self, modifier: Callable | list[Callable], idx: int = -1):
        """Adds a modifier to the instance.

        Parameters
        ----------
        modifier : Callable | list[Callable]
            A function that takes an image and returns a modified image

        See Also
        --------
        :mod:`lsd.modifiers`
            Contains built-in image modifiers
        :meth:`remove_modifier`
            Removes a modifier from the instance

        Notes
        -----
        - Modifiers are applied when calculating the :attr:`composite`.
        """

        if not isinstance(modifier, Iterable):
            modifier = [modifier]
        for mod in modifier:
            self._modifiers.insert(idx, mod)

    def remove_modifier(self, idx):
        """Removes a modifier from the instance.

        Parameters
        ----------
        idx : int
            The index of the modifier to remove

        See Also
        --------
        :meth:`add_modifier`
            Adds a modifier to the instance
        """

        self._modifiers.pop(idx)

    def bg_stack(self) -> tuple[*tuple['Image', ...], ndarray]:
        """Gets the instance and its stack of background instances.

        The returned stack will have at least two elements. The last
        element is always a :class:`numpy.ndarray`.

        Returns
        -------
        ``tuple[Image,numpy.ndarray]``
            The instance has a simple color data background
        ``tuple[Image,...,ndarray]``
            Recursive stack if the background is an :class:`Image`
        """

        if isinstance(self.bg, Image):
            return (self, self.bg, *self.bg.bg_stack())
        return (self, self.bg,)

    def as_text(self, info: bool = False, line_width: int = -1
                ) -> Text | Panel:
        """Gives a colored string representation of the image.

        This renders the :attr:`Image.composite` as an ANSI string with
        colored block characters. With **info** set the string will have
        multiple lines, additionally showing the :attr:`bg`,
        :attr:`raw` and :attr:`cmp` of the image and also adds an
        index indicator. Only **line_width** characters per line will be
        shown. By default this is the width of the console.

        Parameters
        ----------
        info : bool, optional
            Add detailed information about the image to the string
        line_width : int or str, optional
            Characters per line in the string

        Returns
        -------
        :class:`rich.text.Text`
            String representation of the image
        :class:`rich.panel.Panel`
            String representation when **info** is set

        See Also
        --------
        :meth:`print_img()`
            Displays the instance image in the console

        Notes
        -----
        - Ensure the console supports colors to show the string
          properly.
        - If the :attr:`Image.bg` is an :class:`Image` its
          :attr:`Image.composite` data will be shown in the string.
        """

        # Get images to be shown
        imgs = [self.composite]
        img_names = ['cmp']
        if info:
            imgs = [
                self.bg.composite if isinstance(self.bg, Image) else self.bg,
                self.raw_img,
                self.composite]
            img_names = ['bg', 'raw', 'cmp']
            if isinstance(self, Strip):
                imgs.append(self.displayed)
                img_names.append('dis')

        # Format images
        str_repr = Text(no_wrap=True)
        name_offset = max([len(name) for name in img_names]) + 1
        line_width = (get_terminal_size().columns
                      if line_width == -1 else line_width)
        img_offset = (line_width - name_offset - 7)  # Offset panel and '...'
        for i, (img, name) in enumerate(zip(imgs, img_names)):
            img_repr = img_to_text(img=img[:img_offset] if info else img,
                                   name=name,
                                   padding=name_offset,
                                   show_idx=(info and i == len(imgs) - 1))

            # Add '...' if image is longer than console width
            if info and len(img) > img_offset:
                _offset = img_offset + name_offset
                img_repr = img_repr[:_offset] + '...' + img_repr[_offset:]
            str_repr += img_repr + '\n'
        str_repr = str_repr[:-1]  # Remove last newline

        # Add border/panel around string
        if info:
            return Panel(str_repr, title=f"Image ({self.n} pixels)")
        return str_repr

    def print_img(self, info: bool = False):
        """Prints the imag to the console.

        Prints a formatted color representation of the image data to the
        console.

        .. note::
            This is different than ``print(Image())`` which prints class
            information and not the image data.

        Parameters
        ----------
        info : bool, optional
            Additionally show background, raw image and indices

        See Also
        --------
        :meth:`as_text()`
            Converts the strip image to text
        """

        console.print(self.as_text(info, console.size.width))


class Strip(Image):
    """Applies images to the LED strip.

    Holds mutable strip image data and applies that to the LED strip
    through the :attr:`strip_driver`. The strip driver can the
    controller for a physical strip or an emulated version. The strip
    functions like an :class:`Image` and can have background images that
    are blended by an opacity into the strip image.

    .. note::
        Note that all changes made to the strip (or its background) only
        becomes visible once :func:`show()` is called.

    See Also
    --------
    :class:`Image`
        Simple image to be applied to the strip
    :class:`Animation`
        Interactive image that changes its content over time
    :class:`lsd.utils.emulation.NeoPixel`
        Emulated version of the strip driver

    Notes
    -----
    - If the emulation is used ensure the the program has
      :func:`multiprocessing.freeze_support()`.

    Examples
    --------
    >>> strip = Strip(10)
    >>> strip.show(test_img(strip.n))

    >>> strip = Strip(10)
    >>> strip.fill((0, 255, 180))
    >>> strip[0] = (255, 0, 0)
    >>> strip.show()
    """

    strip_driver: 'NeoPixel'
    """Controls the physical LED strip.

    This object is either a :class:`neopixel.NeoPixel` instance or its
    emulated version :class:`lsd.utils.emulation.NeoPixel` used to show
    colors on a strip / simulation of a strip.
    """
    _displayed: ndarray
    """Holds the currently displayed image data.

    The displayed frame is a :class:`numpy.ndarray` with
    :class:`lsd.typing.uint8RGBColor` values clipped to ``0``-``255``.

    .. note::
        Use through the :attr:`displayed` property.
    """

    def __init__(self,
                 pixels: int = None,  # type: ignore  pylint: disable=W0613
                 bg: Union[RGBColor, 'Image', Sequence[RGBColor]] = black,
                 opa: Union[float, Sequence[float]] = 1.,
                 mods: list[Callable] | None = None,
                 brightness: float = 1.0,
                 auto_opa: bool = False,
                 emulation: bool = False,
                 **kwargs):
        """
        Parameters
        ----------
        pixels : int, optional
            Number of pixels in the strip
        bg : :attr:`lsd.typing.RGBColor` or ``Sequence[RGBColor]``, optional
            Background color or image of the strip
        opa : float or ``Sequence[float]``, optional
            Opacity values for all pixels in the strip
        mods : list[Callable], optional
            Image modifiers
        brightness : float, optional
            Brightness of the strip
        auto_opa : bool
            Set opacity values automatically
        emulated : bool, optional
            Use an emulated version for :class:`neopixel.NeoPixel`

        Notes
        -----
        - Keyword arguments can be passed for :class:`neopixel.NeoPixel`
          or its emulated version :class:`lsd.utils.emulation.NeoPixel`
          and :class:`lsd.utils.emulation.Display`.
        - The **brightness** is applied when colors get shown on the
          strip. It does not effect color values.
        - If the emulation is used (either **emulated** is set or
          :mod:`neopixel` is not installed) ensure the the program has
          :func:`multiprocessing.freeze_support()`.

        See Also
        --------
        lsd.strip.Image
            Baseclass for :class:`Strip`

        Examples
        --------
        >>> strip = Strip(10, opa=0.5)
        >>> strip.fill((0, 255, 180))
        >>> strip.print_img()
        >>> strip.show()  # Needs freeze support!
        """

        super().__init__()
        _, _, _, _ = bg, opa, mods, auto_opa

        if emulation:
            from lsd.utils.emulation import NeoPixel as emulated_NeoPixel
            self.strip_driver = emulated_NeoPixel(
                pin=None,
                n=self.n,
                brightness=brightness,
                auto_write=False,
                pixel_order='RGB',
                **kwargs)
        else:
            self.strip_driver = NeoPixel(
                pin=None,
                n=self.n,
                brightness=brightness,
                auto_write=False,
                pixel_order='RGB',
                **kwargs)

        self._displayed = zeros((self.n, 3), dtype=int)

    def __str__(self) -> str:
        """String representation of the strip."""

        text = f"<{type(self).__name__} leds={self.n}, "
        text += f"brightness={self.strip_driver.brightness}"
        text += ">"
        return text

    @property
    def displayed(self) -> ndarray:
        """Gives the color data currently displayed on the strip."""

        return self._displayed

    def show(self, dur: float = 0, advance: bool = True,
             img: Image | None = None):
        """Shows an image on teh physical LED strip.

        Displays the :attr:`composite` data of the strip (or if provided
        the **img** attribute) onto the LED strip. The image is
        converted to integer values before it is shown. After the image
        is applied to the LED strip interactive images in the background
        stack are advanced to the next frame. This can be prevented by
        setting the **advance** parameter. A duration (**dur**) can be
        stated to show this frame for a certain amount of time. This
        will block the thread until the duration is over.

        Parameters
        ----------
        dur : float, optional
            Duration to show the frame [sec]
        advance : bool, optional
            Advance interactive objects to the next state
        img : :class:`Image`, optional
            Image to show on the strip

        Examples
        --------
        >>> strip = Strip(10)
        >>> strip.fill((0, 255, 180))  # Not visible
        >>> strip.show()  # Now visible
        """

        if img is None:
            img = self
        if not isinstance(img, Image):
            img = Image(img, bg=self.bg)
        frame = clip(img.composite.astype('uint8'), 0, 255)

        self._displayed = frame
        self.strip_driver[:] = frame
        self.strip_driver.show()
        if advance:
            img.__next_frame__()
        sleep(dur)

    def clear(self, show: bool = False):
        """Clears the strip.

        Resets the colors and opacity of the strip image and show the
        cleaned black image on the strip if **show** is set.

        Parameters
        ----------
        show : bool, optional
            Apply cleared image to physical strip

        See Also
        --------
        :meth:`Image.clear()`
        """

        super().clear()
        if show:
            self.show()


class Animation(Image):
    """Interactive image that advances with each shown frame.

    An animation is a dynamic image that changes its frame each time
    accessed. Frames are generated through :mod:`~.visuals`. If the
    animation is in the background stack of a :class:`~.Strip` it will
    automatically advance with each :func:`~.Strip.show()` call.

    See Also
    --------
    :meth:`play()`
        Plays the animation as video on a strip
    :mod:`lsd.visuals`
        Visual effect generators
    :func:`lsd.strip.Strip.show()`
        Automatically advances the animation
    """

    playback: bool
    """Enables animation playback.

    If playback is enabled the animation will advance with each"""
    visual: Generator[Image, None, None]
    """Generator function to get animation frames."""

    def __init__(self,  # pylint: disable=W0613
                 visual: Generator[Image, None, None] | Callable,
                 pixels: int = None,  # type: ignore
                 bg: Union[RGBColor, 'Image', Sequence[RGBColor]] = black,
                 playback: bool = True,
                 **kwargs):
        """
        Parameters
        ----------
        pixels : int, optional
            Amount of pixels a frame has
        visual : Generator[Image, None, None] | Callable
            Generator yielding animation frames
        bg : RGBColor | Image | Sequence[RGBColor]
            Background of the animation
        playback : bool
            Enable playback

        See Also
        --------
        :mod:`lsd.visuals`
            Module with visual effect generators
        """

        _, _ = pixels, bg  # linting
        super().__init__()
        if isinstance(visual, Callable):
            visual = visual(leds=self.n)
        self.visual = visual  # type: ignore

        self.set_playback(playback)

    def __str__(self) -> str:
        """String representation."""

        return (f"<{self.__class__.__name__} effect={self.visual.__name__}>")

    def __next_frame__(self, update_bg: bool = True):
        """Advances the animation to the next frame.

        Gets the next frame from the :attr:`visual` and applies it to
        the instance. The frame update call is then recursively passed
        to the background stack.

        Parameters
        ----------
        update_bg : bool
            Whether to pass the update signal to background instances

        Notes
        -----
        - The initial update call is typically made by a :class:`Strip`.
        """

        if self.playback:
            try:
                frame = next(self.visual)
                self.opa = frame.opa
                self[:] = frame[:]
            except StopIteration:
                self.set_playback(False)
        if update_bg and isinstance(self.bg, Image):
            self.bg.__next_frame__()

    def set_playback(self, enabled: bool = True):
        """Sets the playback state of the animation."""

        self.playback = enabled

    def play(self, strip: Strip, fps: float = 30,
             max_dur: float | None = None):
        """Plays the animation as video on a strip.

        The animation will be played on a **strip**.  For infinite
        animations a **max_dur** can be set that ends the playback after
        n seconds. Note that this functions calls :meth:`Strip.show()`
        and will therefore update its background stack. The animation
        should not be part of the strips background or it will be
        updated twice.

        Parameters
        ----------
        strip : Strip
            The strip to play the animation on
        fps : float
            Frames per second
        max_dur : float | None
            Maximum duration of the animation in seconds
        """

        assert fps > 0, 'FPS must be positive and non-zero'
        if any(self is i for i in strip.bg_stack()):
            logger.warning("The animation is in the strip background"
                           " and will be updated twice during"
                           " playback.")

        delay = 1. / fps
        self.set_playback(True)
        start = perf_counter()
        while self.playback:
            strip.show(img=self, dur=delay)
            if max_dur is not None and perf_counter() - start > max_dur:
                break


def test_img(n: int) -> Image:
    """Test image similar to old TVs.

    Creates a test image with a pattern similar to old TV screens but
    one dimensional. The image consists out of different sections with
    colors, contrasts, fades and patterns. The image is scaled to *n*
    but should have at least ``20`` pixels to show all test sections
    correctly.

    Parameters
    ---------
    n : int
        Number of pixels

    Returns
    -------
    :class:`Image`
        Image with test pattern
    """

    from lsd.colors import rainbow_color, white, secondary_colors
    img = Image(n)
    sec_len = max(int(n / 20), 1)
    if n < 20:
        sec_len = max(int(n / 8), 1)

    # Section 0 to 7: colors
    for i, col in enumerate([black, white, *secondary_colors]):
        indices = range(sec_len * i, max(sec_len * (i+1), n-1))
        img[indices] = col
        if n < 20 and indices[-1] >= n-1:
            break
    if n < 20:
        return img

    # Section 8 to 10: black-white fade
    for pos in range(sec_len * 8, sec_len * 11):
        col = array(white) * ((pos-sec_len*8) / (sec_len*3 - 1))
        img[pos] = col

    # Sections 11 to 13: black-white flicker
    sec_14_begin = sec_len * 14
    black_indices = range(sec_len * 11, sec_14_begin, 2)
    white_indices = range(sec_len * 11 + 1, sec_14_begin, 2)
    img[black_indices] = black
    img[white_indices] = white

    # Section 14 to 19: rainbow fade
    for pos in range(sec_14_begin, len(img)):
        img[pos] = rainbow_color(
            (pos - sec_14_begin) * (256 * 3) / (len(img)-sec_14_begin))

    return img

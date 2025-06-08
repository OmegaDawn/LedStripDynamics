#!usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright (c) 2025 OmegaDawn

"""Color frames to be displayed on LED strips.

Notes
-----
- In the context of this module colors are always :class:`~.RGBColor`
  float values that can be negative and out of the RGB range.
"""


from shutil import get_terminal_size
from rich.text import Text
from rich.panel import Panel
from rich.console import Console
from numpy.typing import NDArray
from numpy import (
    array, full, tile, column_stack, clip, multiply, add, ones,
    ndarray, floating)
from typing import Union, Tuple, Any

from lsd import DEFAULT_DTYPE
from lsd.colors import black
from lsd.typing import is_color_value, RGBColor
from lsd.utils.formatting import img_to_text


console = Console()
""":mod:`rich` Console for color output in the terminal."""


class Image(ndarray):
    """LED Strip image.

    The :class:`Image` is a one dimensional array of :attr:`RGBColor`.
    The :attr:`raw_img` data gets merged with a background (:attr:`bg`)
    based on an opacity (:attr:`opa`) to generate the final :attr:`img`
    that is displayed. The background itself can be an :class:`Image`,
    making recursive stacked images possible. Color values can be
    floating and out of the RGB range. Before displaying the values are
    clipped to be in range of ``0``-``255``.

    The image also supports subpixels / floating point indices by
    interpolating the nearest pixels. For example ``Image(2)[0.4]``
    would get the subpixel at index ``0.4`` by taking *60%* of the value
    at index ``0`` and *40%* of the value at index ``1``.

    Examples
    --------
    >>> img = Image(4, bg=(80, 0, 80))
    >>> img[0] = [255, 255, 255]
    >>> img[1.5] = (100, 100, 100)  # Subpixel
    >>> img.set(3, col=(0, 180, 0), opa=0.5)
    >>> img.img
    [[255. 255. 255.],
     [ 50.  50.  50.],
     [ 50.  50.  50.],
     [ 40.  90.  40.]]
    """

    n: int
    """Number of pixels."""
    bg: Union['Image', ndarray]
    """Background object."""
    opa: NDArray[floating]
    """Opacity values for each pixel.

    Opacity controls the transparency and how much of the :attr:`bg` is
    visible. At ``1.0`` the pixel is fully opaque. At ``0.0`` the pixel
    is fully transparent.
    """

    def __new__(cls, pixels: int | ndarray, *args,  # pylint: disable=W0613
                bg: RGBColor | 'Image' = black,
                opa: float = 1., **kwargs):
        """
        Parameters
        ----------
        pixels : int or :class:`numpy.ndarray`
            Number of pixels in the image.
        bg : :attr:`~.RGBColor` or :class:`Image`, optional
            Background color or image.
        opa : float, optional
            Opacity values for all pixels.

        Notes
        -----
        - :func:`__new__()` function is a requirement when subclassing
          :class:`numpy.ndarray` as stated here:
          https://numpy.org/doc/stable/user/basics.subclassing.html
        """

        # Image
        if isinstance(pixels, int):
            assert pixels > 0, "Image must have at least one pixel"
            obj = tile(array((0, 0, 0), DEFAULT_DTYPE), (pixels, 1)).view(cls)
        else:
            raise TypeError(
                "Expected 'pixels' argument to be of type 'int'"
                + f" but got {type(pixels)}")

        # Background
        if isinstance(bg, Image):
            obj.bg = bg
        elif is_color_value(bg):
            obj.bg = tile(array(bg, dtype=DEFAULT_DTYPE), (pixels, 1))
        else:
            raise TypeError(
                "Expected 'bg' argument to be 'float'"
                + f" but got {type(bg)}")

        # Opacity
        if isinstance(opa, (int, float)):
            obj.opa = full(pixels, opa, dtype=DEFAULT_DTYPE)
        elif isinstance(opa, NDArray):
            if opa.shape != (pixels, 1):
                raise ValueError(
                    "Expected 'opa' argument to be of shape"
                    + f" ({pixels}, 1) but got {opa.shape}")
            obj.opa = opa
        else:
            raise TypeError(
                "Expected 'opa' argument to be 'float' or 'ndarray'"
                + f" but got {type(opa)}")

        obj.n = pixels
        return obj

    def __array_finalize__(self, obj: NDArray[DEFAULT_DTYPE] | None):
        """
        Notes
        -----
        - https://numpy.org/devdocs/user/basics.subclassing.html
        """

        if obj is None:
            return

        self.bg = getattr(obj, 'bg', array([black] * self.size))
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

        if int(idx) == idx:
            super().__setitem__(int(idx), value)
            return

        _idx = clip(idx + (1 if idx >= 0 else -1), -self.n, self.n-1)
        super().__setitem__(int(idx), add(
            super().__getitem__(int(idx)) * abs(idx % 1),
            array(value) * abs(1 - idx % 1)))
        super().__setitem__(int(_idx), add(
            super().__getitem__(int(_idx)) * abs(1 - idx % 1),
            array(value) * abs(idx % 1)))

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
        :meth:`Image.img`
            Displayed image that includes background
        """

        return array(self)

    @property
    def img(self) -> ndarray:
        """Visualized image with background influence.

        The :attr:`Image.raw_img` data of this instance is taken and
        combined with the :attr:`Image.bg` and :attr:`Image.opa` to
        get the real displayed image. If the :attr:`Image.bg` object
        itself has a background, the image is calculated recursively.

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
        """

        _opa_reshape = self.opa.reshape(self.n, 1)
        bg_img = self.bg.img if isinstance(self.bg, Image) else self.bg
        real_img = add(multiply(self[:], _opa_reshape),
                       multiply(bg_img, (1 - _opa_reshape)))
        return array(real_img)

    def clear(self):
        """Resets the image data.

        Sets all pixels to black and opacity to ``1.0``.
        """

        self[:] = black
        self.opa[:] = 1.0

    def fill_(self, color: RGBColor | None = None,
              opa: float | None = None):
        """Sets a **color** and **opa** to all pixels.

        A **and** and/or **opa** city can be set. If no arguments are
        provided, the color and opacity are not changed.

        Parameters
        ----------
        color : :class:`~.RGBColor`, optional
            Color to apply to all pixels
        opa : float, optional
            Opacity to apply to all pixels

        Notes
        -----
        """

        assert is_color_value(color), \
            f"Expected an RGB color value not {type(color)}"

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
        col : :class:`~.RGBColor`, optional
            Color to set at the pixel index
        opa : float, optional
            Opacity to set at the pixel index

        Notes
        -----
        - Subpixels are not supported here.
        """

        assert is_color_value(col), \
            f"Expected an RGB color value not {type(col)}"

        if col is not None:
            self[idx] = array(col)
        if opa is not None:
            self.opa[idx] = clip(opa, 0., 1.)

    def bg_stack(self) -> Tuple['Image', ...] | Tuple[ndarray, ...]:
        """Gets the stack of background instances.

        Returns
        -------
        Tuple[:class:`numpy.ndarray`, ...]
            Single element if the background is a :class:`numpy.ndarray`
        Tuple[:class:`Image`, ...]
            Recursive stack if the background is an :class:`Image`
        """

        if isinstance(self.bg, Image):
            return (self.bg, *self.bg.bg_stack())
        return (self.bg,)

    def as_text(self, info: bool = False, line_width: int = -1
                ) -> Text | Panel:
        """Gives a colored string representation of the image.

        This renders the :attr:`Image.img` as an ANSI string with
        colored block characters. With **info** set the string will have
        multiple lines, additionally showing the :attr:`~.bg`,
        :attr:`raw_img` of the image and also adds an index indicator.
        Only **line_width** characters per line will be shown. By
        default this is the width of the console.

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
          :attr:`Image.img` will be shown in the string.
        """

        # Get images to be shown
        imgs = [self.img]
        img_names = ['img']
        if info:
            imgs = [self.bg.img if isinstance(self.bg, Image) else self.bg,
                    self.raw_img,
                    self.img]
            img_names = ['bg', 'raw', 'img']

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
        console. This is different than ``print(Image())`` which prints
        class information and not the image data.

        Parameters
        ----------
        info : bool, optional
            Additionally show background, raw image and indices

        See Also
        --------
        :meth:`as_text()`
            Text that gets printed
        """

        console.print(self.as_text(info, console.size.width))

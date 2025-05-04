#!usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright (c) 2025 OmegaDawn

"""Emulates a LED strip driver for visualization on a PC monitor."""


import matplotlib
import matplotlib.pyplot as plt
from typing import Any
from ctypes import windll
from time import sleep, perf_counter
from multiprocessing import Process, Pipe, freeze_support
from multiprocessing.connection import PipeConnection
from numpy import ndarray, uint8, asarray, arange, expand_dims, zeros

from lsd.typing import RGBColor
from lsd import logger


class Display:
    """An updating :mod:`matplotlib` plot that visualizes a LED strip.

    Visualizes an RGB Strip in a new window. Strip data is gained from a
    pipe. The plot can be slightly customized.

    Notes
    -----
    - The plot can be closed by pressing the 'Q' key.
    """

    pipe_conn: PipeConnection
    """Connection to receive data from."""
    dark_mode: bool
    """Display in dark/light mode."""
    pixels: int
    """Number of pixels in simulated strip."""
    ticks: bool
    """Show ticks/pixel indexes on a-axis."""
    refresh_frames: int
    """UI frame updates since last :attr:`last_fps_time`."""
    update_frames: int
    """Strip data updates since last :attr:`last_fps_time`."""
    last_fps_time: float
    """Timestamp of last FPS calculation."""
    _open: bool
    """Plot is open and visible."""

    def __init__(self,
                 pipe_conn: PipeConnection,
                 pixels: int,
                 dark_mode: bool = True,
                 show_index: bool = False,
                 fps_limit: int = 60,
                 hide_display: bool = False):
        """
        .. note::
            The :class:`Display` must be initiated in a new
            :class:`multiprocessing.Process`.

        Parameters
        ----------
        pipe_con : :mod:`multiprocessing.connection.PipeConnection`
            Pipe to receive strip color data from
        pixels : int
            Number of LEDs in the strip
        dark_mode : bool, optional
            Plot in dark or light mode
        show_index : bool, optional
            Shows the pixel index as x-axis tick
        fps_limit : int, optional
            Limits the plot refresh rate
        hide_display : bool, optional
            Debugging and testing option to hide the plot window

        Notes
        -----
        - There won't be an fps limit if **fps_limit** is set to ``-1``
        - The **hide_display** should be passed down from higher level
          functions/classes.
        """

        logger.debug(
            "Initiating '%s' %s",
            self.__class__.__name__, "(hidden)" if hide_display else '')
        self.pipe_conn = pipe_conn
        self.dark_mode = dark_mode
        self.pixels = pixels
        self.ticks = show_index
        self.refresh_frames = 0
        self.update_frames = 0
        self.last_fps_time = 0
        self._open = True

        # Create plot window
        matplotlib.use('QT5Agg')
        matplotlib.rcParams['toolbar'] = 'None'
        self.fig = plt.figure(facecolor='black' if dark_mode else 'white')
        self.ax = self.fig.add_subplot(111)
        self.img = self.ax.imshow([[[0, 0, 0]] * pixels], aspect='auto',
                                  interpolation='none')
        self.set_plot_style()
        self.fig.canvas.draw()
        if not hide_display:
            plt.show(block=False)
        self.bg = self.fig.canvas.copy_from_bbox(self.ax.bbox)  # type: ignore

        # Plot update loop
        self.pipe_conn.send("$!Setup finished")
        if fps_limit == -1:
            while self._open:
                self.visualize()
        else:
            delay = 1 / fps_limit
            while self._open:
                self.visualize()
                sleep(delay)

    def set_plot_style(self):
        """Styles the plot window."""

        self.fig.canvas.manager.window.setGeometry(  # type: ignore
            0, 0, windll.user32.GetSystemMetrics(0), 50)
        self.fig.canvas.manager.set_window_title(  # type: ignore
            f"Strip Display [{self.pixels} LEDs]")
        self.fig.canvas.mpl_connect('close_event', self.closeEvent)
        self.fig.subplots_adjust(0.01, 0.45, 0.99, 0.8)

        ax = self.ax.axes
        if ax is None:
            return
        ax.get_yaxis().set_visible(False)
        if not self.ticks:
            ax.get_xaxis().set_visible(False)
        ax.tick_params(axis='x', which='major',
                       colors='white' if self.dark_mode else 'black')
        ax.tick_params(axis='x', which='minor',
                       colors='black' if self.dark_mode else 'white')
        ax.set_xticks(arange(-.5, self.pixels, 1), minor=True)
        ax.set_xticks(range(self.pixels))
        if self.pixels > 60:
            ax.set_xticks(list(arange(0, self.pixels, self.pixels//20))
                          + [self.pixels - 1])  # type: ignore

    def visualize(self):
        """Updates the plot with data from the pipe.

        Could be called continuously for live updates. Data update and
        refresh rates are tracked and displayed in the window title.
        Receiving ``None`` from the pipe is interpreted as termination
        signal for the plot.
        """

        # Get latest strip data
        data = None
        try:
            while self.pipe_conn.poll():
                data = self.pipe_conn.recv()
        except BrokenPipeError:
            self.closeEvent()
            return

        # Update plot
        if data is not None:
            self.update_frames += 1
            self.img.set_data(data)
            self.fig.canvas.restore_region(self.bg)  # type: ignore
            self.ax.draw_artist(self.img)
            self.fig.canvas.blit(self.ax.bbox)  # type: ignore
            self.fig.canvas.flush_events()

        # Calculate updates per second
        self.refresh_frames += 1
        if perf_counter() - self.last_fps_time > 1:
            self.fig.canvas.manager.set_window_title(  # type: ignore
                "Strip Display "
                + f"[{self.pixels} LEDs] "
                + f"[{self.refresh_frames} FPS] "
                + f"[{self.update_frames} UPS]")
            self.update_frames = 0
            self.refresh_frames = 0
            self.last_fps_time = perf_counter()

    def closeEvent(self, event: Any = None):  # pylint: disable=w0613 # NOSONAR
        """Terminates the plot window."""

        if not self._open:
            return
        self._open = False
        logger.debug("Closing '%s' window", self.__class__.__name__)
        plt.close(self.fig)


class NeoPixel(ndarray):
    """Emulates the :class:`neopixel.NeoPixel` class.

    This emulates the functionality of the *Adafruit* :mod:`neopixel`
    library as a :mod:`numpy` array. The strip driver is simulated so that
    instead of applying the color data to a physical LED strip, the data
    is visualized onto the monitor using the :class:`Display`.

    See Also
    --------
    :class:`lsd.utils.emulation.Display`
        Plots the RGB strip colors on a monitor
    """

    pin: Any
    """GPIO pin."""
    brightness: float
    """Overall brightness multiplier."""
    auto_write: bool
    """Automatic write mode. See :class:`neopixel.NeoPixel`."""
    pixel_order: str
    """Color channel order. See :class:`neopixel.NeoPixel`."""
    channel_order: list
    """Channel order interpretation."""
    pipe_conn: PipeConnection
    """Connection to the :class:`Display`."""

    def __new__(cls, pin: Any, n: int, *, bpp: int = 3,
                brightness: float = 1.0, auto_write: bool = False,
                pixel_order: str = 'RGB', **display_kwargs):
        """
        Parameters
        ----------
        pin : Any
            Only for compatibility, no effect
        n : int
            Number of pixels in the strip
        bpp : int, optional
            Only for compatibility, no effect
        brightness : float, optional
            Overall brightness multiplier
        auto_write : bool, optional
            Only for compatibility, no effect
        pixel_order : str, optional
            Interpreting order as red, green and blue channels
        display_kwargs : dict, optional
            Optional arguments for the :class:`Display` class

        Notes
        -----
        - Also accepts arguments for the :class:`Display`.
        """

        if auto_write:
            logger.warning(
                "The '%s' emulation does not support 'auto_write'",
                cls.__name__)
            auto_write = False
        if bpp != 3 or 'w' in pixel_order.lower():
            logger.warning(
                "The '%s' emulation does not support white channels. "
                "'bpp' and 'pixel_order' arguments have limited effect",
                cls.__name__)
            pixel_order = 'RGB'

        obj = zeros((n, 3), dtype=uint8).view(cls)
        obj.pin = pin
        obj.brightness = brightness
        obj.auto_write = auto_write
        obj.pixel_order = pixel_order
        obj.channel_order = [pixel_order.lower().index(ch) for ch in 'rgb']
        obj.pipe_conn, pipe_conn = Pipe()

        freeze_support()
        Process(target=Display,
                args=(pipe_conn, n),
                kwargs=display_kwargs,
                daemon=True).start()

        obj.pipe_conn.recv()  # Await Display setup
        obj.show()
        return obj

    def __del__(self):
        self.close()

    def __enter__(self):
        return self

    def __exit__(self, exception_type: Any = None, exception_value: Any = None,
                 traceback: Any = None):
        self.close()

    def __repr__(self):
        return "[" + ", ".join([str(x) for x in self]) + "]"

    @property
    def n(self) -> int:
        """Number of pixels."""

        return len(self)

    def fill(self, value: RGBColor):
        """Fills the strip with a single color.

        Note that the color channels are interpreted as stated by
        :data:`pixel_order`.

        Parameters
        ----------
        value : :data:`lsd.typing.RGBColor`
            RGB color tuple
        """

        self[:] = value

    def show(self):
        """Makes changes visible on the LED strip.

        For the emulation the data will be send trough a
        :class:`multiprocessing.Pipe` to the display.
        """

        data = expand_dims(asarray(self)[:, self.channel_order], axis=0
                           ).astype(int)
        try:
            self.pipe_conn.send(data)
        except BrokenPipeError:
            logger.warning("'%s' emulator terminates because '%s' was closed",
                           self.__class__.__name__,  Display.__name__)
            exit()

    def close(self):
        """Close Display when terminating."""

        try:
            self.pipe_conn.close()
        except AttributeError:
            pass

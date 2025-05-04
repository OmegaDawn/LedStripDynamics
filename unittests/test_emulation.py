#!usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright (c) 2025 OmegaDawn

"""Tests functionality of :mod:`lsd.utils.emulation`."""


import unittest
from numpy.testing import assert_array_equal

from lsd.utils.emulation import NeoPixel


class TestEmulation(unittest.TestCase):
    """Test the :mod:`lsd.utils.emulation` module."""

    def test_neopixel(self):
        """Tests the emulated :class:`neopixel.NeoPixel` class."""

        pixels = 60
        neopixel = NeoPixel('board.D0', pixels, hide_display=True)
        self.assertEqual(neopixel.n, pixels)
        neopixel.fill((255, 0, 0))
        assert_array_equal(neopixel, [(255, 0, 0)] * pixels)
        neopixel[2] = (0, 255, 0)
        neopixel.close()


if __name__ == '__main__':
    unittest.main()

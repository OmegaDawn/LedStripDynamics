#!usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright (c) 2025 OmegaDawn
# type: ignore

"""Tests functionality of :class:`ledstripdynamics.strip.Strip`."""


import unittest
from numpy.testing import assert_array_equal

from lsd.strip import Strip, Image
from lsd.colors import red, green, blue, black


class TestStrip(unittest.TestCase):

    def setUp(self):
        self.img = Image(3)
        self.strip = Strip(3, hide_display=True)

    def test_init(self):
        """Tests strip initialization."""

        # Valid cases (most already tested for Image class)
        strip = Strip(3, bg=self.img, opa=0, hide_display=True)
        self.assertEqual(len(strip), 3)
        assert_array_equal(self.img, strip.bg)
        assert_array_equal(strip.displayed, [black] * strip.n)

        # Invalid cases
        with self.assertRaises(TypeError):
            Strip('a')
        with self.assertRaises(TypeError):
            Strip(10, bg='a')
        with self.assertRaises(TypeError):
            Strip(3, bg=True)
        with self.assertRaises(TypeError):
            Strip(5, bg=[1, 2], opa='a')
        with self.assertRaises(AssertionError):
            Strip(0)
        with self.assertRaises(AssertionError):
            Strip(-1)

    def test_strip_in_bg_stack(self):
        """Tests error raising when a :class:`Strip` is in bg stack."""

        with self.assertRaises(ValueError):
            self.strip.bg = Strip(3, hide_display=True)
        with self.assertRaises(ValueError):
            Image(3, bg=self.strip)

    def test_show(self):
        """Tests the :meth:`Strip.show()` method."""

        # Showing strip data
        colors = [red, green, blue]
        self.strip[:] = colors
        self.strip.show()
        assert_array_equal(self.strip.displayed, colors)

        # Showing passed image
        self.strip.show(self.img)
        assert_array_equal(self.strip.displayed, self.img)

        # Changes not shown
        self.strip.fill(red)
        with self.assertRaises(AssertionError):
            assert_array_equal(self.strip.displayed, self.strip.raw_img)


if __name__ == '__main__':
    unittest.main()

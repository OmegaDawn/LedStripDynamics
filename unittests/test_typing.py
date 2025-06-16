#!usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright (c) 2025 OmegaDawn

"""Tests functionality of :mod:`ledstripdynamics.utils.typing`."""


import unittest
from numpy import array, zeros

from lsd.strip import Image
from lsd.colors import red
from lsd.typing import is_color_value, is_color, is_img_data


class TestFormatting(unittest.TestCase):

    def test_is_color_value(self):
        """Tests :func:`ledstripdynamics.typing.is_color_value()`."""

        # Allowed cases
        self.assertTrue(is_color_value([255, 0, 0]))
        self.assertTrue(is_color_value((0, 255, 0)))
        self.assertTrue(is_color_value((1.2, -0.5, 25.9)))
        self.assertTrue(is_color_value(array([-1, 50, 270])))
        self.assertTrue(is_color_value([True, True, False]))

        # Invalid cases
        self.assertFalse(is_color_value([255, 0]))
        self.assertFalse(is_color_value([255, 0, 0, 255]))
        self.assertFalse(is_color_value([255, '0', 255]))
        self.assertFalse(is_color_value({'r': 255, 'g': 0, 'b': 0}))
        self.assertFalse(is_color_value(['2', '46', '100']))
        self.assertFalse(is_color_value('not a color'))
        self.assertFalse(is_color_value(123))
        self.assertFalse(is_color_value(None))

        # Extreme cases
        self.assertFalse(is_color_value(zeros((100000,))))

    def test_is_color(self):
        """Tests :func:`ledstripdynamics.typing.is_color()`."""

        # Allowed cases
        self.assertTrue(is_color(array([-1, 50, 270])))
        self.assertTrue(is_color(array([-20.7, 392.6, 10.2])))
        self.assertTrue(is_color(red))
        self.assertTrue(is_color(array([0, 1, 1], dtype=bool)))
        self.assertTrue(is_color(Image(5)[0]))

        # invalid cases
        self.assertFalse(is_color([255, 0, 0]))
        self.assertFalse(is_color((-1, 5, 30)))
        self.assertFalse(is_color((-1, '5', True)))
        self.assertFalse(is_color("hello"))
        self.assertFalse(is_color({'r': 255, 'g': 0, 'b': 0}))

        # Extreme cases
        self.assertFalse(is_color(zeros((100000,))))

    def test_is_img_data(self):
        """Tests :func:`ledstripdynamics.typing.is_img_data()`."""

        # Allowed cases
        self.assertTrue(is_img_data(
            array([[0, 120, 253], [0.5, 3.6, 20.8]])))
        self.assertTrue(is_img_data(
            array([[-10, 264, 253], [15, 30, 50]], dtype=bool)))
        self.assertTrue(is_img_data(array([[1, 1, 1]], dtype=bool)))
        self.assertTrue(is_img_data(Image(5)))

        # Invalid cases
        self.assertFalse(is_img_data([255, 0, 0]))
        self.assertFalse(is_img_data((255, 0, 0)))
        self.assertFalse(is_img_data(124))
        self.assertFalse(is_img_data("not an image"))
        self.assertFalse(is_img_data({'r': 255, 'g': 0, 'b': 0}))
        self.assertFalse(is_img_data(array([[0, 1, 2, 3], [4, 5, 6, 7]])))
        self.assertFalse(is_img_data(array([[[0.5, 0.5, 0.5]]], dtype=float)))
        self.assertFalse(is_img_data(array([[[255, 0, 0]]])))

        # Extreme cases
        self.assertTrue(is_img_data(Image(100000)))


if __name__ == '__main__':
    unittest.main()

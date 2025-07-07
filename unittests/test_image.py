#!usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright (c) 2025 OmegaDawn
# type: ignore

"""Tests functionality of :class:`ledstripdynamics.strip.Image`."""


import unittest
from numpy import array
from numpy.testing import assert_array_equal, assert_array_almost_equal

from lsd.strip import Image
from lsd.colors import red, green, blue, black, yellow, cyan, magenta


class TestImage(unittest.TestCase):

    def setUp(self):
        self.raw = array([yellow, cyan, magenta], dtype=float)
        self.img = Image(self.raw, bg=[red, green, blue], opa=[1, 0.5, 0.1])
        self.stack_img = Image(3, bg=self.img)

    def test_init_single_value(self):
        """Tests initialization with single values / colors."""

        # Typical cases
        img = Image(2)
        self.assertEqual(len(img), 2)
        self.assertEqual(len(img.bg), 2)
        self.assertEqual(len(img.opa), 2)
        img = Image(5, bg=red, opa=0.)
        self.assertEqual(len(img), 5)
        assert_array_equal(img.bg[0], red)
        assert_array_equal(img.raw_img[0], [0, 0, 0])
        self.assertEqual(img.opa[0], 0)
        img = Image(5, bg=(0, 255, 0))
        assert_array_equal(img.bg[0], green)
        img = Image(5, bg=[0, 255, 0])
        assert_array_equal(img.bg[0], green)

        # Invalid cases
        with self.assertRaises(AssertionError):
            Image(0)
        with self.assertRaises(AssertionError):
            Image(-1)
        with self.assertRaises(TypeError):
            Image('a')
        with self.assertRaises(TypeError):
            Image(5, bg='a')
        with self.assertRaises(AssertionError):
            Image(5, bg=red, opa='a')
        with self.assertRaises(TypeError):
            Image(5, bg=True)

        # Edge cases
        Image(True)
        Image(2, opa=True)

    def test_init_arrays(self):
        """Tests initialization with array of colors."""

        # Typical cases
        img = Image([red] * 3, bg=[blue] * 3, opa=[0.1, 0.2, 0.3])
        self.assertEqual(len(img), 3)
        assert_array_equal(img, [red, red, red])
        assert_array_equal(img.bg, [blue, blue, blue])
        assert_array_equal(img.opa, [0.1, 0.2, 0.3])
        img = Image(array([blue] * 2), bg=red, opa=0.5)
        assert_array_equal(img, [blue, blue])
        assert_array_equal(img.bg, [red, red])
        assert_array_equal(img.opa, [0.5, 0.5])

        # Invalid cases
        with self.assertRaises(TypeError):
            Image([1, 2, 3])
        with self.assertRaises(AssertionError):
            Image(5, bg=red, opa=[1, 2, 3])
        with self.assertRaises(AssertionError):
            Image([red, green], bg=[blue], opa=[0.5, 0.5])
        with self.assertRaises(AssertionError):
            Image((red, green), bg=[blue, blue], opa=[0.5, 0.5, 0.5])
        with self.assertRaises(TypeError):
            Image('a')

        # Edge cases
        Image(img[:])

    def test_getitem_int(self):
        """Test ``__getitem__()`` with integer index."""

        assert_array_equal(self.img[0], yellow)
        assert_array_equal(self.img[1], cyan)
        assert_array_equal(self.img[2], magenta)

    def test_getitem_slice(self):
        """Test ``__getitem__()`` with slice."""

        sliced = self.img[:2]
        self.assertIsInstance(sliced, Image)
        self.assertEqual(len(sliced), 2)
        assert_array_equal(sliced, [yellow, cyan])

    def test_get_subitem(self):
        """Test ``__getsubitem__()``."""

        # Integer valued float index
        assert_array_equal(self.img[0.0], yellow)
        assert_array_equal(self.img[1.0], cyan)
        assert_array_equal(self.img[2.0], magenta)

        # Subpixel / float index
        subpixel = self.img[0.5]
        expected = (yellow * 0.5 + cyan * 0.5)
        assert_array_almost_equal(subpixel, expected)
        subpixel = self.img[1.75]
        expected = (cyan * 0.25 + magenta * 0.75)
        assert_array_almost_equal(subpixel, expected)

    def test_setitem_int(self):
        """Test ``__setitem__()`` with integer index."""

        self.img[0] = red
        assert_array_equal(self.img[0], red)
        self.img[1] = green
        assert_array_equal(self.img[1], green)
        self.img[2] = blue
        assert_array_equal(self.img[2], blue)

    def test_setitem_slice(self):
        """Test ``__setitem__()`` with slice."""

        self.img[:] = [red, green, blue]
        assert_array_equal(self.img[0], red)
        assert_array_equal(self.img[1], green)
        assert_array_equal(self.img[2], blue)

    def test_setsubitem(self):
        """Test ``__setsubitem__()``"""

        # Integer valued float index
        self.img[2.0] = red
        assert_array_equal(self.img[2], red)

        # Set subpixels values
        self.img[0.5] = black
        assert_array_almost_equal(self.img[0], yellow / 2)
        assert_array_almost_equal(self.img[1], cyan / 2)

        self.img[1:3] = [cyan, magenta]  # Reset subpixel influence
        self.img[1.1] = green
        expected_1 = (cyan * 0.1 + green * 0.9)
        expected_2 = (magenta * 0.9 + green * 0.1)
        assert_array_almost_equal(self.img[1], expected_1)
        assert_array_almost_equal(self.img[2], expected_2)

    def test_assigning_bg(self):
        """Tests assigning background stacks."""

        img1 = Image(3, bg=[red, green, blue])
        with self.assertRaises(ValueError):
            img1.bg = img1

        img2 = Image(3, bg=img1)
        img3 = Image(3, bg=img2)
        with self.assertRaises(ValueError):
            img1.bg = img3

    def test_set(self):
        """Tests ``set()`` method."""

        # Valid cases
        self.img.set(0, blue)
        self.img.set(1, red, 0)
        assert_array_almost_equal(self.img.raw_img, [blue, red, magenta])
        assert_array_equal(self.img.opa, [1, 0, 0.1])

        # Invalid cases
        with self.assertRaises(IndexError):
            self.img.set(3, red)
        with self.assertRaises(AssertionError):
            self.img.set(0, 'not a color')
        with self.assertRaises(AssertionError):
            self.img.set(0, red, 'opa')

        # Edge cases
        self.img.set(0, red, True)
        self.assertEqual(self.img.opa[0], 1)

    def test_fill(self):
        """Tests ``fill()`` method."""

        # Valid cases
        self.img.fill(red)
        assert_array_equal(self.img.raw_img, [red] * self.img.n)
        self.img.fill(green, opa=0.5)
        assert_array_almost_equal(self.img.raw_img, [green] * self.img.n)
        assert_array_almost_equal(self.img.opa, [0.5] * self.img.n)

        # Invalid cases
        with self.assertRaises(AssertionError):
            self.img.fill(True)
        with self.assertRaises(AssertionError):
            self.img.fill(opa="str")

    def test_clear(self):
        """Tests ``clear()`` method."""

        self.img.clear()
        assert_array_equal(self.img.raw_img, [black] * self.img.n)
        assert_array_almost_equal(self.img.opa, [1] * self.img.n)

    def test_img(self):
        """Tests the calculation of the real ``img`` property."""

        assert_array_almost_equal(
            self.img.cmp,
            [[255, 255, 0],
             [0, 255, 127.5],
             [25.5, 0, 255]])


if __name__ == '__main__':
    unittest.main()

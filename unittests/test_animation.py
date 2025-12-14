#!usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright (c) 2025 OmegaDawn

"""Tests functionality of :class:`lsd.animation.Animation`."""


import unittest
from numpy.testing import assert_array_equal

from lsd.strip import Animation
from lsd.visuals import blink
from lsd import MAIN_COLOR
from lsd.colors import black


class TestAnimation(unittest.TestCase):

    def setUp(self):
        self.anim = Animation(blink(10, on_frames=1, off_frames=1), 10)

    def test_init(self):
        """Tests animation initialization."""

        Animation(blink, 10)
        a = Animation(visual=blink, pixels=10)
        self.assertEqual(a.visual.__name__, blink.__name__)  # type: ignore
        self.assertTrue(a.playback)

        # Invalid cases
        with self.assertRaises(TypeError):
            Animation('a', 10)  # type: ignore
        with self.assertRaises(TypeError):
            Animation(blink, 'a')  # type: ignore

    def test_next_frame(self):
        """Tests getting next frame."""

        self.anim.__next_frame__()
        frame_on = self.anim.cmp
        self.anim.__next_frame__()
        frame_off = self.anim.cmp
        assert_array_equal(frame_on, [MAIN_COLOR] * self.anim.n)
        assert_array_equal(frame_off, [black] * self.anim.n)

        # Disabled playback
        self.anim.set_playback(False)
        self.anim.__next_frame__()
        assert_array_equal(self.anim.cmp, frame_off)


if __name__ == '__main__':
    unittest.main()

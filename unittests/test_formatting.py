#!usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright (c) 2025 OmegaDawn

"""Tests functionality of :mod:`ledstripdynamics.utils.formatting`."""


import unittest
from lsd.utils.formatting import format_time


class TestFormatting(unittest.TestCase):

    def test_format_time_seconds(self):
        self.assertEqual(format_time(1), '1.00 sec')
        self.assertEqual(format_time(0.5), '500.00 ms')
        self.assertEqual(format_time(60), '1.00 min')
        self.assertEqual(format_time(3600), '1.00 h')
        self.assertEqual(format_time(86400), '1.00 d')
        self.assertEqual(format_time(0.001), '1.00 ms')
        self.assertEqual(format_time(0.000001), '1.00 µs')
        self.assertEqual(format_time(0.000000001), '1.00 ns')
        self.assertEqual((format_time(60, 0)), '1 min')
        self.assertEqual(format_time(60, 1), '1.0 min')
        self.assertEqual(format_time(60, 3), '1.000 min')


if __name__ == '__main__':
    unittest.main()

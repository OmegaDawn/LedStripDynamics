#!usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright (c) 2025 OmegaDawn

"""Utilities for formatting data."""


def format_time(time: float, decimal_places: int = 2) -> str:
    """Converts a duration to its best suited unit.

    The **time** in seconds will be converted to the time unit that is
    best suited for that value. The conversion range is from nanoseconds
    to days.

    Parameters
    ----------
    time : float
        Time in [sec]
    decimal_places : int, optional
        Number of decimal places to show

    Returns
    -------
    str
        The converted time and its unit

    Examples
    --------
    >>> format_time(60)
    '1.00 min'
    >>> format_time(0.000000001234, 3)
    '1.234 ns'
    """

    units = [(86400.0, 'd'),
             (3600.0, 'h'),
             (60.0, 'min'),
             (1.0, 'sec'),
             (1e-3, 'ms'),
             (1e-6, 'µs'),
             (1e-9, 'ns'),]

    unit = 'sec'  # NOSONAR
    for factor, unit in units:
        if abs(time) >= factor:
            time /= factor
            break
    _time = round(time, decimal_places)
    return f'{_time:.{decimal_places}f} {unit}'

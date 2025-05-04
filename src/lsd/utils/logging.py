#!usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright (c) 2025 OmegaDawn

"""Logging utilities."""


from os import getenv
from rich.logging import RichHandler
from logging import getLogger as getLogger


def get_logger(name: str, level: str = 'DEBUG'):
    """Gets a logger instance."""

    _logger = getLogger(name)
    _logger.setLevel(level)
    _logger.addHandler(RichHandler())

    return _logger


_log_level = getenv('LSD_LOG_LEVEL', 'DEBUG').upper()
logger = get_logger('lsd', _log_level)
"""Logger for the :mod:`ledstripdynamics` package."""

#!usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright (c) 2025 OmegaDawn

"""Various utilities."""


from typing import Any


def get_toml_data(path: str) -> dict[str, dict[str, Any]]:
    """Loads a ``.toml`` file as an dictionary.

    Parameters
    ----------
    path : ``str``
        Path to a ``.toml`` file.

    Returns
    -------
    ``dict[str, dict[str, Any]]``
        Dictionary containing the data from the ``.toml`` file
    """

    if not path.endswith('.toml'):
        raise ValueError("The file must be a '.toml' file.")

    from toml import load
    with open(path, 'r', encoding='utf-8') as file:
        toml_dict = load(file)
    return toml_dict

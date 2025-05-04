#!usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright (c) 2025 OmegaDawn

"""Various utilities."""


from time import perf_counter
from timeit import timeit
from typing import Any, Callable, Iterable
from lsd.utils.formatting import format_time
from lsd.utils.logging import logger


def get_toml_data(path: str) -> dict[str, dict[str, Any]]:
    """Loads a ``.toml`` file as a dictionary.

    Parameters
    ----------
    path : str
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


def track_runtime(func: Callable) -> Callable:
    """Wrapper that outputs the runtime of a function.

    Used as decorator this will run the decorated function and log the
    runtime of that function. The runtime gets formatted and outputted
    to :attr:`lsd.logger`.

    Parameters
    ----------
    func : ``Callable``
        The function to be executed

    Returns
    -------
    ``Callable``
        The wrapped function **func**

    Examples
    --------
    >>> @track_runtime
    ... def some_function():
    ...     print("Hello")
    >>> some_function()
    Hello
    Function 'some_function' executed in 0.0001 sec

    Notes
    -----
    - :attr:`lsd.logger` must be in debug mode to see the output, which
      is its default.
    """

    def wrapper(*args, **kwargs):
        start_time = perf_counter()
        result = func(*args, **kwargs)
        end_time = perf_counter()
        _runtime = format_time(end_time - start_time)
        logger.debug("Function '%s' executed in  %s",
                     func.__name__, _runtime)
        return result
    return wrapper


def benchmark_runtime(func: Callable,
                      args: Iterable | None = None,
                      kwargs: dict | None = None,
                      trials: int = 1
                      ) -> float:
    """Runs a function multiple times and returns the average runtime.

    Parameters
    ----------
    func : ``Callable``
        The function to be executed
    args : ``Iterable``, optional
        Arguments for the function
    kwargs : ``dict``, optional
        Keyword arguments for the function
    trials : ``int``, optional
        Number of times the function should be executed

    Returns
    -------
    ``float``
        Average runtime duration in [sec]
    """

    if args is None:
        args = []
    if kwargs is None:
        kwargs = {}
    return timeit(lambda: func(*args, **kwargs), number=trials) / trials

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright (c) 2025 OmegaDawn

"""CLI scripts for the project."""


def build_docs():
    """Builds the project documentation with ``Sphinx``.

    All relevant files are at ``doc/source`` from the project root. The
    documentation is build in ``html`` format at ``doc/build``. Note
    that the development dependencies must be installed to run this
    script.
    """

    from subprocess import run
    from os import makedirs
    from os.path import join, dirname

    docs_dir = join(dirname(__file__), '..', 'doc', 'source')
    build_dir = join(docs_dir, '..', 'build', 'html')
    makedirs(build_dir, exist_ok=True)
    run(['sphinx-build', '-b', 'html', docs_dir, build_dir], check=True)

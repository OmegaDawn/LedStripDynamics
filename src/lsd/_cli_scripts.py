#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright (c) 2025 OmegaDawn

"""CLI scripts for the project."""


from os import makedirs
from shutil import rmtree
from os.path import join, dirname
from argparse import ArgumentParser
from subprocess import run
from webbrowser import open as web_open


def docs():
    """Builds the project documentation with ``Sphinx``.

    All relevant files are at ``doc/source`` from the project root. The
    documentation is build in *html* format at ``doc/build``. Note
    that the development dependencies must be installed to run this
    script.
    """

    parser = ArgumentParser(
        description="Build or open ledstripdynamics project documentation.")
    parser.add_argument(
        '--open', '-o', action='store_true',
        help="Open documentation in webbrowser")
    parser.add_argument(
        '--clear', '-c', action='store_true',
        help="Clear existing documentation")
    parser.add_argument(
        '--build', '-b', action='store_true',
        help="Build the documentation")
    args = parser.parse_args()

    # Show help if no arguments are provided
    if not any(vars(args).values()):
        parser.print_help()
        return

    # Paths
    base_path = join(dirname(__file__), '..', '..', 'doc')
    docs_dir = join(base_path, 'source')
    build_dir = join(base_path, 'build')

    # Clear
    if args.clear:
        rmtree(build_dir, ignore_errors=True)
        rmtree(join(docs_dir, '_autosummary'), ignore_errors=True)
        rmtree(join(docs_dir, 'uml_images'), ignore_errors=True)
        print("Removed files of built documentation")

    # Build docs
    if args.build:
        makedirs(build_dir, exist_ok=True)
        run(['sphinx-build', '-b', 'html', docs_dir, build_dir], check=True)

    # Web open
    if args.open:
        web_open('file://' + join(build_dir, 'index.html'))
        print("Opening documentation in webbrowser...")

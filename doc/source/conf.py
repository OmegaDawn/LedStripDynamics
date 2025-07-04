#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright (c) 2025 OmegaDawn

"""Configuration file for Sphinx documentation builds."""


from sys import path
from os.path import abspath


try:
    from lsd.utils import get_toml_data
except ModuleNotFoundError as exc:
    raise ModuleNotFoundError(
        "The ledstripdynamics (lsd) package must be installed in the "
        "used environment to build the documentation.") from exc


info = get_toml_data('../../pyproject.toml')  # Path relative to this file
project = info['project']['name']
author = info['project']['authors'][0]['name']
copyright = info['tool']['copyright']['copyright']  # pylint: disable=W0622
release = info['project']['version']
path.insert(0, abspath('../../src/lsd'))


# -- General configuration ---------------------------------------------------
extensions = [
    'sphinx.ext.inheritance_diagram',
    'sphinx.ext.intersphinx',
    'sphinx.ext.autosummary',
    'sphinx.ext.napoleon',
    'sphinx.ext.viewcode',
    'sphinx.ext.graphviz',
    'sphinx.ext.duration',
    'sphinx.ext.doctest',
    'sphinx.ext.autodoc',
    'sphinx_copybutton',
    'sphinx_mdinclude',
    'sphinx_uml'
    ]
source_suffix = {
    '.rst': 'restructuredtext',
    '.txt': 'markdown',
    '.md': 'markdown'}

napoleon_use_rtype = False
autosummary_generate = True
napoleon_preprocess_types = True
napoleon_numpy_docstring = True
autodoc_inherit_docstrings = True
uml_all_associated = True
uml_all_ancestors = True
uml_colorized = True
templates_path = ['_templates']
autodoc_member_order = 'bysource'
# graphviz_output_format = "svg"
# BUG: Output format currently conflicts between uml & inheritance extensions
#      If disabled links in graph don't work but back ground is transparent
inheritance_graph_attrs = {
    'bgcolor': 'transparent',
}
inheritance_node_attrs = {
    'style': 'filled',
    'fillcolor': 'gray50',
    'color': 'gray'
}
inheritance_edge_attrs = {
    'color': 'gray'
}
exclude_patterns = []
nitpicky = True
nitpick_ignore_regex = [
    ('py:.*', r'numpy(\..*)?'),  # NOSONAR
    ('py:.*', r'rich(\..*)?'),
    ('py:.*', r'ndarray(\..*)?'),
    ('py:.*', r'multiprocessing(\..*)?'),
    ('py:.*', r'lsd\.utils\.emulation\.NeoPixel(\..*)?'),
]
intersphinx_mapping = {
    'python': ('https://docs.python.org/3', None),
    'numpy': ('https://numpy.org/doc/stable/', None),
    'matplotlib': ('https://matplotlib.org/stable/', None),
    'rich': ('https://rich.readthedocs.io/en/stable/', None),
    'neopixel': ('https://docs.circuitpython.org/projects/neopixel/en/latest/',
                 None)
}


# -- Options for HTML output -------------------------------------------------
html_theme = 'furo'
html_static_path = ['_static']

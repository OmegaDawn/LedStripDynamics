# ledstripdynamics
A library for amazing light shows on LED-Strips

## Description
The LedStripDynamics (LSD) library is currently in its early development stages. It aims to develop a comprehensive library for creating light effects and animations on LED strips. The library will support customizable and combinable effects, enabling the creation of highly dynamic light shows. The initial phase of development focuses on simulating LED strip behavior, with subsequent support planned for WS2812B LED strips and other types of LED strips. The ultimate goal is to establish a foundational visual library that can be utilized in future projects, such as an AI-driven music visualizer.

## Features
<span style="opacity: 0.5;">Well... none right now :(</span>


## Installation
1. Copy/Clone the repository
2. Open terminal navigate to the repository
3. Run ``python.exe -m pip install -e .``
4. Optionally, to be able to build the documentation [Graphviz](https://graphviz.org/) must be installed.


## Dev
Development dependencies and scripts can be install with ``python.exe -m pip install -e .[dev]``.
# TODO: graphviz

## Usage
Use the library like any other python library
```
import lsd
from lsd import *
```

## Documentation
The project documentation can be generated through [Sphinx](https://www.sphinx-doc.org/en/master/). Necessary files are located in ``doc`` folder. To build the documentation run the ``lsd_build_docs`` command in a CLI. Note that the dev utilities need to be installed for this.


## License
GNU General Public License (GPL)

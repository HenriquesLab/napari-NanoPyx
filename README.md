# napari-nanopyx

<img src="https://github.com/HenriquesLab/NanoPyx/blob/main/.github/logo.png" align="right" width="230"/>

[![License](https://img.shields.io/github/license/HenriquesLab/NanoPyx?color=Green)](https://github.com/HenriquesLab/NanoPyx/blob/main/LICENSE.txt)
[![PyPI](https://img.shields.io/pypi/v/napari-nanopyx.svg?color=green)](https://pypi.org/project/napari-nanopyx)
[![Python Version](https://img.shields.io/pypi/pyversions/napari-nanopyx.svg?color=green)](https://python.org)
[![napari hub](https://img.shields.io/endpoint?url=https://api.napari-hub.org/shields/napari-nanopyx)](https://napari-hub.org/plugins/napari-nanopyx)
[![Docs](https://img.shields.io/badge/documentation-link-blueviolet)](https://github.com/HenriquesLab/napari-NanoPyx/wiki/3.-Methods)
[![Wiki](https://img.shields.io/badge/wiki-click_me-blue)](https://github.com/HenriquesLab/napari-NanoPyx/wiki)

napari plugin of [NanoPyx](https://github.com/HenriquesLab/NanoPyx) (the successor to NanoJ) - focused on light microscopy and super-resolution imaging.

----------------------------------

This [napari] plugin was generated with [Cookiecutter] using [@napari]'s [cookiecutter-napari-plugin] template.

## What is the NanoPyx 🔬 Library?

NanoPyx is a library specialized in the analysis of light microscopy and super-resolution data.
It is a successor to [NanoJ](https://github.com/HenriquesLab/NanoJ-Core), which is a Java library for the analysis of super-resolution microscopy data.

NanoPyx focuses on performance, by heavily exploiting cython aided multiprocessing and simplicity. It implements methods for the bioimage analysis field, with a special emphasis on those developed by the [Henriques Laboratory](https://henriqueslab.github.io/).
It will be distributed as a Python Library and also as [Codeless Jupyter Notebooks](https://github.com/HenriquesLab/NanoPyx#codeless-jupyter-notebooks-available), that can be run locally or on Google Colab, and as a [napari plugin](https://github.com/HenriquesLab/napari-NanoPyx).

You can read more about NanoPyx in our [publication].

Currently it implements the following approaches:
- A reimplementation of the NanoJ image registration, SRRF and Super Resolution metrics
- eSRRF
- Non-local means denoising
- More to come soon™


## Installation

You can install `napari-nanopyx` via [pip]:

    pip install napari-nanopyx

## User Documentation

You can find installation and usage instructions in the [wiki](https://github.com/HenriquesLab/napari-NanoPyx/wiki).

## Contributing

Contributions are very welcome.
Please read our [Contribution Guidelines](https://github.com/HenriquesLab/NanoPyx/blob/main/CONTRIBUTING.md) to know how to proceed.

## License

Distributed under the terms of the [CC-By v4.0] license,
"napari-nanopyx" is free and open source software

## Issues

If you encounter any problems, please [file an issue] along with a detailed description.

[napari]: https://github.com/napari/napari
[Cookiecutter]: https://github.com/audreyr/cookiecutter
[@napari]: https://github.com/napari
[MIT]: http://opensource.org/licenses/MIT
[BSD-3]: http://opensource.org/licenses/BSD-3-Clause
[GNU GPL v3.0]: http://www.gnu.org/licenses/gpl-3.0.txt
[GNU LGPL v3.0]: http://www.gnu.org/licenses/lgpl-3.0.txt
[Apache Software License 2.0]: http://www.apache.org/licenses/LICENSE-2.0
[Mozilla Public License 2.0]: https://www.mozilla.org/media/MPL/2.0/index.txt
[CC-By v4.0]: https://creativecommons.org/licenses/by/4.0/
[cookiecutter-napari-plugin]: https://github.com/napari/cookiecutter-napari-plugin

[napari]: https://github.com/napari/napari
[tox]: https://tox.readthedocs.io/en/latest/
[pip]: https://pypi.org/project/pip/
[PyPI]: https://pypi.org/
[publication]: https://doi.org/10.1038/s41592-024-02562-6

## Citing

If you found this work useful, please cite our [publication].

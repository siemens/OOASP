# OOASP

OOASP is a schema for describing object-oriented models with Answer Set Programming.

OOASP has been developed for research purposes to demonstrate how to describe and instantiate object-oriented models in Answer Set Programming. 
The main application area is product configuration i.e. reasoning about product configuration models.

Older encodings produced along with the original publications on OOASP can be found in [old_encodings](old_encodings).
Currently, the main focus of this project is a prototype for interactive configuration using OOASP as described below.

## Interactive Configuration with ASP

Prototype for interactive configuration using ASP initially developed by [Susana Hahn](https://github.com/susuhahnml) (Potassco Solutions) as part of a collaboration between [Potassco Solutions](https://potassco.com/) and [Siemens](https://www.siemens.com/innovation).

### Installation

```bash
poetry install
```

### Usage

Before running any of the programs, make sure the virtual environment has been activated. This can be done using the command:
```
poetry shell
```

The files corresponding to the current version are in [ooasp](ooasp).

The package usage and new features are showcased in the jupyter notebooks inside the folder [usage](usage).

In order to create a configuration using the command line use the file `run.py` found in the [ooasp](ooasp) directory. This program allows for the specification of an initial partial configuration using arguments in the format `--component N` where `N` refers to the number of components present in the initial configuration and `component` to the class name of the component. *Example: `python ooasp/run.py --elementA 5`*

### Documentation

For the documentation of the protoype see [DOC.md](DOC.md)

## Literature

### Research Papers on OOASP

OOASP: Connecting Object-Oriented and Logic Programming (2015): [Conference paper](https://doi.org/10.1007/978-3-319-23264-5_28) | [Preprint](https://arxiv.org/abs/1508.03032)

### Research Papers on Interactive Configuration with ASP

Interactive Configuration with ASP Multi-Shot Solving (2023): [Workshop Paper](https://ceur-ws.org/Vol-3509/paper13.pdf )

Challenges of Developing an API for Interactive Configuration using ASP (2022): [Extended Abstract](http://www.kr.tuwien.ac.at/events/taasp22/papers/TAASP_2022_paper_5.pdf)

Solver Requirements for Interactive Configuration (2020): [Journal article](https://www.jucs.org/jucs_26_3/solver_requirements_for_interactive.html)

## Licensing

OOASP is distributed under the [MIT License](LICENSE).

Copyright (c) 2022-2024 Siemens AG Oesterreich

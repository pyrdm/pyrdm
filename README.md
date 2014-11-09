    Copyright (C) 2014 Christian T. Jacobs, Alexandros Avdis, Gerard J. Gorman, Matthew D. Piggott.

    This file is part of PyRDM.

    PyRDM is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    PyRDM is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with PyRDM.  If not, see <http://www.gnu.org/licenses/>.

PyRDM
=====

PyRDM is a Python module for research data management (RDM). It facilitates the automated online publication of scientific software and associated input and output data.

[![Build Status](https://travis-ci.org/pyrdm/pyrdm.svg?branch=master)](https://travis-ci.org/pyrdm/pyrdm)
[![Documentation Status](https://readthedocs.org/projects/pyrdm/badge/?version=latest)](https://readthedocs.org/projects/pyrdm/?badge=latest)

Quick Start
-----------

In order to use PyRDM you must build as well as configure the package. Build the package by carrying out the following steps:

1. Install the core dependencies by `sudo pip install -r requirements.txt`
2. Make a clone of this repository by `git clone https://github.com/pyrdm/pyrdm.git pyrdm`
3. Build the package by `cd pyrdm; sudo make install`
4. Build the documentation by `make docs`. This will produce an HTML version of the documentation in the `docs/build` directory. Alternatively, you can view the latest version of the documentation [here](http://pyrdm.readthedocs.org).

The configuration procedure allows PyRDM to access and upload files to your Figshare or Zenodo account. Please see the documentation that you have just built for a graphical guide on how to do this.

Dependencies
------------

PyRDM depends on:

* [GitPython](https://pypi.python.org/pypi/GitPython/)
* [requests-oauthlib](https://github.com/requests/requests-oauthlib)
* [Sphinx](http://sphinx-doc.org/) - to build the documentation.
* [libspud](https://launchpad.net/spud) - this package is not necessary if you do not wish to run the PyRDM-based publication tool `fluidity-publish` specifically designed for the Fluidity CFD code.


Citing
------

When citing PyRDM, please use the following citation:

Jacobs, C.T., Avdis, A, Gorman, G.J. and Piggott, M.D. 2014. PyRDM: A Python-based library for automating the management and online publication of scientific software and data. *Journal of Open Research Software* 2(1):e28, DOI: [http://dx.doi.org/10.5334/jors.bj](http://dx.doi.org/10.5334/jors.bj)


Contact
-------

If you have any questions or comments about PyRDM, please send them via email to <c.jacobs10@imperial.ac.uk>.

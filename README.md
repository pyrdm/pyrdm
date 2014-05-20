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

PyRDM is a Python module for research data management (RDM). It facilitates the automated publication of scientific software and associated input and output data.

Quick Start
-----------

In order to use PyRDM you must build as well as configure the package. Build the package carrying out the following steps:

1. Install GitPython by ```sudo pip install gitpython```
2. Install requests-oauthlib by ```sudo pip install requests requests_oauthlib```
3. Make a clone of this repository by ```git clone https://YOUR_BB_USERNAME@bitbucket.org/ctjacobs/pyrdm.git pyrdm```
4. Build the package by ```cd pyrdm; sudo make install```

The configuration procedure ties the PyRDM package to a particular GidHub repository and your figshare account. The GitHub repository should contains the fluidity code that you use for simulations and need to publish with your data as a file set. To configure PyRDM carry out the following steps:

1. 

Dependencies
------------

PyRDM depends on:

* [GitPython](https://pypi.python.org/pypi/GitPython/)
* [requests-oauthlib](https://github.com/requests/requests-oauthlib)
* pdflatex - to build the user manual.
* [libspud](https://launchpad.net/spud) - this package is not necessary if you do not wish to run the PyRDM-based publication tool `fluidity-publish` specifically designed for the Fluidity CFD code.

Documentation
-------------

The user manual can be built by typing `make manual` at the command line, assuming that the current working directory is the PyRDM base directory (i.e. the same directory that this Makefile is in).

#!/usr/bin/env python

#    Copyright (C) 2014 Christian T. Jacobs, Alexandros Avdis, Gerard J. Gorman, Matthew D. Piggott.

#    This file is part of PyRDM.

#    PyRDM is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    PyRDM is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with PyRDM.  If not, see <http://www.gnu.org/licenses/>.

from distutils.core import setup

setup(name='PyRDM',
      version='0.3',
      license='GPLv3',
      description='PyRDM is a Python module for research data management (RDM). It facilitates the automated publication of scientific software and associated input and output data.',
      author='Christian T. Jacobs, Alexandros Avdis, Gerard J. Gorman, Matthew D. Piggott',
      url='https://github.com/pyrdm/pyrdm',
      packages=['pyrdm'],
      provides=['pyrdm'],
      install_requires=['requests', 'restkit', 'GitPython >= 0.3.2.RC1', 'gitdb', 'sword2', 'Sphinx'],
      package_dir = {'pyrdm': 'pyrdm'},
      scripts=["bin/fluidity-publish", "bin/pyrdm-publish"],
      data_files=[]
     )


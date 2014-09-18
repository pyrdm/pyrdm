Introduction
============

Overview
--------

PyRDM is a project that focuses on the relationship between data and the
scientific software that has either created that data, or operates on
that data to create new information. Two examples from geoscience are
given for illustrative purposes:

-  Dispersion of saline solution into an estuary from desalination
   plant.

   -  Input data: Bathymetry, atmospheric forcing, etc.

   -  Software: Pre-/post-processing codes; numerical models.

   -  Output data: Provenance; simulated flow fields; diagnostic
      quantities.

-  Characterisation of pores media for carbon sequestration.

   -  Input data: Micro-CT images of rock samples.

   -  Software: Pre-/post-processing of data (e.g. image segmentation,
      mesh generation); numerical models.

   -  Output data: Provenance; computational meshes that could be used
      by other flow solvers; computed flow fields; diagnostics.

From these two examples one can already start to see a great deal of
generality emerging. In order to achieve reproducibility, or indeed
computability, one must be able to capture all of the input data (i.e.
collected/measured data which should also have its associated
provenance). Next the actual software that draws information from that
data must be captured, and care must be taken to ensure that the same
version that created a particular result from the data is used. Finally,
the output data from the software must be captured, including provenance
data that details how the input data and software were used to create
this new data. PyRDM aims to address these needs by facilitating the
automated management and online publication of software and data via
citable repositories hosted by Figshare. This library can be
incorporated into the workflow of scientific software to allow research
output to be curated in a straight-forward manner.

Licensing
---------

PyRDM is released under the GNU General Public License. Further details
can be found in the COPYING file supplied with this software.

Getting started
===============

System requirements
-------------------

A standard Python installation is required, as well as any additional
Python modules that are listed in the README file under the
“Dependencies” section. PyRDM is designed to run on the Linux operating
system. All development and testing takes place on the Ubuntu Precise
(12.04) distribution.

Installation
------------

It is recommended that users use the terminal to install and run PyRDM.
After navigating to the base directory of PyRDM (i.e. the directory that
the Makefile is in), use the following command to install the PyRDM
library:

``make install``

**Note 1:** ``sudo`` may be needed for this if the default install
directory is located outside of ``/home``. This will yield a system-wide
install of PyRDM, which is recommended.

**Note 2:** In order for Python to find the PyRDM module, you will need
to add the PyRDM base directory to your ``PYTHONPATH`` environment
variable, unless you have used ``sudo`` as mentioned in Note 1 above.
This can be achieved using:

``export PYTHONPATH=$PYTHONPATH:/path/to/pyrdm``

You may wish to add this statement to your
``/home/your_username/.bashrc`` or ``/etc/bash.bashrc`` files so the
``PYTHONPATH`` is set correctly each time you log in.

Configuration
-------------

You should copy the contents of the file ``pyrdm.ini.example`` to a new
file called ``pyrdm.ini`` and save it in the
``/home/your_username/.config`` directory. If this directory does not
exist, please create it first using

``mkdir /home/your_username/.config``

The contents of the new file ``pyrdm.ini`` should then be modified as
per the guidance in the following subsections.

Figshare authentication
~~~~~~~~~~~~~~~~~~~~~~~

PyRDM requires a set of authentication details in order to publish and
modify files using your Figshare account. You will need to login and use
the Figshare web interface to generate these authentication details,
after which you should paste them into the ``figshare`` section of the
configuration file.

#. Go to ``http://figshare.com/account/applications``

#. Click ``Create a new application``

#. Fill in the application details as per Figure
   [fig:application:sub:`d`\ etails]

#. Ensure that the application has read and write access to your Drafts,
   Private and Public articles, as per Figure [fig:permissions]

#. Click ``Save changes``. PyRDM should appear in your list of
   applications which can access your account.

#. Click ``View`` next to PyRDM and then click the ``Access codes`` tab
   to see the authentication details. The four fields should be pasted
   into the ``pyrdm.ini`` configuration file.

**Note:** If you are publishing through a group account, you will need
to ask the account’s administrator for the authentication details.

|The application details for PyRDM.| [fig:application:sub:`d`\ etails]

|The set of permissions required by PyRDM.| [fig:permissions]

Testing
-------

PyRDM comes with a suite of unit tests which verify the correctness of
its functionality. It is recommended that you run these unit tests
before using PyRDM by executing:

``make unittest``

on the command line. Many of these tests require access to a Figshare
account, so please ensure that the ``pyrdm.ini`` setup file contains
valid Figshare authentication tokens.

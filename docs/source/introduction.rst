Introduction
============

Overview
--------

`PyRDM <https://github.com/pyrdm/pyrdm/>`_ is a project that focuses on the relationship between data and the
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
this new data.

The PyRDM library aims to address these needs by facilitating the automated management and publication of software source code and data via online, citable repositories hosted by `Figshare <http://www.figshare.com/>`_, `Zenodo <http://www.zenodo.org/>`_, or a `DSpace <http://www.dspace.org/>`_-based service. The library can be readily incorporated into scientific workflows to allow research outputs to be curated and shared in a straight-forward manner. Further details and technical information are provided in the following paper:

- **C. T. Jacobs, A. Avdis, G. J. Gorman, M. D. Piggott (2014)**. *PyRDM: A Python-based library for automating the management and online publication of scientific software and data*. Journal of Open Research Software, 2(1):e28, DOI: `10.5334/jors.bj <https://doi.org/10.5334/jors.bj>`_

and in the resources listed `here <http://pyrdm.readthedocs.org/en/latest/references.html>`_.

PyRDM is open-source, and is available to download from the project's GitHub repository: `<https://github.com/pyrdm/pyrdm>`_

Licensing
---------

PyRDM is released under the GNU General Public License. Further details
can be found in the COPYING file supplied with this software.


Application: Fluidity-Publish
=============================

Fluidity-Publish is a Python program which uses the PyRDM library. It is
designed specifically for use with a computational fluid
dynamics code called `Fluidity <http://www.fluidity-project.org/>`_. Currently, you must use
the ``publishing`` branch of Fluidity which contains the publishing functionality:

#. ``git clone https://github.com/FluidityProject/fluidity.git``

#. ``cd fluidity``

#. ``git checkout publishing``

Note that you must build Fluidity (or at least satisfy the libspud dependency noted in
the README file) before using Fluidity-Publish. You may need to add
Fluidity's 'python' directory to your ``PYTHONPATH`` environment
variable in order for the libspud module to be found.

Enable publishing
-----------------

If we want to publish the Fluidity source code used to run a particular
simulation, along with the input and output data, we first need to
enable the ``publish`` option in that simulation's configuration/options
file (the ".flml" file), as shown in figure:diamond_. Simply select
which publishing service you wish to use (e.g. Figshare or Zenodo), and
under the ``input_files`` and ``output_files`` sub-options (see Figure
[fig:diamond]), enter the paths (relative to the options file) to the
input and output files you wish to publish in the following format (a
Python list of strings):

``["path/to/file1", "path/to/file2", "path/to/file3"]``

You may use wildcard characters here (e.g. "\*vtu" to publish all
VTK-based simulation output). Instead of creating a new code repository
or fileset on Figshare or Zenodo, you may also publish to an existing
one by entering its ID in the following option(s):

``/publish/{software,input_data,output_data}/pid``

   .. _figure:diamond:
   .. figure::  images/diamond.png
      :align: center
      :scale: 75 %
      :figclass: align-center
      
      The ``publish`` option enabled in a simulation's configuration file. The file is being modified in Diamond.

Using Fluidity-Publish
----------------------

To publish, you will need to use the ``fluidity-publish`` program
(located in PyRDM's 'bin' directory) at the command line; this expects
one or more of the following options, followed by the (relative or
absolute) path to the simulation's configuration file:

-  ``-s`` : Publish the Fluidity source code. This can be used in
   conjunction with the ``-v`` option to explicitly choose the version
   of Fluidity (in the form of the Git SHA-1 hash of a particular
   commit) that you want to publish.

-  ``-i`` : Publish the input data files whose paths are specified in
   the options file.

-  ``-o`` : Publish the output data files whose paths are specified in
   the options file.

-  ``-p`` : Publish the software or data, but keep it private. Must be
   used in conjunction with the ``-s``, ``-i`` or ``-o`` option. Note
   that any DOI generated will not be valid until the publication is
   made public.
   
-  ``-l`` : Set the log verbosity level (choose 'critical', 'error', 'warning', 'info', or 'debug').

e.g.
``fluidity-publish -i /data/fluidity/tests/top_hat_cg_supg/top_hat_cg_supg.flml``

or, if you did not install PyRDM, change directory (``cd``) to the PyRDM
base directory

(e.g. ``cd /home/my_username_here/pyrdm``) and use:

``python bin/fluidity-publish -i /data/fluidity/tests/top_hat_cg_supg/top_hat_cg_supg.flml``

Note that the software, input data and output data must be published
separately. You cannot yet use the -s, -i and -o options together.

Once the publication process has finished, the ID and DOI of the
publication will be added to the simulation's configuration file for
future reference. If you wish to publish the simulation data again, the
ID and DOI will be re-used (unless you remove them from the
configuration file).

Software version
~~~~~~~~~~~~~~~~

Unless you provide a particular version of Fluidity at the command-line
using the ``-v`` option, Fluidity-Publish will automatically obtain the
version of Fluidity from the file ``version.h`` stored in the
``include`` directory of the local Fluidity repository on your computer.
This file is created at compile-time when the Fluidity binary is built.
If this file is not present (perhaps because you haven't built Fluidity
yet), then Fluidity-Publish will instead use the version (SHA-1 key) of
the HEAD commit of the local repository.

Provenance data
~~~~~~~~~~~~~~~

Fluidity writes a limited amount of provenance data to the header of the
simulation's 'stat' file. If you choose to publish the output data
(which should include the 'stat' file) using the ``-o`` option, then
Fluidity-Publish will (if available) retrieve the IDs and DOIs of the
recently published software and input data from the simulation's options
file. It will then add those to the existing provenance data before
publishing the output data files that you have specified.

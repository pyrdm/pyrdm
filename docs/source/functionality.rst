PyRDM functionality
===================

Publishing software
-------------------

The publication of software is handled by the ``publish_software``
method in the Publication class. This requires:

-  The service (e.g. Figshare) authentication details (see the section on `Figshare authentication <getting_started.html#figshare-authentication>`_ or `Zenodo authentication <getting_started.html#zenodo-authentication>`_).

-  The software's name.

-  The location of the software's Git repository (or the location of any
   file within that repository) on your local hard drive.
   
-  Optionally, the version of the software that you would like to publish (for Git
   repositories, this is the SHA-1 commit hash). If this is not provided, PyRDM will publish the ``HEAD`` of the local Git repository.

Author attribution
~~~~~~~~~~~~~~~~~~

If an AUTHORS file is provided in the Git repository's base directory,
PyRDM parses it and looks for strings of a particular form. At the moment, this form depends on the service being used. However, PyRDM will hopefully be able to use a more standardised way of identifying authors in the future.

For Figshare, PyRDM looks for ``<figshare:xxxx>``, where ``xxxx`` is a Figshare author ID. This should be specified after
each author's full name. An example is:

``Christian Jacobs <figshare:554577>``

For Zenodo, PyRDM looks for ``<zenodo:(xxxx;yyyy)>``, where ``xxxx`` is the author's full name, and ``yyyy`` is the author's affiliation.

PyRDM automatically adds all authors who provide their author information to the software publication.

Publishing data
---------------

The publication of software is handled by the ``publish_software``
method in the Publication class. This requires:

-  The service authentication details (see the section on `Figshare authentication <getting_started.html#figshare-authentication>`_ or `Zenodo authentication <getting_started.html#zenodo-authentication>`_).

-  A dictionary of parameters, containing the following key-value pairs:

   -  ``title``: the title of the dataset

   -  ``description``: a description of the dataset

   -  ``files``: a list of paths to the files within the dataset.

   -  ``category``: the name of a category in `Figshare's categories
      list <http://api.figshare.com/v1/categories>`_. This is not required if using Zenodo.

   -  ``tag_name``: a single string, or list of strings, to tag the
      data's fileset with

-  Optionally, a ``pid`` (publication ID) if the dataset already exists and you wish to update it. By default, this is set
   to ``None``.

MD5 cross-checks
~~~~~~~~~~~~~~~~

When a data file is published, the file's MD5 checksum is stored in a
corresponding checksum file. The next time the user tries to publish the
file, its MD5 checksum is recomputed and compared against the MD5
checksum stored in its corresponding MD5 file. If the two MD5 checksums
are different (or the checksum file does not exist), the file is
uploaded to the server and the checksum file is updated with
the new checksum. If the two checksums are the same, the file is
unmodified and is not re-uploaded. This can help prevent unnecessary
bandwidth usage and is particularly useful when you have large data
files which are not frequently modified.

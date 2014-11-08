PyRDM functionality
===================

Publishing software
-------------------

The publication of software is handled by the ``publish_software``
method in the Publication class. This requires:

-  The Figshare authentication details (see the section on `Figshare authentication <getting_started.html#figshare-authentication>`_).

-  The software's name.

-  The version of the software that you would like to publish (for Git
   repositories, this is the SHA-1 commit hash).

-  The location of the software's Git repository (or the location of any
   file within that repository) on your local hard drive.

-  The ID of a category in Figshare's categories list. The full list of
   categories can be found here:
   ``http://api.figshare.com/v1/categories``.

Author attribution
~~~~~~~~~~~~~~~~~~

If an AUTHORS file is provided in the Git repository's base directory,
PyRDM parses it and looks for strings of the form ``figshare:xxxx``,
where ``xxxx`` is an author ID. Author IDs should be specified after
each author's full name. An example is:

``Christian Jacobs (figshare:554577)``

PyRDM automatically adds all authors who provide their Figshare author
IDs to the software publication.

Publishing data
---------------

The publication of software is handled by the ``publish_software``
method in the Publication class. This requires:

-  The Figshare authentication details (see the section on `Figshare authentication <getting_started.html#figshare-authentication>`_).

-  A dictionary of parameters, containing the following key-value pairs:

   -  ``title``: the title of the dataset

   -  ``description``: a description of the dataset

   -  ``files``: a list of paths to the files within the dataset.

   -  ``category_id``: the ID of a category in Figshare's categories
      list

   -  ``tag_name``: a single string, or list of strings, to tag the
      data's fileset with

-  Optionally, an ``article_id`` if the dataset already exists on the
   Figshare servers and you wish to update it. By default, this is set
   to ``None``.

MD5 cross-checks
~~~~~~~~~~~~~~~~

When a data file is published, the file's MD5 checksum is stored in a
corresponding checksum file. The next time the user tries to publish the
file, its MD5 checksum is recomputed and compared against the MD5
checksum stored in its corresponding MD5 file. If the two MD5 checksums
are different (or the checksum file does not exist), the file is
uploaded to the Figshare server and the checksum file is updated with
the new checksum. If the two checksums are the same, the file is
unmodified and is not re-uploaded. This can help prevent unnecessary
bandwidth usage and is particularly useful when you have large data
files which are not frequently modified.

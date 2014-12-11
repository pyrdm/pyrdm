Getting started
===============

System requirements
-------------------

A standard Python installation is required, as well as any additional
Python modules that are listed in the README file under the
"Dependencies" section. PyRDM is designed to run on the Linux operating
system. All development and testing takes place on the Ubuntu Trusty
(14.04) distribution.

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

#. Fill in the application details as per figure:application_details_.
   
   .. _figure:application_details:
   .. figure::  images/figshare_application_details.png
      :align: center
      :figclass: align-center
      
      The application details for PyRDM.

#. Ensure that the application has read and write access to your Drafts,
   Private and Public articles, as per figure:figshare_application_permissions_.

   .. _figure:figshare_application_permissions:
   .. figure::  images/figshare_application_permissions.png
      :align:   center
      
      The set of permissions required by PyRDM.

#. Click ``Save changes``. PyRDM should appear in your list of
   applications which can access your account.

#. Click ``View`` next to PyRDM and then click the ``Access codes`` tab
   to see the authentication details. The four fields should be pasted
   into the ``pyrdm.ini`` configuration file.

**Note:** If you are publishing through a group account, you will need
to ask the account's administrator for the authentication details.

Zenodo authentication
~~~~~~~~~~~~~~~~~~~~~

Zenodo uses a personal access token to handle authentication.

#. Go to ``http://zenodo.org/account/settings/applications/tokens/new/``

#. Enter ``PyRDM`` as the name of the token. Ensure that ``deposit:actions`` and ``deposit:write`` are selected, as per figure:zenodo_token_.

   .. _figure:zenodo_token:
   .. figure::  images/zenodo_token.png
      :align:   center
      
      Setting up a new personal access token for PyRDM.

#. Click ``Create``. The access token should be pasted into the ``[zenodo]`` section of the ``pyrdm.ini`` configuration file.

#. Zenodo requires at least one author's name and affiliation to be present when creating a deposition. For a software deposition, PyRDM will try to obtain this information from the ``AUTHORS`` file. However, for a dataset deposition, this information needs to be provided under the ``[general]`` section of the ``pyrdm.ini`` configuration file.

DSpace authentication
~~~~~~~~~~~~~~~~~~~~~

PyRDM provides limited support for publishing with DSpace-based services which use the `SWORD protocol <http://swordapp.org>`_ (version 2).

#. Locate the URL of the SWORD Service Document, and add it under the ``[dspace]`` section of the ``pyrdm.ini`` configuration file. Note: this URL may need to be obtained from the system administrator.

#. Add the title of the DSpace Collection that you want to publish in. Note: the publication's privacy settings are determined by the DSpace Collection, not by the `private` parameter in PyRDM.

#. Add your user name and password used to access the DSpace server. Note: this is currently stored in plain text, so make sure that the PyRDM configuration file is not readable by other users.

Testing
-------

PyRDM comes with a suite of unit tests which verify the correctness of
its functionality. It is recommended that you run these unit tests
before using PyRDM by executing:

``make unittest``

on the command line. Many of these tests require access to a Figshare
account, so please ensure that the ``pyrdm.ini`` setup file contains
valid Figshare authentication tokens.

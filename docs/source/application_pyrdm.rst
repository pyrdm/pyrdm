Application: PyRDM-Publish
==========================

Another publishing tool (see ``bin/pyrdm-publish``) has been created to
publish PyRDM itself to Figshare. At the moment this is only used as an
example program to demonstrate PyRDM's functionality without the need to
install libspud (or Fluidity and libspud) as a dependency, and therefore
any Figshare publications produced using this tool will be kept private
in your Figshare account. You can visit the "My data" page on Figshare
to view the publication details.

Only the source code hosted on PyRDM's GitHub repository can be
published; the publishing tool does not publish any input/output files.
To use ``pyrdm-publish``, you will need to provide the path to the local
Git repository on your computer containing PyRDM. For example,

``pyrdm-publish /home/my_username_here/pyrdm``

(or ``python /path/to/pyrdm/bin/pyrdm-publish /path/to/pyrdm``, if you
did not install PyRDM). The following options are also available:

-  ``-v`` : Publish a specific version (Git SHA-1 hash) of the PyRDM source code.
   
-  ``-l`` : Set the log verbosity level (choose 'critical', 'error', 'warning', 'info', or 'debug').

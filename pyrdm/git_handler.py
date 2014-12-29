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

import sys, os
import logging
import git
from urllib2 import urlopen

_LOG = logging.getLogger(__name__)

class GitHandler:

   def __init__(self, repository_location):
      try:
         self.repo = git.Repo(repository_location)
      except git.InvalidGitRepositoryError:
         _LOG.error("Either the scientific software is not under version control, or the version control system has not been detected. Perhaps you downloaded the scientific software as an archived (e.g. .zip or .tar.gz) file and the version control directory (e.g. .git) was not included.")
         sys.exit(1)
      return
      
   def archive(self, sha, archive_path):
      """ Create a .zip archive of the git repository for a given SHA-1 hash. Saves the archive to 'archive_path'. """
      try:
         tree = self.repo.tree(sha)
         f = open(archive_path, "wb")
         self.repo.archive(f, treeish=tree, format="zip")
         f.close()
      except:
         # Perhaps the local version of the software is out-of-date, or corrupted.
         # Let's try and download the .zip file from GitHub instead...
         success = self.get_archive_from_server(sha, archive_path)
         return success
      return True

   def get_archive_from_server(self, sha, archive_path):
      """ Download a GitHub .zip archive. """
      
      # Obtain the origin's URL and get the repository name from that.
      origin_url = self.repo.remotes.origin.url
      if(origin_url.endswith(".git")):
         origin_url = origin_url.replace(".git", "")
      repository_name = os.path.basename(origin_url)
      
      remote_url = "%s/archive/%s.zip" % (origin_url, sha)
   
      _LOG.info("Downloading software from GitHub (URL: %s)..." % origin_url)
      f = urlopen(origin_url)
      try:
         local_file = open(archive_path, "wb")
         local_file.write(f.read())
      except:
         _LOG.error("Could not obtain archive from the GitHub server.")
         return False

      _LOG.info("Download successful.")
      return True
      
   def get_head_version(self):
      return self.repo.head.commit.hexsha

   def get_working_directory(self):
      return self.repo.working_dir


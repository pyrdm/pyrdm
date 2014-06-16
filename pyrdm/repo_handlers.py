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
import unittest
import re

# VCS interfaces
import git
import bzrlib.branch, bzrlib.export, bzrlib.revisiontree

from urllib2 import urlopen

class GitRepoHandler:

   def __init__(self, repository_location):
      try:
         self.repo = git.Repo(repository_location)
      except:
         print "Could not open the local Git repository. Check read permissions?\n"
      return
      
   def get_github_archive_from_server(self, sha, archive_path):
      """ Download a GitHub .zip archive. """
      # FIXME: This currently supports public repositories only.
      
      # Obtain the origin's URL and get the repository name from that.
      origin_url = self.repo.remotes.origin.url
      if(origin_url.endswith(".git")):
         origin_url = origin_url.replace(".git", "")
      repository_name = os.path.basename(origin_url)
      
      remote_url = "%s/archive/%s.zip" % (origin_url, sha)
   
      print "Downloading software from GitHub (URL: %s)..." % origin_url
      f = urlopen(origin_url)
      try:
         local_file = open(archive_path, "wb")
         local_file.write(f.read())
      except:
         print "An error occurred."
         return False

      print "Download successful."
      return True
      
      
   def archive(self, sha, archive_path):
      try:
         tree = self.repo.tree(sha)
         f = open(archive_path, "wb")
         self.repo.archive(f, format="zip")
         f.close()
      except:
         return False
      return True

   def get_head_version(self):
      return self.repo.head.commit.hexsha
      
      
class BzrRepoHandler:
   def __init__(self, repository_location):
      self.branch, self.subdir = bzrlib.branch.Branch.open_containing(repository_location)
      return
      
   def archive(self, revno, archive_path):
      try:
         rev_id = self.branch.get_rev_id(revno)
         tree = bzrlib.revisiontree.RevisionTree(self.branch, rev_id)
         bzrlib.export.export(tree, archive_path, format="zip")
      except:
         return False
      return True
      
      
      

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

# VCS interfaces
import git
import bzrlib.branch, bzrlib.export, bzrlib.revisiontree

from urllib2 import urlopen

class GitHandler:

   def __init__(self, repository_location):
      try:
         self.repo = git.Repo(repository_location)
      except git.InvalidGitRepositoryError:
         print "The Git repository location is not valid or the repository does not exist."
      return
      
   def archive(self, sha, archive_path):
      """ Create a .zip archive of the git repository for a given SHA-1 hash. Saves the archive to 'archive_path'. """
      try:
         tree = self.repo.tree(sha)
         f = open(archive_path, "wb")
         self.repo.archive(f, format="zip")
         f.close()
      except:
         # Perhaps the local version of the software is out-of-date, or corrupted.
         # Let's try and download the .zip file from GitHub instead...
         success = self.get_archive_from_server(version, archive_path)
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
      
   def get_head_version(self):
      return self.repo.head.commit.hexsha

   def get_working_directory(self):
      return self.repo.working_dir

      
class BzrHandler:
   def __init__(self, repository_location):
      self.branch, self.subdir = bzrlib.branch.Branch.open_containing(repository_location)
      return
      
   def archive(self, revno, archive_path):
      """ Create a .zip archive of the bzr branch at a given revision number. Saves the archive to 'archive_path'. """
      try:
         #FIXME: This only allows the publication of the HEAD version at the moment.
         #revid = self.branch.get_rev_id(revno)
         #tree = bzrlib.revisiontree.RevisionTree(self.branch, rev_id)
         tree = self.branch.basis_tree()
         bzrlib.export.export(tree, archive_path, format="zip")
      except:
         return False
      return True
      
   def get_head_version(self):
      return self.branch.revno()


class VCSHandler:
   def __init__(self, repository_location):
      vcs_name = self.determine_vcs(repository_location)

      if(vcs_name == "git"):
         self.vcs = GitHandler(repository_location)
      elif(vcs_name == "bzr"):
         self.vcs = BzrHandler(repository_location)
      else:
         print "ERROR: Either the scientific software is not under version control, or the version control system has not been detected."
         print "Perhaps you downloaded the scientific software as an archived (e.g. .zip or .tar.gz) file and the version control directory (e.g. .git or .bzr) was not included.\n"
         sys.exit(1)
      return

   def determine_vcs(self, repository_location):
      """ Return the name of the version control system (VCS). """

      vcs_name = None

      # Try opening the repository with Git.
      try:
         repo = git.Repo(repository_location)
         vcs_name = "git"
         print "INFO: Git VCS found."
      except:
         pass

      # Try opening the repository with Bazaar.
      try:
         branch, subdir = bzrlib.branch.Branch.open_containing(repository_location)
         vcs_name = "bzr"
         print "INFO: Bazaar VCS found."
      except:
         pass

      return vcs_name


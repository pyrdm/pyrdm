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

class GitRepoHandler:

   def __init__(self, repository_location):
      try:
         self.repo = git.Repo(repository_location)
      except git.InvalidGitRepositoryError:
         print "The Git repository location is not valid or the repository does not exist."
      return
      
   def archive(self, sha, archive_path):
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
      
   def get_head_version(self):
      return self.branch.revno()


class RepoHandler(GitRepoHandler, BzrRepoHandler):
   def __init__(self, repository_location):
      repo_type = self.determine_repo_type(repository_location)

      if(repo_type == "git"):
         GitRepoHandler.__init__(self, repository_location)
      elif(repo_type == "bzr"):
         BzrRepoHandler.__init__(self, repository_location)
      else:
         print "ERROR: Either the scientific software is not under version control, or the version control system has not been detected."
         print "Perhaps you downloaded the scientific software as an archived (e.g. .zip or .tar.gz) file and the version control directory (e.g. .git or .bzr) was not included.\n"
         sys.exit(1)
      return

   def determine_repo_type(self, repository_location):
      # Determine the repository type.
      repo_type = None

      # Try opening the repository with Git.
      try:
         repo = git.Repo(repository_location)
         repo_type = "git"
         print "Git repository found."
      except:
         pass

      # Try opening the repository with Bazaar.
      try:
         branch, subdir = bzrlib.branch.Branch.open_containing(repository_location)
         repo_type = "bzr"
         print "Bazaar repository found."
      except:
         pass

      return repo_type


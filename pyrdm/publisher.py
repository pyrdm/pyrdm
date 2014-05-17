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

import ConfigParser
import sys, os
import unittest
import re

import git
import hashlib # For MD5 checksums

from pyrdm.figshare import Figshare
from pyrdm.zenodo import Zenodo

class Publisher:
   """ A Python module for publishing scientific software and data on Figshare or Zenodo. """

   def __init__(self, service):
      self.service = service
   
      # Read in the authentication tokens, etc from the configuration file.
      self.config = self._load_config(os.path.expanduser("~/pyrdm.config"))
      
      if(service == "figshare"):
         self.figshare = Figshare(client_key = self.config["client_key"], client_secret = self.config["client_secret"],
                        resource_owner_key = self.config["resource_owner_key"], resource_owner_secret = self.config["resource_owner_secret"])
      elif(service == "zenodo"):
         # FIXME: The interface to the Zenodo API is currently not authenticating properly with the Zenodo servers.
         raise NotImplementedError
         self.zenodo = Zenodo(api_key = self.config["zenodo_api_key"])
      else:
         print "Unsupported service: %s" % service
         sys.exit(1)
      return
      
   def _load_config(self, config_file_path):
      """ Load the configuration file containing the OAuth keys and information about the software name, etc
      into a dictionary called 'config' and return it. """
      try:
         f = open(config_file_path, "r")
      except IOError:
         print "Could not open the PyRDM configuration file. Check that the file 'pyrdm.config' is in your home directory, and that it is readable."
         sys.exit(1)

      config = {}
      for line in f.readlines():
         s = line.replace(" ", "").replace("\n", "")
         key, value = s.split("=")
         config[key] = value

      f.close()
      return config

   def find_software(self, software_name, sha):
      """ Checks if the software has already been published. If so, it returns the DOI.
      Otherwise it returns None. """
      
      keyword = "%s-%s" % (software_name, sha)
      
      if(self.service == "figshare"):
         results = self.figshare.search(keyword, tag=sha)

         if(results["count"] >= 1):
            print "Software %s has already been published (with SHA-1 %s)." % (software_name, sha)
            article_id = results["items"][-1]["article_id"]
            return article_id # TODO: Also return the DOI.
         else:
            return None
      else:
         # TODO: Add in Zenodo searching.
         raise NotImplementedError

   def get_authors_list(self, local_repo_location):
      repo = git.Repo(local_repo_location)
      author_ids = []
      try:
         # Assumes that the AUTHORS file is in the root directory of the project.
         f = open(repo.working_dir + "/AUTHORS", "r")
         for line in f.readlines():
            m = re.search("figshare:([0-9]+)", line)
            if(m is not None):
               author_id = int(m.group(1))
               author_ids.append(author_id)
         return author_ids
      except IOError:
         print "Could not open AUTHORS file. Does it exist? Check read permissions?"
         return None

   def publish_software(self, software_name, sha, local_repo_location):
      """ Publishes the software in the current repository to Figshare. """

      # Download the .zip file from GitHub...
      url = "%s/archive/%s.zip" % (self.config["github_location"], sha)
      
      print "Downloading software from GitHub (URL: %s)..." % url
      f = urlopen(url)
      output_file_name = self.config["github_repository_name"]+"-"+os.path.basename(url)
      with open(self.config["github_repository_name"]+"-"+os.path.basename(url), "wb") as local_file:
         local_file.write(f.read())
      print "Download complete."

      # ...then upload it to Figshare.
      print "Creating article on Figshare for software..."
      title='%s-%s' % (software_name, sha)
      description='%s version %s' % (software_name, sha)
      publication_details = self.figshare.create_article(title=title, description=description, defined_type="code", status="Drafts")
      print "Article created with DOI: %s" % publication_details["doi"]
      
      print "Adding tags..."
      self.figshare.add_tag(article_id=publication_details["article_id"], tag_name=sha)
      print "Tags added."

      print "Uploading software to Figshare..."
      self.figshare.add_file(article_id=publication_details["article_id"], file_path="test.txt")
      print "Software uploaded to Figshare."

      print "Adding all authors (with Figshare IDs) to the software article..."
      author_ids = self.get_authors_list(local_repo_location)
      print author_ids
      if(author_ids is not None):
         for author_id in author_ids:
            self.figshare.add_author(publication_details["article_id"], author_id)
      print "All authors (with Figshare IDs) added."

      return publication_details
      
   def publish_data(self, parameters, article_id=None):
      """ Create a new dataset on the Figshare server. 
      Returns a dictionary of details about the new dataset once created. """

      # FIXME: Does Figshare prevent the creation of the same article (or dataset) twice? If not, we'll need to check for this here.
         
      print "Publishing data..."      
      if(article_id is None):
         if(self.service == "figshare"):
            print "Creating dataset on Figshare for data..."
            # NOTE: The defined_type needs to be a 'fileset' to allow multiple files to be uploaded separately.
            publication_details = self.figshare.create_article(title=parameters["title"], description=parameters["description"], defined_type="fileset", status="Drafts")
            print "Dataset created with DOI: %s" % publication_details["doi"]
            print publication_details

            article_id = publication_details["article_id"]
         elif(self.service == "zenodo"):
            print "Creating dataset on Zenodo for data..."
            publication_details = self.zenodo.create_deposition(title=parameters["title"], description=parameters["description"], upload_type="dataset", state="inprogress")
            print publication_details
            print "Dataset created with DOI: %s" % publication_details["doi"]

            article_id = publication_details["id"]
      else:
         publication_details = None
         
      # Check whether any files have been modified.
      modified_files = self.find_modified(parameters["files"])
      print "The following files have been marked for uploading: ", modified_files

      existing_files = self.figshare.get_file_details(article_id)["files"]

      for f in modified_files:
         print "Uploading %s..." % f
         # Check whether the file already exists on the server. If so, over-write the version on the server.
         exists = False
         for e in existing_files:
            if(e["name"] == os.path.basename(f)):
               print "File already exists on Figshare server. Over-writing..."
               exists = True
               # FIXME: Trying to re-upload to an existing file_id doesn't seem to work.
               self.figshare.delete_file(article_id=article_id, file_id=e["id"])
               self.figshare.add_file(article_id=article_id, file_path=f)
         if(not exists):
            self.figshare.add_file(article_id=article_id, file_path=f)
         self.write_checksum(f)

      return publication_details
      
   def write_checksum(self, f):
      """ For a given file with path 'f', write a corresponding MD5 checksum file. """
      md5 = hashlib.md5(open(f).read()).hexdigest()
      checksum_file = open(f + ".md5", "w")
      checksum_file.write(md5)
      checksum_file.close()
      return

   def find_modified(self, files):
      """ Return a list of files (whose paths are in the argument 'files') which have been modified.
      This is based on MD5 checksums. """
      modified = []
      for f in files:
         if(os.path.isfile(f + ".md5")):
            checksum_file = open(f + ".md5", "r")
            md5_original = checksum_file.readline()
            md5 = hashlib.md5(open(f).read()).hexdigest()
            
            if(md5 != md5_original):
               modified.append(f)
         else:
            # No checksum file present - assume new or modified.
            modified.append(f)
            
      return modified
      
      

class TestLog(unittest.TestCase):
   """ Unit test suite for PyRDM's Publisher module. """

   def setUp(self):
      self.publisher = Publisher()
      
      f = open("test_file.txt", "w")
      f.write("Hello World! This is a file for the MD5 functionality test.")
      f.close()
      return

   def tearDown(self):
      return

   def test_md5_write_checksum(self):
      self.publisher.write_checksum("test_file.txt")
      
      f = open("test_file.txt.md5", "r")
      md5_known = "29586140472f40eec4031eb2e0d352e1"
      md5 = hashlib.md5(open("test_file.txt").read()).hexdigest()
      print "Known MD5 hash of file: %s" % md5_known
      print "Computed MD5 hash of file: %s" % md5
      assert(md5 == md5_known)
      
   def test_md5_find_modified(self):
      self.publisher.write_checksum("test_file.txt")
      
      modified = self.publisher.find_modified(["test_file.txt"])
      print "Modified files: ", modified
      assert(modified == [])
      
      # Modify the file.      
      f = open("test_file.txt", "a")
      f.write("This is another line.")
      f.close()
      
      # Check that the MD5 checksums are not the same
      md5_before = "29586140472f40eec4031eb2e0d352e1"
      md5_after = hashlib.md5(open("test_file.txt").read()).hexdigest()
      print "MD5 hash before modification: %s" % md5_before
      print "MD5 hash after modification: %s" % md5_after
      assert(md5_before != md5_after)
      
      modified = self.publisher.find_modified(["test_file.txt"])
      print "Modified files: ", modified
      assert(modified == ["test_file.txt"])
      
if(__name__ == '__main__'):
   unittest.main()

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
from urllib2 import urlopen

from pyrdm.figshare import Figshare
from pyrdm.zenodo import Zenodo

class Publisher:
   """ A Python module for publishing scientific software and data on Figshare or Zenodo. """

   def __init__(self, service):
      self.service = service
   
      # Read in the authentication tokens, etc from the configuration file.
      self.config = self.load_config(os.path.expanduser("~/.config/pyrdm.ini"))
      
      if(service == "figshare"):
         self.figshare = Figshare(client_key = self.config.get("figshare", "client_key"), client_secret = self.config.get("figshare", "client_secret"),
                        resource_owner_key = self.config.get("figshare", "resource_owner_key"), resource_owner_secret = self.config.get("figshare", "resource_owner_secret"))
      elif(service == "zenodo"):
         # FIXME: The interface to the Zenodo API is currently not authenticating properly with the Zenodo servers.
         raise NotImplementedError
         self.zenodo = Zenodo(api_key = self.config.get("zenodo", "api_key"))
      else:
         print "Unsupported service: %s" % service
         sys.exit(1)

      return
      
   def load_config(self, config_file_path):
      """ Load the configuration file containing the OAuth keys and information about the software name, etc
      into a dictionary called 'config' and return it. """

      config = ConfigParser.ConfigParser()
      have_config = (config.read(config_file_path) != [])
      if(not have_config):
         print "Could not open the PyRDM configuration file. Check that the file 'pyrdm.ini' is in the ~/.config/ directory, and that it is readable."
         sys.exit(1)
      return config

   def publish_software(self, software_name, software_sha, software_local_repo_location, category_id, private=False):
      """ Publishes the software in the current repository. """

      # Obtain the origin's URL and get the repository name from that.
      repo = git.Repo(software_local_repo_location)
      origin_url = repo.remotes.origin.url
      if(origin_url.endswith(".git")):
         origin_url = origin_url.replace(".git", "")
      repository_name = os.path.basename(origin_url)

      # Download the .zip file from GitHub...
      url = "%s/archive/%s.zip" % (origin_url, software_sha)
      
      print "Downloading software from GitHub (URL: %s)..." % url
      f = urlopen(url)
      file_name = repository_name + "_" + os.path.basename(url)
      with open(file_name, "wb") as local_file:
         local_file.write(f.read())
      print "Download complete."

      # ...then upload it to Figshare.
      print "Creating code repository on Figshare for software..."
      title='%s (%s)' % (software_name, software_sha)
      description='%s (Version %s)' % (software_name, software_sha)
      publication_details = self.figshare.create_article(title=title, description=description, defined_type="code", status="Drafts")
      print "Code repository created with ID: %d and DOI: %s" % (publication_details["article_id"], publication_details["doi"])

      print "Uploading software to Figshare..."
      self.figshare.add_file(article_id=publication_details["article_id"], file_path=file_name)
      self.verify_upload(article_id=publication_details["article_id"], files=[file_name])

      print "Adding the SHA-1 hash as a tag..."
      self.figshare.add_tag(article_id=publication_details["article_id"], tag_name=software_sha)
      print "Tag added."

      if(category_id is not None):
         print "Adding category..."
         self.figshare.add_category(article_id=publication_details["article_id"], category_id=category_id)
         print "Category added."

      print "Adding all authors (with Figshare IDs) to the code..."
      author_ids = self.get_authors_list(software_local_repo_location)
      print "List of author IDs: ", author_ids
      if(author_ids is not None):
         for author_id in author_ids:
            self.figshare.add_author(publication_details["article_id"], author_id)
      print "All authors (with Figshare IDs) added."

      # If we are not keeping the code private, then make it public.
      if(not private):
         print "Making the code public..."
         self.figshare.make_public(article_id=publication_details["article_id"])
         print "The code has been made public."

      return publication_details
      
   def publish_data(self, parameters, article_id=None, private=False):
      """ Create a new dataset on the Figshare server. 
      Returns a dictionary of details about the new dataset once created. """
         
      print "Publishing data..."      
      if(article_id is None):
         if(self.service == "figshare"):
            print "Creating dataset on Figshare for data..."
            # NOTE: The defined_type needs to be a 'fileset' to allow multiple files to be uploaded separately.
            publication_details = self.figshare.create_article(title=parameters["title"], description=parameters["description"], defined_type="fileset", status="Drafts")
            print "Dataset created with ID: %d and DOI: %s" % (publication_details["article_id"], publication_details["doi"])

            article_id = publication_details["article_id"]
         elif(self.service == "zenodo"):
            raise NotImplementedError # FIXME: Remove this line once the Zenodo interface is ready.
            print "Creating dataset on Zenodo for data..."
            publication_details = self.zenodo.create_deposition(title=parameters["title"], description=parameters["description"], upload_type="dataset", state="inprogress")
            print "Dataset created with DOI: %s" % publication_details["doi"]

            article_id = publication_details["id"]

         # This is a new article, so upload ALL the files!
         modified_files = parameters["files"]
         existing_files = []
      else:
         publication_details = None
         # This is an existing publication, so check whether any files have been modified since they were last published.
         modified_files = self.find_modified(parameters["files"])
         existing_files = self.figshare.get_file_details(article_id)["files"]

      print "The following files have been marked for uploading: ", modified_files
      uploaded_files = []
      for f in modified_files:
         # Check whether the file actually exists locally.
         if(os.path.exists(f)):
            print "Uploading %s..." % f
            # Check whether the file already exists on the server. If so, over-write the version on the server.
            exists = False
            for e in existing_files:
               if(e["name"] == os.path.basename(f)):
                  print "File already exists on the server. Over-writing..."
                  exists = True
                  # FIXME: It is currently not possible to over-write an existing file via the Figshare API.
                  # We have to delete the file and then add it again.
                  self.figshare.delete_file(article_id=article_id, file_id=e["id"])
                  self.figshare.add_file(article_id=article_id, file_path=f)
                  break
            if(not exists):
               self.figshare.add_file(article_id=article_id, file_path=f)
            self.write_checksum(f)
            uploaded_files.append(f)
         else:
            print "File %s not present on the local system. Skipping..." % f
            continue

      self.verify_upload(article_id=article_id, files=uploaded_files)

      # Add category
      print "Adding category..."
      if(parameters["category_id"] is not None):
         self.figshare.add_category(article_id, parameters["category_id"])

      # Add tag(s)
      print "Adding tag(s)..."
      if(parameters["tag_name"] is not None):
         if(type(parameters["tag_name"]) == list):
            for tag_name in parameters["tag_name"]:
               self.figshare.add_tag(article_id, tag_name)
         else:
            self.figshare.add_tag(article_id, parameters["tag_name"])

      # If we are not keeping the data private, then make it public.
      if(not private):
         print "Making the data public..."
         self.figshare.make_public(article_id=article_id)
         print "The data has been made public."

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

   def find_software(self, software_name, sha):
      """ Checks if the software has already been published. If so, it returns the DOI.
      Otherwise it returns None. """
      
      keyword = "%s" % (software_name) # We always include the software's name in the title, so use it as the keyword
      
      if(self.service == "figshare"):
         results = self.figshare.search(keyword, tag=sha) # We always tag the software with the SHA-1 hash.

         if(len(results["items"]) != 0):
            print "Software %s has already been published (with SHA-1 %s).\n" % (software_name, sha)
            article_id = results["items"][-1]["article_id"]
            # Try to find the DOI as well.
            # This try-except block might not be necessary if we are always searching public articles.
            try:
               doi = results["items"][-1]["DOI"]
               print "Software DOI: %s" % doi
            except:
               print "DOI not found."
               doi = None
            return article_id, doi
         else:
            return None, None
      else:
         # TODO: Add in Zenodo searching.
         raise NotImplementedError

   def get_authors_list(self, local_repo_location):
      """ If an AUTHORS file exists in a given Git repository's base directory, then read it and
      match any Figshare author IDs using a regular expression. Return all author IDs in a single list. """
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

   def is_uploaded(self, article_id, files):
      """ Return True if the files in the list 'files' are all present on the server. Otherwise, return False. """
      files_on_server = self.figshare.get_file_details(article_id)["files"]
      for f in files:
         exists = False
         for s in files_on_server:
            if(s["name"] == os.path.basename(f)):
               exists = True
               break
         if(exists):
            continue
         else:
            print "Warning: Could not find file %s on the Figshare server.\n" % f
            return False
      return True

   def verify_upload(self, article_id, files):
      """ Verify that all files in the list 'files' have been uploaded. """
      if(self.is_uploaded(article_id=article_id, files=files)):
         print "All files successfully uploaded."
      else:
         print "Not all files were successfully uploaded. Perhaps you ran out of space on the server?\n"
         while True:
            response = raw_input("Are you sure you want to continue? (Y/N)\n")
            if(response == "y" or response == "Y"):
               break
            elif(response == "n" or response == "N"):
               # Clean up and exit
               self.figshare.delete_article(article_id) # NOTE: This should only delete draft code/filesets.
               sys.exit(1)
            else:
               continue
      return

   def article_exists(self, article_id):
      results = self.figshare.get_article_details(article_id)
      if("error" in results.keys()):
         return False
      else:
         return True

class TestLog(unittest.TestCase):
   """ Unit test suite for PyRDM's Publisher module. """

   def setUp(self):
      self.publisher = Publisher(service="figshare")
      
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

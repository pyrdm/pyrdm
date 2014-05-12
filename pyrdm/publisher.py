#!/usr/bin/env python

#    Copyright (C) 2014 Alexandros Avdis, Christian T. Jacobs, Gerard J. Gorman, Matthew D. Piggott.

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
import zipfile

import git
import hashlib # For MD5 checksums

from pyrdm.figshare import Figshare

class Publisher:
   """ A Python module for publishing scientific software and data on Figshare. """

   def __init__(self):
      # Read in the authentication tokens, etc from the configuration file.
      self.config = self._load_config("pyrdm.config")
      self.figshare = Figshare(client_key = self.config["client_key"], client_secret = self.config["client_secret"],
                     resource_owner_key = self.config["resource_owner_key"], resource_owner_secret = self.config["resource_owner_secret"])
      return
      
   def _load_config(self, config_file_path):
      """ Load the configuration file containing the OAuth keys and information about the software name, etc
      into a dictionary called 'config' and return it. """
      f = open(config_file_path, "r")

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
      results = self.figshare.search(keyword, tag=sha)

      if(results["count"] >= 1):
         print "Software %s has already been published (with SHA-1 %s)." % (software_name, sha)
         article_id = results["items"][-1]["article_id"]
         return article_id # TODO: Also return the DOI.
      else:
         return None
         
   def publish_software(self, software_name, sha):
      """ Publishes the software in the current repository to Figshare. """

      # Download the .zip file from GitHub...
      url = "%s/archive/%s.zip" % (self.config["github_location"], sha)
      #url = "https://github.com/ctjacobs/fluidity-test/archive/master.zip"
      
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
      self.figshare.add_tag(article_id=publication_details["article_id"], tag=sha)
      print "Tags added."

      print "Uploading software to Figshare..."
      self.figshare.upload_file(article_id=publication_details["article_id"], file_path=output_file_name)
      print "Software uploaded to Figshare."

      return publication_details
      
   def publish_data(self, parameters, article_id=None):
      """ Create a new dataset on the Figshare server. 
      Returns a dictionary of details about the new dataset once created. """

      # FIXME: Does Figshare prevent the creation of the same article (or dataset) twice? If not, we'll need to check for this here.
         
      print "Publishing data..."      
      if(article_id is None):
         print "Creating dataset on Figshare for data..."
         # NOTE: The defined_type needs to be a 'fileset' to allow multiple files to be uploaded separately.
         publication_details = self.figshare.create_article(title=parameters["title"], description=parameters["description"], defined_type="fileset", status="Drafts")
         print "Dataset created with DOI: %s" % publication_details["doi"]
         print publication_details

         article_id = publication_details["article_id"]
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

      #zip_file = zipfile.ZipFile("%s.zip" % parameters["title"], "w")
      #   zip_file.write(f)
      #zip_file.close()
      #self.figshare.upload_file(article_id=article_id, file_path='%s.zip' % parameters["title"])

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
      

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

import requests
from requests_oauthlib import OAuth1
import json

import ConfigParser
import sys, os
import zipfile
from urllib2 import urlopen
from urllib import urlencode

import git
import hashlib # For MD5 checksums

class Publisher:
   """ A Python module for publishing scientific software and data to Figshare.
   The functions which use the Figshare API might be moved to a separate module in the future. """

   def __init__(self):
      # Read in the authentication tokens, etc from the configuration file.
      self.config = self._load_config("pyrdm.config")
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
      
   def _create_session(self):
      """ Authenticates with the Figshare server, and creates a session object used to send requests to the server. """
      oauth = OAuth1(client_key = self.config["client_key"], client_secret = self.config["client_secret"],
                     resource_owner_key = self.config["resource_owner_key"], resource_owner_secret = self.config["resource_owner_secret"],
                     signature_type = 'auth_header')

      client = requests.session() 

      return oauth, client

   def find_software(self, software_name, sha):
      """ Checks if the software has already been published. If so, it returns the DOI.
      Otherwise it returns None. """
      
      # Set up a new session.
      oauth, client = self._create_session()

      # FIXME: Only public articles can use the "has_tag" filter.
      #base_url = "http://api.figshare.com/v1/articles/search"
      base_url = "http://api.figshare.com/v1/my_data/articles"
      parameters = {"search_for":"%s-%s" % (software_name, sha), "has_tag":"%s" % sha}
      url = base_url + "?" + urlencode(parameters)

      response = client.get(url, auth=oauth)
      results = json.loads(response.content)
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
      
      # Set up a new session.
      oauth, client = self._create_session()

      # The data that will be sent via HTTP POST.
      body = {'title':'%s-%s' % (software_name, sha), 'description':'%s version %s' % (software_name, sha), 'defined_type':'code', "status": "Drafts"}
      headers = {'content-type':'application/json'}
      
      # FIXME: We should set the article's status to 'public' (by default, it is set to 'draft').
      print "Creating dataset on Figshare for software..."
      response = client.post('http://api.figshare.com/v1/my_data/articles', auth=oauth,
                              data=json.dumps(body), headers=headers)
      publication_details = json.loads(response.content)
      print "Dataset created with DOI: %s" % publication_details["doi"]
      
      print "Adding tags..."
      body = {'tag_name':'%s' % sha}
      response = client.put('http://api.figshare.com/v1/my_data/articles/%d/tags' % publication_details["article_id"], auth=oauth,
                             data=json.dumps(body), headers=headers)
      print "Tags added."

      print "Uploading software to Figshare..."
      files = {'filedata':(output_file_name, open(output_file_name, 'rb'))}
      response = client.put('http://api.figshare.com/v1/my_data/articles/%d/files' % publication_details["article_id"], auth=oauth,
                              files=files)
      print "Software uploaded to Figshare."

      return publication_details
      
   def publish_data(self, parameters, article_id=None):
      """ Create a new dataset on the Figshare server. 
      Returns a dictionary of details about the new dataset once created. """

      # FIXME: Does Figshare prevent the creation of the same article (or dataset) twice? If not, we'll need to check for this here.
         
      print "Publishing data..."
         
      # Set up a new session.
      oauth, client = self._create_session()
      
      if(article_id is None):
         print "Creating dataset on Figshare for data..."
         
         body = {'title':'%s' % parameters["title"], 'description':'%s' % parameters["description"], 'defined_type':'dataset', "status": "Drafts"}
         headers = {'content-type':'application/json'}
         
         response = client.post('http://api.figshare.com/v1/my_data/articles', auth=oauth,
                                 data=json.dumps(body), headers=headers)
         publication_details = json.loads(response.content)
         print "Dataset created with DOI: %s" % publication_details["doi"]
         article_id = publication_details["article_id"]
         print publication_details
      else:
         publication_details = None
         
      # Check whether any files have been modified.
      modified_files = self.find_modified(parameters["files"])
      print "The following files have been marked for uploading: ", modified_files



      # TODO: Don't upload a single .zip file - upload all the files, but only upload the ones that are modified.


      #file_list = []
      #for f in modified_files:
      #   print "Uploading file: %s" % f
      #   file_list.append(('%s' % f, open('%s' % f, 'rb')))
      #filedata = {'filedata':file_list}
      #response = client.put('http://api.figshare.com/v1/my_data/articles/%s/files' % article_id, auth=oauth,
      #                        files=filedata)



      zip_file = zipfile.ZipFile("%s.zip" % parameters["title"], "w")
      for f in modified_files:
         zip_file.write(f)
      zip_file.close()

      filedata = {'filedata':('%s.zip' % parameters["title"], open('%s.zip' % parameters["title"], 'rb'))}      
      response = client.put('http://api.figshare.com/v1/my_data/articles/%s/files' % article_id, auth=oauth,
                           files=filedata)
      

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
      

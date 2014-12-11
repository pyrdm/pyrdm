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

import logging
import sys, os
import unittest

import requests
import json

from urllib2 import urlopen
from urllib import urlencode

_LOG = logging.getLogger(__name__)

class Zenodo:
   """ A Python interface to Zenodo via the Zenodo API. """

   def __init__(self, access_token):
      # The Zenodo authentication tokens.
      self.access_token = access_token
      self.api_url = "https://zenodo.org/api/"

      _LOG.info("Testing Zenodo authentication...")
      try:
         url = self.api_url + "deposit/depositions"
         url = self._append_suffix(url)

         response = requests.get(url)
         _LOG.debug("Server returned response %d" % response.status_code)
         if(response.status_code != requests.codes.ok): # If the status is not "OK", then exit here.
            raise Exception("Could not authenticate with the Zenodo server.")
         else:
            _LOG.info("Authentication test successful.\n")
      except:
         _LOG.error("Could not authenticate with the Zenodo server. Check Internet connection? Check Zenodo authentication keys in ~/.config/pyrdm.ini ?")
         sys.exit(1)
      return

   def _append_suffix(self, url):
      return url + "?access_token=" + self.access_token

   # -------------------------------------------
   # Methods for depositions
   # -------------------------------------------
   def list_depositions(self):
      """ Lists all depositions on Zenodo (associated with the user's account). """

      url = self.api_url + "deposit/depositions"
      url = self._append_suffix(url)

      response = requests.get(url)
      results = json.loads(response.content)
      
      response.raise_for_status()
      
      return results

   def create_deposition(self, title, description, upload_type, creators, keywords, prereserve_doi):
      """ Creates a new deposition on Zenodo. Requires a title, description and upload_type (e.g. software, dataset). 
      Returns a dictionary of information about the created publication. """

      url = self.api_url + "deposit/depositions"
      url = self._append_suffix(url)

      headers = {"content-type": "application/json"}
      data = {"metadata": {"title": title, "description": description, "upload_type": upload_type, "creators": creators, "keywords": keywords, "prereserve_doi": prereserve_doi}}

      response = requests.post(url, data=json.dumps(data), headers=headers)
      results = json.loads(response.content)
      return results

   def retrieve_deposition(self, deposition_id):
      """ Returns details about a deposition with a given ID (deposition_id). """

      url = self.api_url + "deposit/depositions/%d" % deposition_id
      url = self._append_suffix(url)

      response = requests.get(url)
      results = json.loads(response.content)
      return results

   def update_deposition(self, deposition_id):
      """ Update the metadata of a deposition with a given ID (deposition_id). """

      url = self.api_url + "deposit/depositions/%d" % deposition_id
      url = self._append_suffix(url)

      headers = {"content-type": "application/json"}
      data = {"metadata": {"title": title, "description": description, "upload_type": upload_type, "state": state}}

      response = requests.put(url, data=json.dumps(data), headers=headers)
      results = json.loads(response.content)
      return results

   def delete_deposition(self, deposition_id):
      """ Delete a deposition with a given ID (deposition_id). """

      url = self.api_url + "deposit/depositions/%d" % deposition_id
      url = self._append_suffix(url)

      response = requests.delete(url)
      response.raise_for_status()
      return


   # -------------------------------------------
   # Methods for deposition files
   # -------------------------------------------
   def list_files(self, deposition_id):
      """ Lists all files in a given depositions on Zenodo. """

      url = self.api_url + "deposit/depositions/%d/files" % deposition_id
      url = self._append_suffix(url)

      response = requests.get(url)
      results = json.loads(response.content)
      return results

   def create_file(self, deposition_id, file_path):
      """ Creates a new deposition on Zenodo.  """

      url = self.api_url + "deposit/depositions/%d/files" % deposition_id
      url = self._append_suffix(url)

      headers = {"content-type": "multipart/form-data"}
      data = {'filename': os.path.basename(file_path)}
      files = {'file': open(file_path, 'rb')}

      response = requests.post(url, data=data, files=files)
      results = json.loads(response.content)
      return results

   def sort_files(self, deposition_id, file_ids):
      """ Sorts a list of files (with their file_ids in a list called 'file_ids') associated with a given deposition_id on Zenodo. """

      url = self.api_url + "deposit/depositions/%d/files" % deposition_id
      url = self._append_suffix(url)

      headers = {"content-type": "application/json"}
      data = []
      for file_id in file_ids:
         data.append({"id":file_id})

      response = requests.put(url, data=json.dumps(data), headers=headers)
      results = json.loads(response.content)
      return results

   def retrieve_file(self, deposition_id, file_id):
      """ Retrieve details about a file (with a given file_id) in a deposition (with a given deposition_id) on Zenodo. """

      url = self.api_url + "deposit/depositions/%d/files/%d" % (deposition_id, file_id)
      url = self._append_suffix(url)

      response = requests.get(url)
      results = json.loads(response.content)
      return results

   def update_file(self, deposition_id, file_id, new_file_name):
      """ Updates a file (with a given file_id) in a deposition (with a given deposition_id) on Zenodo. 
          Currently this is only used to rename an existing file on the Zenodo servers. """

      url = self.api_url + "deposit/depositions/%d/files/%d" % (deposition_id, file_id)
      url = self._append_suffix(url)

      headers = {"content-type": "application/json"}
      data = {"filename": new_file_name}

      response = requests.get(url, data=json.dumps(data), headers=headers)
      results = json.loads(response.content)
      return results

   def delete_file(self, deposition_id, file_id):
      """ Deletes a file (with a given file_id) in a deposition (with a given deposition_id) on Zenodo. """

      url = self.api_url + "deposit/depositions/%d/files/%d" % (deposition_id, file_id)
      url = self._append_suffix(url)

      response = requests.delete(url)
      results = json.loads(response.content)
      return results

   # -------------------------------------------
   # Methods for deposition actions
   # -------------------------------------------
   def publish_deposition(self, deposition_id):
      """ Publishes a deposition (with a given deposition_id) on Zenodo. """

      url = self.api_url + "deposit/depositions/%d/actions/publish" % deposition_id
      url = self._append_suffix(url)

      response = requests.post(url)
      results = json.loads(response.content)
      return results

   def edit_deposition(self, deposition_id):
      """ Opens up a deposition (with a given deposition_id) on Zenodo for editing. """

      url = self.api_url + "deposit/depositions/%d/actions/edit" % deposition_id
      url = self._append_suffix(url)

      response = requests.post(url)
      results = json.loads(response.content)
      return results

   def discard_deposition(self, deposition_id):
      """ Discards any changes (made in the current editing session) to a deposition (with a given deposition_id) on Zenodo. """

      url = self.api_url + "deposit/depositions/%d/actions/discard" % deposition_id
      url = self._append_suffix(url)

      response = requests.post(url)
      results = json.loads(response.content)
      return results


class TestLog(unittest.TestCase):
   """ Unit test suite for PyRDM's Zenodo module. """

   def setUp(self):
      # NOTE: This requires the user to have their Zenodo authentication details in the file "/home/<user_name>/.config/pyrdm.ini".
      from pyrdm.publisher import Publisher
      self.publisher = Publisher(service="zenodo")
      self.zenodo = Zenodo(access_token = self.publisher.config.get("zenodo", "access_token"))
      
      # Create a test article
      _LOG.info("Creating test article...")
      publication_details = self.zenodo.create_deposition(title="PyRDM Test", description="PyRDM Test Article", upload_type="software", creators=[{"name":"Test User", "affiliation":"Test Affiliation"}], keywords=["Test"], prereserve_doi=True)
      _LOG.debug(str(publication_details))
      assert(not ("errors" in publication_details.keys()))
      self.deposition_id = publication_details["id"]
      return

   def tearDown(self):
      _LOG.info("Deleting test article...")
      self.zenodo.delete_deposition(self.deposition_id)
      return

   def test_zenodo_create_file(self):
      _LOG.info("Creating test file...")
      
      f = open("test_file.txt", "w")
      f.write("This is a test file for PyRDM's Zenodo module unit tests")
      f.close()
      
      results = self.zenodo.create_file(self.deposition_id, "test_file.txt")
      _LOG.debug(str(results))
      assert(results["filename"] == "test_file.txt")
      return
 
if(__name__ == '__main__'):
   unittest.main()

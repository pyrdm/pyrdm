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

import requests
import json

from urllib2 import urlopen
from urllib import urlencode

class Zenodo:
   """ A Python interface to Zenodo via the Zenodo API. """

   def __init__(self, access_token):
      # The Zenodo authentication tokens.
      self.access_token = access_token
      self.api_url = "https://zenodo.org/api/"
      return

   def append_suffix(self, url):
      return url + "?access_token=" + self.access_token

   def create_deposition(self, title, description, upload_type, state="inprogress"):
      """ Creates a new 'deposition' on Zenodo. Requires a title, description and upload_type (e.g. software, dataset). 
      Returns a dictionary of information about the created publication. """

      url = self.api_url + "deposit/depositions"
      url = self.append_suffix(url)

      headers = {"content-type": "application/json"}
      data = {"metadata": {"title": title, "description": description, "upload_type": upload_type, "state": state}}

      response = requests.post(url, data=json.dumps(data), headers=headers)
      results = json.loads(response.content)
      return results

   def list_depositions(self):
      """ Lists all depositions on Zenodo (associated with the user's account). """

      url = self.api_url + "deposit/depositions"
      url = self.append_suffix(url)

      response = requests.get(url)
      results = json.loads(response.content)
      return results

   def retrieve_deposition(self, deposition_id):
      """ Returns data about a deposition with a given ID (deposition_id). """

      url = self.api_url + "deposit/depositions/%d" % deposition_id
      url = self.append_suffix(url)

      response = requests.get(url)
      results = json.loads(response.content)
      return results

   def update_deposition(self, deposition_id):
      """ Update the metadata of a deposition with a given ID (deposition_id). """

      url = self.api_url + "deposit/depositions/%d" % deposition_id
      url = self.append_suffix(url)

      headers = {"content-type": "application/json"}
      data = {"metadata": {"title": title, "description": description, "upload_type": upload_type, "state": state}}

      requests.put(url, data=json.dumps(data), headers=headers)
      results = json.loads(response.content)
      return results

   def delete_deposition(self, deposition_id):
      """ Delete a deposition with a given ID (deposition_id). """

      url = self.api_url + "deposit/depositions/%d" % deposition_id
      url = self.append_suffix(url)

      requests.delete(url)
      results = json.loads(response.content)
      return results


if(__name__ == '__main__'):
   unittest.main()

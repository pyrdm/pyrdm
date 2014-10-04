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

   def __init__(self, api_key):
      # The Zenodo authentication tokens.
      self.api_key = api_key
      return

   def create_deposition(self, title, description, upload_type, state="inprogress"):
      """ Creates a new 'deposition' on Zenodo. Requires a title, description and upload_type (e.g. software, dataset). 
      Returns a dictionary of information about the created article. """

      base_url = "https://zenodo.org/api/deposit/depositions"
      headers = {"content-type": "application/json"}
      data = {}
      _LOG.debug(self.api_key)
      url = base_url + "?apikey=" + self.api_key
      _LOG.debug(url)

      response = requests.get(url)
      results = json.loads(response.content)
      return results



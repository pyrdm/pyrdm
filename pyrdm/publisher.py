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

import git
import ConfigParser

import requests
from requests_oauthlib import OAuth1
import json

from pyrdm.figshare import Figshare

class Publisher:

   def __init__(self):
      # Read in the authentication tokens, etc from the configuration file.
      self.config = self.load_config("pyrdm.config")

      # Set up a Figshare object, in case we want to push data directly to Figshare
      # (rather than via Fidgit).
      self.figshare = Figshare(self.config)

      return

   def load_config(self, config_file_path):
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



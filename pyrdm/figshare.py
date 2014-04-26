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

class Figshare:
   """ An implementation of the Figshare API in Python. """

   def __init__(self, config):
      self.config = config
      return

   def _create_session(self):
      """ Authenticates with the Figshare server, and creates a session object used to send requests to the server. """
      oauth = OAuth1(client_key = self.config["client_key"], client_secret = self.config["client_secret"],
                     resource_owner_key = self.config["resource_owner_key"], resource_owner_secret = self.config["resource_owner_secret"],
                     signature_type = 'auth_header')

      client = requests.session() 

      return oauth, client

   def create_article(self, parameters):
      """ Create a new article (or dataset) on the Figshare server. 
      Returns a dictionary of details about the new article once created. """

      # FIXME: Does Figshare prevent the creation of the same article (or dataset) twice? If not, we'll need to check for this here.

      # Set up a new session.
      oauth, client = self._create_session()

      # The data that will be sent via HTTP POST.
      body = parameters
      headers = {'content-type':'application/json'}
      
      # FIXME: We should set the article's status to 'public' (by default, it is set to 'draft').
      response = client.post('http://api.figshare.com/v1/my_data/articles', auth=oauth,
                              data=json.dumps(body), headers=headers)
      publication_details = json.loads(response.content)
      return publication_details


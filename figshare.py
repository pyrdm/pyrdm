#!/usr/bin/env python

# Copyright (C) 2014 Alexandros Avdis, Gerard J. Gorman, Christian T. Jacobs, Matthew D. Piggott.

import requests
from oauth_hook import OAuthHook
import json

class Figshare:
   """ An implementation of the Figshare API in Python. """

   def __init__(self, config):
      self.config = config
      return

   def _create_session(self):
      """ Authenticates with the Figshare server, and creates a session object used to send requests to the server. """
      oauth = OAuthHook(client_key = self.config["client_key"], client_secret = self.config["client_secret"],
                        resource_owner_key = self.config["token_key"], resource_owner_secret = self.config["token_secret"],
                        signature_type = 'auth_header')

      client = requests.session()

      return oauth, client

   def create_article(self, parameters):
      """ Create a new article (or dataset) on the Figshare server. 
      Returns a dictionary of details about the new article once created. """

      # FIXME: Does Figshare prevent the creation of the same article twice? If not, we'll need to check for this here.

      # Set up a new session.
      oauth, client = self._create_session()

      body = parameters #{'title':'Test dataset', 'description':'Test description','defined_type':'dataset'}
      headers = {'content-type':'application/json'}

      response = client.post('http://api.figshare.com/v1/my_data/articles', auth=oauth,
                              data=json.dumps(body), headers=headers)

      result = json.loads(response.content)
      return result

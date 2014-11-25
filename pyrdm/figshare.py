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
from requests_oauthlib import OAuth1
import json

from urllib import urlencode

_LOG = logging.getLogger(__name__)

class Figshare:
   """ A Python interface to Figshare via the Figshare API. """

   def __init__(self, client_key, client_secret, resource_owner_key, resource_owner_secret):
      # The Figshare authentication tokens.
      self.client_key = client_key
      self.client_secret = client_secret
      self.resource_owner_key = resource_owner_key
      self.resource_owner_secret = resource_owner_secret

      # Set up a new session.
      self.oauth, self.client = self.create_session()

      # Before doing any creating/uploading on Figshare, try something simple like listing the user's articles
      # to check that the authentication is successful.
      _LOG.info("Testing Figshare authentication...")
      try:
         response = self.client.get('http://api.figshare.com/v1/my_data/articles', auth=self.oauth)
         _LOG.debug("Server returned response %d" % response.status_code)
         if(response.status_code != requests.codes.ok): # If the status is not "OK", then exit here.
            raise Exception("Could not authenticate with the Figshare server.")
         else:
            _LOG.info("Authentication test successful.\n")
      except:
         _LOG.error("Could not authenticate with the Figshare server. Check Internet connection? Check Figshare authentication keys in ~/.config/pyrdm.ini ?")
         sys.exit(1)

      return

   def create_session(self):
      """ Authenticates with the Figshare server, and creates a session object used to send requests to the server. """
      oauth = OAuth1(client_key = self.client_key, client_secret = self.client_secret,
                     resource_owner_key = self.resource_owner_key, resource_owner_secret = self.resource_owner_secret,
                     signature_type = 'auth_header')

      client = requests.session()
      return oauth, client

   def create_article(self, title, description, defined_type, status="Drafts"):
      """ Creates a new article on Figshare. Requires a title, description and defined_type. 
      Returns a dictionary of information about the created article. """
      # The data that will be sent via HTTP POST.
      body = {'title':title, 'description':description, 'defined_type':defined_type, "status":status}
      headers = {'content-type':'application/json'}
      response = self.client.post('http://api.figshare.com/v1/my_data/articles', auth=self.oauth,
                              data=json.dumps(body), headers=headers)
      response.raise_for_status()
      
      results = json.loads(response.content)
      return results

   def update_article(self, article_id, title=None, description=None, defined_type=None):
      """ Updates an article with a given article_id. """
      body = {}

      # The possible fields to update
      if(title is not None):
         body['title'] = title
      if(description is not None):
         body['description'] = description
      if(defined_type is not None):
         body['defined_type'] = defined_type

      headers = {'content-type':'application/json'}
      response = self.client.put('http://api.figshare.com/v1/my_data/articles/%s' % str(article_id), auth=self.oauth,
                              data=json.dumps(body), headers=headers)
      results = json.loads(response.content)
      return results

   def delete_article(self, article_id):
      """ Delete a private or draft article with a given article_id. """
      response = self.client.delete('http://api.figshare.com/v1/my_data/articles/%s' % str(article_id), auth=self.oauth)
      results = json.loads(response.content)
      return results

   def search(self, keyword, search_private=False, from_date=None, to_date=None, author=None, title=None, category=None, tag=None, page=None):
      """ Searches public and private articles using a keyword. """

      if(search_private):
         base_url = "http://api.figshare.com/v1/my_data/articles"
      else:
         base_url = "http://api.figshare.com/v1/articles/search"

      parameters = {"search_for":"%s" % keyword}

      # Optional filters
      # NOTE: Only public articles can use the optional filters.
      if(from_date is not None):
         parameters["from_date"] = from_date
      if(to_date is not None):
         parameters["to_date"] = to_date
      if(author is not None):
         parameters["has_author"] = author
      if(title is not None):
         parameters["has_title"] = title
      if(category is not None):
         parameters["has_category"] = category
      if(tag is not None):
         parameters["has_tag"] = tag
      if(page is not None):
         parameters["page"] = page

      url = base_url + "?" + urlencode(parameters)

      response = self.client.get(url, auth=self.oauth)
      results = json.loads(response.content)
      return results

   def add_category(self, article_id, category):
      """ For an article with a given article_id, add a category. Note that this is a string, not the integer ID of the category. """

      category_id = self.get_category_id(category)
      if(category_id is None):
         _LOG.warning("Could not find the category '%s'! No category was added. The publication cannot be made public until a category is added." % category)
         return None
      else:
         body = {'category_id':category_id}
         headers = {'content-type':'application/json'}
         response = self.client.put('http://api.figshare.com/v1/my_data/articles/%s/categories' % str(article_id), auth=self.oauth,
                                 data=json.dumps(body), headers=headers)
         results = json.loads(response.content)
         return results

   def get_category_id(self, category):
      """ Return the integer ID of a given category. If not found, return None. """
      categories_list = self.get_categories()["items"]
      category_id = None
      for c in categories_list:
         if(c["name"] == category):
            category_id = c["id"]
            break
      return category_id

   def get_categories(self):
      """ Get the full list of available categories. No authentication is required. """
      headers = {'content-type':'application/json'}
      response = self.client.get('http://api.figshare.com/v1/categories',
                              headers=headers)
      results = json.loads(response.content)
      return results

   def add_tag(self, article_id, tag_name):
      """ For an article with a given article_id, add a tag with a given tag_name. """
      body = {'tag_name':tag_name}
      headers = {'content-type':'application/json'}
      response = self.client.put('http://api.figshare.com/v1/my_data/articles/%s/tags' % str(article_id), auth=self.oauth,
                                 data=json.dumps(body), headers=headers)
      results = json.loads(response.content)
      return results

   def add_link(self, article_id, link):
      """ For an article with a given article_id, add a link. """
      body = {'link':link}
      headers = {'content-type':'application/json'}
      response = self.client.put('http://api.figshare.com/v1/my_data/articles/%s/links' % str(article_id), auth=self.oauth,
                              data=json.dumps(body), headers=headers)
      results = json.loads(response.content)
      return results

   def search_author(self, full_name):
      """ Search for all authors associated with this account. """
      response = self.client.get('http://api.figshare.com/v1/my_data/authors?search_for=%s' % full_name, auth=self.oauth)
      results = json.loads(response.content)
      return results

   def create_author(self, full_name):
      """ Create a new author and associate them with this account. """
      body = {'full_name':full_name}
      headers = {'content-type':'application/json'}
      response = self.client.post('http://api.figshare.com/v1/my_data/authors', auth=self.oauth,
                                 data=json.dumps(body), headers=headers)
      results = json.loads(response.content)
      return results

   def add_author(self, article_id, author_id):
      """ Create a new author and associate them with this account. """
      body = {'author_id':author_id}
      headers = {'content-type':'application/json'}
      response = self.client.put('http://api.figshare.com/v1/my_data/articles/%s/authors' % str(article_id), auth=self.oauth,
                                 data=json.dumps(body), headers=headers)
      results = json.loads(response.content)
      return results

   def add_file(self, article_id, file_path):
      """ Upload a file with path 'file_path' to an article with a given article_id. """
      files = {'filedata':(os.path.basename(file_path), open(file_path, 'rb'))}
      response = self.client.put('http://api.figshare.com/v1/my_data/articles/%s/files' % str(article_id), auth=self.oauth,
                                 files=files)
      results = json.loads(response.content)
      return results

   def delete_file(self, article_id, file_id):
      response = self.client.delete('http://api.figshare.com/v1/my_data/articles/%s/files/%s' % (str(article_id), str(file_id)), auth=self.oauth)
      results = json.loads(response.content)
      return results

   def get_file_details(self, article_id):
      response = self.client.get('http://api.figshare.com/v1/my_data/articles/%s/files' % str(article_id), auth=self.oauth)
      results = json.loads(response.content)
      return results

   def get_article_details(self, article_id):
      """ Returns a dictionary containing details of an article with ID 'article_id'. """
      response = self.client.get('http://api.figshare.com/v1/my_data/articles/%s' % str(article_id), auth=self.oauth)
      results = json.loads(response.content)
      return results

   def get_article_versions(self, article_id):
      response = self.client.get('http://api.figshare.com/v1/my_data/articles/%s/versions' % str(article_id), auth=self.oauth)
      results = json.loads(response.content)
      return results

   def get_article_version_details(self, article_id, version_id):
      response = self.client.get('http://api.figshare.com/v1/my_data/articles/%s/versions/%s' % (str(article_id), str(version_id)), auth=self.oauth)
      results = json.loads(response.content)
      return results

   def make_public(self, article_id):
      response = self.client.post('http://api.figshare.com/v1/my_data/articles/%s/action/make_public' % str(article_id), auth=self.oauth)
      results = json.loads(response.content)
      return results
   
   def make_private(self, article_id):
      response = self.client.post('http://api.figshare.com/v1/my_data/articles/%s/action/make_private' % str(article_id), auth=self.oauth)
      results = json.loads(response.content)
      return results


class TestLog(unittest.TestCase):
   """ Unit test suite for PyRDM's Figshare module. """

   def setUp(self):
      # NOTE: This requires the user to have their Figshare authentication details in the file "/home/<user_name>/.config/pyrdm.ini".
      from pyrdm.publisher import Publisher
      self.publisher = Publisher(service="figshare")
      self.figshare = Figshare(client_key = self.publisher.config.get("figshare", "client_key"), client_secret = self.publisher.config.get("figshare", "client_secret"),
                        resource_owner_key = self.publisher.config.get("figshare", "resource_owner_key"), resource_owner_secret = self.publisher.config.get("figshare", "resource_owner_secret"))
                     
      # Create a test article
      _LOG.info("Creating test article...")
      publication_details = self.figshare.create_article(title="PyRDM Test", description="PyRDM Test Article", defined_type="code", status="Drafts")
      _LOG.debug(str(publication_details))
      assert(not ("error" in publication_details.keys()))
      self.article_id = publication_details["article_id"]
      return

   def tearDown(self):
      _LOG.info("Deleting test article...")
      results = self.figshare.delete_article(self.article_id)
      _LOG.debug(str(results))
      assert("success" in results.keys())
      return

   def test_figshare_search(self):
      _LOG.info("Searching for test article...")
      results = self.figshare.search("PyRDM Test", search_private=True)
      _LOG.debug(str(results))
      assert (len(results) >= 1)
      return
 
   def test_figshare_add_file(self):
      _LOG.info("Adding file to test article...")
      f = open("test_file.txt", "w")
      f.write("This is a test file for PyRDM's Figshare module unit tests")
      f.close()
      
      results = self.figshare.add_file(self.article_id, "test_file.txt")
      _LOG.debug(str(results))
      assert(results["extension"] == "txt")
      assert(results["name"] == "test_file.txt")
      
      return

   def test_figshare_add_tag(self):
      _LOG.info("Adding tag to test article...")
      
      results = self.figshare.add_tag(self.article_id, "test_file_tag")
      _LOG.debug(str(results))
      assert("success" in results.keys())
      
      return

   def test_figshare_add_category(self):
      _LOG.info("Adding category 'Computer Software' to test article...")
      
      results = self.figshare.add_category(self.article_id, "Computer Software")
      _LOG.debug(str(results))
      assert("success" in results.keys())
      
      return

   def test_figshare_get_article_details(self):
      _LOG.info("Getting article details...")

      publication_details = self.figshare.get_article_details(self.article_id)
      _LOG.debug(str(publication_details))
      assert(len(publication_details["items"]) == 1)
      assert(publication_details["items"][0]["title"] == "PyRDM Test")
      assert(publication_details["items"][0]["description"] == "PyRDM Test Article")
      
      return
      
if(__name__ == '__main__'):
   unittest.main()

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
import hashlib

import requests
from restkit import Resource, request
import json

_LOG = logging.getLogger(__name__)
_HANDLER = logging.StreamHandler()
_LOG.addHandler(_HANDLER)
_HANDLER.setFormatter(logging.Formatter(
    '%(module)s %(levelname)s: %(message)s'))
del(_HANDLER)
_LOG.setLevel(logging.DEBUG)

class Figshare(Resource):
   """ A Python interface to Figshare via version 2 of the Figshare API. """

   def __init__(self, token):
   
      self.base_url = "https://api.figshare.com/v2"
      
      # The Figshare OAuth2 authentication token.
      self.token = token
      
      super(Figshare, self).__init__(self.base_url)

      # Before doing any creating/uploading on Figshare, try something simple like listing the user's articles
      # to check that the authentication is successful.
      _LOG.info("Testing Figshare authentication...")
      try:
         response = self.get('/account/articles', params_dict={"limit":1000}, headers=self.get_headers(token=self.token))
         _LOG.debug("Server returned response %d" % response.status_int)
         if(response.status_int != requests.codes.ok): # If the status is not "OK", then exit here.
            raise Exception("Could not authenticate with the Figshare server.")
         else:
            _LOG.info("Authentication test successful.\n")
      except Exception as e:
         _LOG.error("Could not authenticate with the Figshare server. Check Internet connection? Check Figshare authentication keys in ~/.config/pyrdm.ini ?")
         sys.exit(1)

      return

   def get_headers(self, token=None):
      """ HTTP header information. """
      
      headers = {'Content-Type': 'application/json'}
      if token:
         headers['Authorization'] = 'token %s' % (token)
      return headers

   def create_article(self, title, description, defined_type, tags, categories):
      """ Creates a new article on Figshare. Requires a title, description, tags, defined_type, and category/categories. 
      Returns a dictionary of information about the created article. """
      
      if isinstance(categories, int):
         categories = [categories]
      
      # The data that will be sent via HTTP POST.
      body = {'title':title, 'description':description, 'defined_type':defined_type, "categories":categories, "tags":tags}
      headers = {'content-type':'application/json'}
      response = self.post("/account/articles", payload=json.dumps(body), headers=self.get_headers(token=self.token))
      
      results = json.loads(response.body_string())
      return results

   def update_article(self, article_id, title=None, description=None, defined_type=None, tags=None, categories=None):
      """ Updates an article with a given article_id. """
      body = {}

      # The possible fields to update
      if(title is not None):
         body['title'] = title
      if(description is not None):
         body['description'] = description
      if(defined_type is not None):
         body['defined_type'] = defined_type
      if(tags is not None):
         body['tags'] = tags
      if(categories is not None):
         body['categories'] = categories

      response = self.put('/account/articles/%s' % str(article_id), payload=json.dumps(body), headers=self.get_headers(token=self.token))
      results = json.loads(response.content)
      return results

   def delete_article(self, article_id):
      """ Delete a private or draft article with a given article_id. """
      try:
         response = self.delete('/account/articles/%s' % str(article_id), headers=self.get_headers(token=self.token))
         return {"success": True}
      except Exception as e:
         _LOG.exception(e)
         return {"success": False}

   def get_article_details(self, article_id, private=False):
      """ Return the details of an article with a given article ID. """
      
      if private:
         url = '/account/articles/%s' % str(article_id)
      else:
         url = '/articles/%s' % str(article_id)
         
      response = self.get(url, headers=self.get_headers(token=self.token))
      result = json.loads(response.body_string())
      return result
      
   def search(self, keyword, private=False, institution=None, group=None, published_since=None, modified_since=None):
      """ Searches public and private articles using a keyword. """

      if private:
         url = "/account/articles/search"
      else:
         url = "/articles/search"

      parameters = {"search_for":"%s" % keyword}

      # Optional filters
      if institution:
         parameters["institution"] = institution
      if group:
         parameters["group"] = group
      if published_since:
         parameters["published_since"] = published_since
      if modified_since:
         parameters["modified_since"] = modified_since
      
      response = self.post(url, payload=json.dumps(parameters), headers=self.get_headers(token=self.token))
      results = json.loads(response.body_string())
      return results

   def add_category(self, article_id, category):
      """ For an article with a given article_id, add a category. Note that this is a string, not the integer ID of the category. """

      category_id = self.get_category_id(category)
      if(category_id is None):
         _LOG.warning("Could not find the category '%s'! No category was added. The publication cannot be made public until a category is added." % category)
         return None
      else:
         body = {'categories':category_id}
         response = self.post('/account/articles/%s/categories' % str(article_id), payload=json.dumps(body), headers=self.get_headers(token=self.token))
         return json.loads(response.body_string())

   def get_category_id(self, category):
      """ Return the integer ID of a given category. If not found, return None. """
      categories_list = self.get_categories()
      category_id = None
      for c in categories_list:
         if(c["title"] == category):
            category_id = c["id"]
            break
      return category_id

   def get_categories(self):
      """ Get the full list of available categories. No authentication is required. """
      
      headers = {'content-type':'application/json'}
      response = self.get('/categories', headers=self.get_headers())
      results = json.loads(response.body_string())
      return results

   def add_authors(self, article_id, author_ids):
      """ Associate author(s) with this article. """
      
      # We require author_ids to be a list
      if isinstance(author_ids, int):
         author_ids = [{'id':author_ids}]
         
      payload = json.dumps({'authors':author_ids})
      response = self.put('/account/articles/%s/authors' % str(article_id), payload=payload, headers=self.get_headers(token=self.token))
      return response
    
   def add_file(self, article_id, file_path):
      """ Upload a file with path 'file_path' to an article with a given article_id.
      Based on the example from the Figshare API documentation: https://docs.figshare.com/api/upload_example/"""
      
      file_name = os.path.basename(file_path)
      
      # Get file info
      file_info = {}
      hash = hashlib.md5()
      with open(file_path, "rb") as f:
         for chunk in iter(lambda: f.read(4096), b""):
             hash.update(chunk)
      file_info['md5'] = hash.hexdigest()
      file_info['name'] = file_name
      file_info['size'] = os.path.getsize(file_path)

      # Create file object
      payload = json.dumps(file_info)
      response = self.post('/account/articles/{}/files'.format(article_id), headers=self.get_headers(token=self.token), payload=payload)
      result = json.loads(response.body_string())
      file_location = result["location"]
      
      # Get the file upload URL
      response = request(result["location"], headers=self.get_headers(token=self.token))
      upload_url = json.loads(response.body_string())["upload_url"]
      
      # Upload the file
      response = request(upload_url, headers=self.get_headers(token=self.token))
      result = json.loads(response.body_string())
      parts = result["parts"]

      with open(file_path, 'rb') as file_input:
         for part in parts:
             size = part['endOffset'] - part['startOffset'] + 1
             response = request('{0}/{1}'.format(upload_url, part["partNo"]), method='PUT', body=file_input.read(size))

      response = request(file_location, method='POST', headers=self.get_headers(token=self.token))
      return file_location
        
   def delete_file(self, article_id, file_id):
      """ Delete a file associated with a given article. """
      response = self.delete('/articles/%s/files/%s' % (str(article_id), str(file_id)), headers=self.get_headers(token=self.token))
      results = json.loads(response.body_string())
      return results

   def get_file_details(self, article_id, file_id):
      """ Get the details about a file associated with a given article. """
      response = self.get('/account/articles/%s/files/%s' % (str(article_id), str(file_id)), headers=self.get_headers(token=self.token))
      result = json.loads(response.body_string())
      return result

   def reserve_doi(self, article_id):
      """ Reserve a DOI for the article. """
      response = self.post('/account/articles/%s/reserve_doi' % str(article_id), headers=self.get_headers(token=self.token))
      result = json.loads(response.body_string())["doi"]
      return result

   def publish(self, article_id):
      """ Publish the article and make it public. """
      response = self.post('/account/articles/%s/publish' % str(article_id), headers=self.get_headers(token=self.token))
      result = json.loads(response.body_string())
      return result


class TestLog(unittest.TestCase):
   """ Unit test suite for PyRDM's Figshare module. """

   def setUp(self):
      # NOTE: This requires the user to have their Figshare authentication details in the file "/home/<user_name>/.config/pyrdm.ini".
      from pyrdm.publisher import Publisher
      self.publisher = Publisher(service="figshare")
      self.figshare = Figshare(token = self.publisher.config.get("figshare", "token"))
                     
      # Create a test article
      _LOG.info("Creating test article...")
      publication_details = self.figshare.create_article(title="PyRDM Test", description="PyRDM Test Article", tags=["test", "article"], defined_type="code", categories=2)
      _LOG.debug(str(publication_details))
      assert(not ("error" in publication_details.keys()))
      self.article_id = publication_details["location"].split("/")[-1]
      return

   def tearDown(self):
      _LOG.info("Deleting test article...")
      results = self.figshare.delete_article(self.article_id)
      _LOG.debug(str(results))
      assert("success" in results.keys())
      return

   def test_figshare_search(self):
      _LOG.info("Searching for test article...")
      results = self.figshare.search("PyRDM Test", private=True)
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
      
   def test_figshare_add_category(self):
      _LOG.info("Adding category 'Computer Software' to test article...")
      
      results = self.figshare.add_category(self.article_id, "Computer Software")
      _LOG.debug(str(results))
      assert("success" in results.keys())
      
      return

   def test_figshare_get_article_details(self):
      _LOG.info("Getting article details...")

      publication_details = self.figshare.get_article_details(self.article_id, private=True)
      _LOG.debug(str(publication_details))
      assert(publication_details["title"] == "PyRDM Test")
      assert(publication_details["description"] == "PyRDM Test Article")
      
      return
      
if(__name__ == '__main__'):
   unittest.main()

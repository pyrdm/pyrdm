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
from requests_oauthlib import OAuth1
import json

from urllib2 import urlopen
from urllib import urlencode

class Figshare:
   """ A Python interface to Figshare via the Figshare API. """

   def __init__(self, client_key, client_secret, resource_owner_key, resource_owner_secret):
      # The Figshare authentication tokens.
      self.client_key = client_key
      self.client_secret = client_secret
      self.resource_owner_key = resource_owner_key
      self.resource_owner_secret = resource_owner_secret

      # Set up a new session.
      self.oauth, self.client = self._create_session()
      return

   def _create_session(self):
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

   def search(self, keyword, search_private=True, from_date=None, to_date=None, author=None, title=None, category=None, tag=None, page=None):
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

   def add_category(self, article_id, category_id):
      """ For an article with a given article_id, add a category with a given category_id. """
      body = {'category_id':category_id}
      headers = {'content-type':'application/json'}
      response = self.client.put('http://api.figshare.com/v1/my_data/articles/%s/categories' % str(article_id), auth=self.oauth,
                              data=json.dumps(body), headers=headers)
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
      self.figshare = Figshare()
      return

   def tearDown(self):
      return

   def test_md5_write_checksum(self):
      self.publisher.write_checksum("test_file.txt")
      
      f = open("test_file.txt.md5", "r")
      md5_known = "29586140472f40eec4031eb2e0d352e1"
      md5 = hashlib.md5(open("test_file.txt").read()).hexdigest()
      print "Known MD5 hash of file: %s" % md5_known
      print "Computed MD5 hash of file: %s" % md5
      assert(md5 == md5_known)
      
   def test_md5_find_modified(self):
      self.publisher.write_checksum("test_file.txt")
      
      modified = self.publisher.find_modified(["test_file.txt"])
      print "Modified files: ", modified
      assert(modified == [])
      
      # Modify the file.      
      f = open("test_file.txt", "a")
      f.write("This is another line.")
      f.close()
      
      # Check that the MD5 checksums are not the same
      md5_before = "29586140472f40eec4031eb2e0d352e1"
      md5_after = hashlib.md5(open("test_file.txt").read()).hexdigest()
      print "MD5 hash before modification: %s" % md5_before
      print "MD5 hash after modification: %s" % md5_after
      assert(md5_before != md5_after)
      
      modified = self.publisher.find_modified(["test_file.txt"])
      print "Modified files: ", modified
      assert(modified == ["test_file.txt"])
      
if(__name__ == '__main__'):
   unittest.main()

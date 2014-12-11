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
import sword2
import os.path

_LOG = logging.getLogger(__name__)

class DSpace:
   """ A publishing interface to DSpace using the SWORD2 protocol. """
   
   def __init__(self, service_document_url, user_name, user_pass):
      """ Initialise a new DSpace object. This begins by setting up a connection to the DSpace server
      using the credentials provided by the user in the 'user_name' and 'user_pass' arguments. """
   
      # Set up a connection to the DSpace server.
      self.connection = sword2.Connection(service_document_url, user_name, user_pass)
      
      # Get the Service Document.
      self.connection.get_service_document()
      _LOG.debug("Service document: %s" % self.connection.sd)
      
      # Check that the Service Document has been parsed successfully, and that it is a valid document.
      assert self.connection.sd != None
      assert self.connection.sd.parsed
      assert self.connection.sd.valid
      
      # Retrieve the list of available workspaces.
      self.workspaces = self.connection.workspaces
      _LOG.debug("Workspaces: %s" % (self.workspaces,))
      
      return
    
   def get_history(self):
      """ Return a full history of all transactions made with the DSpace server. """
      return self.connection.history
      
   def get_collection_by_title(self, title, workspace_id = 0):
      """ Locate and return the Collection object with a given title. 
      Return None if the collection cannot be found. """
      collections = self.workspaces[workspace_id][1]
      for i in range(len(collections)):
         if(collections[i].title == title):
            return collections[i]
      return None

   def get_collection_by_index(self, index, workspace_id = 0):
      """ Locate and return the Collection object with a given index. 
      Return None if the collection cannot be found. """
      collections = self.workspaces[workspace_id][1]
      try:
         collection = collections[index]
      except IndexError:
         collection = None
      return collection
      
   def create_deposit_from_file(self, collection, file_path, in_progress=True):
      """ Create a deposit in a specified collection by uploading a file with a given path.
      Return a Receipt object for this transaction. """
      with open(file_path, "rb") as data:
         receipt = self.connection.create(col_iri = collection.href,
                           payload = data,
                           filename = os.path.basename(file_path),
                           in_progress=in_progress)
         return receipt
  
   def create_deposit_from_metadata(self, collection, in_progress=True, **metadata_kwargs):
      """ Create a deposit in a specified collection by providing metadata in **metadata_kwargs.
      Return a Receipt object for this transaction. """
      e = sword2.Entry()
      e.add_fields(**metadata_kwargs)
      receipt = self.connection.create(col_iri = collection.href, in_progress=in_progress, metadata_entry = e)
      return receipt
          
   def replace_deposit_file(self, file_path, receipt):
      """ Replace a deposit's file with another, located at 'path'.
      Return a Receipt object for this replacement action. """
      with open(file_path, "rb") as data:
         replace_receipt = self.connection.update(payload = data,
                           filename = os.path.basename(file_path),
                           dr = receipt,
                           in_progress=True)
         return replace_receipt
       
   def replace_deposit_metadata(self, receipt, **metadata_kwargs):
      """ Replace a deposit's metadata with that defined by **metadata_kwargs.
      Return a Receipt object for this replacement action. """
      e = sword2.Entry()
      e.add_fields(**metadata_kwargs)
      replace_receipt = self.connection.update(metadata_entry = e,
                                              dr = receipt,
                                              in_progress=True)
      return replace_receipt
      
   def append_file_to_deposit(self, file_path, receipt):
      """ Append a new file, located at 'file_path', to a given deposit. 
      Return a Receipt object for this action. """
      with open(file_path, "rb") as data:
         append_receipt = self.connection.append(payload = data,
                              filename = os.path.basename(file_path),
                              mimetype="application/zip",
                              packaging = "http://purl.org/net/sword/package/METSDSpaceSIP", 
                              dr = receipt, 
                              in_progress=True)
         return append_receipt
         
   def add_file(self, file_path, receipt):
      """ Add a file, located at 'file_path', to a given deposit. """
      with open(file_path, "rb") as data:
         r = self.connection.add_file_to_resource(payload = data, 
                                            filename = os.path.basename(file_path),
                                            edit_media_iri = receipt.edit_media,
                                            in_progress=True)
         return r                     
      
   def delete_deposit(self, receipt):
      """ Delete a deposit. Return a Receipt object for this action. """
      delete_receipt = self.connection.delete_container(dr = receipt)
      return delete_receipt
      
   def delete_content(self, receipt):
      """ Delete content in a given deposit. Return a Receipt object for this action. """
      delete_receipt = self.connection.delete_content_of_resource(dr = receipt)
      return delete_receipt
   
   def complete_deposit(self, receipt):
      """ 'Complete' a deposit. Return a Receipt object for this action. """
      receipt = self.connection.complete_deposit(dr = receipt)
      return receipt
      
   def list_files(self, media_edit_feed, user_name=None, user_pass=None):
      """ List all the files at a given repository address. """
      handlers=[]
      if(user_name is not None):
         import urllib2, urlparse
         import feedparser
         auth = urllib2.HTTPBasicAuthHandler()
         auth.add_password("DSpace", uri=media_edit_feed, user=user_name, passwd=user_pass)
         handlers.append(auth)
      feed = feedparser.parse(media_edit_feed, handlers=handlers)

      files = feed["entries"][0]["summary"]
      return files

if(__name__ == '__main__'):
   unittest.main()

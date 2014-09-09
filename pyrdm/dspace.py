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

import sword2
import os.path

class DSpace:
   """ A publishing interface to DSpace using the SWORD2 protocol. """
   
   def __init__(self, service_document_url, user_name, user_pass):
      """ Initialise a new DSpace object. This begins by setting up a connection to the DSpace server
      using the credentials provided by the user in the 'user_name' and 'user_pass' arguments. """
   
      # Set up a connection to the DSpace server.
      self.connection = sword2.Connection(service_document_url, user_name, user_pass)
      
      # Get the Service Document.
      self.connection.get_service_document()
      print self.connection.sd
      
      # Check that the Service Document has been parsed successfully, and that it is a valid document.
      assert self.connection.sd != None
      assert self.connection.sd.parsed
      assert self.connection.sd.valid
      
      # Retrieve the list of available workspaces.
      self.workspaces = self.connection.workspaces
      print self.workspaces
      
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
      
   def create_deposit_from_file(self, collection, path):
      """ Create a deposit in a specified collection by uploading a file with a given path.
      Return a Receipt object for this transaction. """
      with open(path, "rb") as data:
         receipt = self.connection.create(col_iri = collection.href,
                           payload = data,
                           filename = os.path.basename(path))
         return receipt
  
   def create_deposit_from_metadata(self, collection, **metadata_kwargs):
      """ Create a deposit in a specified collection by providing metadata in **metadata_kwargs.
      Return a Receipt object for this transaction. """
      e = sword2.Entry()
      e.add_fields(**metadata_kwargs)
      receipt = self.connection.create(col_iri = collection.href, metadata_entry = e)
      return receipt
          
   def replace_deposit_file(self, path, receipt):
      """ Replace a deposit's file with another, located at 'path'.
      Return a Receipt object for this replacement action. """
      with open(path, "rb") as data:
         replace_receipt = self.connection.update(payload = data,
                           filename = os.path.basename(path),
                           dr = receipt)
         return replace_receipt
       
   def replace_deposit_metadata(self, receipt, **metadata_kwargs):
      """ Replace a deposit's metadata with that defined by **metadata_kwargs.
      Return a Receipt object for this replacement action. """
      e = sword2.Entry()
      e.add_fields(**metadata_kwargs)
      replace_receipt = self.connection.update(metadata_entry = e,
                                              dr = receipt)
      return replace_receipt
      
   def append_file_to_deposit(self, path, receipt):
      """ Append a new file, located at 'path', to a given deposit. 
      Return a Receipt object for this action. """
      with open(path, "rb") as data:
         append_receipt = self.connection.append(payload = data,
                              filename = os.path.basename(path),
                              dr = receipt)
         return append_receipt
      
   def delete_deposit(self, receipt):
      """ Delete a deposit. Return a Receipt object for this action. """
      delete_receipt = self.connection.delete_container(dr = receipt)
      return delete_receipt
      
#url = "http://demo.dspace.org/swordv2/servicedocument"
#user_name = "dspacedemo+colladmin@gmail.com"
#user_pass = "dspace"

#ds = DSpace(url, user_name, user_pass)

#collection = ds.get_collection_by_title("Private Collection")
#print collection.href

#receipt = ds.create_deposit_from_file(collection, path="test.png")
#print receipt

#ds.replace_deposit_metadata(receipt, title="hello world", dcterms_identifier="test deposit")

#ds.append_file_to_deposit("test.txt", receipt)




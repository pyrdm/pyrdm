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
      self.connection = sword2.Connection(service_document_url, user_name, user_pass)
      self.connection.get_service_document()
      
      print self.connection.sd
      
      assert self.connection.sd != None
      assert self.connection.sd.parsed
      assert self.connection.sd.valid
      
      self.workspaces = self.connection.workspaces
      
      return
    
   def get_history(self):
      return self.connection.history
      
   def get_collection_by_title(self, title, workspace_id = 0):
      collections = self.workspaces[workspace_id][1]
      for i in range(len(collections)):
         if(collections[i].title == title):
            return collections[i]
      return None

   def get_collection_by_index(self, index, workspace_id = 0):
      collections = self.workspaces[workspace_id][1]
      try:
         collection = collections[index]
      except IndexError:
         collection = None
      return collection
      
   def create_deposit_from_file(self, path, collection):
      with open(path, "rb") as data:
         receipt = self.connection.create(col_iri = collection.href,
                           payload = data,
                           mimetype = "application/zip",
                           filename = os.path.basename(path),
                           packaging = "http://purl.org/net/sword/package/Binary")
         return receipt
  
   def create_deposit_from_metadata(self, metadata, collection):
      e = Entry()
      
      # Extract the kwargs from the metadata dictionary
      args = []
      for key, value in metadata:
         s = key + "=" + value
         exec(s)
         args.append(s)
      
      receipt = self.connection.create(col_iri = collection.href, metadata_entry = e)
      return receipt
          
   def replace_deposit_file(self, path, receipt):
      with open(path, "rb") as data:
         update_receipt = self.connection.update(payload = data,
                           mimetype = "application/zip",
                           filename = os.path.basename(path),
                           packaging = "http://purl.org/net/sword/package/Binary",
                           dr = receipt)
         assert update_receipt.code == 200
         return update_receipt
       
   def replace_deposit_metadata(self, title, receipt):
      e = Entry(title=title)
      update_receipt = self.connection.update(col_iri = collection.href, metadata_entry = e)
      assert update_receipt.code == 200
      return update_receipt
      
   def append_file_to_deposit(self, path, receipt):
      with open(path, "rb") as data:
         append_receipt = self.connection.append(payload = data,
                              mimetype = "application/zip",
                              filename = os.path.basename(path),
                              packaging = "http://purl.org/net/sword/package/Binary",
                              dr = receipt)
         assert append_receipt.code == 201
         return append_receipt
      
   def delete_deposit(self, receipt):
      delete_receipt = self.connection.delete_container(dr = receipt)
      return delete_receipt
      
url = "http://demo.dspace.org/swordv2/servicedocument"
user_name = "dspacedemo+submit@gmail.com"
user_pass = "dspace"

ds = DSpace(url, user_name, user_pass)

collection = ds.get_collection_by_title("Collection of Sample Items")
print collection.href

receipt = ds.create_deposit_from_file("test.png", collection)
print receipt

ds.delete_deposit(receipt)



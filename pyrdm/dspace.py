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
      
   def get_collection_by_title(self, title):
      collections = self.workspaces[0][1] # FIXME: Consider the first workspace only, for now.
      for i in range(len(collections)):
         if(collections[i].title == title):
            return collections[i]
      return None

   def get_collection_by_index(self, index):
      collections = self.workspaces[0][1] # FIXME: Consider the first workspace only, for now.
      try:
         collection = collections[index]
      except IndexError:
         collection = None
      return collection
      
   def create_deposit(self, path, collection):
      with open(path, "rb") as data:
         receipt = self.connection.create(col_iri = collection.href,
                           payload = data,
                           mimetype = "application/zip",
                           filename = os.path.basename(path),
                           packaging = "http://purl.org/net/sword/package/Binary")
      return receipt
      
url = "http://demo.dspace.org/swordv2/servicedocument"
user_name = "dspacedemo+submit@gmail.com"
user_pass = "dspace"

ds = DSpace(url, user_name, user_pass)

collection = ds.get_collection_by_title("Collection of Sample Items")
receipt = ds.create_deposit("test.png", collection)
print receipt

print collection.href

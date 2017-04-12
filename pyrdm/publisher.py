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

import ConfigParser
import logging
import sys, os
import unittest
import re

import hashlib # For MD5 checksums
from urllib2 import urlopen

from pyrdm.figshare import Figshare
from pyrdm.zenodo import Zenodo
from pyrdm.dspace import DSpace
from pyrdm.git_handler import GitHandler

_LOG = logging.getLogger(__name__)

class Publisher:
   """ A Python module for publishing scientific software and data on Figshare or Zenodo. """

   def __init__(self, service):
      """ Load the PyRDM configuration file and set up the interface object for the desired publishing service. """
      
      self.service = service
   
      # Read in the authentication tokens, etc from the configuration file.
      self.config = self.load_config(os.path.expanduser("~/.config/pyrdm.ini"))
      
      if(service == "figshare"):
         self.figshare = Figshare(token = self.config.get("figshare", "token"))
      elif(service == "zenodo"):
         self.zenodo = Zenodo(access_token = self.config.get("zenodo", "access_token"))
      elif(service == "dspace"):
         self.dspace = DSpace(service_document_url = self.config.get("dspace", "service_document_url"), user_name = self.config.get("dspace", "user_name"), user_pass = self.config.get("dspace", "user_pass"))
      else:
         _LOG.error("Unsupported service: %s" % service)
         sys.exit(1)

      return
      
   def load_config(self, config_file_path):
      """ Load the configuration file and return a dictionary containing the OAuth keys. """

      config = ConfigParser.ConfigParser()
      have_config = (config.read(config_file_path) != [])
      if(not have_config):
         _LOG.error("Could not open the PyRDM configuration file. Check that the file 'pyrdm.ini' is in the ~/.config/ directory, and that it is readable.")
         sys.exit(1)
      return config

   def publish_software(self, name, local_repo_location, version=None, private=False):
      """ Publishes the software in the current repository. """
      
      git_handler = GitHandler(local_repo_location)

      # If no software version is given, use the version of the local repository's HEAD.
      if(version is None):
         version = git_handler.get_head_version()
         _LOG.info("No version information provided. Using the local repository's HEAD as the version to publish (%s)." % version)

      # Search for the software, in case it has already been published.
      pid, doi = self.find_software(name, version)
      if(pid is not None):
         _LOG.info("Version %s of the software has already been published. Re-using the publication ID (%d) and DOI (%s)..." % (version, pid, doi))
         return pid, doi

      # The desired path to the archive file.
      archive_path = name + "-" + str(version) + ".zip"
      
      # Create the archive. First archive the local repository...
      success = git_handler.archive(version, archive_path)
      if(not success):
         _LOG.error("Could not obtain an archive of the software at the specified version.")
         sys.exit(1)
      
      # ...then upload it to the citable repository service.
      _LOG.info("Creating code repository for software...")
      title='%s (%s)' % (name, version)
      description='%s (Version %s)' % (name, version)

      if(self.service == "figshare"):
         pid = self.figshare.create_article(title=title, description=description, defined_type="code", tags=[version], categories=[])
         doi = self.figshare.reserve_doi(pid)
         _LOG.info("Code repository created with ID: %d and DOI: %s" % (pid, doi))

         _LOG.info("Adding category...")
         self.figshare.add_category(article_id=pid, category="Computer Software")
         _LOG.info("Category added.")
         
         _LOG.info("Uploading software...")
         self.figshare.add_file(article_id=pid, file_path=archive_path)
         self.verify_upload(pid=pid, files=[archive_path])

         _LOG.info("Adding all authors (with author IDs) to the code...")
         author_ids = self.get_authors_list(git_handler.get_working_directory())
         _LOG.debug("List of author IDs: %s" % (author_ids,))
         if(author_ids is not None):
            # Convert to a list of dictionaries with ('id':id) pairs.
            author_ids = [{'id':author_id} for author_id in author_ids]
            self.figshare.add_authors(pid, author_ids)
         _LOG.info("All authors (with author IDs) added.")

         # If we are not keeping the code private, then make it public.
         if(not private):
            _LOG.info("Making the code public...")
            self.figshare.publish(article_id=pid)
            _LOG.info("The code has been made public.")

      elif(self.service == "zenodo"):

         # With Zenodo we have to obtain the authors list and tags *before* creating the deposition.
         _LOG.info("Obtaining author names and affiliations...")
         authors = self.get_authors_list(git_handler.get_working_directory())

         if(authors is None or authors == []):
            _LOG.warning("""Could not obtain author information from an AUTHORS file. 
            Zenodo requires at least one author to be present in the author's list. 
            Using the name and affiliation given in the PyRDM configuration file.""")
            authors = [{"name": self.config.get("general", "name"), "affiliation": self.config.get("general", "affiliation")}]
         _LOG.debug("List of authors and affiliations: %s" % (authors,))
         
         publication_details = self.zenodo.create_deposition(title=title, description=description, upload_type="software", 
                                                             creators=authors, keywords=[version], prereserve_doi=True)
         pid = publication_details["id"]
         doi = str(publication_details["metadata"]["prereserve_doi"]["doi"])
         _LOG.info("Code repository created with ID: %d and DOI: %s" % (pid, doi))

         _LOG.info("Uploading software...")
         self.zenodo.create_file(deposition_id=pid, file_path=archive_path)
         self.verify_upload(pid=pid, files=[archive_path])

         # If we are not keeping the code private, then make it public.
         if(not private):
            _LOG.info("Making the code public...")
            self.zenodo.publish_deposition(deposition_id=pid)
            _LOG.info("The code has been made public.")
            
      elif(self.service == "dspace"):
         collection = self.dspace.get_collection_by_title(self.config.get("dspace", "collection_title"))
         deposit_receipt = self.dspace.create_deposit_from_file(collection=collection, file_path=archive_path)
         pid = deposit_receipt.id
         doi = deposit_receipt.alternate # NOTE: This may be a Handle, rather than a DOI.
         
         _LOG.info("Code repository created with ID: %s and DOI: %s" % (pid, doi))
         
         # Add the metadata.
         _LOG.info("Adding metadata to the deposit...")
         authors = self.get_authors_list(git_handler.get_working_directory())
         deposit_receipt = self.dspace.replace_deposit_metadata(deposit_receipt, dcterms_title=title,
                                              dcterms_type="Software", dcterms_contributor=", ".join(authors))
         doi = deposit_receipt.alternate # Once the deposit has been completed, the DOI may have been updated.
         
         # Complete the deposit.
         _LOG.info("Completing the deposit...")
         try:
            self.dspace.complete_deposit(deposit_receipt)
         except:
            _LOG.error("A server error occurred when trying to 'complete' the deposit. This might be because the deposit is already complete, but check the deposit just in case.")
            pass
            
         deposit_receipt = self.dspace.connection.get_deposit_receipt(pid)
         doi = deposit_receipt.alternate # Once the deposit has been completed, the DOI may have been updated.
            
      return pid, doi
      
      
   def publish_data(self, parameters, pid=None, private=False):
      """ Create a new dataset on the online, citable repository's server. 
      Returns a dictionary of details about the new dataset once created. """
         
      _LOG.info("Publishing data...")
  
      if(pid is None):
         _LOG.info("Creating new fileset...")
         if(self.service == "figshare"):
            # NOTE: The defined_type needs to be a 'fileset' to allow multiple files to be uploaded separately.
            pid = self.figshare.create_article(title=parameters["title"], description=parameters["description"], defined_type="fileset", tags=parameters["tag_name"], categories=[])
            doi = self.figshare.reserve_doi(pid)
            
            # Add category
            _LOG.info("Adding category...")
            if(parameters["category"] is not None):
               self.figshare.add_category(pid, parameters["category"])
            
         elif(self.service == "zenodo"):
            publication_details = self.zenodo.create_deposition(title=parameters["title"], description=parameters["description"], upload_type="dataset",
                                                                creators=[{"name": self.config.get("general", "name"), "affiliation": self.config.get("general", "affiliation")}], 
                                                                keywords=parameters["tag_name"], prereserve_doi=True)
            pid = publication_details["id"]
            doi = str(publication_details["metadata"]["prereserve_doi"]["doi"])
            
         elif(self.service == "dspace"):
            collection = self.dspace.get_collection_by_title(self.config.get("dspace", "collection_title"))
            deposit_receipt = self.dspace.create_deposit_from_metadata(collection=collection, in_progress=True, dcterms_title=parameters["title"], dcterms_description=parameters["description"], 
                                              dcterms_type="Dataset", dcterms_creator=self.config.get("general", "name"))
            pid = deposit_receipt.id
            doi = deposit_receipt.alternate  

         _LOG.info("Fileset created with ID: %s and DOI: %s" % (pid, doi))

         # This is a new article, so upload ALL the files!
         modified_files = parameters["files"]
         existing_files = []
      else:
         publication_details = None
         doi = None # FIXME: We could try to look up the DOI associated with a given PID in the future.
         # This is an existing publication, so check whether any files have been modified since they were last published.
         modified_files = self.find_modified(parameters["files"])
         if(self.service == "figshare"):
            existing_files = self.figshare.list_files(pid)
         elif(self.service == "zenodo"):
            existing_files = self.zenodo.list_files(pid)
         elif(self.service == "dspace"):
            raise NotImplementedError("It is not yet possible to modify a deposit that has been 'completed'.")

      _LOG.debug("The following files have been marked for uploading: %s" % modified_files)
      uploaded_files = []
      
      for f in modified_files:
         # Check whether the file actually exists locally.
         if(os.path.exists(f)):
            _LOG.info("Uploading %s..." % f)
            
            # Check whether the file already exists on the server. If so, over-write the version on the server.
            exists = False
            
            if(self.service == "figshare"):
               for e in existing_files:
                  if(e["name"] == os.path.basename(f)):
                     _LOG.info("File already exists on the server. Over-writing...")
                     exists = True
                     # FIXME: It is currently not possible to over-write an existing file via the Figshare API.
                     # We have to delete the file and then add it again.
                     self.figshare.delete_file(article_id=pid, file_id=e["id"])
                     self.figshare.add_file(article_id=pid, file_path=f)
                     break
               if(not exists):
                  self.figshare.add_file(article_id=pid, file_path=f)
                  
            elif(self.service == "zenodo"):
               for e in existing_files:
                  if(e["filename"] == os.path.basename(f)):
                     _LOG.info("File already exists on the server. Over-writing...")
                     exists = True
                     # FIXME: It is currently not possible to over-write an existing file via the Zenodo API.
                     # We have to delete the file and then add it again.
                     self.zenodo.delete_file(deposition_id=pid, file_id=e["id"])
                     self.zenodo.create_file(deposition_id=pid, file_path=f)
                     break
               if(not exists):
                  self.zenodo.create_file(deposition_id=pid, file_path=f)

            elif(self.service == "dspace"):
               #FIXME: With DSpace, we currently have to assume that the file does not exist.
               exists = False
               if(not exists):
                  r = self.dspace.add_file(file_path=f, receipt=deposit_receipt)

            # Write out the .md5 checksum file
            self.write_checksum(f)
            # Record the upload.
            uploaded_files.append(f)
         else:
            _LOG.warning("File %s not present on the local system. Skipping..." % f)
            continue

      self.verify_upload(pid=pid, files=uploaded_files)
      
      # If we are not keeping the data private, then make it public.
      if(not private and self.service != "dspace"):
         _LOG.info("Making the data public...")
         if(self.service == "figshare"):
            self.figshare.publish(article_id=pid)
         elif(self.service == "zenodo"):
            self.zenodo.publish_deposition(deposition_id=pid)
         _LOG.info("The data has been made public.")
         
      # Finalise the deposit in DSpace (if applicable).
      if(self.service == "dspace"):
         _LOG.info("Completing the deposit...")
         try:
            self.dspace.complete_deposit(receipt=deposit_receipt)
         except:
            _LOG.error("A server error occurred when trying to 'complete' the deposit. This might be because the deposit is already complete, but check the deposit just in case.")
            pass
            
         deposit_receipt = self.dspace.connection.get_deposit_receipt(pid)
         doi = deposit_receipt.alternate # Once the deposit has been completed, the DOI may have been updated.
            
      return pid, doi
      
   def write_checksum(self, f):
      """ For a given file with path 'f', write a corresponding MD5 checksum file. """
      md5 = hashlib.md5(open(f).read()).hexdigest()
      checksum_file = open(f + ".md5", "w")
      checksum_file.write(md5)
      checksum_file.close()
      return

   def find_modified(self, files):
      """ Return a list of files (whose paths are in the argument 'files') which have been modified.
      This is based on MD5 checksums. """
      modified = []
      for f in files:
         if(os.path.isfile(f + ".md5")):
            checksum_file = open(f + ".md5", "r")
            md5_original = checksum_file.readline()
            md5 = hashlib.md5(open(f).read()).hexdigest()
            
            if(md5 != md5_original):
               modified.append(f)
         else:
            # No checksum file present - assume new or modified.
            modified.append(f)
            
      return modified

   def find_software(self, name, version):
      """ Checks if the software has already been published. If so, it returns the DOI.
      Otherwise it returns None. """
      
      keyword = "%s" % (name) # We always include the software's name in the title, so use it as the keyword
      
      if(self.service == "figshare"):
         results = self.figshare.search(keyword) # We always tag the software with its version (the SHA-1 hash for Git repositories).

         for article in results:
            try:
               if str(version) in article.tags:
                  _LOG.info("Software %s has already been published (with version %s).\n" % (name, version))
                  pid = article["id"]

                  # Try to find the DOI as well.
                  # This try-except block might not be necessary if we are always searching public articles.
                  try:
                     doi = article["doi"]
                     if doi == "":
                        raise ValueError()
                     _LOG.info("Software DOI: %s" % doi)
                  except:
                     _LOG.info("DOI not found.")
                     doi = None
                  return pid, doi
            except AttributeError:
               pass
              
         return None, None
            
      elif(self.service == "zenodo"):
         # FIXME: There is currently no way of easily searching for a Zenodo deposit based on its keywords via the API.
         # Therefore, assume for now that the software has not been published.
         return None, None
         
      elif(self.service == "dspace"):
         # FIXME: Assume for now that the software has not been published.
         return None, None   

   def get_authors_list(self, wd):
      """ If an AUTHORS file exists in a given repository's base directory, then read it and
      match any author IDs using a regular expression. Return all author IDs in a single list. """
      
      author_ids = []
      try:
         # Assumes that the AUTHORS file is in the root directory of the project.
         f = open(wd + "/AUTHORS", "r")
         for line in f.readlines():
         
            if(self.service == "figshare"):
               m = re.search("<%s:([0-9]+)>" % self.service, line)
               if(m is not None):
                  author_id = int(m.group(1)) # Figshare expects integer author IDs.
                  author_ids.append(author_id)
                  
            elif(self.service == "zenodo"):
               m = re.search("<%s:(.+;.+)>" % self.service, line)
               if(m is not None):
                  s = m.group(1).split(";")
                  author_id = {'name':s[0], 'affiliation':s[1]}
                  author_ids.append(author_id)
                  
            elif(self.service == "dspace"):
               #TODO: This currently uses the author's DSpace username. Is there a better identifier? 
               m = re.search("<%s:(.+)>" % self.service, line)
               if(m is not None):
                  author_id = m.group(1)
                  author_ids.append(author_id)
               
         return author_ids
      except IOError:
         _LOG.warning("Could not open AUTHORS file. Does it exist? Check read permissions?")
         return None

   def is_uploaded(self, pid, files):
      """ Return True if the files in the list 'files' are all present on the server. Otherwise, return False. """
      if(self.service == "figshare"):
         files_on_server = self.figshare.list_files(pid)
         key = "name"
      elif(self.service == "zenodo"):
         files_on_server = self.zenodo.list_files(pid)
         key = "filename"
      elif(self.service == "dspace"):
         deposit_receipt = self.dspace.connection.get_deposit_receipt(pid)
         try:
            files_on_server = self.dspace.list_files(deposit_receipt.edit_media_feed, self.config.get("dspace", "user_name"), self.config.get("dspace", "user_pass"))
         except:
            return True # This will fail if the deposit has not yet been 'completed'. Assume all files have been uploaded successfully (if they haven't, the DSpace library should tell us anyway).
         
      for f in files:
         exists = False
         for s in files_on_server:
            if(isinstance(s, dict)): # Figshare and Zenodo file objects are dictionaries.
               if(s[key] == os.path.basename(f)):
                  exists = True
                  break
            else:
               if(s == os.path.basename(f)):
                  exists = True
                  break
         if(exists):
            continue
         else:
            _LOG.warning("Could not find file %s on the server." % f)
            return False
      return True

   def verify_upload(self, pid, files):
      """ Verify that all files in the list 'files' have been uploaded. """
      if(self.is_uploaded(pid=pid, files=files)):
         _LOG.info("All files successfully uploaded.")
      else:
         _LOG.warning("Not all files were successfully uploaded. Perhaps you ran out of space on the server?")
         while True:
            response = raw_input("Are you sure you want to continue? (Y/N)\n")
            if(response == "y" or response == "Y"):
               break
            elif(response == "n" or response == "N"):
               # Clean up and exit.
               # NOTE: This only deletes draft/unpublished code/filesets.
               if(self.service == "figshare"):
                  self.figshare.delete_article(article_id=pid)
               elif(self.service == "zenodo"):
                  self.zenodo.delete_deposition(deposition_id=pid)
               sys.exit(1)
            else:
               continue
      return

   def publication_exists(self, pid):
      if(self.service == "figshare"):
         results = self.figshare.get_article_details(pid)
         if("error" in results.keys()):
            return False
         else:
            return True
      elif(self.service == "zenodo"):
         try:
            results = self.zenodo.retrieve_deposition(pid)
         except:
            return False
         return True
      elif(self.service == "dspace"):
         #FIXME: Assume that the publication does not exist for now.
         return False

class TestLog(unittest.TestCase):
   """ Unit test suite for PyRDM's Publisher module. """

   def setUp(self):
      self.publisher = Publisher(service="figshare")
            
      f = open("test_file.txt", "w")
      f.write("Hello World! This is a file for the MD5 functionality test.")
      f.close()
      return

   def tearDown(self):
      return

   def test_md5_write_checksum(self):
      self.publisher.write_checksum("test_file.txt")
      
      f = open("test_file.txt.md5", "r")
      md5_known = "29586140472f40eec4031eb2e0d352e1"
      md5 = hashlib.md5(open("test_file.txt").read()).hexdigest()
      _LOG.debug("Known MD5 hash of file: %s" % md5_known)
      _LOG.debug("Computed MD5 hash of file: %s" % md5)
      assert(md5 == md5_known)
      
   def test_md5_find_modified(self):
      self.publisher.write_checksum("test_file.txt")
      
      modified = self.publisher.find_modified(["test_file.txt"])
      _LOG.debug("Modified files: ", modified)
      assert(modified == [])
      
      # Modify the file.      
      f = open("test_file.txt", "a")
      f.write("This is another line.")
      f.close()
      
      # Check that the MD5 checksums are not the same
      md5_before = "29586140472f40eec4031eb2e0d352e1"
      md5_after = hashlib.md5(open("test_file.txt").read()).hexdigest()
      _LOG.debug("MD5 hash before modification: %s" % md5_before)
      _LOG.debug("MD5 hash after modification: %s" % md5_after)
      assert(md5_before != md5_after)
      
      modified = self.publisher.find_modified(["test_file.txt"])
      _LOG.debug("Modified files: ", modified)
      assert(modified == ["test_file.txt"])

   def test_get_authors_list(self):
      try:
         git_handler = GitHandler(".") # Assume that the unittests are being run from the PyRDM base directory
      except git.InvalidGitRepositoryError:
         _LOG.warning("Skipping the 'get_authors_list' test because the Git repository could not be opened. This is expected if you downloaded PyRDM as a .zip or .tar.gz file, but not if you used 'git clone'.")
         return

      authors_list = self.publisher.get_authors_list(git_handler.get_working_directory())
      _LOG.debug("authors_list = %s" % (authors_list,))

      assert(554577 in authors_list)
      assert(566335 in authors_list)
      assert(444083 in authors_list)
      assert(565687 in authors_list)

if(__name__ == '__main__'):
   unittest.main()

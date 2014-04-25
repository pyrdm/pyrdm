#!/usr/bin/env python

# Copyright (C) 2014 Alexandros Avdis, Gerard J. Gorman, Christian T. Jacobs, Matthew D. Piggott.

import git
import ConfigParser

from figshare import Figshare

class Publisher:

   def __init__(self, config):
      # Read in the authentication tokens, etc from the configuration file.
      self.config = config

      # Set up a Figshare object, in case we want to push data directly to Figshare
      # (rather than via Fidgit).
      fs = Figshare(self.config)

      return

   def publish_software(self, exclude_dirs = []):
      """ Publishes the software in the current repository to Figshare using Fidgit. """

      # Create a Repo object representing the current Git repository.
      repo = git.Repo(".")
      assert repo.bare == False

      # Get the origin of the remote repository, for pushing and pulling.
      origin = repo.remotes.origin

      # First make sure we are using an up-to-date version of the repository.
      origin.pull()

      # Is the current state of the Git repository modified?
      if(repo.is_dirty()):
         # Ask the user to commit any modified files...
         response = raw_input("Repository has uncommitted changes. Do you wish to commit them before continuing? (y/n)\n")
         if(response == "y" or response == "Y"):
            index = repo.index # The index is basically the staging area.
            message = raw_input("Please enter a commit message: \n")
            commit = index.commit(message)

            # Maybe ask about untracked files too?

         # Push any outstanding changes to the remote repository.
         pushed = origin.push() # The return value is a list of PushInfo objects, one for each commit in the push.

         if( (pushed is None) or (True in [pushed[i].ERROR for i in range(len(pushed))]) ):
            print "Could not push the changes to GitHub. Check network connection? Check permissions?"
            return None

      # Get the SHA of the HEAD commit.
      head_sha = repo.head.commit.hexsha

      # Get Fidgit to take a snapshot of the repository. This will require an HTTP POST to the server running Fidgit.


      response = client.get('http://api.figshare.com/v1/my_data/authors?search_for=Hill', auth=oauth)
      publication_details = json.loads(response.content)
      doi = publication_details["doi"]

      # Return the DOI. Note: this may have been done in a previous run, so check for an existing version.
      return doi

   def publish_data(self, parameters):
      """ Publishes the user-specified input (or output) files directly to Figshare. """
      publication_details = self.fs.create_article(parameters)
      doi = publication_details["doi"]

      # Return the DOI.
      return doi


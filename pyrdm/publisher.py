#!/usr/bin/env python

#    Copyright (C) 2014 Alexandros Avdis, Christian T. Jacobs, Gerard J. Gorman, Matthew D. Piggott.

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

import git
import ConfigParser

import requests
from requests_oauthlib import OAuth1
import json

from pyrdm.figshare import Figshare

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
      print "Pulling changes from remote '%s', branch '%s' ..." % (origin, repo.active_branch)
      origin.pull(origin.refs[0].remote_head) # FIXME: This assumes that the first RemoteReference in the list 'origin.refs' corresponds to the active branch, which may not always be the case.

      index = repo.index # The index is basically the staging area.
      index.add([diff.a_blob.name for diff in index.diff(None)]) # List all the modified files

      # Is the current state of the Git repository modified?
      if(repo.is_dirty()): # TODO: Make sure that the directories containing modified files are not in the 'exclude_dirs' list.
         # Ask the user to commit any modified files...
         response = raw_input("Repository has uncommitted changes. Do you wish to commit them before continuing? (y/n)\n")
         if(response == "y" or response == "Y"):
            message = raw_input("Please enter a commit message: \n")
            commit = index.commit(message)

            # TODO: Maybe ask about untracked files too?

         # Push any outstanding changes to the remote repository.
         pushed = origin.push() # The return value is a list of PushInfo objects, one for each commit in the push.

         if( (pushed is None) or (True in [pushed[i].ERROR for i in range(len(pushed))]) ):
            print "Could not push the changes to GitHub. Check network connection? Check permissions?"
            return None

      # Get the SHA of the HEAD commit.
      head_sha = repo.head.commit.hexsha

      # Get Fidgit to take a snapshot of the repository. This will require an HTTP POST to the server running Fidgit in order to invoke it.
      # FIXME: We may also need to modify Fidgit so it downloads the repository with the correct version, rather than a specific release/tag.
      oauth = OAuth1(client_key = self.config["github_token"], signature_type = 'auth_header')
      client = requests.session() 
      body = {'release':{'tag_name':'v1.0'}, 'repository':{'full_name':'ctjacobs/game-of-life'}}
      headers = {'content-type':'application/json'}
      response = client.post('%s/events?secret=%s' % (self.config["fidgit_url"], self.config["github_token"]), auth=oauth,
                              data=json.dumps(body), headers=headers)
      print response

      # FIXME: Is there a nicer way to do this? At the moment we invoke Fidgit via HTTP POST, but can't tell us if a) the publication has been created, and b) what the DOI is.
      # So we instead search for the software's name and the matching tag (which is the SHA1 identifier of the head commit).
      #
      # TODO: Include the branch name in the tags.
      response = client.get('http://api.figshare.com/v1/my_data/articles?search_for=%s,has_tag=%s' % (self.config["software_name"], head_sha), auth=oauth)
      publication_details = json.loads(response.content)
      return publication_details

   def publish_data(self, parameters):
      """ Publishes the user-specified input (or output) files directly to Figshare. """
      publication_details = self.fs.create_article(parameters)
      return publication_details


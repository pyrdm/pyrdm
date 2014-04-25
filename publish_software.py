#!/usr/bin/env python

import git
import ConfigParser

def publish_software():
   # Read the configuration file to obtain the OAuth tokens, etc.

   # Get the repository from Git.
   repo = git.Repo(".")
   assert repo.bare == False

   origin = repo.remotes.origin

   # Is the current state of the Git repository modified?
   if(repo.is_dirty()):
      # Ask the user to commit any modified files...
      print "Repository has uncommitted changes. Do you wish to commit them before continuing?"

      # Maybe ask about untracked files too?

      # Push the changes to the remote repository.
      pushed = origin.push() # The return value is a list of PushInfo objects, one for each commit in the push.

      if( (pushed is None) or (True in [pushed[i].ERROR for i in range(len(pushed))]) ):
         print "Could not push the changes to GitHub. Check network connection? Check permissions?"
         return None

   # Get the SHA of the HEAD commit.
   head_sha = repo.head.commit.hexsha

   # Get Fidgit to take a snapshot of the repository. This will require HTTP POST.

   doi = "test"


   # Return the DOI. Note: this may have been done in a previous run, so check for an existing version.
   return doi

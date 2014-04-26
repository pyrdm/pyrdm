#!/usr/bin/env python

# Copyright (C) 2014 Alexandros Avdis, Gerard J. Gorman, Matthew D. Piggott, Christian T. Jacobs.

import ConfigParser

from publisher import Publisher

class PyRDM:

   def __init__(self):
      self.config = self.load_config("pyrdm.config")
      self.publisher = Publisher(self.config)
      return


   def load_config(self, config_file_path):
      """ Load the configuration file containing the OAuth keys and information about the software name, etc
      into a dictionary called 'config' and return it. """
      f = open(config_file_path, "r")

      config = {}
      for line in f.readlines():
         s = line.replace(" ", "").replace("\n", "")
         key, value = s.split("=")
         config[key] = value

      f.close()
      return config

#if(__name__ == "__main__"):
rdm = PyRDM()
rdm.publisher.publish_software([])

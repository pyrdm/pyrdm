#!/usr/bin/env python

# Copyright (C) 2014 Alexandros Avdis, Gerard J. Gorman, Christian T. Jacobs, Matthew D. Piggott.

import ConfigParser

from publisher import Publisher

class PyRDM:

   def __init__(self):
      self.config = self.load_config("pyrdm.config")
      self.publisher = Publisher(self.config)
      return


   def load_config(self, config_file_path):
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
rdm.publisher.publish_data([])

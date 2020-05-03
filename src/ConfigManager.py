#!/usr/bin/env python

"""ConfigManager.py: Configuration file manager."""

__author__      = "Balaji Sundaresan"
__copyright__   = "Copyright 2019-20, mAnava"
__version__     = "0.0.2"

import configparser

class ConfigManager:

   __instance = None
   __config = None

   @staticmethod 
   def getInstance():
      """ Static access method. """
      if ConfigManager.__instance == None:
         ConfigManager()
      instance = ConfigManager.__instance
      return instance

   def __init__(self):
      """ Virtually private constructor. """
      if ConfigManager.__instance != None:
         raise Exception("Error! Internal error Orchestrator is a singleton.")
      else:
         ConfigManager.__instance = self
         try:
            self.__config = configparser.ConfigParser()
            self.__config.read('invoice-extractor-checker.ini')
         except:
            self.__config = None


   def get(self, section_name, key, default_value):

      if self.__config == None:
         return default_value

      return self.__config.get(section_name, key, fallback=default_value)

#!/usr/bin/env python

"""PluginManager.py: Configuration file manager."""

__author__      = "Balaji Sundaresan"
__copyright__   = "Copyright 2019, mAnava"
__version__     = "0.0.1"

from Logger import Logger
from pluginbase import PluginBase

class PluginManager:

   __instance = None
   __plugin_base = None
   __plugin_source = None
   __loaded_plugin = None

   @staticmethod 
   def getInstance():
      """ Static access method. """
      if PluginManager.__instance == None:
         PluginManager()
      instance = PluginManager.__instance
      return instance

   def __init__(self):
      """ Virtually private constructor. """
      if PluginManager.__instance != None:
         raise Exception("Error! Internal error Orchestrator is a singleton.")
      else:
         PluginManager.__instance = self
         try:
            self.__plugin_base = PluginBase(package='plugins')
            self.__plugin_source = self.__plugin_base.make_plugin_source(searchpath=['./plugins'])
         except:
            logger = Logger.getLogger()
            logger.error('Error! Failed to load plugins')
            self.__plugin_base = None
            self.__plugin_source = None

   def load_plugin(self, plugin_name):
      try:
         print plugin_name
         if self.__plugin_source is not None:
            self.__loaded_plugin = self.__plugin_source.load_plugin(plugin_name)
      except Exception as e:
         logger = Logger.getLogger()
         logger.error('Error! Failed to load plugin %s. Plugin transformation will be unavailable.', plugin_name )

   def get(self, _type, type_name, type_value):

      if self.__loaded_plugin == None:
         return type_value
         
      try:
         return self.__loaded_plugin.transform(_type, type_name, type_value)
      except:
         logger = Logger.getLogger()
         logger.error('Error! Failed to transform (%s,%s,%s) in plugin.', _type, type_name, type_value )
         return type_value

   def get_line_item(self, index, type_name, type_value):

      if self.__loaded_plugin == None:
         return type_value
         
      try:
         return self.__loaded_plugin.transform_line_item(index, type_name, type_value)
      except:
         logger = Logger.getLogger()
         logger.error('Error! Failed to transform (%s,%s,%s) in plugin.', index, type_name, type_value )
         return type_value  

   def post_processor(self, extracted_data, container_instance):

      if self.__loaded_plugin == None:
         return extracted_data
         
      try:
         return self.__loaded_plugin.post_processor(extracted_data, container_instance)
      except:
         logger = Logger.getLogger()
         logger.error('Error! Failed to perform post processing in plugin.')
         return extracted_data               

#!/usr/bin/env python

"""Logger.py: Logging related functionality."""

__author__      = "Balaji Sundaresan"
__copyright__   = "Copyright 2019, mAnava"
__version__     = "0.0.1"

import logging
from logging.handlers import TimedRotatingFileHandler
import os
import errno
import sys

from ConfigManager import ConfigManager

class Logger:

   __instance = None
   _logger = None

   @staticmethod 
   def getLogger():
      """ Static access method. """
      if Logger.__instance == None:
         Logger()
      instance = Logger.__instance
      return instance._logger

   def __init__(self):
      """ Virtually private constructor. """
      if Logger.__instance != None:
         raise Exception("Error! Internal error Logger is a singleton.")
      else:
         Logger.__instance = self
         self._set_up_logging()

   def _set_up_logging(self):

      configMgr = ConfigManager.getInstance()
      level_mapping = {"DEBUG":logging.DEBUG, "INFO":logging.INFO, "WARN":logging.WARN, "ERROR":logging.ERROR, \
         "CRITICAL":logging.CRITICAL}
      level = configMgr.get("logger","level",'INFO')
      logging_level = level_mapping.get(level)

      try:
         dirs = ['log']
         for dirName in dirs:
               os.makedirs(dirName)
      except OSError as exc:
         if exc.errno == errno.EEXIST :
               pass
         else:
               raise Exception("ERROR! Failed to create directory.")
            
      self._logger = logging.getLogger()
      formatter = logging.Formatter(
         '%(asctime)s %(name)-12s %(levelname)-8s %(message)s')
      self._logger.setLevel(logging_level)         

      stream_handler = logging.StreamHandler(sys.stdout)
      stream_handler.setLevel(logging.INFO)
      stream_handler.setFormatter(formatter)

      log_filename = configMgr.get("logger","filename",'log/invoice-extractor-checker.logs')
      file_handler = TimedRotatingFileHandler(log_filename,
                                       when="d",
                                       interval=1,
                                       backupCount=60)
      file_handler.setFormatter(formatter)
      file_handler.setLevel(logging_level)

      self._logger.addHandler(stream_handler)
      self._logger.addHandler(file_handler)
        

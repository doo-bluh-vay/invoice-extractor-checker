#!/usr/bin/env python

"""Orchestrator.py: Extraction related orchestrating."""

__author__      = "Balaji Sundaresan"
__copyright__   = "Copyright 2019-20, mAnava"
__version__     = "0.0.2"

from ObjectLayoutContainer import ObjectLayoutContainer
import FieldExtractor
import LineItemExtractor
import TemplateChoser
import io
import json
import Checker

from Logger import Logger
from PluginManager import PluginManager

class Orchestrator:

   __instance = None

   @staticmethod 
   def getInstance():
      """ Static access method. """
      if Orchestrator.__instance == None:
         Orchestrator()
      instance = Orchestrator.__instance
      return instance

   def __init__(self):
      """ Virtually private constructor. """
      if Orchestrator.__instance != None:
         raise Exception("Error! Internal error Orchestrator is a singleton.")
      else:
         Orchestrator.__instance = self

   def go(self, text_dump_filename, template_information, pdf_file_with_path, output_file_with_path):

      logger = Logger.getLogger()

      olb = ObjectLayoutContainer.getInstance()
      olb.parse_pdf(pdf_file_with_path, text_dump_filename)

      try:
         template_file_name = TemplateChoser.get_template_name(template_information)
      except Exception as ex:
         logger.error(str(ex))
         return

      plugin_manager = None
      plugin_name = self._get_plugin_name(template_file_name)
      if plugin_name is not None:
         plugin_manager = PluginManager.getInstance()
         plugin_manager.load_plugin(plugin_name)
         logger.info('Loaded plugin %s', plugin_name)

      dict_of_field_values = FieldExtractor.extract_fields(template_file_name)

      self._transform_field_values(plugin_manager, dict_of_field_values)

      dict_of_line_items = LineItemExtractor.extract_line_items(template_file_name)

      self._transform_lineitem_values(plugin_manager, dict_of_line_items)

      check_status = Checker.check_total(plugin_manager, template_file_name, dict_of_field_values, dict_of_line_items)

      if len(dict_of_field_values) > 0 or len(dict_of_line_items) > 0 or len(check_status) >  0:
         extracted_data = {}
         if len(dict_of_field_values) > 0 :
            extracted_data["fields"] = dict_of_field_values
         if len(dict_of_line_items) > 0 :
            extracted_data["lineitems"] = dict_of_line_items
         if len(check_status) > 0 :
            extracted_data["checkstatus"] = check_status
            logger.info("Check Status Match = %s", str(check_status["match_status"]))

         returned_extraced_value = self._invoke_post_processor(plugin_manager, extracted_data)

         with io.open(output_file_with_path, 'w', encoding='utf-8') as f:
               f.write(str(json.dumps(returned_extraced_value, ensure_ascii=False, indent = 4)))

   def _get_plugin_name(self, template_file_name):

      with open(template_file_name, "r") as read_file:
         json_template = json.load(read_file)     
         
      return json_template.get("plugin")

   def _transform_field_values(self, plugin_manager, dict_of_field_values):

      if plugin_manager is not None and len(dict_of_field_values) > 0 :
         for key, value in list(dict_of_field_values.items()):
            returned_value = plugin_manager.get("field", key, value)
            dict_of_field_values[key] = returned_value

   def _transform_lineitem_values(self, plugin_manager, dict_of_line_items):

      if plugin_manager is not None and len(dict_of_line_items) > 0 :
         index = 0
         for line_item in dict_of_line_items:
            for key, value in list(line_item.items()):
               returned_value = plugin_manager.get_line_item(index, key, value)
               line_item[key] = returned_value
            index += 1

   def _invoke_post_processor(self, plugin_manager, extracted_data):

      if plugin_manager is not None:
         container_instance = ObjectLayoutContainer.getInstance()
         returned_extraced_value = plugin_manager.post_processor(extracted_data, container_instance)
         return returned_extraced_value
      else:
         return extracted_data


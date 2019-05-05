#!/usr/bin/env python

"""Orchestrator.py: Extraction related orchestrating."""

__author__      = "Balaji Sundaresan"
__copyright__   = "Copyright 2019, mAnava"
__version__     = "0.0.1"

from ObjectLayoutContainer import ObjectLayoutContainer
import FieldExtractor
import LineItemExtractor
import TemplateChoser
import io
import json
import Checker

from Logger import Logger

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

      template_file_name = TemplateChoser.get_template_name(template_information)

      dict_of_field_values = FieldExtractor.extract_fields(template_file_name)

      dict_of_line_items = LineItemExtractor.extract_line_items(template_file_name)

      check_status = Checker.check_total(template_file_name, dict_of_field_values, dict_of_line_items)

      if len(dict_of_field_values) > 0 or len(dict_of_line_items) > 0 or len(check_status) >  0:
         extracted_data = {}
         if len(dict_of_field_values) > 0 :
            extracted_data["fields"] = dict_of_field_values
         if len(dict_of_line_items) > 0 :
            extracted_data["lineitems"] = dict_of_line_items
         if len(check_status) > 0 :
            extracted_data["checkstatus"] = check_status
            logger.info("Check Status Match = %s", str(check_status["match_status"]))
         with io.open(output_file_with_path, 'w', encoding='utf-8') as f:
               f.write(json.dumps(extracted_data, ensure_ascii=False, indent = 4))        


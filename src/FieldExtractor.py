#!/usr/bin/env python

"""FieldExtractor.py: Field Extraction related functionality."""

__author__      = "Balaji Sundaresan"
__copyright__   = "Copyright 2019, mAnava"
__version__     = "0.0.1"

import json

from Logger import Logger
import collections
from ObjectLayoutAlgorithms import ObjectLayoutAlgorithms

def extract_fields(template_file_name):

    logger = Logger.getLogger()
    objectlayoutalgo_instance = ObjectLayoutAlgorithms.getInstance()
    dict_of_field_values = collections.OrderedDict()

    with open(template_file_name, "r") as read_file:
        json_template = json.load(read_file)            

        configured_field_count = 0
        for field in json_template['fields']:
            logger.debug("Searching for %s", field['name'])

            if field['location'] == 'regex':
                list_keyword_locations, list_regex_values = objectlayoutalgo_instance.search_regex(field['identifier'])    
                if len(list_regex_values) > 0:
                    counter = 0
                    while counter < len(list_regex_values):
                        text = list_regex_values[counter]
                        if text != None and len(text) > 0:
                            try:
                                ordinal = field['ordinal']
                                if int(ordinal) == (counter+1):
                                    dict_of_field_values[field['name']] = text
                            except KeyError:
                                dict_of_field_values[field['name']] = text
                        counter += 1 
            else:
                list_keyword_locations = []
                list_regex_values = []
                if field['location'] == 'regex' or field['location'].startswith('regex'):
                    list_keyword_locations, list_regex_values = objectlayoutalgo_instance.search_regex(field['identifier'])    
                else:
                    list_keyword_locations = objectlayoutalgo_instance.search_keyword(field['identifier'])

                if len(list_keyword_locations) > 0:
                    counter = 0
                    while counter < len(list_keyword_locations):
                        keyword_location = list_keyword_locations[counter]
                        ordinal = field.get('ordinal')
                        if ordinal == None or int(ordinal) == (counter+1):
                            if field['location'] == 'bottom' or field['location'] == 'regex-bottom':
                                text = objectlayoutalgo_instance.get_text_at_bottom(keyword_location)
                            elif field['location'] == 'right' or field['location'] == 'regex-right':
                                text = objectlayoutalgo_instance.get_text_to_right(1, keyword_location)
                            elif field['location'] == 'second-right' or field['location'] == 'regex-second-right':
                                text = objectlayoutalgo_instance.get_text_to_right(2, keyword_location)
                            if text != None and len(text) > 0:
                                dict_of_field_values[field['name']] = text
                        counter += 1

            configured_field_count += 1

    logger.info("Total fields : Configured = %d, Extracted = %d", configured_field_count, len(dict_of_field_values))
    return dict_of_field_values



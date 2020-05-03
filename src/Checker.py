#!/usr/bin/env python

"""Checker.py: Check if a field with TOTAL value matches the sum of all the Line item TOTAL values."""

__author__      = "Balaji Sundaresan"
__copyright__   = "Copyright 2019-20, mAnava"
__version__     = "0.0.2"

import json
import re

from Logger import Logger
from ConfigManager import ConfigManager
from PluginManager import PluginManager

def check_total(plugin_manager, template_file_name, dict_of_field_values, dict_of_line_items):

    logger = Logger.getLogger()
    logger.debug(' ==> check_total(%s,%d,%d)', template_file_name, len(dict_of_field_values), len(dict_of_line_items) )

    check_status = {}
    match_status = {}

    # Load the template file for accessing check information
    with open(template_file_name, "r") as read_file:
        json_template = json.load(read_file)            

    # Only if these is check information, extract field and lineitem column names
    if json_template.get("check") is not None :
        field = json_template["check"]["field"]
        lineitem = json_template["check"]["lineitem"]
        field_name = field["name"]
        lineitem_name = lineitem["name"]
        field_regex_pattern = field.get("regex")
        lineitem_regex_pattern = lineitem.get("regex")

        try:
            # Get the field value, if regex extract the numeric value else take value as is.
            field_value = dict_of_field_values.get(field_name)
            if field_value is None:
                match_status = { "status" : False, "description" : "Field value cannot be empty"}
                check_status["match_status"] = match_status
                logger.debug('check_total(%s) ==>', str(match_status))
                return check_status
            if field_regex_pattern is not None:
                regex_search = re.search(field_regex_pattern, field_value) 
                if regex_search is not None:
                    column_value = regex_search.group("Total")
                    float_field_value = float(column_value.replace(',', ''))
                else:
                    match_status = { "status" : False, "description" : "field regex pattern mismatch"}
                    check_status["match_status"] = match_status
                    logger.debug('check_total(%s) ==>', str(match_status))
                    return check_status
            elif plugin_manager is not None:
                float_field_value = float(plugin_manager.get("check", "field", field_value))
            else:
                float_field_value = float(field_value.replace(',', ''))

            # Go through all the line items, pick the line item total field value or numeric value regex extracted line item total value
            sum_lineitem_value = 0.0
            for lineitem in dict_of_line_items:
                lineitem_value = lineitem.get(lineitem_name)
                if lineitem_value is not None:
                    if lineitem_regex_pattern is not None:
                        regex_search = re.search(lineitem_regex_pattern, lineitem_value) 
                        if regex_search is not None:
                            column_value = regex_search.group("Total")
                            float_lineitem_value = float(column_value.replace(',', ''))
                        else:
                            match_status = { "status" : False, "description" : "lineitem regex pattern mismatch"}
                            check_status["match_status"] = match_status
                            logger.debug('check_total(%s) ==>', str(match_status))
                            return check_status
                    elif plugin_manager is not None:
                        float_lineitem_value = float(plugin_manager.get("check", "lineitem", str(lineitem_value)))
                    else:
                        float_lineitem_value = float(lineitem_value.replace(',', ''))  
                                         
                    sum_lineitem_value += float_lineitem_value

            # Check if the field total value and sum of line item total values match
            configMgr = ConfigManager.getInstance()
            precision_digits_to_compare = int(configMgr.get("checker","precision_digits_to_compare",2))
            if round(float_field_value,precision_digits_to_compare) == round(sum_lineitem_value,precision_digits_to_compare):
                match_status = { "status" : True}
                check_status["match_status"] = match_status
            else:
                match_status = { "status" : False, "description" : str(float_field_value) + " != " + str(sum_lineitem_value)}
                check_status["match_status"] = match_status
        except ValueError:
            match_status = { "status" : False, "description" : "Conversion error"}
            check_status["match_status"] = match_status
        except IndexError:
            match_status = { "status" : False, "description" : "regex Total lookup failed"}
            check_status["match_status"] = match_status

    logger.debug('check_total(%s) ==>', str(match_status))
    return check_status



#!/usr/bin/env python

"""LineItemExtractor.py: Line Item Extraction related functionality."""

__author__      = "Balaji Sundaresan"
__copyright__   = "Copyright 2019, mAnava"
__version__     = "0.0.1"

import json

from Logger import Logger
from copy import deepcopy
from ObjectLayoutAlgorithms import ObjectLayoutAlgorithms
from ObjectLayoutAlgorithms import ColumnInformation

def extract_line_items(template_file_name):

    with open(template_file_name, "r") as read_file:
        json_template = json.load(read_file)      

    dict_of_line_item_values = {}

    if json_template.get("table_lineitems") != None:
        dict_of_line_item_values = determine_table_lineitems(json_template)
    elif json_template.get("regex_lineitems") != None:
        dict_of_line_item_values = determine_regex_lineitems(json_template)

    return dict_of_line_item_values

####################################################################
#  
#   Table
#  
####################################################################

def determine_table_lineitem_header_location(template):

    logger = Logger.getLogger()

    lineitems_start_location = -1
    lineitems_start_page_location = -1
    dict_column_text_widths = {}

    if template.get("table_lineitems") != None:
        list_lineitem_columns = []
        for column in template["table_lineitems"]["columns"]:
            column_name = column["name"].split('\n')
            list_lineitem_columns.append(column_name)

        objectlayoutalgo_instance = ObjectLayoutAlgorithms.getInstance()
        lineitems_start_page_location, lineitems_start_location, dict_column_text_widths = objectlayoutalgo_instance.get_table_lineitem_header_location(list_lineitem_columns)     

        for header_name, textbox_details in dict_column_text_widths.items():
            logger.debug("TABLE LINEITEM COLUMN |" + header_name.replace("\n","\\n") + "| (x0={0:7.2f},".format(textbox_details.x0) + "x1={0:7.2f})".format(textbox_details.x1) + 
            " (y0={0:7.2f},".format(textbox_details.y0) + "y1={0:7.2f})".format(textbox_details.y1))

    logger.debug("LINE ITEM START Page = " + str(lineitems_start_page_location) + ", Line = " + str(lineitems_start_location))
    return lineitems_start_page_location, lineitems_start_location, dict_column_text_widths

def determine_table_lineitem_end_location(template, lineitems_start_page_location, lineitems_start_location):

    logger = Logger.getLogger()

    lineitems_end_location = -1
    lineitems_end_page_location = -1

    if template.get("table_lineitems") != None and template.get("table_lineitems").get("line_end") != None:
        lineitems_end_text = template["table_lineitems"]["line_end"]
        objectlayoutalgo_instance = ObjectLayoutAlgorithms.getInstance()
        lineitems_end_page_location, lineitems_end_location = \
            objectlayoutalgo_instance.get_table_lineitem_end_location(lineitems_end_text, lineitems_start_page_location, lineitems_start_location)     

    logger.debug("LINE ITEM END Page = " + str(lineitems_end_page_location) + ", Line = " + str(lineitems_end_location))
    return lineitems_end_page_location, lineitems_end_location
    
def determine_table_lineitems(json_template):

    logger = Logger.getLogger()

    dict_of_line_item_values = {}

    lineitems_start_page_location, lineitems_start_location, dict_column_text_widths = determine_table_lineitem_header_location(json_template)   
    if lineitems_start_page_location == -1 or lineitems_start_location == -1:
        logger.error("ERROR!! Could not find the start location. Cannot proceed.") 
        return dict_of_line_item_values

    lineitems_end_page_location, lineitems_end_location =  determine_table_lineitem_end_location(json_template, lineitems_start_page_location, lineitems_start_location)
    if lineitems_end_page_location == -1 or lineitems_end_location == -1:
        logger.error("ERROR!! Could not find the end location. Cannot proceed.") 
        return dict_of_line_item_values
        
    if lineitems_end_page_location < lineitems_start_page_location or (lineitems_start_page_location == lineitems_end_page_location and lineitems_end_location >= lineitems_start_location):
        logger.error("ERROR!! End location should be always after start location.")
        return dict_of_line_item_values
        
    logger.debug("Start = (%7.2f,%7.2f), End = (%7.2f,%7.2f)" ,lineitems_start_page_location, lineitems_start_location, lineitems_end_page_location, lineitems_end_location)

    list_of_column_information = []
    for column in json_template["table_lineitems"]["columns"]:
        column_name = column["name"]
        alignment = column["alignment"]
        row_start = column["row_start"]
        list_of_column_information.append(ColumnInformation(column_name, alignment, row_start))
    has_vertical_lines = json_template["table_lineitems"]["vertical_lines"]
    has_horizontal_lines = json_template["table_lineitems"]["horizontal_lines"]

    objectlayoutalgo_instance = ObjectLayoutAlgorithms.getInstance()
    dict_of_line_item_values = objectlayoutalgo_instance.get_table_lineitems(list_of_column_information, dict_column_text_widths, \
        lineitems_start_page_location, lineitems_start_location, lineitems_end_page_location, lineitems_end_location, has_vertical_lines, \
            has_horizontal_lines)

    logger.info("Total Line Items Extracted = %d", len(dict_of_line_item_values))
    return dict_of_line_item_values    

####################################################################
#  
#   Regular Expression 
#  
####################################################################

def determine_regex_lineitem_header_location(template):

    logger = Logger.getLogger()

    lineitems_start_location = -1
    lineitems_start_page_location = -1

    if template.get("regex_lineitems") != None and template.get("regex_lineitems").get("line_start") != None:
        lineitem_header_regex = template["regex_lineitems"]["line_start"]

        objectlayoutalgo_instance = ObjectLayoutAlgorithms.getInstance()
        lineitems_start_page_location, lineitems_start_location = objectlayoutalgo_instance.get_regex_lineitem_header_location(lineitem_header_regex)     

    logger.debug("LINE ITEM START Page = " + str(lineitems_start_page_location) + ", Line = " + str(lineitems_start_location))
    return lineitems_start_page_location, lineitems_start_location

def determine_regex_lineitem_end_location(template, lineitems_start_page_location, lineitems_start_location):

    logger = Logger.getLogger()

    lineitems_end_location = -1
    lineitems_end_page_location = -1

    if template.get("regex_lineitems") != None and template.get("regex_lineitems").get("line_end") != None:
        lineitem_header_regex = template["regex_lineitems"]["line_end"]

        objectlayoutalgo_instance = ObjectLayoutAlgorithms.getInstance()
        lineitems_end_page_location, lineitems_end_location = objectlayoutalgo_instance.get_table_lineitem_end_location \
        (lineitem_header_regex, lineitems_start_page_location, lineitems_start_location)     

    logger.debug("LINE ITEM END Page = " + str(lineitems_end_page_location) + ", Line = " + str(lineitems_end_location))
    return lineitems_end_page_location, lineitems_end_location

def determine_regex_lineitems(json_template):

    logger = Logger.getLogger()

    dict_of_line_item_values = {}

    lineitems_start_page_location, lineitems_start_location = determine_regex_lineitem_header_location(json_template)
    
    if lineitems_start_page_location == -1 or lineitems_start_location == -1:
        logger.error("ERROR!! Could not find the start location. Cannot proceed.") 
        return dict_of_line_item_values
   
    lineitems_end_page_location, lineitems_end_location = determine_regex_lineitem_end_location(json_template, lineitems_start_page_location, \
        lineitems_start_location)
    
    if lineitems_end_page_location == -1 or lineitems_end_location == -1:
        logger.error("ERROR!! Could not find the end location. Cannot proceed.") 
        return dict_of_line_item_values
        
    if lineitems_end_page_location < lineitems_start_page_location or (lineitems_start_page_location == lineitems_end_page_location and lineitems_end_location >= lineitems_start_location):
        logger.error("ERROR!! End location should be always after start location.")
        return dict_of_line_item_values
        
    logger.debug("Start = (%7.2f,%7.2f), End = (%7.2f,%7.2f)" ,lineitems_start_page_location, lineitems_start_location, lineitems_end_page_location, lineitems_end_location)

    regex_lines = deepcopy(json_template["regex_lineitems"]["lines"])
    list_of_columns = deepcopy(json_template["regex_lineitems"]["columns"])

    objectlayoutalgo_instance = ObjectLayoutAlgorithms.getInstance()
    dict_of_line_item_values = objectlayoutalgo_instance.get_regex_lineitems(regex_lines, list_of_columns, \
        lineitems_start_page_location, lineitems_start_location, lineitems_end_page_location, lineitems_end_location)

    logger.info("Total Line Items Extracted = %d", len(dict_of_line_item_values))
    return dict_of_line_item_values 
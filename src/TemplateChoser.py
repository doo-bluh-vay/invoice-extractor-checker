#!/usr/bin/env python

"""TemplateChoser.py: Decide which template to apply."""

__author__      = "Balaji Sundaresan"
__copyright__   = "Copyright 2019, mAnava"
__version__     = "0.0.1"

import json
import os

from Logger import Logger
from jsonschema import validate
from jsonschema import exceptions
from ObjectLayoutAlgorithms import ObjectLayoutAlgorithms

def get_template_name(template_information):

    # Load the schema json file 
    schema = None
    with open('../schema/invoice-schema-1_0_0.json', "r") as read_file:
        schema = json.load(read_file)

    # Check if schema load was successful
    if schema == None:
        raise Exception("Error! Failed to load the json schema file.")

    # If a template file name is given, check if this is the correct match
    if os.path.isfile(template_information):
        file_name = check_if_template_matches(template_information, schema)
        if file_name != None:
            return file_name
        else:
            raise Exception("Error! Template file did not match.")
    # If a folder name is given, recursively check which template file matches
    elif os.path.isdir(template_information):
        for root, directories, filenames in os.walk(template_information):
            for filename in filenames:
                full_path_template_file_name = os.path.join(root,filename)
                if full_path_template_file_name.endswith(".json"): 
                    file_name = check_if_template_matches(full_path_template_file_name, schema)
                    if file_name != None:
                        return file_name
        
        raise Exception("Error! Could not find a suitable template for the given file.")  
    # Oops!      
    else:
        raise Exception("Error! Template file neither a file nor a directory.")



def check_if_template_matches(full_path_template_file_name, schema):

    logger = Logger.getLogger()
    objectlayoutalgo_instance = ObjectLayoutAlgorithms.getInstance()

    # Check if its a json file
    if full_path_template_file_name.endswith(".json") == False:     
        logger.error("ERROR!! Template file should a json file.")      
        return None

    # Load the template json file
    try: 
        with open(full_path_template_file_name, "r") as read_file:
            json_template = json.load(read_file)            
    except IOError:
        logger.error("ERROR!! Failed to load template file " + full_path_template_file_name)      
        return None

    # Validate the template file and check if this is the template file that matches pdf contents
    try:
        validate(instance=json_template, schema=schema)

        set_keywords = set(json_template["keywords"][:])  

        found_all_keywords = objectlayoutalgo_instance.check_if_all_text_present(set_keywords)

        if found_all_keywords == True:
            logger.info("Picked template file " + full_path_template_file_name)  
            return full_path_template_file_name
        else:
            return None
    except (exceptions.ValidationError, exceptions.SchemaError):
        logger.error("ERROR!! Template file " + full_path_template_file_name + " failed schema validation.")      
        return None

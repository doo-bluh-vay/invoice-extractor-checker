#!/usr/bin/env python

"""Main.py: Program entry point main function."""

__author__      = "Balaji Sundaresan"
__copyright__   = "Copyright 2019, mAnava"
__version__     = "0.0.1"

from Logger import Logger
from Orchestrator import Orchestrator
import argparse

def parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument('--dump', type=str, required=False)
    parser.add_argument('--template', type=str, required=True)
    parser.add_argument('--file', type=str, required=True)
    parser.add_argument('--output', type=str, required=True)
    args = parser.parse_args()
    return args

def setup_logging():
    logger = Logger.getLogger()
    logger.info('***** invoice-extractor-checker STARTED :-) *****')

def setup_orchestrator(text_dump, template_information, pdf_file_with_path, output_file_with_path):
    instance = Orchestrator.getInstance()
    instance.go(text_dump, template_information, pdf_file_with_path, output_file_with_path)

def shutdown_application():
    logger = Logger.getLogger()
    logger.info('***** invoice-extractor-checker COMPLETED *****')

def main():

    # Handle Command line arguments
    args = parse_arguments()

    # Setup logging
    setup_logging()

    # Instantiate and invoke orchestrator
    setup_orchestrator(args.dump, args.template, args.file, args.output)

    # Shutdown
    shutdown_application()


if __name__== "__main__":
    main()        

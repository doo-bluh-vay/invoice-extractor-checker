Solution to extract fields and line items from native PDF invoices
===========================================================

This project is based on invoice2data which extracts data from invoice pdf files using user written regular expressions. It is observed that quite some invoices cannot be extracted just using the regular expression approach since pdf text is organized not as lines of text rather as boxes with co-ordinates. Field values are placed at locations like to the right, bottom of a field so on. Line items can also placed in tables. This solution tries to use other techniques along with regular expressions to solve the problem.

The solution is written in python and provides the following capabilities

 *  Extract Field values (Based on regex or location based - right, bottom ...) 
 *  Table based line item extraction (regex, vertical or horizontal table lines ...) 
 *  Check if the extracted line item Total values matches the Sum Total. 

Installation
============

- Requires python 3
- pip/conda install the following libraries
	json, re, deepcopy, configparser, logging, pdfminer, argparse, sortedcontainers, sets, pluginbase

Templates
=========

Templates which are in json format are used to tell the application how to pick field values (regex, top, bottom of field name) and also how line items are present in the invoice (With or Without Horizontal Vertical Lines, Line item columns…).

Look at the data folder which contains jpg images of a few invoices (original native pdfs). Corresponding templates can be found at the template folder.
Reading the jpg and its corresponding template json side-by-side would help easily understand the template contents.

Detailed Documentation
======================
Refer doc/invoice-extractor-checker.pdf for detailed documentation.


Running the application
=======================

From the src folder, 
python Main.py --dump <PDF text content dump to file> --template <Location of folder where templates are placed> --file <Location of PDF> --output <Location to output extracted contents as json>

E.g:-,
python Main.py --dump dump.txt --template ../template/ --file "../data/Amazon-Storeji.pdf" --output "../output/Amazon-Storeji.json"


Future work
===========
1. Simple User Interface to edit template files.
2. Docker image.
3. Multi page/Multi header occurrences/Multi header pdfs.
4. Improve Table Line items extractions.
5. Run on more invoice samples/new formats.

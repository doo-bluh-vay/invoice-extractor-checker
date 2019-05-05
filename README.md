Solution to extract fields and line items from native PDF invoices
===========================================================

This project is based on invoice2data wherein it extracts data based on regular expressions. However, observation is that quite some invoices cannot be extracted using a regular expression approach. Field values are placed at locations like to the right, bottom of a field so on. Line items are also placed in tables. This solution tries to use other techniques along with regular expressions.

A python based application to extract
1. Field values (Based on regex, right, bottom ...)
2. Table based line item extraction (regex, vertical or horizontal table lines ...)
3. Check if the extracted line item Total values matches the Sum Total.


Installation
============

- Requires python 2.7
- pip/conda install the following libraries
	json, re, deepcopy, configparser, logging, pdfminer, argparse, sortedcontainers, sets

Templates
=========

Templates which are in json format, tell the solution how to pick field values (regex, top, bottom of field name) and how line items
are present in the invoice (W/O Horizontal Vertical Lines, Line item columns)

Look at the data folder which contains jpg images of a few invoices (original native pdfs). Corresponding templates can be found at the template folder.
Reading the jpg and its corresponding template json side-by-side would help easily understand the template contents.


Running the application
=======================

From the src folder, 
python Main.py --dump <PDF text content dump to file> --template <Location of folder where templates are placed> --file <Location of PDF> --output <Location to output extracted contents as json>

E.g:-,
python Main.py --dump dump.txt --template ../template/ --file "../data/Amazon-Storeji.pdf" --output "../output/Amazon-Storeji.json"


Future work
=======================
1. Simple User Interface to edit template files.
2. Docker image.
3. Multi page/Multi header occurrences/Multi header pdfs.
4. Improve Table Line items extractions.
5. Run on more invoice samples/new formats.

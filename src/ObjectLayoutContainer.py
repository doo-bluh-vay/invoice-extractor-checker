#!/usr/bin/env python

"""ObjectLayoutContainer.py: pdf parsing, object building, storage related functionality."""

__author__      = "Balaji Sundaresan"
__copyright__   = "Copyright 2019-20, mAnava"
__version__     = "0.0.2"

import logging
from logging.handlers import TimedRotatingFileHandler
import os
import errno

from Logger import Logger
from copy import deepcopy

from ConfigManager import ConfigManager

from pdfminer.pdfparser import PDFParser
from pdfminer.pdfdocument import PDFDocument
from pdfminer.pdfpage import PDFPage
from pdfminer.pdfpage import PDFTextExtractionNotAllowed
from pdfminer.pdfinterp import PDFResourceManager
from pdfminer.pdfinterp import PDFPageInterpreter
from pdfminer.pdfdevice import PDFDevice
from pdfminer.layout import LAParams
from pdfminer.converter import PDFPageAggregator
import pdfminer

from sortedcontainers import SortedDict, SortedList

class TextBox:
  def __init__(self, x0, y0, x1, y1, text):
    self.x0 = x0
    self.y0 = y0
    self.x1 = x1
    self.y1 = y1
    self.text = text

class HorizontalLine:
  def __init__(self, y, x0, x1):
    self.y = y
    self.x0 = x0
    self.x1 = x1

class VerticalLine:
  def __init__(self, x, y0, y1, src):
    self.x = x
    self.y0 = y0
    self.y1 = y1
    self.src = src

class ObjectLayoutContainer:

   __instance = None
   _pdf_parsed = False
   _pagewise_rows_of_y0_textboxes = []
   _pagewise_rows_of_y1_textboxes = []
   _pagewise_rows_of_horizontal_lines = []
   _pagewise_rows_of_vertical_lines = []   

   @staticmethod 
   def getInstance():
      """ Static access method. """
      if ObjectLayoutContainer.__instance == None:
         ObjectLayoutContainer()
      return ObjectLayoutContainer.__instance

   def __init__(self):
      """ Virtually private constructor. """
      if ObjectLayoutContainer.__instance != None:
         raise Exception("Error! Internal error ObjectLayoutContainer is a singleton.")
      else:
         ObjectLayoutContainer.__instance = self

   @property
   def pdf_parsed(self):
      return self._pdf_parsed

   @property
   def pagewise_rows_of_y0_textboxes(self):
      return self._pagewise_rows_of_y0_textboxes
      
   @property
   def pagewise_rows_of_y1_textboxes(self):
      return self._pagewise_rows_of_y1_textboxes

   @property
   def pagewise_rows_of_horizontal_lines(self):
      return self._pagewise_rows_of_horizontal_lines

   @property
   def pagewise_rows_of_vertical_lines(self):
      return self._pagewise_rows_of_vertical_lines

   def parse_pdf(self, pdf_file_name_with_path, text_dump_filename):

      Logger.getLogger().info("Parsing file " + pdf_file_name_with_path)

      if self._pdf_parsed == True:
         raise Exception('Error! PDF already parsed and loaded.')

      # Open a PDF file.
      fp = open(pdf_file_name_with_path, 'rb')

      # Create a PDF parser object associated with the file object.
      parser = PDFParser(fp)

      # Create a PDF document object that stores the document structure.
      # Password for initialization as 2nd parameter
      document = PDFDocument(parser)

      # Check if the document allows text extraction. If not, abort.
      if not document.is_extractable:
         raise PDFTextExtractionNotAllowed

      # Create a PDF resource manager object that stores shared resources.
      rsrcmgr = PDFResourceManager()

      # Create a PDF device object.
      device = PDFDevice(rsrcmgr)

      # BEGIN LAYOUT ANALYSIS
      # Set parameters for analysis.
      laparams = LAParams()

      # Create a PDF page aggregator object.
      device = PDFPageAggregator(rsrcmgr, laparams=laparams)

      # Create a PDF interpreter object.
      interpreter = PDFPageInterpreter(rsrcmgr, device)
         
      # loop over all pages in the document
      for page in PDFPage.create_pages(document):

         # read the page into a layout object
         interpreter.process_page(page)
         layout = device.get_result()

         # extract text from this object
         self._parse_obj(layout._objs)

      self._perform_sanity_check()

      self._dump_data_structures()

      if text_dump_filename is not None:
         self._dump_text(text_dump_filename)

      # If things came till here, successful parse
      self._pdf_parsed = True

   def _parse_obj(self, lt_objs):

      configMgr = ConfigManager.getInstance()
      character_closeness = int(configMgr.get("object_layout_container","character_closeness",2))

      rows_of_y0_textboxes = SortedDict()
      rows_of_y1_textboxes = SortedDict()
      rows_of_horizontal_lines = SortedDict()
      rows_of_vertical_lines = SortedDict()

      prev_TextBox = TextBox(0,0,0,0,"")

      # loop over the object list
      for obj in lt_objs:

         # if it's a textbox, process text and location
         if isinstance(obj, pdfminer.layout.LTChar):
            x0 = obj.bbox[0]
            y0 = obj.bbox[1]
            x1 = obj.bbox[2]
            y1 = obj.bbox[3]
            if prev_TextBox.y0 == y0 and prev_TextBox.y1 == y1 and (x0 - prev_TextBox.x1) <= character_closeness:
                prev_TextBox.text += obj.get_text()
                prev_TextBox.x1 = x1
            else:
                # y1 based list
                textboxes_at_y1 = rows_of_y1_textboxes.get(prev_TextBox.y1)
                if textboxes_at_y1 == None:
                   textboxes_at_y1 = SortedDict()
                textboxes_at_y1[prev_TextBox.x1] = deepcopy(prev_TextBox)
                rows_of_y1_textboxes[prev_TextBox.y1] = textboxes_at_y1                
                # y0 based list
                textboxes_at_y0 = rows_of_y0_textboxes.get(prev_TextBox.y0)
                if textboxes_at_y0 == None:
                   textboxes_at_y0 = SortedDict()
                textboxes_at_y0[prev_TextBox.x0] = deepcopy(prev_TextBox)
                rows_of_y0_textboxes[prev_TextBox.y0] = textboxes_at_y0                
                prev_TextBox = TextBox(x0,y0,x1,y1,obj.get_text())        

         elif isinstance(obj, pdfminer.layout.LTTextBoxHorizontal):
            for o in obj._objs:
               if isinstance(o, pdfminer.layout.LTTextLineHorizontal):
                  # Get the (x0,y0) & (x1,y1) co-ordinates of the TextBox
                  x0 = o.bbox[0]
                  y0 = o.bbox[1]
                  x1 = o.bbox[2]
                  y1 = o.bbox[3]

                  text = o.get_text().rstrip('\n')
                  # y1 based list
                  textboxes_at_y1 = rows_of_y1_textboxes.get(y1)
                  if textboxes_at_y1 == None:
                     textboxes_at_y1 = SortedDict()
                  textboxes_at_y1[x1] = TextBox(x0,y0,x1,y1,text)
                  rows_of_y1_textboxes[y1] = textboxes_at_y1
                  # y0 based list
                  textboxes_at_y0 = rows_of_y0_textboxes.get(y0)
                  if textboxes_at_y0 == None:
                     textboxes_at_y0 = SortedDict()
                  textboxes_at_y0[x0] = TextBox(x0,y0,x1,y1,text)
                  rows_of_y0_textboxes[y0] = textboxes_at_y0
                   
         # if it's a line, copy its location
         elif isinstance(obj, pdfminer.layout.LTLine):

               # Get the (x0,y0) & (x1,y1) co-ordinates of the Line
               x0 = obj.bbox[0]
               y0 = obj.bbox[1]
               x1 = obj.bbox[2]
               y1 = obj.bbox[3]

               # If its a horizontal line
               if y0 == y1 :
                  horizontal_lines_at_y = rows_of_horizontal_lines.get(y0)
                  if horizontal_lines_at_y == None:
                     horizontal_lines_at_y = SortedDict()
                  horizontal_lines_at_y[x0] = HorizontalLine(y0,x0,x1)
                  rows_of_horizontal_lines[y0] = horizontal_lines_at_y
               # If its a Vertical line
               elif x0 == x1:
                  vertical_lines_at_x = rows_of_vertical_lines.get(x0)
                  if vertical_lines_at_x == None:
                     vertical_lines_at_x = SortedDict()
                  vertical_line_at_x_y0 = vertical_lines_at_x.get(y0)
                  if vertical_line_at_x_y0 == None:
                     vertical_lines_at_x[y0] = VerticalLine(x0,y0,y1, "LINE")
                  else:
                     if vertical_line_at_x_y0.y1 < y1:
                        vertical_line_at_x_y0.y1 = y1
                        vertical_lines_at_x[y0] = vertical_line_at_x_y0
                  rows_of_vertical_lines[x0] = vertical_lines_at_x                    
                  
         # if it's a rectangle, copy its boundaries
         elif isinstance(obj, pdfminer.layout.LTRect) :

               # Get the (x0,y0) & (x1,y1) co-ordinates of the Line
               x0 = obj.bbox[0]
               y0 = obj.bbox[1]
               x1 = obj.bbox[2]
               y1 = obj.bbox[3]

               # Convert Rectangle boundaries to horizontal and vertical lines
               list_hor_lines = [y0,y1]
               for y in list_hor_lines:
                  horizontal_lines_at_y = rows_of_horizontal_lines.get(y)
                  if horizontal_lines_at_y == None:
                     horizontal_lines_at_y = SortedDict()
                  horizontal_lines_at_y[x0] = HorizontalLine(y,x0,x1)
                  rows_of_horizontal_lines[y] = horizontal_lines_at_y
               list_ver_lines = [x0,x1]
               for x in list_ver_lines:
                  vertical_lines_at_x = rows_of_vertical_lines.get(x)
                  if vertical_lines_at_x == None:
                     vertical_lines_at_x = SortedDict()
                  vertical_line_at_x_y0 = vertical_lines_at_x.get(y0)
                  if vertical_line_at_x_y0 == None:
                     vertical_lines_at_x[y0] = VerticalLine(x,y0,y1, "RECT")
                  else:
                     if vertical_line_at_x_y0.y1 < y1:
                        vertical_line_at_x_y0.y1 = y1
                        vertical_lines_at_x[y0] = vertical_line_at_x_y0
                  rows_of_vertical_lines[x] = vertical_lines_at_x                
                  
         # if it's a container, recurse
         elif isinstance(obj, pdfminer.layout.LTFigure):
               self._parse_obj(obj._objs)
   
      if prev_TextBox != None:
         # y1 based list
         textboxes_at_y1 = rows_of_y1_textboxes.get(prev_TextBox.y1)
         if textboxes_at_y1 == None:
            textboxes_at_y1 = SortedDict()
         textboxes_at_y1[prev_TextBox.x1] = deepcopy(prev_TextBox)
         rows_of_y1_textboxes[prev_TextBox.y1] = textboxes_at_y1                
         # y0 based list
         textboxes_at_y0 = rows_of_y0_textboxes.get(prev_TextBox.y0)
         if textboxes_at_y0 == None:
            textboxes_at_y0 = SortedDict()
         textboxes_at_y0[prev_TextBox.x0] = deepcopy(prev_TextBox)
         rows_of_y0_textboxes[prev_TextBox.y0] = textboxes_at_y0          

      self._pagewise_rows_of_y0_textboxes.append(rows_of_y0_textboxes)
      self._pagewise_rows_of_y1_textboxes.append(rows_of_y1_textboxes)
      self._pagewise_rows_of_horizontal_lines.append(rows_of_horizontal_lines)
      self._pagewise_rows_of_vertical_lines.append(rows_of_vertical_lines)

   def _perform_sanity_check(self):

      # Check if the size of the different lists are same (# of pages)
      pages_y0_textboxes_len = len(self._pagewise_rows_of_y0_textboxes)
      pages_y1_textboxes_len = len(self._pagewise_rows_of_y1_textboxes)
      pages_hor_lines_len = len(self._pagewise_rows_of_horizontal_lines)
      pages_ver_lines_len = len(self._pagewise_rows_of_vertical_lines)

      if pages_y0_textboxes_len != pages_y1_textboxes_len or pages_y0_textboxes_len != pages_hor_lines_len or \
         pages_y0_textboxes_len != pages_ver_lines_len:
         raise Exception("Error! # of Pages don't match.")

   def _dump_data_structures(self):
      logger = Logger.getLogger()
      if logger.isEnabledFor(logging.DEBUG):

         logger.debug('***** START Dump *****')

         page_counter = 0

         while page_counter < len(self._pagewise_rows_of_y0_textboxes) :
            
            logger.debug("PAGE #{0:3d}".format(page_counter))

            logger.debug('====== y0 TextBoxes ======')
            rows_of_y0_textboxes = self._pagewise_rows_of_y0_textboxes[page_counter]
            for key_y0 in list(reversed(rows_of_y0_textboxes)):
               row_text = "{0:7.2f}".format(key_y0) + " "
               textboxes_at_y0 = rows_of_y0_textboxes[key_y0]
               for key_x0 in list(textboxes_at_y0):
                     textbox_at_y0_x0 = textboxes_at_y0[key_x0]
                     row_text = row_text + " (" + "{0:7.2f}".format(textbox_at_y0_x0.x0) + ",<" + textbox_at_y0_x0.text + ">," + \
                        "{0:7.2f}".format(textbox_at_y0_x0.x1) + ")"
               logger.debug(row_text)
            logger.debug('====== y1 TextBoxes ======')
            rows_of_y1_textboxes = self._pagewise_rows_of_y1_textboxes[page_counter]
            for key_y1 in list(reversed(rows_of_y1_textboxes)):
               row_text = "{0:7.2f}".format(key_y1) + " "
               textboxes_at_y1 = rows_of_y1_textboxes[key_y1]
               for key_x1 in list(textboxes_at_y1):
                     textbox_at_y1_x1 = textboxes_at_y1[key_x1]
                     row_text = row_text + " (" + "{0:7.2f}".format(textbox_at_y1_x1.x0) + ",<" + textbox_at_y1_x1.text + ">," + \
                        "{0:7.2f}".format(textbox_at_y1_x1.x1) + ")"
               logger.debug(row_text)            
            logger.debug('====== Horizontal Lines ======')
            rows_of_horizontal_lines = self._pagewise_rows_of_horizontal_lines[page_counter]
            for key_y in list(reversed(rows_of_horizontal_lines)):
               row_text = "{0:7.2f}".format(key_y) + " "
               lines_at_y = rows_of_horizontal_lines[key_y]
               for key_x0 in list(lines_at_y):
                     line_at_y_x0 = lines_at_y[key_x0]
                     row_text = row_text + " (" + "{0:7.2f}".format(line_at_y_x0.x0) + "," + "{0:7.2f}".format(line_at_y_x0.x1) + ")"
               logger.debug(row_text)          
            logger.debug('====== Vertical Lines ======')
            rows_of_vertical_lines = self._pagewise_rows_of_vertical_lines[page_counter]
            for key_x in list(reversed(rows_of_vertical_lines)):
               row_text = "{0:7.2f}".format(key_x) + " "
               lines_at_x = rows_of_vertical_lines[key_x]
               for key_y0 in list(lines_at_x):
                     line_at_x_y0 = lines_at_x[key_y0]
                     row_text = row_text + " (" + "{0:7.2f}".format(line_at_x_y0.y0) + "," + "{0:7.2f}".format(line_at_x_y0.y1) + "," + line_at_x_y0.src + ")"
               logger.debug(row_text)    

            page_counter = page_counter + 1

         logger.debug('***** END Dump *****')

   def _dump_text(self, text_dump_filename):

      logger = Logger.getLogger()

      # Dump text to given file name
      try: 
         with open(text_dump_filename, "w") as write_file:
               page_counter = 0

               while page_counter < len(self._pagewise_rows_of_y0_textboxes) :
                  
                  write_file.write("=========\n")
                  write_file.write("PAGE #{0:3d}\n".format(page_counter))
                  write_file.write("=========\n")

                  rows_of_y0_textboxes = self._pagewise_rows_of_y0_textboxes[page_counter]
                  for key_y0 in list(reversed(rows_of_y0_textboxes)):
                     write_file.write(" {0:7.2f}\n".format(key_y0))
                     textboxes_at_y0 = rows_of_y0_textboxes[key_y0]
                     for key_x0 in list(textboxes_at_y0):
                        textbox_at_y0_x0 = textboxes_at_y0[key_x0]
                        write_file.write("     " + "(x0={0:7.2f},".format(textbox_at_y0_x0.x0) + "x1={0:7.2f})".format(textbox_at_y0_x0.x1) \
                           + " |" + textbox_at_y0_x0.text + "|\n")

                  page_counter = page_counter + 1
               
      except IOError:
         logger.error("ERROR!! Failed to dump text to " + text_dump_filename)      

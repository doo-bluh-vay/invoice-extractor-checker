#!/usr/bin/env python

"""ObjectLayoutAlgorithms.py: pdf parsed object access related functionality."""

__author__      = "Balaji Sundaresan"
__copyright__   = "Copyright 2019, mAnava"
__version__     = "0.0.1"

import re
import logging

from Logger import Logger
from ObjectLayoutContainer import ObjectLayoutContainer
from copy import deepcopy
from sortedcontainers import SortedDict, SortedList
from sets import Set

from ConfigManager import ConfigManager

class TextBoxLocation:
  def __init__(self, page_number, x0, y0, x1, y1):
    self.page_number = page_number
    self.x0 = x0
    self.y0 = y0
    self.x1 = x1
    self.y1 = y1

class ColumnInformation:
  def __init__(self, name, alignment, row_start):
    self.name = name
    self.alignment = alignment
    self.row_start = row_start

class ColumnTextWidth:
  def __init__(self, text, x0, x1, alignment):
    self.text = text
    self.x0 = x0
    self.x1 = x1
    self.alignment = alignment    

class ObjectLayoutAlgorithms:

   __instance = None

   @staticmethod 
   def getInstance():
      """ Static access method. """
      if ObjectLayoutAlgorithms.__instance == None:
         ObjectLayoutAlgorithms()
      return ObjectLayoutAlgorithms.__instance

   def __init__(self):
      """ Virtually private constructor. """
      if ObjectLayoutAlgorithms.__instance != None:
         raise Exception("Error! Internal error ObjectLayoutAlgorithms is a singleton.")
      else:
         ObjectLayoutAlgorithms.__instance = self

   def check_if_all_text_present (self, set_keywords):

      container_instance = ObjectLayoutContainer.getInstance()

      if container_instance.pdf_parsed == False :
         return False

      for rows_of_y0_textboxes in container_instance.pagewise_rows_of_y0_textboxes:
         for key_y0 in list(reversed(rows_of_y0_textboxes)):
               textboxes_at_y1 = rows_of_y0_textboxes[key_y0]
               temp_set_keywords = Set([]) 
               for key_x1 in list(textboxes_at_y1):
                  text_to_compare = textboxes_at_y1[key_x1].text
                  for keyword in set_keywords:
                     if keyword in text_to_compare:
                           temp_set_keywords.add(keyword)                    
               for keyword in temp_set_keywords:
                  set_keywords.discard(keyword)
               if len(set_keywords) == 0:
                  return True

      return False

   def search_keyword (self, keyword):

      list_keyword_locations = []

      container_instance = ObjectLayoutContainer.getInstance()

      if container_instance.pdf_parsed == False :
         return []

      page_counter = 0

      while page_counter < len(container_instance.pagewise_rows_of_y0_textboxes) :
         rows_of_y0_textboxes = container_instance.pagewise_rows_of_y0_textboxes[page_counter]
         for key_y0 in list(reversed(rows_of_y0_textboxes)):
            textboxes_at_y0 = rows_of_y0_textboxes[key_y0]
            for key_x0 in list(textboxes_at_y0):
               textbox_at_y0_x0 = textboxes_at_y0[key_x0]
               text_to_compare  = textbox_at_y0_x0.text
               if keyword == text_to_compare :
                  location = TextBoxLocation(page_counter, key_x0, key_y0, textbox_at_y0_x0.x1, textbox_at_y0_x0.y1)
                  list_keyword_locations.append(location)
                     
         page_counter += 1

      return list_keyword_locations

   def search_regex (self, regex_pattern):

      list_keyword_locations = []
      list_regex_values = []

      container_instance = ObjectLayoutContainer.getInstance()

      if container_instance.pdf_parsed == False :
         return []

      page_counter = 0

      while page_counter < len(container_instance.pagewise_rows_of_y0_textboxes) :
         rows_of_y0_textboxes = container_instance.pagewise_rows_of_y0_textboxes[page_counter]
         for key_y0 in list(reversed(rows_of_y0_textboxes)):
            textboxes_at_y0 = rows_of_y0_textboxes[key_y0]
            for key_x0 in list(textboxes_at_y0):
               textbox_at_y0_x0 = textboxes_at_y0[key_x0]
               text_to_compare  = textbox_at_y0_x0.text

               regex_search = re.search(regex_pattern, text_to_compare) 
               if regex_search is not None:
                  location = TextBoxLocation(page_counter, key_x0, key_y0, textbox_at_y0_x0.x1, textbox_at_y0_x0.y1)
                  list_keyword_locations.append(location)
                  try:
                     regex_group = regex_search.group(1)
                     list_regex_values.append(regex_group)
                  except IndexError:
                     list_regex_values.append("")
                     
         page_counter += 1

      return list_keyword_locations, list_regex_values

   def get_text_at_xy (self, textbox_location):

      container_instance = ObjectLayoutContainer.getInstance()

      if container_instance.pdf_parsed == False :
         raise Exception('Error! Internal error. PDF not yet parsed')

      if isinstance(textbox_location , TextBoxLocation) == False:
         raise Exception('Error! Internal error. Passed parameter not of TextBoxLocation type')

      rows_of_y0_textboxes = container_instance.pagewise_rows_of_y0_textboxes[textbox_location.page_number]
      textboxes_at_y0 = rows_of_y0_textboxes[textbox_location.y0]
      textbox_at_y0_x0 = textboxes_at_y0[textbox_location.x0]
      return textbox_at_y0_x0.text

   def get_text_at_bottom (self, textbox_location):

      container_instance = ObjectLayoutContainer.getInstance()

      if container_instance.pdf_parsed == False :
         raise Exception('Error! Internal error. PDF not yet parsed')

      if isinstance(textbox_location , TextBoxLocation) == False:
         raise Exception('Error! Internal error. Passed parameter not of TextBoxLocation type')

      rows_of_y1_textboxes = container_instance.pagewise_rows_of_y1_textboxes[textbox_location.page_number]
      for key_y1 in list(reversed(rows_of_y1_textboxes)):
         if key_y1 < textbox_location.y1:
         #if key_y1 <= textbox_location.y0:
            textboxes_at_y1 = rows_of_y1_textboxes[key_y1]
            for key_x1 in list(textboxes_at_y1):
               textbox_at_y1_x1 = textboxes_at_y1[key_x1]
               if textbox_at_y1_x1.x0 < textbox_location.x0:
                  if textbox_at_y1_x1.x1 > textbox_location.x0:
                     return textbox_at_y1_x1.text
               elif textbox_at_y1_x1.x0 == textbox_location.x0:
                  return textbox_at_y1_x1.text
               elif textbox_at_y1_x1.x0 > textbox_location.x0:
                  if textbox_at_y1_x1.x0 <= textbox_location.x1:
                     return textbox_at_y1_x1.text

      return ""   

   def get_text_to_right (self, position, textbox_location):

      if position < 1 :
         raise Exception('Error! Internal error. Text position cannot be less than 1')

      if isinstance(textbox_location , TextBoxLocation) == False:
         raise Exception('Error! Internal error. Passed parameter not of TextBoxLocation type')

      container_instance = ObjectLayoutContainer.getInstance()

      if container_instance.pdf_parsed == False :
         raise Exception('Error! Internal error. PDF not yet parsed')

      list_of_possible_textboxes = []

      rows_of_y0_textboxes = container_instance.pagewise_rows_of_y0_textboxes[textbox_location.page_number]
      rows_of_y1_textboxes = container_instance.pagewise_rows_of_y1_textboxes[textbox_location.page_number]

      temp_key_list = [list(reversed(rows_of_y1_textboxes)), list(rows_of_y0_textboxes)]
      temp_row_list = [rows_of_y1_textboxes, rows_of_y0_textboxes]
      counter = 0
      while counter < len(temp_key_list):
         for key_y in temp_key_list[counter]:
            if key_y >= textbox_location.y0 and key_y <= textbox_location.y1:
               textboxes_at_y = temp_row_list[counter][key_y]
               list_textboxes_at_y = list(textboxes_at_y)
               len_list_textboxes_at_y = len(list_textboxes_at_y)
               for (index,key_x) in enumerate(list_textboxes_at_y):
                  textbox_at_y_x = textboxes_at_y[key_x]
                  if textbox_at_y_x.x0 >= textbox_location.x1:
                     if position == 1:
                        self._copy_textbox(list_of_possible_textboxes, textbox_at_y_x)
                     elif position == 2:
                        if index < (len_list_textboxes_at_y-1):
                           next_key_x = list_textboxes_at_y[index+1]
                           textbox_at_next_y_x = textboxes_at_y[next_key_x]
                           self._copy_textbox(list_of_possible_textboxes, textbox_at_next_y_x)
         counter += 1

      rows_of_y1_textboxes = container_instance.pagewise_rows_of_y1_textboxes[textbox_location.page_number]

      for key_y in list(reversed(rows_of_y1_textboxes)):
         textboxes_at_y = rows_of_y1_textboxes[key_y]
         list_textboxes_at_y = list(textboxes_at_y)
         len_list_textboxes_at_y = len(list_textboxes_at_y)
         for (index,key_x) in enumerate(list_textboxes_at_y):
            textbox_at_y_x = textboxes_at_y[key_x]
            if textbox_at_y_x.x0 >= textbox_location.x1:
               if textbox_at_y_x.y1 > textbox_location.y1:
                  if textbox_at_y_x.y0 < textbox_location.y0:
                     if position == 1:
                        self._copy_textbox(list_of_possible_textboxes, textbox_at_y_x)
                     elif position == 2:
                        if index < (len_list_textboxes_at_y-1):
                           next_key_x = list_textboxes_at_y[index+1]
                           textbox_at_next_y_x = textboxes_at_y[next_key_x]
                           self._copy_textbox(list_of_possible_textboxes, textbox_at_next_y_x)
      len_list_of_possible_textboxes = len(list_of_possible_textboxes)
      if len_list_of_possible_textboxes == 0:
         return ""      
      elif len_list_of_possible_textboxes == 1:
         return list_of_possible_textboxes[0].text
      else:
         list_overlap = []
         list_closeness = []
         max_overlap = 0
         max_overlap_index = -1
         min_closeness = 0
         min_closeness_index = -1
         for index,temp_textbox in enumerate(list_of_possible_textboxes):
            if temp_textbox.y1 > textbox_location.y1:
               if temp_textbox.y0 < textbox_location.y1 and temp_textbox.y0 >= textbox_location.y0:
                  overlap = abs(textbox_location.y1-temp_textbox.y0)
               else:
                  overlap = abs(textbox_location.y1-textbox_location.y0)
            elif temp_textbox.y1 == textbox_location.y1:
               if temp_textbox.y0 >= textbox_location.y0:
                  overlap = abs(textbox_location.y1-temp_textbox.y0)
               else:
                  overlap = abs(textbox_location.y1-textbox_location.y0)
            else:
               if temp_textbox.y0 < textbox_location.y1 and temp_textbox.y0 >= textbox_location.y0:
                  overlap = abs(temp_textbox.y1-temp_textbox.y0)
               else:
                  overlap = abs(temp_textbox.y1-textbox_location.y0)

            closeness = temp_textbox.x0 - textbox_location.x1

            list_overlap.append(overlap)
            list_closeness.append(closeness)

            if index == 0:
               max_overlap = overlap
               max_overlap_index = 0
               min_closeness = closeness
               min_closeness_index = 0
            else:
               if overlap > max_overlap:
                  max_overlap = overlap
                  max_overlap_index = index
               if closeness < min_closeness:
                  min_closeness = closeness
                  min_closeness_index = index            

         if max_overlap_index == min_closeness_index:
            return list_of_possible_textboxes[max_overlap_index].text   
         else:
            overlap_ratio =  list_overlap[min_closeness_index] / list_overlap[max_overlap_index]
            closeness_ratio = list_closeness[min_closeness_index] / list_closeness[max_overlap_index]

            logger = Logger.getLogger()
            if logger.isEnabledFor(logging.DEBUG):
               logger.debug('OVERLAP INDEX:  ' + str(max_overlap_index))
               logger.debug('OVERLAP TEXT :  ' + list_of_possible_textboxes[max_overlap_index].text)
               logger.debug('OVERLAP VALUE :  ' + str(list_overlap[max_overlap_index]))
               logger.debug('OVERLAP CLOSENESS :  ' + str(list_closeness[max_overlap_index]))

               logger.debug('CLOSENESS INDEX:  ' + str(min_closeness_index))
               logger.debug('CLOSENESS TEXT :  ' + list_of_possible_textboxes[min_closeness_index].text)
               logger.debug('CLOSENESS VALUE :  ' + str(list_closeness[min_closeness_index]))
               logger.debug('CLOSENESS OVERLAP VALUE :  ' + str(list_overlap[min_closeness_index]))   

               logger.debug("OVERLAP RATIO   " + str(overlap_ratio))
               logger.debug("CLOSENESS RATIO " + str(closeness_ratio))

            if overlap_ratio < closeness_ratio:
               logger.debug("PICKED OVERLAP " + list_of_possible_textboxes[max_overlap_index].text )
               return list_of_possible_textboxes[max_overlap_index].text                  
            else:
               logger.debug("OVERLAP CLOSENESS " + list_of_possible_textboxes[min_closeness_index].text )
               return list_of_possible_textboxes[min_closeness_index].text                  

   def _copy_textbox (self, list_of_possible_textboxes, textbox):
      # First check if textbox already exists
      for temp_textbox in list_of_possible_textboxes:
         if temp_textbox.x1 == textbox.x1 and temp_textbox.x0 == textbox.x0 and \
            temp_textbox.y1 == textbox.y1 and temp_textbox.y0 == textbox.y0:
            return

      # if no add it
      list_of_possible_textboxes.append(deepcopy(textbox))

   def get_table_lineitem_header_location (self, list_lineitem_columns):

      container_instance = ObjectLayoutContainer.getInstance()

      if container_instance.pdf_parsed == False :
         return -1, -1, {}

      list_lineitem_columns_indexes = [0] * len(list_lineitem_columns)
      list_lineitem_header_textboxes = [None] * len(list_lineitem_columns)

      counter = 0
      while counter < len(list_lineitem_header_textboxes):
         list_lineitem_header_textboxes[counter] = TextBoxLocation(0,-1,-1,-1,-1)
         counter += 1

      for index, rows_of_y1_textboxes in enumerate(container_instance.pagewise_rows_of_y1_textboxes):
         for key_y1 in list(reversed(rows_of_y1_textboxes)):    

            list_columns_to_search = []
            dict_indexes = {}
            counter = 0
            while counter < len(list_lineitem_columns_indexes):
               temp_index = list_lineitem_columns_indexes[counter]
               if temp_index < len(list_lineitem_columns[counter]):
                  list_columns_to_search.append(list_lineitem_columns[counter][temp_index])
                  dict_indexes[len(list_columns_to_search)-1] = counter
               counter += 1

            search_start_index = 0
            textboxes_at_y1 = rows_of_y1_textboxes[key_y1]
            for key_x1 in list(textboxes_at_y1):
               textbox_at_y1_x1 = textboxes_at_y1[key_x1]
               text_to_search = textbox_at_y1_x1.text
               return_indexes, return_lengths = self._search_header_text(text_to_search, list_columns_to_search, search_start_index)
               if return_indexes == None:
                  list_lineitem_columns_indexes = [0] * len(list_lineitem_columns)
                  break
               else:
                  if len(return_indexes) != len(return_lengths):
                     return -1, -1, None
                  counter = 0
                  len_text_to_search = len(text_to_search)
                  char_width = (textbox_at_y1_x1.x1 - textbox_at_y1_x1.x0)/len_text_to_search
                  start_x0 = textbox_at_y1_x1.x0
                  while counter < len(return_indexes):
                     return_index = return_indexes[counter]
                     return_length = return_lengths[counter]
                     textbox = list_lineitem_header_textboxes[dict_indexes[return_index]]
                     textbox.y1 = key_y1
                     end_x1 = start_x0 + (return_length * char_width)
                     if textbox.x0 == -1 or start_x0 < textbox.x0:
                        textbox.x0 = start_x0
                     if textbox.x1 == -1 or end_x1 > textbox.x1:
                        textbox.x1 = end_x1
                     if textbox.y0 == -1 or textbox_at_y1_x1.y0 < textbox.y0:
                        textbox.y0 = textbox_at_y1_x1.y0
                     if textbox.y1 == -1 or textbox_at_y1_x1.y1 > textbox.y1:
                        textbox.y1 = textbox_at_y1_x1.y1                        
                     list_lineitem_header_textboxes[dict_indexes[return_index]] = textbox
                     start_x0 = end_x1 + char_width
                     list_lineitem_columns_indexes[dict_indexes[return_index]] += 1
                     search_start_index = return_index + 1
                     counter += 1

            found_all = True
            counter = 0
            while counter < len(list_lineitem_columns_indexes):
               temp_index = list_lineitem_columns_indexes[counter]
               if temp_index != len(list_lineitem_columns[counter]):
                  found_all = False
                  break
               counter += 1

            if found_all == True:
               dict_column_text_widths = {}
               for counter, column in enumerate(list_lineitem_columns):
                  column_name = '\n'.join(column)
                  dict_column_text_widths[column_name] = deepcopy(list_lineitem_header_textboxes[counter])
               return index, key_y1, dict_column_text_widths

      return -1, -1, {}

   def _search_header_text (self, text_to_search, list_columns_to_search, search_start_index):
      counter = search_start_index
      while counter < len(list_columns_to_search):
         text_from_list = list_columns_to_search[counter]
         if text_from_list == text_to_search:
            return [counter],[len(text_from_list)]
         elif text_to_search.startswith(text_from_list):
            return_indexes = [counter]
            return_lengths = [len(text_from_list)]
            new_text_to_search = text_to_search[len(text_from_list):].strip()
            if len(new_text_to_search) > 0:
               new_index, new_length = self._search_header_text(new_text_to_search, list_columns_to_search, counter + 1)
               if new_index == None:
                  return None, None
               else:
                  return_indexes = return_indexes + new_index
                  return_lengths = return_lengths + new_length
                  return return_indexes, return_lengths
            else:
               return [counter], [len(text_from_list)]
         counter += 1
         
      return None, None

   def get_table_lineitem_end_location (self, regex_pattern, lineitems_start_page_location, lineitems_start_location):

      container_instance = ObjectLayoutContainer.getInstance()

      if container_instance.pdf_parsed == False :
         return -1, -1

      for page_counter, rows_of_y1_textboxes in enumerate(container_instance.pagewise_rows_of_y1_textboxes):

         if page_counter < lineitems_start_page_location:
            continue  

         for key_y1 in list(reversed(rows_of_y1_textboxes)):

            if page_counter == lineitems_start_page_location and lineitems_start_location <= key_y1:
                  continue  

            textboxes_at_y1 = rows_of_y1_textboxes[key_y1]
            for key_x1 in list(textboxes_at_y1):
               textbox_at_y1_x1 = textboxes_at_y1[key_x1]
               text_to_compare  = textbox_at_y1_x1.text

               regex_search = re.search(regex_pattern, text_to_compare) 
               if regex_search is not None:
                  return page_counter, key_y1

      return -1, -1

   def get_table_lineitems(self, list_of_column_information, dict_column_text_widths, lineitems_start_page_location, \
      lineitems_start_location, lineitems_end_page_location, lineitems_end_location, has_vertical_lines, has_horizontal_lines):

      logger = Logger.getLogger()

      container_instance = ObjectLayoutContainer.getInstance()
      configMgr = ConfigManager.getInstance()
      lineitem_end_location_margin = int(configMgr.get("object_layout_algorithms","lineitem_end_location_margin",5))
      horizontal_line_margin = int(configMgr.get("object_layout_algorithms","horizontal_line_margin",5))
      alignment_margin = int(configMgr.get("object_layout_algorithms","alignment_margin",5))
      lineitem_columns_closeness = int(configMgr.get("object_layout_algorithms","lineitem_columns_closeness",3))

      if container_instance.pdf_parsed == False :
         return []

      list_of_line_items = []
      line_item_collector = {}

      # For case without Horizontal lines
      list_of_mapdata = []
      map_row_start_col_collection_status = {}
      for column in list_of_column_information:
         if column.row_start == True:
            map_row_start_col_collection_status[column.name] = 0
      line_start_index = 0

      # Traverse all the pages
      for page_number, rows_of_y1_textboxes in enumerate(container_instance.pagewise_rows_of_y1_textboxes):

         # Look at only pages from start to end. Others discard
         if page_number < lineitems_start_page_location:
            continue
            
         if page_number > lineitems_end_page_location:
            break

         # Traverse through all the rows in the current page
         previous_key_y1 = -1
         list_reversed_rows_of_y1_textboxes = list(reversed(rows_of_y1_textboxes))
         for row_number, key_y1 in enumerate(list_reversed_rows_of_y1_textboxes):    

            if page_number == lineitems_start_page_location and lineitems_start_location <= key_y1:
               continue

            if page_number == lineitems_end_page_location and ( key_y1 >= (lineitems_end_location-lineitem_end_location_margin) \
               and key_y1 <= (lineitems_end_location+lineitem_end_location_margin) ):
               if len(line_item_collector) > 0 :
                  list_of_line_items.append(line_item_collector)
                  line_item_collector = {}   

               # Flush the contents of list_of_mapdata
               one_line_item_collector = {}
               for counter, one_mapdata in enumerate(list_of_mapdata):
                  # Just copy the one_mapdata row to the collector
                  for column_name in one_mapdata:
                     text = one_line_item_collector.get(column_name)
                     if text == None:
                        text = one_mapdata[column_name]
                     else:
                        text = text + "\n" + one_mapdata[column_name]
                     one_line_item_collector[column_name] = text 
               if len(one_line_item_collector) > 0 :
                  list_of_line_items.append(one_line_item_collector)
               del list_of_mapdata[:]                                 
               break

            textboxes_at_y1 = rows_of_y1_textboxes[key_y1]

            one_row_of_line_item = {} 
            current_column_index = 0

            for key_x1 in list(textboxes_at_y1):

               textbox_at_y1_x1 = textboxes_at_y1[key_x1]    

               if len(textbox_at_y1_x1.text.strip()) == 0:
                  continue

               found_column = False

               if has_vertical_lines == True:
                  nearest_x0 = -1
                  nearest_x1 = -1

                  rows_of_vertical_lines = container_instance.pagewise_rows_of_vertical_lines[page_number]
                  for key_x in list(rows_of_vertical_lines):
                     lines_at_x = rows_of_vertical_lines[key_x]
                     for key_y0 in list(lines_at_x):
                        line_at_x_y0 = lines_at_x[key_y0]

                        # Check if vertical_line_value y0 and y1 is in between text y0 and y1
                        if line_at_x_y0.y0 <= textbox_at_y1_x1.y0 and ( line_at_x_y0.y1 >= textbox_at_y1_x1.y1 or \
                           (line_at_x_y0.y1 >= textbox_at_y1_x1.y0 and line_at_x_y0.y1 <= textbox_at_y1_x1.y1)):
                           if nearest_x0 == -1:
                              if key_x <= textbox_at_y1_x1.x0:
                                 nearest_x0 = key_x
                           else:
                              if key_x <= textbox_at_y1_x1.x0 and key_x > nearest_x0:
                                 nearest_x0 = key_x
                           if nearest_x1 == -1:
                              if key_x > textbox_at_y1_x1.x1:
                                 nearest_x1 = key_x
                           else:
                              if key_x <= textbox_at_y1_x1.x1 and key_x > nearest_x1:
                                 nearest_x1 = key_x

                  column_name_to_add = ""
                  text_to_add_to_column = ""
                  logger.debug('NEAREST ' + textbox_at_y1_x1.text + ' x0=' + str(nearest_x0) + ' x1=' + str(nearest_x1))
                  if nearest_x0 != -1 and nearest_x1 != -1 :
                     for column_name, textbox in dict_column_text_widths.items():
                        if textbox.x0 >= nearest_x0 and textbox.x1 <= nearest_x1:
                           column_name_to_add = column_name
                           text_to_add_to_column = textbox_at_y1_x1.text
                           found_column = True
                           break
                  elif nearest_x1 != -1:
                     first_column_name = list_of_column_information[0].column_name
                     second_column_name = list_of_column_information[1].column_name
                     first_textbox = dict_column_text_widths[first_column_name]
                     second_textbox = dict_column_text_widths[second_column_name]
                     if nearest_x1 >= first_textbox.x1 and nearest_x1 <= second_textbox.x1:
                        column_name_to_add = first_column_name
                        text_to_add_to_column = textbox_at_y1_x1.text
                        found_column = True
                  logger.debug('TEXT = ' + text_to_add_to_column + ' COLUMN = ' + column_name_to_add)                        
                  if found_column == True:
                     text = one_row_of_line_item.get(column_name_to_add)
                     if text == None:
                        text = text_to_add_to_column
                     else:
                        text = text + "\n" + text_to_add_to_column
                     one_row_of_line_item[column_name_to_add] = text     
               
               # Try the bucketizing algorithm
               if found_column == False:
                  counter = current_column_index
                  while counter < len(list_of_column_information):
                     found_column = False                     
                     column = list_of_column_information[counter]
                     column_textbox = dict_column_text_widths[column.name]
                     if column.alignment == "left":
                        x_start = column_textbox.x0 - alignment_margin
                        x_end = column_textbox.x0 + alignment_margin
                        if textbox_at_y1_x1.x0 >= x_start and textbox_at_y1_x1.x0 <= x_end:
                           found_column = True
                     elif column.alignment == "right":
                        x_start = column_textbox.x1 - alignment_margin
                        x_end = column_textbox.x1 + alignment_margin
                        if textbox_at_y1_x1.x1 >= x_start and textbox_at_y1_x1.x1 <= x_end:
                           found_column = True                           
                     elif column.alignment == "center":
                        if textbox_at_y1_x1.x0 >= column_textbox.x0 and textbox_at_y1_x1.x0 <= column_textbox.x1 or \
                           textbox_at_y1_x1.x1 >= column_textbox.x0 and textbox_at_y1_x1.x1 <= column_textbox.x1:
                           found_column = True
                        elif textbox_at_y1_x1.x0 < column_textbox.x0 and textbox_at_y1_x1.x1 > column_textbox.x1:
                           found_column = True
                     else:
                        logger.error("ERROR!! Unsupported alignment type " + column.alignment)                        
                        return {}

                     if found_column == True:
                        text = one_row_of_line_item.get(column.name)
                        if text == None:
                           text = textbox_at_y1_x1.text
                        else:
                           text = text + "\n" + textbox_at_y1_x1.text
                        one_row_of_line_item[column.name] = text   
                        current_column_index = counter + 1
                        break                       

                     counter +=1 

               if found_column == False:
                  logger.warn("WARNING! Trying to fit since could not find column for text |" + textbox_at_y1_x1.text + "|")
                  counter = 0
                  while counter < len(list_of_column_information):
                     column = list_of_column_information[counter]
                     column_textbox = dict_column_text_widths[column.name]
                     if (textbox_at_y1_x1.x0 >= column_textbox.x0 and textbox_at_y1_x1.x0 <= column_textbox.x1) or \
                        (textbox_at_y1_x1.x0 <= column_textbox.x0):
                        logger.debug("Found column |" + column.name + "| for text |" + textbox_at_y1_x1.text + "|")
                        text = one_row_of_line_item.get(column.name)
                        if text == None:
                           text = textbox_at_y1_x1.text
                        else:
                           text = text + "\n" + textbox_at_y1_x1.text
                        one_row_of_line_item[column.name] = text                         
                        break
                     counter += 1

            if has_horizontal_lines == False:

               # if One Row has all the row_start columns
               found_all_row_start_columns = True
               for column in list_of_column_information:
                  if column.row_start == True and one_row_of_line_item.get(column.name) == None:
                        found_all_row_start_columns = False
                        break    

               if found_all_row_start_columns == True:

                  # Flush the contents of list_of_mapdata
                  one_line_item_collector = {}
                  for counter, one_mapdata in enumerate(list_of_mapdata):
                     if counter <= line_start_index :
                        # Just copy the one_mapdata row to the collector
                        for column_name in one_mapdata:
                           text = one_line_item_collector.get(column_name)
                           if text == None:
                              text = one_mapdata[column_name]
                           else:
                              text = text + "\n" + one_mapdata[column_name]
                           one_line_item_collector[column_name] = text 
                  if len(one_line_item_collector) > 0 :
                     list_of_line_items.append(one_line_item_collector)
                  del list_of_mapdata[0:line_start_index+1]

                  # Add the new row to list_of_mapdata
                  list_of_mapdata.append(deepcopy(one_row_of_line_item))
                  
                  # Remember till where the list has to be flushed
                  line_start_index = len(list_of_mapdata) - 1

                  # Clear the map status
                  for column_name in map_row_start_col_collection_status:
                     map_row_start_col_collection_status[column_name] = 0

               else:

                  # Is close to previous 
                  if previous_key_y1 != -1 and abs(key_y1-previous_key_y1) < lineitem_columns_closeness:

                     # Add the new row to the list
                     list_of_mapdata.append(deepcopy(one_row_of_line_item))

                     # Set what all columns were found
                     for column_name in one_row_of_line_item:
                        map_row_start_col_collection_status[column_name] = 1

                     # Now if found all row_start columns
                     found_all_row_start = True
                     for column_name in map_row_start_col_collection_status:
                        if map_row_start_col_collection_status[column_name] == 0:
                           found_all_row_start = False
                           break

                     # If all row_start found
                     if found_all_row_start == True:
                        # Flush the contents of list_of_mapdata

                        one_line_item_collector = {}
                        for counter, one_mapdata in enumerate(list_of_mapdata):
                           if counter < line_start_index :
                              # Just copy the one_mapdata row to the collector
                              for column_name in one_mapdata:
                                 text = one_line_item_collector.get(column_name)
                                 if text == None:
                                    text = one_mapdata[column_name]
                                 else:
                                    text = text + "\n" + one_mapdata[column_name]
                                 one_line_item_collector[column_name] = text 
                        if len(one_line_item_collector) > 0 :
                           list_of_line_items.append(one_line_item_collector)
                        del list_of_mapdata[0:line_start_index]

                        # Remember till where the list has to be flushed
                        line_start_index = len(list_of_mapdata)
                        
                     else:
                        # Not all row_start found
                        pass

                  else:
                     # Not close to previous 

                     # First clear the map status
                     for column_name in map_row_start_col_collection_status:
                        map_row_start_col_collection_status[column_name] = 0

                     # Set what all columns were found
                     for column_name in one_row_of_line_item:
                        map_row_start_col_collection_status[column_name] = 1

                     # Add the new row to the list
                     list_of_mapdata.append(deepcopy(one_row_of_line_item))

                     line_start_index = len(list_of_mapdata) -1 

            else:

               # Just copy the current row to the collector
               for column_name in one_row_of_line_item:
                  text = line_item_collector.get(column_name)
                  if text == None:
                     text = one_row_of_line_item[column_name]
                  else:
                     text = text + "\n" + one_row_of_line_item[column_name]
                  line_item_collector[column_name] = text 
     
               # If the next text line has a horizontal line, complete a line item
               if (row_number+1) < len(list_reversed_rows_of_y1_textboxes):
                  next_key_y1 = list_reversed_rows_of_y1_textboxes[row_number+1]
                  horizontal_lines = container_instance.pagewise_rows_of_horizontal_lines[page_number]
                  for horizontal_line in horizontal_lines:
                     if horizontal_line >= next_key_y1 and horizontal_line <= key_y1 and abs(next_key_y1-key_y1) >= horizontal_line_margin:
                        if len(line_item_collector) > 0 :
                           list_of_line_items.append(line_item_collector)
                           line_item_collector = {}    
                        break 

            previous_key_y1 = key_y1                                   

      return list_of_line_items

   def get_regex_lineitem_header_location (self, lineitem_header_regex):

      container_instance = ObjectLayoutContainer.getInstance()

      if container_instance.pdf_parsed == False :
         return -1, -1

      lineitems_start_location = -1
      lineitems_start_page_location = -1

      for index, rows_of_y1_textboxes in enumerate(container_instance.pagewise_rows_of_y1_textboxes):
         for key_y1 in list(reversed(rows_of_y1_textboxes)):  
            textboxes_at_y1 = rows_of_y1_textboxes[key_y1]
            for key_x1 in list(textboxes_at_y1):
               textbox_at_y1_x1 = textboxes_at_y1[key_x1]
               text_to_compare = textbox_at_y1_x1.text
               regex_search = re.search(lineitem_header_regex, text_to_compare) 
               if regex_search is not None:
                  lineitems_start_location = key_y1 
                  lineitems_start_page_location = index
                  return lineitems_start_page_location, lineitems_start_location

      return lineitems_start_page_location, lineitems_start_location          

   def get_regex_lineitems(self, regex_lines, list_of_columns, lineitems_start_page_location, lineitems_start_location, \
      lineitems_end_page_location, lineitems_end_location):

      container_instance = ObjectLayoutContainer.getInstance()

      if container_instance.pdf_parsed == False :
         return []

      list_of_line_items = []
        
      prev_one_row_data = {}
      last_index = 1
      
      # Traverse all the pages
      for page_number, rows_of_y1_textboxes in enumerate(container_instance.pagewise_rows_of_y1_textboxes):

         # Look at only pages from start to end. Others discard
         if page_number < lineitems_start_page_location:
            continue
            
         if page_number > lineitems_end_page_location:
            break

         # Traverse through all the rows in the current page
         list_reversed_rows_of_y1_textboxes = list(reversed(rows_of_y1_textboxes))
         for key_y1 in list_reversed_rows_of_y1_textboxes:    

            if page_number == lineitems_start_page_location and lineitems_start_location <= key_y1:
               continue

            if page_number == lineitems_end_page_location and ( key_y1 >= (lineitems_end_location-5) and key_y1 <= (lineitems_end_location+5) ):
               break

            textboxes_at_y1 = rows_of_y1_textboxes[key_y1]
            for key_x1 in list(textboxes_at_y1):
               textbox_at_y1_x1 = textboxes_at_y1[key_x1]              
               text_to_compare = textbox_at_y1_x1.text
               regex_search = re.search(regex_lines[0], text_to_compare) 
               if regex_search is not None:
                  last_index = 1
                  if len(prev_one_row_data) > 0 :
                     list_of_line_items.append(prev_one_row_data)
                     prev_one_row_data = {} 
                  for column_name in list_of_columns:
                     try:
                        column_value = regex_search.group(column_name)
                        prev_one_row_data[column_name] = column_value                         
                     except IndexError:
                        pass
               else:
                  if last_index < len(regex_lines):
                        regex_search_next = re.search(regex_lines[last_index], text_to_compare) 
                        if regex_search_next is not None:
                           for column_name in list_of_columns:
                              try:
                                    column_value = regex_search_next.group(column_name)
                                    text = prev_one_row_data.get(column_name)
                                    if text == None:
                                       text = column_value
                                    else:
                                       text = text + "\n" + column_value
                                    prev_one_row_data[column_name] = text 
                              except IndexError:
                                    pass
                           last_index = last_index + 1
               
      if len(prev_one_row_data) > 0 :
         list_of_line_items.append(prev_one_row_data)
         prev_one_row_data = {}             
      
      return list_of_line_items


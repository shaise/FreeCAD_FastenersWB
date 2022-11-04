# -*- coding: utf-8 -*-
###############################################################################
#
#   Original code by:
#   FreeCADTools 
#
###############################################################################
import FreeCADGui

# Converts text to Dative case form for comptable with "Add " preffix
# Used in FSScrewCommand class (FastnersCmd.py)
# More information about Dative case at en.wikipedia.org/wiki/Dative_case
def ToDativeCase(s):
  if FreeCADGui.getLocale() == "Russian":
     #t = s
     s = s + " "
     s = s.replace("ба ", "бу ") # шайба
     s = s.replace("ба,", "бу,")
     s = s.replace("ба-", "бу-")
     s = s.replace("ка ", "ку ") # шпилька, гайка
     s = s.replace("вая ", "вую ") # резьбовая
     s = s.replace("аяся ", "уюся ") # самокотнрящаяся
     s = s.replace("ская ", "скую ")
     s = s.replace("ая серия", "ой серии") # крупная/нормальная/мелкая серия
     s = s.replace("ная ", "ную ")
     s = s.replace("ая,", "ую,") # резьбовая
     s = s.replace("ая ", "ую ")
     # lower case for all string instead abbriviatures like GOST, DIN, ISO etc.
     s = s.replace("Ш", "ш")
     s = s.replace("К", "к")
     s = s.replace("В", "в")
     s = s.replace("М", "м")
     s = s.replace("П", "п")
     s = s.replace("Д", "д")
     s = s.replace("Б", "б")
     s = s.replace("Н", "н")
     s = s.replace("Осо", "осо")
     s = s.replace("Ре", "ре")
     s = s.replace("Га", "га")
     s = s.replace("типа н", "типа Н")
     #print("'Добавить "+t+"' -> 'Добавить "+s+"'")
  return s

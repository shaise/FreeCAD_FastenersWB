# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'screw_selector.ui'
#
# Created: Sat Aug  3 23:19:38 2013
#      by: PyQt4 UI code generator 4.9.3
#
# WARNING! All changes made in this file will be lost!



"""
Macro to generate screws with FreeCAD.
Version 1.4 from 1st of September 2013
Version 1.5 from 23rd of December 2013
Corrected hex-heads above M12 not done.
Version 1.6 from 15th of March 2014
Added PySide support
Version 1.7 from April 2014
fixed bool type error. (int is not anymore accepted at linux)
fixed starting point of real thread at some screw types.
***************************************************************************
*   Copyright (c) 2013 Ulrich Brammer <ulrich1a[at]users.sourceforge.net> *
*                                                                         *
*   This file is a supplement to the FreeCAD CAx development system.      *
*                                                                         *
*   This program is free software; you can redistribute it and/or modify  *
*   it under the terms of the GNU Lesser General Public License (LGPL)    *
*   as published by the Free Software Foundation; either version 2 of     *
*   the License, or (at your option) any later version.                   *
*   for detail see the LICENCE text file.                                 *
*                                                                         *
*   This software is distributed in the hope that it will be useful,      *
*   but WITHOUT ANY WARRANTY; without even the implied warranty of        *
*   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the         *
*   GNU Library General Public License for more details.                  *
*                                                                         *
*   You should have received a copy of the GNU Library General Public     *
*   License along with this macro; if not, write to the Free Software     *
*   Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  *
*   USA                                                                   *
*                                                                         *
***************************************************************************
"""

__author__ = "Ulrich Brammer <ulrich1a@users.sourceforge.net>"





import FreeCAD, Part, math
from FreeCAD import Base
import DraftVecUtils

try:
   #from PyQt4 import QtCore, QtGui
   from PySide import QtCore, QtGui
   FreeCAD.Console.PrintLog("PySyde is used" + "\n")
except:
   #from PySide import QtCore, QtGui
   FreeCAD.Console.PrintLog("PyQt4 is needed" + "\n")
   from PyQt4 import QtCore, QtGui


DEBUG = True # set to True to show debug messages


# Diameters included in this library/macro
# The ISO-standards may include more diameters!
# Dictionary used for user messages
standard_diameters = {
   'ISO4017': ('M1.6', 'M36'), # ISO 4017 Hex-head-screw
   'ISO4014': ('M4',   'M30'), # ISO 4014 Hex-head-bolt
   'EN1662':  ('M5',   'M16'), # EN 1662 Hexagon bolts with flange, small series
   'EN1665':  ('M5',   'M20'), # EN 1665 Hexagon bolts with flange, heavy series
   'ISO4762': ('M1.6', 'M36'), # ISO 4762 Hexagon socket head cap screws
   'ISO2009': ('M1.6', 'M10'), # ISO 2009 Slotted countersunk flat head screws
   'ISO2010': ('M1.6', 'M10'), # ISO 2010 Slotted raised countersunk head screws
   'ISO1580': ('M1.6', 'M10'), # ISO 1580 Slotted pan head screws
   'ISO7045': ('M1.6', 'M10'), # ISO 7045 Pan head screws type H cross recess
   'ISO7046': ('M1.6', 'M10'),
   'ISO7047': ('M1.6', 'M10'),
   'ISO1207': ('M3',   'M10'), # ISO 1207 Slotted cheese head screws
   'ISO7048': ('M2.5', 'M8'),  # ISO 7048 Cross-recessed cheese head screws with type H cross recess
   'ISO7380': ('M3',   'M12'), # ISO 7380 Hexagon socket button head screws
   'ISO10642':('M3',   'M20'), # ISO 10642 Hexagon socket countersunk head screws
   'ISO14579':('M2',   'M20'), # ISO 14579 Hexalobular socket head cap screws
   'ISO14580':('M2',   'M10'), # ISO 14580 Hexalobular socket cheese head screws
   'ISO14583':('M2',   'M10'), # ISO 14583 Hexalobular socket pan head screws  
   'ISO7089': ('M1.6', 'M36')} # Washer

# ISO 4017 Hex-head-screw
#           P,    c,  dw,    e,     k,   r,   s
iso4017head={
   'M1.6':(0.35, 0.2, 2.3,  3.4,   1.1, 0.1,  3.2),
   'M2':  (0.40, 0.2, 3.0,  4.4,   1.4, 0.1,  4.0),
   'M2.5':(0.45, 0.2, 4.0,  5.5,   1.7, 0.1,  5.0),
   'M3':  (0.5,  0.2, 4.6,  6.1,   2.0, 0.1,  5.5),
   'M4':  (0.7,  0.2, 5.9,  7.7,   3.5, 0.2,  7.0), 
   'M5':  (0.8,  0.2, 6.9,  8.9,   3.5, 0.2,  8.0),
	'M6':  (1.0,  0.2, 8.9,  11.05, 4.0, 0.25, 10.0),
	'M8':  (1.25, 0.3, 11.7, 14.5,  5.3, 0.25, 13.0),
	'M10': (1.50, 0.3, 14.7, 17.9,  6.4, 0.4,  16.0),
   'M12': (1.75, 0.3, 16.7, 20.1,  7.5, 0.6,  18.0),
   'M14': (2.00, 0.3, 20.5, 24.5,  8.8, 0.6,  22.0),
   'M16': (2.00, 0.4, 22.4, 26.9, 10.0, 0.6,  24.0),
   'M20': (2.50, 0.4, 28.2, 33.7, 12.5, 0.8,  30.0),
   'M24': (3.00, 0.4, 33.7, 40.1, 15.0, 0.8,  36.0),
   'M27': (3.00, 0.4, 38.0, 45.2, 17.0, 1.0,  41.0),
   'M30': (3.50, 0.4, 42.8, 50.9, 18.7, 1.0,  46.0), #dw not in class A, e not in class A
   'M36': (4.00, 0.4, 51.2, 61.0, 22.5, 1.0,  55.0), #dw not in class A, e not in class A
   'M42': (4.50, 0.7, 60.0, 71.3, 26.0, 1.2,  65.0),
   'M48': (5.00, 0.7, 69.5, 82.6, 30.0, 1.6,  75.0),
   'M56': (5.50, 0.7, 78.7, 93.6, 35.0, 2.0,  85.0),
   'M64': (6.00, 0.7, 88.2,104.9, 40.0, 2.0,  95.0)
   } 


iso4017length = {
   '2': ( 1.8,  2.2),
   '3': ( 2.8,  3.2),
   '4': ( 3.76, 4.24),
   '5': ( 4.76, 5.24),
   '6': ( 5.76, 6.24),
   '8': ( 7.71, 8.29),
   '10':( 9.71, 10.29),
   '12':(11.65, 12.35),
   '14':(13.65, 14.35),
   '16':(15.65, 16.35),
   '20':(19.58, 20.42),
   '25':(24.58, 25.42),
   '30':(29.58, 30.42),
   '35':(34.5,  35.5),
   '40':(39.5,  40.5),
   '45':(44.5,  45.5),
   '50':(49.5,  50.5),
   '55':(54.4, 55.6),
   '60':(59.4, 60.6),
   '65':(64.4, 65.6),
   '70':(69.4, 70.6),
   '80':(79.4, 80.6),
   '100':(99.3, 100.7),
   '110':(109.3, 110.7),
   '120':(119.3, 120.7),
   '130':(129.2, 130.8),
   '140':(139.2, 130.8),
   '150':(149.2, 150.8),
   '160':(159.2, 160.8),
   '180':(179.2, 180.8),
   '200':(199.1, 200.9)
         }

# range of typical srew lengths
#    min_length,  max_length
iso4017range = {
   'M1.6':  ('2', '16'),
   'M2':  ('4', '20'),
   'M2.5':  ('5', '25'),
   'M3':  ('5', '30'),
   'M4':  ('6', '40'),
   'M5':  ('8', '50'),
   'M6':  ('12', '60'),
   'M8': ('16', '80'),
   'M10':('20', '100'),
   'M12':('25','120'),
   'M14':('25','100'), # www.agriti.com
   'M16':('30','150'),
   'M20':('40','160'),
   'M24':('50','180'),
   'M27':('50','100'),
   'M30':('60','200'), 
   'M36':('70','200'),
   'M42':('70','200'),
   'M48':('100','200'),
   'M56':('110','200'),
   'M64':('120','200')
   } 

# ISO 4014 Hex-head-bolt
#          P,   b1,   b2,   b3,   c,  dw,    e,     k,   r,   s
iso4014head={
   'M4': (0.70, 14.0,  0.0,  0.0, 0.2, 5.9,  7.7,   3.5, 0.2, 7.0),
   'M5': (0.80, 16.0,  0.0,  0.0, 0.2, 6.9,  8.9,   3.5, 0.2, 8.0), 
	'M6': (1.00, 18.0, 24.0, 37.0, 0.2, 8.9,  11.05, 4.0, 0.25, 10.0),
	'M8': (1.25, 22.0, 28.0, 41.0, 0.3, 11.7, 14.5,  5.3, 0.4, 13.0),
	'M10':(1.50, 26.0, 32.0, 45.0, 0.3, 14.7, 17.9,  6.4, 0.4, 16.0),
   'M12':(1.75, 30.0, 36.0, 49.0, 0.3, 16.7, 20.1,  7.5, 0.6, 18.0),
   'M14':(2.00, 34.0, 40.0,  0.0, 0.3, 20.5, 24.5,  8.8, 0.6, 22.0),
   'M16':(2.00, 38.0, 44.0, 57.0, 0.4, 22.4, 26.9, 10.0, 0.6, 24.0),
   'M20':(2.50, 46.0, 52.0, 65.0, 0.4, 28.2, 33.7, 12.5, 0.8, 30.0),
   'M24':(3.00, 54.0, 60.0, 73.0, 0.4, 33.7, 40.1, 15.0, 0.8, 36.0),
   'M27':(3.00, 60.0, 66.0, 79.0, 0.4, 38.0, 45.2, 17.0, 1.0, 41.0),
   'M30':(3.50, 66.0, 72.0, 85.0, 0.4, 42.8, 50.9, 18.7, 1.0, 46.0)} #dw not in class A, e not in class A
   #'M36':(   , 0.4, 51.2, 61.0, 22.5, 55.0)} #dw not in class A, e not in class A


iso4014length = {
   '25':(24.58, 25.42),
   '30':(29.58, 30.42),
   '35':(34.5,  35.5),
   '40':(39.5,  40.5),
   '45':(44.5,  45.5),
   '50':(49.5,  50.5),
   '55':(54.4, 55.6),
   '60':(59.4, 60.6),
   '65':(64.4, 65.6),
   '70':(69.4, 70.6),
   '80':(79.4, 80.6),
   '100':(99.3, 100.7),
   '110':(109.3, 110.7),
   '120':(119.3, 120.7),
   '130':(129.2, 130.8),
   '140':(139.2, 130.8),
   '150':(149.2, 150.8),
   '160':(159.2, 160.8),
   '180':(179.2, 180.8),
   '200':(199.1, 200.9),
   '220':(219.1, 220.9)
         }

# range of typical srew lengths
#    min_length,  max_length
iso4014range = {
   'M4':  ('25', '50'),
   'M5':  ('25', '50'),
   'M6':  ('30', '130'),
   'M8': ('30', '180'),
   'M10':('35', '150'),
   'M12':('50','150'),
   'M14':('50','160'),
   'M16':('55','200'),
   'M20':('60','300'),
   'M24':('80','220'),
   'M27':('90', '220'),
   'M30':('90', '220')}


# EN 1662 Hexagon bolts with flange, small series
#          P,   b0,    b1,   b2,   b3,   c,  dc,    dw,    e,     k,   kw,  lf,  r1,   s
en1662def={
   'M5': (0.80, 25.0, 16.0,  0.0,  0.0, 1.0, 11.4,  9.4,  7.59,  5.6, 2.3, 1.4, 0.2, 7.0), 
	'M6': (1.00, 30.0, 18.0,  0.0,  0.0, 1.1, 13.6, 11.6,  8.71,  6.9, 2.9, 1.6, 0.25, 8.0),
	'M8': (1.25, 35.0, 22.0, 28.0,  0.0, 1.2, 17.0, 14.9, 10.95,  8.5, 3.8, 2.1, 0.4, 10.0),
	'M10':(1.50, 40.0, 26.0, 32.0,  0.0, 1.5, 20.8, 18.7, 14.26,  9.7, 4.3, 2.1, 0.4, 13.0),
   'M12':(1.75, 45.0, 30.0, 36.0,  0.0, 1.8, 24.7, 22.5, 17.62, 12.1, 5.4, 2.1, 0.6, 16.0),
   'M14':(2.00, 50.0, 34.0, 40.0,  0.0, 2.1, 28.6, 26.4, 19.86, 12.9, 5.6, 2.1, 0.6, 18.0),
   'M16':(2.00, 55.0, 38.0, 44.0, 57.0, 2.4, 32.8, 30.6, 23.15, 15.2, 6.8, 3.2, 0.6, 21.0)}


# range of typical srew lengths
#    min_length,  max_length
en1662range = {
   'M5': ('10', '50'),
   'M6': ('12', '60'),
   'M8': ('16', '80'),
   'M10':('20','100'),
   'M12':('25','120'),
   'M14':('30','140'), 
   'M16':('35','160')
   } 

en1662length = {
   '10':( 9.71, 10.29),
   '12':(11.65, 12.35),
   '16':(15.65, 16.35),
   '20':(19.58, 20.42),
   '25':(24.58, 25.42),
   '30':(29.58, 30.42),
   '35':(34.5,  35.5),
   '40':(39.5,  40.5),
   '45':(44.5,  45.5),
   '50':(49.5,  50.5),
   '55':(54.4, 55.6),
   '60':(59.4, 60.6),
   '65':(64.4, 65.6),
   '70':(69.4, 70.6),
   '80':(79.4, 80.6),
   '90':(89.3, 90.7),
   '100':(99.3, 100.7),
   '110':(109.3, 110.7),
   '120':(119.3, 120.7),
   '130':(129.2, 130.8),
   '140':(139.2, 130.8),
   '150':(149.2, 150.8),
   '160':(159.2, 160.8)
         }


# EN 1665 Hexagon bolts with flange, heavy series
#          P,    b0,  b1,   b2,   b3,   c,  dc,    dw,    e,     k,   kw,  lf,  r1,   s
en1665def={
   'M5': (0.80, 25.0, 16.0,  0.0,  0.0, 1.0, 11.8,  9.8,  8.71,  5.8, 2.6, 1.4, 0.2,  8.0), 
	'M6': (1.00, 30.0, 18.0,  0.0,  0.0, 1.1, 14.2, 12.2, 10.95,  6.6, 3.0, 1.6, 0.25,10.0),
	'M8': (1.25, 35.0, 22.0, 28.0,  0.0, 1.2, 18.0, 15.8, 14.26,  8.1, 3.9, 2.1, 0.4, 13.0),
	'M10':(1.50, 40.0, 26.0, 32.0,  0.0, 1.5, 22.3, 19.6, 17.62, 10.4, 4.1, 2.1, 0.4, 16.0),
   'M12':(1.75, 45.0, 30.0, 36.0,  0.0, 1.8, 26.6, 23.8, 19.86, 11.8, 5.6, 2.1, 0.6, 18.0),
   'M14':(2.00, 50.0, 34.0, 40.0,  0.0, 2.1, 30.5, 27.6, 23.15, 13.7, 6.5, 2.1, 0.6, 21.0),
   'M16':(2.00, 55.0, 38.0, 44.0, 57.0, 2.4, 35.0, 31.9, 26.51, 15.4, 7.3, 3.2, 0.6, 24.0),
   'M20':(2.50, 65.0, 46.0, 52.0, 65.0, 3.0, 43.0, 39.9, 33.23, 18.9, 8.9, 4.2, 0.8, 30.0)}


# range of typical srew lengths
#    min_length,  max_length
en1665range = {
   'M5': ('10', '50'),
   'M6': ('12', '60'),
   'M8': ('16', '80'),
   'M10':('20','100'),
   'M12':('25','120'),
   'M14':('30','140'), 
   'M16':('35','160'),
   'M20':('65','200')
   } 

en1665length = {
   '10':( 9.71, 10.29),
   '12':(11.65, 12.35),
   '16':(15.65, 16.35),
   '20':(19.58, 20.42),
   '25':(24.58, 25.42),
   '30':(29.58, 30.42),
   '35':(34.5,  35.5),
   '40':(39.5,  40.5),
   '45':(44.5,  45.5),
   '50':(49.5,  50.5),
   '55':(54.4, 55.6),
   '60':(59.4, 60.6),
   '65':(64.4, 65.6),
   '70':(69.4, 70.6),
   '80':(79.4, 80.6),
   '90':(89.3, 90.7),
   '100':(99.3, 100.7),
   '110':(109.3, 110.7),
   '120':(119.3, 120.7),
   '130':(129.2, 130.8),
   '140':(139.2, 130.8),
   '150':(149.2, 150.8),
   '160':(159.2, 160.8),
   '180':(179.2, 180.8),
   '200':(199.1, 200.9)
         }



# ISO 1207 definitions Class A, Slotted cheese head screws
#          P,     a,   b,   dk,  dk_mean, da,  k,  n_min, r, t_min, x
iso1207def={
   'M1.6':(0.35, 0.7, 25.0,  3.0,  2.9,  2.0, 1.1, 0.46, 0.1, 0.45, 0.9),
   'M2':  (0.40, 0.8, 25.0,  3.8,  3.7,  2.6, 1.4, 0.56, 0.1, 0.6, 1.0),
   'M2.5':(0.45, 0.9, 25.0,  4.5,  4.4,  3.1, 1.8, 0.66, 0.1, 0.7, 1.1),
   'M3':  (0.50, 1.0, 25.0,  5.5,  5.4,  3.6, 2.0, 0.86, 0.1, 0.85, 1.25),
   'M3.5':(0.60, 1.2, 38.0,  6.0,  5.9,  4.1, 2.4, 1.06, 0.1, 1.0, 1.5),
   'M4':  (0.70, 1.4, 38.0,  7.0,  6.9,  4.7, 2.6, 1.26, 0.2, 1.1, 1.75),
   'M5':  (0.80, 1.6, 38.0,  8.5,  8.4,  5.7, 3.3, 1.26, 0.2, 1.3, 2.0),
   'M6':  (1.00, 2.0, 38.0, 10.0,  9.9,  6.8, 3.9, 1.66, 0.25,1.6, 2.5),
   'M8':  (1.25, 2.5, 38.0, 13.0, 12.85, 9.2, 5.0, 2.06, 0.4, 2.0, 3.2),
   'M10': (1.50, 3.0, 38.0, 16.0, 15.85, 11.2,6.0, 2.56, 0.4, 2.4, 3.8)}

# range of typical srew lengths
#    min_length,  max_length
iso1207range = {
   'M1.6':('2', '16'),
   'M2':  ('3', '20'),
   'M2.5':('3', '25'),
   'M3':  ('4', '30'),
   'M3.5':('5', '35'),
   'M4':  ('5', '40'),
   'M5':  ('6', '50'),
   'M6':  ('8', '60'),
   'M8': ('10', '80'),
   'M10':('12', '80')}

# slotted cheese head screws
# nom length: l_min, l_max       
iso1207length = {
   '2': (1.8,  2.2),
   '3': ( 2.8,  3.2),
   '4': ( 3.76, 4.24),
   '5': ( 4.76, 5.24),
   '6': ( 5.76, 6.24),
   '8': ( 7.71, 8.29),
   '10':( 9.71, 10.29),
   '12':(11.65, 12.35),
   '14':(13.65, 14.35),
   '16':(15.65, 16.35),
   '20':(19.58, 20.42),
   '25':(24.58, 25.42),
   '30':(29.58, 30.42),
   '35':(34.5,  35.5),
   '40':(39.5,  40.5),
   '45':(44.5,  45.5),
   '50':(49.5,  50.5),
   '55':(54.05, 55.95),
   '60':(59.05, 60.95),
   '65':(64.05, 65.95),
   '70':(69.05, 70.95),
   '75':(74.05, 75.95),
   '80':(79.05, 80.95)
      }


# ISO 14580 definitions , Hexalobular socket cheese head screws
#          P,     a,   b,   dk,  dk_mean, da,  k,  n_min, r, t_min, x
#           tt,    k,    A,  t_mean
iso14580def={
   'M2':  ('T6',  1.55, 1.75, 0.8),
   'M2.5':('T8',  1.85, 2.40, 0.9),
   'M3':  ('T10', 2.40, 2.80, 1.2),
   'M3.5':('T15', 2.60, 3.35, 1.3),
   'M4':  ('T20', 3.10, 3.95, 1.5),
   'M5':  ('T25', 3.65, 4.50, 1.7),
   'M6':  ('T30', 4.40, 5.60, 2.1),
   'M8':  ('T45', 5.80, 7.95, 2.9),
   'M10': ('T50', 6.90, 8.95, 3.3)}
   
# range of typical srew lengths
#    min_length,  max_length
# iso14580range = iso1207range

# nom length: l_min, l_max       
iso14580length = {
   '3': ( 2.8,  3.2),
   '4': ( 3.76, 4.24),
   '5': ( 4.76, 5.24),
   '6': ( 5.76, 6.24),
   '8': ( 7.71, 8.29),
   '10':( 9.71, 10.29),
   '12':(11.65, 12.35),
   '14':(13.65, 14.35),
   '16':(15.65, 16.35),
   '20':(19.58, 20.42),
   '25':(24.58, 25.42),
   '30':(29.58, 30.42),
   '35':(34.5,  35.5),
   '40':(39.5,  40.5),
   '45':(44.5,  45.5),
   '50':(49.5,  50.5),
   '55':(54.05, 55.95),
   '60':(59.05, 60.95),
   '65':(64.05, 65.95),
   '70':(69.05, 70.95),
   '75':(74.05, 75.95),
   '80':(79.05, 80.95)
      }



# ISO 7048 definitions Class A, 
# Cross-recessed cheese head screws with type H or Z cross recess
#          P,     a,   b,   dk,  dk_mean, da,  k,   r,   x, cT,   mH,   mZ 
iso7048def={
   'M2.5':(0.45, 0.9, 25.0,  4.5,  4.4,  3.1, 1.8, 0.1, 1.1, '1', 2.7, 2.4),
   'M3':  (0.50, 1.0, 25.0,  5.5,  5.4,  3.6, 2.0, 0.1, 1.25,'2', 3.5, 3.5),
   'M3.5':(0.60, 1.2, 38.0,  6.0,  5.9,  4.1, 2.4, 0.1, 1.5, '2', 3.8, 3.7),
   'M4':  (0.70, 1.4, 38.0,  7.0,  6.9,  4.7, 2.6, 0.2, 1.75,'2', 4.1, 4.0),
   'M5':  (0.80, 1.6, 38.0,  8.5,  8.4,  5.7, 3.3, 0.2, 2.0, '2', 4.8, 4.6),
   'M6':  (1.00, 2.0, 38.0, 10.0,  9.9,  6.8, 3.9, 0.25,2.5, '3', 6.2, 6.1),
   'M8':  (1.25, 2.5, 38.0, 13.0, 12.85, 9.2, 5.0, 0.4, 3.2, '3', 7.7, 7.5)
   }

# range of typical srew lengths
#    min_length,  max_length
iso7048range = {
   'M2.5':('3', '25'),
   'M3':  ('4', '30'),
   'M3.5':('5', '35'),
   'M4':  ('5', '40'),
   'M5':  ('6', '50'),
   'M6':  ('8', '60'),
   'M8': ('10', '80')}

# nom length: l_min, l_max       
iso7048length = {
   '3': ( 2.8,  3.2),
   '4': ( 3.76, 4.24),
   '5': ( 4.76, 5.24),
   '6': ( 5.76, 6.24),
   '8': ( 7.71, 8.29),
   '10':( 9.71, 10.29),
   '12':(11.65, 12.35),
   '16':(15.65, 16.35),
   '20':(19.58, 20.42),
   '25':(24.58, 25.42),
   '30':(29.58, 30.42),
   '35':(34.5,  35.5),
   '40':(39.5,  40.5),
   '45':(44.5,  45.5),
   '50':(49.5,  50.5),
   '60':(59.05, 60.95),
   '70':(69.05, 70.95),
   '80':(79.05, 80.95)
      }


# Button Head Screw
# nom length: l_min, l_max       
iso7380length = {
   #'2.5':(2.3,  2.7),
   #'3': ( 2.8,  3.2),
   '4': ( 3.76, 4.24),
   '5': ( 4.76, 5.24),
   '6': ( 5.76, 6.24),
   '8': ( 7.71, 8.29),
   '10':( 9.71, 10.29),
   '12':(11.65, 12.35),
   '14':(13.65, 14.35),
   '16':(15.65, 16.35),
   '20':(19.58, 20.42),
   '25':(24.58, 25.42),
   '30':(29.58, 30.42),
   '35':(34.5,  35.5),
   '40':(39.5,  40.5),
   '45':(44.5,  45.5),
   '50':(49.5,  50.5),
   '55':(54.05, 55.95),
   '60':(59.05, 60.95)
      }

# ISO 7380 definitions Class A 
# http://www.agrati.com/it/unificati/it/gamma/unificati/home02.htm
#          P,     a,   da,   dk,  dk_mean,s_mean,t_min, r, k,   e,    w,  
iso7380def={
   'M3':  (0.50, 1.0,  3.6,  5.7,  5.5, 2.03, 1.04, 0.1, 1.65, 2.3,  0.2),
   'M4':  (0.70, 1.4,  4.7,  7.6,  7.4, 2.54, 1.30, 0.2, 2.20, 2.87, 0.3),
   'M5':  (0.80, 1.6,  5.7,  9.5,  9.3, 3.05, 1.56, 0.2, 2.75, 3.44, 0.38),
   'M6':  (1.00, 2.0,  6.8, 10.5, 10.3, 4.05, 2.08, 0.25,3.3,  4.58, 0.74),
   'M8':  (1.25, 2.5,  9.2, 14.0, 13.8, 5.05, 2.60, 0.4, 4.4,  5.72, 1.05),
   'M10': (1.50, 3.0, 11.2, 17.5, 17.3, 6.05, 3.12, 0.4, 5.5,  6.86, 1.45),
   'M12': (1.75, 3.5, 13.7, 21.0, 20.7, 8.06, 4.16, 0.6, 6.6,  9.15, 1.63),
   'M16': (1.75, 3.5, 18.2, 28.0, 27.8, 10.06,5.20, 0.6, 8.8,  9.15, 2.25)
   }

# range of typical srew lengths
#    min_length,  max_length
iso7380range = {
   'M3':  ('5', '25'),
   'M4':  ('5', '40'),
   'M5':  ('6', '40'),
   'M6':  ('8', '60'),
   'M8': ('10', '60'),
   'M10':('12', '60'),
   'M12':('16', '60'),
   'M16':('20', '60')}


L_iso2009length =['2.5','3','4','5','6','8','10','12','14','16','20', \
   '25','30','35','40','45','50','55','60','65','70','75','80'] 
# nom length: l_min, l_max       
iso2009length = {
   '2.5':(2.3,  2.7),
   '3': ( 2.8,  3.2),
   '4': ( 3.76, 4.24),
   '5': ( 4.76, 5.24),
   '6': ( 5.76, 6.24),
   '8': ( 7.71, 8.29),
   '10':( 9.71, 10.29),
   '12':(11.65, 12.35),
   '14':(13.65, 14.35),
   '16':(15.65, 16.35),
   '20':(19.58, 20.42),
   '25':(24.58, 25.42),
   '30':(29.58, 30.42),
   '35':(34.5,  35.5),
   '40':(39.5,  40.5),
   '45':(44.5,  45.5),
   '50':(49.5,  50.5),
   '55':(54.05, 55.95),
   '60':(59.05, 60.95),
   '65':(64.05, 65.95),
   '70':(69.05, 70.95),
   '75':(74.05, 75.95),
   '80':(79.05, 80.95)
      }


# ISO 2009 definitions Class A
#          P, a, b, dk_theo, dk_mean, k, n_min, r, t_mean, x
iso2009def={
   'M1.6':(0.35, 0.7, 25, 3.6, 2.8,  1.0,  0.46, 0.4, 0.4, 0.9),
   'M2':  (0.40, 0.8, 25, 4.4, 3.6,  1.2,  0.56, 0.5, 0.5, 1.0),
   'M2.5':(0.45, 0.9, 25, 5.5, 4.5,  1.5,  0.66, 0.6, 0.6, 1.1),
   'M3':  (0.50, 1.0, 25, 6.3, 5.3,  1.65, 0.86, 0.8, 0.7, 1.25),
   'M3.5':(0.60, 1.2, 38, 8.2, 7.1,  2.35, 1.06, 0.9, 1.0, 1.5),
   'M4':  (0.70, 1.4, 38, 9.4, 8.2,  2.7,  1.26, 1.0, 1.1, 1.75),
   'M5':  (0.80, 1.6, 38,10.4, 9.2,  2.7,  1.26, 1.3, 1.2, 2.0),
   'M6':  (1.00, 2.0, 38,12.6, 11.2, 3.3,  1.66, 1.5, 1.4, 2.5),
   'M8':  (1.25, 2.5, 38,17.3, 15.6, 4.65, 2.06, 2.0, 2.0, 3.2),
   'M10': (1.50, 3.0, 38,20.0, 18.1, 5.0,  2.56, 2.5, 2.3, 3.8)}
   
# range of typical srew lengths
#    min_length,  max_length
iso2009range = {
   'M1.6':('2.5', '16'),
   'M2':  ('3', '20'),
   'M2.5':('4', '25'),
   'M3':  ('5', '30'),
   'M3.5':('6', '35'),
   'M4':  ('6', '40'),
   'M5':  ('8', '50'),
   'M6':  ('8', '60'),
   'M8': ('10', '80'),
   'M10':('12', '80')}


# ISO 7046 definitions Class A
# ISO 7046 Countersunk flat head srews (common head style)
# with type H or type Z cross recess
# Parameters P, a, b, dk_theo, dk_mean, k, r, x to be read from iso2009def
# Length = iso7045length
#          cT,   mH,   mZ 
iso7046def={
   'M1.6':('0', 1.6, 1.6),
   'M2':  ('0', 1.9, 1.9),
   'M2.5':('1', 2.9, 2.8),
   'M3':  ('1', 3.2, 3.0),
   'M3.5':('2', 4.4, 4.1),
   'M4':  ('2', 4.6, 4.4),
   'M5':  ('2', 5.2, 4.0),
   'M6':  ('3', 6.8, 6.6),
   'M8':  ('4', 8.9, 8.8),
   'M10': ('4', 10.0,9.8)}

# range of typical srew lengths
#    min_length,  max_length
iso7046range = {
   'M1.6':('3', '16'),
   'M2':  ('3', '20'),
   'M2.5':('3', '25'),
   'M3':  ('4', '30'),
   'M3.5':('5', '35'),
   'M4':  ('5', '40'),
   'M5':  ('6', '50'),
   'M6':  ('8', '60'),
   'M8': ('10', '60'),
   'M10':('12', '60')}

# ISO 2010, ISO 7047 definitions Class A: Raised Countersunk head srews
# ISO 2010 slotted screws (common head style)   range = iso2009range
# ISO 7047  with type H or type Z cross recess  range = iso7046range
# Parameters P, a, b, dk_theo, dk_mean, k, r, x to be read from iso2009def
# Length = iso7045length
#          rf, t_mean, cT,   mH,   mZ 
Raised_countersunk_def={
   'M1.6':(3.0,  0.7, '0', 1.9,  1.9),
   'M2':  (4.0,  0.9, '0', 2.0,  2.2),
   'M2.5':(5.0,  1.1, '1', 3.0,  2.8),
   'M3':  (6.0,  1.3, '1', 3.4,  3.1),
   'M3.5':(8.5,  1.5, '2', 4.8,  4.6),
   'M4':  (9.5,  1.8, '2', 5.2,  5.0),
   'M5':  (9.5,  2.2, '2', 5.4,  5.3),
   'M6':  (12.0, 2.6, '3', 7.3,  7.1),
   'M8':  (16.5, 3.5, '4', 9.6,  9.5),
   'M10': (19.5, 4.1, '4', 10.4,10.3)}





# ISO 1580 definitions Class A, Slotted pan head screws
#           P,    a,   b, dk_max,da,  k, n_min,  r,  rf, t_mean, x
iso1580def={
   'M1.6':(0.35, 0.7, 25,  3.2, 2.0, 1.0, 0.46, 0.1, 0.5, 0.4, 0.9),
   'M2':  (0.4,  0.8, 25,  4.0, 2.6, 1.3, 0.56, 0.1, 0.6, 0.5, 1.0),
   'M2.5':(0.45, 0.9, 25,  5.0, 3.1, 1.5, 0.66, 0.1, 0.8, 0.6, 1.1),
   'M3':  (0.5,  1.0, 25,  5.6, 3.6, 1.8, 0.86, 0.1, 0.9, 0.7, 1.25),
   'M3.5':(0.6,  1.2, 38,  7.0, 4.1, 2.1, 1.06, 0.1, 1.0, 0.8, 1.5),
   'M4':  (0.7,  1.4, 38,  8.0, 4.7, 2.4, 1.26, 0.2, 1.2, 1.0, 1.75),
   'M5':  (0.8,  1.6, 38,  9.5, 5.7, 3.0, 1.26, 0.2, 1.5, 1.2, 2.0),
   'M6':  (1.0,  2.0, 38, 12.0, 6.8, 3.6, 1.66, 0.25,1.8, 1.4, 2.5),
   'M8':  (1.25, 2.5, 38, 16.0, 9.2, 4.8, 2.06, 0.4, 2.4, 1.9, 3.2),
   'M10': (1.50, 3.0, 38, 20.0,11.2, 6.0, 2.56, 0.4, 3.0, 2.4, 3.8)}



# ISO 7045 definitions Class A, Pan head screws with type H or type Z
# partly used also for ISO 14583 Hexalobular socket pan head screws
#   cross recess;    cT = size of cross recess
#           P,    a,   b, dk_max,da,  k,   r,   rf,  x,  cT,   mH,   mZ 
iso7045def={
   'M1.6':(0.35, 0.7, 25,  3.2, 2.0, 1.3, 0.1, 2.5, 0.9, '0', 1.7, 1.6),
   'M2':  (0.4,  0.8, 25,  4.0, 2.6, 1.6, 0.1, 3.2, 1.0, '0', 1.9, 2.1),
   'M2.5':(0.45, 0.9, 25,  5.0, 3.1, 2.1, 0.1, 4.0, 1.1, '1', 2.7, 2.6),
   'M3':  (0.5,  1.0, 25,  5.6, 3.6, 2.4, 0.1, 5.0, 1.25,'1', 3.0, 2.8),
   'M3.5':(0.6,  1.2, 38,  7.0, 4.1, 2.6, 0.1, 6.0, 1.5, '2', 3.9, 3.9),
   'M4':  (0.7,  1.4, 38,  8.0, 4.7, 3.1, 0.2, 6.5, 1.75,'2', 4.4, 4.3),
   'M5':  (0.8,  1.6, 38,  9.5, 5.7, 3.7, 0.2, 8.0, 2.0, '2', 4.9, 4.7),
   'M6':  (1.0,  2.0, 38, 12.0, 6.8, 4.6, 0.25,10., 2.5, '3', 6.9, 6.7),
   'M8':  (1.25, 2.5, 38, 16.0, 9.2, 6.0, 0.4, 13., 3.2, '4', 9.0, 8.8),
   'M10': (1.50, 3.0, 38, 20.0,11.2, 7.5, 0.4, 16., 3.8, '4', 10.1,9.9)}

# nom length: l_min, l_max       
iso7045length = {
   '3': ( 2.8,  3.2),
   '4': ( 3.76, 4.24),
   '5': ( 4.76, 5.24),
   '6': ( 5.76, 6.24),
   '8': ( 7.71, 8.29),
   '10':( 9.71, 10.29),
   '12':(11.65, 12.35),
   '14':(13.65, 14.35),
   '16':(15.65, 16.35),
   '20':(19.58, 20.42),
   '25':(24.58, 25.42),
   '30':(29.58, 30.42),
   '35':(34.5,  35.5),
   '40':(39.5,  40.5),
   '45':(44.5,  45.5),
   '50':(49.5,  50.5),
   '55':(54.05, 55.95),
   '60':(59.05, 60.95)
      }

# range of typical srew lengths
#    min_length,  max_length
iso7045range = {
   'M1.6':('3', '16'),
   'M2':  ('3', '20'),
   'M2.5':('3', '25'),
   'M3':  ('4', '30'),
   'M3.5':('5', '35'),
   'M4':  ('5', '40'),
   'M5':  ('6', '45'),
   'M6':  ('8', '60'),
   'M8': ('10', '60'),
   'M10':('12', '60')}


# ISO 14583 Hexalobular socket pan head screws
#   hexalobular recess;    tt = size of hexalobular recess

#           tt,    A,  t_mean
iso14583def={
   'M2':  ('T6',  1.75, 0.7),
   'M2.5':('T8',  2.40, 1.0),
   'M3':  ('T10', 2.80, 1.2),
   'M3.5':('T15', 3.35, 1.3),
   'M4':  ('T20', 3.95, 1.5),
   'M5':  ('T25', 4.50, 1.7),
   'M6':  ('T30', 5.60, 2.2),
   'M8':  ('T45', 7.95, 3.0),
   'M10': ('T50', 8.95, 3.8)}


#iso14583range = iso7046range
#iso14583length = iso7045length



# ISO 4762 Hexagon socket head cap screws ( Allan screw)
# ISO 4762 definitions
#           P,   b,  dk_max, da,  ds_min,   e,    lf,   k,   r,   s_mean, t,    v,   dw,   w
iso4762def={
   'M1.6':(0.35, 15.0, 3.0,  2.0,  1.46,  1.73, 0.34,  1.6, 0.1,  1.56,  0.7, 0.16, 2.72, 0.55),
   'M2':  (0.40, 16.0, 3.8,  2.6,  1.86,  1.73, 0.51,  2.0, 0.1,  1.56,  1.0, 0.2,  3.48, 0.55),
   'M2.5':(0.45, 17.0, 4.5,  3.1,  2.36,  2.30, 0.51,  2.5, 0.1,  2.06,  1.1, 0.25, 4.18, 0.85),
   'M3':  (0.50, 18.0,  5.5,  3.6,  2.86,  2.87, 0.51,  3.0, 0.1,  2.56,  1.3, 0.3,  5.07, 1.15),
   'M4':  (0.70, 20.0,  7.0,  4.7,  3.82,  3.44, 0.60,  4.0, 0.2,  3.06,  2.0, 0.4,  6.53, 1.40),
   'M5':  (0.80, 22.0,  8.5,  5.7,  4.82,  4.58, 0.60,  5.0, 0.2,  4.06,  2.5, 0.5,  8.03, 1.9),
   'M6':  (1.00, 24.0, 10.0,  6.8,  5.82,  5.72, 0.68,  6.0, 0.25, 5.06,  3.0, 0.6,  9.38, 2.3),
   'M8':  (1.25, 28.0, 13.0,  9.2,  7.78,  6.86, 1.02,  8.0, 0.4,  6.06,  4.0, 0.8, 12.33, 3.3),
   'M10': (1.50, 32.0, 16.0, 11.2,  9.78,  9.15, 1.02, 10.0, 0.4,  8.07,  5.0, 1.0, 15.33, 4.0),
   'M12': (1.75, 36.0, 18.0, 13.7, 11.73, 11.43, 1.45, 12.0, 0.6, 10.07,  6.0, 1.2, 17.23, 4.8),
   'M14': (2.00, 40.0, 21.0, 15.7, 13.73, 13.72, 1.45, 14.0, 0.6, 12.07,  7.0, 1.4, 20.17, 5.8),
   'M16': (2.00, 44.0, 24.0, 17.7, 15.73, 16.00, 1.45, 16.0, 0.6, 14.08,  8.0, 1.6, 23.17, 6.8),
   'M20': (2.50, 52.0, 30.0, 22.4, 19.67, 19.44, 2.04, 20.0, 0.8, 17.10, 10.0, 2.0, 28.87, 8.6),
   'M24': (3.00, 60.0, 36.0, 26.4, 23.67, 21.73, 2.04, 24.0, 0.8, 19.15, 12.0, 2.0, 34.81, 10.4),
   'M30': (3.50, 72.0, 45.0, 33.4, 29.67, 25.15, 2.89, 30.0, 1.0, 22.15, 15.5, 2.4, 43,61, 13.1),
   'M36': (4.00, 84.0, 54.0, 39.4, 35.61, 30.85, 2.89, 36.0, 1.0, 27.15, 19.0, 3.0, 52.54, 15.3)}       

# nom length: l_min, l_max       
iso4762length = {
   '2.5':(2.3,  2.7),
   '3': ( 2.8,  3.2),
   '4': ( 3.76, 4.24),
   '5': ( 4.76, 5.24),
   '6': ( 5.76, 6.24),
   '8': ( 7.71, 8.29),
   '10':( 9.71, 10.29),
   '12':(11.65, 12.35),
   '14':(13.65, 14.35),
   '16':(15.65, 16.35),
   '20':(19.58, 20.42),
   '25':(24.58, 25.42),
   '30':(29.58, 30.42),
   '35':(34.5,  35.5),
   '40':(39.5,  40.5),
   '45':(44.5,  45.5),
   '50':(49.5,  50.5),
   '55':(54.4, 55.6),
   '60':(59.4, 60.6),
   '65':(64.4, 65.6),
   '70':(69.4, 70.6),
   '75':(74.4, 75.6),
   '80':(79.4, 80.6),
   '100':(99.3, 100.7),
   '110':(109.3, 110.7),
   '120':(119.3, 120.7),
   '130':(129.2, 130.8),
   '140':(139.2, 130.8),
   '150':(149.2, 150.8),
   '160':(159.2, 160.8),
   '180':(179.2, 180.8),
   '200':(199.1, 200.9)
      }

# range of typical srew lengths
#    min_length,  max_length
iso4762range = {
   'M1.6':('2.5', '16'),
   'M2':  ('3', '20'),
   'M2.5':('4', '25'),
   'M3':  ('5', '30'),
   'M3.5':('6', '35'),
   'M4':  ('6', '40'),
   'M5':  ('8', '50'),
   'M6':  ('8', '60'),
   'M8': ('10', '80'),
   'M10':('16', '100'),
   'M12':('20', '120'),
   'M14':('25', '140'),
   'M16':('25', '160'),
   'M20':('16', '100'),
   'M24':('40', '200'),
   'M30':('45', '200'),
   'M36':('55', '200')   
   }


# ISO 14579 Hexalobular socket head cap screws
#   hexalobular recess;    tt = size of hexalobular recess

#           tt,    A,  t_mean
iso14579def={
   'M2':  ( 'T6',  1.75, 0.8),
   'M2.5':( 'T8',  2.40, 1.0),
   'M3':  ('T10',  2.80, 1.2),
   'M4':  ('T20',  3.95, 1.7),
   'M5':  ('T25',  4.50, 1.9),
   'M6':  ('T30',  5.60, 2.3),
   'M8':  ('T45',  7.95, 3.2),
   'M10': ('T50',  8.95, 3.8),
   'M12': ('T55', 11.35, 5.0),
   'M14': ('T60', 13.45, 5.8),
   'M16': ('T70', 15.70, 6.8),
   #'M18': ('T80', 17.75, 7.8),
   'M20': ('T90', 20.20, 9.0),
   }

# range of typical srew lengths
#    min_length,  max_length
iso14579range = {
   'M2':  ('3', '20'),
   'M2.5':('4', '25'),
   'M3':  ('5', '30'),
   'M4':  ('6', '40'),
   'M5':  ('8', '50'),
   'M6': ('10', '60'),
   'M8': ('12', '80'),
   'M10':('16','100'),
   'M12':('20','120'),
   'M14':('25','140'), 
   'M16':('25','160'),
   #'M18':('30','180'),
   'M20':('30','200'),
   } 

iso14579length = {
   '3': ( 2.8,  3.2),
   '4': ( 3.76, 4.24),
   '5': ( 4.76, 5.24),
   '6': ( 5.76, 6.24),
   '8': ( 7.71, 8.29),
   '10':( 9.71, 10.29),
   '12':(11.65, 12.35),
   '16':(15.65, 16.35),
   '20':(19.58, 20.42),
   '25':(24.58, 25.42),
   '30':(29.58, 30.42),
   '35':(34.5,  35.5),
   '40':(39.5,  40.5),
   '45':(44.5,  45.5),
   '50':(49.5,  50.5),
   '55':(54.4, 55.6),
   '60':(59.4, 60.6),
   '65':(64.4, 65.6),
   '70':(69.4, 70.6),
   '80':(79.4, 80.6),
   '90':(89.3, 90.7),
   '100':(99.3, 100.7),
   '110':(109.3, 110.7),
   '120':(119.3, 120.7),
   '130':(129.2, 130.8),
   '140':(139.2, 130.8),
   '150':(149.2, 150.8),
   '160':(159.2, 160.8),
   '180':(179.2, 180.8),
   '200':(199.1, 200.9)
         }


# ISO 10642 Hexagon socket countersunk head screws ( Allan screw)
# ISO 10642 definitions
#           P,   b,  dk_theo, dk_mean,da,  ds_min,   e,  k,   r,   s_mean, t,    w
iso10642def={
   'M3':  (0.50, 18.0,  6.72,  6.0,  3.3,  2.86,  2.31, 1.86, 0.1,  2.06,  1.1, 0.25),
   'M4':  (0.70, 20.0,  8.96,  8.0,  4.4,  3.82,  2.88, 2.48, 0.2,  2.56,  1.5, 0.45),
   'M5':  (0.80, 22.0, 11.20, 10.0,  5.5,  4.82,  3.45, 3.10, 0.2,  3.06,  1.9, 0.66),
   'M6':  (1.00, 24.0, 13.44, 12.0,  6.6,  5.82,  4.59, 3.72, 0.25, 4.06,  2.2, 0.70),
   'M8':  (1.25, 28.0, 17.92, 16.0,  8.54, 7.78,  5.73, 4.96, 0.4,  5.06,  3.0, 1.16),
   'M10': (1.50, 32.0, 22.40, 20.5, 10.62, 9.78,  6.87, 6.20, 0.4,  6.06,  3.6, 1.62),
   'M12': (1.75, 36.0, 26.88, 25.0, 13.5, 11.73,  9.15, 7.44, 0.6,  8.07,  4.3, 1.80),
   'M14': (2.00, 40.0, 30.80, 28.4, 15.5, 13.73, 11.43, 8.40, 0.6, 10.07,  4.5, 1.62),
   'M16': (2.00, 44.0, 33.60, 31.0, 17.5, 15.73, 11.43, 8.80, 0.6, 10.07,  4.8, 2.20),
   'M20': (2.50, 52.0, 40.32, 38.0, 22.0, 19.67, 13.72, 10.16, 0.8, 12.10,  5.6, 2.20)}

# range of typical srew lengths
#    min_length,  max_length
iso10642range = {
   'M3':  ('8', '30'),
   'M4':  ('8', '40'),
   'M5':  ('8', '50'),
   'M6':  ('8', '60'),
   'M8': ('10', '80'),
   'M10':('12','100'),
   'M12':('20','100'),
   'M14':('25','100'), 
   'M16':('30','100'),
   'M20':('35','100'),
   } 

iso10642length = {
   '8': ( 7.71, 8.29),
   '10':( 9.71, 10.29),
   '12':(11.65, 12.35),
   '16':(15.65, 16.35),
   '20':(19.58, 20.42),
   '25':(24.58, 25.42),
   '30':(29.58, 30.42),
   '35':(34.5,  35.5),
   '40':(39.5,  40.5),
   '45':(44.5,  45.5),
   '50':(49.5,  50.5),
   '55':(54.4, 55.6),
   '60':(59.4, 60.6),
   '65':(64.4, 65.6),
   '70':(69.4, 70.6),
   '80':(79.4, 80.6),
   '90':(89.3, 90.7),
   '100':(99.3, 100.7),
         }


# ISO 7089 definitions  Washer
#           d1_min, d2_max, h, h_max
iso7089def={
   'M1.6':( 1.7,  4.0, 0.3, 0.35),
   'M2':  ( 2.2,  5.0, 0.3, 0.35),
   'M2.5':( 2.7,  6.0, 0.5, 0.55),
   'M3':  ( 3.2,  7.0, 0.5, 0.55),
   'M4':  ( 4.3,  9.0, 0.8, 0.90),
   'M5':  ( 5.3, 10.0, 1.0, 1.10),
   'M6':  ( 6.4, 12.0, 1.6, 1.80),
   'M8':  ( 8.4, 16.0, 1.6, 1.80),
   'M10': (10.5, 20.0, 2.0, 2.20),
   'M12': (13.0, 24.0, 2.5, 2.70),
   'M16': (17.0, 30.0, 3.0, 3.30),
   'M20': (21.0, 37.0, 3.0, 3.30),
   'M24': (25.0, 44.0, 4.0, 4.30),
   'M30': (31.0, 56.0, 4.0, 4.30),
   'M36': (37.0, 66.0, 5.0, 5.60),
   'M42': (45.0, 78.0, 8.0, 9.0),
   'M48': (52.0, 92.0, 8.0, 9.0),
   'M56': (62.0,105.0,10.0, 11.0),
   'M64': (70.0,115.0,10.0, 11.0)
   }       


# ISO 4757:1983 Definition of cross recess type H
#          b, e_min, g, f_mean, r, t1, alpha, beta
iso4757def = {
   '0': (0.61, 0.26, 0.81, 0.34, 0.3, 0.22, 138.0, 7.0 ),
   '1': (0.97, 0.41, 1.27, 0.54, 0.5, 0.34, 138.0, 7.0 ),
   '2': (1.47, 0.79, 2.29, 0.70, 0.6, 0.61, 140.0, 5.75),
   '3': (2.41, 1.98, 3.81, 0.83, 0.8, 1.01, 146.0, 5.75),
   '4': (3.48, 2.39, 5.08, 1.23, 1.0, 1.35, 153.0, 7.0 )
   }

# ISO 10664 Hexalobular internal driving feature for bolts and screws
#           A,     B,   Re
iso10664def = {
   'T6': ( 1.75,  1.205, 0.14),
   'T8': ( 2.40,  1.67, 0.20),
   'T10':( 2.80,  1.98, 0.24),
   'T15':( 3.35,  2.35, 0.28),
   'T20':( 3.95,  2.75, 0.32),
   'T25':( 4.50,  3.16, 0.39),
   'T30':( 5.60,  3.95, 0.46),
   'T40':( 6.75,  4.76, 0.56),
   'T45':( 7.93,  5.55, 0.59),
   'T50':( 8.95,  6.36, 0.78),
   'T55':(11.35,  7.92, 0.77),
   'T60':(13.45,  9.48, 1.07),
   'T70':(15.70, 11.08, 1.20),
   'T80':(17.75, 12.64, 1.53),
   'T90':(20.20, 14.22, 1.54),
   'T100':(22.40,15.81, 1.73)
   } 

screwTables = {
    'ISO4017': ("Screw", iso4017head, iso4017length, iso4017range),
    'ISO4014': ("Screw", iso4014head, iso4014length, iso4014range),
    'EN1662': ("Screw", en1662def, en1662length, en1662range),            
    'EN1665': ("Screw", en1665def, en1665length, en1665range),
    'ISO2009': ("Screw", iso2009def, iso2009length, iso2009range),
    'ISO2010': ("Screw", iso2009def, iso2009length, iso2009range),
    'ISO4762': ("Screw", iso4762def, iso4762length, iso4762range),
    'ISO10642': ("Screw", iso10642def, iso10642length, iso10642range),
    'ISO1207': ("Screw", iso1207def, iso1207length, iso1207range),
    'ISO1580': ("Screw", iso1580def, iso2009length, iso2009range),
    'ISO7045': ("Screw", iso7045def, iso7045length, iso7045range),
    'ISO7046': ("Screw", iso7046def, iso7045length, iso7046range),
    'ISO7047': ("Screw", iso2009def, iso7045length, iso7046range),
    'ISO7048': ("Screw", iso7048def, iso7048length, iso7048range),
    'ISO7380': ("Screw", iso7380def, iso7380length, iso7380range),
    'ISO14579': ("Screw", iso14579def, iso14579length, iso14579range),
    'ISO14580': ("Screw", iso14580def, iso14580length, iso1207range),
    'ISO14583': ("Screw", iso14583def, iso7045length, iso7046range),
    'ISO7089': ("Washer", iso7089def, None, None)
}

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class Ui_ScrewMaker(object):
    def setupUi(self, ScrewMaker):
        ScrewMaker.setObjectName(_fromUtf8("ScrewMaker"))
        ScrewMaker.resize(450, 362)
        ScrewMaker.setLocale(QtCore.QLocale(QtCore.QLocale.English, QtCore.QLocale.UnitedKingdom))
        self.layoutWidget = QtGui.QWidget(ScrewMaker)
        self.layoutWidget.setGeometry(QtCore.QRect(330, 20, 111, 161))
        self.layoutWidget.setObjectName(_fromUtf8("layoutWidget"))
        self.verticalLayout_2 = QtGui.QVBoxLayout(self.layoutWidget)
        #self.verticalLayout_2.setMargin(0)
        self.verticalLayout_2.setObjectName(_fromUtf8("verticalLayout_2"))
        self.ScrewTypeLabel = QtGui.QLabel(self.layoutWidget)
        self.ScrewTypeLabel.setObjectName(_fromUtf8("ScrewTypeLabel"))
        self.verticalLayout_2.addWidget(self.ScrewTypeLabel)
        self.NomDiaLabel = QtGui.QLabel(self.layoutWidget)
        self.NomDiaLabel.setObjectName(_fromUtf8("NomDiaLabel"))
        self.verticalLayout_2.addWidget(self.NomDiaLabel)
        self.NomLenLabel = QtGui.QLabel(self.layoutWidget)
        self.NomLenLabel.setObjectName(_fromUtf8("NomLenLabel"))
        self.verticalLayout_2.addWidget(self.NomLenLabel)
        self.ThreadTypeLabel = QtGui.QLabel(self.layoutWidget)
        self.ThreadTypeLabel.setObjectName(_fromUtf8("ThreadTypeLabel"))
        self.verticalLayout_2.addWidget(self.ThreadTypeLabel)
        self.layoutWidget1 = QtGui.QWidget(ScrewMaker)
        self.layoutWidget1.setGeometry(QtCore.QRect(10, 20, 315, 166))
        self.layoutWidget1.setObjectName(_fromUtf8("layoutWidget1"))
        self.verticalLayout = QtGui.QVBoxLayout(self.layoutWidget1)
        #self.verticalLayout.setMargin(0)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.ScrewType = QtGui.QComboBox(self.layoutWidget1)
        self.ScrewType.setObjectName(_fromUtf8("ScrewType"))
        self.ScrewType.addItem(_fromUtf8(""))  # 0
        self.ScrewType.addItem(_fromUtf8(""))
        self.ScrewType.addItem(_fromUtf8(""))
        self.ScrewType.addItem(_fromUtf8(""))
        self.ScrewType.addItem(_fromUtf8(""))
        self.ScrewType.addItem(_fromUtf8(""))
        self.ScrewType.addItem(_fromUtf8(""))
        self.ScrewType.addItem(_fromUtf8(""))
        self.ScrewType.addItem(_fromUtf8(""))
        self.ScrewType.addItem(_fromUtf8(""))
        self.ScrewType.addItem(_fromUtf8("")) # 10
        self.ScrewType.addItem(_fromUtf8("")) # 11
        self.ScrewType.addItem(_fromUtf8("")) # 12
        self.ScrewType.addItem(_fromUtf8("")) # 13
        self.ScrewType.addItem(_fromUtf8("")) # 14
        self.ScrewType.addItem(_fromUtf8("")) # 15
        self.ScrewType.addItem(_fromUtf8("")) # 16
        self.ScrewType.addItem(_fromUtf8("")) # 17
        self.ScrewType.addItem(_fromUtf8("")) # 18
        self.verticalLayout.addWidget(self.ScrewType)
        self.NominalDiameter = QtGui.QComboBox(self.layoutWidget1)
        self.NominalDiameter.setObjectName(_fromUtf8("NominalDiameter"))
        self.NominalDiameter.addItem(_fromUtf8(""))
        self.NominalDiameter.addItem(_fromUtf8(""))
        self.NominalDiameter.addItem(_fromUtf8(""))
        self.NominalDiameter.addItem(_fromUtf8(""))
        self.NominalDiameter.addItem(_fromUtf8(""))
        self.NominalDiameter.addItem(_fromUtf8(""))
        self.NominalDiameter.addItem(_fromUtf8(""))
        self.NominalDiameter.addItem(_fromUtf8(""))
        self.NominalDiameter.addItem(_fromUtf8(""))
        self.NominalDiameter.addItem(_fromUtf8(""))
        self.NominalDiameter.addItem(_fromUtf8(""))
        self.NominalDiameter.addItem(_fromUtf8(""))
        self.NominalDiameter.addItem(_fromUtf8(""))
        self.NominalDiameter.addItem(_fromUtf8(""))
        self.NominalDiameter.addItem(_fromUtf8(""))
        self.NominalDiameter.addItem(_fromUtf8(""))
        self.NominalDiameter.addItem(_fromUtf8(""))
        self.verticalLayout.addWidget(self.NominalDiameter)
        self.NominalLength = QtGui.QComboBox(self.layoutWidget1)
        self.NominalLength.setObjectName(_fromUtf8("NominalLength"))
        self.NominalLength.addItem(_fromUtf8(""))
        self.NominalLength.addItem(_fromUtf8(""))
        self.NominalLength.addItem(_fromUtf8(""))
        self.NominalLength.addItem(_fromUtf8(""))
        self.NominalLength.addItem(_fromUtf8(""))
        self.NominalLength.addItem(_fromUtf8(""))
        self.NominalLength.addItem(_fromUtf8(""))
        self.NominalLength.addItem(_fromUtf8(""))
        self.NominalLength.addItem(_fromUtf8(""))
        self.NominalLength.addItem(_fromUtf8(""))
        self.NominalLength.addItem(_fromUtf8(""))
        self.NominalLength.addItem(_fromUtf8(""))
        self.NominalLength.addItem(_fromUtf8(""))
        self.NominalLength.addItem(_fromUtf8(""))
        self.NominalLength.addItem(_fromUtf8(""))
        self.NominalLength.addItem(_fromUtf8(""))
        self.NominalLength.addItem(_fromUtf8(""))
        self.NominalLength.addItem(_fromUtf8(""))
        self.NominalLength.addItem(_fromUtf8(""))
        self.NominalLength.addItem(_fromUtf8(""))
        self.NominalLength.addItem(_fromUtf8(""))
        self.NominalLength.addItem(_fromUtf8(""))
        self.NominalLength.addItem(_fromUtf8(""))
        self.NominalLength.addItem(_fromUtf8(""))
        self.NominalLength.addItem(_fromUtf8(""))
        self.NominalLength.addItem(_fromUtf8(""))
        self.NominalLength.addItem(_fromUtf8(""))
        self.NominalLength.addItem(_fromUtf8(""))
        self.NominalLength.addItem(_fromUtf8(""))
        self.NominalLength.addItem(_fromUtf8(""))
        self.NominalLength.addItem(_fromUtf8(""))
        self.verticalLayout.addWidget(self.NominalLength)
        self.ThreadType = QtGui.QComboBox(self.layoutWidget1)
        self.ThreadType.setObjectName(_fromUtf8("ThreadType"))
        self.ThreadType.addItem(_fromUtf8(""))
        self.verticalLayout.addWidget(self.ThreadType)
        self.layoutWidget2 = QtGui.QWidget(ScrewMaker)
        self.layoutWidget2.setGeometry(QtCore.QRect(10, 200, 321, 83))
        self.layoutWidget2.setObjectName(_fromUtf8("layoutWidget2"))
        self.verticalLayout_3 = QtGui.QVBoxLayout(self.layoutWidget2)
        #self.verticalLayout_3.setMargin(0)
        self.verticalLayout_3.setObjectName(_fromUtf8("verticalLayout_3"))
        self.SimpleScrew = QtGui.QRadioButton(self.layoutWidget2)
        self.SimpleScrew.setChecked(True)
        self.SimpleScrew.setObjectName(_fromUtf8("SimpleScrew"))
        self.verticalLayout_3.addWidget(self.SimpleScrew)
        self.SymbolThread = QtGui.QRadioButton(self.layoutWidget2)
        self.SymbolThread.setObjectName(_fromUtf8("SymbolThread"))
        self.verticalLayout_3.addWidget(self.SymbolThread)
        self.RealThread = QtGui.QRadioButton(self.layoutWidget2)
        self.RealThread.setObjectName(_fromUtf8("RealThread"))
        self.verticalLayout_3.addWidget(self.RealThread)
        self.MessageLabel = QtGui.QLabel(ScrewMaker)
        self.MessageLabel.setGeometry(QtCore.QRect(20, 290, 411, 21))
        self.MessageLabel.setProperty("Empty_text", _fromUtf8(""))
        self.MessageLabel.setObjectName(_fromUtf8("MessageLabel"))
        self.CreateButton = QtGui.QToolButton(ScrewMaker)
        self.CreateButton.setGeometry(QtCore.QRect(180, 320, 111, 26))
        self.CreateButton.setObjectName(_fromUtf8("CreateButton"))
        self.ScrewAvailable = True

        self.retranslateUi(ScrewMaker)
        self.NominalDiameter.setCurrentIndex(5)
        self.NominalLength.setCurrentIndex(9)
        QtCore.QObject.connect(self.ScrewType, QtCore.SIGNAL(_fromUtf8("currentIndexChanged(int)")), self.check_Data)
        QtCore.QObject.connect(self.CreateButton, QtCore.SIGNAL(_fromUtf8("pressed()")), self.createScrew)
        QtCore.QObject.connect(self.NominalDiameter, QtCore.SIGNAL(_fromUtf8("currentIndexChanged(int)")), self.check_Data)
        QtCore.QObject.connect(self.NominalLength, QtCore.SIGNAL(_fromUtf8("currentIndexChanged(int)")), self.check_Data)
        QtCore.QMetaObject.connectSlotsByName(ScrewMaker)

    def retranslateUi(self, ScrewMaker):
        ScrewMaker.setWindowTitle(QtGui.QApplication.translate("ScrewMaker", "Screw-Maker", None, QtGui.QApplication.UnicodeUTF8))
        self.ScrewTypeLabel.setText(QtGui.QApplication.translate("ScrewMaker", "Type of Screw", None, QtGui.QApplication.UnicodeUTF8))
        self.NomDiaLabel.setText(QtGui.QApplication.translate("ScrewMaker", "Nomimal Diameter", None, QtGui.QApplication.UnicodeUTF8))
        self.NomLenLabel.setText(QtGui.QApplication.translate("ScrewMaker", "Nominal length", None, QtGui.QApplication.UnicodeUTF8))
        self.ThreadTypeLabel.setText(QtGui.QApplication.translate("ScrewMaker", "Thread type", None, QtGui.QApplication.UnicodeUTF8))
        self.ScrewType.setItemText(0, QtGui.QApplication.translate("ScrewMaker", "ISO4017: Hexagon head screws", None, QtGui.QApplication.UnicodeUTF8))
        self.ScrewType.setItemText(1, QtGui.QApplication.translate("ScrewMaker", "ISO4014: Hexagon head bolts", None, QtGui.QApplication.UnicodeUTF8))
        self.ScrewType.setItemText(2, QtGui.QApplication.translate("ScrewMaker", "EN1662: Hexagon bolts with flange, small series", None, QtGui.QApplication.UnicodeUTF8))
        self.ScrewType.setItemText(3, QtGui.QApplication.translate("ScrewMaker", "EN1665: Hexagon bolts with flange, heavy series", None, QtGui.QApplication.UnicodeUTF8))
        self.ScrewType.setItemText(4, QtGui.QApplication.translate("ScrewMaker", "ISO4762: Hexagon socket head cap screws", None, QtGui.QApplication.UnicodeUTF8))
        self.ScrewType.setItemText(5, QtGui.QApplication.translate("ScrewMaker", "ISO7380: Hexagon socket button head screws", None, QtGui.QApplication.UnicodeUTF8))
        self.ScrewType.setItemText(6, QtGui.QApplication.translate("ScrewMaker", "ISO10642: Hexagon socket countersunk head screws", None, QtGui.QApplication.UnicodeUTF8))
        self.ScrewType.setItemText(7, QtGui.QApplication.translate("ScrewMaker", "ISO2009: Slotted countersunk flat head screws", None, QtGui.QApplication.UnicodeUTF8))
        self.ScrewType.setItemText(8, QtGui.QApplication.translate("ScrewMaker", "ISO2010: Slotted raised countersunk head screws", None, QtGui.QApplication.UnicodeUTF8))
        self.ScrewType.setItemText(9, QtGui.QApplication.translate("ScrewMaker", "ISO1207: Slotted cheese head screws", None, QtGui.QApplication.UnicodeUTF8))
        self.ScrewType.setItemText(10, QtGui.QApplication.translate("ScrewMaker", "ISO1580: Slotted pan head screws", None, QtGui.QApplication.UnicodeUTF8))
        self.ScrewType.setItemText(11, QtGui.QApplication.translate("ScrewMaker", "ISO7045: Pan head screws type H cross recess", None, QtGui.QApplication.UnicodeUTF8))
        self.ScrewType.setItemText(12, QtGui.QApplication.translate("ScrewMaker", "ISO7046: Countersunk flat head screws H cross r.", None, QtGui.QApplication.UnicodeUTF8))
        self.ScrewType.setItemText(13, QtGui.QApplication.translate("ScrewMaker", "ISO7047: Raised countersunk head screws H cross r.", None, QtGui.QApplication.UnicodeUTF8))
        self.ScrewType.setItemText(14, QtGui.QApplication.translate("ScrewMaker", "ISO7048: Cheese head screws type H cross recess", None, QtGui.QApplication.UnicodeUTF8))
        self.ScrewType.setItemText(15, QtGui.QApplication.translate("ScrewMaker", "ISO14579: Hexalobular socket head cap screws", None, QtGui.QApplication.UnicodeUTF8))
        self.ScrewType.setItemText(16, QtGui.QApplication.translate("ScrewMaker", "ISO14580: Hexalobular socket cheese head screws", None, QtGui.QApplication.UnicodeUTF8))
        self.ScrewType.setItemText(17, QtGui.QApplication.translate("ScrewMaker", "ISO14583: Hexalobular socket pan head screws", None, QtGui.QApplication.UnicodeUTF8))
        self.ScrewType.setItemText(18, QtGui.QApplication.translate("ScrewMaker", "ISO7089: Washer", None, QtGui.QApplication.UnicodeUTF8))
        self.NominalDiameter.setItemText(0, QtGui.QApplication.translate("ScrewMaker", "M1.6", None, QtGui.QApplication.UnicodeUTF8))
        self.NominalDiameter.setItemText(1, QtGui.QApplication.translate("ScrewMaker", "M2", None, QtGui.QApplication.UnicodeUTF8))
        self.NominalDiameter.setItemText(2, QtGui.QApplication.translate("ScrewMaker", "M2.5", None, QtGui.QApplication.UnicodeUTF8))
        self.NominalDiameter.setItemText(3, QtGui.QApplication.translate("ScrewMaker", "M3", None, QtGui.QApplication.UnicodeUTF8))
        self.NominalDiameter.setItemText(4, QtGui.QApplication.translate("ScrewMaker", "M4", None, QtGui.QApplication.UnicodeUTF8))
        self.NominalDiameter.setItemText(5, QtGui.QApplication.translate("ScrewMaker", "M5", None, QtGui.QApplication.UnicodeUTF8))
        self.NominalDiameter.setItemText(6, QtGui.QApplication.translate("ScrewMaker", "M6", None, QtGui.QApplication.UnicodeUTF8))
        self.NominalDiameter.setItemText(7, QtGui.QApplication.translate("ScrewMaker", "M8", None, QtGui.QApplication.UnicodeUTF8))
        self.NominalDiameter.setItemText(8, QtGui.QApplication.translate("ScrewMaker", "M10", None, QtGui.QApplication.UnicodeUTF8))
        self.NominalDiameter.setItemText(9, QtGui.QApplication.translate("ScrewMaker", "M12", None, QtGui.QApplication.UnicodeUTF8))
        self.NominalDiameter.setItemText(10, QtGui.QApplication.translate("ScrewMaker", "M14", None, QtGui.QApplication.UnicodeUTF8))
        self.NominalDiameter.setItemText(11, QtGui.QApplication.translate("ScrewMaker", "M16", None, QtGui.QApplication.UnicodeUTF8))
        self.NominalDiameter.setItemText(12, QtGui.QApplication.translate("ScrewMaker", "M20", None, QtGui.QApplication.UnicodeUTF8))
        self.NominalDiameter.setItemText(13, QtGui.QApplication.translate("ScrewMaker", "M24", None, QtGui.QApplication.UnicodeUTF8))
        self.NominalDiameter.setItemText(14, QtGui.QApplication.translate("ScrewMaker", "M27", None, QtGui.QApplication.UnicodeUTF8))
        self.NominalDiameter.setItemText(15, QtGui.QApplication.translate("ScrewMaker", "M30", None, QtGui.QApplication.UnicodeUTF8))
        self.NominalDiameter.setItemText(16, QtGui.QApplication.translate("ScrewMaker", "M36", None, QtGui.QApplication.UnicodeUTF8))
        self.NominalLength.setItemText(0, QtGui.QApplication.translate("ScrewMaker", "2.5", None, QtGui.QApplication.UnicodeUTF8))
        self.NominalLength.setItemText(1, QtGui.QApplication.translate("ScrewMaker", "3", None, QtGui.QApplication.UnicodeUTF8))
        self.NominalLength.setItemText(2, QtGui.QApplication.translate("ScrewMaker", "4", None, QtGui.QApplication.UnicodeUTF8))
        self.NominalLength.setItemText(3, QtGui.QApplication.translate("ScrewMaker", "5", None, QtGui.QApplication.UnicodeUTF8))
        self.NominalLength.setItemText(4, QtGui.QApplication.translate("ScrewMaker", "6", None, QtGui.QApplication.UnicodeUTF8))
        self.NominalLength.setItemText(5, QtGui.QApplication.translate("ScrewMaker", "8", None, QtGui.QApplication.UnicodeUTF8))
        self.NominalLength.setItemText(6, QtGui.QApplication.translate("ScrewMaker", "10", None, QtGui.QApplication.UnicodeUTF8))
        self.NominalLength.setItemText(7, QtGui.QApplication.translate("ScrewMaker", "12", None, QtGui.QApplication.UnicodeUTF8))
        self.NominalLength.setItemText(8, QtGui.QApplication.translate("ScrewMaker", "16", None, QtGui.QApplication.UnicodeUTF8))
        self.NominalLength.setItemText(9, QtGui.QApplication.translate("ScrewMaker", "20", None, QtGui.QApplication.UnicodeUTF8))
        self.NominalLength.setItemText(10, QtGui.QApplication.translate("ScrewMaker", "25", None, QtGui.QApplication.UnicodeUTF8))
        self.NominalLength.setItemText(11, QtGui.QApplication.translate("ScrewMaker", "30", None, QtGui.QApplication.UnicodeUTF8))
        self.NominalLength.setItemText(12, QtGui.QApplication.translate("ScrewMaker", "35", None, QtGui.QApplication.UnicodeUTF8))
        self.NominalLength.setItemText(13, QtGui.QApplication.translate("ScrewMaker", "40", None, QtGui.QApplication.UnicodeUTF8))
        self.NominalLength.setItemText(14, QtGui.QApplication.translate("ScrewMaker", "45", None, QtGui.QApplication.UnicodeUTF8))
        self.NominalLength.setItemText(15, QtGui.QApplication.translate("ScrewMaker", "50", None, QtGui.QApplication.UnicodeUTF8))
        self.NominalLength.setItemText(16, QtGui.QApplication.translate("ScrewMaker", "55", None, QtGui.QApplication.UnicodeUTF8))
        self.NominalLength.setItemText(17, QtGui.QApplication.translate("ScrewMaker", "60", None, QtGui.QApplication.UnicodeUTF8))
        self.NominalLength.setItemText(18, QtGui.QApplication.translate("ScrewMaker", "65", None, QtGui.QApplication.UnicodeUTF8))
        self.NominalLength.setItemText(19, QtGui.QApplication.translate("ScrewMaker", "70", None, QtGui.QApplication.UnicodeUTF8))
        self.NominalLength.setItemText(20, QtGui.QApplication.translate("ScrewMaker", "80", None, QtGui.QApplication.UnicodeUTF8))
        self.NominalLength.setItemText(21, QtGui.QApplication.translate("ScrewMaker", "90", None, QtGui.QApplication.UnicodeUTF8))
        self.NominalLength.setItemText(22, QtGui.QApplication.translate("ScrewMaker", "100", None, QtGui.QApplication.UnicodeUTF8))
        self.NominalLength.setItemText(23, QtGui.QApplication.translate("ScrewMaker", "110", None, QtGui.QApplication.UnicodeUTF8))
        self.NominalLength.setItemText(24, QtGui.QApplication.translate("ScrewMaker", "120", None, QtGui.QApplication.UnicodeUTF8))
        self.NominalLength.setItemText(25, QtGui.QApplication.translate("ScrewMaker", "130", None, QtGui.QApplication.UnicodeUTF8))
        self.NominalLength.setItemText(26, QtGui.QApplication.translate("ScrewMaker", "140", None, QtGui.QApplication.UnicodeUTF8))
        self.NominalLength.setItemText(27, QtGui.QApplication.translate("ScrewMaker", "150", None, QtGui.QApplication.UnicodeUTF8))
        self.NominalLength.setItemText(28, QtGui.QApplication.translate("ScrewMaker", "160", None, QtGui.QApplication.UnicodeUTF8))
        self.NominalLength.setItemText(29, QtGui.QApplication.translate("ScrewMaker", "180", None, QtGui.QApplication.UnicodeUTF8))
        self.NominalLength.setItemText(30, QtGui.QApplication.translate("ScrewMaker", "200", None, QtGui.QApplication.UnicodeUTF8))
        self.ThreadType.setItemText(0, QtGui.QApplication.translate("ScrewMaker", "regular pitch", None, QtGui.QApplication.UnicodeUTF8))
        self.SimpleScrew.setText(QtGui.QApplication.translate("ScrewMaker", "Simple Screw (no thread at all!)", None, QtGui.QApplication.UnicodeUTF8))
        self.SymbolThread.setText(QtGui.QApplication.translate("ScrewMaker", "Symbol Thread (not implemented yet)", None, QtGui.QApplication.UnicodeUTF8))
        self.RealThread.setText(QtGui.QApplication.translate("ScrewMaker", "Real Thread (takes time, may not work above M16)", None, QtGui.QApplication.UnicodeUTF8))
        self.MessageLabel.setText(QtGui.QApplication.translate("ScrewMaker", "Select your screw type", None, QtGui.QApplication.UnicodeUTF8))
        self.MessageLabel.setProperty("Errortext", QtGui.QApplication.translate("ScrewMaker", "Combination not implemented", None, QtGui.QApplication.UnicodeUTF8))
        self.MessageLabel.setProperty("OK_text", QtGui.QApplication.translate("ScrewMaker", "Screw is made", None, QtGui.QApplication.UnicodeUTF8))
        self.CreateButton.setText(QtGui.QApplication.translate("ScrewMaker", "create", None, QtGui.QApplication.UnicodeUTF8))


    def check_Data(self):
      FreeCAD.Console.PrintLog("Data checking" + self.NominalLength.currentText() + "\n")
      #set screw not ok
      M_text = "Select your screw type"
      ST_text = str(self.ScrewType.currentText())
      ST_text = ST_text.split(':')[0]
      ND_text = str(self.NominalDiameter.currentText())
      Type_text = ''
      if ST_text == 'ISO4017':
        table = iso4017head
        tab_len = iso4017length
        tab_range = iso4017range
        Type_text = 'Screw'

      if ST_text == 'EN1662':
        table = en1662def
        tab_len = en1662length
        tab_range = en1662range
        Type_text = 'Screw'
        
      if ST_text == 'EN1665':
        table = en1665def
        tab_len = en1665length
        tab_range = en1665range
        Type_text = 'Screw'
                
      if ST_text == 'ISO2009':
        table = iso2009def
        tab_len = iso2009length
        tab_range = iso2009range
        Type_text = 'Screw'
      if ST_text == 'ISO2010':
        table = iso2009def
        tab_len = iso2009length
        tab_range = iso2009range
        Type_text = 'Screw'
      if ST_text == 'ISO4762':
        table = iso4762def
        tab_len = iso4762length
        tab_range = iso4762range
        Type_text = 'Screw'

      if ST_text == 'ISO10642':
        table = iso10642def
        tab_len = iso10642length
        tab_range = iso10642range
        Type_text = 'Screw'


      if ST_text == 'ISO4014':
        table = iso4014head
        tab_len = iso4014length
        tab_range = iso4014range
        Type_text = 'Screw'
        
      if ST_text == 'ISO1207':
        table = iso1207def
        tab_len = iso1207length
        tab_range = iso1207range
        Type_text = 'Screw'
      if ST_text == 'ISO1580':
        table = iso1580def
        tab_len = iso2009length
        tab_range = iso2009range
        Type_text = 'Screw'

      if ST_text == 'ISO7045':
        table = iso7045def
        tab_len = iso7045length
        tab_range = iso7045range
        Type_text = 'Screw'

      if ST_text == 'ISO7046':
        table = iso7046def  # contains only cross recess data
        tab_len = iso7045length
        tab_range = iso7046range
        Type_text = 'Screw'

      if ST_text == 'ISO7047':
        table = iso2009def  
        tab_len = iso7045length
        tab_range = iso7046range
        Type_text = 'Screw'


      if ST_text == 'ISO7048':
        table = iso7048def
        tab_len = iso7048length
        tab_range = iso7048range
        Type_text = 'Screw'

      if ST_text == 'ISO7380':
        table = iso7380def
        tab_len = iso7380length
        tab_range = iso7380range
        Type_text = 'Screw'

      if ST_text == 'ISO14579':
        table = iso14579def
        tab_len = iso14579length
        tab_range = iso14579range
        Type_text = 'Screw'

      if ST_text == 'ISO14580':
        table = iso14580def
        tab_len = iso14580length
        tab_range = iso1207range
        Type_text = 'Screw'

      if ST_text == 'ISO14583':
        table = iso14583def
        tab_len = iso7045length
        tab_range = iso7046range
        Type_text = 'Screw'



      if ST_text == 'ISO7089':
        table = iso7089def
        Type_text = 'Washer'

      if ND_text not in table:
         ND_min, ND_max = standard_diameters[ST_text]
         M_text = ST_text+' has diameters from '+ ND_min +' to ' + ND_max + ' and not ' + ND_text +'!'
         self.ScrewAvailable = False
         # set scew not ok
      else:
         if Type_text == 'Screw':
            NL_text = str(self.NominalLength.currentText())
            NL_min, NL_max = tab_range[ND_text]
            NL_min_float = float(NL_min)
            NL_max_float = float(NL_max)
            NL_text_float = float(NL_text)
            if (NL_text_float<NL_min_float)or(NL_text_float>NL_max_float)or(NL_text not in tab_len):            
               M_text = ST_text+'-'+ ND_text +' has lengths from '+ NL_min +' to ' + NL_max + ' and not ' + NL_text +'!'
               self.ScrewAvailable = False
               # set screw not ok
            else:
               M_text = ST_text+'-'+ ND_text +'x'+ NL_text +' is in library available! '
               self.ScrewAvailable = True
               #set screw ok
         else: # Washers and Nuts
            M_text = ST_text+'-'+ ND_text +' is in library available! '
            self.ScrewAvailable = True
            #set washer/nut ok
      
      #print "Data checking: ", self.NominalLength.currentText(), "\n"
      self.MessageLabel.setText(QtGui.QApplication.translate("ScrewMaker", M_text, None, QtGui.QApplication.UnicodeUTF8))
      FreeCAD.Console.PrintLog("Set Check_result into text " + str(self.ScrewAvailable) + M_text + "\n")


    def createScrew(self):
        if self.ScrewAvailable:
             # first we check if valid numbers have been entered
            FreeCAD.Console.PrintLog("NominalLength: " + self.NominalLength.currentText() + "\n")
            FreeCAD.Console.PrintLog("NominalDiameter: " + self.NominalDiameter.currentText() + "\n")
            FreeCAD.Console.PrintLog("SimpleThread: " + str(self.SimpleScrew.isChecked()) + "\n")
            FreeCAD.Console.PrintLog("SymbolThread: " + str(self.SymbolThread.isChecked()) + "\n")
            FreeCAD.Console.PrintLog("RealThread: " + str(self.RealThread.isChecked()) + "\n")
                       
            ND_text = str(self.NominalDiameter.currentText())
            NL_text = str(self.NominalLength.currentText())
            ST_text = str(self.ScrewType.currentText())
            createScrewParams(ND_text, NL_text, ST_text, self.SymbolThread.isChecked(), self.RealThread.isChecked(), false)
   
    def createScrewParams(self, ND_text, NL_text, ST_text, symbolThread, realThread, shapeOnly):
        try:
            self.symbolThread = symbolThread
            self.realThread = realThread
            ST_text = ST_text.split(':')[0]
            dia = float(ND_text.lstrip('M'))
            l = float(NL_text)
            if ST_text == 'ISO4017':
               table = iso4017head
            if ST_text == 'ISO4014':
               table = iso4014head
            if ST_text == 'EN1662':
               table = en1662def
            if ST_text == 'EN1665':
               table = en1665def
            if ST_text == 'ISO2009':
               table = iso2009def
            if ST_text == 'ISO2010':
               table = iso2009def
            if ST_text == 'ISO4762':
               table = iso4762def
            if ST_text == 'ISO10642':
               table = iso10642def
            if ST_text == 'ISO1207':
               table = iso1207def
            if ST_text == 'ISO1580':
               table = iso1580def
            if ST_text == 'ISO7045':
               table = iso7045def
            if ST_text == 'ISO7046':
               table = iso7045def
            if ST_text == 'ISO7047':
               table = iso7045def
            if ST_text == 'ISO7048':
               table = iso7048def
            if ST_text == 'ISO7380':
               table = iso7380def
            if ST_text == 'ISO7089':
               table = iso7089def
            if ST_text == 'ISO14579':
               table = iso14579def
            if ST_text == 'ISO14580':
               table = iso14580def
            if ST_text == 'ISO14583':
               table = iso14583def
            if ND_text not in table:
               FreeCAD.Console.PrintLog("Combination of type "+ST_text \
                  + " and diameter " + ND_text +" not available!" + "\n")
            #self.MessageLabel.setText(QtGui.QApplication.translate("ScrewMaker", "not implemented", None, QtGui.QApplication.UnicodeUTF8))
            
        except ValueError:
            print "Error! nom_dia and length values must be valid numbers!"
        else:
            done = False
            if ST_text == 'ISO4017':
               FreeCAD.Console.PrintLog("screw Type ISO4017 selected "+ str(dia) +" "+ str(l) + "\n")
               screw = self.makeIso4017(ND_text,l)
               Type_text = 'Screw'
               done = True
            if ST_text == 'ISO4014':
               FreeCAD.Console.PrintLog("screw Type ISO4014 selected "+ str(dia) +" "+ str(l) + "\n")
               screw = self.makeIso4014(ND_text,l)
               Type_text = 'Screw'
               done = True
            if (ST_text == 'EN1662') or (ST_text == 'EN1665'):
               FreeCAD.Console.PrintLog("screw Type EN1662/EN1665 selected "+ str(dia) +" "+ str(l) + "\n")
               screw = self.makeEN1662(ST_text, ND_text,l)
               Type_text = 'Screw'
               done = True
            if (ST_text == 'ISO2009') or (ST_text == 'ISO2010'):
               FreeCAD.Console.PrintLog("screw Type ISO2009/10 selected "+ str(dia) +" "+ str(l) + "\n")
               screw = self.makeIso2009(ST_text, ND_text,l)
               Type_text = 'Screw'
               done = True
            if ST_text == 'ISO4762':
               FreeCAD.Console.PrintLog("screw Type ISO4762 selected "+ str(dia) +" "+ str(l) + "\n")
               screw = self.makeIso4762(ST_text, ND_text,l)
               Type_text = 'Screw'
               done = True
            if ST_text == 'ISO10642':
               FreeCAD.Console.PrintLog("screw Type ISO10642 selected "+ str(dia) +" "+ str(l) + "\n")
               screw = self.makeIso2009(ST_text, ND_text,l)
               Type_text = 'Screw'
               done = True
            if ST_text == 'ISO1207':
               FreeCAD.Console.PrintLog("screw Type ISO1207 selected "+ str(dia) +" "+ str(l) + "\n")
               screw = self.makeIso1207(ST_text, ND_text,l)
               Type_text = 'Screw'
               done = True
            if ST_text == 'ISO1580':
               FreeCAD.Console.PrintLog("screw Type ISO1580 selected "+ str(dia) +" "+ str(l) + "\n")
               screw = self.makeIso1580(ND_text,l)
               Type_text = 'Screw'
               done = True
            if ST_text == 'ISO7045':
               FreeCAD.Console.PrintLog("screw Type ISO7045 selected "+ str(dia) +" "+ str(l) + "\n")
               screw = self.makeIso7045(ST_text, ND_text,l)
               Type_text = 'Screw'
               done = True
            if ST_text == 'ISO7046':
               FreeCAD.Console.PrintLog("screw Type ISO7046 selected "+ str(dia) +" "+ str(l) + "\n")
               screw = self.makeIso2009(ST_text, ND_text,l)
               Type_text = 'Screw'
               done = True
            if ST_text == 'ISO7047':
               FreeCAD.Console.PrintLog("screw Type ISO7047 selected "+ str(dia) +" "+ str(l) + "\n")
               screw = self.makeIso2009(ST_text, ND_text,l)
               Type_text = 'Screw'
               done = True
            if ST_text == 'ISO7048':
               FreeCAD.Console.PrintLog("screw Type ISO7048 selected "+ str(dia) +" "+ str(l) + "\n")
               screw = self.makeIso1207(ST_text, ND_text, l)
               Type_text = 'Screw'
               done = True
            if ST_text == 'ISO7380':
               FreeCAD.Console.PrintLog("screw Type ISO7380 selected "+ str(dia) +" "+ str(l) + "\n")
               screw = self.makeIso7380(ND_text,l)
               Type_text = 'Screw'
               done = True
            if ST_text == 'ISO14579':
               FreeCAD.Console.PrintLog("screw Type ISO14579 selected "+ str(dia) +" "+ str(l) + "\n")
               screw = self.makeIso4762(ST_text, ND_text,l)
               Type_text = 'Screw'
               done = True
            if ST_text == 'ISO14580':
               FreeCAD.Console.PrintLog("screw Type ISO14580 selected "+ str(dia) +" "+ str(l) + "\n")
               screw = self.makeIso1207(ST_text, ND_text,l)
               Type_text = 'Screw'
               done = True
            if ST_text == 'ISO14583':
               FreeCAD.Console.PrintLog("screw Type ISO14583 selected "+ str(dia) +" "+ str(l) + "\n")
               screw = self.makeIso7045(ST_text, ND_text,l)
               Type_text = 'Screw'
               done = True
            if ST_text == 'ISO7089':
               FreeCAD.Console.PrintLog("washer Type ISO7089 selected "+ str(dia) + "\n")
               screw = self.makeIso7089(ND_text)
               Type_text = 'Washer'
               done = True
            if not done:
               FreeCAD.Console.PrintLog("No valid Screw Type!" +  "\n")
            if Type_text == 'Screw':
               label = ST_text + '-' + ND_text +'x'+ NL_text +'_'
            else:
               label = ST_text + '-' + ND_text.lstrip('M') +'_'
            if shapeOnly:
              return (screw, Type_text)
            doc=App.activeDocument()
            ScrewObj = doc.addObject("Part::Feature",label)
            #ScrewObj = doc.addObject("Part::Feature","Screw")
            ScrewObj.Shape=screw
            FreeCAD.Console.PrintLog("Placement: "+ str(ScrewObj.Placement) +"\n")
            self.moveScrew(ScrewObj)
            #ScrewObj.Label = label
            doc.recompute()
            # Part.show(screw)
            return ScrewObj
         
    def moveScrew(self, ScrewObj_m):
      FreeCAD.Console.PrintLog("In Move Screw: " + str(ScrewObj_m) + "\n")

      mylist = Gui.Selection.getSelectionEx()
      if (mylist.__len__() == 1):
         # check selection
         FreeCAD.Console.PrintLog("Selektionen: " + str(mylist.__len__()) + "\n")
         
         for o in Gui.Selection.getSelectionEx():
            #for s in o.SubElementNames:
               #FreeCAD.Console.PrintLog( "name: " + str(s) + "\n")
            for s in o.SubObjects:
               #FreeCAD.Console.PrintLog( "object: "+ str(s) + "\n")
              moveScrewToObject(ScrewObj_m, s, false, 0.0)
    
    def moveScrewToObject(self, ScrewObj_m, attachToObject, invert, offset):
        Pnt1 = None
        Axis1 = None
        Axis2 = None
        s = attachToObject
        if hasattr(s,"Curve"):
          #FreeCAD.Console.PrintLog( "The Object is a Curve!\n")
          if hasattr(s.Curve,"Center"):
              """
              FreeCAD.Console.PrintLog( "The object has a Center!\n")
              FreeCAD.Console.PrintLog( "Curve attribut. "+ str(s.__getattribute__('Curve')) + "\n")
              FreeCAD.Console.PrintLog( "Center: "+ str(s.Curve.Center) + "\n")
              FreeCAD.Console.PrintLog( "Axis: "+ str(s.Curve.Axis) + "\n")
              """
              Pnt1 = s.Curve.Center
              Axis1 = s.Curve.Axis
        if hasattr(s,'Surface'):
          #print 'the object is a face!'
          if hasattr(s.Surface,'Axis'):
              Axis1 = s.Surface.Axis
   
        if hasattr(s,'Point'):
          FreeCAD.Console.PrintLog( "the object seems to be a vertex! "+ str(s.Point) + "\n")
          Pnt1 = s.Point
              
        if (Axis1 != None):
          if invert:
            Axis1 = Base.Vector(0,0,0) - Axis1
          
          Pnt1 = Pnt1 + Axis1 * offset
          #FreeCAD.Console.PrintLog( "Got Axis1: " + str(Axis1) + "\n")
          Axis2 = Base.Vector(0.0,0.0,1.0)
          Axis2_minus = Base.Vector(0.0,0.0,-1.0)
            
          # Calculate angle
          if Axis1 == Axis2:
              normvec = Base.Vector(1.0,0.0,0.0)
              result = 0.0
          else:
              if Axis1 == Axis2_minus:
                  normvec = Base.Vector(1.0,0.0,0.0)
                  result = math.pi
              else:
                  normvec = Axis1.cross(Axis2) # Berechne Achse der Drehung = normvec
                  normvec.normalize() # Normalisieren fuer Quaternionenrechnung
                  #normvec_rot = normvec
                  result = DraftVecUtils.angle(Axis1, Axis2, normvec) # Winkelberechnung
          sin_res = math.sin(result/2.0)
          cos_res = math.cos(result/2.0)
          normvec.multiply(-sin_res) # Berechnung der Quaternionen-Elemente
          #FreeCAD.Console.PrintLog( "Winkel = "+ str(math.degrees(result)) + "\n")
          #FreeCAD.Console.PrintLog("Normalvektor: "+ str(normvec) + "\n")
            
          pl = FreeCAD.Placement()
          pl.Rotation = (normvec.x,normvec.y,normvec.z,cos_res) #Drehungs-Quaternion
          
          #FreeCAD.Console.PrintLog("pl mit Rot: "+ str(pl) + "\n")
          #neuPlatz = Part2.Object.Placement.multiply(pl)
          neuPlatz = ScrewObj_m.Placement
          #FreeCAD.Console.PrintLog("die Position     "+ str(neuPlatz) + "\n")
          neuPlatz.Rotation = pl.Rotation.multiply(ScrewObj_m.Placement.Rotation)
          neuPlatz.move(Pnt1)
          #FreeCAD.Console.PrintLog("die rot. Position: "+ str(neuPlatz) + "\n")



     # make Washer
    def makeIso7089(self,ThreadType ='M6'):
      dia=float(ThreadType.lstrip('M'))
      FreeCAD.Console.PrintLog("die Scheibe mit dia: " + str(dia) + "\n")
      d1_min, d2_max, h, h_max = iso7089def[ThreadType]

      FreeCAD.Console.PrintLog("die Scheibe mit d1_min: " + str(d1_min) + "\n")

      #Washer Points  
      Pnt0 = Base.Vector(d1_min/2.0,0.0,h_max)
      Pnt2 = Base.Vector(d2_max/2.0,0.0,h_max)
      Pnt3 = Base.Vector(d2_max/2.0,0.0,0.0)      
      Pnt4 = Base.Vector(d1_min/2.0,0.0,0.0)
      
      edge1 = Part.makeLine(Pnt0,Pnt2)
      edge2 = Part.makeLine(Pnt2,Pnt3)
      edge3 = Part.makeLine(Pnt3,Pnt4)
      edge4 = Part.makeLine(Pnt4,Pnt0)
      FreeCAD.Console.PrintLog("Edges made Pnt2: " + str(Pnt2) + "\n")

      aWire=Part.Wire([edge1,edge2,edge3,edge4])
      #Part.show(aWire)
      aFace =Part.Face(aWire)
      head = aFace.revolve(Base.Vector(0.0,0.0,0.0),Base.Vector(0.0,0.0,1.0),360)
      FreeCAD.Console.PrintLog("Washer revolved: " + str(dia) + "\n")

      return head



     # make Pan head slotted screw Code is nearly identical to iso1207
    def makeIso1580(self,ThreadType ='M6',l=25.0):
      dia=float(ThreadType.lstrip('M'))
      #FreeCAD.Console.PrintLog("der Kopf mit l: " + str(l) + "\n")
      #P, a, b, dk, dk_mean, da, k, n_min, r, t_min, x = iso1580def[ThreadType]
      P, a, b, dk_max, da, k, n_min, r, rf, t_min, x = iso1580def[ThreadType]
      #FreeCAD.Console.PrintLog("der Kopf mit iso: " + str(dk_max) + "\n")
      
      #Length for calculation of head fillet
      r_fil = rf
      beta = math.radians(5.0)   # angle of pan head edge
      alpha = math.radians(90.0 - (90.0+5.0)/2.0)
      tan_beta = math.tan(beta)      
      # top head diameter without fillet
      rK_top = dk_max/2.0 - k * tan_beta     
      fillet_center_x = rK_top - r_fil + r_fil * tan_beta 
      fillet_center_z = k - r_fil
      fillet_arc_x = fillet_center_x + r_fil * math.sin(alpha)
      fillet_arc_z = fillet_center_z + r_fil * math.cos(alpha)
      #FreeCAD.Console.PrintLog("rK_top: " + str(rK_top) + "\n")

      if (b > (l - 3.0*P)):
         bmax = l-3.0*P
      else:
         bmax = b
      turns = round((bmax+P)/P) # number of thread turns
      a_real = l-turns*P  # starting point of thread
      sqrt2_ = 1.0/math.sqrt(2.0)

      #Head Points  
      Pnt0 = Base.Vector(0.0,0.0,k)
      Pnt2 = Base.Vector(fillet_center_x,0.0,k)
      Pnt3 = Base.Vector(fillet_arc_x,0.0,fillet_arc_z)      
      Pnt4 = Base.Vector(fillet_center_x + r_fil*math.cos(beta),0.0,fillet_center_z+ r_fil * math.sin(beta))
      Pnt5 = Base.Vector(dk_max/2.0,0.0,0.0)
      Pnt6 = Base.Vector(dia/2.0+r,0.0,0.0)     #start of fillet between head and shank
      Pnt7 = Base.Vector(dia/2.0+r-r*sqrt2_,0.0,-r+r*sqrt2_) #arc-point of fillet
      Pnt8 = Base.Vector(dia/2.0,0.0,-r)        # end of fillet
      Pnt9 = Base.Vector(dia/2.0,0.0,-a_real)        # Start of thread
      #FreeCAD.Console.PrintLog("Points defined fillet_center_x: " + str(fillet_center_x) + "\n")
      
      edge1 = Part.makeLine(Pnt0,Pnt2)
      edge2 = Part.Arc(Pnt2,Pnt3,Pnt4).toShape()
      edge3 = Part.makeLine(Pnt4,Pnt5)
      edge4 = Part.makeLine(Pnt5,Pnt6)
      edge5 = Part.Arc(Pnt6,Pnt7,Pnt8).toShape()
      edge6 = Part.makeLine(Pnt8,Pnt9)
      #FreeCAD.Console.PrintLog("Edges made fillet_center_z: " + str(fillet_center_z) + "\n")
      
      # bolt points
      PntB1 = Base.Vector(dia/2.0,0.0,-l-P)
      PntB2 = Base.Vector(0.0,0.0,-l-P)
      
      edgeB1 = Part.makeLine(Pnt9,PntB1)
      edgeB2 = Part.makeLine(PntB1,PntB2)
      edgeZ0 = Part.makeLine(PntB2,Pnt0)
      
      aWire=Part.Wire([edge1,edge2,edge3,edge4,edge5,edge6, \
          edgeB1, edgeB2, edgeZ0])
      #Part.show(aWire)
      aFace =Part.Face(aWire)
      head = aFace.revolve(Base.Vector(0.0,0.0,0.0),Base.Vector(0.0,0.0,1.0),360)
      #FreeCAD.Console.PrintLog("der Kopf mit revolve: " + str(dia) + "\n")

      #Parameter for slot-recess: dk_max, n_min, k, t_min
      slot = Part.makePlane(dk_max, n_min, \
          Base.Vector(dk_max/2.0,-n_min/2.0,k),Base.Vector(0.0,0.0,-1.0))
      slot = slot.extrude(Base.Vector(0.0,0.0,-t_min))
      #Part.show(slot)
      head = head.cut(slot)
      #FreeCAD.Console.PrintLog("der Kopf geschnitten: " + str(dia) + "\n")
      
      if self.realThread:
         head = self.cutIsoThread(head, dia, P, turns, l)
         
      #cyl = self.cutChamfer(dia, P, l)
      cyl = Part.makeCylinder(dia/2.0,P,Base.Vector(0.0,0.0,-l-P),Base.Vector(0.0,0.0,1.0),360)
   
      head = head.cut(cyl)
      return head

    # ISO 7045 Pan head screws with type H or type Z cross recess
    # ISO 14583 Hexalobular socket pan head screws  
    def makeIso7045(self, SType ='ISO7045', ThreadType ='M6',l=25.0):
      dia=float(ThreadType.lstrip('M'))
      #FreeCAD.Console.PrintLog("der Kopf mit l: " + str(l) + "\n")
      P, a, b, dk_max,da, k, r, rf, x, cT, mH, mZ  = iso7045def[ThreadType]
      #FreeCAD.Console.PrintLog("der Kopf mit iso: " + str(dk_max) + "\n")



      #Lengths and angles for calculation of head rounding
      beta = math.asin(dk_max /2.0 / rf)   # angle of head edge
      #print 'beta: ', math.degrees(beta)
      tan_beta = math.tan(beta)      


      if SType == 'ISO14583':
         tt, A, t_mean = iso14583def[ThreadType]
         beta_A = math.asin(A/2.0 / rf)   # angle of recess edge
         tan_beta_A = math.tan(beta_A)

         alpha = (beta_A + beta)/2.0 # half angle
         #print 'alpha: ', math.degrees(alpha)
         # heigth of head edge
         he = k - A/2.0/tan_beta_A + (dk_max/2.0) / tan_beta    
         #print 'he: ', he
         h_arc_x = rf * math.sin(alpha) 
         h_arc_z = k - A/2.0/tan_beta_A + rf * math.cos(alpha)
         #FreeCAD.Console.PrintLog("h_arc_z: " + str(h_arc_z) + "\n")
      else:
         alpha = beta/2.0 # half angle
         #print 'alpha: ', math.degrees(alpha)
         # heigth of head edge
         he = k - rf + (dk_max/2.0) / tan_beta    
         #print 'he: ', he
         h_arc_x = rf * math.sin(alpha) 
         h_arc_z = k - rf + rf * math.cos(alpha)
         #FreeCAD.Console.PrintLog("h_arc_z: " + str(h_arc_z) + "\n")
      
      if (b > (l - 3.0*P)):
         bmax = l- 3.0*P
      else:
         bmax = b
      turns = round((bmax+P)/P) # number of thread turns
      a_real = l-turns*P  # starting point of thread
      sqrt2_ = 1.0/math.sqrt(2.0)
      
      #Head Points  
      Pnt0 = Base.Vector(0.0,0.0,k)
      Pnt1 = Base.Vector(h_arc_x,0.0,h_arc_z)
      Pnt2 = Base.Vector(dk_max/2.0,0.0,he)      
      Pnt3 = Base.Vector(dk_max/2.0,0.0,0.0)
      Pnt4 = Base.Vector(dia/2.0+r,0.0,0.0)     #start of fillet between head and shank
      Pnt5 = Base.Vector(dia/2.0+r-r*sqrt2_,0.0,-r+r*sqrt2_) #arc-point of fillet
      Pnt6 = Base.Vector(dia/2.0,0.0,-r)        # end of fillet
      Pnt7 = Base.Vector(dia/2.0,0.0,-a_real)        # Start of thread
      #FreeCAD.Console.PrintLog("Points defined h_arc_z: " + str(h_arc_z) + "\n")


      if (SType == 'ISO14583'):
         Pnt0 = Base.Vector(0.0,0.0,k-A/4.0)
         PntCham = Base.Vector(A/2.0,0.0,k)
         edgeCham1 = Part.makeLine(Pnt0,PntCham)    
         edgeCham2 = Part.Arc(PntCham,Pnt1,Pnt2).toShape()   
         edge1 = Part.Wire([edgeCham1,edgeCham2]) 
      else:
         Pnt0 = Base.Vector(0.0,0.0,k)
         edge1 = Part.Arc(Pnt0,Pnt1,Pnt2).toShape()  # make round head


      
      #edge1 = Part.Arc(Pnt0,Pnt1,Pnt2).toShape()
      edge2 = Part.makeLine(Pnt2,Pnt3)
      edge3 = Part.makeLine(Pnt3,Pnt4)
      edge4 = Part.Arc(Pnt4,Pnt5,Pnt6).toShape()
      edge5 = Part.makeLine(Pnt6,Pnt7)
      #FreeCAD.Console.PrintLog("Edges made h_arc_z: " + str(h_arc_z) + "\n")
      
      # bolt points
      PntB1 = Base.Vector(dia/2.0,0.0,-l-P)
      PntB2 = Base.Vector(0.0,0.0,-l-P)
      
      edgeB1 = Part.makeLine(Pnt7,PntB1)
      edgeB2 = Part.makeLine(PntB1,PntB2)
      edgeZ0 = Part.makeLine(PntB2,Pnt0)
      
      aWire=Part.Wire([edge1,edge2,edge3,edge4,edge5, \
          edgeB1, edgeB2, edgeZ0])
      #Part.show(aWire)
      aFace =Part.Face(aWire)
      head = aFace.revolve(Base.Vector(0.0,0.0,0.0),Base.Vector(0.0,0.0,1.0),360)
      #FreeCAD.Console.PrintLog("der Kopf mit revolve: " + str(dia) + "\n")
   
      if (SType == 'ISO14583'):
         recess = self.makeIso10664(tt, t_mean, k)

      else:
         #Lengths and angles for calculation of recess positioning
         beta_cr = math.asin(mH /2.0 / rf)   # angle of recess edge
         tan_beta_cr = math.tan(beta_cr)      
         # heigth of cross recess cutting
         hcr = k - rf + (mH/2.0) / tan_beta_cr
         #print 'hcr: ', hcr
         
         #Parameter for cross-recess type H: cT, mH
         recess = self.makeCross_H(cT, mH, hcr)
      head = head.cut(recess)
      #FreeCAD.Console.PrintLog("der Kopf geschnitten: " + str(dia) + "\n")
      
      if self.realThread:
         head = self.cutIsoThread(head, dia, P, turns, l)
   
      #cyl = self.cutChamfer(dia, P, l)
      cyl = Part.makeCylinder(dia/2.0,P,Base.Vector(0.0,0.0,-l-P),Base.Vector(0.0,0.0,1.0),360)
      
      head = head.cut(cyl)
      return head


     # make Cheese head screw
     # ISO 1207 slotted screw
     # ISO 7048 cross recessed screw
     # ISO 14580 Hexalobular socket cheese head screws
    def makeIso1207(self,SType ='ISO1207', ThreadType ='M6',l=25.0):
      dia=float(ThreadType.lstrip('M'))
      FreeCAD.Console.PrintLog("der Kopf mit l: " + str(l) + "\n")
      if (SType == 'ISO1207') or (SType == 'ISO14580'):
         P, a, b, dk, dk_mean, da, k, n_min, r, t_min, x = iso1207def[ThreadType]
      if SType == 'ISO7048':
         P, a, b, dk, dk_mean, da, k, r, x, cT, mH, mZ  = iso7048def[ThreadType]
      if (SType == 'ISO14580'):
         tt, k, A, t_min = iso14580def[ThreadType]

      FreeCAD.Console.PrintLog("der Kopf mit iso: " + str(dk) + "\n")
      
      #Length for calculation of head fillet
      r_fil = r*2.0
      beta = math.radians(5.0)   # angle of cheese head edge
      alpha = math.radians(90.0 - (90.0+5.0)/2.0)
      tan_beta = math.tan(beta)      
      # top head diameter without fillet
      rK_top = dk/2.0 - k * tan_beta     
      fillet_center_x = rK_top - r_fil + r_fil * tan_beta 
      fillet_center_z = k - r_fil
      fillet_arc_x = fillet_center_x + r_fil * math.sin(alpha)
      fillet_arc_z = fillet_center_z + r_fil * math.cos(alpha)
      #FreeCAD.Console.PrintLog("rK_top: " + str(rK_top) + "\n")

      if (b > (l - 1.0*P)):
         bmax = l - 1.0*P
         turns = round((bmax-0.5*P)/P) # number of thread turns
         a_real = l-(turns+0.7)*P  # starting point of thread
      else:
         bmax = b
         turns = round((bmax+P)/P) # number of thread turns
         a_real = l-turns*P  # starting point of thread
      sqrt2_ = 1.0/math.sqrt(2.0)

      #Head Points  
      Pnt2 = Base.Vector(fillet_center_x,0.0,k)
      Pnt3 = Base.Vector(fillet_arc_x,0.0,fillet_arc_z)      
      Pnt4 = Base.Vector(fillet_center_x + r_fil*math.cos(beta),0.0,fillet_center_z+ r_fil * math.sin(beta))
      Pnt5 = Base.Vector(dk/2.0,0.0,0.0)
      Pnt6 = Base.Vector(dia/2.0+r,0.0,0.0)     #start of fillet between head and shank
      Pnt7 = Base.Vector(dia/2.0+r-r*sqrt2_,0.0,-r+r*sqrt2_) #arc-point of fillet
      Pnt8 = Base.Vector(dia/2.0,0.0,-r)        # end of fillet
      Pnt9 = Base.Vector(dia/2.0,0.0,-a_real)        # Start of thread
      #FreeCAD.Console.PrintLog("Points defined fillet_center_x: " + str(fillet_center_x) + "\n")

      if (SType == 'ISO14580'):
         Pnt0 = Base.Vector(0.0,0.0,k-A/4.0)
         PntCham = Base.Vector(A/2.0,0.0,k)
         edgeCham1 = Part.makeLine(Pnt0,PntCham)    
         edgeCham2 = Part.makeLine(PntCham,Pnt2)    
         edge1 = Part.Wire([edgeCham1,edgeCham2]) # make head with countersunk
      else:
         Pnt0 = Base.Vector(0.0,0.0,k)
         edge1 = Part.makeLine(Pnt0,Pnt2)  # make flat head
      
      edge2 = Part.Arc(Pnt2,Pnt3,Pnt4).toShape()
      edge3 = Part.makeLine(Pnt4,Pnt5)
      edge4 = Part.makeLine(Pnt5,Pnt6)
      edge5 = Part.Arc(Pnt6,Pnt7,Pnt8).toShape()
      edge6 = Part.makeLine(Pnt8,Pnt9)
      #FreeCAD.Console.PrintLog("Edges made fillet_center_z: " + str(fillet_center_z) + "\n")
      
      # bolt points
      PntB1 = Base.Vector(dia/2.0,0.0,-l-P)
      PntB2 = Base.Vector(0.0,0.0,-l-P)
      
      edgeB1 = Part.makeLine(Pnt9,PntB1)
      edgeB2 = Part.makeLine(PntB1,PntB2)
      edgeZ0 = Part.makeLine(PntB2,Pnt0)
      
      aWire=Part.Wire([edge1,edge2,edge3,edge4,edge5,edge6, \
          edgeB1, edgeB2, edgeZ0])
      #Part.show(aWire)
      aFace =Part.Face(aWire)
      head = aFace.revolve(Base.Vector(0.0,0.0,0.0),Base.Vector(0.0,0.0,1.0),360.0)
      FreeCAD.Console.PrintLog("der Kopf mit revolve: " + str(dia) + "\n")
      
      if SType == 'ISO1207':
         #Parameter for slot-recess: dk, n_min, k, t_min
         recess = Part.makePlane(dk, n_min, \
             Base.Vector(dk/2.0,-n_min/2.0,k),Base.Vector(0.0,0.0,-1.0))
         recess = recess.extrude(Base.Vector(0.0,0.0,-t_min))
      if SType == 'ISO7048':
         recess = self.makeCross_H(cT, mH, k)
      if (SType == 'ISO14580'):
         recess = self.makeIso10664(tt, t_min, k)

      
      if self.realThread:
         head = self.cutIsoThread(head, dia, P, turns, l)

      #Part.show(slot)
      head = head.cut(recess)
      FreeCAD.Console.PrintLog("der Kopf geschnitten: " + str(dia) + "\n")

         
      #cyl = self.cutChamfer(dia, P, l)
      cyl = Part.makeCylinder(dia/2.0,P,Base.Vector(0.0,0.0,-l-P),Base.Vector(0.0,0.0,1.0),360.0)
      FreeCAD.Console.PrintLog("jetzt Ende schneiden: " + str(dia) + "\n")
   
      head = head.cut(cyl)
      return head


	# make the ISO 4017 Hex-head-screw	
    def makeIso4017(self,ThreadType ='M6',l=25.0):
      dia=float(ThreadType.lstrip('M'))
      FreeCAD.Console.PrintLog("der Kopf mit l: " + str(l) + "\n")
      P, c, dw, e,k,r,s = iso4017head[ThreadType]
      FreeCAD.Console.PrintLog("der Kopf mit iso: " + str(c) + "\n")
      cham = (e-s)*math.sin(math.radians(15)) # needed for chamfer at head top
      #cham_t = P*math.sqrt(3.0)/2.0*17.0/24.0
      turns = round((l-2*P)/P) # number of thread turns
      a = l-turns*P  # starting point of thread
      sqrt2_ = 1.0/math.sqrt(2.0)

      #Head Points  Usage of k, s, cham, c, dw, dia, r, a
      FreeCAD.Console.PrintLog("der Kopf mit math a: " + str(a) + "\n")
      Pnt0 = Base.Vector(0.0,0.0,k)
      Pnt2 = Base.Vector(s/2.0,0.0,k)
      Pnt3 = Base.Vector(s/math.sqrt(3.0),0.0,k-cham)
      Pnt4 = Base.Vector(s/math.sqrt(3.0),0.0,c)
      Pnt5 = Base.Vector(dw/2.0,0.0,c)
      Pnt6 = Base.Vector(dw/2.0,0.0,0.0)
      Pnt7 = Base.Vector(dia/2.0+r,0.0,0.0)     #start of fillet between head and shank
      Pnt8 = Base.Vector(dia/2.0+r-r*sqrt2_,0.0,-r+r*sqrt2_) #arc-point of fillet
      Pnt9 = Base.Vector(dia/2.0,0.0,-r)        # end of fillet
      Pnt10 = Base.Vector(dia/2.0,0.0,-a)        # Start of thread
      
      edge1 = Part.makeLine(Pnt0,Pnt2)
      edge2 = Part.makeLine(Pnt2,Pnt3)
      edge3 = Part.makeLine(Pnt3,Pnt4)
      edge4 = Part.makeLine(Pnt4,Pnt5)
      edge5 = Part.makeLine(Pnt5,Pnt6)
      edge6 = Part.makeLine(Pnt6,Pnt7)
      edge7 = Part.Arc(Pnt7,Pnt8,Pnt9).toShape()
      edge8 = Part.makeLine(Pnt9,Pnt10)
      
      # bolt points
      PntB0 = Base.Vector(0.0,0.0,-a)
      PntB1 = Base.Vector(dia/2.0,0.0,-l-P)
      PntB2 = Base.Vector(0.0,0.0,-l-P)
      
      edgeB1 = Part.makeLine(Pnt10,PntB1)
      edgeB2 = Part.makeLine(PntB1,PntB2)
      edgeZ0 = Part.makeLine(PntB2,Pnt0)
      
      aWire=Part.Wire([edge1,edge2,edge3,edge4,edge5,edge6,edge7,edge8, \
          edgeB1, edgeB2, edgeZ0])
      aFace =Part.Face(aWire)
      head = aFace.revolve(Base.Vector(0.0,0.0,0.0),Base.Vector(0.0,0.0,1.0),360.0)
      #FreeCAD.Console.PrintLog("der Kopf mit revolve: " + str(dia) + "\n")

      # create cutting tool for hexagon head 
      # Parameters s, k, outer circle diameter =  e/2.0+10.0     
      extrude = self.makeHextool(s, k, s*2.0)

      # Part.show(extrude)
      head = head.cut(extrude)		   
      FreeCAD.Console.PrintLog("der Kopf geschnitten: " + str(dia) + "\n")
      
      if self.realThread:
         head = self.cutIsoThread(head, dia, P, turns, l)
         
      cyl = self.cutChamfer(dia, P, l)
      #cyl = Part.makeCylinder(dia/2.0,P,Base.Vector(0.0,0.0,-l-P),Base.Vector(0.0,0.0,1.0),360)
      FreeCAD.Console.PrintLog("vor Schnitt Ende: " + str(dia) + "\n")
      head = head.cut(cyl)
      return head

	# helper method to create the ISO 4014 Hex-head-bolt
    def makeIso4014(self,ThreadType ='M6',l=25.0):
      dia=float(ThreadType.lstrip('M'))
      FreeCAD.Console.PrintLog("der Kopf mit l: " + str(l) + "\n")
      P, b1, b2, b3, c, dw, e, k, r, s = iso4014head[ThreadType]
      if l<= 125.0:
         b = b1
      else:
         if l<= 200.0:
            b = b2
         else:
            b = b3
      
      FreeCAD.Console.PrintLog("der Kopf mit iso4014: " + str(c) + "\n")
      cham = (e-s)*math.sin(math.radians(15)) # needed for chamfer at head top
      turns = round((b+P)/P) # number of thread turns
      a = l-turns*P  # starting point of thread
      sqrt2_ = 1.0/math.sqrt(2.0)

      #Head Points
      FreeCAD.Console.PrintLog("der Kopf mit math a: " + str(a) + "\n")
      Pnt0 = Base.Vector(0.0,0.0,k)
      Pnt2 = Base.Vector(s/2.0,0.0,k)
      #Pnt3 = Base.Vector(e/2.0,0.0,k-cham)   #s/math.sqrt(3.0)
      #Pnt4 = Base.Vector(e/2.0,0.0,c)
      Pnt3 = Base.Vector(s/math.sqrt(3.0),0.0,k-cham)   #s/math.sqrt(3.0)
      Pnt4 = Base.Vector(s/math.sqrt(3.0),0.0,c)
      Pnt5 = Base.Vector(dw/2.0,0.0,c)
      Pnt6 = Base.Vector(dw/2.0,0.0,0.0)
      Pnt7 = Base.Vector(dia/2.0+r,0.0,0.0)     #start of fillet between head and shank
      Pnt8 = Base.Vector(dia/2.0+r-r*sqrt2_,0.0,-r+r*sqrt2_) #arc-point of fillet
      Pnt9 = Base.Vector(dia/2.0,0.0,-r)        # end of fillet
      Pnt10 = Base.Vector(dia/2.0,0.0,-a)        # Start of thread
      
      edge1 = Part.makeLine(Pnt0,Pnt2)
      edge2 = Part.makeLine(Pnt2,Pnt3)
      edge3 = Part.makeLine(Pnt3,Pnt4)
      edge4 = Part.makeLine(Pnt4,Pnt5)
      edge5 = Part.makeLine(Pnt5,Pnt6)
      edge6 = Part.makeLine(Pnt6,Pnt7)
      edge7 = Part.Arc(Pnt7,Pnt8,Pnt9).toShape()
      edge8 = Part.makeLine(Pnt9,Pnt10)
      
      # bolt points
      PntB0 = Base.Vector(0.0,0.0,-a)
      PntB1 = Base.Vector(dia/2.0,0.0,-l-P)
      PntB2 = Base.Vector(0.0,0.0,-l-P)
      
      edgeB1 = Part.makeLine(Pnt10,PntB1)
      edgeB2 = Part.makeLine(PntB1,PntB2)
      edgeZ0 = Part.makeLine(PntB2,Pnt0)
      
      aWire=Part.Wire([edge1,edge2,edge3,edge4,edge5,edge6,edge7,edge8, \
          edgeB1, edgeB2, edgeZ0])
      aFace =Part.Face(aWire)
      head = aFace.revolve(Base.Vector(0.0,0.0,0.0),Base.Vector(0.0,0.0,1.0),360)
      #FreeCAD.Console.PrintLog("der Kopf mit revolve: " + str(dia) + "\n")

      # create cutting tool for hexagon head 
      # Parameters s, k, outer circle diameter =  e/2.0+10.0     
      extrude = self.makeHextool(s, k, s*2.0)

      # Part.show(extrude)
      head = head.cut(extrude)		   
      #FreeCAD.Console.PrintLog("der Kopf geschnitten: " + str(dia) + "\n")
      
      if self.realThread:
         head = self.cutIsoThread(head, dia, P, turns, l)
         
      cyl = self.cutChamfer(dia, P, l)
      #cyl = Part.makeCylinder(dia/2.0,P,Base.Vector(0.0,0.0,-l-P),Base.Vector(0.0,0.0,1.0),360)
      head = head.cut(cyl)
      return head



    # EN 1662 Hex-head-bolt with flange - small series
    # EN 1665 Hexagon bolts with flange, heavy series
    def makeEN1662(self,SType ='EN1662', ThreadType ='M8',l=25.0):
      dia=float(ThreadType.lstrip('M'))
      FreeCAD.Console.PrintLog("der Kopf mit l: " + str(l) + "\n")
      if SType == 'EN1662':
         P, b0, b1, b2, b3, c, dc, dw, e, k, kw,f, r1, s = en1662def[ThreadType]
      else:
         P, b0, b1, b2, b3, c, dc, dw, e, k, kw,f, r1, s = en1665def[ThreadType]
      if l< b0:
         b = l - 2*P
      else:
         if l<= 125.0:
            b = b1
         else:
            if l<= 200.0:
               b = b2
            else:
               b = b3
      
      FreeCAD.Console.PrintLog("der Kopf mit isoEN1662: " + str(c) + "\n")
      cham = s*(2.0/math.sqrt(3.0)-1.0)*math.sin(math.radians(25)) # needed for chamfer at head top
      turns = round((b+P)/P) # number of thread turns
      a = l-turns*P  # starting point of thread
      sqrt2_ = 1.0/math.sqrt(2.0)
   
      # Flange is made with a radius of c
      beta = math.radians(25.0)
      tan_beta = math.tan(beta)
      
      # Calcualtion of Arc points of flange edge using dc and c
      arc1_x = dc/2.0 - c/2.0 + (c/2.0)*math.sin(beta)
      arc1_z = c/2.0 + (c/2.0)*math.cos(beta)
      
      hF = arc1_z + (arc1_x -s/2.0) * tan_beta  # height of flange at center
      
      kmean = arc1_z + (arc1_x - s/math.sqrt(3.0)) * tan_beta + kw * 1.1 + cham
      #kmean = k * 0.95
      
      #Hex-Head Points
      FreeCAD.Console.PrintLog("der Kopf mit math a: " + str(a) + "\n")
      PntH0 = Base.Vector(0.0,0.0,kmean*0.9)
      PntH1 = Base.Vector(s/2.0*0.8 - r1/2.0,0.0,kmean*0.9)
      PntH1a = Base.Vector(s/2.0*0.8-r1/2.0+r1/2.0*sqrt2_,0.0,kmean*0.9 +r1/2.0 -r1/2.0*sqrt2_)
      PntH1b = Base.Vector(s/2.0*0.8,0.0,kmean*0.9 +r1/2.0)
      PntH2 = Base.Vector(s/2.0*0.8,0.0,kmean -r1)
      PntH2a = Base.Vector(s/2.0*0.8+r1-r1*sqrt2_,0.0,kmean -r1 +r1*sqrt2_)
      PntH2b = Base.Vector(s/2.0*0.8 + r1 ,0.0,kmean)
      PntH3 = Base.Vector(s/2.0,0.0,kmean)
      PntH4 = Base.Vector(s/math.sqrt(3.0),0.0,kmean-cham)   #s/math.sqrt(3.0)
      PntH5 = Base.Vector(s/math.sqrt(3.0),0.0,c)
      PntH6 = Base.Vector(0.0,0.0,c)
      
      edgeH1 = Part.makeLine(PntH0,PntH1)
      edgeH2 = Part.Arc(PntH1,PntH1a,PntH1b).toShape()
      edgeH3 = Part.makeLine(PntH1b,PntH2)
      edgeH3a = Part.Arc(PntH2,PntH2a,PntH2b).toShape()   
      edgeH3b = Part.makeLine(PntH2b,PntH3)
      edgeH4 = Part.makeLine(PntH3,PntH4)
      edgeH5 = Part.makeLine(PntH4,PntH5)
      edgeH6 = Part.makeLine(PntH5,PntH6)
      edgeH7 = Part.makeLine(PntH6,PntH0)
      
      hWire=Part.Wire([edgeH1,edgeH2,edgeH3,edgeH3a,edgeH3b,edgeH4,edgeH5,edgeH6,edgeH7])
      hFace =Part.Face(hWire)
      hexhead = hFace.revolve(Base.Vector(0.0,0.0,0.0),Base.Vector(0.0,0.0,1.0),360)
      
      
      # Center of flange:
      Pnt0 = Base.Vector(0.0,0.0,hF)
      Pnt1 = Base.Vector(s/2.0,0.0,hF)
      
      # arc edge of flange:
      Pnt2 = Base.Vector(arc1_x,0.0,arc1_z)
      Pnt3 = Base.Vector(dc/2.0,0.0,c/2.0)
      Pnt4 = Base.Vector((dc-c)/2.0,0.0,0.0)
      
      Pnt5 = Base.Vector(dia/2.0+r1,0.0,0.0)     #start of fillet between head and shank
      Pnt6 = Base.Vector(dia/2.0+r1-r1*sqrt2_,0.0,-r1+r1*sqrt2_) #arc-point of fillet
      Pnt7 = Base.Vector(dia/2.0,0.0,-r1)        # end of fillet
      Pnt8 = Base.Vector(dia/2.0,0.0,-a)        # Start of thread
      
      edge1 = Part.makeLine(Pnt0,Pnt1)
      edge2 = Part.makeLine(Pnt1,Pnt2)
      edge3 = Part.Arc(Pnt2,Pnt3,Pnt4).toShape()
      edge4 = Part.makeLine(Pnt4,Pnt5)
      edge5 = Part.Arc(Pnt5,Pnt6,Pnt7).toShape()
      edge6 = Part.makeLine(Pnt7,Pnt8)
      
      # bolt points
      PntB0 = Base.Vector(0.0,0.0,-a)
      PntB1 = Base.Vector(dia/2.0,0.0,-l-P)
      PntB2 = Base.Vector(0.0,0.0,-l-P)
      
      edgeB1 = Part.makeLine(Pnt8,PntB1)
      edgeB2 = Part.makeLine(PntB1,PntB2)
      edgeZ0 = Part.makeLine(PntB2,Pnt0)
      
      aWire=Part.Wire([edge1,edge2,edge3,edge4,edge5,edge6, \
          edgeB1, edgeB2, edgeZ0])
      aFace =Part.Face(aWire)
      head = aFace.revolve(Base.Vector(0.0,0.0,0.0),Base.Vector(0.0,0.0,1.0),360)
      #FreeCAD.Console.PrintLog("der Kopf mit revolve: " + str(dia) + "\n")
      
      # create cutting tool for hexagon head 
      # Parameters s, k, outer circle diameter =  dc   
      extrude = self.makeHextool(s, k, dc)
      
      #Part.show(extrude)
      hexhead = hexhead.cut(extrude)		   
      #FreeCAD.Console.PrintLog("der Kopf geschnitten: " + str(dia) + "\n")
      #Part.show(hexhead)
      head = head.fuse(hexhead)
      
      if self.realThread:
         head = self.cutIsoThread(head, dia, P, turns, l)
         
      cyl = self.cutChamfer(dia, P, l)
      head = head.cut(cyl)
      return head






    # make ISO 2009 Slotted countersunk flat head screws
    # make ISO 2010 Slotted raised countersunk head screws
    # also used for ISO 7046 countersunk flat head screws with H cross recess
    # also used for ISO 7047 raised countersunk head screws with H cross recess
    # also used for ISO 10642 Hexagon socket countersunk head screws
    def makeIso2009(self, SType ='ISO2009', ThreadType ='M6',l=25.0):
      dia=float(ThreadType.lstrip('M'))
      #FreeCAD.Console.PrintLog("der 2009Kopf mit l: " + str(l) + "\n")
      if (SType == 'ISO10642'):
          P,b,dk_theo,dk_mean,da, ds_min, e, k, r, s_mean, t, w =iso10642def[ThreadType]
          ht = - s_mean / math.sqrt(3.0)
          a = 2*P
          t_mean = t
      else:
          P, a, b, dk_theo, dk_mean, k, n_min, r, t_mean, x = iso2009def[ThreadType]
          ht = 0.0 # Head heigth of flat head
      if SType == 'ISO7046':
         cT, mH, mZ  = iso7046def[ThreadType]
      if (SType == 'ISO2010') or (SType == 'ISO7047'):
         rf, t_mean, cT, mH, mZ = Raised_countersunk_def[ThreadType]

         #Lengths and angles for calculation of head rounding
         beta = math.asin(dk_mean /2.0 / rf)   # angle of head edge
         tan_beta = math.tan(beta)      
         alpha = beta/2.0 # half angle
         # heigth of raised head top
         ht = rf - (dk_mean/2.0) / tan_beta
         #print 'he: ', he
         h_arc_x = rf * math.sin(alpha) 
         h_arc_z = ht - rf + rf * math.cos(alpha)
         FreeCAD.Console.PrintLog("h_arc_z: " + str(h_arc_z) + "\n")
         
      #FreeCAD.Console.PrintLog("der Kopf mit iso r: " + str(r) + "\n")
      cham = (dk_theo - dk_mean)/2.0
      rad225 = math.radians(22.5)
      rad45 = math.radians(45.0)
      rtan = r*math.tan(rad225)
      
      if (b > l - k -a):
         bmax = l-k-a
      else:
         bmax = b
      turns = round((bmax+P/2.0)/P) # number of thread turns
      a_real = l-turns*P  # starting point of thread
         
      #Head Points
      #FreeCAD.Console.PrintLog("der Kopf mit math rtan: " + str(rtan) + "\n")
      Pnt0 = Base.Vector(0.0,0.0,ht)
      Pnt1 = Base.Vector(dk_mean/2.0,0.0,0.0)
      Pnt2 = Base.Vector(dk_mean/2.0,0.0,-cham)
      Pnt3 = Base.Vector(dia/2.0+r-r*math.cos(rad45),0.0,-k-rtan+r*math.sin(rad45))
      
      # Arc-points
      Pnt4 = Base.Vector(dia/2.0+r-r*(math.cos(rad225)),0.0,-k-rtan+r*math.sin(rad225))
      Pnt5 = Base.Vector(dia/2.0,0.0,-k-rtan)
      #FreeCAD.Console.PrintLog("last Arc point: " + str(-k-rtan) + "\n")
      Pnt6 = Base.Vector(dia/2.0,0.0,-a_real)

      if (SType == 'ISO2010') or (SType == 'ISO7047'): # make raised head rounding
         Pnt0arc = Base.Vector(h_arc_x,0.0,h_arc_z)
         edge1 = Part.Arc(Pnt0,Pnt0arc,Pnt1).toShape()     
      else:
         if (SType == 'ISO10642'):
            PntCham = Base.Vector(-ht,0.0,0.0)
            edgeCham1 = Part.makeLine(Pnt0,PntCham)    
            edgeCham2 = Part.makeLine(PntCham,Pnt1)    
            edge1 = Part.Wire([edgeCham1,edgeCham2]) 
         else:
            edge1 = Part.makeLine(Pnt0,Pnt1)  # make flat head
         
      edge2 = Part.makeLine(Pnt1,Pnt2)
      edge3 = Part.makeLine(Pnt2,Pnt3)
      #FreeCAD.Console.PrintLog("before bolt points: " + str(cham) + "\n")
      
      # bolt points
      PntB1 = Base.Vector(dia/2.0,0.0,-l-P)
      PntB2 = Base.Vector(0.0,0.0,-l-P)
      #PntB3 = Base.Vector(0.0,0.0,-l)

      edgeArc = Part.Arc(Pnt3,Pnt4,Pnt5).toShape()     
      edgeArc1 = Part.makeLine(Pnt3,Pnt4)     
      edgeArc2 = Part.makeLine(Pnt4,Pnt5)
      edge6 = Part.makeLine(Pnt5,Pnt6)
      edgeB0 = Part.makeLine(Pnt6,PntB1)
      edgeB1 = Part.makeLine(PntB1,PntB2)
      #edgeB2 = Part.makeLine(PntB2,PntB3)
      edgeZ0 = Part.makeLine(PntB2,Pnt0)
      
      
      aWire=Part.Wire([edge1,edge2,edge3,edgeArc,edge6, \
          edgeB0, edgeB1, edgeZ0])
      #Part.show(aWire)
      aFace =Part.Face(aWire)
      head = aFace.revolve(Base.Vector(0.0,0.0,0.0),Base.Vector(0.0,0.0,1.0),360)
      #FreeCAD.Console.PrintLog("der Kopf mit revolve: " + str(dia) + "\n")
      
      if (SType == 'ISO2009') or (SType == 'ISO2010'):
         #Parameter for slot-recess: dk_theo, n_min, offset, t_mean
         recess = Part.makePlane(dk_theo, n_min, \
             Base.Vector(dk_theo/2.0,-n_min/2.0,ht),Base.Vector(0.0,0.0,-1.0))
         recess = recess.extrude(Base.Vector(0.0,0.0,-t_mean))

      if (SType == 'ISO7046') or (SType == 'ISO7047'):
         recess = self.makeCross_H(cT, mH, ht)

      if SType == 'ISO10642':
         recess = self.makeAllen(s_mean, t_mean, dk_mean, 0.0 )

      head = head.cut(recess)

      if self.realThread:
         # cut the thread
         head = self.cutIsoThread(head, dia, P, turns, l)
         
      if SType == 'ISO10642':
         cyl = self.cutChamfer(dia, P, l)
      else:
         cyl = Part.makeCylinder(dia/2.0,P,Base.Vector(0.0,0.0,-l-P),Base.Vector(0.0,0.0,1.0),360)
      head = head.cut(cyl)
            
      return head

    # make ISO 4762 Allan Screw head
    # ISO 14579 Hexalobular socket head cap screws
    def makeIso4762(self, SType ='ISO4762', ThreadType ='M6',l=25.0):
      dia=float(ThreadType.lstrip('M'))
      #FreeCAD.Console.PrintLog("der 4762Kopf mit l: " + str(l) + "\n")
      P, b, dk_max, da, ds_mean, e, lf, k, r, s_mean, t, v, dw, w = iso4762def[ThreadType]
      #FreeCAD.Console.PrintLog("der Kopf mit iso r: " + str(r) + "\n")
      if SType == 'ISO14579':
         tt, A, t = iso14579def[ThreadType]
         #Head Points 30° countersunk
         Pnt0 = Base.Vector(0.0,0.0,k-A/4.0) #Center Point for countersunk
         Pnt1 = Base.Vector(A/2.0,0.0,k)     #countersunk edge at head
      else:
         e_cham = 2.0 * s_mean / math.sqrt(3.0)
         #Head Points 45° countersunk
         Pnt0 = Base.Vector(0.0,0.0,k-e_cham/2.0) #Center Point for countersunk
         Pnt1 = Base.Vector(e_cham/2.0,0.0,k)     #countersunk edge at head

      
      sqrt2_ = 1.0/math.sqrt(2.0)
      #depth = s_mean / 3.0

      if (b > l - 3*P):
         bmax = l-3*P
      else:
         bmax = b
      turns = round((bmax+P)/P) # number of thread turns
      a_real = l-turns*P  # starting point of thread
           
      #rad30 = math.radians(30.0)
      #Head Points
      Pnt2 = Base.Vector(dk_max/2.0-v,0.0,k)   #start of fillet
      Pnt3 = Base.Vector(dk_max/2.0-v+v*sqrt2_,0.0,k-v+v*sqrt2_) #arc-point of fillet
      Pnt4 = Base.Vector(dk_max/2.0,0.0,k-v)   #end of fillet
      Pnt5 = Base.Vector(dk_max/2.0,0.0,(dk_max-dw)/2.0) #we have a chamfer here
      Pnt6 = Base.Vector(dw/2.0,0.0,0.0)           #end of chamfer
      Pnt7 = Base.Vector(dia/2.0+r,0.0,0.0)     #start of fillet between head and shank
      Pnt8 = Base.Vector(dia/2.0+r-r*sqrt2_,0.0,-r+r*sqrt2_) #arc-point of fillet
      Pnt9 = Base.Vector(dia/2.0,0.0,-r)        # end of fillet
      Pnt10 = Base.Vector(dia/2.0,0.0,-a_real)        # start of thread
      
      edge1 = Part.makeLine(Pnt0,Pnt1)
      edge2 = Part.makeLine(Pnt1,Pnt2)
      edge3 = Part.Arc(Pnt2,Pnt3,Pnt4).toShape()
      edge4 = Part.makeLine(Pnt4,Pnt5)
      edge5 = Part.makeLine(Pnt5,Pnt6)
      edge6 = Part.makeLine(Pnt6,Pnt7)
      edge7 = Part.Arc(Pnt7,Pnt8,Pnt9).toShape()
      edge8 = Part.makeLine(Pnt9,Pnt10)
      
      # bolt points
      PntB1 = Base.Vector(dia/2.0,0.0,-l-P)  # Chamfer is made with a cut later
      PntB2 = Base.Vector(0.0,0.0,-l-P)
      #PntB3 = Base.Vector(0.0,0.0,-l)

      edgeB0 = Part.makeLine(Pnt10,PntB1)
      edgeB1 = Part.makeLine(PntB1,PntB2)
      #edgeB2 = Part.makeLine(PntB2,PntB3)
      edgeZ0 = Part.makeLine(PntB2,Pnt0)
      
      
      aWire=Part.Wire([edge1,edge2,edge3,edge4,edge5,edge6,edge7,edge8, \
          edgeB0, edgeB1, edgeZ0])
      aFace =Part.Face(aWire)
      head = aFace.revolve(Base.Vector(0.0,0.0,0.0),Base.Vector(0.0,0.0,1.0),360)
      
      # The round part of the cutting tool, we need for the allan hex
      #PntH1 = Base.Vector(0.0,0.0,k)
      #PntH2 = Base.Vector(e_cham/2.0,0.0,k)
      #PntH3 = Base.Vector(e_cham/2.0,0.0,k-t)
      #PntH4 = Base.Vector(0.0,0.0,k-t-depth)
      
      #edgeH1 = Part.makeLine(PntH1,PntH2)
      #edgeH2 = Part.makeLine(PntH2,PntH3)
      #edgeH3 = Part.makeLine(PntH3,PntH4)
      #edgeH4 = Part.makeLine(PntH4,PntH1)
      #hWire=Part.Wire([edgeH1,edgeH2,edgeH3,edgeH4])
      #Part.show(hWire)
      #hFace =Part.Face(hWire)
      #roundtool = hFace.revolve(Base.Vector(0.0,0.0,k),Base.Vector(0.0,0.0,1.0),360)

      #extrude = self.makeHextool(s_mean, k, dk_max)
      #Part.show(extrude)
            
      #hextool = roundtool.cut(extrude)		   
      #FreeCAD.Console.PrintLog("der Kopf geschnitten: " + str(dia) + "\n")


      
      if SType == 'ISO14579':
         recess = self.makeIso10664(tt, t, k) # hexalobular recess
      else:
         recess = self.makeAllen(s_mean, t, dk_max, k )

      allenscrew = head.cut(recess)

      if self.realThread:
         # cut the thread
         allenscrew = self.cutIsoThread(allenscrew, dia, P, turns, l)
         
      cyl = self.cutChamfer(dia, P, l)
      #cyl = Part.makeCylinder(dia/2.0,P,Base.Vector(0.0,0.0,-l-P),Base.Vector(0.0,0.0,1.0),360)
      allenscrew = allenscrew.cut(cyl)
      
      return allenscrew


    # make ISO 7380 Button head Screw 
    def makeIso7380(self,ThreadType ='M6',l=25.0):
      dia=float(ThreadType.lstrip('M'))
      FreeCAD.Console.PrintLog("der 7380-Kopf mit l: " + str(l) + "\n")
      P, a, da, dk, dk_mean,s_mean, t_min, r, k, e, w = iso7380def[ThreadType]
      FreeCAD.Console.PrintLog("der Kopf mit iso r: " + str(r) + "\n")
      
      sqrt2_ = 1.0/math.sqrt(2.0)
      e_cham = 2.0 * s_mean / math.sqrt(3.0)
      depth = s_mean / 3.0
      
      #ak = -(k**2 + e_cham**2-dk**2)/(2*k)
      ak = -(4*k**2 + e_cham**2 - dk**2)/(8*k)
      rH = math.sqrt((dk/2.0)**2 + ak**2)
      #alpha = (math.atan((k + ak)/e_cham) + math.atan(ak/dk))/2
      alpha = (math.atan(2*(k + ak)/e_cham) + math.atan((2*ak)/dk))/2
      
      turns = round((l-1.1*P)/P) # number of thread turns
      a_real = l-turns*P  # starting point of thread
      
      FreeCAD.Console.PrintLog("Value ak: " + str(ak) + "\n")
           
      #Head Points
      Pnt0 = Base.Vector(0.0,0.0,k-e_cham/2.0) #Center Point for chamfer
      Pnt1 = Base.Vector(e_cham/2.0,0.0,k)     #inner chamfer edge at head
      Pnt2 = Base.Vector(rH*math.cos(alpha),0.0,-ak + rH*math.sin(alpha)) #arc-point of button
      Pnt3 = Base.Vector(dk/2.0,0.0,0.0)   #end of fillet
      Pnt4 = Base.Vector(dia/2.0+r,0.0,0.0)     #start of fillet between head and shank
      Pnt5 = Base.Vector(dia/2.0+r-r*sqrt2_,0.0,-r+r*sqrt2_) #arc-point of fillet
      Pnt6 = Base.Vector(dia/2.0,0.0,-r)        # end of fillet
      Pnt7 = Base.Vector(dia/2.0,0.0,-a_real)        # start of thread

      FreeCAD.Console.PrintLog("Points made, rH: " + str(rH) + "\n")

      
      edge1 = Part.makeLine(Pnt0,Pnt1)
      edge2 = Part.Arc(Pnt1,Pnt2,Pnt3).toShape()
      edge3 = Part.makeLine(Pnt3,Pnt4)
      edge4 = Part.Arc(Pnt4,Pnt5,Pnt6).toShape()
      edge5 = Part.makeLine(Pnt6,Pnt7)
      
      # bolt points
      PntB1 = Base.Vector(dia/2.0,0.0,-l-P)  # ISO7380 wants a chamfer here!!!
      PntB2 = Base.Vector(0.0,0.0,-l-P)      # we chamfer with the last cut!!!
      #PntB3 = Base.Vector(0.0,0.0,-l)

      edgeB0 = Part.makeLine(Pnt7,PntB1)
      edgeB1 = Part.makeLine(PntB1,PntB2)
      edgeZ0 = Part.makeLine(PntB2,Pnt0)
      
      
      aWire=Part.Wire([edge1,edge2,edge3,edge4,edge5, \
          edgeB0, edgeB1, edgeZ0])
      #Part.show(aWire)
      aFace =Part.Face(aWire)
      #Part.show(aFace)
      head = aFace.revolve(Base.Vector(0.0,0.0,0.0),Base.Vector(0.0,0.0,1.0),360)
      #Part.show(head)
      
      # The round part of the cutting tool, we need for the allan hex
      PntH1 = Base.Vector(0.0,0.0,k)
      PntH2 = Base.Vector(e_cham/2.0,0.0,k)
      PntH3 = Base.Vector(e_cham/2.0,0.0,k-t_min)
      PntH4 = Base.Vector(0.0,0.0,k-t_min-depth)
      
      edgeH1 = Part.makeLine(PntH1,PntH2)
      edgeH2 = Part.makeLine(PntH2,PntH3)
      edgeH3 = Part.makeLine(PntH3,PntH4)
      edgeH4 = Part.makeLine(PntH4,PntH1)
      hWire=Part.Wire([edgeH1,edgeH2,edgeH3,edgeH4])
      #Part.show(hWire)
      hFace =Part.Face(hWire)
      roundtool = hFace.revolve(Base.Vector(0.0,0.0,k),Base.Vector(0.0,0.0,1.0),360)

      extrude = self.makeHextool(s_mean, k, dk)
      #Part.show(extrude)
            
      hextool = roundtool.cut(extrude)		   
      FreeCAD.Console.PrintLog("der Kopf geschnitten: " + str(dia) + "\n")
      buttonscrew = head.cut(hextool)

      if self.realThread:
         # cut the thread
         buttonscrew = self.cutIsoThread(buttonscrew, dia, P, turns, l)
         
      cyl = self.cutChamfer(dia, P, l)
      #cyl = Part.makeCylinder(dia/2.0,P,Base.Vector(0.0,0.0,-l-P),Base.Vector(0.0,0.0,1.0),360)
      buttonscrew = buttonscrew.cut(cyl)
      
      return buttonscrew



    def makeHextool(self,s_hex, k_hex, cir_hex):
      # makes a cylinder with an inner hex hole, used as cutting tool
      # create hexagon
      mhex=Base.Matrix()
      mhex.rotateZ(math.radians(60.0))
      polygon = []
      vhex=Base.Vector(s_hex/math.sqrt(3.0),0.0,0.0)
      for i in range(6):
         polygon.append(vhex)
         vhex = mhex.multiply(vhex)
      polygon.append(vhex)
      hexagon = Part.makePolygon(polygon)
      # create circle
      circ=Part.makeCircle(cir_hex/2.0)
      # Create the face with the circle as outline and the hexagon as hole
      face=Part.Face([Part.Wire(circ),hexagon])
      
      # Extrude in z to create the final cutting tool
      exHex=face.extrude(Base.Vector(0.0,0.0,k_hex*1.1))
      # Part.show(exHex)
      return exHex

    def cutTooliso261(self, d, P, angle = False):
      # P pitch of thread, d nonminal diameter of thread (floats)
      H=P*math.cos(math.radians(30)) # H depth of thread
      r=d/2.0   #Nominal radius
      
      # points for screw cutting profile
      ps1 = (r + H/16.0,0.0,-P/2.0+P/32.0)
      ps2 = (r-H*5.0/8.0,0.0,-P/8.0)
      ps3 = (r-H*17.0/24.0,0.0,0.0) # Center of Arc
      ps4 = (r-H*5.0/8.0,0.0,+P/8.0)
      ps5 =  (r+ H/16.0,0.0,+P/2.0-P/32.0)    

      edge1 = Part.makeLine(ps1,ps2)
      edge2 = Part.Arc(FreeCAD.Vector(ps2),FreeCAD.Vector(ps3),FreeCAD.Vector(ps4)).toShape()
      edge3 = Part.makeLine(ps4,ps5)
      edge4 = Part.makeLine(ps5,ps1)

      alpha_rad = math.atan(H*17.0/24.0/P)
      alpha = math.degrees(alpha_rad)
      Hyp = P/math.cos(alpha_rad) # Parameter for the last turn (angle==True)
      tuning = 0.42
      if d>14:
         tuning = 0.40
    
      # This works for a diameter of 6
      # helix = Part.makeHelix(P,P,(d-H*26.0/24.0)/2.0,0) # make just one turn, length is identical to pitch
      if angle:
         FreeCAD.Console.PrintLog("last cut started: " + str(alpha_rad) + "\n")
         
         helix = Part.makeHelix(Hyp,Hyp,d*tuning,alpha) # make just one turn, length is identical to pitch
      else: 
         helix = Part.makeHelix(P,P,d*0.42,0) # make just one turn, length is identical to pitch
      
      cutProfile = Part.Wire([edge1,edge2,edge3,edge4])
      makeSolid=True
      isFrenet=True
      pipe = Part.Wire(helix).makePipeShell([cutProfile],makeSolid,isFrenet)
      # Part.show(pipe)
      return pipe


    def cutIsoThread(self, rawScrew, dia_cT, P_cT, turns_cT, l_cT):
      # Parameter object=head, dia, P, turns, l
      #FreeCAD.Console.PrintLog("vor cutTool: " + str(dia_cT) + "\n")
      cutTool=self.cutTooliso261(dia_cT, P_cT, False)
      #FreeCAD.Console.PrintLog("cutTool made: " + str(dia_cT) + "\n")
      rotations = int(turns_cT)
      cutTool.Placement.Base = Base.Vector(0.0,0.0,-l_cT-P_cT/2.0)
      FreeCAD.Console.PrintLog("cutTool placed, Rots: " + str(rotations) + "\n")
      
      for i in range(rotations):
         rawScrew = rawScrew.cut(cutTool)
         cutTool.Placement.Base = Base.Vector(0.0,0.0,-l_cT-P_cT/2.0+P_cT*(i+1.0))
         FreeCAD.Console.PrintLog("rotation: " + str(i) + "\n")
      lastCut = self.cutTooliso261(dia_cT, P_cT, True)
      lastCut.Placement.Base = Base.Vector(0.0,0.0,-l_cT-P_cT/2.0+P_cT*(i+1.0))
      threadedScrew = rawScrew.cut(lastCut)
      FreeCAD.Console.PrintLog("last cut done" + str(i) + "\n")
      return threadedScrew

    def cutChamfer(self, dia_cC, P_cC, l_cC):
      cham_t = P_cC*math.sqrt(3.0)/2.0*17.0/24.0
      PntC0 = Base.Vector(0.0,0.0,-l_cC)
      PntC1 = Base.Vector(dia_cC/2.0-cham_t,0.0,-l_cC)
      PntC2 = Base.Vector(dia_cC/2.0,0.0,-l_cC+cham_t)
      PntC3 = Base.Vector(dia_cC/2.0,0.0,-l_cC-P_cC)
      PntC4 = Base.Vector(0.0,0.0,-l_cC-P_cC)
      
      edgeC1 = Part.makeLine(PntC0,PntC1)
      edgeC2 = Part.makeLine(PntC1,PntC2)
      edgeC3 = Part.makeLine(PntC2,PntC3)
      edgeC4 = Part.makeLine(PntC3,PntC4)
      edgeC5 = Part.makeLine(PntC4,PntC0)
      CWire=Part.Wire([edgeC1,edgeC2,edgeC3,edgeC4,edgeC5])
      CFace =Part.Face(CWire)
      cyl = CFace.revolve(Base.Vector(0.0,0.0,0.0),Base.Vector(0.0,0.0,1.0),360)
      return cyl



    # cross recess type H
    def makeCross_H(self, CrossType = '2', m = 6.9, h = 0.0):
      # m = diameter of cross at top of screw at reference level for penetration depth
      b, e_mean, g, f_mean, r, t1, alpha, beta = iso4757def[CrossType]
      
      rad265 = math.radians(26.5)
      rad28 = math.radians(28.0)
      tg = (m-g)/2.0/math.tan(rad265) # depth at radius of g
      t_tot = tg + g/2.0 * math.tan(rad28)
      # print 'tg: ', tg,' t_tot: ', t_tot
      hm = m / 4.0
      
      Pnt0 = Base.Vector(0.0,0.0,hm)
      Pnt1 = Base.Vector(m/2.0,0.0,hm)
      # Hier müssen noch der Radius rein
      Pnt2 = Base.Vector(m/2.0,0.0,0.0)
      Pnt3 = Base.Vector(0.0,0.0,0.0)
      Pnt3 = Base.Vector(0.0,0.0,0.0)
   
      Pnt4 = Base.Vector(g/2.0,0.0,-tg)
      Pnt5 = Base.Vector(0.0,0.0,-t_tot)
   
      edge1 = Part.makeLine(Pnt0,Pnt1)
      edge2 = Part.makeLine(Pnt1,Pnt2)
      edge3 = Part.makeLine(Pnt2,Pnt4)
      edge4 = Part.makeLine(Pnt4,Pnt5)
      edge5 = Part.makeLine(Pnt5,Pnt0)
      FreeCAD.Console.PrintLog("Edges made Pnt2: " + str(Pnt2) + "\n")
      
      aWire=Part.Wire([edge1,edge2,edge3,edge4,edge5])
      #Part.show(aWire)
      aFace =Part.Face(aWire)
      cross = aFace.revolve(Base.Vector(0.0,0.0,0.0),Base.Vector(0.0,0.0,1.0),360)
      FreeCAD.Console.PrintLog("Washer revolved: " + str(e_mean) + "\n")
   
      # the need to cut 4 corners out of the above shape.
      # Definition of corner
      # The angles 92 degrees and alpha are defined on a plane which has 
      # an angle of beta against our coordinate system.
      # The projected angles are needed for easier calculation!
      rad_alpha = math.radians(alpha/2.0)
      rad92 = math.radians(92.0/2.0)
      rad_beta = math.radians(beta)
      
      rad_alpha_p = math.atan(math.tan(rad_alpha)/math.cos(rad_beta))
      rad92_p = math.atan(math.tan(rad92)/math.cos(rad_beta))
      
      tb = tg + (g-b)/2.0 * math.tan(rad28) # depth at dimension b
      rbtop = b/2.0 + (hm + tb)*math.tan(rad_beta) # radius of b-corner at hm
      rbtot = b/2.0 - (t_tot - tb)*math.tan(rad_beta) # radius of b-corner at t_tot
      
      dre = e_mean/2.0 / math.tan(rad_alpha_p)  # delta between corner b and corner e in x direction
      #FreeCAD.Console.PrintLog("delta calculated: " + str(dre) + "\n")
   
      dx = m/2.0 * math.cos(rad92_p)
      dy = m/2.0 * math.sin(rad92_p)
   
      PntC0 = Base.Vector(rbtop,0.0,hm)
      #PntC1 = Base.Vector(b/2.0,0.0,-tb)
      PntC1 = Base.Vector(rbtot,0.0,-t_tot)
      PntC2 = Base.Vector(rbtop+dre,+e_mean/2.0,hm)
      PntC3 = Base.Vector(rbtot+dre,+e_mean/2.0,-t_tot)
      PntC4 = Base.Vector(rbtop+dre,-e_mean/2.0,hm)
      PntC5 = Base.Vector(rbtot+dre,-e_mean/2.0,-t_tot)
      
      PntC6 = Base.Vector(rbtop+dre+dx,+e_mean/2.0+dy,hm)
      PntC7 = Base.Vector(rbtot+dre+dx,+e_mean/2.0+dy,-t_tot)
      PntC8 = Base.Vector(rbtop+dre+dx,-e_mean/2.0-dy,hm)
      PntC9 = Base.Vector(rbtot+dre+dx,-e_mean/2.0-dy,-t_tot)
   
      #wire_hm = Part.makePolygon([PntC0,PntC2,PntC6,PntC8,PntC4,PntC0])
      #face_hm =Part.Face(wire_hm)
      #Part.show(face_hm)
   
      wire_t_tot = Part.makePolygon([PntC1,PntC3,PntC7,PntC9,PntC5,PntC1])
      #Part.show(wire_t_tot)
      edgeC1 = Part.makeLine(PntC0,PntC1)
      #FreeCAD.Console.PrintLog("edgeC1 mit PntC9" + str(PntC9) + "\n")
   
      makeSolid=True
      isFrenet=True
      corner = Part.Wire(edgeC1).makePipeShell([wire_t_tot],makeSolid,isFrenet)
      #Part.show(corner)
      
      rot_axis = Base.Vector(0.,0.,1.0)
      sin_res = math.sin(math.radians(90)/2.0)
      cos_res = math.cos(math.radians(90)/2.0)
      rot_axis.multiply(-sin_res) # Calculation of Quaternion-Elements
      #FreeCAD.Console.PrintLog("Quaternion-Elements" + str(cos_res) + "\n")
   
      pl_rot = FreeCAD.Placement()
      pl_rot.Rotation = (rot_axis.x,rot_axis.y,rot_axis.z,cos_res) #Rotation-Quaternion 90° z-Axis
      
      cross = cross.cut(corner)
      cutplace = corner.Placement
   
      for i in range(3):
         cutplace.Rotation = pl_rot.Rotation.multiply(corner.Placement.Rotation)
         cross = cross.cut(corner)

      FreeCAD.Console.PrintLog("Placement: " + str(pl_rot) + "\n")
         
      cross.Placement.Base = Base.Vector(0.0,0.0,h)
      return cross


    # Allen recess cutting tool
    # Parameters used: s_mean, k, t_min, dk
    def makeAllen(self, s_a = 3.0, t_a = 1.5, dk_a = 5.0, h_a = 2.0 ):
      # h_a  top height location of cutting tool 
      # s_a hex width
      # t_a dept of the allen
      # dk_a diameter needed

      e_cham = 2.0 * s_a / math.sqrt(3.0)
      depth = s_a / 3.0
      FreeCAD.Console.PrintLog("allen tool: " + str(dk_a) + "\n")

      # The round part of the cutting tool, we need for the allen hex recess
      PntH1 = Base.Vector(0.0,0.0,0.0)
      PntH2 = Base.Vector(e_cham/2.0,0.0,0.0)
      PntH3 = Base.Vector(e_cham/2.0,0.0,-t_a)
      PntH4 = Base.Vector(0.0,0.0,-t_a-depth)
      
      edgeH1 = Part.makeLine(PntH1,PntH2)
      edgeH2 = Part.makeLine(PntH2,PntH3)
      edgeH3 = Part.makeLine(PntH3,PntH4)
      edgeH4 = Part.makeLine(PntH4,PntH1)
      hWire=Part.Wire([edgeH1,edgeH2,edgeH3,edgeH4])
      # Part.show(hWire)
      hFace =Part.Face(hWire)
      roundtool = hFace.revolve(Base.Vector(0.0,0.0,0.0),Base.Vector(0.0,0.0,1.0),360)

      extrude = self.makeHextool(s_a, -t_a-depth, dk_a)
            
      allen = roundtool.cut(extrude)
      allen.Placement.Base = Base.Vector(0.0,0.0,h_a)
      return allen  



    # ISO 10664 Hexalobular internal driving feature for bolts and screws
    def makeIso10664(self,RType ='T20',t_hl=3.0, h_hl = 0):
      # t_hl depth of the recess
      # h_hl top height location of Cutting tool
      A, B, Re = iso10664def[RType]
      sqrt_3 = math.sqrt(3.0)
      depth=A/4.0
   
   
      # The round part of the cutting tool, we need for the hexalobular recess
      PntH1 = Base.Vector(0.0,0.0,0.0)
      PntH2 = Base.Vector(A/2.0*1.02,0.0,0.0)
      PntH3 = Base.Vector(A/2.0*1.02,0.0,-t_hl)
      PntH4 = Base.Vector(0.0,0.0,-t_hl-depth)
      
      edgeH1 = Part.makeLine(PntH1,PntH2)
      edgeH2 = Part.makeLine(PntH2,PntH3)
      edgeH3 = Part.makeLine(PntH3,PntH4)
      edgeH4 = Part.makeLine(PntH4,PntH1)
      hWire=Part.Wire([edgeH1,edgeH2,edgeH3,edgeH4])
      # Part.show(hWire)
      hFace =Part.Face(hWire)
      roundtool = hFace.revolve(Base.Vector(0.0,0.0,0.0),Base.Vector(0.0,0.0,1.0),360)
      
      Ri = -((B+sqrt_3*(2.*Re-A))*B+(A-4.*Re)*A)/(4.*B-2.*sqrt_3*A+(4.*sqrt_3-8.)*Re)
      print '2nd  Ri last solution: ', Ri
      beta=math.acos(A/(4*Ri+4*Re)-(2*Re)/(4*Ri+4*Re))-math.pi/6
      print 'beta: ', beta
      Rh=(sqrt_3*(A/2.0-Re))/2.0
      Re_x = A/2.0 - Re + Re*math.sin(beta)
      Re_y = Re*math.cos(beta)
      Ri_y = B/4.0
      Ri_x = sqrt_3*B/4.0
      
      mhex=Base.Matrix()
      mhex.rotateZ(math.radians(60.0))
      hexlobWireList = []
      
      PntRe0=Base.Vector(Re_x,-Re_y,0.0)
      PntRe1=Base.Vector(A/2.0,0.0,0.0)
      PntRe2=Base.Vector(Re_x,Re_y,0.0)
      edge0 = Part.Arc(PntRe0,PntRe1,PntRe2).toShape()
      #Part.show(edge0)
      hexlobWireList.append(edge0)
      
      PntRi = Base.Vector(Ri_x,Ri_y,0.0)
      PntRi2 = mhex.multiply(PntRe0)
      edge1 = Part.Arc(PntRe2,PntRi,PntRi2).toShape()
      #Part.show(edge1)
      hexlobWireList.append(edge1)
   
      for i in range(5):
         #polygon.append(vhex)
         PntRe1 = mhex.multiply(PntRe1)
         PntRe2 = mhex.multiply(PntRe2)
         edge0 = Part.Arc(PntRi2,PntRe1,PntRe2).toShape()
         hexlobWireList.append(edge0)
         PntRi = mhex.multiply(PntRi)
         PntRi2 = mhex.multiply(PntRi2)
         if i == 5:
            edge1 = Part.Arc(PntRe2,PntRi,PntRe0).toShape()
         else:
            edge1 = Part.Arc(PntRe2,PntRi,PntRi2).toShape()
         hexlobWireList.append(edge1)
      hexlobWire=Part.Wire(hexlobWireList)
      #Part.show(hWire)
   
      circ=Part.makeCircle(A/2.0*1.1)
      # Create the face with the circle as outline and the hexagon as hole
      face=Part.Face([Part.Wire(circ),hexlobWire])
      
      # Extrude in z to create the final cutting tool
      cutHelo=face.extrude(Base.Vector(0.0,0.0,-t_hl-depth))
      #Part.show(cutHelo)
      hexlob = roundtool.cut(cutHelo)
      #Part.show(hexlob)
      hexlob.Placement.Base = Base.Vector(0.0,0.0,h_hl)
      return hexlob

      
    def FindClosest(self, type, diam, len):
      ''' Find closest standard screw to given parameters '''
      if not (type in screwTables):
        return (diam, len)
      name, diam_table, len_table, range_table = screwTables[type]
      
      # auto find diameter
      if not (diam in diam_table):
        origdia = float(diam.lstrip('M'))
        mindif = 100.0
        for m in diam_table:
          diff = abs(float(m.lstrip('M')) - origdia)
          if (diff < mindif):
            mindif = diff
            diam = m
      
      # auto find length
      if (len_table != None) and not (len in len_table):
        origlen = float(len)
        mindif = 100.0
        for l in len_table:
          diff = abs(float(l) - origlen)
          if (diff < mindif):
            mindif = diff
            len = l
              
      # make sure length in range
      if range_table != None:
        minl , maxl = range_table[diam]
        if float(len) < float(minl):
          len = minl
        if float(len) > float(maxl):
          len = maxl
        
      return (diam, len)
        
        
    def AutoDiameter(self, type, holeObj):
      ''' Calculate screw diameter automatically based on given hole '''
      res = 'M6'
      if holeObj != None and hasattr(holeObj, 'Curve') and hasattr(holeObj.Curve, 'Radius') and (type in screwTables):
        d = holeObj.Curve.Radius * 2
        table = screwTables[type][1]
        mindif = 10.0
        for m in table:
            dia = float(m.lstrip('M')) + 0.1
            if (dia > d):
              dif = dia - d
              if dif < mindif:
                mindif = dif
                res = m
      return res
            
      

ScrewMakerInstance = None      
def Instance():
  global ScrewMakerInstance
  if ScrewMakerInstance == None:
    ScrewMakerInstance = Ui_ScrewMaker()
  return ScrewMakerInstance


class screw():
  def ShowUI():
    d = QtGui.QWidget()
    d.ui = Ui_ScrewMaker()
    d.ui.setupUi(d)
    d.show()

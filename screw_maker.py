#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  screw_maker2_0.py
#


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

Version 1.8 from July 2014
first approach for a faster real thread

Version 1.9 / 2.0 July 2015
new calculation of starting point of thread
shell-based approach for screw generation
added:
ISO 14582 Hexalobular socket countersunk head screws, high head
ISO 14584 Hexalobular socket raised countersunk head screws
ISO 7380-2 Hexagon socket button head screws with collar
DIN 967 Cross recessed pan head screws with collar
ISO 4032 Hexagon nuts, Style 1
ISO 4033 Hexagon nuts, Style 2
ISO 4035 Hexagon thin nuts, chamfered
EN 1661 Hexagon nuts with flange
ISO 7094 definitions  Plain washers - Extra large series
ISO 7092 definitions  Plain washers - Small series
ISO 7093-1 Plain washer - Large series
Screw-tap to drill inner threads in parts with user defined length

ScrewMaker can now also used as a python module.
The following shows how to generate a screw from a python script:
  import screw_maker2_0

  threadDef = 'M3.5'
  o = screw_maker2_0.Screw()
  t = screw_maker2_0.Screw.setThreadType(o,'real')
  # Creates a Document-Object with label describing the screw
  d = screw_maker2_0.Screw.createScrew(o, 'ISO1207', threadDef, '20', 'real')

  # creates a shape in memory
  t = screw_maker2_0.Screw.setThreadType(o,'real')
  s = screw_maker1_9d.Screw.makeIso7046(o, 'ISO14582', threadDef, 40.0)
  Part.show(s)



to do: check ISO7380 usage of rs and rt, actual only rs is used
check chamfer angle on hexogon heads and nuts
***************************************************************************
*   Copyright (c) 2013, 2014, 2015                                        *
*   Ulrich Brammer <ulrich1a[at]users.sourceforge.net>                    *
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



import FreeCAD, FreeCADGui, Part, math, csv, os
from FreeCAD import Base
import DraftVecUtils

try:
  from PySide import QtCore, QtGui
  #FreeCAD.Console.PrintMessage("PySide is used" + "\n")
except:
  #FreeCAD.Console.PrintMessage("PyQt4 is needed" + "\n")
  from PyQt4 import QtCore, QtGui

try:
    _encoding = QtGui.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)

DEBUG = False # set to True to show debug messages; does not work, still todo.

# import fastener data
__dir__ = os.path.dirname(__file__)
fsdatapath = os.path.join(__dir__, 'FsData')

# function to open a csv file and convert it to a dictionary
def csv2dict(filename, fieldsnamed=True):
  data = open(filename, 'r')
  reader = csv.reader(data, skipinitialspace=True, dialect='unix', quoting=csv.QUOTE_NONNUMERIC)
  dictvar = {}
  if fieldsnamed:
    # skip the first line
    next(reader)
  for line_list in reader:
    thekey = str(line_list[0])
    datavalues = line_list[1:]
    thevalue = []
    for item in datavalues:
      thevalue.append(item)
    thevalue = tuple(thevalue)
    dictvar.update({thekey: thevalue})
  return dictvar

FsData = {}
filelist = os.listdir(fsdatapath)
for item in filelist:
  if item[-4:] == '.csv':
    itempath = os.path.join(fsdatapath,item)
    itemdict = csv2dict(itempath,fieldsnamed=True)
    FsData.update({item[0:-4]: itemdict})


try:
  _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
  _fromUtf8 = lambda s: s

class Ui_ScrewMaker(object):
  def setupUi(self, ScrewMaker):
    FCUi = FreeCADGui.UiLoader()

    ScrewMaker.setObjectName(_fromUtf8("ScrewMaker"))
    ScrewMaker.resize(450, 362)
    ScrewMaker.setLocale(QtCore.QLocale(QtCore.QLocale.English, QtCore.QLocale.UnitedKingdom))
    self.layoutWidget = QtGui.QWidget(ScrewMaker)
    self.layoutWidget.setGeometry(QtCore.QRect(348, 35, 102, 161))
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
    self.UserLenLabel = QtGui.QLabel(self.layoutWidget)
    self.UserLenLabel.setObjectName(_fromUtf8("UserLenLabel"))
    self.verticalLayout_2.addWidget(self.UserLenLabel)

    self.layoutWidget1 = QtGui.QWidget(ScrewMaker)
    self.layoutWidget1.setGeometry(QtCore.QRect(3, 35, 350, 166))
    #self.layoutWidget1.setGeometry(QtCore.QRect(10, 5, 315, 200))
    self.layoutWidget1.setObjectName(_fromUtf8("layoutWidget1"))
    self.verticalLayout = QtGui.QVBoxLayout(self.layoutWidget1)
    #self.verticalLayout.setMargin(0)
    self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
    self.ScrewType = QtGui.QComboBox(self.layoutWidget1)
    self.ScrewType.setObjectName(_fromUtf8("ScrewType"))
    for i in range(57):
      self.ScrewType.addItem(_fromUtf8(""))  # 0

    self.verticalLayout.addWidget(self.ScrewType)
    self.NominalDiameter = QtGui.QComboBox(self.layoutWidget1)
    self.NominalDiameter.setObjectName(_fromUtf8("NominalDiameter"))
    for i in range(28):
      self.NominalDiameter.addItem(_fromUtf8("")) # 0

    self.verticalLayout.addWidget(self.NominalDiameter)
    self.NominalLength = QtGui.QComboBox(self.layoutWidget1)
    self.NominalLength.setObjectName(_fromUtf8("NominalLength"))
    for i in range(48):
      self.NominalLength.addItem(_fromUtf8("")) #0

    self.verticalLayout.addWidget(self.NominalLength)
    #self.UserLen = QtGui.QComboBox(self.layoutWidget1)
    self.UserLen = FCUi.createWidget("Gui::InputField")
    self.UserLen.setObjectName(_fromUtf8("UserLen"))
    #self.UserLen.addItem(_fromUtf8(""))
    self.UserLen.setProperty("text", "0 mm")
    self.verticalLayout.addWidget(self.UserLen)

    #self.CommentLabel = QtGui.QLabel(self.layoutWidget)
    self.CommentLabel = QtGui.QLabel(ScrewMaker)
    self.CommentLabel.setObjectName(_fromUtf8("CommentLabel"))
    self.CommentLabel.setGeometry(QtCore.QRect(10, 184, 411, 21))
    #self.verticalLayout.addWidget(self.CommentLabel)





    self.layoutWidget2 = QtGui.QWidget(ScrewMaker)
    #self.layoutWidget2.setGeometry(QtCore.QRect(10, 200, 321, 83))
    self.layoutWidget2.setGeometry(QtCore.QRect(3, 200, 321, 120))
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
    self.MessageLabel.setGeometry(QtCore.QRect(10, 10, 411, 21))
    self.MessageLabel.setProperty("Empty_text", _fromUtf8(""))
    self.MessageLabel.setObjectName(_fromUtf8("MessageLabel"))
    self.CreateButton = QtGui.QToolButton(ScrewMaker)
    self.CreateButton.setGeometry(QtCore.QRect(180, 320, 111, 26))
    self.CreateButton.setObjectName(_fromUtf8("CreateButton"))
    self.ScrewAvailable = True

    self.simpThread = self.SimpleScrew.isChecked()
    self.symThread = self.SymbolThread.isChecked()
    self.rThread = self.RealThread.isChecked()

    self.theScrew = Screw()


    self.retranslateUi(ScrewMaker)
    self.NominalDiameter.setCurrentIndex(5)
    self.NominalLength.setCurrentIndex(9)
    QtCore.QObject.connect(self.ScrewType, QtCore.SIGNAL(_fromUtf8("currentIndexChanged(int)")), self.guiCheck_Data)
    QtCore.QObject.connect(self.CreateButton, QtCore.SIGNAL(_fromUtf8("pressed()")), self.guiCreateScrew)
    QtCore.QObject.connect(self.NominalDiameter, QtCore.SIGNAL(_fromUtf8("currentIndexChanged(int)")), self.guiCheck_Data)
    QtCore.QObject.connect(self.NominalLength, QtCore.SIGNAL(_fromUtf8("currentIndexChanged(int)")), self.guiCheck_Data)
    QtCore.QMetaObject.connectSlotsByName(ScrewMaker)

  def retranslateUi(self, ScrewMaker):
    ScrewMaker.setWindowTitle(_translate("ScrewMaker", "Screw-Maker 2.0", None))
    self.ScrewTypeLabel.setText(_translate("ScrewMaker", "Type of Screw", None))
    self.NomDiaLabel.setText(_translate("ScrewMaker", "Nominal\nDiameter", None))
    self.NomLenLabel.setText(_translate("ScrewMaker", "Nominal\nLength", None))
    self.UserLenLabel.setText(_translate("ScrewMaker", "User length \nfor screw-tap", None))
    self.CommentLabel.setText(_translate("ScrewMaker", "Values in brackets are not recommended!", None))
    self.ScrewType.setItemText(0, _translate("ScrewMaker", "ISO4017: Hexagon head screws", None))
    self.ScrewType.setItemText(1, _translate("ScrewMaker", "ISO4014: Hexagon head bolts", None))
    self.ScrewType.setItemText(2, _translate("ScrewMaker", "EN1662: Hexagon bolts with flange, small\n   series", None))
    self.ScrewType.setItemText(3, _translate("ScrewMaker", "EN1665: Hexagon bolts with flange, heavy\n   series", None))
    self.ScrewType.setItemText(4, _translate("ScrewMaker", "ISO4762: Hexagon socket head cap screws", None))
    self.ScrewType.setItemText(5, _translate("ScrewMaker", "ISO7380-1: Hexagon socket button head\n    screws", None))
    self.ScrewType.setItemText(6, _translate("ScrewMaker", "ISO7380-2: Hexagon socket button head\n    screws with collar", None))
    self.ScrewType.setItemText(7, _translate("ScrewMaker", "DIN967: Cross recessed pan head screws\n    with collar", None))
    self.ScrewType.setItemText(8, _translate("ScrewMaker", "ISO10642: Hexagon socket countersunk \n    head screws", None))
    self.ScrewType.setItemText(9, _translate("ScrewMaker", "ISO2009: Slotted countersunk flat head\n    screws", None))
    self.ScrewType.setItemText(10, _translate("ScrewMaker", "ISO2010: Slotted raised countersunk head\n   screws", None))
    self.ScrewType.setItemText(11, _translate("ScrewMaker", "ISO1207: Slotted cheese head screws", None))
    self.ScrewType.setItemText(12, _translate("ScrewMaker", "ISO1580: Slotted pan head screws", None))
    self.ScrewType.setItemText(13, _translate("ScrewMaker", "ISO7045: Pan head screws, type H cross recess", None))
    self.ScrewType.setItemText(14, _translate("ScrewMaker", "ISO7046: Countersunk flat head screws\n    H cross recess", None))
    self.ScrewType.setItemText(15, _translate("ScrewMaker", "ISO7047: Raised countersunk head screws\n    H cross recess", None))
    self.ScrewType.setItemText(16, _translate("ScrewMaker", "ISO7048: Cheese head screws type H cross recess", None))
    self.ScrewType.setItemText(17, _translate("ScrewMaker", "ISO14579: Hexalobular socket head cap screws", None))
    self.ScrewType.setItemText(18, _translate("ScrewMaker", "ISO14580: Hexalobular socket cheese head\n   screws", None))
    self.ScrewType.setItemText(19, _translate("ScrewMaker", "ISO14583: Hexalobular socket pan head screws", None))
    self.ScrewType.setItemText(20, _translate("ScrewMaker", "ISO14582: Hexalobular socket countersunk\n    head screws, high head", None))
    self.ScrewType.setItemText(21, _translate("ScrewMaker", "ISO14584: Hexalobular socket raised\n    countersunk head screws", None))
    self.ScrewType.setItemText(22, _translate("ScrewMaker", "ISO7089: Plain washers - Normal series", None))
    self.ScrewType.setItemText(23, _translate("ScrewMaker", "ISO7090: Plain washers, chamfered - Normal series", None))
    self.ScrewType.setItemText(24, _translate("ScrewMaker", "ISO7092: Plain washers - Small series", None))
    self.ScrewType.setItemText(25, _translate("ScrewMaker", "ISO7093-1: Plain washer - Large series", None))
    self.ScrewType.setItemText(26, _translate("ScrewMaker", "ISO7094: Plain washers - Extra large series", None))
    self.ScrewType.setItemText(27, _translate("ScrewMaker", "ISO4032: Hexagon nuts, Style 1", None))
    self.ScrewType.setItemText(28, _translate("ScrewMaker", "ISO4033: Hexagon nuts, Style 2", None))
    self.ScrewType.setItemText(29, _translate("ScrewMaker", "ISO4035: Hexagon thin nuts, chamfered", None))
    self.ScrewType.setItemText(30, _translate("ScrewMaker", "EN1661: Hexagon nuts with flange", None))
    self.ScrewType.setItemText(31, _translate("ScrewMaker", "ScrewTap: ISO Screw-Tap", None))
    self.ScrewType.setItemText(32, _translate("ScrewMaker", "ScrewDie: ISO Screw-Die", None))
    self.ScrewType.setItemText(33, _translate("ScrewMaker", "ThreadedRod: DIN 975 Threaded Rod", None))
    self.ScrewType.setItemText(34, _translate("ScrewMaker", "DIN7984: Hexagon socket head cap screws with low head", None))
    self.ScrewType.setItemText(34, _translate("ScrewMaker", "DIN6912: Hexagon socket head cap screws with low head, with centre", None))
    self.ScrewType.setItemText(35, _translate("ScrewMaker", "ISO7379: Hexagon socket head shoulder screws", None))
    self.ScrewType.setItemText(36, _translate("ScrewMaker", "ISO4026: Hexagon socket set screws with flat point", None))
    self.ScrewType.setItemText(37, _translate("ScrewMaker", "ISO4027: Hexagon socket set screws with cone point", None))
    self.ScrewType.setItemText(38, _translate("ScrewMaker", "ISO4028: Hexagon socket set screws with dog point", None))
    self.ScrewType.setItemText(39, _translate("ScrewMaker", "ISO4029: Hexagon socket set screws with cup point", None))
    self.ScrewType.setItemText(40, _translate("ScrewMaker", "ASMEB18.2.1.6: UNC Hexagon head screws", None))
    self.ScrewType.setItemText(41, _translate("ScrewMaker", "ASMEB18.2.1.8: UNC hex head bolts with flange", None))
    self.ScrewType.setItemText(42, _translate("ScrewMaker", "ASMEB18.2.2.1A: UNC machine screw nuts", None))
    self.ScrewType.setItemText(43, _translate("ScrewMaker", "ASMEB18.2.2.4A: UNC Hexagon nuts", None))
    self.ScrewType.setItemText(44, _translate("ScrewMaker", "ASMEB18.2.2.4B: UNC Hexagon thin nuts", None))
    self.ScrewType.setItemText(45, _translate("ScrewMaker", "ASMEB18.3.1A: UNC Hexagon socket head cap screws", None))
    self.ScrewType.setItemText(46, _translate("ScrewMaker", "ASMEB18.3.3A: UNC Hexagon socket button head screws", None))
    self.ScrewType.setItemText(47, _translate("ScrewMaker", "ASMEB18.3.3B: UNC Hexagon socket button head screws with flange", None))
    self.ScrewType.setItemText(48, _translate("ScrewMaker", "ASMEB18.3.4: UNC Hexagon socket head shoulder screws", None))
    self.ScrewType.setItemText(49, _translate("ScrewMaker", "ASMEB18.3.5A: UNC Hexagon socket set screws with flat point", None))
    self.ScrewType.setItemText(50, _translate("ScrewMaker", "ASMEB18.3.5B: UNC Hexagon socket set screws with cone point", None))
    self.ScrewType.setItemText(51, _translate("ScrewMaker", "ASMEB18.3.5C: UNC Hexagon socket set screws with dog point", None))
    self.ScrewType.setItemText(52, _translate("ScrewMaker", "ASMEB18.3.5D: UNC Hexagon socket set screws with cup point", None))
    self.ScrewType.setItemText(53, _translate("ScrewMaker", "ASMEB18.6.3.1A: UNC slotted countersunk flat head screws", None))
    self.ScrewType.setItemText(54, _translate("ScrewMaker", "ASMEB18.21.1.12A: UN washers, narrow series", None))
    self.ScrewType.setItemText(55, _translate("ScrewMaker", "ASMEB18.21.1.12B: UN washers, regular series", None))
    self.ScrewType.setItemText(56, _translate("ScrewMaker", "ASMEB18.21.1.12C: UN washers, wide series", None))
    

    self.NominalDiameter.setItemText(0, _translate("ScrewMaker", "M1.6", None))
    self.NominalDiameter.setItemText(1, _translate("ScrewMaker", "M2", None))
    self.NominalDiameter.setItemText(2, _translate("ScrewMaker", "M2.5", None))
    self.NominalDiameter.setItemText(3, _translate("ScrewMaker", "M3", None))
    self.NominalDiameter.setItemText(4, _translate("ScrewMaker", "(M3.5)", None))
    self.NominalDiameter.setItemText(5, _translate("ScrewMaker", "M4", None))
    self.NominalDiameter.setItemText(6, _translate("ScrewMaker", "M5", None))
    self.NominalDiameter.setItemText(7, _translate("ScrewMaker", "M6", None))
    self.NominalDiameter.setItemText(8, _translate("ScrewMaker", "M8", None))
    self.NominalDiameter.setItemText(9, _translate("ScrewMaker", "M10", None))
    self.NominalDiameter.setItemText(10, _translate("ScrewMaker", "M12", None))
    self.NominalDiameter.setItemText(11, _translate("ScrewMaker", "(M14)", None))
    self.NominalDiameter.setItemText(12, _translate("ScrewMaker", "M16", None))
    self.NominalDiameter.setItemText(13, _translate("ScrewMaker", "(M18)", None))
    self.NominalDiameter.setItemText(14, _translate("ScrewMaker", "M20", None))
    self.NominalDiameter.setItemText(15, _translate("ScrewMaker", "(M22)", None))
    self.NominalDiameter.setItemText(16, _translate("ScrewMaker", "M24", None))
    self.NominalDiameter.setItemText(17, _translate("ScrewMaker", "(M27)", None))
    self.NominalDiameter.setItemText(18, _translate("ScrewMaker", "M30", None))
    self.NominalDiameter.setItemText(19, _translate("ScrewMaker", "M36", None))
    self.NominalDiameter.setItemText(20, _translate("ScrewMaker", "(M33)", None))
    self.NominalDiameter.setItemText(21, _translate("ScrewMaker", "M42", None))
    self.NominalDiameter.setItemText(22, _translate("ScrewMaker", "(M45)", None))
    self.NominalDiameter.setItemText(23, _translate("ScrewMaker", "M48", None))
    self.NominalDiameter.setItemText(24, _translate("ScrewMaker", "(M52)", None))
    self.NominalDiameter.setItemText(25, _translate("ScrewMaker", "M54", None))
    self.NominalDiameter.setItemText(26, _translate("ScrewMaker", "(M60)", None))
    self.NominalDiameter.setItemText(27, _translate("ScrewMaker", "M64", None))

    self.NominalLength.setItemText(0, _translate("ScrewMaker", "2", None))
    self.NominalLength.setItemText(1, _translate("ScrewMaker", "2.5", None))
    self.NominalLength.setItemText(2, _translate("ScrewMaker", "3", None))
    self.NominalLength.setItemText(3, _translate("ScrewMaker", "4", None))
    self.NominalLength.setItemText(4, _translate("ScrewMaker", "5", None))
    self.NominalLength.setItemText(5, _translate("ScrewMaker", "6", None))
    self.NominalLength.setItemText(6, _translate("ScrewMaker", "8", None))
    self.NominalLength.setItemText(7, _translate("ScrewMaker", "10", None))
    self.NominalLength.setItemText(8, _translate("ScrewMaker", "12", None))
    self.NominalLength.setItemText(9, _translate("ScrewMaker", "16", None))
    self.NominalLength.setItemText(10, _translate("ScrewMaker", "20", None))
    self.NominalLength.setItemText(11, _translate("ScrewMaker", "25", None))
    self.NominalLength.setItemText(12, _translate("ScrewMaker", "30", None))
    self.NominalLength.setItemText(13, _translate("ScrewMaker", "35", None))
    self.NominalLength.setItemText(14, _translate("ScrewMaker", "40", None))
    self.NominalLength.setItemText(15, _translate("ScrewMaker", "45", None))
    self.NominalLength.setItemText(16, _translate("ScrewMaker", "50", None))
    self.NominalLength.setItemText(17, _translate("ScrewMaker", "55", None))
    self.NominalLength.setItemText(18, _translate("ScrewMaker", "60", None))
    self.NominalLength.setItemText(19, _translate("ScrewMaker", "65", None))
    self.NominalLength.setItemText(20, _translate("ScrewMaker", "70", None))
    self.NominalLength.setItemText(21, _translate("ScrewMaker", "80", None))
    self.NominalLength.setItemText(22, _translate("ScrewMaker", "90", None))
    self.NominalLength.setItemText(23, _translate("ScrewMaker", "100", None))
    self.NominalLength.setItemText(24, _translate("ScrewMaker", "110", None))
    self.NominalLength.setItemText(25, _translate("ScrewMaker", "120", None))
    self.NominalLength.setItemText(26, _translate("ScrewMaker", "130", None))
    self.NominalLength.setItemText(27, _translate("ScrewMaker", "140", None))
    self.NominalLength.setItemText(28, _translate("ScrewMaker", "150", None))
    self.NominalLength.setItemText(29, _translate("ScrewMaker", "160", None))
    self.NominalLength.setItemText(30, _translate("ScrewMaker", "180", None))
    self.NominalLength.setItemText(31, _translate("ScrewMaker", "200", None))
    self.NominalLength.setItemText(32, _translate("ScrewMaker", "220", None))
    self.NominalLength.setItemText(33, _translate("ScrewMaker", "240", None))
    self.NominalLength.setItemText(34, _translate("ScrewMaker", "260", None))
    self.NominalLength.setItemText(35, _translate("ScrewMaker", "280", None))
    self.NominalLength.setItemText(36, _translate("ScrewMaker", "300", None))
    self.NominalLength.setItemText(37, _translate("ScrewMaker", "320", None))
    self.NominalLength.setItemText(38, _translate("ScrewMaker", "340", None))
    self.NominalLength.setItemText(39, _translate("ScrewMaker", "360", None))
    self.NominalLength.setItemText(40, _translate("ScrewMaker", "380", None))
    self.NominalLength.setItemText(41, _translate("ScrewMaker", "400", None))
    self.NominalLength.setItemText(42, _translate("ScrewMaker", "420", None))
    self.NominalLength.setItemText(43, _translate("ScrewMaker", "440", None))
    self.NominalLength.setItemText(44, _translate("ScrewMaker", "460", None))
    self.NominalLength.setItemText(45, _translate("ScrewMaker", "480", None))
    self.NominalLength.setItemText(46, _translate("ScrewMaker", "500", None))
    self.NominalLength.setItemText(47, _translate("ScrewMaker", "User", None))
    #self.UserLen.setItemText(0, _translate("ScrewMaker", "regular pitch", None))
    self.SimpleScrew.setText(_translate("ScrewMaker", "Simple Screw (no thread at all!)", None))
    self.SymbolThread.setText(_translate("ScrewMaker", "Symbol Thread (not implemented yet)", None))
    self.RealThread.setText(_translate("ScrewMaker", "Real Thread (takes time, memory intensive)\nMay not work for all screws!", None))
    self.MessageLabel.setText(_translate("ScrewMaker", "Select your screw type", None))
    self.MessageLabel.setProperty("Errortext", _translate("ScrewMaker", "Combination not implemented", None))
    self.MessageLabel.setProperty("OK_text", _translate("ScrewMaker", "Screw is made", None))
    self.CreateButton.setText(_translate("ScrewMaker", "create", None))

  def guiCheck_Data(self):
    ST_text = str(self.ScrewType.currentText())
    ST_text = ST_text.split(':')[0]
    ND_text = str(self.NominalDiameter.currentText())
    NL_text = str(self.NominalLength.currentText())
    M_text, self.ScrewAvailable  = self.theScrew.check_Data(ST_text, ND_text, NL_text)
    self.MessageLabel.setText(_translate("ScrewMaker", M_text, None))


  def guiCreateScrew(self):
    #self.simpThread = self.SimpleScrew.isChecked()
    #self.symThread = self.SymbolThread.isChecked()
    #self.rThread = self.RealThread.isChecked()
    if self.SimpleScrew.isChecked():
      threadType = 'simple'
    if self.SymbolThread.isChecked():
      threadType = 'symbol'
    if self.RealThread.isChecked():
      threadType = 'real'

    ND_text = str(self.NominalDiameter.currentText())
    NL_text = str(self.NominalLength.currentText())
    ST_text = str(self.ScrewType.currentText())
    ST_text = ST_text.split(':')[0]

    if ST_text == ('ScrewTap' or 'ScrewDie' or 'ThreadedRod'):
      if NL_text == 'User':
        textValue = self.UserLen.property("text")
        stLength = FreeCAD.Units.parseQuantity(textValue).Value
        NL_text = str(stLength)

    myObj = self.theScrew.createScrew(ST_text, ND_text, NL_text, threadType)







class Screw(object):
  def __init__(self):
    self.objAvailable = True
    self.Tuner = 510
    # thread scaling for 3D printers
    # scaled_diam = diam * ScaleA + ScaleB
    self.sm3DPrintMode = False
    self.smNutThrScaleA = 1.0
    self.smNutThrScaleB = 0.0
    self.smScrewThrScaleA = 1.0
    self.smScrewThrScaleB = 0.0

  def check_Data(self, ST_text, ND_text, NL_text):
    #FreeCAD.Console.PrintMessage("Data checking" + NL_text + "\n")
    #set screw not ok
    self.objAvailable = False
    M_text = "Select your screw type"
    Type_text = ''
    if ST_text == 'ISO4017':
      table = FsData["iso4017head"]
      tab_len = FsData["iso4017length"]
      tab_range = FsData["iso4017range"]
      Type_text = 'Screw'

    if ST_text == 'EN1662':
      table = FsData["en1662def"]
      tab_len = FsData["en1662length"]
      tab_range = FsData["en1662range"]
      Type_text = 'Screw'

    if ST_text == 'EN1665':
      table = FsData["en1665def"]
      tab_len = FsData["en1665length"]
      tab_range = FsData["en1665range"]
      Type_text = 'Screw'

    if ST_text == 'ISO2009':
      table = FsData["iso2009def"]
      tab_len = FsData["iso2009length"]
      tab_range = FsData["iso2009range"]
      Type_text = 'Screw'

    if ST_text == 'ISO2010':
      table = FsData["iso2009def"]
      tab_len = FsData["iso2009length"]
      tab_range = FsData["iso2009range"]
      Type_text = 'Screw'

    if ST_text == 'ISO4762':
      table = FsData["iso4762def"]
      tab_len = FsData["iso4762length"]
      tab_range = FsData["iso4762range"]
      Type_text = 'Screw'

    if ST_text == 'ISO10642':
      table = FsData["iso10642def"]
      tab_len = FsData["iso10642length"]
      tab_range = FsData["iso10642range"]
      Type_text = 'Screw'

    if ST_text == 'ISO4014':
      table = FsData["iso4014head"]
      tab_len = FsData["iso4014length"]
      tab_range = FsData["iso4014range"]
      Type_text = 'Screw'

    if ST_text == 'ISO1207':
      table = FsData["iso1207def"]
      tab_len = FsData["iso1207length"]
      tab_range = FsData["iso1207range"]
      Type_text = 'Screw'

    if ST_text == 'ISO1580':
      table = FsData["iso1580def"]
      tab_len = FsData["iso2009length"]
      tab_range = FsData["iso2009range"]
      Type_text = 'Screw'

    if ST_text == 'ISO7045':
      table = FsData["iso7045def"]
      tab_len = FsData["iso7045length"]
      tab_range = FsData["iso7045range"]
      Type_text = 'Screw'

    if ST_text == 'ISO7046':
      table = FsData["iso7046def"]  # contains only cross recess data
      tab_len = FsData["iso7045length"]
      tab_range = FsData["iso7046range"]
      Type_text = 'Screw'

    if ST_text == 'ISO7047':
      table = FsData["iso2009def"]
      tab_len = FsData["iso7045length"]
      tab_range = FsData["iso7046range"]
      Type_text = 'Screw'

    if ST_text == 'ISO7048':
      table = FsData["iso7048def"]
      tab_len = FsData["iso7048length"]
      tab_range = FsData["iso7048range"]
      Type_text = 'Screw'

    if ST_text == 'ISO7380-1':
      table = FsData["iso7380def"]
      tab_len = FsData["iso7380length"]
      tab_range = FsData["iso7380range"]
      Type_text = 'Screw'

    if ST_text == 'ISO7380-2':
      table = FsData["iso7380_2def"]
      tab_len = FsData["iso7380length"]
      tab_range = FsData["iso7380range"]
      Type_text = 'Screw'

    if ST_text == 'DIN967':
      table = FsData["din967def"]
      tab_len = FsData["din967length"]
      tab_range = FsData["din967range"]
      Type_text = 'Screw'

    if ST_text == 'ISO14579':
      table = FsData["iso14579def"]
      tab_len = FsData["iso14579length"]
      tab_range = FsData["iso14579range"]
      Type_text = 'Screw'

    if ST_text == 'ISO14580':
      table = FsData["iso14580def"]
      tab_len = FsData["iso14580length"]
      tab_range = FsData["iso1207range"]
      Type_text = 'Screw'

    if ST_text == 'ISO14583':
      table = FsData["iso14583def"]
      tab_len = FsData["iso7045length"]
      tab_range = FsData["iso7046range"]
      Type_text = 'Screw'

    if ST_text == 'ISO14584':
      table = FsData["iso14584def"]
      tab_len = FsData["iso7045length"]
      tab_range = FsData["iso14584range"]
      Type_text = 'Screw'

    if ST_text == 'ISO14582':
      table = FsData["iso14582def"]
      tab_len = FsData["iso14582length"]
      tab_range = FsData["iso14582range"]
      Type_text = 'Screw'

    if ST_text == 'ISO7089':
      table = FsData["iso7089def"]
      Type_text = 'Washer'

    if ST_text == 'ISO7090':
      table = FsData["iso7090def"]
      Type_text = 'Washer'

    if ST_text == 'ISO7091':
      table = FsData["iso7091def"]
      Type_text = 'Washer'

    if ST_text == 'ISO7092':
      table = FsData["iso7092def"]
      Type_text = 'Washer'

    if ST_text == 'ISO7093-1':
      table = FsData["iso7093def"]
      Type_text = 'Washer'

    if ST_text == 'ISO7094':
      table = FsData["iso7094def"]
      Type_text = 'Washer'

    if (ST_text == 'ISO4026') or (ST_text == 'ISO4027') or (ST_text == 'ISO4029'):
      table = FsData["iso4026def"]
      tab_len = FsData["iso4026length"]
      tab_range = FsData["iso4026range"]
      Type_text = 'Screw'

    if ST_text == 'ISO4028':
      table = FsData["iso4028def"]
      tab_len = FsData["iso4028length"]
      tab_range = FsData["iso4028range"]
      Type_text = 'Screw'

    if ST_text == 'ISO4032':
      table = FsData["iso4032def"]
      Type_text = 'Nut'

    if ST_text == 'ISO4033':
      table = FsData["iso4033def"]
      Type_text = 'Nut'

    if ST_text == 'ISO4035':
      table = FsData["iso4035def"]
      Type_text = 'Nut'

    if ST_text == 'ISO4036':
      table = FsData["iso4036def"]
      Type_text = 'Nut'

    if ST_text == 'EN1661':
      table = FsData["en1661def"]
      Type_text = 'Nut'

    if ST_text == 'DIN7984':
      table = FsData["din7984def"]
      tab_len = FsData["din7984length"]
      tab_range = FsData["din7984range"]
      Type_text = 'Screw'

    if ST_text == 'DIN6912':
      table = FsData["din6912def"]
      tab_len = FsData["din6912length"]
      tab_range = FsData["din6912range"]
      Type_text = 'Screw'

    if ST_text == 'iso7379':
      table = FsData["iso7379def"]
      tab_len = FsData["iso7379length"]
      tab_range = FsData["iso7379range"]
      Type_text = 'Screw'

    if ST_text == 'ASMEB18.2.1.6':
      table = FsData["asmeb18.2.1.6def"]
      tab_len = FsData["asmeb18.2.1.6length"]
      tab_range = FsData["asmeb18.2.1.6range"]
      Type_text = 'Screw'

    if ST_text == 'ASMEB18.2.1.8':
      table = FsData["asmeb18.2.1.8def"]
      tab_len = FsData["inch_fs_length"]
      tab_range = FsData["asmeb18.2.1.8range"]
      Type_text = 'Screw'

    if ST_text == 'ASMEB18.2.2.1A':
      table = FsData["asmeb18.2.2.1adef"]
      Type_text = 'Nut'

    if ST_text == 'ASMEB18.2.2.4A':
      table = FsData["asmeb18.2.2.4def"]
      Type_text = 'Nut'

    if ST_text == 'ASMEB18.2.2.4B':
      table = FsData["asmeb18.2.2.4def"]
      Type_text = 'Nut'

    if ST_text == 'ASMEB18.3.1A':
      table = FsData["asmeb18.3.1adef"]
      tab_len = FsData["inch_fs_length"]
      tab_range = FsData["asmeb18.3.1arange"]
      Type_text = 'Screw'

    if ST_text == 'ASMEB18.3.3A':
      table = FsData["asmeb18.3.3adef"]
      tab_len = FsData["inch_fs_length"]
      tab_range = FsData["asmeb18.3.3arange"]
      Type_text = 'Screw'

    if ST_text == 'ASMEB18.3.3B':
      table = FsData["asmeb18.3.3bdef"]
      tab_len = FsData["inch_fs_length"]
      tab_range = FsData["asmeb18.3.3brange"]
      Type_text = 'Screw'

    if ST_text == 'ASMEB18.3.4':
      table = FsData["asmeb18.3.4def"]
      tab_len = FsData["inch_fs_length"]
      tab_range = FsData["asmeb18.3.4range"]
      Type_text = 'Screw'

    if ST_text[:-1] == 'ASMEB18.3.5':
      table = FsData["asmeb18.3.5def"]
      tab_len = FsData["inch_fs_length"]
      tab_range = FsData["asmeb18.3.5range"]
      Type_text = 'Screw'

    if ST_text[:-1] == 'ASMEB18.5.5':
      table = FsData["asmeb18.5.2def"]
      tab_len = FsData["inch_fs_length"]
      tab_range = FsData["asmeb18.5.2range"]
      Type_text = 'Screw'

    if ST_text == 'ASMEB18.6.3.1A':
      table = FsData["asmeb18.6.3.1adef"]
      tab_len = FsData["inch_fs_length"]
      tab_range = FsData["asmeb18.6.3.1arange"]
      Type_text = 'Screw'

    if ST_text[:-1] == 'ASMEB18.21.1.12':
      table = FsData["asmeb18.21.1.12def"]
      Type_text = 'Washer'

    if ST_text == 'ScrewTap':
      table = FsData["tuningTable"]
      Type_text = 'Screw-Tap'

    if ST_text == 'ScrewDie':
      table = FsData["tuningTable"]
      Type_text = 'Screw-Die'

    if ST_text == 'ThreadedRod':
      table = FsData["tuningTable"]
      Type_text = 'Threaded-Rod'

    if ND_text not in table:
       ND_min, ND_max = FsData["standard_diameters"][ST_text]
       M_text = ST_text+' has diameters from '+ ND_min +' to ' + ND_max + ' and not ' + ND_text +'!'
       self.objAvailable = False
       # set scew not ok
    else:
      if Type_text == 'Screw':
        #NL_text = str(self.NominalLength.currentText())
        NL_min, NL_max = tab_range[ND_text]
        NL_min_float = self.getLength(NL_min)
        NL_max_float = self.getLength(NL_max)
        if NL_text == 'User':
          M_text = 'User length is only available for the screw-tab!'
          self.objAvailable = False
        else:
          NL_text_float = self.getLength(NL_text)
          if (NL_text_float<NL_min_float)or(NL_text_float>NL_max_float)or(NL_text not in tab_len):
            if '(' in ND_text:
              ND_text = ND_text.lstrip('(').rstrip(')')
            M_text = ST_text+'-'+ ND_text +' has lengths from '+ NL_min +' to ' + NL_max + ' and not ' + NL_text +'!'
            self.objAvailable = False
            # set screw not ok
          else:
            if '(' in ND_text:
              ND_text = ND_text.lstrip('(').rstrip(')')
            M_text = ST_text+'-'+ ND_text +'x'+ NL_text +' is in library available! '
            self.objAvailable = True
            #set screw ok
      else: # Washers and Nuts
        if not (Type_text == ('Screw-Tap' or 'Screw-Die' or 'Threaded-Rod')):
          if '(' in ND_text:
            ND_text = ND_text.lstrip('(').rstrip(')')
          M_text = ST_text+'-'+ ND_text +' is in library available! '
          self.objAvailable = True
          #set washer/nut ok
        else:
          if NL_text == 'User':
            M_text = 'Screw-tab with user length is ok!'
            self.objAvailable = True
          else:
            #NL_text = str(self.NominalLength.currentText())
            if '(' in ND_text:
              ND_text = ND_text.lstrip('(').rstrip(')')
            M_text = ST_text+'-'+ ND_text +' with '+ NL_text +'mm length is in library available! '
            self.objAvailable = True
            #set screwTap ok

    #print "Data checking: ", self.NominalLength.currentText(), "\n"
    #FreeCAD.Console.PrintMessage("Set Check_result into text " + str(self.objAvailable) + M_text + "\n")
    return M_text, self.objAvailable


  def createScrew(self, ST_text, ND_text, NL_text, threadType, shapeOnly = False):
    #self.simpThread = self.SimpleScrew.isChecked()
    #self.symThread = self.SymbolThread.isChecked()
    #self.rThread = self.RealThread.isChecked()
    if threadType == 'real':
      self.rThread = True
    else:
      self.rThread = False

    if self.objAvailable:
      try:
        # first we check if valid numbers have been entered
        #FreeCAD.Console.PrintMessage("NominalLength: " + self.NominalLength.currentText() + "\n")
        #FreeCAD.Console.PrintMessage("NominalDiameter: " + self.NominalDiameter.currentText() + "\n")
        #FreeCAD.Console.PrintMessage("SimpleThread: " + str(self.SimpleScrew.isChecked()) + "\n")
        #FreeCAD.Console.PrintMessage("SymbolThread: " + str(self.SymbolThread.isChecked()) + "\n")
        #FreeCAD.Console.PrintMessage("RealThread: " + str(self.RealThread.isChecked()) + "\n")

        #ND_text = str(self.NominalDiameter.currentText())
        #NL_text = str(self.NominalLength.currentText())
        #ST_text = str(self.ScrewType.currentText())
        #ST_text = ST_text.split(':')[0]
        #dia = float(ND_text.lstrip('M'))
        l = self.getLength(NL_text)
        if ST_text == 'ISO4017':
           table = FsData["iso4017head"]
        if ST_text == 'ISO4014':
           table = FsData["iso4014head"]
        if ST_text == 'EN1662':
           table = FsData["en1662def"]
        if ST_text == 'EN1665':
           table = FsData["en1665def"]
        if ST_text == 'ISO2009':
           table = FsData["iso2009def"]
        if ST_text == 'ISO2010':
           table = FsData["iso2009def"]
        if ST_text == 'ISO4762':
           table = FsData["iso4762def"]
        if ST_text == 'ISO10642':
           table = FsData["iso10642def"]
        if ST_text == 'ISO1207':
           table = FsData["iso1207def"]
        if ST_text == 'ISO1580':
           table = FsData["iso1580def"]
        if ST_text == 'ISO7045':
           table = FsData["iso7045def"]
        if ST_text == 'ISO7046':
           table = FsData["iso7045def"]
        if ST_text == 'ISO7047':
           table = FsData["iso7045def"]
        if ST_text == 'ISO7048':
           table = FsData["iso7048def"]
        if ST_text == 'ISO7380-1':
           table = FsData["iso7380def"]
        if ST_text == 'ISO7380-2':
           table = FsData["iso7380_2def"]
        if ST_text == 'DIN967':
           table = FsData["din967def"]
        if ST_text == 'ISO14579':
           table = FsData["iso14579def"]
        if ST_text == 'ISO14580':
           table = FsData["iso14580def"]
        if ST_text == 'ISO14582':
           table = FsData["iso14582def"]
        if ST_text == 'ISO14583':
           table = FsData["iso14583def"]
        if ST_text == 'ISO14584':
          table = FsData["iso14584def"]
        if ST_text == 'ISO7089':
           table = FsData["iso7089def"]
        if ST_text == 'ISO7090':
           table = FsData["iso7090def"]
        if ST_text == 'ISO7091':
           table = FsData["iso7091def"]
        if ST_text == 'ISO7092':
           table = FsData["iso7092def"]
        if ST_text == 'ISO7093-1':
           table = FsData["iso7093def"]
        if ST_text == 'ISO7094':
           table = FsData["iso7094def"]
        if ST_text == 'ISO4026':
           table = FsData["iso4026def"]
        if ST_text == 'ISO4027':
           table = FsData["iso4026def"]
        if ST_text == 'ISO4028':
          table = FsData["iso4028def"]
        if ST_text == 'ISO4029':
           table = FsData["iso4026def"]
        if ST_text == 'ISO4032':
           table = FsData["iso4032def"]
        if ST_text == 'ISO4033':
           table = FsData["iso4033def"]
        if ST_text == 'ISO4035':
           table = FsData["iso4035def"]
        if ST_text == 'ISO4036':
           table = FsData["iso4036def"]
        if ST_text == 'EN1661':
           table = FsData["en1661def"]
        if ST_text == 'DIN7984':
           table = FsData["din7984def"]
        if ST_text == 'DIN6912':
           table = FsData["din6912def"]
        if ST_text == 'ISO7379':
           table = FsData["iso7379def"]
        if ST_text == 'ASMEB18.2.1.6':
           table = FsData["asmeb18.2.1.6def"]
        if ST_text == 'ASMEB18.2.1.8':
           table = FsData["asmeb18.2.1.8def"]
        if ST_text == 'ASMEB18.2.2.1A':
           table = FsData["asmeb18.2.2.1adef"]
        if ST_text[:-1] == 'ASMEB18.2.2.4':
           table = FsData["asmeb18.2.2.4def"]
        if ST_text == 'ASMEB18.3.1A':
           table = FsData["asmeb18.3.1adef"]
        if ST_text == 'ASMEB18.3.2':
           table = FsData["asmeb18.3.2def"]
        if ST_text == 'ASMEB18.3.3A':
           table = FsData["asmeb18.3.3adef"]
        if ST_text == 'ASMEB18.3.3B':
           table = FsData["asmeb18.3.3bdef"]
        if ST_text == 'ASMEB18.3.4':
           table = FsData["asmeb18.3.4def"]
        if ST_text[:-1] == 'ASMEB18.3.5':
           table = FsData["asmeb18.3.5def"]
        if ST_text == 'ASMEB18.6.3.1A':
           table = FsData["asmeb18.6.3.1adef"]
        if ST_text == 'ASMEB18.5.2':
           table = FsData["asmeb18.5.2def"]
        if ST_text[:-1] == 'ASMEB18.21.1.12':
           table = FsData["asmeb18.21.1.12def"]
        if (ST_text == 'ScrewTap') or (ST_text == 'ScrewDie') or (ST_text == 'ThreadedRod'):
           table = FsData["tuningTable"]
        if ND_text not in table:
           FreeCAD.Console.PrintMessage("Combination of type "+ST_text \
              + " and diameter " + ND_text +" not available!" + "\n")
        #self.MessageLabel.setText(_translate("ScrewMaker", "not implemented", None))

      except ValueError:
        #print "Error! nom_dia and length values must be valid numbers!"
        FreeCAD.Console.PrintMessage("Error! nom_dia and length values must be valid numbers!\n")
      else:
        doc=FreeCAD.activeDocument()
        done = False
        if (ST_text == 'ISO4014') or (ST_text == 'ISO4017') or (ST_text == 'ASMEB18.2.1.6'):
          screw = self.makeIso4017_2(ST_text, ND_text,l)
          Type_text = 'Screw'
          done = True
        if (ST_text == 'EN1662') or (ST_text == 'EN1665') or (ST_text == 'ASMEB18.2.1.8'):
          screw = self.makeEN1662_2(ST_text, ND_text,l)
          Type_text = 'Screw'
          done = True
        if (ST_text == 'ISO2009') or (ST_text == 'ISO2010') or \
          (ST_text == 'ISO1580') or (ST_text == 'ASMEB18.6.3.1A'):
          screw = self.makeSlottedScrew(ST_text, ND_text,l)
          Type_text = 'Screw'
          done = True
        if (ST_text == 'ISO4762') or (ST_text == 'ISO14579') or (ST_text == 'DIN7984') or \
           (ST_text == 'DIN6912') or (ST_text == 'ASMEB18.3.1A'):
          screw = self.makeIso4762(ST_text, ND_text,l)
          Type_text = 'Screw'
          done = True
        if (ST_text == 'ISO1207') or (ST_text == 'ISO14580') or (ST_text == 'ISO7048'):
          screw = self.makeIso1207(ST_text, ND_text,l)
          Type_text = 'Screw'
          done = True
        if (ST_text == 'ISO7045') or (ST_text == 'ISO14583'):
          screw = self.makeIso7045(ST_text, ND_text,l)
          Type_text = 'Screw'
          done = True
        if (ST_text == 'ISO7046') or (ST_text == 'ISO7047') or \
          (ST_text == 'ISO14582') or (ST_text == 'ISO14584') or \
          (ST_text == 'ISO10642') or (ST_text == 'ASMEB18.3.2'):
          screw = self.makeIso7046(ST_text, ND_text,l)
          Type_text = 'Screw'
          done = True
        if (ST_text == 'ISO7380-1') or (ST_text == 'ISO7380-2') or \
          (ST_text == 'DIN967') or (ST_text == 'ASMEB18.3.3A') or \
          (ST_text == 'ASMEB18.3.3B'):
          screw = self.makeIso7380(ST_text, ND_text,l)
          Type_text = 'Screw'
          done = True
        if (ST_text == 'ISO7379') or (ST_text == 'ASMEB18.3.4'):
          screw = self.makeIso7379(ST_text, ND_text,l)
          Type_text = 'Screw'
          done = True
        if (ST_text == 'ISO7089') or (ST_text == 'ISO7090') or (ST_text == 'ISO7093-1') or \
          (ST_text == 'ISO7091') or (ST_text == 'ISO7092') or (ST_text == 'ISO7094') or \
          (ST_text[:-1] == 'ASMEB18.21.1.12'):
          screw = self.makeIso7089(ST_text, ND_text)
          Type_text = 'Washer'
          done = True
        if (ST_text == 'ISO4026') or (ST_text == 'ISO4027') or \
          (ST_text == 'ISO4028') or (ST_text == 'ISO4029') or \
          (ST_text[:-1] == 'ASMEB18.3.5'):
          screw = self.makeIso4026(ST_text, ND_text, l)
          Type_text = 'Screw'
          done = True
        if (ST_text == 'ISO4032') or (ST_text == 'ISO4033') or \
          (ST_text == 'ISO4035') or (ST_text == 'ASMEB18.2.2.1A') or \
          (ST_text[:-1] == 'ASMEB18.2.2.4'):
          screw = self.makeIso4032(ST_text, ND_text)
          Type_text = 'Nut'
          done = True
        if (ST_text == 'ASMEB18.5.2'):
          screw = self.makeCarriageBolt(ST_text, ND_text, l)
          Type_text = 'Screw'
          done = True
        if ST_text == 'EN1661':
          screw = self.makeEN1661(ND_text)
          Type_text = 'Nut'
          done = True
        if ST_text == 'ScrewTap':
          screw = self.makeScrewTap(ND_text,l)
          Type_text = 'Screw-Tap'
          done = True
        if ST_text == 'ScrewDie':
          screw = self.makeScrewDie(ND_text,l)
          Type_text = 'Screw-Die'
          done = True
        if ST_text == 'ThreadedRod':
          screw = self.makeThreadedRod(ND_text,l,pitch)
          Type_text = 'Threaded-Rod'
          done = True
        if not done:
          FreeCAD.Console.PrintMessage("No valid Screw Type!" +  "\n")
        if '(' in ND_text:
          ND_text = ND_text.lstrip('(').rstrip(')')

        if Type_text == 'Screw':
          label = ST_text + "-" + ND_text +"x"+ NL_text +"_"
        else:
          if (Type_text == 'Nut'):
            label = ST_text + '-' + ND_text +'_'
          else:
            if Type_text == ('Screw-Tap' or 'Screw-Die' or 'Threaded-Rod'):
              label = ST_text + '-' + ND_text +'x'+ NL_text +'_'
            else: # washer
              label = ST_text + '-' + ND_text.lstrip('M') +'_'
        if shapeOnly:
          return screw
        ScrewObj = doc.addObject("Part::Feature")
        ScrewObj.Label=label
        ScrewObj.Shape=screw
        #FreeCAD.Console.PrintMessage("Placement: "+ str(ScrewObj.Placement) +"\n")
        #FreeCAD.Console.PrintMessage("The label: "+ label +"\n")
        self.moveScrew(ScrewObj)
        #ScrewObj.Label = label
        doc.recompute()
        # Part.show(screw)
        return ScrewObj


  def moveScrew(self, ScrewObj_m):
    #FreeCAD.Console.PrintMessage("In Move Screw: " + str(ScrewObj_m) + "\n")

    mylist = FreeCAD.Gui.Selection.getSelectionEx()
    if (mylist.__len__() == 1):
       # check selection
       #FreeCAD.Console.PrintMessage("Selektionen: " + str(mylist.__len__()) + "\n")
       Pnt1 = None
       Axis1 = None
       Axis2 = None

       for o in Gui.Selection.getSelectionEx():
          #for s in o.SubElementNames:
             #FreeCAD.Console.PrintMessage( "name: " + str(s) + "\n")
          for s in o.SubObjects:
             #FreeCAD.Console.PrintMessage( "object: "+ str(s) + "\n")
             if hasattr(s,"Curve"):
                #FreeCAD.Console.PrintMessage( "The Object is a Curve!\n")
                if hasattr(s.Curve,"Center"):
                   """
                   FreeCAD.Console.PrintMessage( "The object has a Center!\n")
                   FreeCAD.Console.PrintMessage( "Curve attribute. "+ str(s.__getattribute__('Curve')) + "\n")
                   FreeCAD.Console.PrintMessage( "Center: "+ str(s.Curve.Center) + "\n")
                   FreeCAD.Console.PrintMessage( "Axis: "+ str(s.Curve.Axis) + "\n")
                   """
                   Pnt1 = s.Curve.Center
                   Axis1 = s.Curve.Axis
             if hasattr(s,'Surface'):
                #print 'the object is a face!'
                if hasattr(s.Surface,'Axis'):
                   Axis1 = s.Surface.Axis

             if hasattr(s,'Point'):
                #FreeCAD.Console.PrintMessage( "the object seems to be a vertex! "+ str(s.Point) + "\n")
                Pnt1 = s.Point

       if (Axis1 != None):
          #FreeCAD.Console.PrintMessage( "Got Axis1: " + str(Axis1) + "\n")
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
          #FreeCAD.Console.PrintMessage( "Winkel = "+ str(math.degrees(result)) + "\n")
          #FreeCAD.Console.PrintMessage("Normalvektor: "+ str(normvec) + "\n")

          pl = FreeCAD.Placement()
          pl.Rotation = (normvec.x,normvec.y,normvec.z,cos_res) #Drehungs-Quaternion

          #FreeCAD.Console.PrintMessage("pl mit Rot: "+ str(pl) + "\n")
          #neuPlatz = Part2.Object.Placement.multiply(pl)
          neuPlatz = ScrewObj_m.Placement
          #FreeCAD.Console.PrintMessage("die Position     "+ str(neuPlatz) + "\n")
          neuPlatz.Rotation = pl.Rotation.multiply(ScrewObj_m.Placement.Rotation)
          neuPlatz.move(Pnt1)
          #FreeCAD.Console.PrintMessage("die rot. Position: "+ str(neuPlatz) + "\n")


  # make Washer
  def makeIso7089(self,SType ='ISO7089', ThreadType ='M6'):
    dia = self.getDia(ThreadType, True)
    #FreeCAD.Console.PrintMessage("die Scheibe mit dia: " + str(dia) + "\n")
    if SType == 'ISO7089':
      d1_min, d2_max, h, h_max = FsData["iso7089def"][ThreadType]
    if SType == 'ISO7090':
      d1_min, d2_max, h, h_max = FsData["iso7090def"][ThreadType]
    if SType == 'ISO7091':
      d1_min, d2_max, h, h_max = FsData["iso7091def"][ThreadType]
    if SType == 'ISO7092':
      d1_min, d2_max, h, h_max = FsData["iso7092def"][ThreadType]
    if SType == 'ISO7093-1':
      d1_min, d2_max, h, h_max = FsData["iso7093def"][ThreadType]
    if SType == 'ISO7094':
      d1_min, d2_max, h, h_max = FsData["iso7094def"][ThreadType]
    if SType == 'ASMEB18.21.1.12A':
      d1_min, d2_a, d2_b, d2_c, h_a, h_b, h_c = FsData["asmeb18.21.1.12def"][ThreadType]
      d2_max = d2_a
      h_max = h_a
    if SType == 'ASMEB18.21.1.12B':
      d1_min, d2_a, d2_b, d2_c, h_a, h_b, h_c = FsData["asmeb18.21.1.12def"][ThreadType]
      d2_max = d2_b
      h_max = h_b
    if SType == 'ASMEB18.21.1.12C':
      d1_min, d2_a, d2_b, d2_c, h_a, h_b, h_c = FsData["asmeb18.21.1.12def"][ThreadType]
      d2_max = d2_c
      h_max = h_c

    #FreeCAD.Console.PrintMessage("die Scheibe mit d1_min: " + str(d1_min) + "\n")

    #Washer Points
    Pnt0 = Base.Vector(d1_min/2.0,0.0,h_max)
    Pnt2 = Base.Vector(d2_max/2.0,0.0,h_max)
    Pnt3 = Base.Vector(d2_max/2.0,0.0,0.0)
    Pnt4 = Base.Vector(d1_min/2.0,0.0,0.0)
    if SType == 'ISO7090':
      Pnt1 = Base.Vector(d2_max/2.0-h_max/4.0,0.0,h_max)
      Pnt2 = Base.Vector(d2_max/2.0,0.0,h_max*0.75)
      edge1 = Part.makeLine(Pnt0,Pnt1)
      edgeCham = Part.makeLine(Pnt1,Pnt2)
      edge1 = Part.Wire([edge1, edgeCham])
    else:
      edge1 = Part.makeLine(Pnt0,Pnt2)

    edge2 = Part.makeLine(Pnt2,Pnt3)
    edge3 = Part.makeLine(Pnt3,Pnt4)
    edge4 = Part.makeLine(Pnt4,Pnt0)
    #FreeCAD.Console.PrintMessage("Edges made Pnt2: " + str(Pnt2) + "\n")

    aWire=Part.Wire([edge1,edge2,edge3,edge4])
    #Part.show(aWire)
    aFace =Part.Face(aWire)
    head = aFace.revolve(Base.Vector(0.0,0.0,0.0),Base.Vector(0.0,0.0,1.0),360)
    #FreeCAD.Console.PrintMessage("Washer revolved: " + str(dia) + "\n")

    return head


  # make ISO 2009 Slotted countersunk flat head screws
  # make ISO 2010 Slotted raised countersunk head screws
  # make ISO 1580 Pan head slotted screw (Code is nearly identical to iso1207)
  def makeSlottedScrew(self,SType ='ISO1580', ThreadType ='M6',l=25.0):
    dia = self.getDia(ThreadType, False)
    if SType == 'ISO1580':
      #FreeCAD.Console.PrintMessage("der Kopf mit l: " + str(l) + "\n")
      #P, a, b, dk, dk_mean, da, k, n_min, r, t_min, x = iso1580def[ThreadType]
      P, a, b, dk_max, da, k, n_min, r, rf, t_min, x = FsData["iso1580def"][ThreadType]
      #FreeCAD.Console.PrintMessage("der Kopf mit iso: " + str(dk_max) + "\n")
      ht = k
      headEnd = r

      #Length for calculation of head fillet
      sqrt2_ = 1.0/math.sqrt(2.0)
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
      #FreeCAD.Console.PrintMessage("rK_top: " + str(rK_top) + "\n")
      if (b > (l - 1.0*P)):
        bmax = l- 1.0*P
      else:
        bmax = b

      #Head Points
      Pnt0 = Base.Vector(0.0,0.0,k)
      Pnt2 = Base.Vector(fillet_center_x,0.0,k)
      Pnt3 = Base.Vector(fillet_arc_x,0.0,fillet_arc_z)
      Pnt4 = Base.Vector(fillet_center_x + r_fil*math.cos(beta),0.0,fillet_center_z+ r_fil * math.sin(beta))
      Pnt5 = Base.Vector(dk_max/2.0,0.0,0.0)
      Pnt6 = Base.Vector(dia/2.0+r,0.0,0.0)     #start of fillet between head and shank
      Pnt7 = Base.Vector(dia/2.0+r-r*sqrt2_,0.0,-r+r*sqrt2_) #arc-point of fillet
      #Pnt8 = Base.Vector(dia/2.0,0.0,-r)        # end of fillet
      PntR = Base.Vector(dia/2.0,0.0,-r)        # end of fillet
      PntT0 = Base.Vector(0.0,0.0,-r)        # helper point for real thread

      edge1 = Part.makeLine(Pnt0,Pnt2)
      edge2 = Part.Arc(Pnt2,Pnt3,Pnt4).toShape()
      edge3 = Part.makeLine(Pnt4,Pnt5)
      edge4 = Part.makeLine(Pnt5,Pnt6)
      edge5 = Part.Arc(Pnt6,Pnt7,PntR).toShape()
      headWire=Part.Wire([edge1,edge2,edge3,edge4,edge5])

    if (SType == 'ISO2009') or (SType == 'ISO2010') or (SType == 'ASMEB18.6.3.1A'):
      if (SType == 'ISO2009') or (SType == 'ISO2010'):
        P, a, b, dk_theo, dk_mean, k, n_min, r, t_mean, x = FsData["iso2009def"][ThreadType]
      elif (SType == 'ASMEB18.6.3.1A'):
        P, b, dk_theo, dk_mean, k, n_min, r, t_mean = FsData["asmeb18.6.3.1adef"][ThreadType]
      dk_max = dk_theo
      t_min = t_mean
      ht = 0.0 # Head height of flat head
      if (SType == 'ISO2010'):
        rf, t_mean, cT, mH, mZ = FsData["Raised_countersunk_def"][ThreadType]
        #Lengths and angles for calculation of head rounding
        beta = math.asin(dk_mean /2.0 / rf)   # angle of head edge
        tan_beta = math.tan(beta)
        alpha = beta/2.0 # half angle
        # height of raised head top
        ht = rf - (dk_mean/2.0) / tan_beta
        h_arc_x = rf * math.sin(alpha)
        h_arc_z = ht - rf + rf * math.cos(alpha)

      cham = (dk_theo - dk_mean)/2.0
      rad225 = math.radians(22.5)
      rad45 = math.radians(45.0)
      rtan = r*math.tan(rad225)
      headEnd = k + rtan

      if (b > l - k - rtan/2.0 - 1.0*P):
        bmax = l-k-rtan/2.0 - 1.0*P
      else:
        bmax = b

      #Head Points
      Pnt0 = Base.Vector(0.0,0.0,ht)
      Pnt1 = Base.Vector(dk_mean/2.0,0.0,0.0)
      Pnt2 = Base.Vector(dk_mean/2.0,0.0,-cham)
      Pnt3 = Base.Vector(dia/2.0+r-r*math.cos(rad45),0.0,-k-rtan+r*math.sin(rad45))
      # Arc-points
      Pnt4 = Base.Vector(dia/2.0+r-r*(math.cos(rad225)),0.0,-k-rtan+r*math.sin(rad225))
      PntR = Base.Vector(dia/2.0,0.0,-k-rtan)
      #PntA = Base.Vector(dia/2.0,0.0,-a_point)
      PntT0 = Base.Vector(0.0,0.0,-k-rtan)        # helper point for real thread

      if (SType == 'ISO2010'): # make raised head rounding
        Pnt0arc = Base.Vector(h_arc_x,0.0,h_arc_z)
        edge1 = Part.Arc(Pnt0,Pnt0arc,Pnt1).toShape()
      else:
        edge1 = Part.makeLine(Pnt0,Pnt1)  # make flat head

      edge2 = Part.makeLine(Pnt1,Pnt2)
      edge3 = Part.makeLine(Pnt2,Pnt3)
      edgeArc = Part.Arc(Pnt3,Pnt4,PntR).toShape()
      headWire=Part.Wire([edge1,edge2,edge3,edgeArc])


    ### make the new code with math.modf(l)
    residue, turns = math.modf((bmax)/P)
    halfturns = 2*int(turns)
    if residue < 0.5:
      a_point = l - (turns+1.0) * P
      halfturns = halfturns +1
    else:
      halfturns = halfturns + 2
      a_point = l - (turns+2.0) * P
    #halfturns = halfturns + 2
    offSet = headEnd - a_point
    PntA = Base.Vector(dia/2.0,0.0,-a_point)        # Start of thread


    if self.rThread:
      edgeZ1 = Part.makeLine(PntR,PntT0)
      edgeZ0 = Part.makeLine(PntT0,Pnt0)
      aWire=Part.Wire([headWire, edgeZ1, edgeZ0])

    else:
      # bolt points
      PntB1 = Base.Vector(dia/2.0,0.0,-l)
      PntB2 = Base.Vector(0.0,0.0,-l)

      edgeB2 = Part.makeLine(PntB1,PntB2)
      edgeZ0 = Part.makeLine(PntB2,Pnt0)

      if a_point <= r:
        edgeB1 = Part.makeLine(PntR,PntB1)
        aWire=Part.Wire([headWire, edgeB1, edgeB2, edgeZ0])
      else:
        edgeRA = Part.makeLine(PntR,PntA)
        edgeB1 = Part.makeLine(PntA,PntB1)
        aWire=Part.Wire([headWire, edgeRA, edgeB1, edgeB2, edgeZ0])

    aFace =Part.Face(aWire)
    head = aFace.revolve(Base.Vector(0.0,0.0,0.0),Base.Vector(0.0,0.0,1.0),360)
    #FreeCAD.Console.PrintMessage("der Kopf mit revolve: " + str(dia) + "\n")

    #Parameter for slot-recess: dk_max, n_min, k, t_min
    slot = Part.makePlane(dk_max, n_min, \
        Base.Vector(dk_max/2.0,-n_min/2.0,ht+1.0),Base.Vector(0.0,0.0,-1.0))
    slot = slot.extrude(Base.Vector(0.0,0.0,-t_min-1.0))
    #Part.show(slot)
    head = head.cut(slot)
    #FreeCAD.Console.PrintMessage("der Kopf geschnitten: " + str(dia) + "\n")
    #Part.show(head)

    if self.rThread:
      rthread = self.makeShellthread(dia, P, halfturns, False, offSet)
      rthread.translate(Base.Vector(0.0, 0.0,-a_point -2.0*P))
      #Part.show(rthread)
      headFaces = []
      if (SType == 'ISO2009') or (SType == 'ASMEB18.6.3.1A'):
        for i in range(0,len(head.Faces)-2):
          headFaces.append(head.Faces[i])
        headFaces.append(head.Faces[len(head.Faces)-1])

      if (SType == 'ISO1580') or (SType == 'ISO2010'):
        for i in range(0,len(head.Faces)-1):
          headFaces.append(head.Faces[i])

      for threadFace in rthread.Faces:
        headFaces.append(threadFace)

      newHeadShell = Part.Shell(headFaces)
      #Part.show(newHeadShell)
      head = Part.Solid(newHeadShell)

    return head


  # ISO 7045 Pan head screws with type H or type Z cross recess
  # ISO 14583 Hexalobular socket pan head screws
  def makeIso7045(self, SType ='ISO7045', ThreadType ='M6',l=25.0):
    dia = self.getDia(ThreadType, False)
    #FreeCAD.Console.PrintMessage("der Kopf mit l: " + str(l) + "\n")
    P, a, b, dk_max,da, k, r, rf, x, cT, mH, mZ  = FsData["iso7045def"][ThreadType]
    #FreeCAD.Console.PrintMessage("der Kopf mit iso: " + str(dk_max) + "\n")

    #Lengths and angles for calculation of head rounding
    beta = math.asin(dk_max /2.0 / rf)   # angle of head edge
    #print 'beta: ', math.degrees(beta)
    tan_beta = math.tan(beta)


    if SType == 'ISO14583':
       tt, A, t_mean = FsData["iso14583def"][ThreadType]
       beta_A = math.asin(A/2.0 / rf)   # angle of recess edge
       tan_beta_A = math.tan(beta_A)

       alpha = (beta_A + beta)/2.0 # half angle
       #print 'alpha: ', math.degrees(alpha)
       # height of head edge
       he = k - A/2.0/tan_beta_A + (dk_max/2.0) / tan_beta
       #print 'he: ', he
       h_arc_x = rf * math.sin(alpha)
       h_arc_z = k - A/2.0/tan_beta_A + rf * math.cos(alpha)
       #FreeCAD.Console.PrintMessage("h_arc_z: " + str(h_arc_z) + "\n")
    else:
       alpha = beta/2.0 # half angle
       #print 'alpha: ', math.degrees(alpha)
       # height of head edge
       he = k - rf + (dk_max/2.0) / tan_beta
       #print 'he: ', he
       h_arc_x = rf * math.sin(alpha)
       h_arc_z = k - rf + rf * math.cos(alpha)
       #FreeCAD.Console.PrintMessage("h_arc_z: " + str(h_arc_z) + "\n")

    if (b > (l - 1.0*P)):
       bmax = l- 1.0*P
    else:
       bmax = b

    ### make the new code with math.modf(l)
    residue, turns = math.modf((bmax)/P)
    halfturns = 2*int(turns)
    if residue < 0.5:
      a_point = l - (turns+1.0) * P
      halfturns = halfturns +1
    else:
      halfturns = halfturns + 2
      a_point = l - (turns+2.0) * P
    #halfturns = halfturns + 2
    offSet = r - a_point
    #FreeCAD.Console.PrintMessage("The transition at a: " + str(a) + " turns " + str(turns) + "\n")

    sqrt2_ = 1.0/math.sqrt(2.0)

    #Head Points
    Pnt1 = Base.Vector(h_arc_x,0.0,h_arc_z)
    Pnt2 = Base.Vector(dk_max/2.0,0.0,he)
    Pnt3 = Base.Vector(dk_max/2.0,0.0,0.0)
    Pnt4 = Base.Vector(dia/2.0+r,0.0,0.0)     #start of fillet between head and shank
    Pnt5 = Base.Vector(dia/2.0+r-r*sqrt2_,0.0,-r+r*sqrt2_) #arc-point of fillet
    Pnt6 = Base.Vector(dia/2.0,0.0,-r)        # end of fillet
    Pnt7 = Base.Vector(dia/2.0,0.0,-a_point)        # Start of thread
    #FreeCAD.Console.PrintMessage("Points defined a_point: " + str(a_point) + "\n")


    if (SType == 'ISO14583'):
      #Pnt0 = Base.Vector(0.0,0.0,k-A/4.0)
      Pnt0 = Base.Vector(0.0,0.0,k-A/8.0)
      PntFlat = Base.Vector(A/8.0,0.0,k-A/8.0)
      PntCham = Base.Vector(A/1.99,0.0,k)
      edgeCham0 = Part.makeLine(Pnt0,PntFlat)
      edgeCham1 = Part.makeLine(PntFlat,PntCham)
      edgeCham2 = Part.Arc(PntCham,Pnt1,Pnt2).toShape()
      #edge1 = Part.Wire([edgeCham0,edgeCham1,edgeCham2])
      edge1 = Part.Wire([edgeCham0,edgeCham1])
      edge2 = Part.makeLine(Pnt2,Pnt3)
      edge2 = Part.Wire([edgeCham2, edge2])
      # Part.show(edge2)

      # Here is the next approach to shorten the head building time
      # Make two helper points to create a cutting tool for the
      # recess and recess shell.
      PntH1 = Base.Vector(A/1.99,0.0, 2.0*k)
      PntH2 = Base.Vector(0.0,0.0, 2.0*k)
      edgeH1 = Part.makeLine(PntCham,PntH1)
      edgeH2 = Part.makeLine(PntH1,PntH2)
      edgeH3 = Part.makeLine(PntH2,Pnt0)

    else:
      Pnt0 = Base.Vector(0.0,0.0,k)
      edge1 = Part.Arc(Pnt0,Pnt1,Pnt2).toShape()  # make round head
      edge2 = Part.makeLine(Pnt2,Pnt3)

      # Here is the next approach to shorten the head building time
      # Make two helper points to create a cutting tool for the
      # recess and recess shell.
      PntH1 = Base.Vector(dk_max/2.0,0.0, 2.0*k)
      PntH2 = Base.Vector(0.0,0.0, 2.0*k)
      edgeH1 = Part.makeLine(Pnt2,PntH1)
      edgeH2 = Part.makeLine(PntH1,PntH2)
      edgeH3 = Part.makeLine(PntH2,Pnt0)

    edge3 = Part.makeLine(Pnt3,Pnt4)
    edge4 = Part.Arc(Pnt4,Pnt5,Pnt6).toShape()
    #FreeCAD.Console.PrintMessage("Edges made h_arc_z: " + str(h_arc_z) + "\n")

    #if self.RealThread.isChecked():
    if self.rThread:
      aWire=Part.Wire([edge2,edge3,edge4])
    else:
      # bolt points
      PntB1 = Base.Vector(dia/2.0,0.0,-l)
      PntB2 = Base.Vector(0.0,0.0,-l)
      edgeB2 = Part.makeLine(PntB1,PntB2)
      if a_point <= (r + 0.00001):
        edgeB1 = Part.makeLine(Pnt6,PntB1)
        aWire=Part.Wire([edge2, edge3, edge4, edgeB1, edgeB2])
      else:
        edge5 = Part.makeLine(Pnt6,Pnt7)
        edgeB1 = Part.makeLine(Pnt7,PntB1)
        aWire=Part.Wire([edge2, edge3, edge4, edge5, edgeB1, edgeB2])



    hWire = Part.Wire([edge1,edgeH1,edgeH2,edgeH3]) # Cutter for recess-Shell
    hFace = Part.Face(hWire)
    hCut = hFace.revolve(Base.Vector(0.0,0.0,0.0),Base.Vector(0.0,0.0,1.0),360)
    #Part.show(hWire)

    headShell = aWire.revolve(Base.Vector(0.0,0.0,0.0),Base.Vector(0.0,0.0,1.0),360)
    #head = Part.Solid(headShell)
    #Part.show(aWire)
    #FreeCAD.Console.PrintMessage("der Kopf mit revolve: " + str(dia) + "\n")
    headFaces = headShell.Faces

    if (SType == 'ISO14583'):
      recess, recessShell = self.makeIso10664_3(tt, t_mean, k)
      recessShell = recessShell.cut(hCut)
      topFace = hCut.Faces[1]
      topFace = topFace.cut(recess)
      #Part.show(topFace)
      #Part.show(recessShell)
      #Part.show(headShell)
      headFaces.append(topFace.Faces[0])
      #headFaces.append(hCut.Faces[2])

    else:
      #Lengths and angles for calculation of recess positioning
      beta_cr = math.asin(mH /2.0 / rf)   # angle of recess edge
      tan_beta_cr = math.tan(beta_cr)
      # height of cross recess cutting
      hcr = k - rf + (mH/2.0) / tan_beta_cr
      #print 'hcr: ', hcr

      #Parameter for cross-recess type H: cT, mH
      recess, recessShell = self.makeCross_H3(cT, mH, hcr)
      recessShell = recessShell.cut(hCut)
      topFace = hCut.Faces[0]
      topFace = topFace.cut(recess)
      #Part.show(topFace)
      #Part.show(recessShell)
      #Part.show(headShell)
      headFaces.append(topFace.Faces[0])

    #Part.show(hCut)
    headFaces.extend(recessShell.Faces)


    #if self.RealThread.isChecked():
    if self.rThread:
      #head = self.cutIsoThread(head, dia, P, turns, l)
      rthread = self.makeShellthread(dia, P, halfturns, False, offSet)
      rthread.translate(Base.Vector(0.0, 0.0,-a_point -2.0*P))
      #head = head.fuse(rthread)
      #Part.show(rthread)
      for threadFace in rthread.Faces:
        headFaces.append(threadFace)

    newHeadShell = Part.Shell(headFaces)
    #Part.show(newHeadShell)
    head = Part.Solid(newHeadShell)

    return head


  # make Cheese head screw
  # ISO 1207 slotted screw
  # ISO 7048 cross recessed screw
  # ISO 14580 Hexalobular socket cheese head screws
  def makeIso1207(self,SType ='ISO1207', ThreadType ='M6',l=25.0):
    dia = self.getDia(ThreadType, False)
    '''
    if '(' in TreadType:
      threadString = ThreadType.lstrip('(M')
      dia = float(ThreadType.rstrip(')'))
    else:
      dia=float(ThreadType.lstrip('M'))
    '''
    #FreeCAD.Console.PrintMessage("der Kopf mit l: " + str(l) + "\n")
    if (SType == 'ISO1207') or (SType == 'ISO14580'):
       P, a, b, dk, dk_mean, da, k, n_min, r, t_min, x = FsData["iso1207def"][ThreadType]
    if SType == 'ISO7048':
       P, a, b, dk, dk_mean, da, k, r, x, cT, mH, mZ  = FsData["iso7048def"][ThreadType]
    if (SType == 'ISO14580'):
       tt, k, A, t_min = FsData["iso14580def"][ThreadType]

    #FreeCAD.Console.PrintMessage("der Kopf mit iso: " + str(dk) + "\n")

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
    #FreeCAD.Console.PrintMessage("rK_top: " + str(rK_top) + "\n")

    if (b > (l - 1.0*P)):
       bmax = l- 1.0*P
    else:
       bmax = b

    ### make the new code with math.modf(l)
    residue, turns = math.modf((bmax)/P)
    halfturns = 2*int(turns)
    if residue < 0.5:
      a_point = l - (turns+1.0) * P
      halfturns = halfturns +1
    else:
      halfturns = halfturns + 2
      a_point = l - (turns+2.0) * P
    #halfturns = halfturns + 2
    offSet = r - a_point

    sqrt2_ = 1.0/math.sqrt(2.0)

    #Head Points
    Pnt2 = Base.Vector(fillet_center_x,0.0,k)
    Pnt3 = Base.Vector(fillet_arc_x,0.0,fillet_arc_z)
    Pnt4 = Base.Vector(fillet_center_x + r_fil*math.cos(beta),0.0,fillet_center_z+ r_fil * math.sin(beta))
    Pnt5 = Base.Vector(dk/2.0,0.0,0.0)
    Pnt6 = Base.Vector(dia/2.0+r,0.0,0.0)     #start of fillet between head and shank
    Pnt7 = Base.Vector(dia/2.0+r-r*sqrt2_,0.0,-r+r*sqrt2_) #arc-point of fillet
    Pnt8 = Base.Vector(dia/2.0,0.0,-r)        # end of fillet
    Pnt9 = Base.Vector(dia/2.0,0.0,-a_point)        # Start of thread
    #FreeCAD.Console.PrintMessage("Points defined fillet_center_x: " + str(fillet_center_x) + "\n")

    if (SType == 'ISO14580'):
      # Pnt0 = Base.Vector(0.0,0.0,k-A/4.0) #Center Point for countersunk
      Pnt0 = Base.Vector(0.0,0.0,k-A/8.0) #Center Point for flat countersunk
      PntFlat = Base.Vector(A/8.0,0.0,k-A/8.0) # End of flat part
      Pnt1 = Base.Vector(A/1.99,0.0,k)     #countersunk edge at head
      edgeCham0 = Part.makeLine(Pnt0,PntFlat)
      edgeCham1 = Part.makeLine(PntFlat,Pnt1)
      edgeCham2 = Part.makeLine(Pnt1,Pnt2)
      edge1 = Part.Wire([edgeCham1,edgeCham2]) # make head with countersunk
      PntH1 = Base.Vector(A/1.99,0.0, 2.0*k)

    else:
      Pnt0 = Base.Vector(0.0,0.0,k)
      edge1 = Part.makeLine(Pnt0,Pnt2)  # make flat head


    edge2 = Part.Arc(Pnt2,Pnt3,Pnt4).toShape()
    edge3 = Part.makeLine(Pnt4,Pnt5)
    edge4 = Part.makeLine(Pnt5,Pnt6)
    edge5 = Part.Arc(Pnt6,Pnt7,Pnt8).toShape()
    #FreeCAD.Console.PrintMessage("Edges made fillet_center_z: " + str(fillet_center_z) + "\n")

    if SType == 'ISO1207':
      #Parameter for slot-recess: dk, n_min, k, t_min
      recess = Part.makePlane(dk, n_min, \
        Base.Vector(dk/2.0,-n_min/2.0,k+1.0),Base.Vector(0.0,0.0,-1.0))
      recess = recess.extrude(Base.Vector(0.0,0.0,-t_min-1.0))

      if self.rThread:
        Pnt11 = Base.Vector(0.0,0.0,-r)        # helper point for real thread
        edgeZ1 = Part.makeLine(Pnt8,Pnt11)
        edgeZ0 = Part.makeLine(Pnt11,Pnt0)
        aWire=Part.Wire([edge1,edge2,edge3,edge4,edge5, \
            edgeZ1, edgeZ0])
      else:
        # bolt points
        PntB1 = Base.Vector(dia/2.0,0.0,-l)
        PntB2 = Base.Vector(0.0,0.0,-l)

        edgeB2 = Part.makeLine(PntB1,PntB2)

        if a_point <= r:
          edgeB1 = Part.makeLine(Pnt8,PntB1)
          aWire=Part.Wire([edge1,edge2,edge3,edge4,edge5, \
              edgeB1, edgeB2])
        else:
          edge6 = Part.makeLine(Pnt8,Pnt9)
          edgeB1 = Part.makeLine(Pnt9,PntB1)
          aWire=Part.Wire([edge1,edge2,edge3,edge4,edge5,edge6, \
              edgeB1, edgeB2])

      aFace =Part.Face(aWire)
      head = aFace.revolve(Base.Vector(0.0,0.0,0.0),Base.Vector(0.0,0.0,1.0),360.0)
      head = head.cut(recess)
      # FreeCAD.Console.PrintMessage("der Kopf geschnitten: " + str(dia) + "\n")
      #Part.show(head)
      if self.rThread:
        screwFaces = []
        for i in range(0, len(head.Faces)-1):
          screwFaces.append(head.Faces[i])
        rthread = self.makeShellthread(dia, P, halfturns, False, offSet)
        rthread.translate(Base.Vector(0.0, 0.0,-a_point -2.0*P))
        for threadFace in rthread.Faces:
          screwFaces.append(threadFace)

        screwShell = Part.Shell(screwFaces)
        head = Part.Solid(screwShell)



    else:
      if self.rThread:
        aWire=Part.Wire([edge1,edge2,edge3,edge4,edge5 ])
      else:
        # bolt points
        PntB1 = Base.Vector(dia/2.0,0.0,-l)
        PntB2 = Base.Vector(0.0,0.0,-l)

        edgeB2 = Part.makeLine(PntB1,PntB2)

        if a_point <= r:
          edgeB1 = Part.makeLine(Pnt8,PntB1)
          aWire=Part.Wire([edge1,edge2,edge3,edge4,edge5, \
              edgeB1, edgeB2])
        else:
          edge6 = Part.makeLine(Pnt8,Pnt9)
          edgeB1 = Part.makeLine(Pnt9,PntB1)
          aWire=Part.Wire([edge1,edge2,edge3,edge4,edge5,edge6, \
              edgeB1, edgeB2])

      #aFace =Part.Face(aWire)
      headShell = aWire.revolve(Base.Vector(0.0,0.0,0.0),Base.Vector(0.0,0.0,1.0),360.0)
      #FreeCAD.Console.PrintMessage("der Kopf mit revolve: " + str(dia) + "\n")

      if SType == 'ISO7048':
        # hCut should be just a cylinder
        hCut = Part.makeCylinder(fillet_center_x,k,Pnt0)
        recess, recessShell = self.makeCross_H3(cT, mH, k)
        recessShell = recessShell.cut(hCut)
        topFace = headShell.Faces[0].cut(recess)
        screwFaces = [topFace.Faces[0]]
        screwFaces.extend(recessShell.Faces)
      if (SType == 'ISO14580'):
        # Ring-cutter for recess shell
        PntH2 = Base.Vector(A/8.0,0.0, 2.0*k)
        edgeH1 = Part.makeLine(Pnt1,PntH1)
        edgeH2 = Part.makeLine(PntH1,PntH2)
        edgeH3 = Part.makeLine(PntH2,PntFlat)
        hWire = Part.Wire([edgeCham1,edgeH1,edgeH2,edgeH3]) # Cutter for recess-Shell
        hFace = Part.Face(hWire)
        hCut = hFace.revolve(Base.Vector(0.0,0.0,0.0),Base.Vector(0.0,0.0,1.0),360)
        #Part.show(hWire)

        recess, recessShell = self.makeIso10664_3(tt, t_min, k)
        recessShell = recessShell.cut(hCut)
        topFace = headShell.Faces[0].cut(recess)
        screwFaces = [topFace.Faces[0]]
        screwFaces.extend(recessShell.Faces)

      for i in range(1, len(headShell.Faces)):
        screwFaces.append(headShell.Faces[i])

      if self.rThread:
        #head = self.cutIsoThread(head, dia, P, turns, l)
        rthread = self.makeShellthread(dia, P, halfturns, False, offSet)
        rthread.translate(Base.Vector(0.0, 0.0,-a_point -2.0*P))
        #head = head.fuse(rthread)
        #Part.show(rthread)
        for threadFace in rthread.Faces:
          screwFaces.append(threadFace)

      screwShell = Part.Shell(screwFaces)
      head = Part.Solid(screwShell)

    return head


  # make the ISO 4017 Hex-head-screw
  # make the ISO 4014 Hex-head-bolt
  def makeIso4017_2(self, SType, ThreadType,l=40.0):
    dia = self.getDia(ThreadType, False)
    #FreeCAD.Console.PrintMessage("der Kopf mit l: " + str(l) + "\n")
    if SType == 'ISO4017':
      P, c, dw, e,k,r,s = FsData["iso4017head"][ThreadType]

      ### make the new code with math.modf(l)
      residue, turns = math.modf((l-1*P)/P)
      halfturns = 2*int(turns)

    if SType == 'ISO4014':
      P, b1, b2, b3, c, dw, e, k, r, s = FsData["iso4014head"][ThreadType]
      if l<= 125.0:
         b = b1
      else:
         if l<= 200.0:
            b = b2
         else:
            b = b3

      ### make the new code with math.modf(l)
      residue, turns = math.modf((b)/P)
      halfturns = 2*int(turns)

    if SType == 'ASMEB18.2.1.6':
      b, P, c, dw, e, k, r, s = FsData["asmeb18.2.1.6def"][ThreadType]
      if l > 6*25.4:
        b += 6.35

      ### make the new code with math.modf(l)
      residue, turns = math.modf((b)/P)
      halfturns = 2*int(turns)

    if residue < 0.5:
      a = l - (turns+1.0) * P
      halfturns = halfturns +1
    else:
      halfturns = halfturns + 2
      a = l - (turns+2.0) * P
    #halfturns = halfturns + 2
    offSet = r - a

    sqrt2_ = 1.0/math.sqrt(2.0)
    cham = (e-s)*math.sin(math.radians(15)) # needed for chamfer at head top

    #Head Points  Usage of k, s, cham, c, dw, dia, r, a
    #FreeCAD.Console.PrintMessage("der Kopf mit halfturns: " + str(halfturns) + "\n")
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

    # create cutting tool for hexagon head
    # Parameters s, k, outer circle diameter =  e/2.0+10.0
    extrude = self.makeHextool(s, k, s*2.0)

    #if self.RealThread.isChecked():
    if self.rThread:
      Pnt11 = Base.Vector(0.0,0.0,-r)        # helper point for real thread
      edgeZ1 = Part.makeLine(Pnt9,Pnt11)
      edgeZ0 = Part.makeLine(Pnt11,Pnt0)
      aWire=Part.Wire([edge1,edge2,edge3,edge4,edge5,edge6,edge7, \
          edgeZ1, edgeZ0])

      aFace =Part.Face(aWire)
      head = aFace.revolve(Base.Vector(0.0,0.0,0.0),Base.Vector(0.0,0.0,1.0),360.0)
      #FreeCAD.Console.PrintMessage("der Kopf mit revolve: " + str(dia) + "\n")

      # Part.show(extrude)
      head = head.cut(extrude)
      #FreeCAD.Console.PrintMessage("der Kopf geschnitten: " + str(dia) + "\n")
      #Part.show(head)

      headFaces = []
      for i in range(18):
        headFaces.append(head.Faces[i])

      if (dia < 3.0) or (dia > 5.0):
        rthread = self.makeShellthread(dia, P, halfturns, True, offSet)
        rthread.translate(Base.Vector(0.0, 0.0,-a-2.0*P))
        #rthread.translate(Base.Vector(0.0, 0.0,-2.0*P))
        #Part.show(rthread)
        for tFace in rthread.Faces:
          headFaces.append(tFace)
        headShell = Part.Shell(headFaces)
        head = Part.Solid(headShell)
      else:
        rthread = self.makeShellthread(dia, P, halfturns, False, offSet)
        rthread.translate(Base.Vector(0.0, 0.0,-a-2.0*P))
        #rthread.translate(Base.Vector(0.0, 0.0,-2.0*P))
        #Part.show(rthread)
        for tFace in rthread.Faces:
          headFaces.append(tFace)
        headShell = Part.Shell(headFaces)
        head = Part.Solid(headShell)
        cyl = self.cutChamfer(dia, P, l)
        #FreeCAD.Console.PrintMessage("vor Schnitt Ende: " + str(dia) + "\n")
        head = head.cut(cyl)

    else:
      # bolt points
      cham_t = P*math.sqrt(3.0)/2.0*17.0/24.0

      PntB0 = Base.Vector(0.0,0.0,-a)
      PntB1 = Base.Vector(dia/2.0,0.0,-l+cham_t)
      PntB2 = Base.Vector(dia/2.0-cham_t,0.0,-l)
      PntB3 = Base.Vector(0.0,0.0,-l)

      edgeB1 = Part.makeLine(Pnt10,PntB1)
      edgeB2 = Part.makeLine(PntB1,PntB2)
      edgeB3 = Part.makeLine(PntB2,PntB3)

      edgeZ0 = Part.makeLine(PntB3,Pnt0)
      if a <= r:
        edgeB1 = Part.makeLine(Pnt9,PntB1)
        aWire=Part.Wire([edge1,edge2,edge3,edge4,edge5,edge6,edge7, \
            edgeB1, edgeB2, edgeB3, edgeZ0])

      else:
        edge8 = Part.makeLine(Pnt9,Pnt10)
        edgeB1 = Part.makeLine(Pnt10,PntB1)
        aWire=Part.Wire([edge1,edge2,edge3,edge4,edge5,edge6,edge7,edge8, \
            edgeB1, edgeB2, edgeB3, edgeZ0])

      aFace =Part.Face(aWire)
      head = aFace.revolve(Base.Vector(0.0,0.0,0.0),Base.Vector(0.0,0.0,1.0),360.0)
      #FreeCAD.Console.PrintMessage("der Kopf mit revolve: " + str(dia) + "\n")

      # Part.show(extrude)
      head = head.cut(extrude)
      #FreeCAD.Console.PrintMessage("der Kopf geschnitten: " + str(dia) + "\n")

    return head


  # EN 1662 Hex-head-bolt with flange - small series
  # EN 1665 Hexagon bolts with flange, heavy series
  def makeEN1662_2(self,SType ='EN1662', ThreadType ='M8',l=25.0):
    dia = self.getDia(ThreadType, False)
    #FreeCAD.Console.PrintMessage("der Kopf mit l: " + str(l) + "\n")
    if SType == 'EN1662':
       P, b0, b1, b2, b3, c, dc, dw, e, k, kw,f, r1, s = FsData["en1662def"][ThreadType]
    elif SType == 'EN1665':
       P, b0, b1, b2, b3, c, dc, dw, e, k, kw,f, r1, s = FsData["en1665def"][ThreadType]
    elif SType == 'ASMEB18.2.1.8':
       b0, P, c, dc, kw, r1, s = FsData["asmeb18.2.1.8def"][ThreadType]
       b = b0
    if l< b0:
       b = l - 2*P
    elif (SType != 'ASME18.2.1.8'):
       if l<= 125.0:
          b = b1
       else:
          if l<= 200.0:
             b = b2
          else:
             b = b3

    #FreeCAD.Console.PrintMessage("der Kopf mit isoEN1662: " + str(c) + "\n")
    cham = s*(2.0/math.sqrt(3.0)-1.0)*math.sin(math.radians(25)) # needed for chamfer at head top

    ### make the new code with math.modf(l)
    residue, turns = math.modf((b)/P)
    halfturns = 2*int(turns)
    if residue < 0.5:
      a_point = l - (turns+1.0) * P
      halfturns = halfturns +1
    else:
      halfturns = halfturns + 2
      a_point = l - (turns+2.0) * P
    #halfturns = halfturns + 2
    offSet = r1 - a_point

    sqrt2_ = 1.0/math.sqrt(2.0)

    # Flange is made with a radius of c
    beta = math.radians(25.0)
    tan_beta = math.tan(beta)

    # Calculation of Arc points of flange edge using dc and c
    arc1_x = dc/2.0 - c/2.0 + (c/2.0)*math.sin(beta)
    arc1_z = c/2.0 + (c/2.0)*math.cos(beta)

    hF = arc1_z + (arc1_x -s/2.0) * tan_beta  # height of flange at center

    kmean = arc1_z + (arc1_x - s/math.sqrt(3.0)) * tan_beta + kw * 1.1 + cham
    #kmean = k * 0.95


    #Hex-Head Points
    #FreeCAD.Console.PrintMessage("der Kopf mit math a: " + str(a_point) + "\n")
    PntH0 = Base.Vector(0.0,0.0,kmean*0.9)
    PntH1 = Base.Vector(s/2.0*0.8 - r1/2.0,0.0,kmean*0.9)
    PntH1a = Base.Vector(s/2.0*0.8-r1/2.0+r1/2.0*sqrt2_,0.0,kmean*0.9 +r1/2.0 -r1/2.0*sqrt2_)
    PntH1b = Base.Vector(s/2.0*0.8,0.0,kmean*0.9 +r1/2.0)
    PntH2 = Base.Vector(s/2.0*0.8,0.0,kmean -r1)
    PntH2a = Base.Vector(s/2.0*0.8+r1-r1*sqrt2_,0.0,kmean -r1 +r1*sqrt2_)
    PntH2b = Base.Vector(s/2.0*0.8 + r1 ,0.0,kmean)
    PntH3 = Base.Vector(s/2.0,0.0,kmean)
    #PntH4 = Base.Vector(s/math.sqrt(3.0),0.0,kmean-cham)   #s/math.sqrt(3.0)
    #PntH5 = Base.Vector(s/math.sqrt(3.0),0.0,c)
    #PntH6 = Base.Vector(0.0,0.0,c)

    edgeH1 = Part.makeLine(PntH0,PntH1)
    edgeH2 = Part.Arc(PntH1,PntH1a,PntH1b).toShape()
    edgeH3 = Part.makeLine(PntH1b,PntH2)
    edgeH3a = Part.Arc(PntH2,PntH2a,PntH2b).toShape()
    edgeH3b = Part.makeLine(PntH2b,PntH3)

    hWire=Part.Wire([edgeH1,edgeH2,edgeH3,edgeH3a,edgeH3b])
    topShell = hWire.revolve(Base.Vector(0.0,0.0,0.0),Base.Vector(0.0,0.0,1.0),360)
    #Part.show(hWire)
    #Part.show(topShell)

    # create a cutter ring to generate the chamfer at the top of the hex
    chamHori = s/math.sqrt(3.0) - s/2.0
    PntC1 = Base.Vector(s/2.0-chamHori,0.0,kmean+kmean)
    PntC2 = Base.Vector(s/math.sqrt(3.0)+chamHori,0.0,kmean+kmean)
    PntC3 = Base.Vector(s/2.0-chamHori,0.0,kmean+cham)
    PntC4 = Base.Vector(s/math.sqrt(3.0)+chamHori,0.0,kmean-cham-cham)   #s/math.sqrt(3.0)
    edgeC1 = Part.makeLine(PntC3, PntC1)
    edgeC2 = Part.makeLine(PntC1, PntC2)
    edgeC3 = Part.makeLine(PntC2, PntC4)
    edgeC4 = Part.makeLine(PntC4, PntC3)
    cWire = Part.Wire([edgeC4, edgeC1, edgeC2, edgeC3])
    cFace = Part.Face(cWire)
    chamCut = cFace.revolve(Base.Vector(0.0,0.0,0.0),Base.Vector(0.0,0.0,1.0),360)
    #Part.show(cWire)
    #Part.show(chamCut)


    # create hexagon
    mhex=Base.Matrix()
    mhex.rotateZ(math.radians(60.0))
    polygon = []
    vhex=Base.Vector(s/math.sqrt(3.0),0.0,kmean)
    for i in range(6):
       polygon.append(vhex)
       vhex = mhex.multiply(vhex)
    polygon.append(vhex)
    hexagon = Part.makePolygon(polygon)
    hexFace = Part.Face(hexagon)
    solidHex = hexFace.extrude(Base.Vector(0.0,0.0,c-kmean))
    #Part.show(solidHex)
    hexCham = solidHex.cut(chamCut)
    #Part.show(hexCham)

    topFaces = topShell.Faces

    topFaces.append(hexCham.Faces[6])
    topFaces.append(hexCham.Faces[12])
    topFaces.append(hexCham.Faces[14])
    topFaces.append(hexCham.Faces[13])
    topFaces.append(hexCham.Faces[8])
    topFaces.append(hexCham.Faces[2])
    topFaces.append(hexCham.Faces[1])

    hexFaces = [hexCham.Faces[5], hexCham.Faces[11], hexCham.Faces[10]]
    hexFaces.extend([hexCham.Faces[9], hexCham.Faces[3], hexCham.Faces[0]])
    hexShell = Part.Shell(hexFaces)

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
    Pnt8 = Base.Vector(dia/2.0,0.0,-a_point)        # Start of thread

    edge1 = Part.makeLine(Pnt0,Pnt1)
    edge2 = Part.makeLine(Pnt1,Pnt2)
    edge3 = Part.Arc(Pnt2,Pnt3,Pnt4).toShape()
    edge4 = Part.makeLine(Pnt4,Pnt5)
    edge5 = Part.Arc(Pnt5,Pnt6,Pnt7).toShape()

    # make a cutter for the hexShell
    PntHC1 = Base.Vector(0.0,0.0,arc1_z)
    PntHC2 = Base.Vector(0.0,0.0,0.0)

    edgeHC1 = Part.makeLine(Pnt2,PntHC1)
    edgeHC2 = Part.makeLine(PntHC1,PntHC2)
    edgeHC3 = Part.makeLine(PntHC2,Pnt0)

    HCWire = Part.Wire([edge2, edgeHC1, edgeHC2, edgeHC3, edge1])
    HCFace = Part.Face(HCWire)
    hex2Cut = HCFace.revolve(Base.Vector(0.0,0.0,0.0),Base.Vector(0.0,0.0,1.0),360)

    hexShell = hexShell.cut(hex2Cut)
    #Part.show(hexShell)

    topFaces.extend(hexShell.Faces)

    # bolt points
    cham_t = P*math.sqrt(3.0)/2.0*17.0/24.0

    PntB0 = Base.Vector(0.0,0.0,-a_point)
    PntB1 = Base.Vector(dia/2.0,0.0,-l+cham_t)
    PntB2 = Base.Vector(dia/2.0-cham_t,0.0,-l)
    PntB3 = Base.Vector(0.0,0.0,-l)

    edgeB2 = Part.makeLine(PntB1,PntB2)
    edgeB3 = Part.makeLine(PntB2,PntB3)

    #if self.RealThread.isChecked():
    if self.rThread:
      aWire=Part.Wire([edge2,edge3,edge4,edge5])
      boltIndex = 4

    else:
      if a_point <=r1:
        edgeB1 = Part.makeLine(Pnt7,PntB1)
        aWire=Part.Wire([edge2,edge3,edge4,edge5, edgeB1, edgeB2, edgeB3])
        boltIndex = 7
      else:
        edgeB1 = Part.makeLine(Pnt8,PntB1)
        edge6 = Part.makeLine(Pnt7,Pnt8)
        aWire=Part.Wire([edge2,edge3,edge4,edge5,edge6, \
            edgeB1, edgeB2, edgeB3])
        boltIndex = 8


    #aFace =Part.Face(aWire)
    #Part.show(aWire)
    headShell = aWire.revolve(Base.Vector(0.0,0.0,0.0),Base.Vector(0.0,0.0,1.0),360)
    #FreeCAD.Console.PrintMessage("der Kopf mit revolve: " + str(dia) + "\n")
    #Part.show(headShell)
    chamFace = headShell.Faces[0].cut(solidHex)
    #Part.show(chamFace)

    topFaces.append(chamFace.Faces[0])
    for i in range(1,boltIndex):
      topFaces.append(headShell.Faces[i])


    if self.rThread:
      if (dia < 3.0) or (dia > 5.0):
        rthread = self.makeShellthread(dia, P, halfturns, True, offSet)
        rthread.translate(Base.Vector(0.0, 0.0,-a_point-2.0*P))
        for tFace in rthread.Faces:
          topFaces.append(tFace)
        headShell = Part.Shell(topFaces)
        screw = Part.Solid(headShell)
      else:
        rthread = self.makeShellthread(dia, P, halfturns, False, offSet)
        rthread.translate(Base.Vector(0.0, 0.0,-a_point-2.0*P))
        for tFace in rthread.Faces:
          topFaces.append(tFace)
        headShell = Part.Shell(topFaces)
        head = Part.Solid(headShell)
        cyl = self.cutChamfer(dia, P, l)
        #FreeCAD.Console.PrintMessage("vor Schnitt Ende: " + str(dia) + "\n")
        screw = head.cut(cyl)
    else:
      screwShell = Part.Shell(topFaces)
      screw = Part.Solid(screwShell)

    return screw


  # also used for ISO 7046 countersunk flat head screws with H cross recess
  # also used for ISO 7047 raised countersunk head screws with H cross recess
  # also used for ISO 10642 Hexagon socket countersunk head screws
  # also used for ISO 14582 Hexalobular socket countersunk head screws, high head
  # also used for ISO 14584 Hexalobular socket raised countersunk head screws
  def makeIso7046(self, SType ='ISO7046', ThreadType ='M6',l=25.0):
    dia = self.getDia(ThreadType, False)
    #FreeCAD.Console.PrintMessage("der 2009Kopf mit l: " + str(l) + "\n")
    if (SType == 'ISO10642'):
      P,b,dk_theo,dk_mean,da, ds_min, e, k, r, s_mean, t, w = FsData["iso10642def"][ThreadType]
      ePrax = s_mean / math.sqrt(3.0) / 0.99
      ht = 0.0
      a = 2*P
      t_mean = t
    elif (SType == 'ASMEB18.3.2'):
      P, b, dk_theo, dk_mean, k, r, s_mean, t = FsData["asmeb18.3.2def"][ThreadType]
      ePrax = s_mean / math.sqrt(3.0) / 0.99
      ht = 0.0
      a = 2*P
      t_mean = t
    else: #still need the data from iso2009def, but this screw can not created here
      P, a, b, dk_theo, dk_mean, k, n_min, r, t_mean, x = FsData["iso2009def"][ThreadType]
      ht = 0.0 # Head height of flat head
    if SType == 'ISO7046':
      cT, mH, mZ  = FsData["iso7046def"][ThreadType]
    if (SType == 'ISO7047'):
      rf, t_mean, cT, mH, mZ = FsData["Raised_countersunk_def"][ThreadType]
      #Lengths and angles for calculation of head rounding
      beta = math.asin(dk_mean /2.0 / rf)   # angle of head edge
      tan_beta = math.tan(beta)
      alpha = beta/2.0 # half angle
      # height of raised head top
      ht = rf - (dk_mean/2.0) / tan_beta
      #print 'he: ', he
      h_arc_x = rf * math.sin(alpha)
      h_arc_z = ht - rf + rf * math.cos(alpha)
      #FreeCAD.Console.PrintMessage("h_arc_z: " + str(h_arc_z) + "\n")

    if (SType == 'ISO14582'):
      P, a, b, dk_theo, dk_mean, k, r, tt, A, t_mean = FsData["iso14582def"][ThreadType]
      ePrax = A / 2.0 / 0.99

    if (SType == 'ISO14584'):
      P, b, dk_theo, dk_mean, f, k, r, rf, x, tt, A, t_mean = FsData["iso14584def"][ThreadType]
      ePrax = A / 2.0 / 0.99
      #Lengths and angles for calculation of head rounding
      beta = math.asin(dk_mean /2.0 / rf)   # angle of head edge
      tan_beta = math.tan(beta)
      ctp = - (dk_mean/2.0) / tan_beta # Center Top Edge = center for rf
      betaA = math.asin(ePrax / rf)   # angle of head edge at start of recess
      ht = ctp + ePrax / math.tan(betaA)
      alpha = betaA + (beta - betaA)/2.0 # half angle of top Arc
      h_arc_x = rf * math.sin(alpha)
      h_arc_z = ctp + rf * math.cos(alpha)


    #FreeCAD.Console.PrintMessage("der Kopf mit iso r: " + str(r) + "\n")
    cham = (dk_theo - dk_mean)/2.0
    rad225 = math.radians(22.5)
    rad45 = math.radians(45.0)
    rtan = r*math.tan(rad225)
    #FreeCAD.Console.PrintMessage("Checking rtan: " + str(rtan) + "\n")

    if (b > (l - k - rtan/2.0 - 1.0*P)):
      bmax = l - k - rtan/2.0 - 1.0*P
    else:
      bmax = b

    ### make the new code with math.modf(l)
    residue, turns = math.modf((bmax)/P)
    halfturns = 2*int(turns)
    if residue < 0.5:
      a_point = l - (turns+1.0) * P
      halfturns = halfturns +1
    else:
      halfturns = halfturns + 2
      a_point = l - (turns+2.0) * P
    #halfturns = halfturns + 2
    offSet = k + rtan - a_point

    #Head Points
    Pnt1 = Base.Vector(dk_mean/2.0,0.0,0.0)
    Pnt2 = Base.Vector(dk_mean/2.0,0.0,-cham)
    Pnt3 = Base.Vector(dia/2.0+r-r*math.cos(rad45),0.0,-k-rtan+r*math.sin(rad45))

    # Arc-points
    Pnt4 = Base.Vector(dia/2.0+r-r*(math.cos(rad225)),0.0,-k-rtan+r*math.sin(rad225))
    Pnt5 = Base.Vector(dia/2.0,0.0,-k-rtan)
    Pnt6 = Base.Vector(dia/2.0,0.0,-a_point)

    if (SType == 'ISO10642') or (SType == 'ISO14582') or (SType == 'ASMEB18.3.2'):
      if (SType == 'ISO10642') or (SType == 'ASMEB18.3.2'):
        recess, recessShell = self.makeAllen2(s_mean, t_mean, 0.0 )
        Pnt0 = Base.Vector(ePrax/2.0,0.0,-ePrax/2.0)
        PntCham = Base.Vector(ePrax,0.0,0.0)
        edge1 = Part.makeLine(Pnt0,PntCham)
        edgeCham2 = Part.makeLine(PntCham,Pnt1)
        edge2 = Part.makeLine(Pnt1,Pnt2)
        edge2 = Part.Wire([edgeCham2,edge2])
        PntH0 = Base.Vector(ePrax/2.0,0.0, ht + k)
        PntH1 = Base.Vector(ePrax,0.0, ht + k)
      if (SType == 'ISO14582'):
        recess, recessShell = self.makeIso10664_3(tt, t_mean, 0.0) # hexalobular recess
        Pnt0 = Base.Vector(0.0,0.0,0.0)
        edge1 = Part.makeLine(Pnt0,Pnt1)
        edge2 = Part.makeLine(Pnt1,Pnt2)


      # bolt points with bolt chamfer
      cham_b = P*math.sqrt(3.0)/2.0*17.0/24.0

      PntB1 = Base.Vector(dia/2.0,0.0,-l+cham_b)
      PntB2 = Base.Vector(dia/2.0-cham_b,0.0,-l)
      PntB3 = Base.Vector(0.0,0.0,-l)
      if a_point <= (k + rtan):
        edgeB0 = Part.makeLine(Pnt5,PntB1)
      else:
        edgeB0 = Part.makeLine(Pnt6,PntB1)
      edgeB2 = Part.makeLine(PntB1,PntB2)
      edgeB3 = Part.makeLine(PntB2,PntB3)
      edgeB1 = Part.Wire([edgeB2,edgeB3])

    else:
      # bolt points
      PntB1 = Base.Vector(dia/2.0,0.0,-l)
      PntB2 = Base.Vector(0.0,0.0,-l)
      if a_point <= (k + rtan):
        edgeB0 = Part.makeLine(Pnt5,PntB1)
      else:
        edgeB0 = Part.makeLine(Pnt6,PntB1)
      edgeB1 = Part.makeLine(PntB1,PntB2)

      if (SType == 'ISO7047'): # make raised head rounding
        Pnt0 = Base.Vector(0.0,0.0,ht)
        Pnt0arc = Base.Vector(h_arc_x,0.0,h_arc_z)
        edge1 = Part.Arc(Pnt0,Pnt0arc,Pnt1).toShape()
        edge2 = Part.makeLine(Pnt1,Pnt2)
        PntH0 = Base.Vector(0.0,0.0, ht + k)
        PntH1 = Base.Vector(dk_mean/2.0,0.0, ht + k)
        recess, recessShell = self.makeCross_H3(cT, mH, ht)
      if (SType == 'ISO7046'):
        # ISO7046
        Pnt0 = Base.Vector(0.0,0.0,ht)
        edge1 = Part.makeLine(Pnt0,Pnt1)  # make flat head
        edge2 = Part.makeLine(Pnt1,Pnt2)
        recess, recessShell = self.makeCross_H3(cT, mH, ht)

      if (SType == 'ISO14584'): # make raised head rounding with chamfer
        Pnt0 = Base.Vector(ePrax/2.0,0.0,ht-ePrax/4.0)
        PntCham = Base.Vector(ePrax,0.0,ht)
        PntArc = Base.Vector(h_arc_x,0.0,h_arc_z)
        edge1 = Part.makeLine(Pnt0,PntCham)
        edgeArc = Part.Arc(PntCham,PntArc,Pnt1).toShape()
        edge2 = Part.makeLine(Pnt1,Pnt2)
        edge2 = Part.Wire([edgeArc,edge2])
        PntH0 = Base.Vector(ePrax/2.0,0.0, ht + k)
        PntH1 = Base.Vector(ePrax,0.0, ht + k)
        recess, recessShell = self.makeIso10664_3(tt, t_mean, ht) # hexalobular recess

    edge3 = Part.makeLine(Pnt2,Pnt3)
    edgeArc = Part.Arc(Pnt3,Pnt4,Pnt5).toShape()
    edgeArc1 = Part.makeLine(Pnt3,Pnt4)
    edgeArc2 = Part.makeLine(Pnt4,Pnt5)
    edge6 = Part.makeLine(Pnt5,Pnt6)

    if self.rThread:
      #aWire=Part.Wire([edge1,edge2,edge3,edgeArc])
      aWire=Part.Wire([edge2,edge3,edgeArc])
    else:
      if a_point <= (k + rtan):
        aWire=Part.Wire([edge2,edge3,edgeArc, edgeB0, edgeB1])
      else:
        aWire=Part.Wire([edge2,edge3,edgeArc,edge6, edgeB0, edgeB1])

    #Part.show(aWire)
    headShell = aWire.revolve(Base.Vector(0.0,0.0,0.0),Base.Vector(0.0,0.0,1.0),360)
    headFaces = headShell.Faces
    #Part.show(headShell)

    if (SType == 'ISO7046') or (SType == 'ISO14582'):
      # hCut is just a cylinder for ISO7046
      hCut = Part.makeCylinder(dk_mean/2.0,k,Pnt0)
      #Part.show(hCut)
      topFace = hCut.Faces[2]
    else:
      edgeH1 = Part.makeLine(Pnt1,PntH1)
      edgeH2 = Part.makeLine(PntH1,PntH0)
      edgeH3 = Part.makeLine(PntH0,Pnt0)
      hWire = Part.Wire([edge1,edgeH3,edgeH2,edgeH1]) # Cutter for recess-Shell
      hWire.reverse()  # a fix to work with ver 18
      hFace = Part.Face(hWire)
      hCut = hFace.revolve(Base.Vector(0.0,0.0,0.0),Base.Vector(0.0,0.0,1.0),360)
      #Part.show(hWire)
      topFace = hCut.Faces[0]

    recessShell = recessShell.cut(hCut)
    topFace = topFace.cut(recess)
    #Part.show(topFace)
    #Part.show(recessShell)
    #Part.show(headShell)
    headFaces.append(topFace.Faces[0])
    headFaces.extend(recessShell.Faces)


    if (SType == 'ISO10642') or (SType == 'ISO14582') or (SType == 'ASMEB18.3.2'):
      if self.rThread:
        if (dia < 3.0) or (dia > 5.0):
          #if True:
          rthread = self.makeShellthread(dia, P, halfturns, True, offSet)
          rthread.translate(Base.Vector(0.0, 0.0,-a_point -2.0*P))
          #head = head.fuse(rthread)
          #Part.show(rthread)
          for threadFace in rthread.Faces:
            headFaces.append(threadFace)

          screwShell = Part.Shell(headFaces)
          screw = Part.Solid(screwShell)
        else:
          '''
          # head = self.cutIsoThread(head, dia, P, turns, l)
          rthread = self.makeShellthread(dia, P, halfturns, False)
          rthread.translate(Base.Vector(0.0, 0.0,-a_point-2.0*P))
          head = head.fuse(rthread)
          head = head.removeSplitter()
          cyl = self.cutChamfer(dia, P, l)
          #FreeCAD.Console.PrintMessage("vor Schnitt Ende: " + str(dia) + "\n")
          head = head.cut(cyl)
          '''

          rthread = self.makeShellthread(dia, P, halfturns, False, offSet)
          rthread.translate(Base.Vector(0.0, 0.0,-a_point -2.0*P))
          #head = head.fuse(rthread)
          #Part.show(rthread)
          for threadFace in rthread.Faces:
            headFaces.append(threadFace)

          screwShell = Part.Shell(headFaces)
          screw = Part.Solid(screwShell)
          cyl = self.cutChamfer(dia, P, l)
          screw = screw.cut(cyl)
      else:
        screwShell = Part.Shell(headFaces)
        screw = Part.Solid(screwShell)

    else:
      if self.rThread:
        rthread = self.makeShellthread(dia, P, halfturns, False, offSet)
        rthread.translate(Base.Vector(0.0, 0.0,-a_point -2.0*P))
        #head = head.fuse(rthread)
        #Part.show(rthread)
        for threadFace in rthread.Faces:
          headFaces.append(threadFace)

      screwShell = Part.Shell(headFaces)
      screw = Part.Solid(screwShell)



    return screw


  # make ISO 4762 Allan Screw head
  # DIN 7984 Allan Screw head
  # ISO 14579 Hexalobular socket head cap screws
  def makeIso4762(self, SType ='ISO4762', ThreadType ='M6',l=25.0):
    dia = self.getDia(ThreadType, False)
    #FreeCAD.Console.PrintMessage("der 4762Kopf mit l: " + str(l) + "\n")
    #FreeCAD.Console.PrintMessage("der Kopf mit iso r: " + str(r) + "\n")
    if SType == 'ISO14579':
      P, b, dk_max, da, ds_mean, e, lf, k, r, s_mean, t, v, dw, w = FsData["iso4762def"][ThreadType]
      tt, A, t = FsData["iso14579def"][ThreadType]
      #Head Points 30° countersunk
      # Pnt0 = Base.Vector(0.0,0.0,k-A/4.0) #Center Point for countersunk
      Pnt0 = Base.Vector(0.0,0.0,k-A/8.0) #Center Point for flat countersunk
      PntFlat = Base.Vector(A/8.0,0.0,k-A/8.0) # End of flat part
      Pnt1 = Base.Vector(A/1.99,0.0,k)     #countersunk edge at head
      edgeCham0 = Part.makeLine(Pnt0,PntFlat)
      edgeCham1 = Part.makeLine(PntFlat,Pnt1)
      edge1 = Part.Wire([edgeCham0,edgeCham1])

      # Here is the next approach to shorten the head building time
      # Make two helper points to create a cutting tool for the
      # recess and recess shell.
      PntH1 = Base.Vector(A/1.99,0.0, 2.0*k)

    elif SType == 'DIN7984':
      P, b, dk_max, da, ds_min, e, k, r, s_mean, t, v, dw = FsData["din7984def"][ThreadType]
      e_cham = 2.0 * s_mean / math.sqrt(3.0)
      #Head Points 45° countersunk
      Pnt0 = Base.Vector(0.0,0.0,k-e_cham/1.99/2.0) #Center Point for countersunk
      PntFlat = Base.Vector(e_cham/1.99/2.0,0.0,k-e_cham/1.99/2.0) # End of flat part
      Pnt1 = Base.Vector(e_cham/1.99,0.0,k)     #countersunk edge at head
      edgeCham0 = Part.makeLine(Pnt0,PntFlat)
      edgeCham1 = Part.makeLine(PntFlat,Pnt1)
      edge1 = Part.Wire([edgeCham0,edgeCham1])
      PntH1 = Base.Vector(e_cham/1.99,0.0, 2.0*k)

    elif SType == 'DIN6912':
      P, b, dk_max, da, ds_min, e, k, r, s_mean, t, t2, v, dw = FsData["din6912def"][ThreadType]
      e_cham = 2.0 * s_mean / math.sqrt(3.0)
      #Head Points 45° countersunk
      Pnt0 = Base.Vector(0.0,0.0,k-e_cham/1.99/2.0) #Center Point for countersunk
      PntFlat = Base.Vector(e_cham/1.99/2.0,0.0,k-e_cham/1.99/2.0) # End of flat part
      Pnt1 = Base.Vector(e_cham/1.99,0.0,k)     #countersunk edge at head
      edgeCham0 = Part.makeLine(Pnt0,PntFlat)
      edgeCham1 = Part.makeLine(PntFlat,Pnt1)
      edge1 = Part.Wire([edgeCham0,edgeCham1])
      PntH1 = Base.Vector(e_cham/1.99,0.0, 2.0*k)

    elif (SType == 'ISO4762') or (SType == 'ASMEB18.3.1A'):
      if SType == 'ISO4762':
        P, b, dk_max, da, ds_mean, e, lf, k, r, s_mean, t, v, dw, w = FsData["iso4762def"][ThreadType]
      if SType == 'ASMEB18.3.1A':
        P, b, dk_max, k, r, s_mean, t, v, dw = FsData["asmeb18.3.1adef"][ThreadType]
      e_cham = 2.0 * s_mean / math.sqrt(3.0)
      #Head Points 45° countersunk
      Pnt0 = Base.Vector(0.0,0.0,k-e_cham/1.99/2.0) #Center Point for countersunk
      PntFlat = Base.Vector(e_cham/1.99/2.0,0.0,k-e_cham/1.99/2.0) # End of flat part
      Pnt1 = Base.Vector(e_cham/1.99,0.0,k)     #countersunk edge at head
      edgeCham0 = Part.makeLine(Pnt0,PntFlat)
      edgeCham1 = Part.makeLine(PntFlat,Pnt1)
      edge1 = Part.Wire([edgeCham0,edgeCham1])
      PntH1 = Base.Vector(e_cham/1.99,0.0, 2.0*k)


    PntH2 = Base.Vector(0.0,0.0, 2.0*k)
    edgeH1 = Part.makeLine(Pnt1,PntH1)
    edgeH2 = Part.makeLine(PntH1,PntH2)
    edgeH3 = Part.makeLine(PntH2,Pnt0)
    hWire = Part.Wire([edge1,edgeH1,edgeH2,edgeH3]) # Cutter for recess-Shell
    hFace = Part.Face(hWire)
    hCut = hFace.revolve(Base.Vector(0.0,0.0,0.0),Base.Vector(0.0,0.0,1.0),360)
    #Part.show(hWire)
    '''


    PntH2 = Base.Vector(A/8.0,0.0, 2.0*k)
    edgeH1 = Part.makeLine(Pnt1,PntH1)
    edgeH2 = Part.makeLine(PntH1,PntH2)
    edgeH3 = Part.makeLine(PntH2,PntFlat)
    hWire = Part.Wire([edgeCham1,edgeH1,edgeH2,edgeH3]) # Cutter for recess-Shell
    hFace = Part.Face(hWire)
    hCut = hFace.revolve(Base.Vector(0.0,0.0,0.0),Base.Vector(0.0,0.0,1.0),360)
    #Part.show(hWire)
    '''


    sqrt2_ = 1.0/math.sqrt(2.0)
    #depth = s_mean / 3.0

    '''
    if (b > l - 2*P):
       bmax = l-2*P
    else:
       bmax = b
    halfturns = round(2.0*(bmax+P)/P) # number of thread turns
    if self.RealThread.isChecked():
      a_real = l-(halfturns+2)*P/2.0  # point to fuse real thread
    else:
      a_real = l-halfturns*P/2.0  # starting point of thread
    if a_real < r:
      a_point = r*1.3
    else:
      a_point = a_real
    '''


    if (b > (l - 1.0*P)):
       bmax = l- 1.0*P
    else:
       bmax = b

    ### make the new code with math.modf(l)
    residue, turns = math.modf((bmax)/P)
    halfturns = 2*int(turns)
    if residue < 0.5:
      a_point = l - (turns+1.0) * P
      halfturns = halfturns +1
    else:
      halfturns = halfturns + 2
      a_point = l - (turns+2.0) * P
    #halfturns = halfturns + 2
    offSet = r - a_point
    #FreeCAD.Console.PrintMessage("The transition at a: " + str(a) + " turns " + str(turns) + "\n")




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
    Pnt10 = Base.Vector(dia/2.0,0.0,-a_point)        # start of thread

    edge1 = Part.makeLine(Pnt0,Pnt1)
    edge2 = Part.makeLine(Pnt1,Pnt2)
    edge3 = Part.Arc(Pnt2,Pnt3,Pnt4).toShape()
    edge4 = Part.makeLine(Pnt4,Pnt5)
    edge5 = Part.makeLine(Pnt5,Pnt6)
    edge6 = Part.makeLine(Pnt6,Pnt7)
    edge7 = Part.Arc(Pnt7,Pnt8,Pnt9).toShape()

    '''
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
    '''



    if self.rThread:
      aWire=Part.Wire([edge2,edge3,edge4,edge5,edge6,edge7])

    else:
      # bolt points
      cham_t = P*math.sqrt(3.0)/2.0*17.0/24.0

      PntB1 = Base.Vector(dia/2.0,0.0,-l+cham_t)
      PntB2 = Base.Vector(dia/2.0-cham_t,0.0,-l)
      PntB3 = Base.Vector(0.0,0.0,-l)

      #edgeB1 = Part.makeLine(Pnt10,PntB1)
      edgeB2 = Part.makeLine(PntB1,PntB2)
      edgeB3 = Part.makeLine(PntB2,PntB3)

      if a_point <= (r + 0.0001):
        edgeB1 = Part.makeLine(Pnt9,PntB1)
        aWire=Part.Wire([edge2,edge3,edge4,edge5,edge6,edge7, \
            edgeB1, edgeB2, edgeB3])
      else:
        edge8 = Part.makeLine(Pnt9,Pnt10)
        edgeB1 = Part.makeLine(Pnt10,PntB1)
        aWire=Part.Wire([edge2,edge3,edge4,edge5,edge6,edge7,edge8, \
            edgeB1, edgeB2, edgeB3])
      #Part.show(aWire)

    headShell = aWire.revolve(Base.Vector(0.0,0.0,0.0),Base.Vector(0.0,0.0,1.0),360)
    #head = Part.Solid(headShell)
    #Part.show(aWire)
    #FreeCAD.Console.PrintMessage("der Kopf mit revolve: " + str(dia) + "\n")
    headFaces = headShell.Faces

    # Hex cutout
    if SType == 'ISO14579':
      #recess = self.makeIso10664(tt, t, k) # hexalobular recess
      recess, recessShell = self.makeIso10664_3(tt, t, k) # hexalobular recess
    elif SType == 'DIN6912':
      recess, recessShell = self.makeAllen2(s_mean, t, k, t2) # hex with center
    else:
      recess, recessShell = self.makeAllen2(s_mean, t, k )

    recessShell = recessShell.cut(hCut)
    topFace = hCut.Faces[1]
    #topFace = hCut.Faces[0]
    topFace = topFace.cut(recess)
    #Part.show(topFace)
    #Part.show(recessShell)
    #Part.show(headShell)
    headFaces.append(topFace.Faces[0])
    #headFaces.append(hCut.Faces[2])

    #allenscrew = head.cut(recess)
    #Part.show(hCut)
    headFaces.extend(recessShell.Faces)

    #if self.RealThread.isChecked():
    if self.rThread:
      #if (dia < 3.0) or (dia > 5.0):
      if True:
        # head = self.cutIsoThread(head, dia, P, turns, l)
        rthread = self.makeShellthread(dia, P, halfturns, True, offSet)
        rthread.translate(Base.Vector(0.0, 0.0,-a_point-2.0*P))
        #Part.show(rthread)
        for tFace in rthread.Faces:
          headFaces.append(tFace)
        headShell = Part.Shell(headFaces)
        allenscrew = Part.Solid(headShell)

      else:
        # head = self.cutIsoThread(head, dia, P, turns, l)
        rthread = self.makeShellthread(dia, P, halfturns, False, offSet)
        rthread.translate(Base.Vector(0.0, 0.0,-a_point-2.0*P))
        for tFace in rthread.Faces:
          headFaces.append(tFace)
        headShell = Part.Shell(headFaces)
        allenscrew = Part.Solid(headShell)
        cyl = self.cutChamfer(dia, P, l)
        # FreeCAD.Console.PrintMessage("vor Schnitt Ende: " + str(dia) + "\n")
        allenscrew = allenscrew.cut(cyl)
    else:
      headShell = Part.Shell(headFaces)
      allenscrew = Part.Solid(headShell)


    return allenscrew


  # make ISO 7379 Hexagon socket head shoulder screw
  def makeIso7379(self, SType ='ISO7379', ThreadType ='M6',l=16):
    if (SType ==  'ISO7379'):
      P, d1, d3, l2, l3, SW = FsData["iso7379def"][ThreadType]
    if (SType == 'ASMEB18.3.4'):
      P, d1, d3, l2, l3, SW = FsData["asmeb18.3.4def"][ThreadType]
    d2 = self.getDia(ThreadType, False)
    l1 = l
    # define the fastener head and shoulder
    # applicable for both threaded and unthreaded versions
    point1 = Base.Vector(0,0,l1+l3)
    point2 = Base.Vector(d3/2-0.04*d3,0,l3+l1)
    point3 = Base.Vector(d3/2,0,l3-0.04*d3+l1)
    point4 = Base.Vector(d3/2,0,l1)
    point5 = Base.Vector(d1/2,0,l1)
    point6 = Base.Vector(d1/2-0.04*d1,0,l1-0.1*l3)
    point7 = Base.Vector(d1/2,0,l1-0.2*l3)
    point8 = Base.Vector(d1/2,0,0)
    point9 = Base.Vector(d2/2,0,0)
    edge1 = Part.makeLine(point1,point2)
    edge2 = Part.makeLine(point2,point3)
    edge3 = Part.makeLine(point3,point4)
    edge4 = Part.makeLine(point4,point5)
    edge5 = Part.Arc(point5,point6,point7).toShape()
    edge6 = Part.makeLine(point7,point8)
    edge7 = Part.makeLine(point8,point9)
    top_face_profile = Part.Wire([edge1])
    top_face = top_face_profile.revolve(Base.Vector(0,0,0),Base.Vector(0,0,1),360)
    head_shoulder_profile = Part.Wire([edge2, edge3, edge4, edge5, edge6, edge7])
    if not self.rThread:
      # if a modelled thread is not desired:
      # add a cylindrical section to represent the threads
      point10= Base.Vector(d2/2-0.075*d2,0,-0.075*l2)
      point11= Base.Vector(d2/2,0,-0.15*l2)
      point12= Base.Vector(d2/2,0,-1*l2+0.1*d2)
      point13= Base.Vector(d2/2-0.1*d2,0,-1*l2)
      point14= Base.Vector(0,0,-1*l2)
      edge8 = Part.Arc(point9,point10,point11).toShape()
      edge9 = Part.makeLine(point11,point12)
      edge10= Part.makeLine(point12,point13)
      edge11= Part.makeLine(point13,point14)
      # append the wire with the added section
      p_profile = Part.Wire([head_shoulder_profile, edge8, edge9, edge10, edge11])
      # revolve the profile into a shell object
      p_shell = p_profile.revolve(Base.Vector(0,0,0),Base.Vector(0,0,1),360)
    else:
      # if we need a modelled thread:
      # the revolved profile is only the head and shoulder
      p_profile = head_shoulder_profile
      p_shell = p_profile.revolve(Base.Vector(0,0,0),Base.Vector(0,0,1),360)
      # calculate the number of thread half turns
      residue, turns = math.modf((l2)/P)
      halfturns = 2*int(turns)
      if residue > 0.5:
        halfturns = halfturns+1
      # make the threaded section
      shell_thread = self.makeShellthread(d2,P,halfturns,True,0)
      shell_thread.translate(Base.Vector(0,0,-2*P))
      # combine the top & threaded section
      p_faces = p_shell.Faces
      p_faces.extend(shell_thread.Faces)
      p_shell = Part.Shell(p_faces)
    # make a hole for a hex key in the head
    hex_solid, hex_shell = self.makeAllen2(SW,l3*0.4,l3+l1)
    top_face = top_face.cut(hex_solid)
    p_faces = p_shell.Faces
    p_faces.extend(top_face.Faces)
    hex_shell.translate(Base.Vector(0,0,-1))
    p_faces.extend(hex_shell.Faces)
    p_shell = Part.Shell(p_faces)
    screw = Part.Solid(p_shell)
    # chamfer the hex recess
    cham_p1 = Base.Vector(0,0,l3+l1)
    cham_p2 = Base.Vector(SW/math.sqrt(3),0,l3+l1)
    cham_p3 = Base.Vector(0,0,l3+l1-SW/math.sqrt(3)) #45 degree chamfer
    cham_e1 = Part.makeLine(cham_p1,cham_p2)
    cham_e2 = Part.makeLine(cham_p2,cham_p3)
    cham_profile = Part.Wire([cham_e1,cham_e2])
    cham_shell = cham_profile.revolve(Base.Vector(0,0,0),Base.Vector(0,0,1),360)
    cham_solid = Part.Solid(cham_shell)
    screw = screw.cut(cham_solid)
    return screw


  # make ISO 7380-1 Button head Screw
  # make ISO 7380-2 Button head Screw with collar
  # make DIN 967 cross recessed pan head Screw with collar
  def makeIso7380(self, SType ='ISO7380-1', ThreadType ='M6',l=25.0):
    dia = self.getDia(ThreadType, False)
    #todo: different radii for screws with thread to head or with shaft?
    sqrt2_ = 1.0/math.sqrt(2.0)

    if (SType == 'DIN967'):
      P, b, c, da, dk, r, k, rf, x, cT, mH, mZ = FsData["din967def"][ThreadType]

      rH = rf # radius of button arc
      alpha = math.acos((rf-k+c)/rf)

      #Head Points
      Pnt0 = Base.Vector(0.0,0.0,k)
      PntArc = Base.Vector(rf*math.sin(alpha/2.0),0.0,k-rf + rf*math.cos(alpha/2.0)) #arc-point of button
      Pnt1 = Base.Vector(rf*math.sin(alpha),0.0,c)     #end of button arc
      PntC0 = Base.Vector((dk)/2.0,0.0,c)     #collar points
      PntC2 = Base.Vector((dk)/2.0,0.0,0.0)     #collar points
      Pnt4 = Base.Vector(dia/2.0+r,0.0,0.0)     #start of fillet between head and shank

      edge1 = Part.Arc(Pnt0,PntArc,Pnt1).toShape()
      edgeC0 = Part.makeLine(Pnt1,PntC0)
      edgeC1 = Part.makeLine(PntC0,PntC2)
      edge2 = Part.Wire([edgeC0, edgeC1])
      edge3 = Part.makeLine(PntC2,Pnt4)
      #Points for recessShell cutter
      PntH0 = Base.Vector(0.0,0.0,2.0*k)
      PntH1 = Base.Vector(rf*math.sin(alpha),0.0,2.0*k)
      recess, recessShell = self.makeCross_H3(cT, mH, k)

    else:
      if (SType =='ISO7380-1'):
        P, b, a, da, dk, dk_mean,s_mean, t_min, r, k, e, w = FsData["iso7380def"][ThreadType]

        # Bottom of recess
        e_cham = 2.0 * s_mean / math.sqrt(3.0) / 0.99
        #depth = s_mean / 3.0

        ak = -(4*k**2 + e_cham**2 - dk**2)/(8*k) # helper value for button arc
        rH = math.sqrt((dk/2.0)**2 + ak**2) # radius of button arc
        alpha = (math.atan(2*(k + ak)/e_cham) + math.atan((2*ak)/dk))/2

        Pnt2 = Base.Vector(rH*math.cos(alpha),0.0,-ak + rH*math.sin(alpha)) #arc-point of button
        Pnt3 = Base.Vector(dk/2.0,0.0,0.0)   #end of fillet
        Pnt4 = Base.Vector(dia/2.0+r,0.0,0.0)     #start of fillet between head and shank
        edge3 = Part.makeLine(Pnt3,Pnt4)
      
      if (SType == 'ASMEB18.3.3A'):
        P, b, da, dk, s_mean, t_min, r, k = FsData["asmeb18.3.3adef"][ThreadType]
        # Bottom of recess
        e_cham = 2.0 * s_mean / math.sqrt(3.0) / 0.99
        #depth = s_mean / 3.0
        ak = -(4*k**2 + e_cham**2 - dk**2)/(8*k) # helper value for button arc
        rH = math.sqrt((dk/2.0)**2 + ak**2) # radius of button arc
        alpha = (math.atan(2*(k + ak)/e_cham) + math.atan((2*ak)/dk))/2
        Pnt2 = Base.Vector(rH*math.cos(alpha),0.0,-ak + rH*math.sin(alpha)) #arc-point of button
        Pnt3 = Base.Vector(dk/2.0,0.0,0.0)   #end of fillet
        Pnt4 = Base.Vector(dia/2.0+r,0.0,0.0)     #start of fillet between head and shank
        edge3 = Part.makeLine(Pnt3,Pnt4)

      if (SType == 'ISO7380-2') or (SType == 'ASMEB18.3.3B'):
        if (SType =='ISO7380-2'):
          P, b, c, da, dk, dk_c,s_mean,t_min, r, k, e, w = FsData["iso7380_2def"][ThreadType]
        if (SType == 'ASMEB18.3.3B'):
          P, b, c, dk, dk_c, s_mean, t_min, r, k = FsData["asmeb18.3.3bdef"][ThreadType]

        # Bottom of recess
        e_cham = 2.0 * s_mean / math.sqrt(3.0) / 0.99
        #depth = s_mean / 3.0

        ak = -(4*(k-c)**2 + e_cham**2 - dk**2)/(8*(k-c)) # helper value for button arc
        rH = math.sqrt((dk/2.0)**2 + ak**2) # radius of button arc
        alpha = (math.atan(2*(k -c + ak)/e_cham) + math.atan((2*ak)/dk))/2

        Pnt2 = Base.Vector(rH*math.cos(alpha),0.0,c -ak + rH*math.sin(alpha)) #arc-point of button
        Pnt3 = Base.Vector(dk/2.0,0.0,c)   #end of fillet
        Pnt4 = Base.Vector(dia/2.0+r,0.0,0.0)     #start of fillet between head and shank
        PntC0 = Base.Vector((dk_c-c)/2.0,0.0,c)     #collar points
        PntC1 = Base.Vector(dk_c/2.0,0.0,c/2.0)     #collar points
        PntC2 = Base.Vector((dk_c-c)/2.0,0.0,0.0)     #collar points

        edgeC0 = Part.makeLine(Pnt3,PntC0)
        edgeC1 = Part.Arc(PntC0,PntC1,PntC2).toShape()
        edge3 = Part.makeLine(PntC2,Pnt4)
        edge3 = Part.Wire([edgeC0, edgeC1, edge3])

      #Head Points
      Pnt0 = Base.Vector(e_cham/4.0,0.0,k-e_cham/4.0) #Center Point for chamfer
      Pnt1 = Base.Vector(e_cham/2.0,0.0,k)     #inner chamfer edge at head
      #Points for recessShell cutter
      PntH0 = Base.Vector(e_cham/4.0,0.0,2.0*k)
      PntH1 = Base.Vector(e_cham/2.0,0.0,2.0*k)

      edge1 = Part.makeLine(Pnt0,Pnt1)
      edge2 = Part.Arc(Pnt1,Pnt2,Pnt3).toShape()
      recess, recessShell = self.makeAllen2(s_mean, t_min, k)

    if (b > (l - 1.0*P)):
       bmax = l- 1.0*P
    else:
       bmax = b

    ### make the new code with math.modf(l)
    residue, turns = math.modf((bmax)/P)
    halfturns = 2*int(turns)
    if residue < 0.5:
      a_point = l - (turns+1.0) * P
      halfturns = halfturns +1
    else:
      halfturns = halfturns + 2
      a_point = l - (turns+2.0) * P
    offSet = r - a_point


    Pnt5 = Base.Vector(dia/2.0+r-r*sqrt2_,0.0,-r+r*sqrt2_) #arc-point of fillet
    Pnt6 = Base.Vector(dia/2.0,0.0,-r)        # end of fillet
    Pnt7 = Base.Vector(dia/2.0,0.0,-a_point)        # start of thread

    edge4 = Part.Arc(Pnt4,Pnt5,Pnt6).toShape()
    edge5 = Part.makeLine(Pnt6,Pnt7)

    if (SType =='DIN967'):
      # bolt points
      PntB1 = Base.Vector(dia/2.0,0.0,-l)
      PntB2 = Base.Vector(0.0,0.0,-l)
      edgeB2 = Part.makeLine(PntB1,PntB2)
    else:
      # bolt points
      cham_b = P*math.sqrt(3.0)/2.0*17.0/24.0

      PntB1 = Base.Vector(dia/2.0,0.0,-l+cham_b)
      PntB2 = Base.Vector(dia/2.0-cham_b,0.0,-l)
      PntB3 = Base.Vector(0.0,0.0,-l)

      edgeB2 = Part.makeLine(PntB1,PntB2)
      edgeB3 = Part.makeLine(PntB2,PntB3)
      edgeB2 = Part.Wire([edgeB2, edgeB3])

    if self.rThread:
      aWire=Part.Wire([edge2,edge3,edge4])
    else:
      if a_point <= r:
        edgeB1 = Part.makeLine(Pnt6,PntB1)
        aWire=Part.Wire([edge2,edge3,edge4, edgeB1, edgeB2])
      else:
        edge5 = Part.makeLine(Pnt6,Pnt7)
        edgeB1 = Part.makeLine(Pnt7,PntB1)
        aWire=Part.Wire([edge2,edge3,edge4,edge5, edgeB1, edgeB2])

    #Part.show(aWire)
    headShell = aWire.revolve(Base.Vector(0.0,0.0,0.0),Base.Vector(0.0,0.0,1.0),360)
    #Part.show(headShell)
    headFaces = headShell.Faces

    edgeH1 = Part.makeLine(Pnt1,PntH1)
    edgeH2 = Part.makeLine(PntH1,PntH0)
    edgeH3 = Part.makeLine(PntH0,Pnt0)
    hWire = Part.Wire([edge1,edgeH1,edgeH2,edgeH3]) # Cutter for recess-Shell
    hFace = Part.Face(hWire)
    hCut = hFace.revolve(Base.Vector(0.0,0.0,0.0),Base.Vector(0.0,0.0,1.0),360)
    #Part.show(hWire)
    topFace = hCut.Faces[0]

    recessShell = recessShell.cut(hCut)
    topFace = topFace.cut(recess)
    #Part.show(topFace)
    #Part.show(recessShell)
    #Part.show(headShell)
    headFaces.append(topFace.Faces[0])
    headFaces.extend(recessShell.Faces)


    if self.rThread:
      #if (dia < 3.0) or (dia > 5.0):
      if True:
        if (SType =='DIN967'):
          rthread = self.makeShellthread(dia, P, halfturns, False, offSet)
        else:
          rthread = self.makeShellthread(dia, P, halfturns, True, offSet)
        rthread.translate(Base.Vector(0.0, 0.0,-a_point -2.0*P))
        for threadFace in rthread.Faces:
          headFaces.append(threadFace)

        screwShell = Part.Shell(headFaces)
        screw = Part.Solid(screwShell)
      else:
        rthread = self.makeShellthread(dia, P, halfturns, False, offSet)
        rthread.translate(Base.Vector(0.0, 0.0,-a_point -2.0*P))
        for threadFace in rthread.Faces:
          headFaces.append(threadFace)

        screwShell = Part.Shell(headFaces)
        screw = Part.Solid(screwShell)
        cyl = self.cutChamfer(dia, P, l)
        screw = screw.cut(cyl)
    else:
      screwShell = Part.Shell(headFaces)
      screw = Part.Solid(screwShell)

    return screw


  # make ISO 4026 Hexagon socket set screws with flat point
  def makeIso4026(self, SType ='ISO4026', Threadtype ='M6',l=16):
    if (SType == 'ISO4026') or (SType == 'ISO4027') or (SType == 'ISO4029'):
      P, t, dp, dt, df, s = FsData["iso4026def"][Threadtype]
    elif SType == 'ISO4028':
      P, t, dp, df, z, s = FsData["iso4028def"][Threadtype]
    elif SType[:-1] == 'ASMEB18.3.5':
      P, t, dp, dt, df, s, z = FsData["asmeb18.3.5def"][Threadtype]
    d = self.getDia(Threadtype, False)
    d=d*1.01
    # generate the profile of the set-screw
    if (SType == 'ISO4026') or (SType =='ASMEB18.3.5A'):
      p0 = Base.Vector(0,0,0)
      p1 = Base.Vector(df/2,0,0)
      p2 = Base.Vector(d/2,0,-1*((d-df)/2))
      p3 = Base.Vector(d/2,0,-1*l+((d-dp)/2))
      p4 = Base.Vector(dp/2,0,-1*l)
      p5 = Base.Vector(0,0,-1*l)
      e1 = Part.makeLine(p0,p1)
      e2 = Part.makeLine(p1,p2)
      e3 = Part.makeLine(p2,p3)
      e4 = Part.makeLine(p3,p4)
      e5 = Part.makeLine(p4,p5)
      p_profile = Part.Wire([e2,e3,e4,e5])
    elif (SType == 'ISO4027') or (SType == 'ASMEB18.3.5B'):
      p0 = Base.Vector(0,0,0)
      p1 = Base.Vector(df/2,0,0)
      p2 = Base.Vector(d/2,0,-1*((d-df)/2))
      p3 = Base.Vector(d/2,0,-1*l+((d-dt)/2))
      p4 = Base.Vector(dt/2,0,-1*l)
      p5 = Base.Vector(0,0,-1*l)
      e1 = Part.makeLine(p0,p1)
      e2 = Part.makeLine(p1,p2)
      e3 = Part.makeLine(p2,p3)
      e4 = Part.makeLine(p3,p4)
      e5 = Part.makeLine(p4,p5)
      p_profile = Part.Wire([e2,e3,e4,e5])
    elif (SType == 'ISO4028') or (SType == 'ASMEB18.3.5C'):
      # the shortest available dog-point set screws often have 
      # shorter dog-points. There  is not much hard data accessible for this
      # approximate by halving the dog length for short screws
      if (l < 1.5*d):
        z = z*0.5
      p0 = Base.Vector(0,0,0)
      p1 = Base.Vector(df/2,0,0)
      p2 = Base.Vector(d/2,0,-1*((d-df)/2))
      p3 = Base.Vector(d/2,0,-1*l+((d-dp)/2+z))
      p4 = Base.Vector(dp/2,0,-1*l+z)
      p5 = Base.Vector(dp/2,0,-1*l)
      p6 = Base.Vector(0,0,-1*l)
      e1 = Part.makeLine(p0,p1)
      e2 = Part.makeLine(p1,p2)
      e3 = Part.makeLine(p2,p3)
      e4 = Part.makeLine(p3,p4)
      e5 = Part.makeLine(p4,p5)
      e6 = Part.makeLine(p5,p6)
      p_profile = Part.Wire([e2,e3,e4,e5,e6])
    elif (SType == 'ISO4029') or (SType == 'ASMEB18.3.5D'):
      p0 = Base.Vector(0,0,0)
      p1 = Base.Vector(df/2,0,0)
      p2 = Base.Vector(d/2,0,-1*((d-df)/2))
      p3 = Base.Vector(d/2,0,-1*l+((d-dp)/2))
      p4 = Base.Vector(dp/2,0,-1*l)
      p5 = Base.Vector(0,0,-1*l+math.sqrt(3)/6*dp)
      e1 = Part.makeLine(p0,p1)
      e2 = Part.makeLine(p1,p2)
      e3 = Part.makeLine(p2,p3)
      e4 = Part.makeLine(p3,p4)
      e5 = Part.makeLine(p4,p5)
      p_profile = Part.Wire([e2,e3,e4,e5])

    p_shell = p_profile.revolve(Base.Vector(0,0,0),Base.Vector(0,0,1),360)
    # generate a top face with a hex-key recess
    top_face_profile = Part.Wire([e1])
    top_face = top_face_profile.revolve(Base.Vector(0,0,0),Base.Vector(0,0,1),360)
    hex_solid, hex_shell = self.makeAllen2(s,t-1,0)
    top_face = top_face.cut(hex_solid)
    p_faces = p_shell.Faces
    p_faces.extend(top_face.Faces)
    hex_shell.translate(Base.Vector(0,0,-1))
    p_faces.extend(hex_shell.Faces)
    p_shell = Part.Shell(p_faces)
    screw = Part.Solid(p_shell)
    # chamfer the hex recess
    cham_p1 = Base.Vector(0,0,0)
    cham_p2 = Base.Vector(s/math.sqrt(3),0,0)
    cham_p3 = Base.Vector(0,0,0-s/math.sqrt(3)) #45 degree chamfer
    cham_e1 = Part.makeLine(cham_p1,cham_p2)
    cham_e2 = Part.makeLine(cham_p2,cham_p3)
    cham_profile = Part.Wire([cham_e1,cham_e2])
    cham_shell = cham_profile.revolve(Base.Vector(0,0,0),Base.Vector(0,0,1),360)
    cham_solid = Part.Solid(cham_shell)
    screw = screw.cut(cham_solid)
    # produce a modelled thread if necessary
    if self.rThread:
      # calculate the number of thread half turns
      residue, turns = math.modf((l)/P)
      halfturns = 2*int(turns)
      if residue > 0.5:
        halfturns = halfturns+9
      else:
        halfturns = halfturns+8
      # make the threaded section
      d=d/1.01
      shell_thread = self.makeShellthread(d,P,halfturns,False,0)
      thr_p1 = Base.Vector(0,0,2*P)
      thr_p2 = Base.Vector(d/2,0,2*P)
      thr_e1 = Part.makeLine(thr_p1,thr_p2)
      thr_cap_profile = Part.Wire([thr_e1])
      thr_cap = thr_cap_profile.revolve(Base.Vector(0,0,0),Base.Vector(0,0,1),360)
      thr_faces = shell_thread.Faces
      thr_faces.extend(thr_cap.Faces)
      thread_shell = Part.Shell(thr_faces)
      thread_solid = Part.Solid(thread_shell)
      thread_solid.translate(Base.Vector(0,0,2*P))
      #Part.show(thread_solid)
      screw = screw.common(thread_solid)
    return screw


  def makeCarriageBolt(self, SType = 'ASMEB18.5.2', Threadtype = '1/4in', l = 25.4) :
    d = self.getDia(Threadtype, False)
    if SType == 'ASMEB18.5.2':
      tpi,_,A,H,O,P,_,_ = FsData["asmeb18.5.2def"][Threadtype]
      A,H,O,P = (25.4*x for x in (A,H,O,P))
      pitch = 25.4/tpi
      if l <= 152.4:
        L_t = d*2+6.35
      else:
        L_t = d*2+12.7
    # lay out points for head generation
    p1 = Base.Vector(0,0,H)
    head_r = A/math.sqrt(2)
    p2 = Base.Vector(head_r*math.sin(math.pi/8),0,H-head_r+head_r*math.cos(math.pi/8))
    p3 = Base.Vector(A/2,0,0)
    p4 = Base.Vector(math.sqrt(2)/2*O,0,0)
    p5 = Base.Vector(math.sqrt(2)/2*O,0,-1*P+(math.sqrt(2)/2*O-d/2))
    p6 = Base.Vector(d/2,0,-1*P)
    # arcs must be converted to shapes in order to be merged with other line segments 
    a1 = Part.Arc(p1,p2,p3).toShape()
    l2 = Part.makeLine(p3,p4)
    l3 = Part.makeLine(p4,p5)
    l4 = Part.makeLine(p5,p6)
    wire1 = Part.Wire([a1,l2,l3,l4])
    head_shell = wire1.revolve(Base.Vector(0,0,0),Base.Vector(0,0,1),360)
    if not self.rThread:
      # simplified threaded section
      p7 = Base.Vector(d/2,0,-1*l+d/10)
      p8 = Base.Vector(d/2-d/10,0,-1*l)
      p9 = Base.Vector(0,0,-1*l)
      l5 = Part.makeLine(p6,p7)
      l6 = Part.makeLine(p7,p8)
      l7 = Part.makeLine(p8,p9)
      thread_profile_wire = Part.Wire([l5,l6,l7])
      shell_thread = thread_profile_wire.revolve(Base.Vector(0,0,0),Base.Vector(0,0,1),360)
    else:
      # modeled threaded section
      # calculate the number of thread half turns
      if l <= L_t:  # fully threaded fastener
        residue, turns = math.modf((l-P)/pitch)
        halfturns = 2*int(turns)
        if residue > 0.5:
          halfturns = halfturns+1
        shell_thread = self.makeShellthread(d,pitch,halfturns,False,0)
        shell_thread.translate(Base.Vector(0,0,-2*pitch-P))
      else:  # partially threaded fastener
        residue, turns = math.modf((L_t-P)/pitch)
        halfturns = 2*int(turns)
        if residue > 0.5:
          halfturns = halfturns+1
        shell_thread = self.makeShellthread(d,pitch,halfturns,False,0)
        shell_thread.translate(Base.Vector(0,0,-2*pitch-P-(l-L_t)))
        p7 = Base.Vector(d/2,0,-1*P-(l-L_t))
        helper_wire = Part.Wire([Part.makeLine(p6,p7)])
        shank = helper_wire.revolve(Base.Vector(0,0,0),Base.Vector(0,0,1),360)
        shell_thread = Part.Shell(shell_thread.Faces+shank.Faces)
    p_shell = Part.Shell(head_shell.Faces+shell_thread.Faces)
    p_solid = Part.Solid(p_shell)
    # cut 4 flats under the head
    for i in range(4):
      p_solid = p_solid.cut(Part.makeBox(d,A,P,Base.Vector(d/2,-1*A/2,-1*P)).rotate(Base.Vector(0,0,0),Base.Vector(0,0,1),i*90))
    # removeSplitter is equivalent to the 'Refine' option for FreeCAD PartDesign objects
    return p_solid.removeSplitter()
    

  def makeHextool(self,s_hex, k_hex, cir_hex):
    # makes a cylinder with an inner hex hole, used as cutting tool
    # create hexagon face
    mhex=Base.Matrix()
    mhex.rotateZ(math.radians(60.0))
    polygon = []
    vhex=Base.Vector(s_hex/math.sqrt(3.0),0.0,-k_hex*0.1)
    for i in range(6):
       polygon.append(vhex)
       vhex = mhex.multiply(vhex)
    polygon.append(vhex)
    hexagon = Part.makePolygon(polygon)
    hexagon = Part.Face(hexagon)

    # create circle face
    circ=Part.makeCircle(cir_hex/2.0,Base.Vector(0.0,0.0,-k_hex*0.1))
    circ=Part.Face(Part.Wire(circ))


    # Create the face with the circle as outline and the hexagon as hole
    face=circ.cut(hexagon)

    # Extrude in z to create the final cutting tool
    exHex=face.extrude(Base.Vector(0.0,0.0,k_hex*1.2))
    # Part.show(exHex)
    return exHex


  def makeShellthread(self, d, P, halfrots, withcham, offSet):
    d = float(d)

    #rotations = int(rots)-1
    halfrots_int = int(halfrots)
    rotations = int((halfrots_int / 2)-1)
    #print ("halfrots_int: ", halfrots_int, " rotations: ", rotations)
    if halfrots_int % 2 == 1:
      #FreeCAD.Console.PrintMessage("got half turn: " + str(halfrots_int) + "\n")
      halfturn = True
      # bot_off = - P/2.0 # transition of half a turn
      bot_off = 0.0 # nominal length
    else:
      halfturn = False
      bot_off = 0.0 # nominal length

    H=P*math.cos(math.radians(30)) # Gewindetiefe H
    r=d/2.0

    # helix = Part.makeHelix(P,P,d*511/1000.0,0) # make just one turn, length is identical to pitch
    helix = Part.makeHelix(P,P,d*self.Tuner/1000.0,0) # make just one turn, length is identical to pitch
    helix.translate(FreeCAD.Vector(0.0, 0.0,-P*9.0/16.0))

    extra_rad = P
    # points for screw profile
    ps0 = (r,0.0, 0.0)
    ps1 = (r-H*5.0/8.0,0.0, -P*5.0/16.0)
    ps2 = (r-H*17.0/24.0,0.0, -P*7.0/16.0) # Center of Arc
    ps3 = (r-H*5.0/8.0,0.0, -P*9.0/16.0 )
    ps4 =  (r, 0.0, -P*14.0/16.0)
    ps5 = (r,0.0, -P)
    ps6 = (r+extra_rad,0.0, -P)
    ps7 = (r+extra_rad,0.0, 0.0)

    edge0 = Part.makeLine(ps0,ps1)
    edge1 = Part.Arc(FreeCAD.Vector(ps1),FreeCAD.Vector(ps2),FreeCAD.Vector(ps3)).toShape()
    edge2 = Part.makeLine(ps3,ps4)
    edge3 = Part.makeLine(ps4,ps5)
    edge4 = Part.makeLine(ps5,ps6)
    edge5 = Part.makeLine(ps6,ps7)
    edge6 = Part.makeLine(ps7,ps0)

    W0 = Part.Wire([edge0, edge1, edge2, edge3, edge4, edge5, edge6])

    makeSolid=True
    isFrenet=True
    pipe0 = Part.Wire(helix).makePipeShell([W0],makeSolid,isFrenet)
    # pipe1 = pipe0.copy()

    TheFaces = []
    TheFaces.append(pipe0.Faces[0])
    #Part.show(pipe0.Faces[0])
    TheFaces.append(pipe0.Faces[1])
    #Part.show(pipe0.Faces[1])
    TheFaces.append(pipe0.Faces[2])
    #Part.show(pipe0.Faces[2])
    TheFaces.append(pipe0.Faces[3])
    #Part.show(pipe0.Faces[3])

    TheShell = Part.Shell(TheFaces)
    # print "Shellpoints: ", len(TheShell.Vertexes)


    i = 1
    for i in range(rotations-2):
       TheShell.translate(FreeCAD.Vector(0.0, 0.0,- P))

       for flaeche in TheShell.Faces:
         TheFaces.append(flaeche)

    #FreeCAD.Console.PrintMessage("Base-Shell: " + str(i) + "\n")
    # Make separate faces for the tip of the screw
    botFaces = []
    for i in range(rotations-2, rotations, 1):
       TheShell.translate(FreeCAD.Vector(0.0, 0.0,- P))

       for flaeche in TheShell.Faces:
         botFaces.append(flaeche)
    #FreeCAD.Console.PrintMessage("Bottom-Shell: " + str(i) + "\n")

    # making additional faces for transition to cylinder

    pc1 = (r + H/16.0,0.0,P*1/32.0)
    pc2 = (r-H*5.0/8.0,0.0,-P*5.0/16.0 )
    pc3 = (r-H*17.0/24.0,0.0, -P*7.0/16.0 ) # Center of Arc
    pc4 = (r-H*5.0/8.0,0.0, -P*9.0/16.0 )
    pc5 =  (r+ H/16.0, 0.0, -P*29.0/32.0 )

    edgec0 = Part.makeLine(pc5,pc1)
    edgec1 = Part.makeLine(pc1,pc2)
    edgec2 = Part.Arc(FreeCAD.Vector(pc2),FreeCAD.Vector(pc3),FreeCAD.Vector(pc4)).toShape()
    edgec3 = Part.makeLine(pc4,pc5)

    cut_profile = Part.Wire([edgec1, edgec2, edgec3, edgec0 ])

    alpha_rad = math.atan(2*H*17.0/24.0/P)
    alpha = math.degrees(alpha_rad)
    Hyp = P/math.cos(alpha_rad)
    # tuning = 511/1000.0
    tuning = self.Tuner/1000.0
    angled_Helix = Part.makeHelix(Hyp,Hyp*1.002/2.0,d*tuning,alpha)

    SH_faces = []

    if halfturn:
      half_Helix = Part.makeHelix(P,P/2.0,d*self.Tuner/1000.0,0) # make just half a turn
      angled_Helix.rotate(Base.Vector(0,0,0),Base.Vector(0,0,1),180)
      angled_Helix.translate(FreeCAD.Vector(0.0, 0.0,P/2.0))
      # Part.show(half_Helix)
      # Part.show(angled_Helix)
      pipe_cut = Part.Wire([half_Helix, angled_Helix]).makePipeShell([cut_profile],True,isFrenet)
      SH_faces.append(pipe_cut.Faces[0])
      SH_faces.append(pipe_cut.Faces[1])
      SH_faces.append(pipe_cut.Faces[2])
      SH_faces.append(pipe_cut.Faces[4])
      SH_faces.append(pipe_cut.Faces[5])
      SH_faces.append(pipe_cut.Faces[6])

    else:
      pipe_cut = Part.Wire(angled_Helix).makePipeShell([cut_profile],True,isFrenet)
      SH_faces.append(pipe_cut.Faces[0])
      SH_faces.append(pipe_cut.Faces[1])
      SH_faces.append(pipe_cut.Faces[2])

    # Part.show(pipe_cut)


    Shell_helix = Part.Shell(SH_faces)

    # rect_helix_profile, needed for cutting a tube-shell
    pr1 = (r +H/16.0, 0.0, 0.0)
    pr2 = (r -H/16.0, 0.0, 0.0)
    pr3 = (r -H/16.0, 0.0, P)
    pr4 = (r +H/16.0, 0.0, P)

    edge_r1 = Part.makeLine(pr1,pr2)
    edge_r2 = Part.makeLine(pr2,pr3)
    edge_r3 = Part.makeLine(pr3,pr4)
    edge_r4 = Part.makeLine(pr4,pr1)
    rect_profile = Part.Wire([edge_r1, edge_r2, edge_r3, edge_r4 ])
    rect_helix = Part.Wire(helix).makePipeShell([rect_profile], True, isFrenet)
    # if halfturn:
    #   rect_helix.rotate(Base.Vector(0,0,0),Base.Vector(0,0,1),180)
    rect_helix.translate(FreeCAD.Vector(0.0, 0.0,- P))
    # Part.show(rect_helix)

    # rect_ring, needed for cutting the Shell_helix
    pr5 = (r +H*1.1, 0.0, P*1.1)
    pr6 = (r, 0.0, P*1.1)
    pr7 = (r, 0.0, -P*1.1)
    pr8 = (r +H*1.1, 0.0, -P*1.1)

    edge_r5 = Part.makeLine(pr5,pr6)
    edge_r6 = Part.makeLine(pr6,pr7)
    edge_r7 = Part.makeLine(pr7,pr8)
    edge_r8 = Part.makeLine(pr8,pr5)
    rect_profile = Part.Wire([edge_r5, edge_r6, edge_r7, edge_r8 ])

    rect_Face =Part.Face(rect_profile)
    rect_ring= rect_Face.revolve(Base.Vector(0.0,0.0,0.0),Base.Vector(0.0,0.0,1.0),360)
    #Part.show(rect_ring)

    Shell_helix = Shell_helix.cut(rect_ring)
    Shell_helix.translate(FreeCAD.Vector(0.0, 0.0, P))
    # Part.show(Shell_helix)

    # shell_ring, the transition to a cylinder
    pr9 = (r, 0.0, P-offSet)
    pr10 = (r, 0.0, -P )
    edge_r9 = Part.makeLine(pr9,pr10)
    shell_ring= edge_r9.revolve(Base.Vector(0.0,0.0,0.0),Base.Vector(0.0,0.0,1.0),360)

    shell_ring = shell_ring.cut(pipe_cut)
    #Part.show(shell_ring)
    shell_ring = shell_ring.cut(rect_helix)
    shell_ring.translate(FreeCAD.Vector(0.0, 0.0, P))
    #Part.show(shell_ring)

    for flaeche in shell_ring.Faces:
      TheFaces.append(flaeche)

    for flaeche in Shell_helix.Faces:
      TheFaces.append(flaeche)

    if withcham:
      #FreeCAD.Console.PrintMessage("with chamfer: " + str(i) + "\n")
      # cutting of the bottom Faces
      # bot_off = 0.0 # nominal length
      cham_off = H/8.0
      cham_t = P*math.sqrt(3.0)/2.0*17.0/24.0

      # points for chamfer: common-Method
      pch0 =  (0.0, 0.0, -(rotations)*P + bot_off) # bottom center
      pch1 =  (r-cham_t,0.0, -(rotations)*P + bot_off)
      pch2 =  (r+cham_off, 0.0, -(rotations)*P + cham_t +cham_off  + bot_off)
      pch3 =  (r+cham_off, 0.0, -(rotations)*P + 3.0*P + bot_off)
      pch4 =  (0.0, 0.0, -(rotations)*P + 3.0*P + bot_off)

      edgech0 = Part.makeLine(pch0,pch1)
      edgech1 = Part.makeLine(pch1,pch2)
      edgech2 = Part.makeLine(pch2,pch3)
      edgech3 = Part.makeLine(pch3,pch4)
      edgech4 = Part.makeLine(pch4,pch0)

      Wch_wire = Part.Wire([edgech0, edgech1, edgech2, edgech3, edgech4])
      cham_Face =Part.Face(Wch_wire)
      cham_Solid = cham_Face.revolve(Base.Vector(0.0,0.0,-(rotations-1)*P),Base.Vector(0.0,0.0,1.0),360)
      # Part.show(cham_Solid)

      BotShell = Part.Shell(botFaces)
      BotShell = BotShell.common(cham_Solid)
      # Part.show(BotShell)

      cham_faces = []
      cham_faces.append(cham_Solid.Faces[0])
      cham_faces.append(cham_Solid.Faces[1])
      cham_Shell = Part.Shell(cham_faces)
      # Part.show(cham_Shell)

      pipe0.translate(FreeCAD.Vector(0.0, 0.0, -(rotations-1)*P))
      # Part.show(pipe0)

      # Part.show(Fillet_shell)
      cham_Shell = cham_Shell.cut(pipe0)
      pipe0.translate(FreeCAD.Vector(0.0, 0.0, -P))
      # Part.show(pipe0)
      cham_Shell = cham_Shell.cut(pipe0)

      '''
      botFaces2 = []
      for flaeche in BotShell.Faces:
        botFaces2.append(flaeche)
      for flaeche in cham_Shell.Faces:
        botFaces2.append(flaeche)
      '''

    else: # tip of screw without chamfer
      #FreeCAD.Console.PrintMessage("without chamfer: " + str(i) + "\n")

      commonbox = Part.makeBox(d+4.0*P, d+4.0*P, 3.0*P)
      commonbox.translate(FreeCAD.Vector(-(d+4.0*P)/2.0, -(d+4.0*P)/2.0,-(rotations)*P+bot_off))
      #commonbox.translate(FreeCAD.Vector(-(d+4.0*P)/2.0, -(d+4.0*P)/2.0,-(rotations+3)*P+bot_off))
      #Part.show(commonbox)

      BotShell = Part.Shell(botFaces)
      #Part.show(BotShell)

      BotShell = BotShell.common(commonbox)
      #BotShell = BotShell.cut(commonbox)
      bot_edges =[]
      bot_z =  1.0e-5 -(rotations)*P + bot_off

      for kante in BotShell.Edges:
         if (kante.Vertexes[0].Point.z<=bot_z) and (kante.Vertexes[1].Point.z<=bot_z):
            bot_edges.append(kante)
            # Part.show(kante)
      bot_wire = Part.Wire(Part.__sortEdges__(bot_edges))

      #botFaces2 = []
      #for flaeche in BotShell.Faces:
      #  botFaces2.append(flaeche)

      bot_face = Part.Face(bot_wire)
      bot_face.reverse()
      #botFaces2.append(bot_face)

    '''

    BotShell2 = Part.Shell(botFaces2)
    # Part.show(BotShell2)

    TheShell2 = Part.Shell(TheFaces)

    # This gives a shell
    FaceList = []
    for flaeche in TheShell2.Faces:
      FaceList.append(flaeche)
    for flaeche in BotShell2.Faces:
      FaceList.append(flaeche)

    TheShell = Part.Shell(FaceList)
    # Part.show(TheShell)
    '''
    for flaeche in BotShell.Faces:
      TheFaces.append(flaeche)
    if withcham:
      for flaeche in cham_Shell.Faces:
        TheFaces.append(flaeche)
    else:
      TheFaces.append(bot_face)
    TheShell = Part.Shell(TheFaces)

    #print self.Tuner, " ", TheShell.ShapeType, " ", TheShell.isValid(), " hrots: ", halfrots_int, " Shellpunkte: ", len(TheShell.Vertexes)

    return TheShell


  # if da is not None: make Shell for a nut else: make a screw tap
  def makeInnerThread_2(self, d, P, rotations, da, l):
    d = float(d)
    bot_off = 0.0 # nominal length
    
    if d>52.0:
      fuzzyValue = 5e-5
    else:
      fuzzyValue = 0.0

    H=P*math.cos(math.radians(30)) # Gewindetiefe H
    r=d/2.0
    
    
    helix = Part.makeHelix(P,P,d*self.Tuner/1000.0,0) # make just one turn, length is identical to pitch
    helix.translate(FreeCAD.Vector(0.0, 0.0,-P*9.0/16.0))
  
    extra_rad = P

    # points for inner thread profile
    ps0 = (r,0.0, 0.0)
    ps1 = (r-H*5.0/8.0,0.0, -P*5.0/16.0)
    ps2 = (r-H*5.0/8.0,0.0, -P*9.0/16.0 )
    ps3 =  (r, 0.0, -P*14.0/16.0)
    ps4 = (r+H*1/24.0,0.0, -P*31.0/32.0) # Center of Arc
    ps5 = (r,0.0, -P)
    
    
    ps6 = (r+extra_rad,0.0, -P)
    ps7 = (r+extra_rad,0.0, 0.0) 
     
    edge0 = Part.makeLine(ps0,ps1)
    edge1 = Part.makeLine(ps1,ps2)
    edge2 = Part.makeLine(ps2,ps3)
    edge3 = Part.Arc(FreeCAD.Vector(ps3),FreeCAD.Vector(ps4),FreeCAD.Vector(ps5)).toShape()
    edge4 = Part.makeLine(ps5,ps6)
    edge5 = Part.makeLine(ps6,ps7)
    edge6 = Part.makeLine(ps7,ps0)
     
    W0 = Part.Wire([edge0, edge1, edge2, edge3, edge4, edge5, edge6])
    # Part.show(W0, 'W0')
    
    makeSolid=True
    isFrenet=True
    pipe0 = Part.Wire(helix).makePipeShell([W0],makeSolid,isFrenet)
    #pipe1 = pipe0.copy()
  
    TheFaces = [] 
    TheFaces.append(pipe0.Faces[0])
    TheFaces.append(pipe0.Faces[1])
    TheFaces.append(pipe0.Faces[2])
    TheFaces.append(pipe0.Faces[3])
    #topHeliFaces = [pipe0.Faces[6], pipe0.Faces[8]]
    #innerHeliFaces = [pipe0.Faces[5]]
    #bottomFaces = [pipe0.Faces[4], pipe0.Faces[7]]
    
    TheShell = Part.Shell(TheFaces)
    #singleThreadShell = TheShell.copy()
    # print "Shellpoints: ", len(TheShell.Vertexes)
    if da is None:
      commonbox = Part.makeBox(d+4.0*P, d+4.0*P, 3.0*P)
      commonbox.translate(FreeCAD.Vector(-(d+4.0*P)/2.0, -(d+4.0*P)/2.0,-(3.0)*P))
      topShell = TheShell.common(commonbox)
      top_edges =[]
      top_z =  -1.0e-5 
      
      for kante in topShell.Edges:
         if (kante.Vertexes[0].Point.z>=top_z) and (kante.Vertexes[1].Point.z>=top_z):
            top_edges.append(kante)
            # Part.show(kante)
      top_wire = Part.Wire(Part.__sortEdges__(top_edges))
      top_face = Part.Face(top_wire)
      
      TheFaces = [top_face.Faces[0]]
      TheFaces.extend(topShell.Faces)
  
      for i in range(rotations-2):
         TheShell.translate(FreeCAD.Vector(0.0, 0.0,- P))
         for flaeche in TheShell.Faces:
           TheFaces.append(flaeche)
      
      #FreeCAD.Console.PrintMessage("Base-Shell: " + str(i) + "\n")
      # Make separate faces for the tip of the screw
      botFaces = []
      for i in range(rotations-2, rotations, 1):
         TheShell.translate(FreeCAD.Vector(0.0, 0.0,- P))
    
         for flaeche in TheShell.Faces:
           botFaces.append(flaeche)
      #FreeCAD.Console.PrintMessage("Bottom-Shell: " + str(i) + "\n")
      #FreeCAD.Console.PrintMessage("without chamfer: " + str(i) + "\n")
  
      commonbox = Part.makeBox(d+4.0*P, d+4.0*P, 3.0*P)
      commonbox.translate(FreeCAD.Vector(-(d+4.0*P)/2.0, -(d+4.0*P)/2.0,-(rotations)*P+bot_off))
      #commonbox.translate(FreeCAD.Vector(-(d+4.0*P)/2.0, -(d+4.0*P)/2.0,-(rotations+3)*P+bot_off))
      #Part.show(commonbox)
     
      BotShell = Part.Shell(botFaces)
      #Part.show(BotShell)
    
      BotShell = BotShell.common(commonbox)
      #BotShell = BotShell.cut(commonbox)
      bot_edges =[]
      bot_z =  1.0e-5 -(rotations)*P + bot_off
      
      for kante in BotShell.Edges:
         if (kante.Vertexes[0].Point.z<=bot_z) and (kante.Vertexes[1].Point.z<=bot_z):
            bot_edges.append(kante)
            # Part.show(kante)
      bot_wire = Part.Wire(Part.__sortEdges__(bot_edges))
         
      bot_face = Part.Face(bot_wire)
      bot_face.reverse()
    
      for flaeche in BotShell.Faces:
        TheFaces.append(flaeche)
      # if da is not None:
        # for flaeche in cham_Shell.Faces:
          # TheFaces.append(flaeche)
      # else:  
      TheFaces.append(bot_face)
      TheShell = Part.Shell(TheFaces)
      TheSolid = Part.Solid(TheShell)
      #print self.Tuner, " ", TheShell.ShapeType, " ", TheShell.isValid(), " rotations: ", rotations, " Shellpoints: ", len(TheShell.Vertexes)
      return TheSolid

    else:
      # Try to make the inner thread shell of a nut
      cham_i = 2* H * math.tan(math.radians(15.0)) # inner chamfer
      
      # points for chamfer: cut-Method
      pch0 =  (da/2.0 - 2*H, 0.0, +cham_i) # bottom chamfer
      pch1 =  (da/2.0, 0.0, 0.0)  #
      pch2 =  (da/2.0, 0.0, - 2.1*P)
      pch3 =  (da/2.0 - 2*H, 0.0, - 2.1*P) # 


      # pch2 =  (da/2.0, 0.0, l)
      # pch3 =  (da/2.0 - 2*H, 0.0, l - cham_i)
    
      edgech0 = Part.makeLine(pch0,pch1)
      edgech1 = Part.makeLine(pch1,pch2)
      edgech2 = Part.makeLine(pch2,pch3)
      edgech3 = Part.makeLine(pch3,pch0)
    
      Wch_wire = Part.Wire([edgech0, edgech1, edgech2, edgech3])
      bottom_Face =Part.Face(Wch_wire)
      #bottom_Solid = bottom_Face.revolve(Base.Vector(0.0,0.0,-(rotations-1)*P),Base.Vector(0.0,0.0,1.0),360)
      bottom_Solid = bottom_Face.revolve(Base.Vector(0.0,0.0,0.0),Base.Vector(0.0,0.0,1.0),360)
      #Part.show(cham_Solid, 'cham_Solid')
      #Part.show(Wch_wire)
      bottomChamferFace = bottom_Solid.Faces[0]

      # points for chamfer: cut-Method
      pch0t =  (da/2.0 - 2*H, 0.0, l -cham_i) # top chamfer
      pch1t =  (da/2.0, 0.0, l)  #
      pch2t =  (da/2.0, 0.0, l + 4*P)
      pch3t =  (da/2.0 - 2*H, 0.0, l + 4*P) # 
    
      edgech0t = Part.makeLine(pch0t,pch1t)
      edgech1t = Part.makeLine(pch1t,pch2t)
      edgech2t = Part.makeLine(pch2t,pch3t)
      edgech3t = Part.makeLine(pch3t,pch0t)
    
      Wcht_wire = Part.Wire([edgech0t, edgech1t, edgech2t, edgech3t])
      top_Face =Part.Face(Wcht_wire)
      top_Solid = top_Face.revolve(Base.Vector(0.0,0.0,(rotations-1)*P),Base.Vector(0.0,0.0,1.0),360)
      #Part.show(top_Solid, 'top_Solid')
      #Part.show(Wch_wire)
      topChamferFace = top_Solid.Faces[0]
      
      threeThreadFaces = TheFaces.copy()
      for k in range(1):
        TheShell.translate(FreeCAD.Vector(0.0, 0.0, P))
        for threadFace in TheShell.Faces:
          threeThreadFaces.append(threadFace)
          
      chamferShell = Part.Shell(threeThreadFaces)
      #Part.show(chamferShell, 'chamferShell')
      #Part.show(bottomChamferFace, 'bottomChamferFace')

      
      bottomPart = chamferShell.cut(bottom_Solid)
      #Part.show(bottomPart, 'bottomPart')
      bottomFuse, bottomMap = bottomChamferFace.generalFuse([chamferShell], fuzzyValue)
      #print ('bottomMap: ', bottomMap)
      #chamFuse, chamMap = chamferShell.generalFuse([bottomChamferFace])
      #print ('chamMap: ', chamMap)
      #Part.show(bottomFuse, 'bottomFuse')
      #Part.show(bottomMap[0][0], 'bMap0')
      #Part.show(bottomMap[0][1], 'bMap1')
      innerThreadFaces = [bottomMap[0][1]]
      for face in bottomPart.Faces:
        innerThreadFaces.append(face)
      #bottomShell = Part.Shell(innerThreadFaces)
      #Part.show(bottomShell)
      bottomFaces =[]
      #TheShell.translate(FreeCAD.Vector(0.0, 0.0, P))
      for k in range(1, rotations -2):
        TheShell.translate(FreeCAD.Vector(0.0, 0.0, P))
        for threadFace in TheShell.Faces:
          innerThreadFaces.append(threadFace)
      #testShell = Part.Shell(innerThreadFaces)
      #Part.show(testShell, 'testShell')
      
      chamferShell.translate(FreeCAD.Vector(0.0, 0.0, (rotations - 1)*P))
      #Part.show(chamferShell, 'chamferShell')
      #Part.show(topChamferFace, 'topChamferFace')
      topPart = chamferShell.cut(top_Solid)
      #Part.show(topPart, 'topPart')
      for face in topPart.Faces:
        innerThreadFaces.append(face)
           
      topFuse, topMap = topChamferFace.generalFuse([chamferShell], fuzzyValue)
      #print ('topMap: ', topMap)
      #Part.show(topMap[0][0], 'tMap0')
      #Part.show(topMap[0][1], 'tMap1')
      #Part.show(topFuse, 'topFuse')
      innerThreadFaces.append(topMap[0][1])
      
      #topFaces = []
      #for face in topPart.Faces:
      #  topFaces.append(face)
      #topFaces.append(topMap[0][1])
      #testTopShell = Part.Shell(topFaces)
      #Part.show(testTopShell, 'testTopShell')

      threadShell = Part.Shell(innerThreadFaces)
      #Part.show(threadShell, 'threadShell')
      
      return threadShell


  # make the ISO 4032 Hex-nut
  # make the ISO 4033 Hex-nut
  def makeIso4032(self,SType ='ISO4032', ThreadType ='M6'):
    dia = self.getDia(ThreadType, True)
    #         P, tunIn, tunEx   
    #Ptun, self.tuning, tunEx = tuningTable[ThreadType]
    if SType == 'ISO4032':
      # P, c, damax,  dw,    e,     m,   mw,   s_nom
      P, c, da, dw, e, m, mw, s = FsData["iso4032def"][ThreadType]
    if SType == 'ISO4033':
      # P, c, damax,  dw,    e,     m,   mw,   s_nom
      P, c, da, dw, e, m, mw, s = FsData["iso4033def"][ThreadType]
    if SType == 'ISO4035':
      # P, c, damax,  dw,    e,     m,   mw,   s_nom
      P, c, da, dw, e, m, mw, s = FsData["iso4035def"][ThreadType]
    if SType == 'ASMEB18.2.2.1A':
      P, da, e, m, s = FsData["asmeb18.2.2.1adef"][ThreadType]
    if SType == 'ASMEB18.2.2.4A':
      P, da, e, m_a, m_b, s = FsData["asmeb18.2.2.4def"][ThreadType]
      m = m_a
    if SType == 'ASMEB18.2.2.4B':
      P, da, e, m_a, m_b, s = FsData["asmeb18.2.2.4def"][ThreadType]
      m = m_b

    residue, turns = math.modf(m/P)
    #halfturns = 2*int(turns)
      
    if residue > 0.0:
      turns += 1.0
    if SType == 'ISO4033' and ThreadType == '(M14)':
      turns -= 1.0
    if SType == 'ISO4035' and ThreadType == 'M56':
      turns -= 1.0

    
    sqrt2_ = 1.0/math.sqrt(2.0)
    cham = (e-s)*math.sin(math.radians(15)) # needed for chamfer at nut top
    H=P*math.cos(math.radians(30)) # Gewindetiefe H
    cham_i_delta = da/2.0 - (dia/2.0-H*5.0/8.0)
    cham_i = cham_i_delta * math.tan(math.radians(15.0))
  

    if self.rThread:
      Pnt0 = Base.Vector(da/2.0-2.0*cham_i_delta,0.0,m - 2.0*cham_i)
      Pnt7 = Base.Vector(da/2.0-2.0*cham_i_delta,0.0,0.0+ 2.0*cham_i)
    else:
      Pnt0 = Base.Vector(dia/2.0-H*5.0/8.0,0.0,m - cham_i)
      Pnt7 = Base.Vector(dia/2.0-H*5.0/8.0,0.0,0.0+ cham_i)

    Pnt1 = Base.Vector(da/2.0,0.0,m)
    Pnt2 = Base.Vector(s/2.0,0.0,m)
    Pnt3 = Base.Vector(s/math.sqrt(3.0),0.0,m-cham)
    Pnt4 = Base.Vector(s/math.sqrt(3.0),0.0,cham)
    Pnt5 = Base.Vector(s/2.0,0.0,0.0)
    Pnt6 = Base.Vector(da/2.0,0.0,0.0)
    
    edge0 = Part.makeLine(Pnt0,Pnt1)
    edge1 = Part.makeLine(Pnt1,Pnt2)
    edge2 = Part.makeLine(Pnt2,Pnt3)
    edge3 = Part.makeLine(Pnt3,Pnt4)
    edge4 = Part.makeLine(Pnt4,Pnt5)
    edge5 = Part.makeLine(Pnt5,Pnt6)
    edge6 = Part.makeLine(Pnt6,Pnt7)
    edge7 = Part.makeLine(Pnt7,Pnt0)
    
    # create cutting tool for hexagon head 
    # Parameters s, k, outer circle diameter =  e/2.0+10.0     
    extrude = self.makeHextool(s, m, s*2.0)

    aWire=Part.Wire([edge0,edge1,edge2,edge3,edge4,edge5,edge6,edge7])
    # Part.show(aWire)
    aFace =Part.Face(aWire)
    head = aFace.revolve(Base.Vector(0.0,0.0,0.0),Base.Vector(0.0,0.0,1.0),360.0)
    #Part.show(head)
  
    # Part.show(extrude)
    nut = head.cut(extrude)
    #Part.show(nut, 'withoutTread')

    if self.rThread:
      #if (dia < 1.6)or (dia > 52.0):
      if (dia < 1.6)or (dia > 64.0):
        #if (dia < 3.0):
        threadCutter = self.makeInnerThread_2(dia, P, int(turns+1), None, m)
        threadCutter.translate(Base.Vector(0.0, 0.0,turns*P+0.5*P))
        #Part.show(threadCutter, 'threadCutter')
        nut = nut.cut(threadCutter)
        #chamFace = nut.Faces[0].cut(threadCutter)
        #Part.show(chamFace, 'chamFace0_')
      else:
        nutFaces = [nut.Faces[2]]
        for i in range(4,25):
          nutFaces.append(nut.Faces[i])
        # Part.show(Part.Shell(nutFaces), 'OuterNutshell')
  
        threadShell = self.makeInnerThread_2(dia, P, int(turns), da, m)
        #threadShell.translate(Base.Vector(0.0, 0.0,turns*P))
        # Part.show(threadShell, 'threadShell')
        nutFaces.extend(threadShell.Faces)
        
        nutShell = Part.Shell(nutFaces)
        nut = Part.Solid(nutShell)
        #Part.show(nutShell)
    
    return nut





  # EN 1661 Hexagon nuts with flange
  # chamfer at top of hexagon is wrong = more than 30°
  def makeEN1661(self, ThreadType ='M8'):
    dia = self.getDia(ThreadType, True)
    P, da, c, dc, dw, e, m, mw, r1, s = FsData["en1661def"][ThreadType]

    residue, turns = math.modf(m/P)
    #halfturns = 2*int(turns)
      
    if residue > 0.0:
      turns += 1.0
    
    #FreeCAD.Console.PrintMessage("the nut with isoEN1661: " + str(c) + "\n")
    cham = s*(2.0/math.sqrt(3.0)-1.0)*math.sin(math.radians(25)) # needed for chamfer at head top

    sqrt2_ = 1.0/math.sqrt(2.0)
 
    # Flange is made with a radius of c
    beta = math.radians(25.0)
    tan_beta = math.tan(beta)
    
    # Calculation of Arc points of flange edge using dc and c
    arc1_x = dc/2.0 - c/2.0 + (c/2.0)*math.sin(beta)
    arc1_z = c/2.0 + (c/2.0)*math.cos(beta)
    
    hF = arc1_z + (arc1_x -s/2.0) * tan_beta  # height of flange at center
    
    #kmean = arc1_z + (arc1_x - s/math.sqrt(3.0)) * tan_beta + mw * 1.1 + cham
    #kmean = k * 0.95
    

    #Hex-Head Points
    #FreeCAD.Console.PrintMessage("the nut with kmean: " + str(m) + "\n")
    PntH0 = Base.Vector(da/2.0,0.0,m)
    PntH1 = Base.Vector(s/2.0,0.0,m)
    edgeH1 = Part.makeLine(PntH0,PntH1)

    hWire=Part.Wire([edgeH1])
    topShell = hWire.revolve(Base.Vector(0.0,0.0,0.0),Base.Vector(0.0,0.0,1.0),360)
    #Part.show(hWire)
    #Part.show(topShell)
    
    # create a cutter ring to generate the chamfer at the top of the hex
    chamHori = s/math.sqrt(3.0) - s/2.0
    PntC1 = Base.Vector(s/2.0-chamHori,0.0,m+m)
    PntC2 = Base.Vector(s/math.sqrt(3.0)+chamHori,0.0,m+m)
    PntC3 = Base.Vector(s/2.0-chamHori,0.0,m+cham)
    PntC4 = Base.Vector(s/math.sqrt(3.0)+chamHori,0.0,m-cham-cham)   #s/math.sqrt(3.0)
    edgeC1 = Part.makeLine(PntC3, PntC1)
    edgeC2 = Part.makeLine(PntC1, PntC2)
    edgeC3 = Part.makeLine(PntC2, PntC4)
    edgeC4 = Part.makeLine(PntC4, PntC3)
    cWire = Part.Wire([edgeC4, edgeC1, edgeC2, edgeC3])
    cFace = Part.Face(cWire)
    chamCut = cFace.revolve(Base.Vector(0.0,0.0,0.0),Base.Vector(0.0,0.0,1.0),360)
    #Part.show(cWire)
    #Part.show(chamCut)


    # create hexagon
    mhex=Base.Matrix()
    mhex.rotateZ(math.radians(60.0))
    polygon = []
    vhex=Base.Vector(s/math.sqrt(3.0),0.0,m)
    for i in range(6):
       polygon.append(vhex)
       vhex = mhex.multiply(vhex)
    polygon.append(vhex)
    hexagon = Part.makePolygon(polygon)
    hexFace = Part.Face(hexagon)
    solidHex = hexFace.extrude(Base.Vector(0.0,0.0,c-m))
    #Part.show(solidHex)
    hexCham = solidHex.cut(chamCut)
    #Part.show(hexCham)
    
    topFaces = topShell.Faces
    
    topFaces.append(hexCham.Faces[1])
    topFaces.append(hexCham.Faces[2])
    topFaces.append(hexCham.Faces[8])
    topFaces.append(hexCham.Faces[13])
    topFaces.append(hexCham.Faces[14])
    topFaces.append(hexCham.Faces[12])
    topFaces.append(hexCham.Faces[6])
    
    hexFaces = [hexCham.Faces[5], hexCham.Faces[11], hexCham.Faces[10]]
    hexFaces.extend([hexCham.Faces[9], hexCham.Faces[3], hexCham.Faces[0]])
    hexShell = Part.Shell(hexFaces)


    H=P*math.cos(math.radians(30)) # Gewindetiefe H
    cham_i_delta = da/2.0 - (dia/2.0-H*5.0/8.0)
    cham_i = cham_i_delta * math.tan(math.radians(15.0))
  
    # Center of flange:
    Pnt0 = Base.Vector(0.0,0.0,hF)
    Pnt1 = Base.Vector(s/2.0,0.0,hF)
    
    # arc edge of flange:
    Pnt2 = Base.Vector(arc1_x,0.0,arc1_z)
    Pnt3 = Base.Vector(dc/2.0,0.0,c/2.0)
    Pnt4 = Base.Vector((dc-c)/2.0,0.0,0.0)
    Pnt5 = Base.Vector(da/2.0,0.0,0.0)     #start of fillet between flat and thread
    
    edge1 = Part.makeLine(Pnt0,Pnt1)
    edge2 = Part.makeLine(Pnt1,Pnt2)
    edge3 = Part.Arc(Pnt2,Pnt3,Pnt4).toShape()
    edge4 = Part.makeLine(Pnt4,Pnt5)

    # make a cutter for the hexShell
    PntHC1 = Base.Vector(0.0,0.0,arc1_z)
    PntHC2 = Base.Vector(0.0,0.0,0.0)
    
    edgeHC1 = Part.makeLine(Pnt2,PntHC1)
    edgeHC2 = Part.makeLine(PntHC1,PntHC2)
    edgeHC3 = Part.makeLine(PntHC2,Pnt0)

    HCWire = Part.Wire([edge2, edgeHC1, edgeHC2, edgeHC3, edge1])
    HCFace = Part.Face(HCWire)
    hex2Cut = HCFace.revolve(Base.Vector(0.0,0.0,0.0),Base.Vector(0.0,0.0,1.0),360)
    
    hexShell = hexShell.cut(hex2Cut)
    #Part.show(hexShell)
    
    topFaces.extend(hexShell.Faces)
    
    if self.rThread and (dia > 4.0):
      aWire=Part.Wire([edge2,edge3,edge4])
      boltIndex = 3
    
    else:
      if self.rThread:
        Pnt7 = Base.Vector(dia/2.1-H*5.0/8.0,0.0,m - cham_i)
        Pnt6 = Base.Vector(dia/2.1-H*5.0/8.0,0.0,0.0+ cham_i)
        
      else:
        Pnt7 = Base.Vector(dia/2.0-H*5.0/8.0,0.0,m - cham_i)
        Pnt6 = Base.Vector(dia/2.0-H*5.0/8.0,0.0,0.0+ cham_i)
      edge5 = Part.makeLine(Pnt5,Pnt6)
      edge6 = Part.makeLine(Pnt6,Pnt7)
      edge7 = Part.makeLine(Pnt7,PntH0)
      aWire=Part.Wire([edge2,edge3,edge4,edge5,edge6,edge7])
      boltIndex = 6


    #aFace =Part.Face(aWire)
    #Part.show(aWire)
    headShell = aWire.revolve(Base.Vector(0.0,0.0,0.0),Base.Vector(0.0,0.0,1.0),360)
    #FreeCAD.Console.PrintMessage("der Kopf mit revolve: " + str(dia) + "\n")
    #Part.show(headShell)
    chamFace = headShell.Faces[0].cut(solidHex)
    #Part.show(chamFace)
    
    topFaces.append(chamFace.Faces[0])
    for i in range(1,boltIndex):
      topFaces.append(headShell.Faces[i])

    
    if self.rThread:
      if dia < 5.0:
        nutShell = Part.Shell(topFaces)
        nut = Part.Solid(nutShell)
        #Part.show(nut, 'unthreadedNut')
        threadCutter = self.makeInnerThread_2(dia, P, int(turns+1), None, m)
        threadCutter.translate(Base.Vector(0.0, 0.0,turns*P+0.5*P))
        #Part.show(threadCutter, 'threadCutter')
        nut = nut.cut(threadCutter)
        
      else:
        threadShell = self.makeInnerThread_2(dia, P, int(turns), da, m)
        #threadShell.translate(Base.Vector(0.0, 0.0,turns*P))
        #Part.show(threadShell)
        for tFace in threadShell.Faces:
          topFaces.append(tFace)
        headShell = Part.Shell(topFaces)
        nut = Part.Solid(headShell)
    else:
      nutShell = Part.Shell(topFaces)
      nut = Part.Solid(nutShell)

    return nut


  # make ISO 7380-1 Button head Screw
  # make ISO 7380-2 Button head Screw with collar
  # make DIN 967 cross recessed pan head Screw with collar
  def makeScrewTap(self, SType = "ScrewTap", ThreadType ='M6',l=25.0, customPitch=None, customDia=None):
    if ThreadType != "Custom":
      dia = self.getDia(ThreadType, False)
      if SType == "ScrewTap":
        P, tunIn, tunEx  = FsData["tuningTable"][ThreadType]
      elif SType == "ScrewTapInch":
        P = FsData["asmeb18.3.1adef"][ThreadType][0]
    else: # custom pitch and diameter
      P = customPitch
      dia = customDia
    residue, turns = math.modf((l)/P)
    turns += 1.0
    #FreeCAD.Console.PrintMessage("ScrewTap residue: " + str(residue) + " turns: " + str(turns) + "\n")


    if self.rThread:
      screwTap = self.makeInnerThread_2(dia, P, int(turns), None, 0.0)
      screwTap.translate(Base.Vector(0.0, 0.0,(1-residue)*P))
    else:
      H=P*math.cos(math.radians(30)) # Gewindetiefe H
      r=dia/2.0

      # points for inner thread profile
      Pnt0 = Base.Vector(0.0,0.0,(1-residue)*P)
      Pnt1 = Base.Vector(r-H*5.0/8.0,0.0,(1-residue)*P)
      Pnt2 = Base.Vector(r-H*5.0/8.0,0.0,-l)
      Pnt3 = Base.Vector(0.0,0.0,-l)

      edge1 = Part.makeLine(Pnt0,Pnt1)
      edge2 = Part.makeLine(Pnt1,Pnt2)
      edge3 = Part.makeLine(Pnt2,Pnt3)
      aWire=Part.Wire([edge1,edge2,edge3])
      headShell = aWire.revolve(Base.Vector(0.0,0.0,0.0),Base.Vector(0.0,0.0,1.0),360.0)
      screwTap = Part.Solid(headShell)

    return screwTap


  # make object to cut external threads on a shaft
  def makeScrewDie(self, SType = "ScrewDie", ThreadType = 'M6', l=25.0, customPitch=None, customDia=None):
    if ThreadType != "Custom":
      dia = self.getDia(ThreadType, False)
      if SType == "ScrewDie":
        P, tunIn, tunEx  = FsData["tuningTable"][ThreadType]
      elif SType == "ScrewDieInch":
        P = FsData["asmeb18.3.1adef"][ThreadType][0]
    else: # custom pitch and diameter
      P = customPitch
      dia = customDia
    if self.rThread:
      cutDia = dia*0.75
    else:
      cutDia = dia
    refpoint = Base.Vector(0,0,-1*l)
    screwDie = Part.makeCylinder(dia*1.1/2,l,refpoint)
    screwDie = screwDie.cut(Part.makeCylinder(cutDia/2,l,refpoint))
    #screwDie = screwDie.translate(Base.Vector(0,0,-1*l))
    if self.rThread:
      residue, turns = math.modf((l)/P)
      turns += 2.0
      halfturns = 2*turns
      shell_thread = self.makeShellthread(dia,P,halfturns,False,0)
      thr_p1 = Base.Vector(0,0,2*P)
      thr_p2 = Base.Vector(dia/2,0,2*P)
      thr_e1 = Part.makeLine(thr_p1,thr_p2)
      thr_cap_profile = Part.Wire([thr_e1])
      thr_cap = thr_cap_profile.revolve(Base.Vector(0,0,0),Base.Vector(0,0,1),360)
      thr_faces = shell_thread.Faces
      thr_faces.extend(thr_cap.Faces)
      thread_shell = Part.Shell(thr_faces)
      thread_solid = Part.Solid(thread_shell)
      screwDie = screwDie.cut(thread_solid)
    return screwDie


  # make a length of standard threaded rod
  def makeThreadedRod(self, SType = "ThreadedRod", ThreadType = 'M6', l=25.0, customPitch=None, customDia=None):
    if ThreadType != "Custom":
      dia = self.getDia(ThreadType, False)
      if SType == "ThreadedRod":
        P, tunIn, tunEx  = FsData["tuningTable"][ThreadType]
      elif SType == "ThreadedRodInch":
        P = FsData["asmeb18.3.1adef"][ThreadType][0]
    else: # custom pitch and diameter
      P = customPitch
      dia = customDia
    dia = dia*1.01
    cham = P
    p0 = Base.Vector(0,0,0)
    p1 = Base.Vector(dia/2-cham,0,0)
    p2 = Base.Vector(dia/2,0,0-cham)
    p3 = Base.Vector(dia/2,0,-1*l+cham)
    p4 = Base.Vector(dia/2-cham,0,-1*l)
    p5 = Base.Vector(0,0,-1*l)
    e1 = Part.makeLine(p0,p1)
    e2 = Part.makeLine(p1,p2)
    e3 = Part.makeLine(p2,p3)
    e4 = Part.makeLine(p3,p4)
    e5 = Part.makeLine(p4,p5)
    p_profile = Part.Wire([e1,e2,e3,e4,e5])
    p_shell = p_profile.revolve(Base.Vector(0.0,0.0,0.0),Base.Vector(0.0,0.0,1.0),360.0)
    screw = Part.Solid(p_shell)
    if self.rThread:
      dia = dia/1.01
      residue, turns = math.modf((l)/P)
      halfturns = 2*int(turns)
      if residue > 0.5:
        halfturns = halfturns+7
      else:
        halfturns = halfturns+6
      # make the threaded section
      shell_thread = self.makeShellthread(dia,P,halfturns,False,0)
      thr_p1 = Base.Vector(0,0,2*P)
      thr_p2 = Base.Vector(dia/2,0,2*P)
      thr_e1 = Part.makeLine(thr_p1,thr_p2)
      thr_cap_profile = Part.Wire([thr_e1])
      thr_cap = thr_cap_profile.revolve(Base.Vector(0,0,0),Base.Vector(0,0,1),360)
      thr_faces = shell_thread.Faces
      thr_faces.extend(thr_cap.Faces)
      thread_shell = Part.Shell(thr_faces)
      thread_solid = Part.Solid(thread_shell)
      thread_solid.translate(Base.Vector(0,0,2*P))
      #Part.show(thread_solid)
      screw = screw.common(thread_solid)
    return screw


  def cutChamfer(self, dia_cC, P_cC, l_cC):
    cham_t = P_cC*math.sqrt(3.0)/2.0*17.0/24.0
    PntC0 = Base.Vector(0.0,0.0,-l_cC)
    PntC1 = Base.Vector(dia_cC/2.0-cham_t,0.0,-l_cC)
    PntC2 = Base.Vector(dia_cC/2.0+cham_t,0.0,-l_cC+cham_t+cham_t)
    PntC3 = Base.Vector(dia_cC/2.0+cham_t,0.0,-l_cC-P_cC-cham_t)
    PntC4 = Base.Vector(0.0,0.0,-l_cC-P_cC-cham_t)

    edgeC1 = Part.makeLine(PntC0,PntC1)
    edgeC2 = Part.makeLine(PntC1,PntC2)
    edgeC3 = Part.makeLine(PntC2,PntC3)
    edgeC4 = Part.makeLine(PntC3,PntC4)
    edgeC5 = Part.makeLine(PntC4,PntC0)
    CWire=Part.Wire([edgeC1,edgeC2,edgeC3,edgeC4,edgeC5])
    #Part.show(CWire)
    CFace =Part.Face(CWire)
    cyl = CFace.revolve(Base.Vector(0.0,0.0,0.0),Base.Vector(0.0,0.0,1.0),360)
    return cyl


  # cross recess type H
  def makeCross_H3(self, CrossType = '2', m = 6.9, h = 0.0):
    # m = diameter of cross at top of screw at reference level for penetration depth
    b, e_mean, g, f_mean, r, t1, alpha, beta = FsData["iso4757def"][CrossType]

    rad265 = math.radians(26.5)
    rad28 = math.radians(28.0)
    tg = (m-g)/2.0/math.tan(rad265) # depth at radius of g
    t_tot = tg + g/2.0 * math.tan(rad28) # total depth

    # print 'tg: ', tg,' t_tot: ', t_tot
    hm = m / 4.0
    hmc = m / 2.0
    rmax = m / 2.0 + hm*math.tan(rad265)

    Pnt0 = Base.Vector(0.0,0.0,hm)
    Pnt1 = Base.Vector(rmax,0.0,hm)
    Pnt3 = Base.Vector(0.0,0.0,0.0)
    Pnt4 = Base.Vector(g/2.0,0.0,-tg)
    Pnt5 = Base.Vector(0.0,0.0,-t_tot)

    edge1 = Part.makeLine(Pnt0,Pnt1)
    edge3 = Part.makeLine(Pnt1,Pnt4)
    edge4 = Part.makeLine(Pnt4,Pnt5)
    # FreeCAD.Console.PrintMessage("Edges made Pnt2: " + str(Pnt2) + "\n")

    aWire=Part.Wire([edge1,edge3,edge4])
    crossShell = aWire.revolve(Pnt3,Base.Vector(0.0,0.0,1.0),360)
    # FreeCAD.Console.PrintMessage("Peak-wire revolved: " + str(e_mean) + "\n")
    cross = Part.Solid(crossShell)
    #Part.show(cross)

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
    rbtop = b/2.0 + (hmc + tb)*math.tan(rad_beta) # radius of b-corner at hm
    rbtot = b/2.0 - (t_tot - tb)*math.tan(rad_beta) # radius of b-corner at t_tot

    dre = e_mean/2.0 / math.tan(rad_alpha_p)  # delta between corner b and corner e in x direction
    #FreeCAD.Console.PrintMessage("delta calculated: " + str(dre) + "\n")

    dx = m/2.0 * math.cos(rad92_p)
    dy = m/2.0 * math.sin(rad92_p)

    PntC0 = Base.Vector(rbtop,0.0,hmc)
    PntC1 = Base.Vector(rbtot,0.0,-t_tot)
    PntC2 = Base.Vector(rbtop+dre,+e_mean/2.0,hmc)
    PntC3 = Base.Vector(rbtot+dre,+e_mean/2.0,-t_tot)
    PntC4 = Base.Vector(rbtop+dre,-e_mean/2.0,hmc)
    PntC5 = Base.Vector(rbtot+dre,-e_mean/2.0,-t_tot)

    PntC6 = Base.Vector(rbtop+dre+dx,+e_mean/2.0+dy,hmc)
    #PntC7 = Base.Vector(rbtot+dre+dx,+e_mean/2.0+dy,-t_tot)
    PntC7 = Base.Vector(rbtot+dre+2.0*dx,+e_mean+2.0*dy,-t_tot)
    PntC8 = Base.Vector(rbtop+dre+dx,-e_mean/2.0-dy,hmc)
    #PntC9 = Base.Vector(rbtot+dre+dx,-e_mean/2.0-dy,-t_tot)
    PntC9 = Base.Vector(rbtot+dre+2.0*dx,-e_mean-2.0*dy,-t_tot)

    #wire_hm = Part.makePolygon([PntC0,PntC2,PntC6,PntC8,PntC4,PntC0])
    #face_hm =Part.Face(wire_hm)
    #Part.show(face_hm)

    wire_t_tot = Part.makePolygon([PntC1,PntC3,PntC7,PntC9,PntC5,PntC1])
    # Part.show(wire_t_tot)
    edgeC1 = Part.makeLine(PntC0,PntC1)
    #FreeCAD.Console.PrintMessage("edgeC1 mit PntC9" + str(PntC9) + "\n")

    makeSolid=True
    isFrenet=False
    corner = Part.Wire(edgeC1).makePipeShell([wire_t_tot],makeSolid,isFrenet)
    #Part.show(corner)

    rot_axis = Base.Vector(0.,0.,1.0)
    sin_res = math.sin(math.radians(90)/2.0)
    cos_res = math.cos(math.radians(90)/2.0)
    rot_axis.multiply(-sin_res) # Calculation of Quaternion-Elements
    #FreeCAD.Console.PrintMessage("Quaternion-Elements" + str(cos_res) + "\n")

    pl_rot = FreeCAD.Placement()
    pl_rot.Rotation = (rot_axis.x,rot_axis.y,rot_axis.z,cos_res) #Rotation-Quaternion 90° z-Axis

    crossShell = crossShell.cut(corner)
    #Part.show(crossShell)
    cutplace = corner.Placement

    cornerFaces = []
    cornerFaces.append(corner.Faces[0])
    cornerFaces.append(corner.Faces[1])
    cornerFaces.append(corner.Faces[3])
    cornerFaces.append(corner.Faces[4])

    cornerShell = Part.Shell(cornerFaces)
    cornerShell = cornerShell.common(cross)
    addPlace = cornerShell.Placement

    crossFaces = cornerShell.Faces

    for i in range(3):
      cutplace.Rotation = pl_rot.Rotation.multiply(corner.Placement.Rotation)
      corner.Placement=cutplace
      crossShell = crossShell.cut(corner)
      addPlace.Rotation = pl_rot.Rotation.multiply(cornerShell.Placement.Rotation)
      cornerShell.Placement = addPlace
      for coFace in cornerShell.Faces:
        crossFaces.append(coFace)

    #Part.show(crossShell)
    for i in range(1,6):
      crossFaces.append(crossShell.Faces[i])

    crossShell0 = Part.Shell(crossFaces)

    crossFaces.append(crossShell.Faces[0])
    crossShell = Part.Shell(crossFaces)

    cross = Part.Solid(crossShell)


    #FreeCAD.Console.PrintMessage("Placement: " + str(pl_rot) + "\n")

    cross.Placement.Base = Base.Vector(0.0,0.0,h)
    crossShell0.Placement.Base = Base.Vector(0.0,0.0,h)
    #Part.show(crossShell0)
    #Part.show(cross)
    return cross, crossShell0


  # Allen recess cutting tool
  # Parameters used: s_mean, k, t_min, dk
  def makeAllen2(self, s_a = 3.0, t_a = 1.5, h_a = 2.0, t_2 = 0.0 ):
    # h_a  top height location of cutting tool
    # s_a hex width
    # t_a dept of the allen
    # t_2 depth of center-bore


    if t_2 == 0.0:
      depth = s_a / 3.0
      e_cham = 2.0 * s_a / math.sqrt(3.0)
      #FreeCAD.Console.PrintMessage("allen tool: " + str(s_a) + "\n")
      
      
      # Points for an arc at the peak of the cone
      rCone = e_cham/4.0
      hyp = (depth*math.sqrt(e_cham**2/depth**2+1.0)*rCone)/e_cham
      radAlpha = math.atan(e_cham/depth)
      radBeta = math.pi/2.0 - radAlpha
      zrConeCenter=hyp - depth -t_a
      xArc1=math.sin(radBeta)*rCone
      zArc1=zrConeCenter - math.cos(radBeta)*rCone
      xArc2=math.sin(radBeta/2.0)*rCone
      zArc2=zrConeCenter - math.cos(radBeta/2.0)*rCone
      zArc3 = zrConeCenter - rCone
      
      # The round part of the cutting tool, we need for the allen hex recess
      PntH1 = Base.Vector(0.0,0.0,-t_a-depth-depth)
      PntH2 = Base.Vector(e_cham,0.0,-t_a-depth-depth)
      PntH3 = Base.Vector(e_cham,0.0,-t_a+depth)
      PntH4 = Base.Vector(0.0,0.0,-t_a-depth)
      
      PntA1 = Base.Vector(xArc1,0.0,zArc1)
      PntA2 = Base.Vector(xArc2,0.0,zArc2)
      PntA3 = Base.Vector(0.0,0.0,zArc3)
      
      edgeA1 = Part.Arc(PntA1,PntA2,PntA3).toShape()
      
      edgeH1 = Part.makeLine(PntH1,PntH2)
      edgeH2 = Part.makeLine(PntH2,PntH3)
      edgeH3 = Part.makeLine(PntH3,PntA1)
      edgeH4 = Part.makeLine(PntA3,PntH1)
      
      hWire=Part.Wire([edgeH1,edgeH2,edgeH3,edgeA1,edgeH4])
      hex_depth = -1.0-t_a-depth*1.1
    else:
      e_cham = 2.0 * s_a / math.sqrt(3.0)
      d_cent = s_a / 3.0
      depth_cent = d_cent * math.tan(math.pi/6.0)
      depth_cham = (e_cham-d_cent) * math.tan(math.pi/6.0)
      
      Pnts = [
        Base.Vector(0.0, 0.0, -t_2-depth_cent),
        Base.Vector(0.0, 0.0, -t_2-depth_cent-depth_cent),
        Base.Vector(e_cham, 0.0, -t_2-depth_cent-depth_cent),
        Base.Vector(e_cham, 0.0, -t_a+depth_cham),
        Base.Vector(d_cent, 0.0, -t_a),
        Base.Vector(d_cent, 0.0, -t_2)
      ]
      
      edges = []
      for i in range(0,len(Pnts)-1):
        edges.append(Part.makeLine(Pnts[i], Pnts[i+1]))
      edges.append(Part.makeLine(Pnts[5], Pnts[0]))
        
      hWire=Part.Wire(edges)
      hex_depth = -1.0-t_2-depth_cent*1.1
      
    #Part.show(hWire)
    hFace =Part.Face(hWire)
    roundtool = hFace.revolve(Base.Vector(0.0,0.0,0.0),Base.Vector(0.0,0.0,1.0),360)

    # create hexagon
    mhex=Base.Matrix()
    mhex.rotateZ(math.radians(60.0))
    polygon = []
    vhex=Base.Vector(s_a/math.sqrt(3.0),0.0,1.0)
    for i in range(6):
       polygon.append(vhex)
       vhex = mhex.multiply(vhex)
    polygon.append(vhex)
    hexagon = Part.makePolygon(polygon)
    hexFace = Part.Face(hexagon)
    solidHex = hexFace.extrude(Base.Vector(0.0,0.0,hex_depth))
    allen = solidHex.cut(roundtool)
    #Part.show(allen)

    allenFaces = [allen.Faces[0]]
    for i in range(2,len(allen.Faces)):
      allenFaces.append(allen.Faces[i])
    allenShell = Part.Shell(allenFaces)
    solidHex.Placement.Base = Base.Vector(0.0,0.0,h_a)
    allenShell.Placement.Base = Base.Vector(0.0,0.0,h_a)
    
    return solidHex, allenShell



  # ISO 10664 Hexalobular internal driving feature for bolts and screws
  def makeIso10664_3(self,RType ='T20',t_hl=3.0, h_hl = 0):
    # t_hl depth of the recess
    # h_hl top height location of Cutting tool
    A, B, Re = FsData["iso10664def"][RType]
    sqrt_3 = math.sqrt(3.0)
    depth=A/4.0
    offSet = 1.0

    # Chamfer cutter for the hexalobular recess
    PntH1 = Base.Vector(0.0,0.0,-t_hl-depth-1.0)
    #PntH2 = Base.Vector(A/2.0*1.02,0.0,-t_hl-depth-1.0)
    #PntH3 = Base.Vector(A/2.0*1.02,0.0,-t_hl)
    PntH2 = Base.Vector(A,0.0,-t_hl-depth-1.0)
    PntH3 = Base.Vector(A,0.0,-t_hl+depth)
    PntH4 = Base.Vector(0.0,0.0,-t_hl-depth)

    # Points for an arc at the peak of the cone
    rCone = A/4.0
    hyp = (depth*math.sqrt(A**2/depth**2+1.0)*rCone)/A
    radAlpha = math.atan(A/depth)
    radBeta = math.pi/2.0 - radAlpha
    zrConeCenter=hyp - depth -t_hl
    xArc1=math.sin(radBeta)*rCone
    zArc1=zrConeCenter - math.cos(radBeta)*rCone
    xArc2=math.sin(radBeta/2.0)*rCone
    zArc2=zrConeCenter - math.cos(radBeta/2.0)*rCone
    zArc3 = zrConeCenter - rCone

    PntA1 = Base.Vector(xArc1,0.0,zArc1)
    PntA2 = Base.Vector(xArc2,0.0,zArc2)
    PntA3 = Base.Vector(0.0,0.0,zArc3)

    edgeA1 = Part.Arc(PntA1,PntA2,PntA3).toShape()

    edgeH1 = Part.makeLine(PntH1,PntH2)
    edgeH2 = Part.makeLine(PntH2,PntH3)
    edgeH3 = Part.makeLine(PntH3,PntA1)
    edgeH4 = Part.makeLine(PntA3,PntH1)

    hWire=Part.Wire([edgeH1,edgeH2,edgeH3,edgeA1])
    cutShell = hWire.revolve(Base.Vector(0.0,0.0,0.0),Base.Vector(0.0,0.0,1.0),360)
    cutTool = Part.Solid(cutShell)


    Ri = -((B+sqrt_3*(2.*Re-A))*B+(A-4.*Re)*A)/(4.*B-2.*sqrt_3*A+(4.*sqrt_3-8.)*Re)
    #print '2nd  Ri last solution: ', Ri
    beta=math.acos(A/(4*Ri+4*Re)-(2*Re)/(4*Ri+4*Re))-math.pi/6
    #print 'beta: ', beta
    Rh=(sqrt_3*(A/2.0-Re))/2.0
    Re_x = A/2.0 - Re + Re*math.sin(beta)
    Re_y = Re*math.cos(beta)
    Ri_y = B/4.0
    Ri_x = sqrt_3*B/4.0

    mhex=Base.Matrix()
    mhex.rotateZ(math.radians(60.0))
    hexlobWireList = []

    PntRe0=Base.Vector(Re_x,-Re_y,offSet)
    PntRe1=Base.Vector(A/2.0,0.0,offSet)
    PntRe2=Base.Vector(Re_x,Re_y,offSet)
    edge0 = Part.Arc(PntRe0,PntRe1,PntRe2).toShape()
    #Part.show(edge0)
    hexlobWireList.append(edge0)

    PntRi = Base.Vector(Ri_x,Ri_y,offSet)
    PntRi2 = mhex.multiply(PntRe0)
    edge1 = Part.Arc(PntRe2,PntRi,PntRi2).toShape()
    #Part.show(edge1)
    hexlobWireList.append(edge1)

    for i in range(5):
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

    face=Part.Face(hexlobWire)

    # Extrude in z to create the cutting tool for the screw-head-face
    Helo=face.extrude(Base.Vector(0.0,0.0,-t_hl-depth-offSet))
    # Make the recess-shell for the screw-head-shell

    hexlob = Helo.cut(cutTool)
    #Part.show(hexlob)
    hexlobFaces = [hexlob.Faces[0]]
    for i in range(2,15):
      hexlobFaces.append(hexlob.Faces[i])

    hexlobShell = Part.Shell(hexlobFaces)

    hexlobShell.Placement.Base = Base.Vector(0.0,0.0,h_hl)
    Helo.Placement.Base = Base.Vector(0.0,0.0,h_hl)

    return Helo, hexlobShell


  def setThreadType(self, TType = 'simple'):
    self.simpThread = False
    self.symThread = False
    self.rThread = False
    if TType == 'simple':
      self.simpThread = True
    if TType == 'symbol':
      self.symThread = True
    if TType == 'real':
      self.rThread = True


  def setTuner(self, myTuner = 511):
    self.Tuner = myTuner


  def getDia(self, ThreadType, isNut):
    threadstring = ThreadType.strip("()")
    dia = FsData["DiaList"][threadstring][0]
    if self.sm3DPrintMode:
      if isNut:
        dia = self.smNutThrScaleA * dia + self.smNutThrScaleB
      else:
        dia = self.smScrewThrScaleA * dia + self.smScrewThrScaleB
    return dia


  def getLength(self, LenStr):
    # washers and nuts pass an int (1), for their unused length attribute
    # handle this circumstance if necessary
    if type(LenStr) == int:
      return LenStr
    # otherwise convert the string to a number using predefined rules
    if 'in' not in LenStr:
      LenFloat = float(LenStr)
    else:
      components = LenStr.strip('in').split(' ')
      total = 0
      for item in components:
        if '/' in item:
          subcmpts = item.split('/')
          total += float(subcmpts[0])/float(subcmpts[1])
        else:
          total += float(item)
      LenFloat = total*25.4
    return LenFloat


class ScrewMacro(object):
  d = QtGui.QWidget()
  d.ui = Ui_ScrewMaker()
  d.ui.setupUi(d)
  if __name__ == '__main__':
    d.show()


def main():
  o = ScrewMacro()


if __name__ == '__main__':
  main()

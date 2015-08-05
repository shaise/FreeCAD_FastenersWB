# -*- coding: utf-8 -*-
###################################################################################
#
#  ScrewCalc.py
#  A calculator utility to calculate needed hole sizes for selected fasteners
#  
#  Copyright 2015 Shai Seger <shaise at gmail dot com>
#  
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#  
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#  
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA 02110-1301, USA.
#  
#  
###################################################################################

###################################################################################
# replace below with generated code from pyuic4
###################################################################################

from PySide import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QtGui.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)

class Ui_DockWidget(object):
    def setupUi(self, DockWidget):
        DockWidget.setObjectName(_fromUtf8("DockWidget"))
        DockWidget.resize(267, 136)
        DockWidget.setFloating(True)
        self.dockWidgetContents = QtGui.QWidget()
        self.dockWidgetContents.setObjectName(_fromUtf8("dockWidgetContents"))
        self.gridLayout = QtGui.QGridLayout(self.dockWidgetContents)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.verticalLayout = QtGui.QVBoxLayout()
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.label = QtGui.QLabel(self.dockWidgetContents)
        self.label.setObjectName(_fromUtf8("label"))
        self.horizontalLayout.addWidget(self.label)
        spacerItem = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.comboFastenerType = QtGui.QComboBox(self.dockWidgetContents)
        self.comboFastenerType.setObjectName(_fromUtf8("comboFastenerType"))
        self.horizontalLayout.addWidget(self.comboFastenerType)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.horizontalLayout_2 = QtGui.QHBoxLayout()
        self.horizontalLayout_2.setObjectName(_fromUtf8("horizontalLayout_2"))
        self.label_2 = QtGui.QLabel(self.dockWidgetContents)
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.horizontalLayout_2.addWidget(self.label_2)
        spacerItem1 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout_2.addItem(spacerItem1)
        self.comboDiameter = QtGui.QComboBox(self.dockWidgetContents)
        self.comboDiameter.setObjectName(_fromUtf8("comboDiameter"))
        self.horizontalLayout_2.addWidget(self.comboDiameter)
        self.verticalLayout.addLayout(self.horizontalLayout_2)
        self.horizontalLayout_3 = QtGui.QHBoxLayout()
        self.horizontalLayout_3.setObjectName(_fromUtf8("horizontalLayout_3"))
        self.labelHoleSize = QtGui.QLabel(self.dockWidgetContents)
        self.labelHoleSize.setObjectName(_fromUtf8("labelHoleSize"))
        self.horizontalLayout_3.addWidget(self.labelHoleSize)
        spacerItem2 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout_3.addItem(spacerItem2)
        self.textHole = QtGui.QLineEdit(self.dockWidgetContents)
        self.textHole.setReadOnly(True)
        self.textHole.setObjectName(_fromUtf8("textHole"))
        self.horizontalLayout_3.addWidget(self.textHole)
        self.verticalLayout.addLayout(self.horizontalLayout_3)
        spacerItem3 = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem3)
        self.gridLayout.addLayout(self.verticalLayout, 1, 0, 1, 1)
        DockWidget.setWidget(self.dockWidgetContents)

        self.retranslateUi(DockWidget)
        QtCore.QMetaObject.connectSlotsByName(DockWidget)

    def retranslateUi(self, DockWidget):
        DockWidget.setWindowTitle(_translate("DockWidget", "Screw hole calculator", None))
        self.label.setText(_translate("DockWidget", "Fastener type:", None))
        self.label_2.setText(_translate("DockWidget", "Screw Diameter:", None))
        self.labelHoleSize.setText(_translate("DockWidget", "Suggested Hole diameter (mm):", None))

        ###################################################################################
        # End position for generated code from pyuic4
        ###################################################################################

    def fillScrewTypes(self):
        self.comboFastenerType.currentIndexChanged.connect(self.onTypeChange)
        self.comboDiameter.currentIndexChanged.connect(self.onDiameterChange)
        self.comboFastenerType.clear()
        for type in FSCScrewTypes:
            icon, name, table = type
            self.comboFastenerType.addItem(QtGui.QIcon(os.path.join(iconPath , icon)), name)
            
    def fillDiameters(self):
        self.comboDiameter.clear()
        idx = self.comboFastenerType.currentIndex()
        table = FSCScrewTypes[idx][2]
        for diam in table:
          self.comboDiameter.addItem(diam[0])
 
    def onDiameterChange(self, diamindex):
        idx = self.comboFastenerType.currentIndex()
        table = FSCScrewTypes[idx][2]
        self.textHole.setText(str(table[diamindex][1]))
         
    def onTypeChange(self, typeindex):
        self.fillDiameters()
    
from FreeCAD import Gui
from FreeCAD import Base
import FreeCAD, FreeCADGui, Part, os, math
__dir__ = os.path.dirname(__file__)
iconPath = os.path.join( __dir__, 'Icons' )

import FastenerBase
from FastenerBase import FSBaseObject
import ScrewMaker  
screwMaker = ScrewMaker.Instance()


FSCScrewHoleChart = (
  ("M1", 0.75),
  ("M1.1", 0.85),
  ("M1.2", 0.95),
  ("M1.4", 1.10),
  ("M1.6", 1.25),
  ("M1.8", 1.45),
  ("M2", 1.60),
  ("M2.2", 1.75),
  ("M2.5", 2.05),
  ("M3", 2.50),
  ("M3.5", 2.90),
  ("M4", 3.30),
  ("M4.5", 3.70),
  ("M5", 4.20),
  ("M6", 5.00),
  ("M7", 6.00),
  ("M8", 6.80),
  ("M9", 7.80),
  ("M10", 8.50),
  ("M11", 9.50),
  ("M12", 10.20),
  ("M14", 12.00),
  ("M16", 14.00),
  ("M18", 15.50),
  ("M20", 17.50),
  ("M22", 19.50),
  ("M24", 21.00),
  ("M27", 24.00),
  ("M30", 26.50),
  ("M33", 29.50),
  ("M36", 32.00),
  ("M39", 35.00),
  ("M42", 37.50),
  ("M45", 40.50),
  ("M48", 43.00),
  ("M52", 47.00),
  ("M56", 50.50),
  ("M60", 54.50),
  ("M64", 58.00),
  ("M68", 62.00)
)

FSCPEMPressNutHoleChart = (
  ("M2", 4.22),
  ("M2.5", 4.22),
  ("M3", 4.22),
  ("M3.5", 4.75),
  ("M4", 5.41),
  ("M5", 6.35),
  ("M6", 8.75),
  ("M8", 10.5),
  ("M10", 14),
  ("M12", 17)
)        

# hole size +0.08
FSCPEMStandOffHoleChart = (
  ("M3", 4.22),
  ("3.5M3", 5.41),
  ("M3.5", 5.41),
  ("M4", 7.14),
  ("M5", 7.14)
)        

FSCPEMStudHoleChart = (
  ("M2.5", 2.5),
  ("M3", 3),
  ("M3.5", 3.5),
  ("M4", 4),
  ("M5", 5),
  ("M6", 6),
  ("M8", 8)
)

FSCScrewTypes = (
  ("ISO7045.svg", "Metric Screw", FSCScrewHoleChart),
  ("PEMPressNut.svg", "PEM Press-nut", FSCPEMPressNutHoleChart),
  ("PEMBLStandoff.svg", "PEM Stand-off", FSCPEMStudHoleChart),
  ("PEMStud.svg", "PEM Stud", FSCPEMStudHoleChart)
)

# prepare a dictionary for fast search of FSCGetInnerThread
FSCScrewHoleChartDict = {}
for s in FSCScrewHoleChart:
  FSCScrewHoleChartDict[s[0]] = s[1]
       
def FSCGetInnerThread(diam):
  diam = diam.lstrip('(')
  diam = diam.rstrip(')')
  return FSCScrewHoleChartDict[diam]
       
FSScrewCalcDlg = QtGui.QDockWidget()
FSScrewCalcDlg.ui = Ui_DockWidget()
FSScrewCalcDlg.ui.setupUi(FSScrewCalcDlg)
FSScrewCalcDlg.ui.fillScrewTypes()
Gui.getMainWindow().addDockWidget(QtCore.Qt.RightDockWidgetArea, FSScrewCalcDlg)
FSScrewCalcDlg.setFloating(True)
FSScrewCalcDlg.hide()
   

class FSScrewCalcCommand:
  """Display a calculator for needed screw holes"""

  def GetResources(self):
    FreeCAD.Console.PrintLog("Getting resources\n")
    icon = os.path.join( iconPath , 'IconScrewCalc.svg')
    return {'Pixmap'  : icon , # the name of a svg file available in the resources
            'MenuText': "Screw calculator" ,
            'ToolTip' : "Show a screw hole calculator"}
 
  def Activated(self):
    if FSScrewCalcDlg.isHidden():
      FSScrewCalcDlg.show()
    else:
      FSScrewCalcDlg.hide()
    return
   
  def IsActive(self):
    return True

Gui.addCommand("FSScrewCalc", FSScrewCalcCommand())
FastenerBase.FSCommands.append("FSScrewCalc", "command")


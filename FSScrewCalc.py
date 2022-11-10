# -*- coding: utf-8 -*-
###############################################################################
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
###############################################################################

# Enable text translation support
from TranslateUtils import translate
import os
import FastenerBase
import FreeCAD
from FreeCAD import Gui
from PySide import QtCore, QtGui
import ScrewMaker
from FSutils import iconPath
screwMaker = ScrewMaker.Instance

###############################################################################
# replace below with generated code from pyuic4
###############################################################################


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
        spacerItem = QtGui.QSpacerItem(
            40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
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
        spacerItem1 = QtGui.QSpacerItem(
            40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
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
        spacerItem2 = QtGui.QSpacerItem(
            40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout_3.addItem(spacerItem2)
        self.textHole = QtGui.QLineEdit(self.dockWidgetContents)
        self.textHole.setReadOnly(True)
        self.textHole.setObjectName(_fromUtf8("textHole"))
        self.horizontalLayout_3.addWidget(self.textHole)
        self.verticalLayout.addLayout(self.horizontalLayout_3)
        spacerItem3 = QtGui.QSpacerItem(
            20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem3)
        self.gridLayout.addLayout(self.verticalLayout, 1, 0, 1, 1)
        DockWidget.setWidget(self.dockWidgetContents)

        self.retranslateUi(DockWidget)
        QtCore.QMetaObject.connectSlotsByName(DockWidget)

    def retranslateUi(self, DockWidget):
        DockWidget.setWindowTitle(_translate(
            "DockWidget", "Screw hole calculator", None))
        self.label.setText(_translate("DockWidget", "Fastener type:", None))
        self.label_2.setText(_translate("DockWidget", "Screw Diameter:", None))
        self.labelHoleSize.setText(_translate(
            "DockWidget", "Suggested Hole diameter (mm):", None))

        #######################################################################
        # End position for generated code from pyuic4
        #######################################################################

    def fillScrewTypes(self):
        self.comboFastenerType.currentIndexChanged.connect(self.onTypeChange)
        self.comboDiameter.currentIndexChanged.connect(self.onDiameterChange)
        self.comboFastenerType.clear()
        for type in FSCScrewTypes:
            icon, name, table = type
            self.comboFastenerType.addItem(
                QtGui.QIcon(os.path.join(iconPath, icon)), name)

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
    ("ISO7045.svg", "Metric Screw", ScrewMaker.FSCScrewHoleChart),
    ("PEMPressNut.svg", "PEM Press-nut", FSCPEMPressNutHoleChart),
    ("PEMBLStandoff.svg", "PEM Stand-off", FSCPEMStandOffHoleChart),
    ("PEMStud.svg", "PEM Stud", FSCPEMStudHoleChart),
    ("ASMEB18.2.1.6.svg", "Inch Screw", ScrewMaker.FSC_Inch_ScrewHoleChart)
)

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
        icon = os.path.join(iconPath, 'IconScrewCalc.svg')
        return {
            'Pixmap': icon,  # the name of a svg file available in the resources
            'MenuText': _translate("DockWidget", "Screw calculator", None),
            'ToolTip': _translate("DockWidget", "Show a screw hole calculator", None)
        }

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

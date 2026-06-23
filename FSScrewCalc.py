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

import os
import FastenerBase
import FreeCAD
from FreeCAD import Gui
from PySide import QtCore, QtGui
import ScrewMaker
from FSutils import iconPath

screwMaker = ScrewMaker.Instance

# Enable text translation support
translate = FreeCAD.Qt.translate

###############################################################################
# replace below with generated code from pyuic4
###############################################################################


try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:

    def _fromUtf8(s):
        return s

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
        # Fastener Type Layout
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.label = QtGui.QLabel(self.dockWidgetContents)
        self.label.setObjectName(_fromUtf8("label"))
        self.horizontalLayout.addWidget(self.label)
        spacerItem = QtGui.QSpacerItem(
            40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum
        )
        self.horizontalLayout.addItem(spacerItem)
        self.comboFastenerType = QtGui.QComboBox(self.dockWidgetContents)
        self.comboFastenerType.setObjectName(_fromUtf8("comboFastenerType"))
        self.horizontalLayout.addWidget(self.comboFastenerType)
        self.verticalLayout.addLayout(self.horizontalLayout)

        # Material Type Layout
        self.matWidget = QtGui.QWidget()
        self.matHorizontalLayout = QtGui.QHBoxLayout(self.matWidget)
        layout = self.matWidget.layout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        self.matHorizontalLayout.setObjectName(_fromUtf8("matHorizontalLayout"))
        self.matLabel = QtGui.QLabel(self.dockWidgetContents)
        self.matLabel.setObjectName(_fromUtf8("matlabel"))
        self.matHorizontalLayout.addWidget(self.matLabel)
        spacerItem = QtGui.QSpacerItem(
            40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum
        )
        self.matHorizontalLayout.addItem(spacerItem)
        self.comboMaterialType = QtGui.QComboBox(self.dockWidgetContents)
        self.comboMaterialType.setObjectName(_fromUtf8("comboMaterialType"))
        self.matHorizontalLayout.addWidget(self.comboMaterialType)
        self.verticalLayout.addWidget(self.matWidget)
        self.matWidget.hide()

        # screw diameter layout
        self.horizontalLayout_2 = QtGui.QHBoxLayout()
        self.horizontalLayout_2.setObjectName(_fromUtf8("horizontalLayout_2"))
        self.label_2 = QtGui.QLabel(self.dockWidgetContents)
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.horizontalLayout_2.addWidget(self.label_2)
        spacerItem1 = QtGui.QSpacerItem(
            40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum
        )
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
            40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum
        )
        self.horizontalLayout_3.addItem(spacerItem2)
        self.textHole = QtGui.QLineEdit(self.dockWidgetContents)
        self.textHole.setReadOnly(True)
        self.textHole.setObjectName(_fromUtf8("textHole"))
        self.horizontalLayout_3.addWidget(self.textHole)
        self.verticalLayout.addLayout(self.horizontalLayout_3)
        spacerItem3 = QtGui.QSpacerItem(
            20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding
        )
        self.verticalLayout.addItem(spacerItem3)
        self.gridLayout.addLayout(self.verticalLayout, 1, 0, 1, 1)
        DockWidget.setWidget(self.dockWidgetContents)

        self.retranslateUi(DockWidget)
        QtCore.QMetaObject.connectSlotsByName(DockWidget)
        self.matTable = None
        self.diamTable = None

    def retranslateUi(self, DockWidget):
        DockWidget.setWindowTitle(translate("DockWidget", "Screw hole calculator"))
        self.label.setText(translate("DockWidget", "Fastener type:"))
        self.label_2.setText(translate("DockWidget", "Screw Diameter:"))
        self.labelHoleSize.setText(translate("DockWidget", "Suggested Hole diameter (mm):"))
        self.matLabel.setText(translate("DockWidget", "Material:"))

        #######################################################################
        # End position for generated code from pyuic4
        #######################################################################

    def fillScrewTypes(self):
        self.comboFastenerType.currentIndexChanged.connect(self.onTypeChange)
        self.comboDiameter.currentIndexChanged.connect(self.onDiameterChange)
        self.comboMaterialType.currentIndexChanged.connect(self.onMaterialChange)
        self.comboFastenerType.clear()
        for type in FSCScrewTypes:
            icon, name, _diamtable, _mattable = type
            self.comboFastenerType.addItem(QtGui.QIcon(os.path.join(iconPath, icon)), name)

    def fillDiameters(self):
        self.comboDiameter.clear()
        self.comboMaterialType.clear()
        idx = self.comboFastenerType.currentIndex()
        self.matTable = FSCScrewTypes[idx][3]
        if self.matTable:
            self.matWidget.show()
            for material in self.matTable:
                self.comboMaterialType.addItem(material[0])
        else:
            self.matWidget.hide()
        self.diamTable = FSCScrewTypes[idx][2]
        for diam in self.diamTable:
            self.comboDiameter.addItem(diam[0])

    def onMaterialChange(self, matindex):
        self.matIndex = matindex
        self.updateHoleDiam()

    def onDiameterChange(self, diamindex):
        self.diamIndex = diamindex
        self.updateHoleDiam()

    def updateHoleDiam(self):
        val = self.diamTable[self.diamIndex][1]
        if self.matTable:
            val *= self.matTable[self.matIndex][1]
        stval = f"{val:.3f}".rstrip("0").rstrip(".")
        self.textHole.setText(stval)


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
    ("M12", 17),
)

# hole size +0.08
FSCPEMStandOffHoleChart = (
    ("M3", 4.22),
    ("3.5M3", 5.41),
    ("M3.5", 5.41),
    ("M4", 7.14),
    ("M5", 7.14),
)

FSCPEMStudHoleChart = (
    ("M2.5", 2.5),
    ("M3", 3),
    ("M3.5", 3.5),
    ("M4", 4),
    ("M5", 5),
    ("M6", 6),
    ("M8", 8),
)

EJOTDiamChart = (
    ("K30", 3.0),
    ("K35", 3.5),
    ("K40", 4.0),
    ("K50", 5.0),
    ("K60", 6.0),
    ("K70", 7.0),
    ("K80", 8.0),
    ("K100", 10.0),
)

EJOTMaterialChart = (
    ("ABS", 0.8),
    ("ABS PC Blend", 0.8),
    ("ASA", 0.78),
    ("PA 4.6", 0.73),
    ("PA 6", 0.75),
    ("PA 6.6", 0.75),
    ("PBT", 0.75),
    ("PE-LD", 0.70),
    ("PE-HD", 0.75),
    ("PET", 0.75),
    ("PET-GF 30", 0.8),
    ("POM", 0.75),
    ("POM-GF 30", 0.8),
    ("PP", 0.70),
    ("PP-GF 30", 0.72),
    ("PP-TV 20", 0.72),
    ("PS", 0.8),
    ("PVC", 0.8),
    ("SAN", 0.77),
    ("Other", 0.8),
)

FSCScrewTypes = (
    ("ISO7045.svg", translate("DockWidget", "Metric Screw"), ScrewMaker.FSCScrewHoleChart, None),
    ("PEMPressNut.svg", translate("DockWidget", "PEM Press-nut"), FSCPEMPressNutHoleChart, None),
    ("PEMBLStandoff.svg", translate("DockWidget", "PEM Stand-off"), FSCPEMStandOffHoleChart, None),
    ("PEMStud.svg", translate("DockWidget", "PEM Stud"), FSCPEMStudHoleChart, None),
    (
        "ASMEB18.2.1.6.svg",
        translate("DockWidget", "Inch Screw"),
        ScrewMaker.FSC_Inch_ScrewHoleChart, None,
    ),
    ("WN1446.svg", "EJOT PT", EJOTDiamChart, EJOTMaterialChart),
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
        icon = os.path.join(iconPath, "IconScrewCalc.svg")
        return {
            "Pixmap": icon,  # the name of a svg file available in the resources
            "MenuText": translate("DockWidget", "Screw calculator"),
            "ToolTip": translate("DockWidget", "Show a screw hole calculator"),
        }

    def Activated(self):
        if FSScrewCalcDlg.isHidden():
            FSScrewCalcDlg.show()
        else:
            FSScrewCalcDlg.hide()
        return

    def IsActive(self):
        return True


Gui.addCommand("Fasteners_ScrewCalculator", FSScrewCalcCommand())
FastenerBase.FSCommands.append("Fasteners_ScrewCalculator", "command")

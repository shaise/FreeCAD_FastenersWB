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
import FreeCAD
import FastenerBase
from FastenerBase import FSParam
from FastenersCmd import screwMaker
from PySide import QtCore, QtWidgets
from FreeCAD import Gui
from FSutils import iconPath
from FSutils import settings3d_file_path

# Enable text translation support
translate = FreeCAD.Qt.translate


###############################################################################################
# Task Panel
###############################################################################################

class SM3DpSettingsTaskPanel:
    """A TaskPanel for the 3D print settings."""

    def __init__(self):
        QtCore.QDir.addSearchPath("Icons", iconPath)
        self.form = Gui.PySideUic.loadUi(settings3d_file_path)
        # Make sure all properties are added.
        self.form.pushUpdate.clicked.connect(self.updateSettings)
        self.UpdateGuiFromPrefs()

    def UpdateGuiFromPrefs(self):
        spins = self.form.findChildren(QtWidgets.QDoubleSpinBox)
        for s in spins:
            propName = s.property("prefEntry")
            if propName:
                s.setValue(FSParam.GetFloat(str(propName, "utf-8"), s.value()))
        cb = self.form.comboThreadGen
        propName = cb.property("prefEntry")
        if propName:
            cb.setCurrentIndex(FSParam.GetInt(str(propName, "utf-8"), cb.currentIndex()))        

    def updatePrefsFromGui(self):
        spins = self.form.findChildren(QtWidgets.QDoubleSpinBox)
        for s in spins:
            propName = s.property("prefEntry")
            if propName:
                FSParam.SetFloat(str(propName, "utf-8"), s.value())
        cb = self.form.comboThreadGen
        propName = cb.property("prefEntry")
        if propName:
            FSParam.SetInt(str(propName, "utf-8"), cb.currentIndex())

    def updateSettings(self):
        self.updatePrefsFromGui()
        if screwMaker.updateFastenerParameters():
            for obj in FreeCAD.ActiveDocument.Objects:
                if hasattr(obj, "Thread") and obj.Thread:
                    obj.recompute()
                    print(obj.Name, obj.Thread)


    def accept(self):
        self.updateSettings()
        return True

    def reject(self):
        return True

class FS3dpSettings:
    """Display a calculator for needed screw holes"""

    def GetResources(self):
        icon = os.path.join(iconPath, "Icon3dPrint.svg")
        return {
            "Pixmap": icon,  # the name of a svg file available in the resources
            "MenuText": translate("3DpWidget", "3D Print Settings"),
            "ToolTip": translate("3DpWidget", "Show 3D Print settings for threads"),
        }

    def Activated(self):
        Gui.Control.showDialog(SM3DpSettingsTaskPanel())
        return

    def IsActive(self):
        return True


Gui.addCommand("Fasteners_3dPrintSettings", FS3dpSettings())
FastenerBase.FSCommands.append("Fasteners_3dPrintSettings", "command")

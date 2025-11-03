# -*- coding: utf-8 -*-
###############################################################################
#
#  InitGui.py
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
import FreeCADGui
from FSutils import languagePath

# Add translations path
FreeCADGui.addLanguagePath(languagePath)
FreeCADGui.updateLocale()


class FastenersWorkbench(FreeCADGui.Workbench):
    from FSutils import iconPath

    MenuText = FreeCAD.Qt.translate("Workbench", "Fasteners")
    ToolTip = FreeCAD.Qt.translate("Workbench", "Create ISO Fasteners")
    Icon = os.path.join(iconPath, "FNLogo.svg")

    def Initialize(self):
        "This function is executed when FreeCAD starts"
        from FSutils import pref_file_path
        from FSutils import iconPath
        import FSutils
        import FastenerBase
        import PEMInserts
        import FastenersCmd
        import CountersunkHoles
        import GrammaticalTools
        if FSutils.isGuiLoaded():
            import FSScrewCalc
            import FS3dpSettings
            import FSChangeParams
            

        self.list = []
        cmdlist = FastenerBase.FSGetCommands("command")
        toolbar_cmds = [
            cmd
            for cmd in cmdlist
            if not (isinstance(cmd, str) and cmd == "Fasteners_RestoreProperties")
        ]
        if toolbar_cmds:
            self.appendToolbar(FreeCAD.Qt.translate("Workbench", "FS Commands"), toolbar_cmds)
        self.appendMenu(
            FreeCAD.Qt.translate("Workbench", "Fasteners"), cmdlist
        )  # creates a new menu
        self.list.extend(cmdlist)
        screwlist1 = FastenerBase.FSGetCommands("screws")
        screwlist = []
        lastcmd = ""
        for cmd in screwlist1:
            if isinstance(cmd, tuple):  # group in sub toolbars
                group, commands, groupTitle = cmd
                # FreeCAD.Console.PrintLog("Append group toolbar " + group + "," + str(commands) + "," + groupTitle + "\n")
                parentmenu = [
                    FreeCAD.Qt.translate("Workbench", "Fasteners"),
                ]
                if group.startswith("Other "):
                    parentmenu.append(FreeCAD.Qt.translate("Workbench", "Add Other"))
                else:
                    self.appendToolbar(group, commands)
                self.list.extend(commands)
                parentmenu.append(
                    FreeCAD.Qt.translate("Workbench", "Add ")
                    + GrammaticalTools.ToSingular(groupTitle)
                )
                self.appendMenu(
                    parentmenu,
                    commands,
                )
            else:
                parentmenu = [
                    FreeCAD.Qt.translate("Workbench", "Fasteners"),
                    FreeCAD.Qt.translate("Workbench", "Add Fasteners"),
                ]
                if cmd.startswith("Other "):
                    parentmenu.append(FreeCAD.Qt.translate("Workbench", "Other"))
                else:
                    duplicateSeparator = cmd == "Separator" and lastcmd == "Separator"
                    lastcmd = cmd
                    if not duplicateSeparator:
                        screwlist.append(cmd)
                        # FreeCAD.Console.PrintLog("Append toolbar " + str(cmd) + "\n")

                self.appendMenu(
                    parentmenu,
                    cmd,
                )
        if len(screwlist) > 0:
            self.appendToolbar(
                FreeCAD.Qt.translate("Workbench", "FS Screws"), screwlist
            )  # creates main screw toolbar
            self.list.extend(screwlist)
        FreeCADGui.addIconPath(iconPath)
        FreeCADGui.addPreferencePage(pref_file_path, "Fasteners")

    def Activated(self):
        "This function is executed when the workbench is activated"
        import FastenerBase

        FastenerBase.InitCheckables()
        return

    def Deactivated(self):
        "This function is executed when the workbench is deactivated"
        return

    def ContextMenu(self, recipient):
        "This is executed whenever the user right-clicks on screen"
        # "recipient" will be either "view" or "tree"
        self.appendContextMenu(
            FreeCAD.Qt.translate("Workbench", "Fasteners"), self.list
        )  # add commands to the context menu

    def GetClassName(self):
        # this function is mandatory if this is a full python workbench
        return "Gui::PythonWorkbench"


FreeCADGui.addWorkbench(FastenersWorkbench())

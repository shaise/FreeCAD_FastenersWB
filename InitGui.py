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


class FastenersWorkbench(FreeCADGui.Workbench):

    from TranslateUtils import translate
    from FSutils import iconPath

    MenuText = translate("InitGui", "Fasteners")
    ToolTip = translate("InitGui", "Create ISO Fasteners")
    Icon = os.path.join(iconPath, "FNLogo.svg")

    def Initialize(self):
        "This function is executed when FreeCAD starts"
        from TranslateUtils import translate
        from FSutils import pref_file_path
        import FastenerBase
        import FSScrewCalc
        import PEMInserts
        import FastenersCmd
        import CountersunkHoles
        import FSChangeParams
        import GrammaticalTools

        self.list = []
        cmdlist = FastenerBase.FSGetCommands("command")
        self.appendToolbar("FS Commands", cmdlist)
        self.appendMenu(
            translate("InitGui", "Fasteners"), cmdlist
        )  # creates a new menu
        self.list.extend(cmdlist)
        screwlist1 = FastenerBase.FSGetCommands("screws")
        screwlist = []
        for cmd in screwlist1:
            # FreeCAD.Console.PrintLog("Append toolbar " + str(cmd) + "\n")
            if isinstance(cmd, tuple):  # group in sub toolbars
                self.appendToolbar(cmd[0], cmd[1])
                self.list.extend(cmd[1])
                self.appendMenu(
                    [
                        translate("InitGui", "Fasteners"),
                        translate("InitGui", "Add ") + GrammaticalTools.ToSingular(cmd[2]),
                    ],
                    cmd[1],
                )
            else:
                screwlist.append(cmd)
                self.appendMenu(
                    [
                        translate("InitGui", "Fasteners"),
                        translate("InitGui", "Add Fasteners"),
                    ],
                    cmd,
                )
        if len(screwlist) > 0:
            self.appendToolbar("FS Screws", screwlist)  # creates main screw toolbar
            self.list.extend(screwlist)
        FreeCADGui.addIconPath(FastenerBase.iconPath)
        FreeCADGui.addPreferencePage(
            pref_file_path, "Fasteners"
        )

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
            "Fasteners", self.list
        )  # add commands to the context menu

    def GetClassName(self):
        # this function is mandatory if this is a full python workbench
        return "Gui::PythonWorkbench"

FreeCADGui.addWorkbench(FastenersWorkbench())

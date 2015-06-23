# -*- coding: utf-8 -*-
###################################################################################
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
###################################################################################

class FastenersWorkbench (Workbench):
 
    MenuText = "Fasteners"
    ToolTip = "Create ISO Fasteners"
    Icon = '''
/* XPM */
static char * C:\Program Files\FreeCAD 0_15\Mod\Fasteners\wbicon_xpm[] = {
"16 16 5 1",
" 	c None",
".	c #000000",
"+	c #03B83F",
"@	c #0D8132",
"#	c #034D1C",
"                ",
" .....    ..... ",
" .+@@.    .@@#. ",
" .+@@.    .@@#. ",
" .+@@......@@#. ",
" .+@@@@@@@@@@#. ",
" .+@@@@@@@@@@#. ",
" .+@@@@@@@@@@#. ",
" .............. ",
"     .+@@#.     ",
"     .+@@#.     ",
"     .+@@#.     ",
"     .+@@#.     ",
"     .+@@#.     ",
"     ......     ",
"                "};
'''
 
    def Initialize(self):
        "This function is executed when FreeCAD starts"
        import FastenerBase, FastenersCmd, PEMInserts, FSNuts
        self.list = FastenerBase.FSGetCommands() # A list of command names created in the line above
        self.appendToolbar("My Commands",self.list) # creates a new toolbar with your commands
        # self.appendMenu("My New Menu",self.list) # creates a new menu
        # self.appendMenu(["An existing Menu","My submenu"],self.list) # appends a submenu to an existing menu
 
    def Activated(self):
        "This function is executed when the workbench is activated"
        return
 
    def Deactivated(self):
        "This function is executed when the workbench is deactivated"
        return
 
    def ContextMenu(self, recipient):
        "This is executed whenever the user right-clicks on screen"
        # "recipient" will be either "view" or "tree"
        self.appendContextMenu("My commands",self.list) # add commands to the context menu
 
    def GetClassName(self): 
        # this function is mandatory if this is a full python workbench
        return "Gui::PythonWorkbench"
 
Gui.addWorkbench(FastenersWorkbench())
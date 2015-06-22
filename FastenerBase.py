# -*- coding: utf-8 -*-
###################################################################################
#
#  FastenerBase.py
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
from FreeCAD import Gui
import FreeCAD, FreeCADGui, Part, os
__dir__ = os.path.dirname(__file__)
iconPath = os.path.join( __dir__, 'Icons' )

class FSBaseObject:
  '''Base Class for all fasteners'''
  def __init__(self, obj, attachTo):
    obj.addProperty("App::PropertyLength","offset","Parameters","Offset from surface").offset = 0.0
    obj.addProperty("App::PropertyBool", "invert", "Parameters", "Invert screw direction").invert = False
    obj.addProperty("App::PropertyLinkSub", "baseObject", "Parameters", "Base object").baseObject = attachTo
  
FSCommands = []

def FSGetCommands():
  return FSCommands

# common actions on fateners:

class FSMoveCommand:
  """Move Screw command"""

  def GetResources(self):
    icon = os.path.join( iconPath , 'IconMove.svg')
    return {'Pixmap'  : icon , # the name of a svg file available in the resources
            'MenuText': "Move fastner" ,
            'ToolTip' : "Move fastner to a new location"}
 
  def Activated(self):
    selObj = self.GetSelection()
    if selObj[0] == None:
      return
    selObj[0].baseObject = selObj[1]
    FreeCAD.ActiveDocument.recompute()
    return
   
  def IsActive(self):
    selObj = self.GetSelection()
    if selObj[0] != None:
      return True
    return False

  def GetSelection(self):
    screwObj = None
    edgeObj = None
    for selObj in Gui.Selection.getSelectionEx():
      obj = selObj.Object
      if (hasattr(obj, 'Proxy') and isinstance(obj.Proxy, FSBaseObject)):
        screwObj = obj
      elif (len(selObj.SubObjects) == 1 and isinstance(selObj.SubObjects[0],Part.Edge)):
        edgeObj = (obj, [selObj.SubElementNames[0]])
    return (screwObj, edgeObj)
        
        
Gui.addCommand('FSMove',FSMoveCommand())
FSCommands.append('FSMove')
 
 
class FSFlipCommand:
  """Flip Screw command"""

  def GetResources(self):
    icon = os.path.join( iconPath , 'IconFlip.svg')
    return {'Pixmap'  : icon , # the name of a svg file available in the resources
            'MenuText': "Flip fastner" ,
            'ToolTip' : "flip fastner orientation"}
 
  def Activated(self):
    selObj = self.GetSelection()
    if selObj == None:
      return
    selObj.invert = not(selObj.invert)
    FreeCAD.ActiveDocument.recompute()
    return
   
  def IsActive(self):
    selObj = self.GetSelection()
    if selObj != None:
      return True
    return False

  def GetSelection(self):
    screwObj = None
    if len(Gui.Selection.getSelectionEx()) == 1:
      obj = Gui.Selection.getSelectionEx()[0].Object
      if (hasattr(obj, 'Proxy') and isinstance(obj.Proxy, FSBaseObject)):
        if obj.baseObject != None:
          screwObj = obj
    return screwObj
        
        
Gui.addCommand('FSFlip',FSFlipCommand())
FSCommands.append('FSFlip')

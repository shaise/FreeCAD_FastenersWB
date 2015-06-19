# -*- coding: utf-8 -*-
###################################################################################
#
#  FastenersCmd.py
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

import ScrewMaker  
screwMaker = ScrewMaker.Ui_ScrewMaker()

class FSScrewObject:
  def __init__(self, obj, type, attachTo):
    '''"Add screw type fastener" '''
    self.itemText = "Screw"
    #self.Proxy = obj.Name
    
    obj.addProperty("App::PropertyEnumeration","type","Parameters","Screw type").type = [
        'ISO4017', 'ISO4014', 'EN1662', 'EN1665', 'ISO4762', 'ISO2009', 'ISO2010', 'ISO1580', 'ISO7045', 'ISO7046',
        'ISO7047', 'ISO1207', 'ISO7048', 'ISO7380', 'ISO10642', 'ISO14579', 'ISO14580', 'ISO14583', 'ISO7089']
    obj.addProperty("App::PropertyEnumeration","diameter","Parameters","Screw diameter standard").diameter = [
        'Auto', 'M1.6', 'M2', 'M2.5', 'M3', 'M4', 'M5', 'M6', 'M8', 'M10', 'M12', 'M14', 'M16', 'M20', 'M24',
        'M27', 'M30', 'M36', 'M42', 'M48', 'M56', 'M64' ]
    obj.addProperty("App::PropertyEnumeration","length","Parameters","Screw length").length = [
        '2', '3', '4', '5', '6', '8', '10', '12', '14', '16', '20', '25', '30', '35', '40', '45', '50',
        '55', '60', '65', '70', '80', '100', '110', '120', '130', '140', '150', '160', '180', '200' ]
    obj.addProperty("App::PropertyLength","offset","Parameters","Offset from surface").offset = 0.0
    obj.addProperty("App::PropertyBool", "invert", "Parameters", "Invert screw direction").invert = False
    obj.addProperty("App::PropertyBool", "thread", "Parameters", "Generate real thread").thread = False
    obj.addProperty("App::PropertyLinkSub", "baseObject", "Parameters", "Base object").baseObject = attachTo
    obj.type = type
    obj.Proxy = self
 
  def execute(self, fp):
    '''"Print a short message when doing a recomputation, this method is mandatory" '''
    
    try:
      baseobj = fp.baseObject[0]
      shape = baseobj.Shape.getElement(fp.baseObject[1][0])
    except:
      baseobj = None
      shape = None
   
    if (not (hasattr(self,'diameter')) or self.diameter != fp.diameter or self.length != fp.length 
          or self.type != fp.type or self.realThread != fp.thread):
      if fp.diameter == 'Auto':
        d = screwMaker.AutoDiameter(fp.type, shape)
      else:
        d = fp.diameter
        
      d , l = screwMaker.FindClosest(fp.type, d, fp.length)
      if l != fp.length:
        fp.length = l
      if d != fp.diameter:
        fp.diameter = d
      s = screwMaker.createScrewParams(d, l, fp.type + ':', False, fp.thread, True)
      self.diameter = fp.diameter
      self.length = fp.length
      self.type = fp.type
      self.realThread = fp.thread
      fp.Label = s[1]
      self.itemText = s[1]
      fp.Shape = s[0]
    else:
      FreeCAD.Console.PrintLog("Using cached object\n")
    if shape != None:
      #feature = FreeCAD.ActiveDocument.getObject(self.Proxy)
      fp.Placement = FreeCAD.Placement() # reset placement
      screwMaker.moveScrewToObject(fp, shape, fp.invert, fp.offset.Value)
    
  def getItemText():
    return self.itemText
    


class FSViewProviderTree:
  "A View provider that nests children objects under the created one"
      
  def __init__(self, obj):
    obj.Proxy = self
    self.Object = obj.Object
      
  def attach(self, obj):
    self.Object = obj.Object
    return

  def updateData(self, fp, prop):
    return

  def getDisplayModes(self,obj):
    modes=[]
    return modes

  def setDisplayMode(self,mode):
    return mode

  def onChanged(self, vp, prop):
    return

  def __getstate__(self):
    #        return {'ObjectName' : self.Object.Name}
    return None

  def __setstate__(self,state):
    if state is not None:
      import FreeCAD
      doc = FreeCAD.ActiveDocument #crap
      self.Object = doc.getObject(state['ObjectName'])
 
  def getIcon(self):
    if hasattr(self.Object, "type"):
      return os.path.join( iconPath , self.Object.type + '.svg')
    return os.path.join( iconPath , 'ISO4017.svg')



class FSScrewCommand:
  """Add Screw command"""

  def __init__(self, type, help):
    self.Type = type
    self.Help = help

  def GetResources(self):
    icon = os.path.join( iconPath , self.Type + '.svg')
    return {'Pixmap'  : icon , # the name of a svg file available in the resources
            'MenuText': "Add " + self.Help ,
            'ToolTip' : self.Help}
 
  def Activated(self):
    baseObjectNames = [ None ]
    obj = None
    selObjects = Gui.Selection.getSelectionEx()
    if len(selObjects) > 0:
      baseObjectNames = selObjects[0].SubElementNames
      obj = selObjects[0].Object
    for baseObjectName in baseObjectNames:      
      a=FreeCAD.ActiveDocument.addObject("Part::FeaturePython","Screw")
      if baseObjectName == None:
        baseObject = None
      else:
        baseObject = (obj, [baseObjectName])
      FSScrewObject(a, self.Type, baseObject)
      a.Label = a.Proxy.itemText
      FSViewProviderTree(a.ViewObject)
    FreeCAD.ActiveDocument.recompute()
    return
   
  def IsActive(self):
    return True

FSCommands = []

def FSAddCommand(type, help):
  cmd = 'FS' + type
  Gui.addCommand(cmd,FSScrewCommand(type, help))
  FSCommands.append(cmd)

def FSGetCommands():
  return FSCommands
  
FSAddCommand("ISO4017", "ISO 4017 Hex head screw")
FSAddCommand("ISO4014", "ISO 4014 Hex head bolt")
FSAddCommand("EN1662", "EN 1662 Hexagon bolt with flange, small series")
FSAddCommand("EN1665", "EN 1665 Hexagon bolt with flange, heavy series")
FSAddCommand("ISO4762", "Hexagon socket head cap screw")
FSAddCommand("ISO7380", "ISO 7380 Hexagon socket button head screw")
FSAddCommand("ISO10642", "ISO 10642 Hexagon socket countersunk head screw")
FSAddCommand("ISO2009", "ISO 2009 Slotted countersunk flat head screw")
FSAddCommand("ISO2010", "ISO 2010 Slotted raised countersunk head screw")
FSAddCommand("ISO1580", "ISO 1580 Slotted pan head screw")
FSAddCommand("ISO1207", "ISO 1207 Slotted cheese head screw")
FSAddCommand("ISO7045", "ISO 7045 Pan head screws type H cross recess")
FSAddCommand("ISO7046", "ISO 7046 Countersunk flat head screws H cross r.")
FSAddCommand("ISO7047", "ISO 7047 Raised countersunk head screws H cross r.")
FSAddCommand("ISO7048", "ISO 7048 Cheese head screws with type H cross r.")
FSAddCommand("ISO14579", "ISO 14579 Hexalobular socket head cap screws")
FSAddCommand("ISO14580", "ISO 14580 Hexalobular socket cheese head screws")
FSAddCommand("ISO14583", "ISO 14583 Hexalobular socket pan head screws")
FSAddCommand("ISO7089", "Washer")


  
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
      #FreeCAD.Console.PrintMessage(str(obj.Proxy is FastenerCmd.FSScrewObject))
      if (hasattr(obj, 'Proxy') and isinstance(obj.Proxy, FSScrewObject)):
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
      if (hasattr(obj, 'Proxy') and isinstance(obj.Proxy, FSScrewObject)):
        if obj.baseObject != None:
          screwObj = obj
    return screwObj
        
        
Gui.addCommand('FSFlip',FSFlipCommand())
FSCommands.append('FSFlip')

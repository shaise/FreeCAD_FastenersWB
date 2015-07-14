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
    obj.addProperty("App::PropertyDistance","offset","Parameters","Offset from surface").offset = 0.0
    obj.addProperty("App::PropertyBool", "invert", "Parameters", "Invert screw direction").invert = False
    obj.addProperty("App::PropertyLinkSub", "baseObject", "Parameters", "Base object").baseObject = attachTo
    
class FSGroupCommand:
    def __init__(self, cmds, menuText, toolTip):
        self.commands = cmds
        self.menuText = menuText
        self.toolTip = toolTip
    
    def GetCommands(self):
        return tuple(self.commands) # a tuple of command names that you want to group
        #return ('FSFlip', 'FSMove', 'FSSimple', 'FSFillet')

    def GetResources(self):
        return { 'MenuText': self.menuText, 'ToolTip': self.toolTip}
 
    def IsActive(self):
        return Gui.ActiveDocument != None
    #def Activated(self, index): # index is an int in the range [0, len(GetCommands)

DropButtonSupported = int(FreeCAD.Version()[1]) > 15 and  int(FreeCAD.Version()[2].split()[0]) > 5165    
    
class FSCommandList:
  def __init__(self):
    self.commands = {}
    
  def append(self, cmd, group = "screws", subgroup = None):
    if not(group in self.commands):
      self.commands[group] = []
    self.commands[group].append((cmd, subgroup))
    
  def getCommands(self, group):      
    cmdlist = []
    cmdsubs = {}
    for cmd in self.commands[group]:
      command, subgroup = cmd
      if subgroup != None and DropButtonSupported:
        if not(subgroup in cmdsubs):
          cmdsubs[subgroup] = []
          cmdlist.append(subgroup.replace(" ", ""))
        cmdsubs[subgroup].append(command)
      else:
        cmdlist.append(command)
    for subcommand in cmdsubs:
      FreeCAD.Console.PrintLog(subcommand + ":" + str(cmdsubs[subcommand]) + "\n")
      Gui.addCommand(subcommand.replace(" ", ""), FSGroupCommand(cmdsubs[subcommand], subcommand, subcommand))
    FreeCAD.Console.PrintLog(str(cmdlist) + "\n")
    return cmdlist
  
FSCommands = FSCommandList()
FSClassIcons = {}
FSLastInvert = False

def FSGetCommands(group = "screws"):
  return FSCommands.getCommands(group)


# common helpers 

# fastener chach - prevent recreation of same fasteners
FSCache = {}
def FSGetKey(*args):
  obj = None
  key = 'FS'
  for arg in args:
    key = key + '|' + str(arg)
  if key in FSCache:
    FreeCAD.Console.PrintLog("Using cached shape for: " + key + "\n")
    return (key, FSCache[key])
  return (key, None)

# sort compare function for m sizes
def MCompare(x, y):
  x1 = float(x.lstrip('M'))
  y1 = float(y.lstrip('M'))
  if x1 > y1:
    return 1
  if x1 < y1:
    return -1
  return 0

# sort compare function for string numbers
def NumCompare(x, y):
  x1 = float(x)
  y1 = float(y)
  if x1 > y1:
    return 1
  if x1 < y1:
    return -1
  return 0

class FSFaceMaker:
  '''Create a face point by point on the x,z plane'''
  def __init__(self):
    self.edges = []
    self.firstPoint = None
    
  def AddPoint(self, x, z):
    curPoint = FreeCAD.Base.Vector(x,0,z)
    if (self.firstPoint == None):
      self.firstPoint = curPoint
    else:
      self.edges.append(Part.makeLine(self.lastPoint, curPoint))
    self.lastPoint = curPoint
    FreeCAD.Console.PrintLog("Add Point: " + str(curPoint) + "\n")
    
    # add an arc starting at last point and going through x1,z1 and x2,z2
  def AddArc(self, x1, z1, x2, z2):
    midPoint = FreeCAD.Base.Vector(x1,0,z1)
    endPoint = FreeCAD.Base.Vector(x2,0,z2)
    self.edges.append(Part.Arc(self.lastPoint, midPoint, endPoint).toShape())
    self.lastPoint = endPoint

    
  def GetFace(self):
    self.edges.append(Part.makeLine(self.lastPoint, self.firstPoint))
    w = Part.Wire(self.edges)
    return Part.Face(w)
    
def FSAutoDiameterM(holeObj, table, tablepos):
  res = 'M5'
  if holeObj != None and hasattr(holeObj, 'Curve') and hasattr(holeObj.Curve, 'Radius'):
    d = holeObj.Curve.Radius * 2
    mindif = 10.0
    for m in table:
        if tablepos == -1:
          dia = float(m.lstrip('M')) + 0.1
        else:
          dia = table[m][tablepos] + 0.1
        if (dia > d):
          dif = dia - d
          if dif < mindif:
            mindif = dif
            res = m
  return res

class FSViewProviderIcon:
  "A View provider for custom icon"
      
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
    for type in FSClassIcons:
      if isinstance(self.Object.Proxy, type):
        return os.path.join( iconPath , FSClassIcons[type])
    return None

def GetEdgeName(obj, edge):
  i = 1
  for e in obj.Edges:
    if e.isEqual(edge):
      return 'Edge' + str(i)
    i = i + 1
  return None
      
    
def FSGetAttachableSelections():
  asels = []
  for selObj in Gui.Selection.getSelectionEx():
    baseObjectNames = selObj.SubElementNames
    obj = selObj.Object
    edgestable = {}
    # add explicitly selected edges
    for baseObjectName in baseObjectNames:
      shape = obj.Shape.getElement(baseObjectName)
      if not(hasattr(shape,"Curve")):
        continue
      if not(hasattr(shape.Curve,"Center")):
        continue
      asels.append((obj, [baseObjectName]))
      edgestable[baseObjectName] = 1
      
    # add all edges of a selected surface
    for subobj in selObj.SubObjects:
      if not(isinstance(subobj, Part.Face)):
        continue
      #FreeCAD.Console.PrintLog("Found face: " + str(subobj) + "\n")

      for edge in subobj.Edges:
        if not(hasattr(edge,"Curve")):
          continue
        if not(hasattr(edge.Curve,"Center")):
          continue
        edgeName = GetEdgeName(obj.Shape, edge)
        if edgeName == None or edgeName in edgestable:
          continue
        asels.append((obj, [edgeName]))
        edgestable[edgeName] = 1
          
  if len(asels) == 0:
    asels.append(None)
  return asels

def FSGenerateObjects(objectClass, name):
  for selObj in FSGetAttachableSelections():
    a=FreeCAD.ActiveDocument.addObject("Part::FeaturePython",name)
    objectClass(a, selObj)
    FSViewProviderIcon(a.ViewObject)
  FreeCAD.ActiveDocument.recompute()



# common actions on fateners:
class FSFlipCommand:
  """Flip Screw command"""

  def GetResources(self):
    icon = os.path.join( iconPath , 'IconFlip.svg')
    return {'Pixmap'  : icon , # the name of a svg file available in the resources
            'MenuText': "Invert fastner" ,
            'ToolTip' : "Invert fastner orientation"}
 
  def Activated(self):
    selObjs = self.GetSelection()
    if len(selObjs) == 0:
      return
    for selObj in selObjs:
      FreeCAD.Console.PrintLog("sel obj: " + str(selObj.invert) + "\n")
      selObj.invert = not(selObj.invert)
    FreeCAD.ActiveDocument.recompute()
    return
   
  def IsActive(self):
    selObjs = self.GetSelection()
    return len(selObjs) > 0

  def GetSelection(self):
    screwObj = []
    for selobj in Gui.Selection.getSelectionEx():
      obj = selobj.Object
      #FreeCAD.Console.PrintLog("sel obj: " + str(obj) + "\n")
      if (hasattr(obj, 'Proxy') and isinstance(obj.Proxy, FSBaseObject)):
        if obj.baseObject != None:
          screwObj.append(obj)
    return screwObj
        
        
Gui.addCommand('FSFlip',FSFlipCommand())
FSCommands.append('FSFlip', "command")

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
FSCommands.append('FSMove', "command")
 
class FSMakeSimpleCommand:
  """Move Screw command"""

  def GetResources(self):
    icon = os.path.join( iconPath , 'IconShape.svg')
    return {'Pixmap'  : icon , # the name of a svg file available in the resources
            'MenuText': "Simplify shape" ,
            'ToolTip' : "Change object to simple non-parametric shape"}
 
  def Activated(self):
    for selObj in Gui.Selection.getSelectionEx():
      obj = selObj.Object
      FreeCAD.Console.PrintLog("sel shape: " + str(obj.Shape) + "\n")
      if isinstance(obj.Shape, (Part.Solid, Part.Compound)):
        FreeCAD.Console.PrintLog("simplify shape: " + obj.Name + "\n")
        cobj = FreeCAD.ActiveDocument.addObject("Part::Feature", obj.Label + "_Copy")
        cobj.Shape = obj.Shape;
        Gui.ActiveDocument.getObject(obj.Name).Visibility = False
    FreeCAD.ActiveDocument.recompute()
    return
   
  def IsActive(self):
    if len(Gui.Selection.getSelectionEx()) > 0:
      return True
    return False
        
        
Gui.addCommand('FSSimple',FSMakeSimpleCommand())
FSCommands.append('FSSimple', "command")
 

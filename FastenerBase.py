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
from FreeCAD import Base
from PySide import QtGui
import FreeCAD, FreeCADGui, Part, os, math, sys
import DraftVecUtils

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

DropButtonSupported = int(FreeCAD.Version()[1]) > 15 # and  int(FreeCAD.Version()[2].split()[0]) >= 5165
RadioButtonSupported = int(FreeCAD.Version()[1]) > 15 # and  int(FreeCAD.Version()[2].split()[0]) >= 5560   
FSParam = FreeCAD.ParamGet("User parameter:BaseApp/Preferences/Mod/Fasteners")
GroupButtonMode = FSParam.GetInt("ScrewToolbarGroupMode", 0) # 0 = nine, 1 = separate toolbar 2 = drop down buttons
if GroupButtonMode == 2 and not(DropButtonSupported):
  GroupButtonMode = 1
    
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
      if subgroup != None and GroupButtonMode > 0:
        if not(subgroup in cmdsubs):
          cmdsubs[subgroup] = []
          if GroupButtonMode == 2:
            cmdlist.append(subgroup.replace(" ", ""))
            cmdlist.append("Separator")
        cmdsubs[subgroup].append(command)     
      else:
        cmdlist.append(command)
    for subcommand in cmdsubs:
      if GroupButtonMode == 2:
        Gui.addCommand(subcommand.replace(" ", ""), FSGroupCommand(cmdsubs[subcommand], subcommand, subcommand))
      else:
        cmdlist.append((subcommand.replace(" ", ""), cmdsubs[subcommand]))
    return cmdlist
  
FSCommands = FSCommandList()
FSClassIcons = {}
FSLastInvert = False

def FSGetCommands(group = "screws"):
  return FSCommands.getCommands(group)

# fastener types

class FSFastenerType:
  def __init__(self, typeName, hasLength, lengthFixed):
    self.typeName = typeName
    self.hasLength = hasLength
    self.lengthFixed = lengthFixed
    self.items = []
    
FSFasenerTypeDB = {}
def FSAddFastenerType(typeName, hasLength = True, lengthFixed = True):
  FSFasenerTypeDB[typeName] = FSFastenerType(typeName, hasLength, lengthFixed)
  
def FSAddItemsToType(typeName, item):
  if not(typeName in FSFasenerTypeDB):
    return
  FSFasenerTypeDB[typeName].items.append(item)

# common helpers 

# show traceback of system error
def FSShowError():
  global lastErr
  lastErr = sys.exc_info()
  tb = lastErr[2]
  tbnext = tb
  x = 10
  while tbnext != None and x > 0:
    FreeCAD.Console.PrintError("At " + tbnext.tb_frame.f_code.co_filename + " Line " + str(tbnext.tb_lineno) + "\n")
    tbnext = tbnext.tb_next
    x = x - 1
  FreeCAD.Console.PrintError(str(lastErr[1]) + ": " + lastErr[1].__doc__ + "\n")


# get instance of a toolbar item
def FSGetToolbarItem(tname, iname):
  mw = QtGui.qApp.activeWindow()
  tb = None
  for c in mw.children():
    if isinstance(c, QtGui.QToolBar) and c.windowTitle() == tname:
      tb = c
      break
  if tb == None:
    return None
  for c in tb.children():
    if isinstance(c, QtGui.QToolButton) and c.text() == iname:
      return c
  return None
      

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

def MToFloat(m):
    m = m.lstrip('(');
    m = m.rstrip(')');
    return float(m.lstrip('M'))
  
# sort compare function for m sizes
def MCompare(x, y):
  x1 = MToFloat(x)
  y1 = MToFloat(y)
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
    #FreeCAD.Console.PrintLog("Add Point: " + str(curPoint) + "\n")
    
    # add an arc starting at last point and going through x1,z1 and x2,z2
  def AddArc(self, x1, z1, x2, z2):
    midPoint = FreeCAD.Base.Vector(x1,0,z1)
    endPoint = FreeCAD.Base.Vector(x2,0,z2)
    self.edges.append(Part.Arc(self.lastPoint, midPoint, endPoint).toShape())
    self.lastPoint = endPoint
    
    # add an arc starting at last point, with relative center xc, zc and angle a
  def AddArc2(self, xc, zc, a):
    # convert to radians
    a = math.radians(a)
    # get absolute center
    xac = self.lastPoint.x + xc
    zac = self.lastPoint.z + zc
    # start angle
    sa = math.atan2(-zc, -xc)
    # radius
    r = math.sqrt(xc * xc + zc * zc)
    # middle point
    sa += a / 2.0
    #FreeCAD.Console.PrintLog("ang1: " + str(math.degrees(sa)) + "\n")
    x1 = xac + r * math.cos(sa)
    z1 = zac + r * math.sin(sa)
    # end point
    sa += a / 2.0
    #FreeCAD.Console.PrintLog("ang2: " + str(math.degrees(sa)) + "\n")
    x2 = xac + r * math.cos(sa)
    z2 = zac + r * math.sin(sa)
    self.AddArc(x1, z1, x2, z2)
    
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
          dia = MToFloat(m) + 0.1
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
    if e.isSame(edge):
      return 'Edge' + str(i)
    i = i + 1
  return None
      
    
def FSGetAttachableSelections():
  asels = []
  for selObj in Gui.Selection.getSelectionEx():
    baseObjectNames = selObj.SubElementNames
    obj = selObj.Object
    grp = obj.getParentGeoFeatureGroup()
    if grp != None and hasattr(grp,'TypeId') and grp.TypeId == 'PartDesign::Body' :
      obj = grp
    edgestable = {}
    # add explicitly selected edges
    for baseObjectName in baseObjectNames:
      shape = obj.Shape.getElement(baseObjectName)
      if not(hasattr(shape,"Curve")):
        continue
      if not(hasattr(shape.Curve,"Center")):
        continue
      asels.append((obj, [baseObjectName]))
      FreeCAD.Console.PrintLog("Linking to " + obj.Name + "[" + baseObjectName + "].\n")
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

def FSMoveToObject(ScrewObj_m, attachToObject, invert, offset):
    Pnt1 = None
    Axis1 = None
    Axis2 = None
    s = attachToObject
    if hasattr(s,"Curve"):
      if hasattr(s.Curve,"Center"):
          Pnt1 = s.Curve.Center
          Axis1 = s.Curve.Axis
    if hasattr(s,'Surface'):
      #print 'the object is a face!'
      if hasattr(s.Surface,'Axis'):
          Axis1 = s.Surface.Axis

    if hasattr(s,'Point'):
      FreeCAD.Console.PrintLog( "the object seems to be a vertex! "+ str(s.Point) + "\n")
      Pnt1 = s.Point
            
    if (Axis1 != None):
      if invert:
        Axis1 = Base.Vector(0,0,0) - Axis1
      
      Pnt1 = Pnt1 + Axis1 * offset
      #FreeCAD.Console.PrintLog( "Got Axis1: " + str(Axis1) + "\n")
      Axis2 = Base.Vector(0.0,0.0,1.0)
      Axis2_minus = Base.Vector(0.0,0.0,-1.0)
        
      # Calculate angle
      if Axis1 == Axis2:
          normvec = Base.Vector(1.0,0.0,0.0)
          result = 0.0
      else:
          if Axis1 == Axis2_minus:
              normvec = Base.Vector(1.0,0.0,0.0)
              result = math.pi
          else:
              normvec = Axis1.cross(Axis2) # Berechne Achse der Drehung = normvec
              normvec.normalize() # Normalisieren fuer Quaternionenrechnung
              #normvec_rot = normvec
              result = DraftVecUtils.angle(Axis1, Axis2, normvec) # Winkelberechnung
      sin_res = math.sin(result/2.0)
      cos_res = math.cos(result/2.0)
      normvec.multiply(-sin_res) # Berechnung der Quaternionen-Elemente
              
      #FreeCAD.Console.PrintLog( "Winkel = "+ str(math.degrees(result)) + "\n")
      #FreeCAD.Console.PrintLog("Normalvektor: "+ str(normvec) + "\n")
        
      pl = FreeCAD.Placement()
      pl.Rotation = (normvec.x,normvec.y,normvec.z,cos_res) #Drehungs-Quaternion
      
      #FreeCAD.Console.PrintLog("pl mit Rot: "+ str(pl) + "\n")
      ScrewObj_m.Placement = FreeCAD.Placement()
      ScrewObj_m.Placement.Rotation = pl.Rotation.multiply(ScrewObj_m.Placement.Rotation)
      ScrewObj_m.Placement.move(Pnt1)


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
 

FSMatchOuter = False
FSMatchIconNeedUpdate = 0

# frecad 0.15 version:
class FSToggleMatchTypeCommand:
  """Toggle screw matching method"""

  def GetResources(self):
    self.menuText = "Toggle Match Type"
    self.iconInner = os.path.join( iconPath , 'IconMatchTypeInner.svg')
    self.iconOuter = os.path.join( iconPath , 'IconMatchTypeOuter.svg')
    return {'Pixmap'  : self.iconInner , # the name of a svg file available in the resources
            'MenuText': self.menuText ,
            'ToolTip' : "Toggle auto screw diameter matching inner<->outer thread"}
 
  def Activated(self):
    global FSMatchOuter
    if not(hasattr(self, 'toolbarItem')):
      self.toolbarItem = FSGetToolbarItem("FS Commands", self.menuText)
    if self.toolbarItem == None:
      return
    FSMatchOuter = not(FSMatchOuter)
    self.UpdateIcon()
    return
    
  def UpdateIcon(self):
    if FSMatchOuter:
      self.toolbarItem.setIcon(QtGui.QIcon(self.iconOuter))    
    else:
      self.toolbarItem.setIcon(QtGui.QIcon(self.iconInner))
    
  def IsActive(self):
    global FSMatchIconNeedUpdate
    if FSMatchIconNeedUpdate > 0:
      FSMatchIconNeedUpdate = FSMatchIconNeedUpdate - 1
      if FSMatchIconNeedUpdate == 0:
        self.UpdateIcon()
    return True
        

#freecad v0.16 version:
class FSMatchTypeInnerCommand:
    def Activated(self, index):
        pass

    def GetResources(self):
        return { 'Pixmap'  : os.path.join( iconPath , 'IconMatchTypeInner.svg'),
                 'MenuText': 'Match screws by inner thread diameter (Tap hole)', 
                 'Checkable': True}


class FSMatchTypeOuterCommand:
    def Activated(self, index):
        pass
        
    def GetResources(self):
        return { 'Pixmap'  : os.path.join( iconPath , 'IconMatchTypeOuter.svg'),
                 'MenuText': 'Match screws by outer thread diameter (Pass hole)', 
                 'Checkable': False}

class FSMatchTypeGroupCommand:
    def GetCommands(self):
        return ("FSMatchTypeInner", "FSMatchTypeOuter") # a tuple of command names that you want to group

    def Activated(self, index):
        if index == 0:
            FSMatchOuter = False
            FreeCAD.Console.PrintLog("Set auto diameter to match inner thread\n")
        else:
            FSMatchOuter = True
            FreeCAD.Console.PrintLog("Set auto diameter to match outer thread\n")

    def GetDefaultCommand(self): # return the index of the tuple of the default command. This method is optional and when not implemented '0' is used 
        return 0

    def GetResources(self):
        return { 'MenuText': 'Screw diamter matching mode', 'ToolTip': 'Screw diamter matching mode (by inner or outer thread diameter)', 'DropDownMenu': False, 'Exclusive' : True }
       
    def IsActive(self): # optional
        return True

if RadioButtonSupported:
    FreeCADGui.addCommand('FSMatchTypeInner',FSMatchTypeInnerCommand())
    FreeCADGui.addCommand('FSMatchTypeOuter',FSMatchTypeOuterCommand())
    FreeCADGui.addCommand('FSMatchTypeGroup',FSMatchTypeGroupCommand())
    FSCommands.append('FSMatchTypeGroup', "command")
else:
    Gui.addCommand('FSToggleMatchType',FSToggleMatchTypeCommand())
    FSCommands.append('FSToggleMatchType', "command")
 
###################################################################################
# Generate BOM command
###################################################################################

class FSMakeBomCommand:
  """Generate fasteners bill of material"""

  def GetResources(self):
    icon = os.path.join( iconPath , 'IconBOM.svg')
    return {'Pixmap'  : icon , # the name of a svg file available in the resources
            'MenuText': "Generate BOM" ,
            'ToolTip' : "Generate fasteners bill of material"}
 
  def Activated(self):
    self.fastenerDB = {}
    sheet = FreeCAD.ActiveDocument.addObject('Spreadsheet::Sheet','Fasteners_BOM')
    sheet.setColumnWidth('A', 200)
    sheet.set('A1', "Type")
    sheet.set('B1', "Qty")
    for obj in FreeCAD.ActiveDocument.Objects:
      name = filter(lambda c: not c.isdigit(), obj.Name)
      method = getattr(self, 'Add' + name, lambda x: "nothing")
      method(obj)
      FreeCAD.Console.PrintLog(name + "\n")
    line = 2
    for fastener in sorted(self.fastenerDB.keys()):
      sheet.set('A' + str(line), fastener)
      sheet.set('B' + str(line), str(self.fastenerDB[fastener]))
      line += 1
    FreeCAD.ActiveDocument.recompute()
    return
    
  def AddFastener(self, fastener):
    if self.fastenerDB.has_key(fastener):
      self.fastenerDB[fastener] = self.fastenerDB[fastener] + 1
    else:
      self.fastenerDB[fastener] = 1
      
  def AddScrew(self, obj):
    self.AddFastener(obj.type + " Screw " + obj.diameter + "x" + obj.length)
    
  def AddNut(self, obj):
    if hasattr(obj, 'type'):
      type = obj.type
    else:
      type = 'ISO4033'
    self.AddFastener(type + " Nut " + obj.diameter)

  def AddWasher(self, obj):
    self.AddFastener(obj.type + " Washer " + obj.diameter)
    
  def AddScrewTap(self, obj):
    self.AddFastener("ScrewTap " + obj.diameter + "x" + str(obj.length))
    
  def AddPressNut(self, obj):
    self.AddFastener("PEM PressNut " + obj.diameter + "-" + obj.tcode)
    
  def AddStandoff(self, obj):
    self.AddFastener("PEM Standoff " + obj.diameter + "x" + obj.length)
    
  def AddStud(self, obj):
    self.AddFastener("PEM Stud " + obj.diameter + "x" + obj.length)
    
    
  def IsActive(self):
    return Gui.ActiveDocument != None
        
        
Gui.addCommand('FSMakeBOM',FSMakeBomCommand())
FSCommands.append('FSMakeBOM', "command")

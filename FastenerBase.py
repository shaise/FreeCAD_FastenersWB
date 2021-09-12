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
from screw_maker import *

__dir__ = os.path.dirname(__file__)
iconPath = os.path.join( __dir__, 'Icons' )

class FSBaseObject:
  '''Base Class for all fasteners'''
  def __init__(self, obj, attachTo):
    obj.addProperty("App::PropertyDistance","offset","Parameters","Offset from surface").offset = 0.0
    obj.addProperty("App::PropertyBool", "invert", "Parameters", "Invert screw direction").invert = False
    obj.addProperty("App::PropertyXLinkSub", "baseObject", "Parameters", "Base object").baseObject = attachTo

  def updateProps(self, obj):
    if obj.getTypeIdOfProperty("baseObject") != "App::PropertyXLinkSub":
      linkedObj = obj.baseObject
      obj.removeProperty("baseObject")
      obj.addProperty("App::PropertyXLinkSub", "baseObject", "Parameters", "Base object").baseObject = linkedObj

    
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

DropButtonSupported = int(float(FreeCAD.Version()[1])) > 15 # and  int(FreeCAD.Version()[2].split()[0]) >= 5165
RadioButtonSupported = int(float(FreeCAD.Version()[1])) > 15 # and  int(FreeCAD.Version()[2].split()[0]) >= 5560   
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
        cmdlist.append((subcommand.replace(" ", ""), cmdsubs[subcommand], subcommand))
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
  if tb is None:
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
  
# removes all cached fasteners with real thread
def FSCacheRemoveThreaded():
  for key in list(FSCache.keys()):
    if key.endswith('|real'):
      FreeCAD.Console.PrintLog("Removing cached shape: " + key + "\n")
      del FSCache[key]

def MToFloat(m):
    m = m.lstrip('(')
    m = m.rstrip(')')
    return float(m.lstrip('M'))

def DiaStr2Num(DiaStr):
  DiaStr = DiaStr.strip("()")
  return FsData["DiaList"][DiaStr][0]

# inch tolerant version of length string to number converter
def LenStr2Num(DiaStr):
  # remove brackets indicating less common diameters
  StripStr = DiaStr.strip("()")
  # metric diameters of format 'Mxyz'
  if 'M' in StripStr:
    DiaFloat = float(StripStr.lstrip('M'))
  # inch diameters of format 'x y/z\"'
  elif 'in' in StripStr:
    components = StripStr.strip('in').split(' ')
    total = 0
    for item in components:
      if '/' in item:
        subcmpts = item.split('/')
        total += float(subcmpts[0])/float(subcmpts[1])
      else:
        total += float(item)
    DiaFloat = total*25.4
  # if there are no identifying unit chars, default to mm
  else:
    DiaFloat = float(StripStr)
  return DiaFloat
  
# sort compare function for m sizes
def MCompare(x, y):
  x1 = DiaStr2Num(x)
  y1 = DiaStr2Num(y)
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
  
def FSRemoveDigits(txt):
  res = ''
  for c in txt:
    if not c.isdigit():
      res += c
  return res

# get number of links to this object  
def GetNumLinks(obj):
  cnt = 0
  for parent in obj.InList:
    if parent.TypeId == 'App::Link':
      if parent.ElementCount > 0:
        cnt = cnt + parent.ElementCount
      else:
        cnt = cnt + 1
  return cnt

# get total count of a selected object taking arrays/links into account  
def GetTotalObjectRepeats(obj):
  cnt = 0
  for parent in obj.InList:
    numreps = 1
    if parent.TypeId != 'App::Link' and parent.TypeId != "App::LinkElement" and parent.TypeId != 'App::DocumentObjectGroup':
    #if parent.TypeId == 'Part::FeaturePython':
      if hasattr(parent,'ArrayType'):
        if parent.ArrayType == 'ortho':
            numreps = parent.NumberX * parent.NumberY * parent.NumberZ
        elif parent.ArrayType == 'polar':
            numreps = parent.NumberPolar
      #print (parent.Name + ", " + str(numreps) + ", " + str(GetTotalObjectRepeats(parent)) + ", " + str(GetNumLinks(parent)) + "\n")
      parentreps = GetTotalObjectRepeats(parent) 
      parentlinks = GetNumLinks(parent)
      #FreeCAD.Console.PrintLog("Parent:" + parent.Name + "/" + parent.TypeId + ", Reps:" + str(parentreps) + ", Links:" + str(parentlinks))
      cnt += numreps * (parentreps + parentlinks)
  if cnt == 0:
    cnt = 1
  return cnt


class FSFaceMaker:
  '''Create a face point by point on the x,z plane'''
  def __init__(self):
    self.edges = []
    self.firstPoint = None
    
  def AddPoint(self, x, z):
    curPoint = FreeCAD.Base.Vector(x,0,z)
    if (self.firstPoint is None):
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
          dia = DiaStr2Num(m) + 0.1
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
        if edgeName is None or edgeName in edgestable:
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


# common actions on fasteners:
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
    if selObj[0] is None:
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
        cobj.Shape = obj.Shape
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

# freecad 0.15 version:
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
    if self.toolbarItem is None:
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
        global FSMatchOuter
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
      name = FSRemoveDigits(obj.Name)
      #apply arrays
      cnt = GetTotalObjectRepeats(obj) * (1 + GetNumLinks(obj))
      #FreeCAD.Console.PrintLog("Using method: Add" + name + "\n")
      method = getattr(self, 'Add' + name, lambda x,y: "nothing")
      method(obj, cnt)
      #FreeCAD.Console.PrintLog('Add ' + str(cnt) + " " + obj.Name  + "\n")
    line = 2
    for fastener in sorted(self.fastenerDB.keys()):
      sheet.set('A' + str(line), fastener)
      sheet.set('B' + str(line), str(self.fastenerDB[fastener]))
      line += 1
    FreeCAD.ActiveDocument.recompute()
    return
    
  def AddFastener(self, fastener, cnt):
    if fastener in self.fastenerDB:
      self.fastenerDB[fastener] = self.fastenerDB[fastener] + cnt
    else:
      self.fastenerDB[fastener] = cnt
      
  def AddScrew(self, obj, cnt):
    len = obj.length
    if len == 'Custom':
      len = str(float(obj.lengthCustom)).rstrip("0").rstrip('.')
    self.AddFastener(obj.type + " Screw " + obj.diameter + "x" + len, cnt)
    
  def AddNut(self, obj, cnt):
    if hasattr(obj, 'type'):
      type = obj.type
    else:
      type = 'ISO4033'
    self.AddFastener(type + " Nut " + obj.diameter, cnt)

  def AddWasher(self, obj, cnt):
    self.AddFastener(obj.type + " Washer " + obj.diameter, cnt)
    
  def AddScrewTap(self, obj, cnt):
    self.AddFastener("ScrewTap " + obj.diameter + "x" + str(obj.length), cnt)
    
  def AddPressNut(self, obj, cnt):
    self.AddFastener("PEM PressNut " + obj.diameter + "-" + obj.tcode, cnt)
    
  def AddStandoff(self, obj, cnt):
    self.AddFastener("PEM Standoff " + obj.diameter + "x" + obj.length, cnt)
    
  def AddStud(self, obj, cnt):
    self.AddFastener("PEM Stud " + obj.diameter + "x" + obj.length, cnt)

  def AddPcbStandoff(self, obj, cnt):
    self.AddFastener("PCB Standoff " + obj.diameter + "x" + obj.width + "x" + obj.length, cnt)
    
    
  def IsActive(self):
    return Gui.ActiveDocument != None
        
        
Gui.addCommand('FSMakeBOM',FSMakeBomCommand())
FSCommands.append('FSMakeBOM', "command")

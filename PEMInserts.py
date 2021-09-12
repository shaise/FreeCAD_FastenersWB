# -*- coding: utf-8 -*-
###################################################################################
#
#  PEMInserts.py
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
import FreeCAD, FreeCADGui, Part, os, math
__dir__ = os.path.dirname(__file__)
iconPath = os.path.join( __dir__, 'Icons' )

import FastenerBase
from FastenerBase import FSBaseObject
import ScrewMaker  
screwMaker = ScrewMaker.Instance()

tan30 = math.tan(math.radians(30))
cos30 = math.cos(math.radians(30))

###################################################################################
# PEM Self Clinching nuts types: S/SS/CLS/CLSS/SP
CLSSizeCodes = ['00', '0', '1', '2']
CLSDiamCodes = ['Auto', 'M2', 'M2.5', 'M3', 'M3.5', 'M4', 'M5', 'M6', 'M8', 'M10', 'M12']
CLSPEMTable = {
#         (00,   0,    1,    2   )  C,     E,     T,    d
  'M2':  ((0,    0.77, 0.97, 1.38), 4.2,   6.35,  1.5,  1.6),
  'M2.5':((0,    0.77, 0.97, 1.38), 4.2,   6.35,  1.5,  2.05),
  'M3':  ((0,    0.77, 0.97, 1.38), 4.2,   6.35,  1.5,  2.5),
  'M3.5':((0,    0.77, 0.97, 1.38), 4.73,  7.11,  1.5,  2.9),
  'M4':  ((0,    0.77, 0.97, 1.38), 5.38,  7.87,  2.0,  3.3),
  'M5':  ((0,    0.77, 0.97, 1.38), 6.33,  8.64,  2.0,  4.2),
  'M6':  ((0.89, 1.15, 1.38, 2.21), 8.73,  11.18, 4.08, 5.0),
  'M8':  ((0,    0,    1.38, 2.21), 10.47, 12.7,  5.47, 6.8),
  'M10': ((0,    0,    2.21, 3.05), 13.97, 17.35, 7.48, 8.5),
  'M12': ((0,    0,    3.05, 0),    16.95, 20.57, 8.5,  10.2)
  }


def clMakeWire(do, di, a, c, e, t):
  do = do / 2
  di = di / 2
  ch1 = do - di
  ch2 = ch1 / 2
  if ch2 < 0.2:
    ch2 = 0.2
  c = c / 2
  e = e / 2
  c2 = (c + e) / 2
  sl = a / 20
  a2 = a / 2
  
  fm = FastenerBase.FSFaceMaker()
  fm.AddPoint(di, -a + ch1)
  fm.AddPoint(do, -a)
  fm.AddPoint(c, -a)
  fm.AddPoint(c, -a * 0.75,)
  fm.AddPoint(c - sl, -a2)
  fm.AddPoint(c2, -a2)
  fm.AddPoint(c2, 0)
  fm.AddPoint(e, 0)
  fm.AddPoint(e, t - ch2)
  fm.AddPoint(e - ch2, t)
  fm.AddPoint(do, t)
  fm.AddPoint(di, t - ch1) 
  return fm.GetFace()

def clMakePressNut(diam, code):
  if not (code in CLSSizeCodes):
    return None
  i = CLSSizeCodes.index(code)

  if not(diam in CLSPEMTable):
    return None
  
  (key, shape) = FastenerBase.FSGetKey('PressNut', diam, code)
  if shape != None:
    return shape

  ls, c, e, t, di = CLSPEMTable[diam]
  a = ls[i]
  if a == 0:
    return None
  do = FastenerBase.MToFloat(diam)
  f = clMakeWire(do, di, a, c, e, t)
  p = f.revolve(Base.Vector(0.0,0.0,0.0),Base.Vector(0.0,0.0,1.0),360)
  FastenerBase.FSCache[key] = p
  return p

def clFindClosest(diam, code):
  ''' Find closest standard screw to given parameters '''
  if not (code in CLSSizeCodes):
    return '1'
  i = CLSSizeCodes.index(code)
  lens = CLSPEMTable[diam][0]
  if lens[i] != 0:
    return code
  min = 999
  max = len(CLSSizeCodes)
  j = 0
  for c in lens:
    if c != 0 and min == 999:
      min = j
    if c == 0 and min != 999:
      max = j - 1
      break
    j = j + 1
  if i < min:
    return CLSSizeCodes[min]
  # i is probably > max
  return CLSSizeCodes[max]
      

# h = clMakePressNut('M5','1')

class FSPressNutObject(FSBaseObject):
  def __init__(self, obj, attachTo):
    '''"Add Press nut (self clinching) type fastener" '''
    FSBaseObject.__init__(self, obj, attachTo)
    self.itemText = "PressNut"
    #self.Proxy = obj.Name
    
    obj.addProperty("App::PropertyEnumeration","tcode","Parameters","Thickness code").tcode = CLSSizeCodes
    obj.addProperty("App::PropertyEnumeration","diameter","Parameters","Press nut thread diameter").diameter = CLSDiamCodes
    obj.invert = FastenerBase.FSLastInvert
    obj.tcode = '1'
    obj.Proxy = self
 
  def execute(self, fp):
    '''"Print a short message when doing a recomputation, this method is mandatory" '''
    
    try:
      baseobj = fp.baseObject[0]
      shape = baseobj.Shape.getElement(fp.baseObject[1][0])
    except:
      baseobj = None
      shape = None
    self.updateProps(fp)
    if (not (hasattr(self,'diameter')) or self.diameter != fp.diameter or self.tcode != fp.tcode):
      if fp.diameter == 'Auto':
        d = FastenerBase.FSAutoDiameterM(shape, CLSPEMTable, 1)
      else:
        d = fp.diameter
        
      l = clFindClosest(d, fp.tcode)
      if l != fp.tcode:
        fp.tcode = l
      if d != fp.diameter:
        fp.diameter = d
      s = clMakePressNut(d, l)
      self.diameter = fp.diameter
      self.tcode = fp.tcode
      FastenerBase.FSLastInvert = fp.invert
      fp.Label = fp.diameter + '-PressNut'
      fp.Shape = s
    else:
      FreeCAD.Console.PrintLog("Using cached object\n")
    if shape != None:
      #feature = FreeCAD.ActiveDocument.getObject(self.Proxy)
      #fp.Placement = FreeCAD.Placement() # reset placement
      FastenerBase.FSMoveToObject(fp, shape, fp.invert, fp.offset.Value)


FastenerBase.FSClassIcons[FSPressNutObject] = 'PEMPressNut.svg'    

class FSPressnutCommand:
  """Add Preass-nut command"""

  def GetResources(self):
    icon = os.path.join( iconPath , 'PEMPressNut.svg')
    return {'Pixmap'  : icon , # the name of a svg file available in the resources
            'MenuText': "Add Press-Nut" ,
            'ToolTip' : "Add PEM Self Clinching Metric Nut"}
 
  def Activated(self):
    FastenerBase.FSGenerateObjects(FSPressNutObject, "PressNut")
    return
   
  def IsActive(self):
    return Gui.ActiveDocument != None

Gui.addCommand("FSPressNut", FSPressnutCommand())
FastenerBase.FSCommands.append("FSPressNut", "screws", "PEM Inserts")


###################################################################################
# PEM Self Clinching standoffs types: SO/SOS/SOA/SO4
SOLengths = {'3':0, '4':0, '6':0, '8':0, '10':4, '12':4, '14':4, '16':8, '18':8, '20':8, '22':11, '25':11}
#BSLengths = {'6':3.2, '8':4, '10':4, '12':5, '14':6.5, '16':6.5, '18':9.5, '20':9.5, '22':9.5, '25':9.5}
SODiameters = ['Auto', 'M3', '3.5M3', 'M3.5', 'M4', 'M5' ]
SOPEMTable = {
#          B,    C,    H,   d, Lmin, Lmax
  'M3':   (3.2,  4.2,  4.8, 2.5, 3, 18),
  '3.5M3':(3.2,  5.39, 6.4, 2.5, 3, 25),
  'M3.5': (3.9,  5.39, 6.4, 2.9, 3, 25),
  'M4':   (4.8,  7.12, 7.9, 3.3, 3, 25),
  'M5':   (5.36, 7.12, 7.9, 4.2, 3, 25)
  }


def soMakeFace(b, c, h, d, l):
  h10 = h / 10.0
  c12 = c / 12.5
  c20 = c / 20.0
  c40 = c / 40.0
  b = b / 2
  c = c / 2
  d = d / 2
  ch1 = b - d
  l1 = float(l)
  l2 = l1 - SOLengths[l]
  c1 = c - c40
  c2 = c - c20
  l3 = h10 * 2 + (c12 + c20) * 2
  
  fm = FastenerBase.FSFaceMaker()
  fm.AddPoint(b, 0)
  fm.AddPoint(d, -ch1)
  fm.AddPoint(d, -(l2 - ch1))
  fm.AddPoint(b, -l2)
  if (l1 - l2) > 0.01:
    fm.AddPoint(b, -l1)
  fm.AddPoint(c, -l1)
  if (l3 < l1):
    fm.AddPoint(c, -l3)
    fm.AddPoint(c1, -l3)
    fm.AddPoint(c1, -(l3 - c20))
    fm.AddPoint(c, -(l3 - c20))
  fm.AddPoint(c, -(h10 * 2 + c12 + c20))
  fm.AddPoint(c1, -(h10 * 2 + c12 + c20))
  fm.AddPoint(c1, -(h10 * 2 + c12))
  fm.AddPoint(c, -(h10 * 2 + c12))
  fm.AddPoint(c, -h10 * 2)
  fm.AddPoint(c2, -h10 * 2)
  fm.AddPoint(c2, -h10)
  fm.AddPoint(h * 0.6, -h10)
  fm.AddPoint(h * 0.6, 0)
  return fm.GetFace()

def bsMakeFace(b, c, h, d, l):
  h10 = h / 10.0
  h102 = h10 + h10 / 2
  c12 = c / 12.5
  c20 = c / 20.0
  c40 = c / 40.0
  b = b / 2
  c = c / 2
  d = d / 2
  ch1 = b - d
  ch2 = d * tan30
  l1 = float(l)
  #l2 = l1 - SOLengths[l]
  c1 = c - c40
  c2 = c - c20
  l3 = h10 * 2 + (c12 + c20) * 2
  
  fm = FastenerBase.FSFaceMaker()
  fm.AddPoint(0, 0)
  fm.AddPoint(0, -h102)
  fm.AddPoint(d, -(h102 + ch2))
  fm.AddPoint(d, -(l1 - ch1))
  fm.AddPoint(b, -l1)
  fm.AddPoint(c, -l1)
  if (l3 < l1):
    fm.AddPoint(c, -l3)
    fm.AddPoint(c1, -l3)
    fm.AddPoint(c1, -(l3 - c20))
    fm.AddPoint(c, -(l3 - c20))
  fm.AddPoint(c, -(h10 * 2 + c12 + c20))
  fm.AddPoint(c1, -(h10 * 2 + c12 + c20))
  fm.AddPoint(c1, -(h10 * 2 + c12))
  fm.AddPoint(c, -(h10 * 2 + c12))
  fm.AddPoint(c, -h10 * 2)
  fm.AddPoint(c2, -h10 * 2)
  fm.AddPoint(c2, -h10)
  fm.AddPoint(h * 0.6, -h10)
  fm.AddPoint(h * 0.6, 0)
  return fm.GetFace()

def soMakeStandOff(diam, len, blind):
  if not(len in SOLengths):
    return None
  if not(diam in SOPEMTable):
    return None

  (key, shape) = FastenerBase.FSGetKey('StandOff', diam, len, blind)
  if shape != None:
    return shape
  
  l = int(len)
  b, c, h, d, lmin, lmax = SOPEMTable[diam]
  if blind:
    lmin, lmax = (6, 25)
  if l < lmin or l > lmax:
    return None
  
  if blind:
    f = bsMakeFace(b, c, h, d, len)
  else:
    f = soMakeFace(b, c, h, d, len)
  p = f.revolve(Base.Vector(0.0,0.0,0.0),Base.Vector(0.0,0.0,1.0),360)
  htool = screwMaker.makeHextool(h, 3, h * 2)
  htool.translate(Base.Vector(0.0,0.0,-2.0))
  shape = p.cut(htool)
  FastenerBase.FSCache[key] = shape
  return shape

def soFindClosest(diam, len):
  ''' Find closest standard screw to given parameters '''
  if not(diam in SOPEMTable):
    return None
  if (float(len) > SOPEMTable[diam][5]):
    return str(SOPEMTable[diam][5])
  if (float(len) < SOPEMTable[diam][4]):
    return str(SOPEMTable[diam][4])
  return len
 
def soGetAllLengths(diam, blind):
  if blind:
    lmin, lmax = (6, 25)
  else:
    b, c, h, d, lmin, lmax = SOPEMTable[diam]
  list = []
  for len in SOLengths:
    l = float(len)
    if l >= lmin and l <= lmax:
      list.append(len)
  try:  # py3
    import functools
    sorted(list, key = functools.cmp_to_key(FastenerBase.NumCompare))
  except:
    list.sort(cmp = FastenerBase.NumCompare)
  return list

# h = clMakePressNut('M5','1')

class FSStandOffObject(FSBaseObject):
  def __init__(self, obj, attachTo):
    '''"Add StandOff (self clinching) type fastener" '''
    FSBaseObject.__init__(self, obj, attachTo)
    self.itemText = "StandOff"
    #self.Proxy = obj.Name
    
    obj.addProperty("App::PropertyEnumeration","diameter","Parameters","Standoff thread diameter").diameter = SODiameters
    obj.addProperty("App::PropertyBool", "blind", "Parameters", "Blind Standoff type").blind = False
    obj.addProperty("App::PropertyEnumeration","length","Parameters","Standoff length").length = soGetAllLengths(SODiameters[1], False)
    obj.invert = FastenerBase.FSLastInvert
    obj.Proxy = self
 
  def execute(self, fp):
    '''"Print a short message when doing a recomputation, this method is mandatory" '''
    
    try:
      baseobj = fp.baseObject[0]
      shape = baseobj.Shape.getElement(fp.baseObject[1][0])
    except:
      baseobj = None
      shape = None
    self.updateProps(fp)
    if (not (hasattr(self,'diameter')) or self.diameter != fp.diameter or self.length != fp.length or self.blind != fp.blind):
      diameterchange = False      
      if not (hasattr(self,'diameter')) or self.diameter != fp.diameter:
        diameterchange = True      
      if fp.diameter == 'Auto':
        d = FastenerBase.FSAutoDiameterM(shape, SOPEMTable, 1)
        diameterchange = True      
      else:
        d = fp.diameter
        
      blindchange = False
      if not(hasattr(self,'blind')) or self.blind != fp.blind:
        blindchange = True;
        
      l = soFindClosest(d, fp.length)
      if d != fp.diameter:
        diameterchange = True      
        fp.diameter = d

      if l != fp.length or diameterchange or blindchange:
        if diameterchange or blindchange:
          fp.length = soGetAllLengths(fp.diameter, fp.blind)
        fp.length = l
               
      s = soMakeStandOff(d, l, fp.blind)
      self.diameter = fp.diameter
      self.length = fp.length
      self.blind = fp.blind
      FastenerBase.FSLastInvert = fp.invert
      fp.Label = fp.diameter + 'x' + fp.length + '-Standoff'
      fp.Shape = s
    else:
      FreeCAD.Console.PrintLog("Using cached object\n")
    if shape != None:
      #feature = FreeCAD.ActiveDocument.getObject(self.Proxy)
      #fp.Placement = FreeCAD.Placement() # reset placement
      FastenerBase.FSMoveToObject(fp, shape, fp.invert, fp.offset.Value)


FastenerBase.FSClassIcons[FSStandOffObject] = 'PEMTHStandoff.svg'    

class FSStandOffCommand:
  """Add Standoff command"""

  def GetResources(self):
    icon = os.path.join( iconPath , 'PEMTHStandoff.svg')
    return {'Pixmap'  : icon , # the name of a svg file available in the resources
            'MenuText': "Add Standoff" ,
            'ToolTip' : "Add PEM Self Clinching Metric Standoff"}
 
  def Activated(self):
    FastenerBase.FSGenerateObjects(FSStandOffObject, "Standoff")
    return
   
  def IsActive(self):
    return Gui.ActiveDocument != None

Gui.addCommand("FSStandOff", FSStandOffCommand())
FastenerBase.FSCommands.append("FSStandOff", "screws", "PEM Inserts")

###################################################################################
# PEM Self Clinching studs types: FH/FHS/FHA
FHLengths = ['6', '8', '10', '12', '15', '18', '20', '25', '30', '35']
#BSLengths = {'6':3.2, '8':4, '10':4, '12':5, '14':6.5, '16':6.5, '18':9.5, '20':9.5, '22':9.5, '25':9.5}
FHDiameters = ['Auto', 'M2.5', 'M3', 'M3.5', 'M4', 'M5', 'M6', 'M8' ]
FHPEMTable = {
#          H,    S,    d, Lmin, Lmax
  'M2.5': (4.1,  1.95, 2.05, 6,  18),
  'M3':   (4.6,  2.1,  2.5,  6,  25),
  'M3.5': (5.3,  2.25, 2.9,  6,  30),
  'M4':   (5.9,  2.4,  3.3,  6,  35),
  'M5':   (6.5,  2.7,  4.2,  8,  35),
  'M6':   (8.2,  3.0,  5.0,  10, 35),
  'M8':   (9.6,  3.7, 6.75, 12, 35)
  }

def fhMakeFace(m, h, d, l):
  h10 = h / 10.0
  h20 = h / 20.0
  m25 = m * 0.025
  hs = 0.8 + 0.125 * m
  he = 0.8 + 0.2 * m
  h = h / 2.0
  m = m / 2.0
  d = d / 2.0
  h85 = h * 0.85
  m9 = m * 0.9
  mr = m9 - m25 * (1.0 - cos30)
  ch1 = m - d
  
  fm = FastenerBase.FSFaceMaker()
  fm.AddPoint(0, 0)
  fm.AddPoint(h - h20, 0)
  fm.AddArc(h, - h20, h - h20, -h10)
  fm.AddPoint(h - h20, -(h10 + h20))
  fm.AddPoint(m , -(h10 + h20))
  fm.AddPoint(m , -hs)
  fm.AddPoint(m9, -(hs + m25))
  fm.AddArc(mr, -(hs + m25 * 1.5), m9, -(hs + m25 * 2))
  fm.AddPoint(m, -he)
  fm.AddPoint(m, -(l - ch1))
  fm.AddPoint(m - ch1, -l)
  fm.AddPoint(0, -l)
  return fm.GetFace()

def fhMakeStud(diam, len):
  if not(len in FHLengths):
    return None
  if not(diam in FHPEMTable):
    return None

  (key, shape) = FastenerBase.FSGetKey('Stud', diam, len)
  if shape != None:
    return shape
  
  l = int(len)
  m = FastenerBase.MToFloat(diam)
  h, s, d, lmin, lmax = FHPEMTable[diam]
  if l < lmin or l > lmax:
    return None
  
  f = fhMakeFace(m, h, d, l)
  p = f.revolve(Base.Vector(0.0,0.0,0.0),Base.Vector(0.0,0.0,1.0),360)
  FastenerBase.FSCache[key] = p
  return p

def fhFindClosest(diam, len):
  ''' Find closest standard screw to given parameters '''
  if not(diam in FHPEMTable):
    return None
  if (float(len) > FHPEMTable[diam][4]):
    return str(FHPEMTable[diam][4])
  if (float(len) < FHPEMTable[diam][3]):
    return str(FHPEMTable[diam][3])
  return len
 
def fhGetAllLengths(diam):
  h, s, d, lmin, lmax = FHPEMTable[diam]
  list = []
  for len in FHLengths:
    l = float(len)
    if l >= lmin and l <= lmax:
      list.append(len)
  try:  # py3
    import functools
    sorted(list, key = functools.cmp_to_key(FastenerBase.NumCompare))
  except:
    list.sort(cmp = FastenerBase.NumCompare)
  return list

  
class FSStudObject(FSBaseObject):
  def __init__(self, obj, attachTo):
    '''"Add Stud (self clinching) type fastener" '''
    FSBaseObject.__init__(self, obj, attachTo)
    self.itemText = "Stud"
    #self.Proxy = obj.Name
    
    obj.addProperty("App::PropertyEnumeration","diameter","Parameters","Standoff thread diameter").diameter = FHDiameters
    obj.addProperty("App::PropertyEnumeration","length","Parameters","Standoff length").length = fhGetAllLengths(FHDiameters[1])
    obj.invert = FastenerBase.FSLastInvert
    obj.Proxy = self
 
  def execute(self, fp):
    '''"Print a short message when doing a recomputation, this method is mandatory" '''
    
    try:
      baseobj = fp.baseObject[0]
      shape = baseobj.Shape.getElement(fp.baseObject[1][0])
    except:
      baseobj = None
      shape = None
    self.updateProps(fp)
    if (not (hasattr(self,'diameter')) or self.diameter != fp.diameter or self.length != fp.length):
      diameterchange = False      
      if not (hasattr(self,'diameter')) or self.diameter != fp.diameter:
        diameterchange = True      
      if fp.diameter == 'Auto':
        d = FastenerBase.FSAutoDiameterM(shape, FHPEMTable, -1)
        diameterchange = True      
      else:
        d = fp.diameter
        
      l = fhFindClosest(d, fp.length)
      if d != fp.diameter:
        diameterchange = True      
        fp.diameter = d

      if l != fp.length or diameterchange:
        if diameterchange:
          fp.length = fhGetAllLengths(fp.diameter)
        fp.length = l
               
      s = fhMakeStud(d, l)
      self.diameter = fp.diameter
      self.length = fp.length
      FastenerBase.FSLastInvert = fp.invert
      fp.Label = fp.diameter + 'x' + fp.length + '-Stud'
      fp.Shape = s
    else:
      FreeCAD.Console.PrintLog("Using cached object\n")
    if shape != None:
      #feature = FreeCAD.ActiveDocument.getObject(self.Proxy)
      #fp.Placement = FreeCAD.Placement() # reset placement
      FastenerBase.FSMoveToObject(fp, shape, fp.invert, fp.offset.Value)


FastenerBase.FSClassIcons[FSStudObject] = 'PEMStud.svg'    

class FSStudCommand:
  """Add Standoff command"""

  def GetResources(self):
    icon = os.path.join( iconPath , 'PEMStud.svg')
    return {'Pixmap'  : icon , # the name of a svg file available in the resources
            'MenuText': "Add Stud" ,
            'ToolTip' : "Add PEM Self Clinching Metric Stud"}
 
  def Activated(self):
    FastenerBase.FSGenerateObjects(FSStudObject, "Stud")
    return
   
  def IsActive(self):
    return Gui.ActiveDocument != None

Gui.addCommand("FSStud", FSStudCommand())
FastenerBase.FSCommands.append("FSStud", "screws", "PEM Inserts")

## add fastener types
FastenerBase.FSAddFastenerType("PressNut", False)
FastenerBase.FSAddItemsToType("PressNut", "PressNut")
FastenerBase.FSAddFastenerType("StandOff")
FastenerBase.FSAddItemsToType("StandOff", "StandOff")
FastenerBase.FSAddFastenerType("Stud")
FastenerBase.FSAddItemsToType("Stud", "Stud")

def FSPIGetAllDiameters(type):
  if type == "PressNut":
    diams = list(CLSDiamCodes)
  elif type == "StandOff":
    diams = list(SODiameters)
  elif type == "Stud":
    diams = list(FHDiameters)
  diams.pop(0)
  return diams
  
def FSPIGetAllLengths(type, diam):
  #if type == "PressNut":
  #  return []
  if type == "StandOff":
    return soGetAllLengths(diam, False)
  elif type == "Stud":
    return fhGetAllLengths(diam)
  return []


###################################################################################
# PCB standoffs / Wurth standard WA-SSTIE 
PSLengths = {
  'M2.5x5' : ('5', '6', '7', '8', '9', '10', '12', '15', '17', '18', '20', '25', '30'),
  'M3x5'   : ('10', '15', '20', '25'),
  'M3x5.5' : ('5', '6', '7', '8', '9', '10', '11', '12', '13', '14', '15', '16', '17', '18', '19', '20', '22', '23', '25', '27', '28', '30', '35', '40', '45', '50', '55', '60'),
  'M3x6'   : ('8', '10', '12', '15', '20', '25', '30', '35', '40'),
  'M4x7'   : ('5', '6', '8', '10', '12', '15', '20', '25', '30', '35', '40'),
  'M5x8'   : ('8', '10', '15', '20', '25', '30', '40', '50', '60', '70'),
  'M6x10'  : ('15', '20', '25', '30', '35', '40', '45', '50', '60')
}
PSDiameters = ['Auto', 'M2.5', 'M3', 'M4', 'M5', 'M6' ]
PSMTable = {
#          Tlo, id,   SW(s)
  'M2.5': (6,   2.05, ('5',)),
  'M3':   (6,   2.5,  ('5', '5.5', '6')),
  'M4':   (8,   3.3,  ('7',)),
  'M5':   (10,  4.2,  ('8',)),
  'M6':   (10,  5,    ('10',))
  }


def psMakeFace(m, sw, lo, l, id):
  l = float(l)
  id2 = id / 2.0
  sw2 = float(sw) / 2.0
  m2 = m / 2.0
  d2 = 0.95 * sw2 / cos30
  l1 = l - (d2 - sw2) / 2.0
  dd = m2 - id2
  lo1 = -0.6
  lo2 = lo1 - dd
  lo3 = dd - lo
  p = l - 10
  if (p < 1):
    p = 1
  p1 = p + id2

  fm = FastenerBase.FSFaceMaker()
  fm.AddPoint(0, p)
  fm.AddPoint(id2, p1)
  fm.AddPoint(id2, l - dd)
  fm.AddPoint(id2 + dd, l)
  fm.AddPoint(sw2, l)
  fm.AddPoint(d2, l1)
  fm.AddPoint(d2, 0)
  fm.AddPoint(id2, 0)
  fm.AddPoint(id2, lo1)
  fm.AddPoint(m2, lo2)
  fm.AddPoint(m2, lo3)
  fm.AddPoint(id2, -lo)
  fm.AddPoint(0, -lo)
  return fm.GetFace()

def psMakeStandOff(diam, len, width, screwlen):
  FreeCAD.Console.PrintLog("Making PCB standof" + diam + "x" + len + "x" + width + "x" + str(screwlen) + "\n")
  if not(diam in PSMTable):
    return None
  lenKey = diam + "x" + width
  if not(lenKey in PSLengths):
    return None

  (key, shape) = FastenerBase.FSGetKey('PcbStandOff', diam, width, len, screwlen)
  if shape != None:
    return shape
  
  tlo, id, sw = PSMTable[diam]

  m = FastenerBase.MToFloat(diam)
  f = psMakeFace(m, width, screwlen, len, id)
  p = f.revolve(Base.Vector(0.0,0.0,0.0),Base.Vector(0.0,0.0,1.0),360)
  w = float(width)
  l = float(len)
  htool = screwMaker.makeHextool(w, l + screwlen, w * 2)
  htool.translate(Base.Vector(0.0,0.0,-screwlen - 0.1))
  shape = p.cut(htool)
  FastenerBase.FSCache[key] = shape
  return shape

def psFindClosest(mtable, ltable, diam, width, len):
  ''' Find closest standard standoff to given parameters '''
  if not(diam in mtable):
    return None
  lenKey = diam + "x" + width
  if not(lenKey in ltable):
    return None
  lens = ltable[lenKey]
  for l in lens:
    if (float(len) <= float(l)):
      return l
  return lens[len(lens) - 1]

def psGetAllWidths(mtable, diam):
  if not(diam in mtable):
    return None
  list = mtable[diam][2]
  try:  # py3
    import functools
    sorted(list, key = functools.cmp_to_key(FastenerBase.NumCompare))
  except:
    list.sort(cmp = FastenerBase.NumCompare)
  return list

 
def psGetAllLengths(mtable, ltable, diam, width):
  if not(diam in mtable):
    return None
  if not (width in mtable[diam][2]):
    width = mtable[diam][2][0]
  lenKey = diam + "x" + width
  if not(lenKey in ltable):
    return None
  list = []
  for len in ltable[lenKey]:
    list.append(len)
  try:  # py3
    import functools
    sorted(list, key = functools.cmp_to_key(FastenerBase.NumCompare))
  except:
    list.sort(cmp = FastenerBase.NumCompare)
  list.append("Custom")
  return list

# h = clMakePressNut('M5','1')

class FSPcbStandOffObject(FSBaseObject):
  def __init__(self, obj, attachTo):
    '''"Add PCB StandOff type fastener" '''
    FSBaseObject.__init__(self, obj, attachTo)
    self.itemText = "PcbStandOff"
    #self.Proxy = obj.Name
    
    obj.addProperty("App::PropertyEnumeration","diameter","Parameters","Standoff thread diameter").diameter = PSDiameters
    widths = psGetAllWidths(PSMTable ,PSDiameters[1])
    obj.addProperty("App::PropertyEnumeration", "width", "Parameters", "Standoff body width").width = widths
    self.VerifyMissingAttrs(obj, PSDiameters[1], widths[0])
    #obj.addProperty("App::PropertyEnumeration","length","Parameters","Standoff length").length = psGetAllLengths(PSMTable, PSLengths ,PSDiameters[1], widths[0])
    obj.invert = FastenerBase.FSLastInvert
    obj.Proxy = self

  def VerifyMissingAttrs(self, obj, diam, width):
    self.updateProps(obj)
    if (not hasattr(obj, 'lengthCustom')):
      slens = psGetAllLengths(PSMTable, PSLengths ,diam, width)
      if (hasattr(obj, 'length')):
        origLen = obj.length
        obj.length = slens
        if not (origLen in slens):
          obj.length = slens[0]
        else:
          obj.length = origLen
      else:
        obj.addProperty("App::PropertyEnumeration","length","Parameters","Standoff length").length = slens
      obj.addProperty("App::PropertyLength","lengthCustom","Parameters","Custom length").lengthCustom = slens[0]
    if (not hasattr(obj, 'screwLength')):
      obj.addProperty("App::PropertyLength","screwLength","Parameters","Thread length").screwLength = PSMTable[diam][0]

  def ActiveLength(self, obj):
    if not hasattr(obj,'length'):
      return '0'
    if obj.length == 'Custom':
      return str(float(obj.lengthCustom)).rstrip("0").rstrip('.')
    return obj.length

  def execute(self, fp):
    '''"Print a short message when doing a recomputation, this method is mandatory" '''
    
    try:
      baseobj = fp.baseObject[0]
      shape = baseobj.Shape.getElement(fp.baseObject[1][0])
    except:
      baseobj = None
      shape = None
  
    # for backward compatibility: add missing attribute if needed
    self.VerifyMissingAttrs(fp, fp.diameter, fp.width)
 
    diameterchange = not (hasattr(self,'diameter')) or self.diameter != fp.diameter
    widthchange = not(hasattr(self,'width')) or self.width != fp.width
    lengthchange = not(hasattr(self,'length')) or self.length != fp.length
    cutstlenchange = not(hasattr(self,'lengthCustom')) or self.lengthCustom != fp.lengthCustom
    screwlenchange = not(hasattr(self,'screwLength')) or self.screwLength != fp.screwLength
    if (diameterchange or widthchange or lengthchange or cutstlenchange or screwlenchange):
      if fp.diameter == 'Auto':
        d = FastenerBase.FSAutoDiameterM(shape, PSMTable, 1)
        diameterchange = True      
      else:
        d = fp.diameter

      if d != fp.diameter:
        diameterchange = True      
        fp.diameter = d

      if widthchange or diameterchange:
        widthchange = True
        if diameterchange:
          allwidth = psGetAllWidths(PSMTable, d)
          fp.width = allwidth
          if (len(allwidth) > 1):
            fp.width = allwidth[1]
          else:
            fp.width = allwidth[0]

      if (not lengthchange and hasattr(self,'lengthCustom') and self.lengthCustom != fp.lengthCustom.Value):
        fp.length = 'Custom'

      if fp.length == 'Custom':
        l = str(float(fp.lengthCustom)).rstrip("0").rstrip('.')
      else:
        l = psFindClosest(PSMTable, PSLengths ,d, fp.width, fp.length)

        if l != fp.length or diameterchange or widthchange:
          if diameterchange or widthchange:
            fp.length = psGetAllLengths(PSMTable, PSLengths ,fp.diameter, fp.width)
          fp.length = l
        fp.lengthCustom = l
        
      if diameterchange:
        fp.screwLength = PSMTable[fp.diameter][0]
      elif fp.screwLength < 2:
        fp.screwLength = 2

      s = psMakeStandOff(d, l, fp.width, float(fp.screwLength))
        
      self.diameter = fp.diameter
      self.length = fp.length
      self.width = fp.width
      self.lengthCustom = fp.lengthCustom.Value
      self.screwLength = fp.screwLength.Value
      FastenerBase.FSLastInvert = fp.invert
      fp.Label = fp.diameter + 'x' + fp.width + 'x' + l + '-Standoff'
      fp.Shape = s
    else:
      FreeCAD.Console.PrintLog("Using cached object\n")
    if shape != None:
      #feature = FreeCAD.ActiveDocument.getObject(self.Proxy)
      #fp.Placement = FreeCAD.Placement() # reset placement
      FastenerBase.FSMoveToObject(fp, shape, fp.invert, fp.offset.Value)


FastenerBase.FSClassIcons[FSPcbStandOffObject] = 'PCBStandoff.svg'    

class FSPcbStandOffCommand:
  """Add PCB Standoff command"""

  def GetResources(self):
    icon = os.path.join( iconPath , 'PCBStandoff.svg')
    return {'Pixmap'  : icon , # the name of a svg file available in the resources
            'MenuText': "Add PCB Standoff" ,
            'ToolTip' : "Add PCB Metric Standoff"}
 
  def Activated(self):
    FastenerBase.FSGenerateObjects(FSPcbStandOffObject, "PcbStandoff")
    return
   
  def IsActive(self):
    return Gui.ActiveDocument != None

Gui.addCommand("FSPcbStandOff", FSPcbStandOffCommand())
FastenerBase.FSCommands.append("FSPcbStandOff", "screws", "PEM Inserts")

###################################################################################
# PCB Spacers / Wurth standard WA-SSTII 
PSPLengths = {
  'M2.5x5' : ('5', '10', '11', '12', '15', '17', '18', '20', '22'),
  'M3x5'   : ('5', '10', '15', '20'),
  'M3x5.5' : ('5', '6', '7', '8', '9', '10', '11', '12', '13', '14', '15', '16', '17', '18', '19', '20', '21', '22', '23', '25', '27', '30', '35', '40'),
  'M4x7'   : ('5', '8', '10', '12', '15', '20', '25', '30', '35', '40', '45', '50', '60', '70', '80'),
  'M5x8'   : ('10', '12', '15', '20', '25', '30', '35', '40', '50'),
  'M6x10'  : ('10', '15', '20', '25', '30', '35', '40', '45', '50', '60')
}
PSPDiameters = ['Auto', 'M2.5', 'M3', 'M4', 'M5', 'M6' ]
PSPMTable = {
#          Th,   id,   SW(s)
  'M2.5': (18,   2.05, ('5',)),
  'M3':   (20,   2.5,  ('5', '5.5')),
  'M4':   (20,   3.3,  ('7',)),
  'M5':   (20,   4.2,  ('8',)),
  'M6':   (20,   5,    ('10',))
  }


def pspMakeFace(m, sw, l, id, th):
  l = float(l)
  id2 = id / 2.0
  sw2 = float(sw) / 2.0
  m2 = m / 2.0
  d2 = 0.95 * sw2 / cos30
  l1 = l - (d2 - sw2) / 2.0
  dd = m2 - id2
  p = 10
  if (p + 0.5 > l / 2.0):
    p = l / 2.0 - 0.5
  p1 = p - id2
 
  fm = FastenerBase.FSFaceMaker()
  fm.AddPoint(id2, l - dd)
  fm.AddPoint(id2 + dd, l)
  fm.AddPoint(sw2, l)
  fm.AddPoint(d2, l1)
  fm.AddPoint(d2, dd)
  fm.AddPoint(sw2, 0)
  fm.AddPoint(id2 + dd, 0)
  fm.AddPoint(id2, dd)
  if (l > th):
    # separate holes
    fm.AddPoint(id2, p1)
    fm.AddPoint(0, p)
    fm.AddPoint(0, l - p)
    fm.AddPoint(id2, l - p1)
  return fm.GetFace()

def pspMakeSpacer(diam, len, width):
  FreeCAD.Console.PrintLog("Making PCB spacer" + diam + "x" + len + "x" + width + "\n")
  if not(diam in PSPMTable):
    return None
  lenKey = diam + "x" + width
  if not(lenKey in PSPLengths):
    return None

  (key, shape) = FastenerBase.FSGetKey('PcbSpacer', diam, width, len)
  if shape != None:
    return shape
  
  th, id, sw = PSPMTable[diam]

  m = FastenerBase.MToFloat(diam)
  f = pspMakeFace(m, width, len, id, th)
  p = f.revolve(Base.Vector(0.0,0.0,0.0),Base.Vector(0.0,0.0,1.0),360)
  w = float(width)
  l = float(len)
  htool = screwMaker.makeHextool(w, l, w * 2)
  htool.translate(Base.Vector(0.0,0.0,- 0.1))
  shape = p.cut(htool)
  FastenerBase.FSCache[key] = shape
  return shape

# h = clMakePressNut('M5','1')

class FSPcbSpacerObject(FSBaseObject):
  def __init__(self, obj, attachTo):
    '''"Add PCB Spacer type fastener" '''
    FSBaseObject.__init__(self, obj, attachTo)
    self.itemText = "PcbSpacer"
    #self.Proxy = obj.Name
    
    obj.addProperty("App::PropertyEnumeration","diameter","Parameters","Standoff thread diameter").diameter = PSDiameters
    widths = psGetAllWidths(PSPMTable ,PSDiameters[1])
    obj.addProperty("App::PropertyEnumeration", "width", "Parameters", "Standoff body width").width = widths
    obj.addProperty("App::PropertyEnumeration","length","Parameters","Standoff length").length = psGetAllLengths(PSPMTable, PSPLengths ,PSDiameters[1], widths[0])
    obj.invert = FastenerBase.FSLastInvert
    obj.Proxy = self
 
  def execute(self, fp):
    '''"Print a short message when doing a recomputation, this method is mandatory" '''
    try:
      baseobj = fp.baseObject[0]
      shape = baseobj.Shape.getElement(fp.baseObject[1][0])
    except:
      baseobj = None
      shape = None
    self.updateProps(fp)
    if (not (hasattr(self,'diameter')) or self.diameter != fp.diameter or self.width != fp.width or self.length != fp.length):
      diameterchange = False      
      if not (hasattr(self,'diameter')) or self.diameter != fp.diameter:
        diameterchange = True      
      if fp.diameter == 'Auto':
        d = FastenerBase.FSAutoDiameterM(shape, PSMTable, 1)
        diameterchange = True      
      else:
        d = fp.diameter

      if d != fp.diameter:
        diameterchange = True      
        fp.diameter = d

      widthchange = False
      if diameterchange or not(hasattr(self,'width')) or self.width != fp.width:
        widthchange = True
        if diameterchange:
          allwidth = psGetAllWidths(PSPMTable, d)
          fp.width = allwidth
          if (len(allwidth) > 1):
            fp.width = allwidth[1]
          else:
            fp.width = allwidth[0]

      l = psFindClosest(PSPMTable, PSPLengths ,d, fp.width, fp.length)

      if l != fp.length or diameterchange or widthchange:
        if diameterchange or widthchange:
          fp.length = psGetAllLengths(PSPMTable, PSPLengths, fp.diameter, fp.width)
        fp.length = l

      s = pspMakeSpacer(d, l, fp.width)
        
      self.diameter = fp.diameter
      self.length = fp.length
      self.width = fp.width
      FastenerBase.FSLastInvert = fp.invert
      fp.Label = fp.diameter + 'x' + fp.width + 'x' + fp.length + '-Spacer'
      fp.Shape = s
    else:
      FreeCAD.Console.PrintLog("Using cached object\n")
    if shape != None:
      #feature = FreeCAD.ActiveDocument.getObject(self.Proxy)
      #fp.Placement = FreeCAD.Placement() # reset placement
      FastenerBase.FSMoveToObject(fp, shape, fp.invert, fp.offset.Value)


FastenerBase.FSClassIcons[FSPcbSpacerObject] = 'PCBSpacer.svg'    

class FSPcbSpacerCommand:
  """Add PCB Spacer command"""

  def GetResources(self):
    icon = os.path.join( iconPath , 'PCBSpacer.svg')
    return {'Pixmap'  : icon , # the name of a svg file available in the resources
            'MenuText': "Add PCB Spacer" ,
            'ToolTip' : "Add PCB Metric Spacer"}
 
  def Activated(self):
    FastenerBase.FSGenerateObjects(FSPcbSpacerObject, "PcbSpacer")
    return
   
  def IsActive(self):
    return Gui.ActiveDocument != None

Gui.addCommand("FSPcbSpacer", FSPcbSpacerCommand())
FastenerBase.FSCommands.append("FSPcbSpacer", "screws", "PEM Inserts")


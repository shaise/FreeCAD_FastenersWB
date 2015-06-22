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
from FreeCAD import Base
import FreeCAD, FreeCADGui, Part, os
__dir__ = os.path.dirname(__file__)
iconPath = os.path.join( __dir__, 'Icons' )

import FastenerBase
from FastenerBase import FSBaseObject
import ScrewMaker  
screwMaker = ScrewMaker.Instance()


# PEM Self Clinching nuts types: S/SS/CLS/CLSS/SP
CLSSizeCodes = ['00', '0', '1', '2']
CLSDiamCodes = ['Auto', 'M2', 'M2.5', 'M3', 'M3.5', 'M4', 'M5', 'M6', 'M8', 'M10', 'M12']
CLSPEMTable = {
#         (00,   0,    1,    2   )  C,     E,     T,    d
  'M2':  ((0,    0.77, 0.97, 1.38), 4.2,   6.35,  1.5,  1.6),
  'M2.5':((0,    0.77, 0.97, 1.38), 4.2,   6.35,  1.5,  2.05),
  'M3':  ((0,    0.77, 0.97, 1.38), 4.2,   6.35,  1.5,  2.5),
  'M3.5':((0,    0.77, 0.97, 1.38), 4.73,  7.11,  1.5,  2.9),
  'M4':  ((0,    0.77, 0.97, 1.38), 5.38,  7.87,  2,    3.3),
  'M5':  ((0,    0.77, 0.97, 1.38), 6.33,  8.64,  2,    4.2),
  'M6':  ((0.89, 1.15, 1.38, 2.21), 8.73,  11.18, 4.08, 5),
  'M8':  ((0,    0,    1.38, 2.21), 10.47, 12.7,  5.47, 6.8),
  'M10': ((0,    0,    2.21, 3.05), 13.97, 17.35, 7.48, 8.5),
  'M12': ((0,    0,    3.05, 0),    16.95, 20.57, 8.5,  10.2)
  }

# 2D lines on the X, Z Plane
def clMakeLine2D(x1, z1, x2, z2):
  return Part.makeLine(FreeCAD.Base.Vector(x1,0,z1),FreeCAD.Base.Vector(x2,0,z2))


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
  e1 = clMakeLine2D(di, -a + ch1, do, -a)
  e2 = clMakeLine2D(do, -a, c, -a)
  e3 = clMakeLine2D(c, -a, c, -a * 0.75)
  e4 = clMakeLine2D(c, -a * 0.75, c - sl, -a2)
  e5 = clMakeLine2D(c - sl, -a2, c2, -a2)
  e6 = clMakeLine2D(c2, -a2, c2, 0)
  e7 = clMakeLine2D(c2, 0, e, 0)
  e8 = clMakeLine2D(e, 0, e, t - ch2)
  e9 = clMakeLine2D(e, t - ch2, e - ch2, t)
  e10 = clMakeLine2D(e - ch2, t, do, t)
  e11 = clMakeLine2D(do, t, di, t - ch1)
  e12 = clMakeLine2D(di, t - ch1, di, -a + ch1) 
  w = Part.Wire([e1,e2,e3,e4,e5,e6,e7,e8,e9,e10,e11,e12])
  return Part.Face(w)

def clMakePressNut(diam, code):
  if not (code in CLSSizeCodes):
    return None
  i = CLSSizeCodes.index(code)

  if not(diam in CLSPEMTable):
    return None
  
  ls, c, e, t, di = CLSPEMTable[diam]
  a = ls[i]
  if a == 0:
    return None
  do = float(diam.lstrip('M'))
  f = clMakeWire(do, di, a, c, e, t)
  p = f.revolve(Base.Vector(0.0,0.0,0.0),Base.Vector(0.0,0.0,1.0),360)
  return p
  
def clAutoDiameter(holeObj):
  res = 'M5'
  if holeObj != None and hasattr(holeObj, 'Curve') and hasattr(holeObj.Curve, 'Radius'):
    d = holeObj.Curve.Radius * 2
    mindif = 10.0
    for m in CLSPEMTable:
        dia = CLSPEMTable[m][1] + 0.1
        if (dia > d):
          dif = dia - d
          if dif < mindif:
            mindif = dif
            res = m
  return res

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
   
    if (not (hasattr(self,'diameter')) or self.diameter != fp.diameter or self.tcode != fp.tcode):
      if fp.diameter == 'Auto':
        d = clAutoDiameter(shape)
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
      fp.Shape = s
    else:
      FreeCAD.Console.PrintLog("Using cached object\n")
    if shape != None:
      #feature = FreeCAD.ActiveDocument.getObject(self.Proxy)
      fp.Placement = FreeCAD.Placement() # reset placement
      screwMaker.moveScrewToObject(fp, shape, fp.invert, fp.offset.Value)

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
    if isinstance(self.Object.Proxy,FSPressNutObject):
      return os.path.join( iconPath , 'PEMPressNut.svg')
    return None

    

class FSPressnutCommand:
  """Add Preass-nut command"""

  def GetResources(self):
    icon = os.path.join( iconPath , 'PEMPressNut.svg')
    return {'Pixmap'  : icon , # the name of a svg file available in the resources
            'MenuText': "Add Press-Nut" ,
            'ToolTip' : "Add PEM Self Clinching Metric Nut"}
 
  def Activated(self):
    baseObjectNames = [ None ]
    obj = None
    selObjects = Gui.Selection.getSelectionEx()
    if len(selObjects) > 0:
      baseObjectNames = selObjects[0].SubElementNames
      obj = selObjects[0].Object
    for baseObjectName in baseObjectNames:      
      a=FreeCAD.ActiveDocument.addObject("Part::FeaturePython","PressNut")
      if baseObjectName == None:
        baseObject = None
      else:
        baseObject = (obj, [baseObjectName])
      FSPressNutObject(a, baseObject)
      FSViewProviderIcon(a.ViewObject)
    FreeCAD.ActiveDocument.recompute()
    return
   
  def IsActive(self):
    return True

Gui.addCommand("FSPressNut", FSPressnutCommand())
FastenerBase.FSCommands.append("FSPressNut")

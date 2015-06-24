# -*- coding: utf-8 -*-
###################################################################################
#
#  FSNuts.py
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


###################################################################################
# Standard Metric Hex nuts 
NutDiamCodes = ['Auto', 'M1.6', 'M2', 'M2.5', 'M3', 'M3.5', 'M4', 'M5', 'M6', 'M8', 'M10', 'M12', 'M14', 'M16', 'M20', 'M24', 'M30', 'M36']
MHexNutTable = {
#         S,    M,    d
  'M1.6':(3.2,  1.3,  1.25),
  'M2':  (4.0,  1.6,  1.6),
  'M2.5':(5.0,  2.0,  2.05),
  'M3':  (5.5,  2.4,  2.5),
  'M3.5':(6.0,  2.8,  2.9),
  'M4':  (7.0,  3.2,  3.3),
  'M5':  (8.0,  4.7,  4.2),
  'M6':  (10.0, 5.2,  5.0),
  'M8':  (13.0, 6.8,  6.8),
  'M10': (16.0, 8.4,  8.5),
  'M12': (18.0, 10.8, 10.2),
  'M14': (21.0, 12.8, 12.0),
  'M16': (24.0, 14.8, 14.0),
  'M20': (30.0, 18.0, 15.0),
  'M24': (36.0, 21.5, 21.0),
  'M30': (46.0, 25.6, 26.5),
  'M36': (55.0, 31.0, 32.0)
  }

# 2D lines on the X, Z Plane
def nutMakeLine2D(x1, z1, x2, z2):
  return Part.makeLine(FreeCAD.Base.Vector(x1,0,z1),FreeCAD.Base.Vector(x2,0,z2))

cos15 = math.cos(math.radians(15.0))
cos30 = math.cos(math.radians(30.0))

def nutMakeFace(do, di, s, m):
  do = do / 2
  di = di / 2
  s = s / 2.01
  e = s * 1.02 / cos30
  ch1 = do - di
  ch2 = (e - s) / cos15
  fm = FastenerBase.FSFaceMaker()
  fm.AddPoint(di, ch1)
  fm.AddPoint(do, 0)
  fm.AddPoint(s, 0)
  fm.AddPoint(e, ch2)
  fm.AddPoint(e, m - ch2)
  fm.AddPoint(s, m)
  fm.AddPoint(do, m)
  fm.AddPoint(di, m - ch1)
  return fm.GetFace()

def nutMakeSolid(diam):
  if not(diam in MHexNutTable):
    return None
  
  s, m, di = MHexNutTable[diam]
  do = float(diam.lstrip('M'))
  f = nutMakeFace(do, di, s, m)
  p = f.revolve(Base.Vector(0.0,0.0,0.0),Base.Vector(0.0,0.0,1.0),360)
  htool = screwMaker.makeHextool(s, m, s * 2)
  return p.cut(htool)
  
# h = clMakePressNut('M5','1')

class FSHexNutObject(FSBaseObject):
  def __init__(self, obj, attachTo):
    '''"Add Metric Hex nut" '''
    FSBaseObject.__init__(self, obj, attachTo)
    self.itemText = "Nut"
    
    obj.addProperty("App::PropertyEnumeration","diameter","Parameters","Press nut thread diameter").diameter = NutDiamCodes
    obj.Proxy = self
 
  def execute(self, fp):
    '''"perform object creation" '''
    
    try:
      baseobj = fp.baseObject[0]
      shape = baseobj.Shape.getElement(fp.baseObject[1][0])
    except:
      baseobj = None
      shape = None
   
    if (not (hasattr(self,'diameter')) or self.diameter != fp.diameter):
      if fp.diameter == 'Auto':
        d = FastenerBase.FSAutoDiameterM(shape, MHexNutTable, -1)
      else:
        d = fp.diameter
        
      if d != fp.diameter:
        fp.diameter = d
      s = nutMakeSolid(d)
      self.diameter = fp.diameter
      fp.Shape = s
    else:
      FreeCAD.Console.PrintLog("Using cached object\n")
    if shape != None:
      fp.Placement = FreeCAD.Placement() # reset placement
      screwMaker.moveScrewToObject(fp, shape, fp.invert, fp.offset.Value)

FastenerBase.FSClassIcons[FSHexNutObject] = 'HexNut.svg'    

class FSHexNutCommand:
  """Add Preass-nut command"""

  def GetResources(self):
    icon = os.path.join( iconPath , 'HexNut.svg')
    return {'Pixmap'  : icon , # the name of a svg file available in the resources
            'MenuText': "Add Hex Nut" ,
            'ToolTip' : "Add Metric Hexagon Nut - ISO 4032"}
 
  def Activated(self):
    FastenerBase.FSGenerateObjects(FSHexNutObject, "Nut")
    return
   
  def IsActive(self):
    return True

Gui.addCommand("FSHexNut", FSHexNutCommand())
FastenerBase.FSCommands.append("FSHexNut")

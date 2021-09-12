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


# NOTE!! this command is left for backward compatibility, Screw_Maker.py nuts are now used.


from FreeCAD import Gui
from FreeCAD import Base
import FreeCAD, FreeCADGui, Part, os, math
__dir__ = os.path.dirname(__file__)
iconPath = os.path.join( __dir__, 'Icons' )

import FastenerBase
from FastenerBase import FSBaseObject
import ScrewMaker  
#screwMaker = ScrewMaker.Instance()


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
tan15 = math.tan(math.radians(15.0))
tan30 = math.tan(math.radians(30.0))

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
  (key, shape) = FastenerBase.FSGetKey('Nut', diam)
  if shape != None:
    return shape
  
  s, m, di = MHexNutTable[diam]
  do = FastenerBase.MToFloat(diam)
  f = nutMakeFace(do, di, s, m)
  p = f.revolve(Base.Vector(0.0,0.0,0.0),Base.Vector(0.0,0.0,1.0),360)
  screwMaker = ScrewMaker.Instance()
  htool = screwMaker.makeHextool(s, m, s * 2)
  shape = p.cut(htool)
  FastenerBase.FSCache[key] = shape
  return shape
  
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
    self.updateProps(obj)
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
      fp.Label = fp.diameter + '-Nut'
    else:
      FreeCAD.Console.PrintLog("Using cached object\n")
    if shape != None:
      #fp.Placement = FreeCAD.Placement() # reset placement
      FastenerBase.FSMoveToObject(fp, shape, fp.invert, fp.offset.Value)

FastenerBase.FSClassIcons[FSHexNutObject] = 'HexNut.svg'    

class FSHexNutCommand:
  """Add Preass-nut command"""

  def GetResources(self):
    icon = os.path.join( iconPath , 'HexNut.svg')
    return {'Pixmap'  : icon , # the name of a svg file available in the resources
            'MenuText': "Add Hex Nut" ,
            'ToolTip' : "Add Metric Hexagon Nut - ISO 4032, Style 3"}
 
  def Activated(self):
    FastenerBase.FSGenerateObjects(FSHexNutObject, "Nut")
    return
   
  def IsActive(self):
    return Gui.ActiveDocument != None

Gui.addCommand("FSHexNut", FSHexNutCommand())
#FastenerBase.FSCommands.append("FSHexNut", "screws", "Nut")

###################################################################################
# Square Metric Hex nuts DIN562
din562def = {
#         s,    m,    d
  'M1.6':(3.2,  1,    1.25),
  'M2':  (4.0,  1.2,  1.6),
  'M2.5':(5.0,  1.6,  2.05),
  'M3':  (5.5,  1.8,  2.5),
  'M4':  (7.0,  2.2,  3.3),
  'M5':  (8.0,  2.7,  4.2),
  'M6':  (10.0, 3.2,  5.0),
  'M8':  (13.0, 4,    6.8),
  'M10': (17.0, 5,    8.5)
}

def makeSquareTool(s, m):
  # makes a cylinder with an inner square hole, used as cutting tool
  # create square face
  msq = Base.Matrix()
  msq.rotateZ(math.radians(90.0))
  polygon = []
  vsq = Base.Vector(s / 2.0, s / 2.0, -m * 0.1)
  for i in range(4):
     polygon.append(vsq)
     vsq = msq.multiply(vsq)
  polygon.append(vsq)
  square = Part.makePolygon(polygon)
  square = Part.Face(square)

  # create circle face
  circ = Part.makeCircle(s * 3.0, Base.Vector(0.0, 0.0, -m * 0.1))
  circ = Part.Face(Part.Wire(circ))

  # Create the face with the circle as outline and the square as hole
  face=circ.cut(square)
 
  # Extrude in z to create the final cutting tool
  exSquare = face.extrude(Base.Vector(0.0, 0.0, m * 1.2))
  # Part.show(exHex)
  return exSquare


def sqnutMakeFace(do, di, dw, s, m):
  do = do / 2
  dw = dw / 2
  di = di / 2
  ch1 = do - di
  ch2 = (s - dw) * tan30
  
  fm = FastenerBase.FSFaceMaker()
  fm.AddPoint(di, ch1)
  fm.AddPoint(do, 0)
  fm.AddPoint(s, 0)
  if dw > 0:
    fm.AddPoint(s, m - ch2)
    fm.AddPoint(dw, m)
  else :
    fm.AddPoint(s, m)
  fm.AddPoint(do, m)
  fm.AddPoint(di, m - ch1)
  return fm.GetFace()

def nut562MakeSolid(diam):
  if not(diam in din562def):
    return None
  (key, shape) = FastenerBase.FSGetKey('Nut562', diam)
  if shape != None:
    return shape
  
  s, m, di = din562def[diam]
  do = FastenerBase.MToFloat(diam)
  f = sqnutMakeFace(do, di, 0, s, m)
  p = f.revolve(Base.Vector(0.0,0.0,0.0),Base.Vector(0.0,0.0,1.0),360)
  htool = makeSquareTool(s, m)
  shape = p.cut(htool)
  FastenerBase.FSCache[key] = shape
  return shape
    
###################################################################################
# Square Metric Hex nuts DIN 557
din557def = {
#         s,    m,    d     dw
  'M4':  (7.0,  3.2,  3.3,  5.7),
  'M5':  (8.0,  4,    4.2,  6.7),
  'M6':  (10.0, 5,    5.0,  8.7),
  'M8':  (13.0, 6.5,  6.8,  11.5),
  'M10': (17.0, 8,    8.5,  15.5),
  'M12': (19.0, 10,   10.2, 17.2),
  'M16': (24.0, 13,   14.0, 22)
}

def nut557MakeSolid(diam):
  if not(diam in din557def):
    return None
  (key, shape) = FastenerBase.FSGetKey('Nut557', diam)
  if shape != None:
    return shape
  
  s, m, di, dw = din557def[diam]
  do = FastenerBase.MToFloat(diam)
  f = sqnutMakeFace(do, di, dw, s, m)
  p = f.revolve(Base.Vector(0.0,0.0,0.0),Base.Vector(0.0,0.0,1.0),360)
  htool = makeSquareTool(s, m)
  shape = p.cut(htool)
  FastenerBase.FSCache[key] = shape
  return shape
  
###################################################################################
# Nyloc Hex nuts DIN 985
din985def = {
#           P,    damax, dw,  e,     m,   h,    s_nom
  'M3':    (0.5,  3.45, 4.6,  6.1,   2.4,  4.0,  5.5),
  'M4':    (0.7,  4.6,  5.9,  7.7,   2.9,  5.0,  7.0), 
  'M5':    (0.8,  5.75, 6.9,  8.9,   3.2,  5.0,  8.0),
  'M6':    (1.0,  6.75, 8.9,  11.05, 4.0,  6.0, 10.0),
  'M7':    (1.0,  6.75, 9.6,  12.12, 4.7,  7.5, 11.0),
  'M8':    (1.25, 8.75, 11.6, 14.5,  5.5,  8.0, 13.0),
  'M10':   (1.50, 10.8, 15.6, 17.9,  6.5, 10.0,  16.0),
  'M12':   (1.75, 13.0, 17.4, 20.1,  8.0, 12.0,  18.0),
  'M14':   (2.00, 15.1, 20.5, 24.5,  9.5, 14.0,  22.0),
  'M16':   (2.00, 17.3, 22.5, 26.9, 10.5, 16.0,  24.0),
  'M18':   (2.50, 19.5, 24.9, 29.6, 13.0, 18.5,  27.0),
  'M20':   (2.50, 21.6, 27.7, 33.7, 14.0, 20.0,  30.0),
  'M22':   (2.50, 23.7, 29.5, 37.3, 15.0, 22.0,  34.0),
  'M24':   (3.00, 25.9, 33.2, 40.1, 15.0, 24.0,  36.0),
  'M27':   (3.00, 29.1, 38.0, 45.2, 17.0, 27.0,  41.0),
  'M30':   (3.50, 32.4, 42.7, 50.9, 19.0, 30.0,  46.0), 
  'M33':   (3.50, 35.6, 46.6, 55.4, 22.0, 33.0,  50.0), 
  'M36':   (4.00, 38.9, 51.1, 61.0, 25.0, 36.0,  55.0),
  'M39':   (4.00, 42.1, 55.9, 66.5, 17.0, 39.0,  60.0),
  'M42':   (4.50, 45.4, 60.6, 71.3, 29.0, 42.0,  65.0),
  'M45':   (4.50, 48.6, 64.7, 77.0, 32.0, 45.0,  70.0),
  'M48':   (5.00, 51.8, 69.4, 82.6, 36.0, 48.0,  75.0),
  } 

  
def nylocMakeFace(do, p, da, dw, e, m, h, s):
  di = (do - p) / 2
  do = do / 2
  dw = dw / 2
  da = da / 2
  e = e / 2
  s = s / 2
  s1 = s * 0.999
  ch1 = do - di
  ch2 = (e - dw) * tan30
  ch3 = m - (e - s) * tan30
  h1 = h * 0.9
  r = (s - di) / 3
    
  fm = FastenerBase.FSFaceMaker()
  fm.AddPoint(di, ch1)
  fm.AddPoint(da, 0)
  fm.AddPoint(dw, 0)
  fm.AddPoint(e, ch2)
  fm.AddPoint(e, ch3)
  fm.AddPoint(s1, m)
  fm.AddPoint(s1, h - r)
  fm.AddArc2(-r, 0, 90)
  fm.AddPoint(di + r, h)
  fm.AddPoint(di + r, h1)
  fm.AddPoint(di, h1)
  return fm.GetFace()

def nut985MakeSolid(diam):
  if not(diam in din985def):
    return None
  (key, shape) = FastenerBase.FSGetKey('Nut985', diam)
  if shape != None:
    return shape
  
  p, da, dw, e, m, h, s = din985def[diam]
  do = FastenerBase.MToFloat(diam)
  f = nylocMakeFace(do, p, da, dw, e, m, h, s)
  p = f.revolve(Base.Vector(0.0,0.0,0.0),Base.Vector(0.0,0.0,1.0),360)
  screwMaker = ScrewMaker.Instance()
  htool = htool = screwMaker.makeHextool(s, m, s * 2)
  shape = p.cut(htool)
  FastenerBase.FSCache[key] = shape
  return shape
 
 
def createNut(type, diam):
  if (type == 'DIN557'):
    return nut557MakeSolid(diam)
  if (type == 'DIN562'):
    return nut562MakeSolid(diam)
  if (type == 'DIN985'):
    return nut985MakeSolid(diam)
  return None
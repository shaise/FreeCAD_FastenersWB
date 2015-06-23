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
import FreeCAD, FreeCADGui, Part, os
__dir__ = os.path.dirname(__file__)
iconPath = os.path.join( __dir__, 'Icons' )

import FastenerBase
from FastenerBase import FSBaseObject
import ScrewMaker  
screwMaker = ScrewMaker.Instance()


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
  
  ls, c, e, t, di = CLSPEMTable[diam]
  a = ls[i]
  if a == 0:
    return None
  do = float(diam.lstrip('M'))
  f = clMakeWire(do, di, a, c, e, t)
  p = f.revolve(Base.Vector(0.0,0.0,0.0),Base.Vector(0.0,0.0,1.0),360)
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
      fp.Shape = s
    else:
      FreeCAD.Console.PrintLog("Using cached object\n")
    if shape != None:
      #feature = FreeCAD.ActiveDocument.getObject(self.Proxy)
      fp.Placement = FreeCAD.Placement() # reset placement
      screwMaker.moveScrewToObject(fp, shape, fp.invert, fp.offset.Value)


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
    return True

Gui.addCommand("FSPressNut", FSPressnutCommand())
FastenerBase.FSCommands.append("FSPressNut")

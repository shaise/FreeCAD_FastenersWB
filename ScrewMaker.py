# -*- coding: utf-8 -*-

# A Wrapper to Ulrich's screw_maker macro

import FreeCAD, FreeCADGui, Part, math
from FreeCAD import Base
import DraftVecUtils
import FastenerBase

from PySide import QtCore, QtGui
from screw_maker import *
import FSNuts
from FSNuts import din557def, din562def, din985def
from FastenerBase import FSParam

FSCScrewHoleChart = (
  ("M1", 0.75),
  ("M1.1", 0.85),
  ("M1.2", 0.95),
  ("M1.4", 1.10),
  ("M1.6", 1.25),
  ("M1.8", 1.45),
  ("M2", 1.60),
  ("M2.2", 1.75),
  ("M2.5", 2.05),
  ("M3", 2.50),
  ("M3.5", 2.90),
  ("M4", 3.30),
  ("M4.5", 3.70),
  ("M5", 4.20),
  ("M6", 5.00),
  ("M7", 6.00),
  ("M8", 6.80),
  ("M9", 7.80),
  ("M10", 8.50),
  ("M11", 9.50),
  ("M12", 10.20),
  ("M14", 12.00),
  ("M16", 14.00),
  ("M18", 15.50),
  ("M20", 17.50),
  ("M22", 19.50),
  ("M24", 21.00),
  ("M27", 24.00),
  ("M30", 26.50),
  ("M33", 29.50),
  ("M36", 32.00),
  ("M39", 35.00),
  ("M42", 37.50),
  ("M45", 40.50),
  ("M48", 43.00),
  ("M52", 47.00),
  ("M56", 50.50),
  ("M60", 54.50),
  ("M64", 58.00),
  ("M68", 62.00)
)

# prepare a dictionary for fast search of FSCGetInnerThread
FSCScrewHoleChartDict = {}
for s in FSCScrewHoleChart:
  FSCScrewHoleChartDict[s[0]] = s[1]
       
def FSCGetInnerThread(diam):
  diam = diam.lstrip('(')
  diam = diam.rstrip(')')
  return FSCScrewHoleChartDict[diam]


screwTables = {
    #            name,    def table,   length table,  range table,  diam pos*, K pos**
    'ISO4017':  ("Screw",  iso4017head,  iso4017length,  iso4017range,  -1, 0),
    'ISO4014':  ("Screw",  iso4014head,  iso4014length,  iso4014range,  -1, 0),
    'EN1662':   ("Screw",  en1662def,    en1662length,   en1662range,   -1, 0),            
    'EN1665':   ("Screw",  en1665def,    en1665length,   en1665range,   -1, 0),
    'ISO2009':  ("Screw",  iso2009def,   iso2009length,  iso2009range,  4, 5),
    'ISO2010':  ("Screw",  iso2009def,   iso2009length,  iso2009range,  4, 5),
    'ISO4762':  ("Screw",  iso4762def,   iso4762length,  iso4762range,  -1, 0),
    'ISO10642': ("Screw",  iso10642def,  iso10642length, iso10642range, 3, 7),
    'ISO1207':  ("Screw",  iso1207def,   iso1207length,  iso1207range,  -1, 0),
    'ISO1580':  ("Screw",  iso1580def,   iso2009length,  iso2009range,  -1, 0),
    'ISO7045':  ("Screw",  iso7045def,   iso7045length,  iso7045range,  -1, 0),
    'ISO7046':  ("Screw",  iso2009def,   iso7045length,  iso7046range,  4, 5),
    'ISO7047':  ("Screw",  iso2009def,   iso7045length,  iso7046range,  4, 5),
    'ISO7048':  ("Screw",  iso7048def,   iso7048length,  iso7048range,  -1, 0),
    'DIN967':   ("Screw",  din967def,    din967length,   din967range,   -1, 0),
    'ISO7379':  ("Screw",  iso7379def,   iso7379length,  iso7379range,  2, 0),
    #'ISO7380':  ("Screw", iso7380def, iso7380length, iso7380range, -1),
    'ISO7380-1':("Screw",  iso7380def,   iso7380length,  iso7380range,  -1, 0),
    'ISO7380-2':("Screw",  iso7380_2def, iso7380length,  iso7380range,  -1, 0),
    'ISO14579': ("Screw",  iso14579def,  iso14579length, iso14579range, -1, 0),
    'ISO14580': ("Screw",  iso14580def,  iso14580length, iso1207range,  -1, 0),
    'ISO14582': ("Screw",  iso14582def,  iso14582length, iso14582range, 4, 5),
    'ISO14583': ("Screw",  iso14583def,  iso7045length,  iso7046range,  -1, 0),
    'ISO14584': ("Screw",  iso14584def,  iso7045length, iso14584range,  3, 5),
    'DIN7984':  ("Screw",  din7984def,   din7984length, din7984range, -1, 0),
    'ISO7089':  ("Washer", iso7089def,   None,          None,           -1, 0),
    'ISO7090':  ("Washer", iso7090def,   None,          None,           -1, 0),
    #'ISO7091':  ("Washer", iso7091def,   None,          None,           -1, 0), # same as 7089 ??
    'ISO7092':  ("Washer", iso7092def,   None,          None,           -1, 0),
    'ISO7093-1':("Washer", iso7093def,   None,          None,           -1, 0),
    'ISO7094':  ("Washer", iso7094def,   None,          None,           -1, 0),
    'ISO4032':  ("Nut",    iso4032def,   None,          None,           -1, 0),
    'ISO4033':  ("Nut",    iso4033def,   None,          None,           -1, 0),
    'ISO4035':  ("Nut",    iso4035def,   None,          None,           -1, 0),
    #'ISO4036':  ("Nut",    iso4036def,   None,          None,           -1),
    'EN1661':   ("Nut",    en1661def,    None,          None,           -1, 0),
    'DIN557':   ("Nut",    din557def,    None,          None,           -1, 0),
    'DIN562':   ("Nut",    din562def,    None,          None,           -1, 0),
    'DIN985':   ("Nut",    din985def,    None,          None,           -1, 0),
    'ScrewTap': ("ScrewTap", tuningTable, None,         None,           -1, 0),
    
    # * diam pos = the position within the def table to be used for auto diameter selection, -1 = get size from Mxx
    # * K Pos = the position within the def table to be used for countersunk holes creation
}

FSNutsList = ['DIN562', 'DIN557', 'DIN985']

class FSScrewMaker(Screw):
    def FindClosest(self, type, diam, len):
      ''' Find closest standard screw to given parameters '''        
      if not (type in screwTables):
        return (diam, len)
      name, diam_table, len_table, range_table, table_pos, k_pos = screwTables[type]
      
      # auto find diameter
      if not (diam in diam_table):
        origdia = FastenerBase.MToFloat(diam)
        mindif = 100.0
        for m in diam_table:
          diff = abs(FastenerBase.MToFloat(m) - origdia)
          if (diff < mindif):
            mindif = diff
            diam = m

      # auto find length
      if (len_table != None) and not (len in len_table):
        origlen = float(len)
        mindif = 100.0
        for l in len_table:
          diff = abs(float(l) - origlen)
          if (diff < mindif):
            mindif = diff
            len = l
              
      # make sure length in range
      if range_table != None:
        minl , maxl = range_table[diam]
        if float(len) < float(minl):
          len = minl
        if float(len) > float(maxl):
          len = maxl
        
      return (diam, len)
        
        
    def AutoDiameter(self, type, holeObj, baseobj = None, matchOuter = FastenerBase.FSMatchOuter):
      ''' Calculate screw diameter automatically based on given hole '''
      res = 'M6'
      #matchOuter = FastenerBase.FSMatchOuter
      if baseobj != None and baseobj.Name.startswith("Washer"):
        matchOuter = True
      if holeObj != None and hasattr(holeObj, 'Curve') and hasattr(holeObj.Curve, 'Radius') and (type in screwTables):
        d = holeObj.Curve.Radius * 2
        table = screwTables[type][1]
        tablepos = screwTables[type][4]
        mindif = 10.0
        dif = mindif
        for m in table:
            #FreeCAD.Console.PrintLog("Test M:" + m + "\n")
            if (tablepos == -1):
              if matchOuter:
                dia = FastenerBase.MToFloat(m) - 0.01
                if (d > dia):
                  dif = d - dia
              else:
                dia = FSCGetInnerThread(m)
                dif = math.fabs(dia - d)
              
            else:
              dia = table[m][tablepos]
              if (d > dia):
                dif = d - dia
            if dif < mindif:
              mindif = dif
              res = m
      return res
    
    def GetAllTypes(self, typeName):
      list = []
      for key in screwTables:
        if screwTables[key][0] == typeName:
          list.append(key)
      list.sort()
      return list
      
    def GetTypeName(self, type):
      if not(type in screwTables):
        return "None"
      return screwTables[type][0]
    
    def GetAllDiams(self, type):
      FreeCAD.Console.PrintLog("Get diams for type:" + str(type) + "\n")
      return sorted(screwTables[type][1], key = FastenerBase.MToFloat)

    def GetAllLengths(self, type, diam):
      lens = screwTables[type][2]
      range = screwTables[type][3][diam]
      list = []
      min = float(range[0])
      max = float(range[1])
      for len in lens:
        l = float(len)
        if l >= min and l <= max:
          list.append(len)
      list.sort(key = FastenerBase.MToFloat)
      list.append("Custom")
      return list

    def GetAllCountersunkTypes(self):
      list = []
      for key in screwTables:
        if screwTables[key][0] == "Screw" and screwTables[key][4] >= 0:
          list.append(key)
      list.sort()
      return list
      
    def GetCountersunkDiams(self, type):
      dpos = screwTables[type][4]
      if dpos < 0:
        return None
      kpos = screwTables[type][5]
      table = screwTables[type][1]
      res = {}
      for diam in table:
        res[diam] = (table[diam][dpos], table[diam][kpos])
      return res
   
    def GetCountersunkDims(self, type, diam):
      dpos = screwTables[type][4]
      if dpos < 0:
        return (0,0)
      kpos = screwTables[type][5]
      table = screwTables[type][1]
      if not(diam in table):
        return (0,0)
      return (table[diam][dpos], table[diam][kpos])
      
    def updateFastenerParameters(self):
      global FSParam
      oldState = str(self.sm3DPrintMode) + str(self.smNutThrScaleA) + str(self.smNutThrScaleB) + str(self.smScrewThrScaleA) + str(self.smScrewThrScaleB)
      self.sm3DPrintMode = False
      threadMode = FSParam.GetInt("ScrewToolbarThreadGeneration", 0) # 0 = standard, 1 = 3dprint
      if threadMode == 1:
        self.sm3DPrintMode = True
      self.smNutThrScaleA = FSParam.GetFloat("NutThrScaleA", 1.03)
      self.smNutThrScaleB = FSParam.GetFloat("NutThrScaleB", 0.1)
      self.smScrewThrScaleA = FSParam.GetFloat("ScrewThrScaleA", 0.99)
      self.smScrewThrScaleB = FSParam.GetFloat("ScrewThrScaleB", -0.05)
      newState = str(self.sm3DPrintMode) + str(self.smNutThrScaleA) + str(self.smNutThrScaleB) + str(self.smScrewThrScaleA) + str(self.smScrewThrScaleB)
      if (oldState != newState):
        FastenerBase.FSCacheRemoveThreaded() # thread parameters have changed, remove cached ones    

    def createFastener(self, type, diam, len, threadType, shapeOnly = False):
      if type in FSNutsList :
        return FSNuts.createNut(type, diam)
      return self.createScrew(type, diam, len, threadType, shapeOnly)


ScrewMakerInstance = None      
def Instance():
  global ScrewMakerInstance
  if ScrewMakerInstance == None:
    ScrewMakerInstance = FSScrewMaker()
  return ScrewMakerInstance

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
    'ISO4017':  ("Screw",  FsData["iso4017head"],  FsData["iso4017length"],  FsData["iso4017range"],  -1, 0),
    'ISO4014':  ("Screw",  FsData["iso4014head"],  FsData["iso4014length"],  FsData["iso4014range"],  -1, 0),
    'EN1662':   ("Screw",  FsData["en1662def"],    FsData["en1662length"],   FsData["en1662range"],   -1, 0),            
    'EN1665':   ("Screw",  FsData["en1665def"],    FsData["en1665length"],   FsData["en1665range"],   -1, 0),
    'ISO2009':  ("Screw",  FsData["iso2009def"],   FsData["iso2009length"],  FsData["iso2009range"],  4, 5),
    'ISO2010':  ("Screw",  FsData["iso2009def"],   FsData["iso2009length"],  FsData["iso2009range"],  4, 5),
    'ISO4762':  ("Screw",  FsData["iso4762def"],   FsData["iso4762length"],  FsData["iso4762range"],  -1, 0),
    'ISO10642': ("Screw",  FsData["iso10642def"],  FsData["iso10642length"], FsData["iso10642range"], 3, 7),
    'ISO1207':  ("Screw",  FsData["iso1207def"],   FsData["iso1207length"],  FsData["iso1207range"],  -1, 0),
    'ISO1580':  ("Screw",  FsData["iso1580def"],   FsData["iso2009length"],  FsData["iso2009range"],  -1, 0),
    'ISO7045':  ("Screw",  FsData["iso7045def"],   FsData["iso7045length"],  FsData["iso7045range"],  -1, 0),
    'ISO7046':  ("Screw",  FsData["iso2009def"],   FsData["iso7045length"],  FsData["iso7046range"],  4, 5),
    'ISO7047':  ("Screw",  FsData["iso2009def"],   FsData["iso7045length"],  FsData["iso7046range"],  4, 5),
    'ISO7048':  ("Screw",  FsData["iso7048def"],   FsData["iso7048length"],  FsData["iso7048range"],  -1, 0),
    'DIN967':   ("Screw",  FsData["din967def"],    FsData["din967length"],   FsData["din967range"],   -1, 0),
    'ISO7379':  ("Screw",  FsData["iso7379def"],   FsData["iso7379length"],  FsData["iso7379range"],  -1, 0),
    'ISO7380-1':("Screw",  FsData["iso7380def"],   FsData["iso7380length"],  FsData["iso7380range"],  -1, 0),
    'ISO7380-2':("Screw",  FsData["iso7380_2def"], FsData["iso7380length"],  FsData["iso7380range"],  -1, 0),
    'ISO14579': ("Screw",  FsData["iso14579def"],  FsData["iso14579length"], FsData["iso14579range"], -1, 0),
    'ISO14580': ("Screw",  FsData["iso14580def"],  FsData["iso14580length"], FsData["iso1207range"],  -1, 0),
    'ISO14582': ("Screw",  FsData["iso14582def"],  FsData["iso14582length"], FsData["iso14582range"], 4, 5),
    'ISO14583': ("Screw",  FsData["iso14583def"],  FsData["iso7045length"],  FsData["iso7046range"],  -1, 0),
    'ISO14584': ("Screw",  FsData["iso14584def"],  FsData["iso7045length"],  FsData["iso14584range"],  3, 5),
    'DIN7984':  ("Screw",  FsData["din7984def"],   FsData["din7984length"],  FsData["din7984range"], -1, 0),
    'ISO7089':  ("Washer", FsData["iso7089def"],   None,          None,           -1, 0),
    'ISO7090':  ("Washer", FsData["iso7090def"],   None,          None,           -1, 0),
    'ISO7092':  ("Washer", FsData["iso7092def"],   None,          None,           -1, 0),
    'ISO7093-1':("Washer", FsData["iso7093def"],   None,          None,           -1, 0),
    'ISO7094':  ("Washer", FsData["iso7094def"],   None,          None,           -1, 0),
    'ISO4026':  ("Screw",  FsData["iso4026def"],   FsData["iso4026length"],  FsData["iso4026range"],   -1, 0),
    'ISO4027':  ("Screw",  FsData["iso4026def"],   FsData["iso4026length"],  FsData["iso4026range"],   -1, 0),
    'ISO4028':  ("Screw",  FsData["iso4028def"],   FsData["iso4028length"],  FsData["iso4028range"],   -1, 0),
    'ISO4029':  ("Screw",  FsData["iso4026def"],   FsData["iso4026length"],  FsData["iso4026range"],   -1, 0),
    'ISO4032':  ("Nut",    FsData["iso4032def"],   None,          None,           -1, 0),
    'ISO4033':  ("Nut",    FsData["iso4033def"],   None,          None,           -1, 0),
    'ISO4035':  ("Nut",    FsData["iso4035def"],   None,          None,           -1, 0),
    'EN1661':   ("Nut",    FsData["en1661def"],    None,          None,           -1, 0),
    'DIN557':   ("Nut",    din557def,    None,          None,           -1, 0),
    'DIN562':   ("Nut",    din562def,    None,          None,           -1, 0),
    'DIN985':   ("Nut",    din985def,    None,          None,           -1, 0),
    'ASMEB18.2.1.6': ("Screw", FsData["asmeb18.2.1.6def"], FsData["asmeb18.2.1.6length"], FsData["asmeb18.2.1.6range"], -1, 0),
    'ASMEB18.2.1.8':   ("Screw", FsData["asmeb18.2.1.8def"], FsData["inch_fs_length"], FsData["asmeb18.2.1.8range"], -1, 0),
    'ASMEB18.3.1A': ("Screw", FsData["asmeb18.3.1adef"], FsData["inch_fs_length"], FsData["asmeb18.3.1arange"], -1, 0),
    'ASMEB18.3.2': ("Screw", FsData["asmeb18.3.2def"], FsData["inch_fs_length"], FsData["asmeb18.3.2range"], -1, 0),
    'ASMEB18.3.3A': ("Screw", FsData["asmeb18.3.3adef"], FsData["inch_fs_length"], FsData["asmeb18.3.3arange"], -1, 0),
    'ASMEB18.3.3B': ("Screw", FsData["asmeb18.3.3bdef"], FsData["inch_fs_length"], FsData["asmeb18.3.3brange"], -1, 0),
    'ASMEB18.3.4': ("Screw", FsData["asmeb18.3.4def"], FsData["inch_fs_length"], FsData["asmeb18.3.4range"], -1, 0),
    'ASMEB18.3.5A': ("Screw", FsData["asmeb18.3.5def"], FsData["inch_fs_length"], FsData["asmeb18.3.5range"], -1, 0),
    'ASMEB18.3.5B': ("Screw", FsData["asmeb18.3.5def"], FsData["inch_fs_length"], FsData["asmeb18.3.5range"], -1, 0),
    'ASMEB18.3.5C': ("Screw", FsData["asmeb18.3.5def"], FsData["inch_fs_length"], FsData["asmeb18.3.5range"], -1, 0),
    'ASMEB18.3.5D': ("Screw", FsData["asmeb18.3.5def"], FsData["inch_fs_length"], FsData["asmeb18.3.5range"], -1, 0),
    'ScrewTap': ("ScrewTap", FsData["tuningTable"], None,         None,           -1, 0),
    'ScrewDie': ("ScrewDie", FsData["tuningTable"], None,         None,           -1, 0),
    'ThreadedRod': ("ThreadedRod", FsData["tuningTable"], None,   None,           -1, 0),
    
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
        origdia = FastenerBase.DiaStr2Num(diam)
        mindif = 100.0
        for m in diam_table:
          diff = abs(FastenerBase.DiaStr2Num(m) - origdia)
          if (diff < mindif):
            mindif = diff
            diam = m

      # auto find length
      if (len_table != None) and not (len in len_table):
        origlen = FastenerBase.LenStr2Num(len)
        mindif = 100.0
        for l in len_table:
          diff = abs(FastenerBase.LenStr2Num(l) - origlen)
          if (diff < mindif):
            mindif = diff
            len = l
              
      # make sure length in range
      if range_table != None:
        minl , maxl = range_table[diam]
        if FastenerBase.LenStr2Num(len) < FastenerBase.LenStr2Num(minl):
          len = minl
        if FastenerBase.LenStr2Num(len) > FastenerBase.LenStr2Num(maxl):
          len = maxl
        
      return (diam, len)
        
        
    def AutoDiameter(self, type, holeObj, baseobj = None, matchOuter = FastenerBase.FSMatchOuter):
      ''' Calculate screw diameter automatically based on given hole '''
      # this function is also used to assign the deafult screw diameter
      # when a new fastener is created. the following deafult values are 
      # assigned depending on available diameters
      if 'M6' in self.GetAllDiams(type):
        res = 'M6'
      elif '1/4in' in self.GetAllDiams(type):
        res = '1/4in'
      elif '#10' in self.GetAllDiams(type):
        res = '#10'
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
                dia = FastenerBase.DiaStr2Num(m) - 0.01
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
      return sorted(screwTables[type][1], key = FastenerBase.DiaStr2Num) #***

    def GetAllLengths(self, type, diam):
      lens = screwTables[type][2]
      range = screwTables[type][3][diam]
      list = []
      min = FastenerBase.LenStr2Num(range[0])
      max = FastenerBase.LenStr2Num(range[1])
      for len in lens:
        l = FastenerBase.LenStr2Num(len)
        if l >= min and l <= max:
          list.append(len)
      list.sort(key = FastenerBase.LenStr2Num) #***
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

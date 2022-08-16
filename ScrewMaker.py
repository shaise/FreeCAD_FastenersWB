# -*- coding: utf-8 -*-

# A Wrapper to Ulrich's screw_maker macro

import FreeCAD, FreeCADGui, Part, math
from FreeCAD import Base
import DraftVecUtils
import FastenerBase

from PySide import QtCore, QtGui
from screw_maker import *
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

FSC_Inch_ScrewHoleChart = (
    ("#0", 1.2),
    ("#1", 1.5),
    ("#2", 1.8),
    ("#3", 2.0),
    ("#4", 2.3),
    ("#5", 2.6),
    ("#6", 2.7),
    ("#8", 3.5),
    ("#10", 3.8),
    ("#12", 4.5),
    ("1/4in", 5.1),
    ("5/16in", 6.5),
    ("3/8in", 8.0),
    ("7/16in", 9.3),
    ("1/2in", 10.7),
    ("9/16in", 12.3),
    ("5/8in", 13.5),
    ("3/4in", 16.7),
    ("7/8in", 19.4),
    ("1in", 22.2),
    ("1 1/8in", 25.0),
    ("1 1/4in", 28.0),
    ("1 3/8in", 31.0),
    ("1 1/2in", 34.0),
    ("1 5/8in", 37.75),
    ("1 3/4in", 41.0),
    ("1 7/8in", 44.0),
    ("2in", 47.0),
    ("2 1/4in", 54.0),
    ("2 1/2in", 56.5),
    ("2 3/4in", 63.0),
    ("3in", 69.0),
    ("3 1/4in", 75.5),
    ("3 1/2in", 82.0),
    ("3 3/4in", 88.0),
    ("4in", 95.0)
)

FSC_DIN7998_ScrewHoleChart = (
    ("4 mm", 2.8),
    ("5 mm", 3.5),
    ("6 mm", 4.2),
    ("8 mm", 5.6),
    ("10 mm", 7),
    ("12 mm", 9),
    ("16 mm", 12),
    ("20 mm", 25)
)

# prepare a dictionary for fast search of FSCGetInnerThread
FSCScrewHoleChartDict = {}
for s in FSCScrewHoleChart:
    FSCScrewHoleChartDict[s[0]] = s[1]
for s in FSC_Inch_ScrewHoleChart:
    FSCScrewHoleChartDict[s[0]] = s[1]
for s in FSC_DIN7998_ScrewHoleChart:
    FSCScrewHoleChartDict[s[0]] = s[1]


def FSCGetInnerThread(diam):
    diam = diam.lstrip('(')
    diam = diam.rstrip(')')
    return FSCScrewHoleChartDict[diam]

FASTENER_FAMILY_POS = 0
COUNTERSUNK_DPOS = 1
COUNTERSUNK_KPOS = 2
FUNCTION_POS = 3

screwTables = {
    #            name,     diam pos*, K pos**, function
    'ISO4017':  ("Screw",  -1, 0, "makeHexHeadBolt"),
    'ISO4014':  ("Screw",  -1, 0, "makeHexHeadBolt"),
    'EN1662':   ("Screw",  -1, 0, "makeHexHeadWithFlunge"),
    'EN1665':   ("Screw",  -1, 0, "makeHexHeadWithFlunge"),
    'ISO2009':  ("Screw",   4, 5, "makeSlottedScrew"),
    'ISO2010':  ("Screw",   4, 5, "makeSlottedScrew"),
    'ISO4762':  ("Screw",  -1, 0, "makeCylinderHeadScrew"),
    'ISO10642': ("Screw",   3, 7, "makeCountersunkHeadScrew"),
    'ISO1207':  ("Screw",  -1, 0, "makeCheeseHeadScrew"),
    'ISO1580':  ("Screw",  -1, 0, "makeSlottedScrew"),
    'ISO7045':  ("Screw",  -1, 0, "makePanHeadScrew"),
    'ISO7046':  ("Screw",   4, 5, "makeCountersunkHeadScrew"),
    'ISO7047':  ("Screw",   4, 5, "makeCountersunkHeadScrew"),
    'ISO7048':  ("Screw",  -1, 0, "makeCheeseHeadScrew"),
    'DIN967':   ("Screw",  -1, 0, "makeButtonHeadScrew"),
    'ISO7379':  ("Screw",  -1, 0, "makeShoulderScrew"),
    'ISO7380-1':("Screw",  -1, 0, "makeButtonHeadScrew"),
    'ISO7380-2':("Screw",  -1, 0, "makeButtonHeadScrew"),
    'ISO14579': ("Screw",  -1, 0, "makeCylinderHeadScrew"),
    'ISO14580': ("Screw",  -1, 0, "makeCheeseHeadScrew"),
    'ISO14582': ("Screw",   4, 5, "makeCountersunkHeadScrew"),
    'ISO14583': ("Screw",  -1, 0, "makePanHeadScrew"),
    'ISO14584': ("Screw",   3, 5, "makeCountersunkHeadScrew"),
    'DIN7984':  ("Screw",  -1, 0, "makeCylinderHeadScrew"),
    'DIN6912':  ("Screw",  -1, 0, "makeCylinderHeadScrew"),
    'DIN571':   ("Screw",  -1, 0, "makeWoodScrew"),
    'ISO7089':  ("Washer", -1, 0, "makeWasher"),
    'ISO7090':  ("Washer", -1, 0, "makeWasher"),
    'ISO7091':  ("Washer", -1, 0, "makeWasher"),
    'ISO7092':  ("Washer", -1, 0, "makeWasher"),
    'ISO7093-1':("Washer", -1, 0, "makeWasher"),
    'ISO7094':  ("Washer", -1, 0, "makeWasher"),
    'NFE27-619':("Washer", -1, 0, "makeWasher"),
    'ISO4026':  ("Screw",  -1, 0, "makeSetScrew"),
    'ISO4027':  ("Screw",  -1, 0, "makeSetScrew"),
    'ISO4028':  ("Screw",  -1, 0, "makeSetScrew"),
    'ISO4029':  ("Screw",  -1, 0, "makeSetScrew"),
    'ISO4032':  ("Nut",    -1, 0, "makeHexNut"),
    'ISO4033':  ("Nut",    -1, 0, "makeHexNut"),
    'ISO4035':  ("Nut",    -1, 0, "makeHexNut"),
    'EN1661':   ("Nut",    -1, 0, "makeHexNutWFlunge"),
    'DIN917':   ("Nut",    -1, 0, "makeThinCupNut"),
    'DIN1587':  ("Nut",    -1, 0, "makeCupNut"),
    'DIN557':   ("Nut",    -1, 0, "makeSquareNut"),
    'DIN562':   ("Nut",    -1, 0, "makeSquareNut"),
    'DIN985':   ("Nut",    -1, 0, "makeNylocNut"),
    'ASMEB18.2.1.6': ("Screw",   -1, 0, "makeHexHeadBolt"),
    'ASMEB18.2.1.8':   ("Screw", -1, 0, "makeHexHeadWithFlunge"),
    'ASMEB18.2.2.1A': ("Nut",    -1, 0, "makeHexNut"),
    'ASMEB18.2.2.4A': ("Nut",    -1, 0, "makeHexNut"),
    'ASMEB18.2.2.4B': ("Nut",    -1, 0, "makeHexNut"),
    'ASMEB18.3.1A': ("Screw",    -1, 0, "makeCylinderHeadScrew"),
    'ASMEB18.3.1G': ("Screw",    -1, 0, "makeCylinderHeadScrew"),
    'ASMEB18.3.2': ("Screw",     -1, 0, "makeCountersunkHeadScrew"),
    'ASMEB18.3.3A': ("Screw",    -1, 0, "makeButtonHeadScrew"),
    'ASMEB18.3.3B': ("Screw",    -1, 0, "makeButtonHeadScrew"),
    'ASMEB18.3.4': ("Screw",     -1, 0, "makeShoulderScrew"),
    'ASMEB18.3.5A': ("Screw",    -1, 0, "makeSetScrew"),
    'ASMEB18.3.5B': ("Screw",    -1, 0, "makeSetScrew"),
    'ASMEB18.3.5C': ("Screw",    -1, 0, "makeSetScrew"),
    'ASMEB18.3.5D': ("Screw",    -1, 0, "makeSetScrew"),
    'ASMEB18.6.3.1A': ("Screw",  -1, 0, "makeSlottedScrew"),
    'ASMEB18.5.2': ("Screw",     -1, 0, "makeCarriageBolt"),
    'ASMEB18.21.1.12A': ("Washer", -1, 0, "makeWasher"),
    'ASMEB18.21.1.12B': ("Washer", -1, 0, "makeWasher"),
    'ASMEB18.21.1.12C': ("Washer", -1, 0, "makeWasher"),
    'ScrewTap': ("ScrewTap",           -1, 0, "makeScrewTap"),
    'ScrewTapInch': ("ScrewTap",       -1, 0, "makeScrewTap"),
    'ScrewDie': ("ScrewDie",           -1, 0, "makeScrewDie"),
    'ScrewDieInch': ("ScrewDie",       -1, 0, "makeScrewDie"),
    'ThreadedRod': ("ThreadedRod",     -1, 0, "makeThreadedRod"),
    'ThreadedRodInch': ("ThreadedRod", -1, 0, "makeThreadedRod"),
    
    # * diam pos = the position within the def table to be used for auto diameter selection, -1 = get size from Mxx
    # * K Pos = the position within the def table to be used for countersunk holes creation
}

class FSScrewMaker(Screw):
    def FindClosest(self, type, diam, len):
        ''' Find closest standard screw to given parameters '''
        if type not in screwTables:
            return diam, len

        diam_table = FsData[type + "def"]
        len_table = FsData[type + "length"]
        range_table = FsData[type + "range"]
        # auto find diameter
        if diam not in diam_table:
            origdia = FastenerBase.DiaStr2Num(diam)
            mindif = 100.0
            for m in diam_table:
                diff = abs(FastenerBase.DiaStr2Num(m) - origdia)
                if diff < mindif:
                    mindif = diff
                    diam = m

        # auto find length
        if (len_table is not None) and len not in len_table:
            origlen = FastenerBase.LenStr2Num(len)
            mindif = 100.0
            for l in len_table:
                diff = abs(FastenerBase.LenStr2Num(l) - origlen)
                if diff < mindif:
                    mindif = diff
                    len = l

        # make sure length in range
        if range_table is not None:
            minl, maxl = range_table[diam]
            if FastenerBase.LenStr2Num(len) < FastenerBase.LenStr2Num(minl):
                len = minl
            if FastenerBase.LenStr2Num(len) > FastenerBase.LenStr2Num(maxl):
                len = maxl

        return diam, len

    def AutoDiameter(self, type, holeObj, baseobj=None, matchOuter=FastenerBase.FSMatchOuter):
        ''' Calculate screw diameter automatically based on given hole '''
        # this function is also used to assign the default screw diameter
        # when a new fastener is created. the following default values are
        # assigned depending on available diameters
        if 'M6' in self.GetAllDiams(type):
            res = 'M6'
        elif '1/4in' in self.GetAllDiams(type):
            res = '1/4in'
        elif '#10' in self.GetAllDiams(type):
            res = '#10'
        elif '6 mm' in self.GetAllDiams(type):
            res = '6 mm'
        # matchOuter = FastenerBase.FSMatchOuter
        if baseobj is not None and baseobj.Name.startswith("Washer"):
            matchOuter = True
        if holeObj is not None and hasattr(holeObj, 'Curve') and hasattr(holeObj.Curve, 'Radius') and (
                type in screwTables):
            d = holeObj.Curve.Radius * 2
            table = FsData[type + "def"]
            tablepos = screwTables[type][COUNTERSUNK_DPOS]
            mindif = 10.0
            dif = mindif
            for m in table:
                # FreeCAD.Console.PrintLog("Test M:" + m + "\n")
                if tablepos == -1:
                    if matchOuter:
                        dia = FastenerBase.DiaStr2Num(m) - 0.01
                        if d > dia:
                            dif = d - dia
                    else:
                        dia = FSCGetInnerThread(m)
                        dif = math.fabs(dia - d)

                else:
                    dia = table[m][tablepos]
                    if d > dia:
                        dif = d - dia
                if dif < mindif:
                    mindif = dif
                    res = m
        return res

    def GetAllTypes(self, typeName):
        list = []
        for key in screwTables:
            if screwTables[key][FASTENER_FAMILY_POS] == typeName:
                list.append(key)
        list.sort()
        return list

    def GetTypeName(self, type):
        if not (type in screwTables):
            return "None"
        return screwTables[type][FASTENER_FAMILY_POS]

    def GetAllDiams(self, type):
        FreeCAD.Console.PrintLog("Get diams for type:" + str(type) + "\n")
        return sorted(FsData[type + "def"], key=FastenerBase.DiaStr2Num)  # ***

    def GetAllTcodes(self, type):
        return FsData[type + "tcode"]

    def GetAllLengths(self, type, diam, addCustom = True):
        lens = FsData[type + "length"]
        range = FsData[type + "range"][diam]
        list = []
        min = FastenerBase.LenStr2Num(range[0])
        max = FastenerBase.LenStr2Num(range[1])
        for len in lens:
            l = FastenerBase.LenStr2Num(len)
            if l >= min and l <= max:
                list.append(len)
        list.sort(key=FastenerBase.LenStr2Num)  # ***
        if addCustom:
            list.append("Custom")
        return list

    def GetAllCountersunkTypes(self):
        list = []
        for key in screwTables:
            if screwTables[key][FASTENER_FAMILY_POS] == 'Screw' and screwTables[key][COUNTERSUNK_DPOS] >= 0:
                list.append(key)
        list.sort()
        return list

    def GetCountersunkDiams(self, type):
        dpos = screwTables[type][COUNTERSUNK_DPOS]
        if dpos < 0:
            return None
        kpos = screwTables[type][COUNTERSUNK_KPOS]
        table = FsData[type + "def"]
        res = {}
        for diam in table:
            res[diam] = (table[diam][dpos], table[diam][kpos])
        return res

    def GetCountersunkDims(self, type, diam):
        dpos = screwTables[type][COUNTERSUNK_DPOS]
        if dpos < 0:
            return 0, 0
        kpos = screwTables[type][COUNTERSUNK_KPOS]
        table = FsData[type + "def"]
        if not (diam in table):
            return 0, 0
        return table[diam][dpos], table[diam][kpos]

    def updateFastenerParameters(self):
        global FSParam
        oldState = str(self.sm3DPrintMode) + str(self.smNutThrScaleA) + str(self.smNutThrScaleB) + str(self.smScrewThrScaleA) + str(self.smScrewThrScaleB)
        self.sm3DPrintMode = False
        threadMode = FSParam.GetInt("ScrewToolbarThreadGeneration", 0)  # 0 = standard, 1 = 3dprint
        if threadMode == 1:
            self.sm3DPrintMode = True
        self.smNutThrScaleA = FSParam.GetFloat("NutThrScaleA", 1.03)
        self.smNutThrScaleB = FSParam.GetFloat("NutThrScaleB", 0.1)
        self.smScrewThrScaleA = FSParam.GetFloat("ScrewThrScaleA", 0.99)
        self.smScrewThrScaleB = FSParam.GetFloat("ScrewThrScaleB", -0.05)
        newState = str(self.sm3DPrintMode) + str(self.smNutThrScaleA) + str(self.smNutThrScaleB) + str(
            self.smScrewThrScaleA) + str(self.smScrewThrScaleB)
        if oldState != newState:
            FastenerBase.FSCacheRemoveThreaded()  # thread parameters have changed, remove cached ones

    def createFastener(self, type, diam, len, threadType, leftHanded, customPitch=None, customDia=None):
        return self.createScrew(type, diam, len, threadType, screwTables[type][FUNCTION_POS], leftHanded, customPitch, customDia)


ScrewMakerInstance = None


def Instance():
    global ScrewMakerInstance
    if ScrewMakerInstance is None:
        ScrewMakerInstance = FSScrewMaker()
    return ScrewMakerInstance

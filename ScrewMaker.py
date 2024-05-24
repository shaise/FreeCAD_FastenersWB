# -*- coding: utf-8 -*-

# A Wrapper to Ulrich's screw_maker macro
import FreeCAD
from screw_maker import Screw
from screw_maker import FsData
from FastenerBase import FsTitles
import FastenerBase
from FastenerBase import FSParam
from FSAliases import FSGetTypeAlias, FSAppendAliasesToTable

import math

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
    ("1.6 mm", 1.1),
    ("2 mm", 1.4),
    ("2.5 mm", 1.7),
    ("3 mm", 2.1),
    ("3.5 mm", 2.4),
    ("4 mm", 2.8),
    ("4.5 mm", 3.1),
    ("5 mm", 3.5),
    ("5.5 mm", 3.8),
    ("6 mm", 4.2),
    ("7 mm", 4.9),
    ("8 mm", 5.6),
    ("10 mm", 7),
    ("12 mm", 9),
    ("16 mm", 12),
    ("20 mm", 15)
)

FSC_ISO1478_ScrewHoleChart = (
    ("ST1.5", 0.91),
    ("ST1.9", 1.24),
    ("ST2.2", 1.63),
    ("ST2.6", 1.9),
    ("ST2.9", 2.18),
    ("ST3.3", 2.39),
    ("ST3.5", 2.64),
    ("ST3.9", 2.92),
    ("ST4.2", 3.1),
    ("ST4.8", 3.58),
    ("ST5.5", 4.17),
    ("ST6.3", 4.88),
    ("ST8", 6.2),
    ("ST9.5", 7.85)
)

# prepare a dictionary for fast search of GetInnerThread
FSCScrewHoleChartDict = {}
for s in FSCScrewHoleChart:
    FSCScrewHoleChartDict[s[0]] = s[1]
for s in FSC_Inch_ScrewHoleChart:
    FSCScrewHoleChartDict[s[0]] = s[1]
for s in FSC_DIN7998_ScrewHoleChart:
    FSCScrewHoleChartDict[s[0]] = s[1]
for s in FSC_ISO1478_ScrewHoleChart:
    FSCScrewHoleChartDict[s[0]] = s[1]


FASTENER_FAMILY_POS = 0
FUNCTION_POS = 1

screwTables = {
    #            name,    function
    "DIN933": ("Screw", "makeHexHeadBolt"),
    "DIN961": ("Screw", "makeHexHeadBolt"),
    "ISO4014": ("Screw", "makeHexHeadBolt"),
    "ISO4015": ("Screw", "makeReducedShankHexHeadBolt"),
    "ISO4016": ("Screw", "makeHexHeadBolt"),
    "ISO4017": ("Screw", "makeHexHeadBolt"),
    "ISO4018": ("Screw", "makeHexHeadBolt"),
    "ISO4162": ("Screw", "makeHexHeadWithFlange"),
    "ISO15071": ("Screw", "makeHexHeadWithFlange"),
    "ISO15072": ("Screw", "makeHexHeadWithFlange"),
    "ISO8676": ("Screw", "makeHexHeadBolt"),
    "ISO8765": ("Screw", "makeHexHeadBolt"),
    "EN1662": ("Screw", "makeHexHeadWithFlange"),
    "EN1665": ("Screw", "makeHexHeadWithFlange"),
    "ISO2009": ("Screw", "makeCountersunkHeadScrew"),
    "ISO2010": ("Screw", "makeRaisedCountersunkScrew"),
    "ISO4762": ("Screw", "makeCylinderHeadScrew"),
    "ISO10642": ("Screw", "makeCountersunkHeadScrew"),
    "ISO1207": ("Screw", "makeCheeseHeadScrew"),
    "DIN84": ("Screw", "makeCheeseHeadScrew"),
    "ISO1580": ("Screw", "makeCheeseHeadScrew"),
    "ISO7045": ("Screw", "makePanHeadScrew"),
    "ISO7046": ("Screw", "makeCountersunkHeadScrew"),
    "ISO7047": ("Screw", "makeRaisedCountersunkScrew"),
    "ISO7048": ("Screw", "makeCheeseHeadScrew"),
    "DIN967": ("Screw", "makeFlangedPanHeadScrew"),
    "ISO7379": ("Screw", "makeShoulderScrew"),
    "ISO7380-1": ("Screw", "makeButtonHeadScrew"),
    "ISO7380-2": ("Screw", "makeFlangedButtonHeadScrew"),
    "ISO14579": ("Screw", "makeCylinderHeadScrew"),
    "ISO14580": ("Screw", "makeCheeseHeadScrew"),
    "ISO14581": ("Screw", "makeCountersunkHeadScrew"),
    "ISO14582": ("Screw", "makeCountersunkHeadScrew"),
    "ISO14583": ("Screw", "makePanHeadScrew"),
    "ISO14584": ("Screw", "makeRaisedCountersunkScrew"),
    "DIN7984": ("Screw", "makeCylinderHeadScrew"),
    "DIN6912": ("Screw", "makeCylinderHeadScrew"),
    "DIN478": ("Screw", "makeFlangedSquareHeadBolt"),
    "DIN603": ("Screw", "makeCarriageBolt"),
    "ISO2342": ("Screw", "makeHeadlessScrew"),
    "DIN571": ("Screw", "makeWoodScrew"),
    "DIN96": ("Screw", "makeWoodScrew"),
    "DIN7996": ("Screw", "makeWoodScrew"),
    "GOST1144-1": ("Screw", "makeWoodScrew"),
    "GOST1144-2": ("Screw", "makeWoodScrew"),
    "GOST1144-3": ("Screw", "makeWoodScrew"),
    "GOST1144-4": ("Screw", "makeWoodScrew"),
    "ISO7049-C": ("Screw", "makeSelfTappingScrew"),
    "ISO7049-F": ("Screw", "makeSelfTappingScrew"),
    "ISO7049-R": ("Screw", "makeSelfTappingScrew"),
    "ISO7089": ("Washer", "makeWasher"),
    "ISO7090": ("Washer", "makeWasher"),
    "ISO7091": ("Washer", "makeWasher"),
    "ISO7092": ("Washer", "makeWasher"),
    "ISO7093-1": ("Washer", "makeWasher"),
    "ISO7094": ("Washer", "makeWasher"),
    "ISO8738": ("Washer", "makeWasher"),
    "DIN6319C": ("Washer", "makeSphericalWasher"),
    "DIN6319D": ("Washer", "makeSphericalWasher"),
    "DIN6319G": ("Washer", "makeSphericalWasher"),
    "DIN6340": ("Washer", "makeWasher"),
    "NFE27-619": ("Washer", "makeWasher"),
    "ISO4026": ("Screw", "makeSetScrew"),
    "ISO4027": ("Screw", "makeSetScrew"),
    "ISO4028": ("Screw", "makeSetScrew"),
    "ISO4029": ("Screw", "makeSetScrew"),
    "ISO4766": ("Screw", "makeSetScrew"),
    "ISO7434": ("Screw", "makeSetScrew"),
    "ISO7435": ("Screw", "makeSetScrew"),
    "ISO7436": ("Screw", "makeSetScrew"),
    "DIN464": ("Screw", "makeThumbScrew"),
    "DIN465": ("Screw", "makeThumbScrew"),
    "DIN653": ("Screw", "makeThumbScrew"),
    "ISO4032": ("Nut", "makeHexNut"),
    "ISO4033": ("Nut", "makeHexNut"),
    "ISO4034": ("Nut", "makeHexNut"),
    "ISO4035": ("Nut", "makeHexNut"),
    "ISO4161": ("Nut", "makeHexNutWFlange"),
    "ISO7040": ("Nut", "makeNylocNut"),
    "ISO7041": ("Nut", "makeNylocNut"),
    "ISO7043": ("Nut", "makeFlangedNylocNut"),
    "ISO7044": ("Nut", "makeAllMetalFlangedLockNut"),
    "ISO7719": ("Nut", "makeAllMetalLockNut"),
    "ISO7720": ("Nut", "makeAllMetalLockNut"),
    "ISO8673": ("Nut", "makeHexNut"),
    "ISO8674": ("Nut", "makeHexNut"),
    "ISO8675": ("Nut", "makeHexNut"),
    "ISO10511": ("Nut", "makeNylocNut"),
    "ISO10512": ("Nut", "makeNylocNut"),
    "ISO10513": ("Nut", "makeAllMetalLockNut"),
    "ISO10663": ("Nut", "makeHexNutWFlange"),
    "ISO12125": ("Nut", "makeFlangedNylocNut"),
    "ISO12126": ("Nut", "makeAllMetalFlangedLockNut"),
    "ISO21670": ("Nut", "makeWeldNut"),
    "DIN934": ("Nut", "makeHexNut"),
    "EN1661": ("Nut", "makeHexNutWFlange"),
    "DIN917": ("Nut", "makeThinCupNut"),
    "DIN1587": ("Nut", "makeCupNut"),
    "DIN6330": ("Nut", "makeHexNut"),
    "DIN6331": ("Nut", "makeHexNutWFlange"),
    "DIN6334": ("Nut", "makeHexNut"),
    "DIN7967": ("Nut", "makePalNut"),
    "GOST11860-1": ("Nut", "makeCupNut"),
    "DIN315": ("Nut", "makeWingNut"),
    "DIN557": ("Nut", "makeSquareNut"),
    "DIN562": ("Nut", "makeSquareNut"),
    "DIN928": ("Nut", "makeWeldNut"),
    "DIN929": ("Nut", "makeWeldNut"),
    "DIN935": ("Nut", "makeCastleNut"),
    "DIN985": ("Nut", "makeNylocNut"),
    "DIN508": ("TSlot", "makeTSlot"),
    "4PWTI": ("Nut", "makeTeeNut"),
    "GN505": ("TSlot", "makeTSlot"),
    "GN505.4": ("TSlot", "makeTSlot"),
    "GN506": ("TSlot", "makeTSlot"),
    "GN507": ("TSlot", "makeTSlot"),
    "ASMEB18.2.1.1": ("Screw", "makeSquareBolt"),
    "ASMEB18.2.1.6": ("Screw", "makeHexHeadBolt"),
    "ASMEB18.2.1.8": ("Screw", "makeHexHeadWithFlange"),
    "ASMEB18.2.2.1A": ("Nut", "makeHexNut"),
    "ASMEB18.2.2.1B": ("Nut", "makeSquareNut"),
    "ASMEB18.2.2.2": ("Nut", "makeSquareNut"),
    "ASMEB18.2.2.4A": ("Nut", "makeHexNut"),
    "ASMEB18.2.2.4B": ("Nut", "makeHexNut"),
    "ASMEB18.2.2.5": ("Nut", "makeCastleNut"),
    "ASMEB18.2.2.12": ("Nut", "makeHexNutWFlange"),
    "ASMEB18.2.2.13": ("Nut", "makeHexNut"),
    "ASMEB18.6.9A": ("Nut", "makeWingNut"),
    "SAEJ483a1": ("Nut", "makeCupNut"),
    "SAEJ483a2": ("Nut", "makeCupNut"),
    "ASMEB18.3.1A": ("Screw", "makeCylinderHeadScrew"),
    "ASMEB18.3.1G": ("Screw", "makeCylinderHeadScrew"),
    "ASMEB18.3.2": ("Screw", "makeCountersunkHeadScrew"),
    "ASMEB18.3.3A": ("Screw", "makeButtonHeadScrew"),
    "ASMEB18.3.3B": ("Screw", "makeFlangedButtonHeadScrew"),
    "ASMEB18.3.4": ("Screw", "makeShoulderScrew"),
    "ASMEB18.3.5A": ("Screw", "makeSetScrew"),
    "ASMEB18.3.5B": ("Screw", "makeSetScrew"),
    "ASMEB18.3.5C": ("Screw", "makeSetScrew"),
    "ASMEB18.3.5D": ("Screw", "makeSetScrew"),
    "ASMEB18.6.1.2": ("Screw", "makeWoodScrew"),
    "ASMEB18.6.1.3": ("Screw", "makeWoodScrew"),
    "ASMEB18.6.1.4": ("Screw", "makeWoodScrew"),
    "ASMEB18.6.1.5": ("Screw", "makeWoodScrew"),
    "ASMEB18.6.3.1A": ("Screw", "makeCountersunkHeadScrew"),
    "ASMEB18.6.3.1B": ("Screw", "makeCountersunkHeadScrew"),
    "ASMEB18.6.3.4A": ("Screw", "makeRaisedCountersunkScrew"),
    "ASMEB18.6.3.4B": ("Screw", "makeRaisedCountersunkScrew"),
    "ASMEB18.6.3.9A": ("Screw", "makePanHeadScrew"),
    "ASMEB18.6.3.9B": ("Screw", "makePanHeadScrew"),
    "ASMEB18.6.3.10A": ("Screw", "makePanHeadScrew"),
    "ASMEB18.6.3.10B": ("Screw", "makePanHeadScrew"),
    "ASMEB18.6.3.12A": ("Screw", "makePanHeadScrew"),
    "ASMEB18.6.3.12C": ("Screw", "makePanHeadScrew"),
    "ASMEB18.6.3.16A": ("Screw", "makeRoundHeadScrew"),
    "ASMEB18.6.3.16B": ("Screw", "makeRoundHeadScrew"),
    "ASMEB18.5.2": ("Screw", "makeCarriageBolt"),
    "ASMEB18.21.1.12A": ("Washer", "makeWasher"),
    "ASMEB18.21.1.12B": ("Washer", "makeWasher"),
    "ASMEB18.21.1.12C": ("Washer", "makeWasher"),
    "ScrewTap": ("ScrewTap", "makeScrewTap"),
    "ScrewTapInch": ("ScrewTap", "makeScrewTap"),
    "ScrewDie": ("ScrewDie", "makeScrewDie"),
    "ScrewDieInch": ("ScrewDie", "makeScrewDie"),
    "ThreadedRod": ("ThreadedRod", "makeThreadedRod"),
    "ThreadedRodInch": ("ThreadedRod", "makeThreadedRod"),
    "PEMPressNut": ("PressNut", "makePEMPressNut"),
    "PEMStandoff": ("Standoff", "makePEMStandoff"),
    "PEMStud": ("Stud", "makePEMStud"),
    "PCBStandoff": ("Standoff", "makePCBStandoff"),
    "PCBSpacer": ("Spacer", "makePCBSpacer"),
    "IUTHeatInsert": ("Insert", "makeHeatInsert"),
    "DIN471": ("RetainingRing", "makeExternalRetainingRing"),
    "DIN472": ("RetainingRing", "makeInternalRetainingRing"),
    "DIN6799": ("RetainingRing", "makeEClip"),
    "ISO2936": ("HexKey", "makeHexKey"),
    "DIN1143": ("Nail", "makeNail"),
    "DIN1144-A": ("Nail", "makeNail"),
    "DIN1151-A": ("Nail", "makeNail"),
    "DIN1151-B": ("Nail", "makeNail"),
    "DIN1152": ("Nail", "makeNail"),
    "DIN1160-A": ("Nail", "makeNail"),
    "DIN1160-B": ("Nail", "makeNail"),
    "ISO1234": ("Pin", "makeSplitPin"),
    "ISO2338": ("Pin", "makeDowelPin"),
    "ISO2339": ("Pin", "makeTaperedPin"),
    "ISO2340A": ("Pin", "makeHeadlessClevisPin"),
    "ISO2340B": ("Pin", "makeHeadlessClevisPin"),
    "ISO2341A": ("Pin", "makeClevisPin"),
    "ISO2341B": ("Pin", "makeClevisPin"),
    "ISO8733": ("Pin", "makeInternalThreadedDowelPin"),
    "ISO8734": ("Pin", "makeDowelPin"),
    "ISO8735": ("Pin", "makeInternalThreadedDowelPin"),
    "ISO8736": ("Pin", "makeInternalThreadedTaperPin"),
    "ISO8737": ("Pin", "makeExternalThreadedTaperPin"),
    "ISO8739": ("Pin", "makePilotedGroovedDowelPin"),
    "ISO8740": ("Pin", "makeGroovedParallelPin"),
    "ISO8741": ("Pin", "makeReverseTaperGroovedPin"),
    "ISO8742": ("Pin", "makeCenterGroovedPin"),
    "ISO8743": ("Pin", "makeCenterGroovedPin"),
    "ISO8744": ("Pin", "makeTaperGroovedPin"),
    "ISO8745": ("Pin", "makeTaperGroovedPin"),
    "ISO8746": ("Pin", "makeRoundHeadGroovedPin"),
    "ISO8747": ("Pin", "makeCskHeadGroovedPin"),
    "ISO8748": ("Pin", "makeCoiledSpringPin"),
    "ISO8750": ("Pin", "makeCoiledSpringPin"),
    "ISO8751": ("Pin", "makeCoiledSpringPin"),
    "ISO8752": ("Pin", "makeSlottedSpringPin"),
    "ISO13337": ("Pin", "makeSlottedSpringPin"),
    # * diam pos and K pos were moved from this table to the csv titles
}
FSAppendAliasesToTable(screwTables)


class FSScrewMaker(Screw):
    def __init__(self):
        super().__init__()

    def FindClosest(self, type, diam, len, width=None):
        """Find closest standard screw to given parameters"""
        if type not in screwTables:
            return diam, len, width

        diam_table = FsData[type + "def"]
        # auto find diameter
        if diam not in diam_table:
            origdia = FastenerBase.DiaStr2Num(diam)
            mindif = 1000.0
            for m in diam_table:
                diff = abs(FastenerBase.DiaStr2Num(m) - origdia)
                if diff < mindif:
                    mindif = diff
                    diam = m

        # auto find width, if applicable
        if width is not None:
            width_table = FsData[type + "width"][diam]
            if width not in width_table:
                origdiff = FastenerBase.LenStr2Num(width)
                mindif = 1000.0
                for w in width_table:
                    diff = abs(FastenerBase.LenStr2Num(w) - origdiff)
                    if diff < mindif:
                        mindif = diff
                        width = w

        # auto find length
        lens = self.GetAllLengths(type, diam, False, width)
        origlen = FastenerBase.LenStr2Num(len)
        mindif = 1000.0
        for l in lens:
            diff = abs(FastenerBase.LenStr2Num(l) - origlen)
            if diff < mindif:
                mindif = diff
                len = l

        return diam, len, width

    def AutoDiameter(self, type, holeObj, baseobj=None, matchOuter=False):
        """Calculate screw diameter automatically based on given hole"""
        # this function is also used to assign the default screw diameter
        if baseobj is not None and baseobj.Name.startswith("Washer"):
            matchOuter = True
        is_attached = (
            holeObj is not None and hasattr(holeObj, 'Curve') and
            hasattr(holeObj.Curve, 'Radius') and
            (type in screwTables)
        )
        is_retaining_ring = type in ["DIN471", "DIN472", "DIN6799"]
        if is_attached and not is_retaining_ring:
            d = holeObj.Curve.Radius * 2
            table = FsData[type + "def"]
            tablepos = self.GetTablePos(type, 'csh_diam')
            mindif = 100000.0
            dif = mindif
            for m in table:
                # FreeCAD.Console.PrintLog("Test M:" + m + "\n")
                if tablepos == -1:
                    if matchOuter:
                        dia = FastenerBase.DiaStr2Num(m) - 0.01
                        if d > dia:
                            dif = d - dia
                    else:
                        dia = self.GetInnerThread(m)
                        dif = math.fabs(dia - d)

                else:
                    dia = table[m][tablepos]
                    if d > dia:
                        dif = d - dia
                if dif < mindif:
                    mindif = dif
                    res = m
        elif is_attached and is_retaining_ring:
            d = holeObj.Curve.Radius * 2
            table = FsData[type + "def"]
            is_external_ring = type in ["DIN471", "DIN6799"]
            mindif = 100000.0
            dif = mindif
            tablepos = self.GetTablePos(type, 'groove_dia')
            if matchOuter ^ is_external_ring:
                # use the groove diameter
                for m in table:
                    dif = abs(table[m][tablepos] - d)
                    if dif < mindif:
                        mindif = dif
                        res = m
            else:
                # use the nominal shaft diameter
                for m in table:
                    if type != "DIN6799":
                        dia = float(m.split()[0])
                    else:
                        p1 = self.GetTablePos(type, "shaft_dia_min")
                        p2 = self.GetTablePos(type, "shaft_dia_max")
                        dia = table[m][p1] + 0.5*(table[m][p2] - table[m][p1])
                    dif = abs(dia - d)
                    if dif < mindif:
                        mindif = dif
                        res = m
        # when a new fastener is created. the following default values are
        # assigned depending on available diameters
        else:
            diams = self.GetAllDiams(type)
            if 'M6' in diams:
                res = 'M6'
            elif '1/4in' in diams:
                res = '1/4in'
            elif '#10' in diams:
                res = '#10'
            elif '6 mm' in diams:
                res = '6 mm'
            elif '25 mm' in diams:
                res = '25 mm'
            elif '10-14 mm' in diams:
                res = '10-14 mm'
            else:
                res = diams[0]
        return res

    def GetTypeName(self, type):
        if type not in screwTables:
            return "None"
        return screwTables[type][FASTENER_FAMILY_POS]

    def GetAllDiams(self, type):
        type = FSGetTypeAlias(type)
        return list(FsData[type + "def"].keys())

    def GetAllTcodes(self, type, diam):
        FSGetTypeAlias(type)
        tcodes = FsTitles[type + "tcodes"]
        tdata = FsData[type + "tcodes"][diam]
        res = []
        for i in range(len(tdata)):
            if tdata[i] != 0:
                res.append(tcodes[i])
        return res

    def GetAllSlotWidths(self, type, diam):
        type = FSGetTypeAlias(type)
        swidths = FsTitles[type + "slotwidths"]
        swdata = FsData[type + "slotwidths"][diam]
        res = []
        for i in range(len(swdata)):
            if swdata[i] != 0:
                res.append(swidths[i])
        return res

    def GetAllKeySizes(self, type, diam):
        FSGetTypeAlias(type)
        klengths = FsTitles[type + "keysizes"]
        ldata = FsData[type + "keysizes"][diam]
        res = []
        for i in range(len(ldata)):
            if ldata[i] != 0:
                res.append(klengths[i])
        return res

    def GetAllWidthcodes(self, type, diam):
        type = FSGetTypeAlias(type)
        widths = FsData[type + "width"][diam]
        return list(widths)

    def GetAllLengths(self, type, diam, addCustom=True, width=None):
        lenlist = []
        type = FSGetTypeAlias(type)
        rangeTableName = type + "range"
        if diam != "Auto":
            if width is not None:
                diam += "x" + width
            if rangeTableName in FsData:
                rangeTable = FsData[rangeTableName]
                if "all" in rangeTable:
                    lens = rangeTable["all"]
                else:
                    lens = FsData[type + "length"]
                range = rangeTable[diam]
                min = FastenerBase.LenStr2Num(range[0])
                max = FastenerBase.LenStr2Num(range[1])
                for len in lens:
                    l = FastenerBase.LenStr2Num(len)
                    if l >= min and l <= max:
                        lenlist.append(len)
            else:
                lens = FsData[type + "length"]
                lenlist = list(lens[diam])
            lenlist.sort(key=FastenerBase.LenStr2Num)
        if addCustom:
            lenlist.append("Custom")
        return lenlist

    def GetTablePos(self, type, name):
        titles = FsTitles[type + 'def']
        if name not in titles:
            return -1
        return titles.index(name)
    def GetTableProperty(self, type, diam, property, default_val):
        tablepos = self.GetTablePos(type, property)
        FreeCAD.Console.PrintLog("Found pos for " + property + ": " + str(tablepos) + "\n")
        if (tablepos < 0):
            return default_val
        table = FsData[type + "def"]
        FreeCAD.Console.PrintLog("Fetching value for diam: " + diam + "\n")
        return table[diam][tablepos]        

    def GetThreadLength(self, type, diam):
        return self.GetTableProperty(type, diam, 'thr_len', 10.0)

    def GetInnerThread(self, diam):
        diam = FastenerBase.cleanDiamStr(diam)
        if diam in FSCScrewHoleChartDict:
            return FSCScrewHoleChartDict[diam]
        return 0

    def GetAllCountersunkTypes(self):
        list = []
        for key in screwTables:
            if (
                screwTables[key][FASTENER_FAMILY_POS] == 'Screw' and
                self.GetTablePos(key, 'csh_diam') >= 0
            ):
                list.append(key)
        list.sort()
        return list

    def GetCountersunkDiams(self, type):
        dpos = self.GetTablePos(type, 'csh_diam')
        if dpos < 0:
            return None
        kpos = self.GetTablePos(type, 'csh_height')
        if kpos < 0:
            return None
        table = FsData[type + "def"]
        res = {}
        for diam in table:
            res[diam] = (table[diam][dpos], table[diam][kpos])
            FreeCAD.Console.PrintMessage(
                diam + ":" + str(res[diam][0]) + "," + str(res[diam][1])
            )
        return res

    def updateFastenerParameters(self):
        oldState = (
            str(self.sm3DPrintMode) +
            str(self.smNutThrScaleA) +
            str(self.smNutThrScaleB) +
            str(self.smScrewThrScaleA) +
            str(self.smScrewThrScaleB)
        )
        self.sm3DPrintMode = False
        # threading modes: 0 = standard, 1 = 3dprint
        threadMode = FSParam.GetInt("ScrewToolbarThreadGeneration", 0)
        if threadMode == 1:
            self.sm3DPrintMode = True
        self.smNutThrScaleA = FSParam.GetFloat("NutThrScaleA", 1.03)
        self.smNutThrScaleB = FSParam.GetFloat("NutThrScaleB", 0.1)
        self.smScrewThrScaleA = FSParam.GetFloat("ScrewThrScaleA", 0.99)
        self.smScrewThrScaleB = FSParam.GetFloat("ScrewThrScaleB", -0.05)
        newState = (
            str(self.sm3DPrintMode) +
            str(self.smNutThrScaleA) +
            str(self.smNutThrScaleB) +
            str(self.smScrewThrScaleA) +
            str(self.smScrewThrScaleB)
        )
        if oldState != newState:
            # thread parameters have changed, remove cached ones
            FastenerBase.FSCacheRemoveThreaded()

    def createFastener(self, fastenerAttribs):
        func = screwTables[fastenerAttribs.baseType][FUNCTION_POS]
        return self.createScrew(func, fastenerAttribs)


Instance = FSScrewMaker()

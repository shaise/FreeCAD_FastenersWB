# -*- coding: utf-8 -*-
###############################################################################
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
###############################################################################

from FreeCAD import Gui
import FreeCAD
import os
import re
from TranslateUtils import translate
import FastenerBase
from FastenerBase import FSParam
from FastenerBase import FSBaseObject
import ScrewMaker
from FSutils import iconPath

screwMaker = ScrewMaker.Instance

# These strings are required for fasteners translation in treeview.
# They are used by the pylupdate5 utility for update *.ts files. Don't delete them.
translate("FastenerCmdTreeView", "Screw")
translate("FastenerCmdTreeView", "Washer")
translate("FastenerCmdTreeView", "Nut")
translate("FastenerCmdTreeView", "ThreadedRod")
translate("FastenerCmdTreeView", "PressNut")
translate("FastenerCmdTreeView", "Standoff")
translate("FastenerCmdTreeView", "Spacer")
translate("FastenerCmdTreeView", "Stud")
translate("FastenerCmdTreeView", "ScrewTap")
translate("FastenerCmdTreeView", "ScrewDie")
translate("FastenerCmdTreeView", "Insert")
translate("FastenerCmdTreeView", "RetainingRing")

ScrewParameters = {"type", "diameter",
                   "matchOuter", "thread", "leftHanded", "length"}
ScrewParametersLC = {"type", "diameter", "matchOuter",
                     "thread", "leftHanded", "length", "lengthCustom"}
RodParameters = {"type", "diameter", "matchOuter", "thread",
                 "leftHanded", "lengthArbitrary",  "diameterCustom", "pitchCustom"}
NutParameters = {"type", "diameter", "matchOuter", "thread", "leftHanded"}
WasherParameters = {"type", "diameter", "matchOuter"}
PCBStandoffParameters = {"type", "diameter", "matchOuter", "thread",
                         "leftHanded", "threadLength", "lenByDiamAndWidth", "lengthCustom", "widthCode"}
PCBSpacerParameters = {"type", "diameter", "matchOuter", "thread",
                       "leftHanded", "lenByDiamAndWidth", "lengthCustom", "widthCode"}
PEMPressNutParameters = {"type", "diameter",
                         "matchOuter", "thread", "leftHanded", "thicknessCode"}
PEMStandoffParameters = {"type", "diameter", "matchOuter",
                         "thread", "leftHanded", "length", "blindness"}
RetainingRingParameters = {"type", "diameter", "matchOuter"}
TSlotNutParameters = { "type", "diameter", "matchOuter",
                        "thread", "leftHanded", "slotWidth" }
FastenerAttribs = ['type', 'diameter', 'thread', 'leftHanded', 'matchOuter', 'length', 'lengthCustom', 'width', 
                   'diameterCustom', 'pitchCustom', 'tcode', 'blind', 'screwLength', "slotW"]

# Names of fasteners groups translated once before FSScrewCommandTable created.
# For make FSScrewCommandTable more compact and readable
HexHeadGroup = translate("FastenerCmd", "Hex head")
HexagonSocketGroup = translate("FastenerCmd", "Hexagon socket")
HexalobularSocketGroup = translate("FastenerCmd", "Hexalobular socket")
SlottedGroup = translate("FastenerCmd", "Slotted")
HCrossGroup = translate("FastenerCmd", "H cross")
NutGroup = translate("FastenerCmd", "Nut")
WasherGroup = translate("FastenerCmd", "Washer")
OtherHeadGroup = translate("FastenerCmd", "Other head")
ThreadedRodGroup = translate("FastenerCmd", "ThreadedRod")
PEMInsertsGroup = translate("FastenerCmd", "PEM Inserts")
RetainingRingGroup = translate("FastenerCmd", "Retaining Rings")
TSlotGroup = translate("FastenerCmd", "T Slot")

CMD_HELP = 0
CMD_GROUP = 1
CMD_PARAMETER_GRP = 2
FSScrewCommandTable = {
    # type - (help, group, parameter-group)  
    "DIN933": (translate("FastenerCmd", "DIN 933 Hex head screw"), HexHeadGroup, ScrewParametersLC),
    "ISO4017": (translate("FastenerCmd", "ISO 4017 Hex head screw"), HexHeadGroup, ScrewParametersLC),
    "ISO4014": (translate("FastenerCmd", "ISO 4014 Hex head bolt"), HexHeadGroup, ScrewParametersLC),
    "EN1662": (translate("FastenerCmd", "EN 1662 Hexagon bolt with flange, small series"), HexHeadGroup, ScrewParametersLC),
    "EN1665": (translate("FastenerCmd", "EN 1665 Hexagon bolt with flange, heavy series"), HexHeadGroup, ScrewParametersLC),
    "DIN571": (translate("FastenerCmd", "DIN 571 Hex head wood screw"), HexHeadGroup, ScrewParametersLC),

    "ISO4762": (translate("FastenerCmd", "ISO4762 Hexagon socket head cap screw"), HexagonSocketGroup, ScrewParametersLC),
    "DIN7984": (translate("FastenerCmd", "DIN 7984 Hexagon socket head cap screws with low head"), HexagonSocketGroup, ScrewParametersLC),
    "DIN6912": (translate("FastenerCmd", "DIN 6912 Hexagon socket head cap screws with low head with centre"), HexagonSocketGroup, ScrewParametersLC),
    "ISO7380-1": (translate("FastenerCmd", "ISO 7380 Hexagon socket button head screw"), HexagonSocketGroup, ScrewParametersLC),
    "ISO7380-2": (translate("FastenerCmd", "ISO 7380 Hexagon socket button head screws with collar"), HexagonSocketGroup, ScrewParametersLC),
    "ISO10642": (translate("FastenerCmd", "ISO 10642 Hexagon socket countersunk head screw"), HexagonSocketGroup, ScrewParametersLC),
    "ISO7379": (translate("FastenerCmd", "ISO 7379 Hexagon socket head shoulder screw"), HexagonSocketGroup, ScrewParametersLC),
    "ISO4026": (translate("FastenerCmd", "ISO 4026 Hexagon socket set screws with flat point"), HexagonSocketGroup, ScrewParametersLC),
    "ISO4027": (translate("FastenerCmd", "ISO 4027 Hexagon socket set screws with cone point"), HexagonSocketGroup, ScrewParametersLC),
    "ISO4028": (translate("FastenerCmd", "ISO 4028 Hexagon socket set screws with dog point"), HexagonSocketGroup, ScrewParametersLC),
    "ISO4029": (translate("FastenerCmd", "ISO 4029 Hexagon socket set screws with cup point"), HexagonSocketGroup, ScrewParametersLC),

    "ISO14579": (translate("FastenerCmd", "ISO 14579 Hexalobular socket head cap screws"), HexalobularSocketGroup, ScrewParametersLC),
    "ISO14580": (translate("FastenerCmd", "ISO 14580 Hexalobular socket cheese head screws"), HexalobularSocketGroup, ScrewParametersLC),
    #    "ISO14581": (translate("FastenerCmd", "ISO 14581 Hexalobular socket countersunk flat head screws"), HexalobularSocketGroup, ScrewParametersLC),
    "ISO14582": (translate("FastenerCmd", "ISO 14582 Hexalobular socket countersunk head screws, high head"), HexalobularSocketGroup, ScrewParametersLC),
    "ISO14583": (translate("FastenerCmd", "ISO 14583 Hexalobular socket pan head screws"), HexalobularSocketGroup, ScrewParametersLC),
    "ISO14584": (translate("FastenerCmd", "ISO 14584 Hexalobular socket raised countersunk head screws"), HexalobularSocketGroup, ScrewParametersLC),

    "ISO2009": (translate("FastenerCmd", "ISO 2009 Slotted countersunk flat head screw"), SlottedGroup, ScrewParametersLC),
    "ISO2010": (translate("FastenerCmd", "ISO 2010 Slotted raised countersunk head screw"), SlottedGroup, ScrewParametersLC),
    "ISO1580": (translate("FastenerCmd", "ISO 1580 Slotted pan head screw"), SlottedGroup, ScrewParametersLC),
    "ISO1207": (translate("FastenerCmd", "ISO 1207 Slotted cheese head screw"), SlottedGroup, ScrewParametersLC),
    "DIN84": (translate("FastenerCmd", "DIN84 (superseded by ISO 1207) Slotted cheese head screw"), SlottedGroup, ScrewParametersLC),
    "DIN96":   (translate("FastenerCmd", "DIN 96 Slotted half round head wood screw"), SlottedGroup, ScrewParametersLC),
    "GOST1144-1": (translate("FastenerCmd", "GOST 1144 (Type 1) Half — round head wood screw"), SlottedGroup, ScrewParametersLC),
    "GOST1144-2": (translate("FastenerCmd", "GOST 1144 (Type 2) Half — round head wood screw"), SlottedGroup, ScrewParametersLC),

    "DIN967": (translate("FastenerCmd", "DIN 967 Cross recessed pan head screws with collar"), HCrossGroup, ScrewParametersLC),
    "ISO7045": (translate("FastenerCmd", "ISO 7045 Pan head screws type H cross recess"), HCrossGroup, ScrewParametersLC),
    "ISO7046": (translate("FastenerCmd", "ISO 7046 Countersunk flat head screws H cross r."), HCrossGroup, ScrewParametersLC),
    "ISO7047": (translate("FastenerCmd", "ISO 7047 Raised countersunk head screws H cross r."), HCrossGroup, ScrewParametersLC),
    "ISO7048": (translate("FastenerCmd", "ISO 7048 Cheese head screws with type H cross r."), HCrossGroup, ScrewParametersLC),
    "GOST1144-3": (translate("FastenerCmd", "GOST 1144 (Type 3) Half — round head wood screw"), HCrossGroup, ScrewParametersLC),
    "GOST1144-4": (translate("FastenerCmd", "GOST 1144 (Type 4) Half — round head wood screw"), HCrossGroup, ScrewParametersLC),

    "DIN603": (translate("FastenerCmd", "DIN 603 Mushroom head square neck bolts"), OtherHeadGroup, ScrewParametersLC),
    "DIN478": (translate("FastenerCmd", "DIN 478 Square head bolts with collar"), OtherHeadGroup, ScrewParametersLC),

    "ISO4032": (translate("FastenerCmd", "ISO 4032 Hexagon nuts, Style 1"), NutGroup, NutParameters),
    "ISO4033": (translate("FastenerCmd", "ISO 4033 Hexagon nuts, Style 2"), NutGroup, NutParameters),
    "ISO4035": (translate("FastenerCmd", "ISO 4035 Hexagon thin nuts, chamfered"), NutGroup, NutParameters),
    "DIN934": (translate("FastenerCmd", "DIN 934(superseded by ISO 4035 and ISO 8673) Hexagon thin nuts, chamfered"), NutGroup, NutParameters),
    #    "ISO4036": (translate("FastenerCmd", "ISO 4035 Hexagon thin nuts, unchamfered"), NutGroup, NutParameters),
    "EN1661": (translate("FastenerCmd", "EN 1661 Hexagon nuts with flange"), NutGroup, NutParameters),
    "DIN917": (translate("FastenerCmd", "DIN917 Cap nuts, thin style"), NutGroup, NutParameters),
    "DIN928": (translate("FastenerCmd", "DIN 928 square weld nuts"), NutGroup, NutParameters),
    "DIN929": (translate("FastenerCmd", "DIN 929 hexagonal weld nuts"), NutGroup, NutParameters),
    "DIN935": (translate("FastenerCmd", "DIN 935 Slotted / Castle nuts"), NutGroup, NutParameters),
    "DIN6334": (translate("FastenerCmd", "DIN 6334 elongated hexagon nuts"), NutGroup, NutParameters),
    "DIN7967": (translate("FastenerCmd", "DIN 7967 self locking counter nuts"), NutGroup, WasherParameters),
    "DIN1587": (translate("FastenerCmd", "DIN 1587 Cap nuts"), NutGroup, NutParameters),
    "GOST11860-1": (translate("FastenerCmd", "GOST 11860 (Type 1) Cap nuts"), NutGroup, NutParameters), 
    "DIN315": (translate("FastenerCmd", "DIN 315 wing nuts"), NutGroup, NutParameters),
    "DIN557": (translate("FastenerCmd", "DIN 557 Square nuts"), NutGroup, NutParameters),
    "DIN562": (translate("FastenerCmd", "DIN 562 Square nuts"), NutGroup, NutParameters),
    "DIN985": (translate("FastenerCmd", "DIN 985 Nyloc nuts"), NutGroup, NutParameters),
    "DIN1624": (translate("FastenerCmd", "DIN 1624 Tee nuts"), NutGroup, NutParameters),

    "DIN508": (translate("FastenerCmd", "DIN 508 T-Slot nuts"), TSlotGroup, TSlotNutParameters),
    "GN507": (translate("FastenerCmd", "GN 507 T-Slot nuts"), TSlotGroup, TSlotNutParameters),

    "ISO7089": (translate("FastenerCmd", "ISO 7089 Washer"), WasherGroup, WasherParameters),
    "ISO7090": (translate("FastenerCmd", "ISO 7090 Plain Washers, chamfered - Normal series"), WasherGroup, WasherParameters),
    #    "ISO7091": (translate("FastenerCmd", "ISO 7091 Plain washer - Normal series Product Grade C"), WasherGroup, WasherParameters),   # same as 7089??
    "ISO7092": (translate("FastenerCmd", "ISO 7092 Plain washers - Small series"), WasherGroup, WasherParameters),
    "ISO7093-1": (translate("FastenerCmd", "ISO 7093-1 Plain washers - Large series"), WasherGroup, WasherParameters),
    "ISO7094": (translate("FastenerCmd", "ISO 7094 Plain washers - Extra large series"), WasherGroup, WasherParameters),
    "NFE27-619": (translate("FastenerCmd", "NFE27-619 Countersunk washer"), WasherGroup, WasherParameters),

    # Inch

    "ASMEB18.2.1.1": (translate("FastenerCmd", "ASME B18.2.1 UNC Square bolts"), OtherHeadGroup, ScrewParametersLC),
    "ASMEB18.2.1.6": (translate("FastenerCmd", "ASME B18.2.1 UNC Hex head screws"), HexHeadGroup, ScrewParametersLC),
    "ASMEB18.2.1.8": (translate("FastenerCmd", "ASME B18.2.1 UNC Hex head screws with flange"), HexHeadGroup, ScrewParametersLC),

    "ASMEB18.3.1A": (translate("FastenerCmd", "ASME B18.3 UNC Hex socket head cap screws"), HexagonSocketGroup, ScrewParametersLC),
    "ASMEB18.3.1G": (translate("FastenerCmd", "ASME B18.3 UNC Hex socket head cap screws with low head"), HexagonSocketGroup, ScrewParametersLC),
    "ASMEB18.3.2": (translate("FastenerCmd", "ASME B18.3 UNC Hex socket countersunk head screws"), HexagonSocketGroup, ScrewParametersLC),
    "ASMEB18.3.3A": (translate("FastenerCmd", "ASME B18.3 UNC Hex socket button head screws"), HexagonSocketGroup, ScrewParametersLC),
    "ASMEB18.3.3B": (translate("FastenerCmd", "ASME B18.3 UNC Hex socket button head screws with flange"), HexagonSocketGroup, ScrewParametersLC),
    "ASMEB18.3.4": (translate("FastenerCmd", "ASME B18.3 UNC Hexagon socket head shoulder screws"), HexagonSocketGroup, ScrewParametersLC),
    "ASMEB18.3.5A": (translate("FastenerCmd", "ASME B18.3 UNC Hexagon socket set screws with flat point"), HexagonSocketGroup, ScrewParametersLC),
    "ASMEB18.3.5B": (translate("FastenerCmd", "ASME B18.3 UNC Hexagon socket set screws with cone point"), HexagonSocketGroup, ScrewParametersLC),
    "ASMEB18.3.5C": (translate("FastenerCmd", "ASME B18.3 UNC Hexagon socket set screws with dog point"), HexagonSocketGroup, ScrewParametersLC),
    "ASMEB18.3.5D": (translate("FastenerCmd", "ASME B18.3 UNC Hexagon socket set screws with cup point"), HexagonSocketGroup, ScrewParametersLC),

    "ASMEB18.6.3.1A": (translate("FastenerCmd", "ASME B18.6.3 UNC slotted countersunk flat head screws"), SlottedGroup, ScrewParametersLC),

    "ASMEB18.5.2": (translate("FastenerCmd", "ASME B18.5 UNC Round head square neck bolts"), OtherHeadGroup, ScrewParametersLC),

    "ASMEB18.2.2.1A": (translate("FastenerCmd", "ASME B18.2.2 UNC Hex Machine screw nuts"), NutGroup, NutParameters),
    "ASMEB18.2.2.1B": (translate("FastenerCmd", "ASME B18.2.2 UNC Square machine screw nuts"), NutGroup, NutParameters),
    "ASMEB18.2.2.2": (translate("FastenerCmd", "ASME B18.2.2 UNC Square nuts"), NutGroup, NutParameters),
    "ASMEB18.2.2.4A": (translate("FastenerCmd", "ASME B18.2.2 UNC Hexagon nuts"), NutGroup, NutParameters),
    "ASMEB18.2.2.4B": (translate("FastenerCmd", "ASME B18.2.2 UNC Hexagon thin nuts"), NutGroup, NutParameters),
    "ASMEB18.2.2.5": (translate("FastenerCmd", "ASME B18.2.2 UNC Hex slotted nuts"), NutGroup, NutParameters),
    "ASMEB18.2.2.12": (translate("FastenerCmd", "ASME B18.2.2 UNC Hex flange nuts"), NutGroup, NutParameters),
    "ASMEB18.2.2.13": (translate("FastenerCmd", "ASME B18.2.2 UNC Hex coupling nuts"), NutGroup, NutParameters),
    "ASMEB18.6.9A": (translate("FastenerCmd", "ASME B18.6.9 wing nuts, type A"), NutGroup, NutParameters),
    "SAEJ483a1": (translate("FastenerCmd", "SAE J483a low cap nuts"), NutGroup, NutParameters),
    "SAEJ483a2": (translate("FastenerCmd", "SAE J483a high cap nuts"), NutGroup, NutParameters),

    "ASMEB18.21.1.12A": (translate("FastenerCmd", "ASME B18.21.1 UN washers, narrow series"), WasherGroup, WasherParameters),
    "ASMEB18.21.1.12B": (translate("FastenerCmd", "ASME B18.21.1 UN washers, regular series"), WasherGroup, WasherParameters),
    "ASMEB18.21.1.12C": (translate("FastenerCmd", "ASME B18.21.1 UN washers, wide series"), WasherGroup, WasherParameters),

    "ScrewTap": (translate("FastenerCmd", "Metric threaded rod for tapping holes"), ThreadedRodGroup, RodParameters),
    "ScrewTapInch": (translate("FastenerCmd", "Inch threaded rod for tapping holes"), ThreadedRodGroup, RodParameters),
    "ScrewDie": (translate("FastenerCmd", "Tool object to cut external metric threads"), ThreadedRodGroup, RodParameters),
    "ScrewDieInch": (translate("FastenerCmd", "Tool object to cut external non-metric threads"), ThreadedRodGroup, RodParameters),
    "ThreadedRod": (translate("FastenerCmd", "DIN 975 metric threaded rod"), ThreadedRodGroup, RodParameters),
    "ThreadedRodInch": (translate("FastenerCmd", "UNC threaded rod"), ThreadedRodGroup, RodParameters),
    "PEMPressNut": (translate("FastenerCmd", "PEM Self Clinching nut"), PEMInsertsGroup, PEMPressNutParameters),
    "PEMStandoff": (translate("FastenerCmd", "PEM Self Clinching standoff"), PEMInsertsGroup, PEMStandoffParameters),
    "PEMStud": (translate("FastenerCmd", "PEM Self Clinching stud"), PEMInsertsGroup, ScrewParameters),
    "PCBStandoff": (translate("FastenerCmd", "Wurth WA-SSTII  PCB standoff"), PEMInsertsGroup, PCBStandoffParameters),
    "PCBSpacer": (translate("FastenerCmd", "Wurth WA-SSTII PCB spacer"), PEMInsertsGroup, PCBSpacerParameters),
    "IUTHeatInsert": (translate("FastenerCmd", "IUT[A/B/C] Heat Staked Metric Insert"), PEMInsertsGroup, NutParameters),

    "DIN471": (translate("FastenerCmd", "Metric external retaining rings"), RetainingRingGroup, RetainingRingParameters),
    "DIN472": (translate("FastenerCmd", "Metric internal retaining rings"), RetainingRingGroup, RetainingRingParameters),
    "DIN6799": (translate("FastenerCmd", "Metric E-clip retaining rings"), RetainingRingGroup, RetainingRingParameters),
}


def GetParams(type):
    if type not in FSScrewCommandTable:
        return {}
    return FSScrewCommandTable[type][CMD_PARAMETER_GRP]


class FSScrewObject(FSBaseObject):
    def __init__(self, obj, type, attachTo):
        '''"Add screw type fastener" '''
        super().__init__(obj, attachTo)
        # FreeCAD.Console.PrintMessage("Added: " + type + "\n")
        # self.Proxy = obj.Name
        self.VerifyMissingAttrs(obj, type)
        obj.Proxy = self

    def inswap(self, inpstr):
        if '″' in inpstr:
            return inpstr.replace('″', 'in')
        else:
            return inpstr

    def InitBackupAttribs(self):
        for attr in FastenerAttribs:
            if not hasattr(self, 'attr'):
                setattr(self, attr, None)

        # calculated attribs
        self.familyType = ""
        self.calc_diam = None
        self.calc_pitch = None
        self.calc_len = None

        # some extra params
        self.dimTable = None

    def BackupObject(self, obj):
        for attr in FastenerAttribs:
            if hasattr(obj, attr):
                val = getattr(obj, attr)
                valtype = val.__class__.__name__
                if valtype in ("str", "bool", "int", "float"):
                    setattr(self, attr, val)
                else:
                    setattr(self, attr, str(val))

    # get a hash key for the fastener attribs (for cashing similar objects)
    def GetKey(self):
        key = ""
        for attr in FastenerAttribs:
            val = getattr(self, attr)
            if val is not None:
                key += attr + ":" + str(val) + "|"
        return key.rstrip("|")

    def VerifyMissingAttrs(self, obj, type=None):
        self.updateProps(obj)
        # the backup attribs holds a copy of the object attribs. It is used to detect which attrib was
        # changed when executing the command. It should hold all possible object attribs. Unused ones will be None
        self.InitBackupAttribs()

        # basic parameters
        # all objects must have type - since they all use the same command
        if not hasattr(obj, "type"):
            if type is None:  # probably pre V0.4.0 object
                if hasattr(self, "originalType"):
                    type = self.originalType
                    FreeCAD.Console.PrintMessage(
                        "using original type: " + type + "\n")
            obj.addProperty("App::PropertyEnumeration", "type", "Parameters", translate(
                "FastenerCmd", "Screw type")).type = self.GetCompatibleTypes(type)
            obj.type = type
        else:
            type = obj.type

        if obj.type == "ISO7380":
            # backward compatibility - remove at FreeCAD version 0.23
            obj.type = type = "ISO7380-1"
        self.familyType = screwMaker.GetTypeName(type)

        if not hasattr(obj, "diameter"):
            diameters = screwMaker.GetAllDiams(type)
            diameters.insert(0, 'Auto')
            if "diameterCustom" in GetParams(type):
                diameters.append("Custom")
            obj.addProperty("App::PropertyEnumeration", "diameter", "Parameters", translate(
                "FastenerCmd", "Standard diameter")).diameter = diameters
            diameter = diameters[1]
        else:
            diameter = obj.diameter
        params = GetParams(type)

        # thread parameters
        if "thread" in params and not hasattr(obj, "thread"):
            obj.addProperty("App::PropertyBool", "thread", "Parameters", translate(
                "FastenerCmd", "Generate real thread")).thread = False
        if "leftHanded" in params and not hasattr(obj, 'leftHanded'):
            obj.addProperty("App::PropertyBool", "leftHanded", "Parameters", translate(
                "FastenerCmd", "Left handed thread")).leftHanded = False
        if "matchOuter" in params and not hasattr(obj, "matchOuter"):
            obj.addProperty("App::PropertyBool", "matchOuter", "Parameters", translate(
                "FastenerCmd", "Match outer thread diameter")).matchOuter = FSParam.GetBool("MatchOuterDiameter")

        # width parameters
        if "widthCode" in params and not hasattr(obj, "width"):
            obj.addProperty("App::PropertyEnumeration", "width", "Parameters", translate(
                "FastenerCmd", "Body width code")).width = screwMaker.GetAllWidthcodes(type, diameter)

        # length parameters
        addCustomLen = "lengthCustom" in params and not hasattr(
            obj, "lengthCustom")
        if "length" in params or "lenByDiamAndWidth" in params:
            # if diameter == "Auto":
            #     diameter = self.initialDiameter
            if "lenByDiamAndWidth" in params:
                slens = screwMaker.GetAllLengths(
                    type, diameter, addCustomLen, obj.width)
            else:
                slens = screwMaker.GetAllLengths(type, diameter, addCustomLen)
            if not hasattr(obj, 'length'):
                obj.addProperty("App::PropertyEnumeration", "length", "Parameters", translate(
                    "FastenerCmd", "Screw length")).length = slens
            elif addCustomLen:
                origLen = obj.length
                obj.length = slens
                if origLen in slens:
                    obj.length = origLen
            if addCustomLen:
                obj.addProperty("App::PropertyLength", "lengthCustom", "Parameters", translate(
                    "FastenerCmd", "Custom length")).lengthCustom = self.inswap(slens[0])

        # custom size parameters
        if "lengthArbitrary" in params and not hasattr(obj, "length"):
            obj.addProperty("App::PropertyLength", "length", "Parameters", translate(
                "FastenerCmd", "Screw length")).length = 20.0
        if "diameterCustom" in params and not hasattr(obj, "diameterCustom"):
            obj.addProperty("App::PropertyLength", "diameterCustom", "Parameters", translate(
                "FastenerCmd", "Screw major diameter custom")).diameterCustom = 6
        if "pitchCustom" in params and not hasattr(obj, "pitchCustom"):
            obj.addProperty("App::PropertyLength", "pitchCustom", "Parameters", translate(
                "FastenerCmd", "Screw pitch custom")).pitchCustom = 1.0

        # thickness
        if "thicknessCode" in params and not hasattr(obj, "tcode"):
            obj.addProperty("App::PropertyEnumeration", "tcode", "Parameters", translate(
                "FastenerCmd", "Thickness code")).tcode = screwMaker.GetAllTcodes(type, diameter)

        # slot width
        if "slotWidth" in params and not hasattr(obj, "slotW"):
            obj.addProperty("App::PropertyLength", "slotW", "Parameters", translate("FastenerCmd", "Slot width")).slotW = 6.0

        # misc
        if "blindness" in params and not hasattr(obj, "blind"):
            obj.addProperty("App::PropertyBool", "blind", "Parameters", translate(
                "FastenerCmd", "Blind Standoff type")).blind = False
        if "threadLength" in params and not hasattr(obj, "screwLength"):
            obj.addProperty("App::PropertyLength", "screwLength", "Parameters", translate(
                "FastenerCmd", "Threaded part length")).screwLength = screwMaker.GetThreadLength(type, diameter)

        self.BackupObject(obj)
        # for attr in FastenerAttribs:
        #     atval = getattr(self, attr)
        #     if atval is not None:
        #         FreeCAD.Console.PrintMessage(attr + "(" + atval.__class__.__name__ + ") = " + str(atval) + "\n")

    # get all fastener types compatible with given one (that uses same properties)
    def GetCompatibleTypes(self, ftype):
        pargrp = GetParams(ftype)
        types = []
        for ftype2 in FSScrewCommandTable:
            if GetParams(ftype2) is pargrp:
                types.append(ftype2)
        types.sort()
        return types

    def onDocumentRestored(self, obj):
        # for backward compatibility: add missing attribute if needed
        self.VerifyMissingAttrs(obj)

    def CleanDecimals(self, val):
        val = str(val)
        if len(re.findall("[.]\d*$", val)) > 0:
            return val.rstrip('0').rstrip('.')
        return val

    def ActiveLength(self, obj):
        if not hasattr(obj, 'length'):
            return '0'
        if type(obj.length) != type(""):
            return self.CleanDecimals(float(obj.length))
        if obj.length == 'Custom':
            return self.CleanDecimals(float(obj.lengthCustom))
        return obj.length

    def paramChanged(self, param, value):
        return getattr(self, param) != value

    def execute(self, fp):
        '''"Print a short message when doing a recomputation, this method is mandatory" '''

        try:
            baseobj = fp.baseObject[0]
            shape = baseobj.Shape.getElement(fp.baseObject[1][0])
        except:
            baseobj = None
            shape = None

        # for backward compatibility: add missing attribute if needed
        # self.VerifyMissingAttrs(fp, fp.diameter)

        # FreeCAD.Console.PrintLog("MatchOuter:" + str(fp.matchOuter) + "\n")
        params = GetParams(fp.type)

        # handle type changes
        typechange = False
        if fp.type != self.type:
            typechange = True
            curdiam = fp.diameter
            diameters = screwMaker.GetAllDiams(fp.type)
            diameters.insert(0, 'Auto')
            if "diameterCustom" in params:
                diameters.append("Custom")

            if not (curdiam in diameters):
                curdiam = 'Auto'
            fp.diameter = diameters
            fp.diameter = curdiam

        # handle diameter changes
        if self.pitchCustom is not None and hasattr(fp, "pitchCustom") and str(fp.pitchCustom) != self.pitchCustom:
            fp.diameter = 'Custom'
        diameterchange = self.diameter != fp.diameter
        matchouterchange = self.matchOuter != fp.matchOuter
        widthchange = hasattr(fp, "width") and self.width != fp.width

        if fp.diameter == 'Auto' or matchouterchange:
            self.calc_diam = screwMaker.AutoDiameter(
                fp.type, shape, baseobj, fp.matchOuter)
            fp.diameter = self.calc_diam
            diameterchange = True
        elif fp.diameter == 'Custom' and hasattr(fp, "diameterCustom"):
            self.calc_diam = str(fp.diameterCustom.Value)
        else:
            self.calc_diam = fp.diameter

        # handle length changes
        if hasattr(fp, 'length'):
            if "lengthArbitrary" in params:
                # arbitrary lengths
                l = fp.length.Value
                if l < 2.0:
                    l = 2.0
                    fp.length = 2.0
                self.calc_len = str(l)
            else:
                # fixed lengths
                width = None
                if "lenByDiamAndWidth" in params:
                    width = fp.width
                if self.paramChanged('length', fp.length):
                    if fp.length != 'Custom' and hasattr(fp, 'lengthCustom'):
                        fp.lengthCustom = FastenerBase.LenStr2Num(
                            fp.length)  # ***
                elif self.lengthCustom is not None and str(fp.lengthCustom) != self.lengthCustom:
                    fp.length = 'Custom'
                origLen = self.ActiveLength(fp)
                origIsCustom = fp.length == 'Custom'
                self.calc_diam, l, auto_width = screwMaker.FindClosest(
                    fp.type, self.calc_diam, origLen, width)
                if self.calc_diam != fp.diameter:
                    diameterchange = True
                    fp.diameter = self.calc_diam
                if width != auto_width:
                    widthchange = True
                    fp.width = screwMaker.GetAllWidthcodes(
                        fp.type, fp.diameter)
                    fp.width = width = auto_width

                if origIsCustom:
                    l = origLen

                if l != origLen or diameterchange or typechange or widthchange:
                    if diameterchange or typechange or widthchange:
                        fp.length = screwMaker.GetAllLengths(
                            fp.type, fp.diameter, hasattr(fp, 'lengthCustom'), width)
                        if hasattr(fp, 'screwLength'):
                            fp.screwLength = screwMaker.GetThreadLength(
                                fp.type, fp.diameter)
                    if origIsCustom:
                        fp.length = 'Custom'
                    else:
                        fp.length = l
                        if hasattr(fp, 'lengthCustom'):
                            fp.lengthCustom = FastenerBase.LenStr2Num(l)
                self.calc_len = l
        else:
            self.calc_len = None

        if diameterchange and "thicknessCode" in params:
            tcodes = screwMaker.GetAllTcodes(fp.type, fp.diameter)
            oldcode = fp.tcode
            fp.tcode = tcodes
            if oldcode in tcodes:
                fp.tcode = oldcode

        if fp.diameter == 'Custom' and hasattr(fp, "pitchCustom"):
            self.calc_pitch = fp.pitchCustom.Value
        else:
            self.calc_pitch = None

        screwMaker.updateFastenerParameters()

        self.BackupObject(fp)

        # Here we are generating a new key if is not present in cache. This key is also used in method
        # FastenerBase.FSCacheRemoveThreaded. This way it will allow to correctly recompute
        # the threaded screws and nuts in case of changing the 3D Printing settings in Fasteners Workbench.
        (key, s) = FastenerBase.FSGetKey(self.GetKey())
        if s is None:
            s = screwMaker.createFastener(self)
            FastenerBase.FSCache[key] = s
        else:
            FreeCAD.Console.PrintLog("Using cached object\n")

        # Formation of fastener name: DxLxH(LH)-Type
        dispDiam = self.CleanDecimals(self.calc_diam)
        label = dispDiam
        if hasattr(fp, 'length'):
            dispLen = self.ActiveLength(fp)
            label += 'x' + dispLen
            if hasattr(fp, 'width'):
                dispWidth = 'x' + fp.width
                label += 'x' + dispWidth
        if hasattr(fp, 'leftHanded'):
            if self.leftHanded:
                label += 'LH'
        # Add translated name of fastener type
        selfFamilyType = translate("FastenerCmdTreeView", self.familyType)
        label += '-' + selfFamilyType
        # Set completed label
        fp.Label = label

        # self.familyType = s[1]
        fp.Shape = s

        if shape is not None:
            # feature = FreeCAD.ActiveDocument.getObject(self.Proxy)
            # fp.Placement = FreeCAD.Placement() # reset placement
            FastenerBase.FSMoveToObject(fp, shape, fp.invert, fp.offset.Value)


class FSViewProviderTree:
    "A View provider for custom icon"

    def __init__(self, obj):
        obj.Proxy = self
        self.Object = obj.Object

    def attach(self, obj):
        self.Object = obj.Object
        return

    def updateData(self, fp, prop):
        return

    def getDisplayModes(self, obj):
        modes = []
        return modes

    def setDisplayMode(self, mode):
        return mode

    def onChanged(self, vp, prop):
        return

    def __getstate__(self):
        #        return {'ObjectName' : self.Object.Name}
        return None

    def __setstate__(self, state):
        if state is not None:
            import FreeCAD
            doc = FreeCAD.ActiveDocument  # crap
            self.Object = doc.getObject(state['ObjectName'])

    def getIcon(self):
        if hasattr(self.Object, "type"):
            return os.path.join(iconPath, self.Object.type + '.svg')
        elif hasattr(self.Object.Proxy, "type"):
            return os.path.join(iconPath, self.Object.Proxy.type + '.svg')
        # default to ISO4017.svg
        return os.path.join(iconPath, 'ISO4017.svg')


class FSScrewCommand:
    """Add Screw command"""

    def __init__(self, type, help):
        self.Type = type
        self.Help = help
        self.TypeName = screwMaker.GetTypeName(type)

    def GetResources(self):
        import GrammaticalTools
        
        icon = os.path.join(iconPath, self.Type + '.svg')
        return {'Pixmap': icon,
                # the name of a svg file available in the resources
                'MenuText': translate("FastenerCmd", "Add ") + GrammaticalTools.ToDativeCase(self.Help),
                'ToolTip': self.Help}

    def Activated(self):
        for selObj in FastenerBase.FSGetAttachableSelections():
            a = FreeCAD.ActiveDocument.addObject("Part::FeaturePython",
                                                 self.TypeName)
            FSScrewObject(a, self.Type, selObj)
            a.Label = a.Proxy.familyType
            FSViewProviderTree(a.ViewObject)
        FreeCAD.ActiveDocument.recompute()
        return

    def IsActive(self):
        return Gui.ActiveDocument is not None


def FSAddScrewCommand(type):
    cmd = 'FS' + type
    Gui.addCommand(cmd, FSScrewCommand(
        type, FSScrewCommandTable[type][CMD_HELP]))
    FastenerBase.FSCommands.append(
        cmd, "screws", FSScrewCommandTable[type][CMD_GROUP])


# generate all commands
for key in FSScrewCommandTable:
    FSAddScrewCommand(key)

# for backward compatibility, add old objects as derivative of FSScrewObject


class FSWasherObject(FSScrewObject):
    pass


class FSScrewRodObject(FSScrewObject):
    def onDocumentRestored(self, obj):
        self.originalType = obj.Proxy.type
        super().onDocumentRestored(obj)


class FSScrewDieObject(FSScrewObject):
    def onDocumentRestored(self, obj):
        self.originalType = obj.Proxy.type
        super().onDocumentRestored(obj)


class FSThreadedRodObject(FSScrewObject):
    def onDocumentRestored(self, obj):
        self.originalType = obj.Proxy.type
        super().onDocumentRestored(obj)


# add fastener types
FastenerBase.FSAddFastenerType("Screw")
FastenerBase.FSAddFastenerType("Washer", False)
FastenerBase.FSAddFastenerType("Nut", False)
FastenerBase.FSAddFastenerType("ThreadedRod", True, False)
FastenerBase.FSAddFastenerType("PressNut", False)
FastenerBase.FSAddFastenerType("Standoff")
FastenerBase.FSAddFastenerType("Stud")
FastenerBase.FSAddFastenerType("HeatSet", False)
FastenerBase.FSAddFastenerType("RetainingRing", False)
for item in ScrewMaker.screwTables:
    FastenerBase.FSAddItemsToType(ScrewMaker.screwTables[item][0], item)

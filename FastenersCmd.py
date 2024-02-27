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
from FSAliases import FSGetIconAlias, FSGetTypeAlias

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
translate("FastenerCmdTreeView", "T-Slot")
translate("FastenerCmdTreeView", "SetScrew")
translate("FastenerCmdTreeView", "HexKey")
translate("FastenerCmdTreeView", "Nail")
translate("FastenerCmdTreeView", "Pin")

ScrewParameters = {"type", "diameter",
                   "matchOuter", "thread", "leftHanded", "length"}
ScrewParametersLC = {"type", "diameter", "matchOuter",
                     "thread", "leftHanded", "length", "lengthCustom"}
RodParameters = {"type", "diameter", "matchOuter", "thread",
                 "leftHanded", "lengthArbitrary",  "diameterCustom", "pitchCustom"}
NutParameters = {"type", "diameter", "matchOuter", "thread", "leftHanded"}
WoodInsertParameters = {"type", "diameter", "matchOuter", "thread", "leftHanded"}
HeatInsertParameters = {"type", "diameter", "lengthArbitrary", "externalDiam", "matchOuter", "thread", "leftHanded"}
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
PinParameters = {"type", "diameter", "length", "lengthCustom", "leftHanded", "thread"}
TSlotNutParameters = { "type", "diameter", "matchOuter",
                        "thread", "leftHanded", "slotWidth" }
TSlotBoltParameters = { "type", "diameter", "length", "lengthCustom",
                       "matchOuter", "thread", "leftHanded", "slotWidth" }
HexKeyParameters = { "type", "diameter", "matchOuter", "keySize" }
NailParameters = { "type", "diameter", "matchOuter", }
# this is a list of all possible fastener attribs
FastenerAttribs = ['type', 'diameter', 'thread', 'leftHanded', 'matchOuter', 'length',
                   'lengthCustom', 'width', 'diameterCustom', 'pitchCustom', 'tcode',
                   'blind', 'screwLength', "slotWidth", 'externalDiam', 'keySize']


def tr_cmd(text):
    return translate("FastenerCmd", text)

# Names of fasteners groups translated once before FSScrewCommandTable created.
# For make FSScrewCommandTable more compact and readable
HexHeadGroup = tr_cmd("Hex head")
HexagonSocketGroup = tr_cmd("Hexagon socket")
HexalobularSocketGroup = tr_cmd("Hexalobular socket")
SlottedGroup = tr_cmd("Slotted")
HCrossGroup = tr_cmd("H cross")
NutGroup = tr_cmd("Nut")
WasherGroup = tr_cmd("Washer")
OtherHeadGroup = tr_cmd("Misc head")
ThreadedRodGroup = tr_cmd("ThreadedRod")
InsertGroup = tr_cmd("Inserts")
RetainingRingGroup = tr_cmd("Retaining Rings")
TSlotGroup = tr_cmd("T-Slot Fasteners")
SetScrewGroup = tr_cmd("Set screws")
NailGroup = tr_cmd("Nails")
PinGroup = tr_cmd("Pins")

CMD_HELP = 0
CMD_GROUP = 1
CMD_PARAMETER_GRP = 2
CMD_STD_GROUP = 3

FSScrewCommandTable = {
    # type - (help, group, parameter-group, standard-group)

    # HexHeadGroup

    "ASMEB18.2.1.1": (tr_cmd("UNC Square bolts"), OtherHeadGroup, ScrewParametersLC),
    "ASMEB18.2.1.6": (tr_cmd("UNC Hex head screws"), HexHeadGroup, ScrewParametersLC),
    "ASMEB18.2.1.8": (tr_cmd("UNC Hex head screws with flange"), HexHeadGroup, ScrewParametersLC),
    "DIN571": (tr_cmd("Hex head wood screw"), HexHeadGroup, ScrewParametersLC),
    "DIN933": (tr_cmd("Hex head screw"), HexHeadGroup, ScrewParametersLC),
    "DIN961": (tr_cmd("Hex head screw"), HexHeadGroup, ScrewParametersLC),
    "EN1662": (tr_cmd("Hexagon bolt with flange, small series"), HexHeadGroup, ScrewParametersLC),
    "EN1665": (tr_cmd("Hexagon bolt with flange, heavy series"), HexHeadGroup, ScrewParametersLC),
    "ISO4014": (tr_cmd("Hex head bolt - Product grades A and B"), HexHeadGroup, ScrewParametersLC),
    "ISO4015": (tr_cmd("Hexagon head bolts with reduced shank"), HexHeadGroup, ScrewParametersLC),
    "ISO4016": (tr_cmd("Hex head bolts - Product grade C"), HexHeadGroup, ScrewParametersLC),
    "ISO4017": (tr_cmd("Hex head screw - Product grades A and B"), HexHeadGroup, ScrewParametersLC),
    "ISO4018": (tr_cmd("Hex head screws - Product grade C"), HexHeadGroup, ScrewParametersLC),
    "ISO4162": (tr_cmd("Hexagon bolts with flange - Small series - Product grade A with driving feature of product grade B"), HexHeadGroup, ScrewParametersLC),
    "ISO8676": (tr_cmd("Hex head screws with fine pitch thread"), HexHeadGroup, ScrewParametersLC),
    "ISO8765": (tr_cmd("Hex head bolt with fine pitch thread"), HexHeadGroup, ScrewParametersLC),
    "ISO15071": (tr_cmd("Hexagon bolts with flange - Small series - Product grade A"), HexHeadGroup, ScrewParametersLC),
    "ISO15072": (tr_cmd("Hexagon bolts with flange with fine pitch thread - Small series - Product grade A"), HexHeadGroup, ScrewParametersLC),

    # HexagonSocketGroup

    "ASMEB18.3.1A": (tr_cmd("UNC Hex socket head cap screws"), HexagonSocketGroup, ScrewParametersLC),
    "ASMEB18.3.1G": (tr_cmd("UNC Hex socket head cap screws with low head"), HexagonSocketGroup, ScrewParametersLC),
    "ASMEB18.3.2": (tr_cmd("UNC Hex socket countersunk head screws"), HexagonSocketGroup, ScrewParametersLC),
    "ASMEB18.3.3A": (tr_cmd("UNC Hex socket button head screws"), HexagonSocketGroup, ScrewParametersLC),
    "ASMEB18.3.3B": (tr_cmd("UNC Hex socket button head screws with flange"), HexagonSocketGroup, ScrewParametersLC),
    "ASMEB18.3.4": (tr_cmd("UNC Hexagon socket head shoulder screws"), HexagonSocketGroup, ScrewParametersLC),
    "DIN6912": (tr_cmd("Hexagon socket head cap screws with low head with centre"), HexagonSocketGroup, ScrewParametersLC),
    "DIN7984": (tr_cmd("Hexagon socket head cap screws with low head"), HexagonSocketGroup, ScrewParametersLC),
    "ISO2936": (tr_cmd("Hexagon socket screw keys"), HexagonSocketGroup, HexKeyParameters),
    "ISO4762": (tr_cmd("Hexagon socket head cap screw"), HexagonSocketGroup, ScrewParametersLC),
    "ISO7379": (tr_cmd("Hexagon socket head shoulder screw"), HexagonSocketGroup, ScrewParametersLC),
    "ISO7380-1": (tr_cmd("Hexagon socket button head screw"), HexagonSocketGroup, ScrewParametersLC),
    "ISO7380-2": (tr_cmd("Hexagon socket button head screws with collar"), HexagonSocketGroup, ScrewParametersLC),
    "ISO10642": (tr_cmd("Hexagon socket countersunk head screw"), HexagonSocketGroup, ScrewParametersLC),

    # HexalobularSocketGroup

    "ISO14579": (tr_cmd("Hexalobular socket head cap screws"), HexalobularSocketGroup, ScrewParametersLC),
    "ISO14580": (tr_cmd("Hexalobular socket cheese head screws"), HexalobularSocketGroup, ScrewParametersLC),
    # "ISO14581": (tr_cmd("Hexalobular socket countersunk flat head screws"), HexalobularSocketGroup, ScrewParametersLC),
    "ISO14582": (tr_cmd("Hexalobular socket countersunk head screws, high head"), HexalobularSocketGroup, ScrewParametersLC),
    "ISO14583": (tr_cmd("Hexalobular socket pan head screws"), HexalobularSocketGroup, ScrewParametersLC),
    "ISO14584": (tr_cmd("Hexalobular socket raised countersunk head screws"), HexalobularSocketGroup, ScrewParametersLC),

    # SlottedGroup

    "ASMEB18.6.1.2": (tr_cmd("Slotted flat countersunk head wood screws"), SlottedGroup, ScrewParametersLC),
    "ASMEB18.6.1.4": (tr_cmd("Slotted oval countersunk head wood screws"), SlottedGroup, ScrewParametersLC),
    "ASMEB18.6.3.1A": (tr_cmd("UNC slotted countersunk flat head screws"), SlottedGroup, ScrewParametersLC),
    "ASMEB18.6.3.4A": (tr_cmd("UNC Slotted oval countersunk head screws"), SlottedGroup, ScrewParametersLC),
    "ASMEB18.6.3.9A": (tr_cmd("UNC Slotted pan head screws"), SlottedGroup, ScrewParametersLC),
    "ASMEB18.6.3.10A": (tr_cmd("UNC Slotted fillister head screws"), SlottedGroup, ScrewParametersLC),
    "ASMEB18.6.3.12A": (tr_cmd("UNC Slotted truss head screws"), SlottedGroup, ScrewParametersLC),
    "ASMEB18.6.3.16A": (tr_cmd("UNC Slotted round head screws"), SlottedGroup, ScrewParametersLC),
    "DIN84": (tr_cmd("(superseded by ISO 1207) Slotted cheese head screw"), SlottedGroup, ScrewParametersLC),
    "DIN96":   (tr_cmd("Slotted half round head wood screw"), SlottedGroup, ScrewParametersLC),
    "GOST1144-1": (tr_cmd("(Type 1) Half — round head wood screw"), SlottedGroup, ScrewParametersLC),
    "GOST1144-2": (tr_cmd("(Type 2) Half — round head wood screw"), SlottedGroup, ScrewParametersLC),
    "ISO1207": (tr_cmd("Slotted cheese head screw"), SlottedGroup, ScrewParametersLC),
    "ISO1580": (tr_cmd("Slotted pan head screw"), SlottedGroup, ScrewParametersLC),
    "ISO2009": (tr_cmd("Slotted countersunk flat head screw"), SlottedGroup, ScrewParametersLC),
    "ISO2010": (tr_cmd("Slotted raised countersunk head screw"), SlottedGroup, ScrewParametersLC),

    # HCrossGroup

    "ASMEB18.6.1.3": (tr_cmd("Cross recessed flat countersunk head wood screws"), HCrossGroup, ScrewParametersLC),
    "ASMEB18.6.1.5": (tr_cmd("Cross recessed oval countersunk head wood screws"), HCrossGroup, ScrewParametersLC),
    "ASMEB18.6.3.1B": (tr_cmd("UNC Cross recessed countersunk flat head screws"), HCrossGroup, ScrewParametersLC),
    "ASMEB18.6.3.4B": (tr_cmd("UNC Cross recessed oval countersunk head screws"), HCrossGroup, ScrewParametersLC),
    "ASMEB18.6.3.9B": (tr_cmd("UNC Cross recessed pan head screws"), HCrossGroup, ScrewParametersLC),
    "ASMEB18.6.3.10B": (tr_cmd("UNC Cross recessed fillister head screws"), HCrossGroup, ScrewParametersLC),
    "ASMEB18.6.3.12C": (tr_cmd("UNC Cross recessed truss head screws"), HCrossGroup, ScrewParametersLC),
    "ASMEB18.6.3.16B": (tr_cmd("UNC Cross recessed round head screws"), HCrossGroup, ScrewParametersLC),
    "DIN967": (tr_cmd("Cross recessed pan head screws with collar"), HCrossGroup, ScrewParametersLC),
    "DIN7996": (tr_cmd("Cross recessed pan head wood screw"), HCrossGroup, ScrewParametersLC),
    "GOST1144-3": (tr_cmd("(Type 3) Half — round head wood screw"), HCrossGroup, ScrewParametersLC),
    "GOST1144-4": (tr_cmd("(Type 4) Half — round head wood screw"), HCrossGroup, ScrewParametersLC),
    "ISO7045": (tr_cmd("Pan head screws type H cross recess"), HCrossGroup, ScrewParametersLC),
    "ISO7046": (tr_cmd("Countersunk flat head screws H cross r."), HCrossGroup, ScrewParametersLC),
    "ISO7047": (tr_cmd("Raised countersunk head screws H cross r."), HCrossGroup, ScrewParametersLC),
    "ISO7048": (tr_cmd("Cheese head screws with type H cross r."), HCrossGroup, ScrewParametersLC),
    "ISO7049-C": (tr_cmd("Pan head self tapping screws with conical point, type H cross r."), HCrossGroup, ScrewParametersLC),
    "ISO7049-F": (tr_cmd("Pan head self tapping screws with flat point, type H cross r."), HCrossGroup, ScrewParametersLC),
    "ISO7049-R": (tr_cmd("Pan head self tapping screws with rounded point type H cross r."), HCrossGroup, ScrewParametersLC),

    # OtherHeadGroup

    "ASMEB18.2.1.1": (tr_cmd("UNC Square bolts"), OtherHeadGroup, ScrewParametersLC),
    "ASMEB18.5.2": (tr_cmd("UNC Round head square neck bolts"), OtherHeadGroup, ScrewParametersLC),
    "DIN478": (tr_cmd("Square head bolts with collar"), OtherHeadGroup, ScrewParametersLC),
    "DIN603": (tr_cmd("Mushroom head square neck bolts"), OtherHeadGroup, ScrewParametersLC),
    "ISO2342": (tr_cmd("headless screws with shank"), OtherHeadGroup, ScrewParametersLC),

    # SetScrewGroup

    "ASMEB18.3.5A": (tr_cmd("UNC Hexagon socket set screws with flat point"), SetScrewGroup, ScrewParametersLC),
    "ASMEB18.3.5B": (tr_cmd("UNC Hexagon socket set screws with cone point"), SetScrewGroup, ScrewParametersLC),
    "ASMEB18.3.5C": (tr_cmd("UNC Hexagon socket set screws with dog point"), SetScrewGroup, ScrewParametersLC),
    "ASMEB18.3.5D": (tr_cmd("UNC Hexagon socket set screws with cup point"), SetScrewGroup, ScrewParametersLC),
    "ISO4026": (tr_cmd("Hexagon socket set screws with flat point"), SetScrewGroup, ScrewParametersLC),
    "ISO4027": (tr_cmd("Hexagon socket set screws with cone point"), SetScrewGroup, ScrewParametersLC),
    "ISO4028": (tr_cmd("Hexagon socket set screws with dog point"), SetScrewGroup, ScrewParametersLC),
    "ISO4029": (tr_cmd("Hexagon socket set screws with cup point"), SetScrewGroup, ScrewParametersLC),
    "ISO4766": (tr_cmd("Slotted socket set screws with flat point"), SetScrewGroup, ScrewParametersLC),
    "ISO7434": (tr_cmd("Slotted socket set screws with cone point"), SetScrewGroup, ScrewParametersLC),
    "ISO7435": (tr_cmd("Slotted socket set screws with long dog point"), SetScrewGroup, ScrewParametersLC),
    "ISO7436": (tr_cmd("Slotted socket set screws with cup point"), SetScrewGroup, ScrewParametersLC),

    # NutGroup

    "ASMEB18.2.2.1A": (tr_cmd("UNC Hex Machine screw nuts"), NutGroup, NutParameters),
    "ASMEB18.2.2.1B": (tr_cmd("UNC Square machine screw nuts"), NutGroup, NutParameters),
    "ASMEB18.2.2.2": (tr_cmd("UNC Square nuts"), NutGroup, NutParameters),
    "ASMEB18.2.2.4A": (tr_cmd("UNC Hexagon nuts"), NutGroup, NutParameters),
    "ASMEB18.2.2.4B": (tr_cmd("UNC Hexagon thin nuts"), NutGroup, NutParameters),
    "ASMEB18.2.2.5": (tr_cmd("UNC Hex slotted nuts"), NutGroup, NutParameters),
    "ASMEB18.2.2.12": (tr_cmd("UNC Hex flange nuts"), NutGroup, NutParameters),
    "ASMEB18.2.2.13": (tr_cmd("UNC Hex coupling nuts"), NutGroup, NutParameters),
    "ASMEB18.6.9A": (tr_cmd("wing nuts, type A"), NutGroup, NutParameters),
    "DIN315": (tr_cmd("wing nuts"), NutGroup, NutParameters),
    "DIN557": (tr_cmd("Square nuts"), NutGroup, NutParameters),
    "DIN562": (tr_cmd("Square nuts"), NutGroup, NutParameters),
    "DIN917": (tr_cmd("Cap nuts, thin style"), NutGroup, NutParameters),
    "DIN928": (tr_cmd("square weld nuts"), NutGroup, NutParameters),
    "DIN929": (tr_cmd("hexagonal weld nuts"), NutGroup, NutParameters),
    "DIN934": (tr_cmd("(superseded by ISO 4035 and ISO 8673) Hexagon thin nuts, chamfered"), NutGroup, NutParameters),
    "DIN935": (tr_cmd("Slotted / Castle nuts"), NutGroup, NutParameters),
    "DIN985": (tr_cmd("Nyloc nuts"), NutGroup, NutParameters),
    "DIN1587": (tr_cmd("Cap nuts"), NutGroup, NutParameters),
    "DIN6330": (tr_cmd("Hexagon nuts with a height of 1,5 d"), NutGroup, NutParameters),
    "DIN6331": (tr_cmd("Hexagon nuts with collar height 1,5 d"), NutGroup, NutParameters),
    "DIN6334": (tr_cmd("elongated hexagon nuts"), NutGroup, NutParameters),
    "DIN7967": (tr_cmd("self locking counter nuts"), NutGroup, WasherParameters),
    "EN1661": (tr_cmd("Hexagon nuts with flange"), NutGroup, NutParameters),
    "GOST11860-1": (tr_cmd("(Type 1) Cap nuts"), NutGroup, NutParameters),
    "ISO4032": (tr_cmd("Hexagon nuts, Style 1"), NutGroup, NutParameters),
    "ISO4033": (tr_cmd("Hexagon nuts, Style 2"), NutGroup, NutParameters),
    "ISO4034": (tr_cmd("Hexagon nuts, Style 1"), NutGroup, NutParameters),
    "ISO4035": (tr_cmd("Hexagon thin nuts, chamfered"), NutGroup, NutParameters),
    # "ISO4036": (tr_cmd("Hexagon thin nuts, unchamfered"), NutGroup, NutParameters),
    "ISO4161": (tr_cmd("Hexagon nuts with flange"), NutGroup, NutParameters),
    "ISO7040": (tr_cmd("Prevailing torque type hexagan nuts (with non-metallic insert)"), NutGroup, NutParameters),
    "ISO7041": (tr_cmd("Prevailing torque type hexagan nuts (with non-metallic insert), style 2"), NutGroup, NutParameters),
    "ISO7043": (tr_cmd("Prevailing torque type hexagon nuts with flange (with non-metallic insert)"), NutGroup, NutParameters),
    "ISO7044": (tr_cmd("Prevailing torque type all-metal hexagon nuts with flange"), NutGroup, NutParameters),
    "ISO7719": (tr_cmd("Prevailing torque type all-metal hexagon regular nuts"), NutGroup, NutParameters),
    "ISO7720": (tr_cmd("Prevailing torque type all-metal hexagon nuts, style 2"), NutGroup, NutParameters),
    "ISO8673": (tr_cmd("Hexagon regular nuts (style 1) with metric fine pitch thread — Product grades A and B"), NutGroup, NutParameters),
    "ISO8674": (tr_cmd("Hexagon high nuts (style 2) with metric fine pitch thread "), NutGroup, NutParameters),
    "ISO8675": (tr_cmd("Hexagon thin nuts chamfered (style 0) with metric fine pitch thread — Product grades A and B"), NutGroup, NutParameters),
    "ISO10511": (tr_cmd("Prevailing torque type hexagan thin nuts (with non-metallic insert)"), NutGroup, NutParameters),
    "ISO10512": (tr_cmd("Prevailing torque type hexagan nuts (with non-metallic insert) - fine pitch thread"), NutGroup, NutParameters),
    "ISO10513": (tr_cmd("Prevailing torque type all-metal hexagon nuts with fine pitch thread"), NutGroup, NutParameters),
    "ISO10663": (tr_cmd("Hexagon nuts with flange - fine pitch thread"), NutGroup, NutParameters),
    "ISO12125": (tr_cmd("Prevailing torque type hexagon nuts with flange (with non-metallic insert) - fine pitch thread"), NutGroup, NutParameters),
    "ISO12126": (tr_cmd("Prevailing torque type all-metal hexagon nuts with flange - fine pitch thread"), NutGroup, NutParameters),
    "ISO21670": (tr_cmd("Hexagon weld nuts with flange"), NutGroup, NutParameters),
    "SAEJ483a1": (tr_cmd("low cap nuts"), NutGroup, NutParameters),
    "SAEJ483a2": (tr_cmd("high cap nuts"), NutGroup, NutParameters),

    # TSlotGroup

    "DIN508": (tr_cmd("T-Slot nuts"), TSlotGroup, TSlotNutParameters),
    "GN505": (tr_cmd("GN 505 Serrated Quarter-Turn T-Slot nuts"), TSlotGroup, TSlotNutParameters),
    "GN505.4": (tr_cmd("GN 505.4 Serrated T-Slot Bolts"), TSlotGroup, TSlotBoltParameters),
    "GN506": (tr_cmd("GN 506 T-Slot nuts to swivel in"), TSlotGroup, TSlotNutParameters),
    "GN507": (tr_cmd("GN 507 T-Slot sliding nuts"), TSlotGroup, TSlotNutParameters),
    "ISO299": (tr_cmd("T-Slot nuts"), TSlotGroup, TSlotNutParameters),

    # WasherGroup

    "ASMEB18.21.1.12A": (tr_cmd("UN washers, narrow series"), WasherGroup, WasherParameters),
    "ASMEB18.21.1.12B": (tr_cmd("UN washers, regular series"), WasherGroup, WasherParameters),
    "ASMEB18.21.1.12C": (tr_cmd("UN washers, wide series"), WasherGroup, WasherParameters),
    "DIN6319C": (tr_cmd("Spherical washer"), WasherGroup, WasherParameters),
    "DIN6319D": (tr_cmd("Conical seat"), WasherGroup, WasherParameters),
    "DIN6319G": (tr_cmd("Conical seat"), WasherGroup, WasherParameters),
    "DIN6340": (tr_cmd("Washers for clamping devices"), WasherGroup, WasherParameters),
    "ISO7089": (tr_cmd("Plain washers - Normal series"), WasherGroup, WasherParameters),
    "ISO7090": (tr_cmd("Plain Washers, chamfered - Normal series"), WasherGroup, WasherParameters),
    # "ISO7091": (tr_cmd("Plain washer - Normal series - Product Grade C"), WasherGroup, WasherParameters),   # same as 7089??
    "ISO7092": (tr_cmd("Plain washers - Small series"), WasherGroup, WasherParameters),
    "ISO7093-1": (tr_cmd("Plain washers - Large series"), WasherGroup, WasherParameters),
    "ISO7094": (tr_cmd("Plain washers - Extra large series"), WasherGroup, WasherParameters),
    "ISO8738": (tr_cmd("Plain washers for clevis pins"), WasherGroup, WasherParameters),
    "NFE27-619": (tr_cmd("NFE27-619 Countersunk washer"), WasherGroup, WasherParameters),

    # ThreadedRodGroup

    "ScrewTapInch": (tr_cmd("Inch threaded rod for tapping holes"), ThreadedRodGroup, RodParameters),
    "ScrewDieInch": (tr_cmd("Tool object to cut external non-metric threads"), ThreadedRodGroup, RodParameters),
    "ThreadedRodInch": (tr_cmd("UNC threaded rod"), ThreadedRodGroup, RodParameters),
    "ThreadedRod": (tr_cmd("metric threaded rod"), ThreadedRodGroup, RodParameters),
    "ScrewTap": (tr_cmd("Metric threaded rod for tapping holes"), ThreadedRodGroup, RodParameters),
    "ScrewDie": (tr_cmd("Tool object to cut external metric threads"), ThreadedRodGroup, RodParameters),

    # InsertGroup

    "IUTHeatInsert": (tr_cmd("IUT[A/B/C] Heat Staked Metric Insert"), InsertGroup, HeatInsertParameters),
    "PEMPressNut": (tr_cmd("PEM Self Clinching nut"), InsertGroup, PEMPressNutParameters),
    "PEMStandoff": (tr_cmd("PEM Self Clinching standoff"), InsertGroup, PEMStandoffParameters),
    "PEMStud": (tr_cmd("PEM Self Clinching stud"), InsertGroup, ScrewParameters),
    "PCBSpacer": (tr_cmd("Wurth WA-SSTII PCB spacer"), InsertGroup, PCBSpacerParameters),
    "PCBStandoff": (tr_cmd("Wurth WA-SSTII  PCB standoff"), InsertGroup, PCBStandoffParameters),
    "4PWTI": (tr_cmd("4 Prong Wood Thread Insert (DIN 1624 Tee nuts)"), InsertGroup, WoodInsertParameters),

    # RetainingRingGroup

    "DIN471": (tr_cmd("Metric external retaining rings"), RetainingRingGroup, RetainingRingParameters),
    "DIN472": (tr_cmd("Metric internal retaining rings"), RetainingRingGroup, RetainingRingParameters),
    "DIN6799": (tr_cmd("Metric E-clip retaining rings"), RetainingRingGroup, RetainingRingParameters),

    # NailsGroup

    "DIN1160-A": (tr_cmd("Clout or slate nails"), NailGroup, NailParameters),
    "DIN1160-B": (tr_cmd("Clout or slate wide head nails"), NailGroup, NailParameters),

    # pins group
    "ISO1234": (tr_cmd("Split pins"), PinGroup, PinParameters),
    "ISO2338": (tr_cmd("Parallel pins"), PinGroup, PinParameters),
    "ISO2339": (tr_cmd("Taper pins"), PinGroup, PinParameters),
    "ISO2340A": (tr_cmd("Clevis pins without head"), PinGroup, PinParameters),
    "ISO2340B": (tr_cmd("Clevis pins without head (with split pin holes)"), PinGroup, PinParameters),
    "ISO2341A": (tr_cmd("Clevis pins with head"), PinGroup, PinParameters),
    "ISO2341B": (tr_cmd("Clevis pins with head (with split pin hole)"), PinGroup, PinParameters),
    "ISO8733": (tr_cmd("Parallel pins with internal thread, unhardened"), PinGroup, PinParameters),
    "ISO8734": (tr_cmd("Dowel pins"), PinGroup, PinParameters),
    "ISO8735": (tr_cmd("Parallel pins with internal thread, hardened"), PinGroup, PinParameters),
    "ISO8736": (tr_cmd("Taper pins with internal thread, unhardened"), PinGroup, PinParameters),
    "ISO8737": (tr_cmd("Taper pins with external thread, unhardened"), PinGroup, PinParameters),
    "ISO8739": (tr_cmd("Full-length grooved pins with pilot"), PinGroup, PinParameters),
    "ISO8740": (tr_cmd("Full-length grooved pins with chamfer"), PinGroup, PinParameters),
    "ISO8741": (tr_cmd("Half-length reverse taper grooved pins"), PinGroup, PinParameters),
    "ISO8742": (tr_cmd("Third-length center grooved pins"), PinGroup, PinParameters),
    "ISO8743": (tr_cmd("Half-length center grooved pins"), PinGroup, PinParameters),
    "ISO8744": (tr_cmd("Full-length taper grooved pins"), PinGroup, PinParameters),
    "ISO8745": (tr_cmd("Half-length taper grooved pins"), PinGroup, PinParameters),
    "ISO8746": (tr_cmd("Grooved pins with round head"), PinGroup, PinParameters),
    "ISO8747": (tr_cmd("Grooved pins with countersunk head"), PinGroup, PinParameters),
    "ISO8748": (tr_cmd("Coiled spring pins, heavy duty"), PinGroup, PinParameters),
    "ISO8750": (tr_cmd("Coiled spring pins, standard duty"), PinGroup, PinParameters),
    "ISO8751": (tr_cmd("Coiled spring pins, light duty"), PinGroup, PinParameters),
    "ISO8752": (tr_cmd("Slotted spring pins, heavy duty"), PinGroup, PinParameters),
    "ISO13337": (tr_cmd("Slotted spring pins, light duty"), PinGroup, PinParameters),
}

FatenersStandards = { "ASME", "DIN", "ISO", "SAE", "EN", "GOST"}
FastenersStandardMap = {"ScrewTapInch": "ASME", "ScrewDieInch": "ASME", "ThreadedRodInch": "ASME",
                        "ThreadedRod": "DIN", "ScrewTap": "ISO", "ScrewDie": "ISO" }
def FSGetStandardFromType(type):
    if type in FastenersStandardMap:
        return FastenersStandardMap[type]
    for std in FatenersStandards:
        if type.startswith(std):
            return std
    return "other"

def FSGetTypePretty(type):
    if type in FastenersStandardMap:
        return FastenersStandardMap[type] + " " + type
    for std in FatenersStandards:
        if type.startswith(std):
            return std + " " + type[len(std):]
    return "other"


def FSGetParams(type):
    if type not in FSScrewCommandTable:
        return {}
    return FSScrewCommandTable[type][CMD_PARAMETER_GRP]

def FSGetDescription(type):
    if type not in FSScrewCommandTable:
        return ""
    return FSGetTypePretty(type) + " " + FSScrewCommandTable[type][CMD_HELP]

def FSUpdateFormatString(fmtstr, type):
    if type not in FSScrewCommandTable:
        return fmtstr
    params = FSScrewCommandTable[type][CMD_PARAMETER_GRP]
    sizestr = ""
    for par in {"diameter", "length"}:
        if (par in params):
            sizestr += " x " + par
    return fmtstr.replace("{dimension}", "{" + sizestr[3:] + "}")


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
                "FastenerCmd", "Fastener type")).type = self.GetCompatibleTypes(type)
            obj.type = type
        else:
            type = obj.type

        if obj.type == "ISO7380":
            # backward compatibility - remove at FreeCAD version 0.23
            obj.type = type = "ISO7380-1"
        if obj.type == "DIN1624":
            # backward compatibility - remove at FreeCAD version 0.23
            type = "4PWTI"
            obj.type = self.GetCompatibleTypes(type)
            obj.type = type
        self.familyType = screwMaker.GetTypeName(type)

        if not hasattr(obj, "diameter"):
            diameters = screwMaker.GetAllDiams(type)
            diameters.insert(0, 'Auto')
            if "diameterCustom" in FSGetParams(type):
                diameters.append("Custom")
            obj.addProperty("App::PropertyEnumeration", "diameter", "Parameters", translate(
                "FastenerCmd", "Standard diameter")).diameter = diameters
            diameter = diameters[1]
        else:
            diameter = obj.diameter
        params = FSGetParams(type)

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
                "FastenerCmd", "Screw length")).length = screwMaker.GetTableProperty(type, diameter, "Length", 20.0)
        if "externalDiam" in params and not hasattr(obj, "externalDiam"):
            obj.addProperty("App::PropertyLength", "externalDiam", "Parameters", translate(
                "FastenerCmd", "External Diameter")).externalDiam = screwMaker.GetTableProperty(type, diameter, "ExtDia", 8.0)
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
        if "slotWidth" in params and not hasattr(obj, "slotWidth"):
            obj.addProperty("App::PropertyEnumeration", "slotWidth", "Parameters", translate(
                "FastenerCmd", "Slot width")).slotWidth = screwMaker.GetAllSlotWidths(type, diameter)

        # hex key length
        if "keySize" in params and not hasattr(obj, "keySize"):
            obj.addProperty("App::PropertyEnumeration", "keySize", "Parameters", translate(
                "FastenerCmd", "Key size")).keySize = screwMaker.GetAllKeySizes(type, diameter)

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
        pargrp = FSGetParams(ftype)
        types = []
        for ftype2 in FSScrewCommandTable:
            if FSGetParams(ftype2) is pargrp:
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
        if not isinstance(obj.length, str):
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
        params = FSGetParams(fp.type)

        # handle type changes
        typechange = False
        if fp.type != self.type:
            typechange = True
            curdiam = fp.diameter
            diameters = screwMaker.GetAllDiams(fp.type)
            diameters.insert(0, 'Auto')
            if "diameterCustom" in params:
                diameters.append("Custom")

            if curdiam not in diameters:
                curdiam = 'Auto'
            fp.diameter = diameters
            fp.diameter = curdiam

        # handle diameter changes
        if self.pitchCustom is not None and hasattr(fp, "pitchCustom") and str(fp.pitchCustom) != self.pitchCustom:
            fp.diameter = 'Custom'
        diameterchange = self.diameter != fp.diameter
        matchouterchange = hasattr(fp, "matchOuter") and self.matchOuter != fp.matchOuter
        widthchange = hasattr(fp, "width") and self.width != fp.width

        if fp.diameter == 'Auto' or matchouterchange:
            mo = fp.matchOuter if hasattr(fp, "matchOuter") else False
            self.calc_diam = screwMaker.AutoDiameter(
                fp.type, shape, baseobj, mo)
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
                if (diameterchange):
                    l = screwMaker.GetTableProperty(fp.type, fp.diameter, "Length", fp.length.Value)
                else:
                    l = fp.length.Value
                if l < 2.0:
                    l = 2.0
                fp.length = l
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

        if hasattr(fp, 'externalDiam'):
            if (diameterchange):
                fp.externalDiam = screwMaker.GetTableProperty(fp.type, fp.diameter, "ExtDia", 8.0)

        if diameterchange and "thicknessCode" in params:
            tcodes = screwMaker.GetAllTcodes(fp.type, fp.diameter)
            oldcode = fp.tcode
            fp.tcode = tcodes
            if oldcode in tcodes:
                fp.tcode = oldcode

        if (typechange or diameterchange) and "slotWidth" in params:
            swidths = screwMaker.GetAllSlotWidths(fp.type, fp.diameter)
            oldsw = fp.slotWidth
            fp.slotWidth = swidths
            if oldsw in swidths:
                fp.slotWidth = oldsw

        if diameterchange and "keySize" in params:
            sizes = screwMaker.GetAllKeySizes(fp.type, fp.diameter)
            olds = fp.keySize
            fp.keySize = sizes
            if olds in sizes:
                fp.keySize = olds

        if fp.diameter == 'Custom' and hasattr(fp, "pitchCustom"):
            self.calc_pitch = fp.pitchCustom.Value
        else:
            self.calc_pitch = None

        screwMaker.updateFastenerParameters()

        self.BackupObject(fp)
        self.baseType = FSGetTypeAlias(self.type)

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

    def dumps(self):
        #        return {'ObjectName' : self.Object.Name}
        return None

    def loads(self, state):
        if state is not None:
            import FreeCAD
            doc = FreeCAD.ActiveDocument  # crap
            self.Object = doc.getObject(state['ObjectName'])

    if FastenerBase.FsUseGetSetState: # compatibility with old versions
        def __getstate__(self):
            return self.dumps()

        def __setstate__(self, state):
            self.loads(state)

    def getIcon(self):
        type = 'ISO4017.svg'
        if hasattr(self.Object, "type"):
            type = self.Object.type
        elif hasattr(self.Object.Proxy, "type"):
            type = self.Object.Proxy.type
        # default to ISO4017.svg
        return os.path.join(iconPath, FSGetIconAlias(type) + '.svg')

class FSScrewCommand:
    """Add Screw command"""

    def __init__(self, type, help):
        self.Type = type
        self.Help = help
        self.TypeName = screwMaker.GetTypeName(type)

    def GetResources(self):
        import GrammaticalTools

        icon = os.path.join(iconPath, FSGetIconAlias(self.Type) + '.svg')
        return {'Pixmap': icon,
                # the name of a svg file available in the resources
                'MenuText': tr_cmd("Add ") + GrammaticalTools.ToDativeCase(self.Help),
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
    enabled_fastener_toolbutton_types = {
        # default to showing all toolbars if the preferences entry is not found
        "ISO": FSParam.GetBool("ShowISOInToolbars", True),
        "DIN": FSParam.GetBool("ShowDINInToolbars", True),
        "EN": FSParam.GetBool("ShowENInToolbars", True),
        "ASME": FSParam.GetBool("ShowASMEInToolbars", True),
        "SAE": FSParam.GetBool("ShowSAEInToolbars", True),
        "GOST": FSParam.GetBool("ShowGOSTInToolbars", True),
        "other": True,
    }
    cmd = 'FS' + type
    Gui.addCommand(cmd, FSScrewCommand(
        type, FSGetDescription(type)))
    group = FSScrewCommandTable[type][CMD_GROUP]
    # Don't add the command to the toolbar for this session if the user has
    # disabled the standard type in the preferences page:
    if not enabled_fastener_toolbutton_types[FSGetStandardFromType(type)]:
        group = "Other " + group
    FastenerBase.FSCommands.append(cmd, "screws", group)


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
FastenerBase.FSAddFastenerType("T-Slot", False)
FastenerBase.FSAddFastenerType("SetScrew")
FastenerBase.FSAddFastenerType("HexKey", False)
FastenerBase.FSAddFastenerType("Pin")
for item in ScrewMaker.screwTables:
    FastenerBase.FSAddItemsToType(ScrewMaker.screwTables[item][0], item)

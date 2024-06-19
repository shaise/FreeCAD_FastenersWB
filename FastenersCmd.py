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
translate("FastenerCmdTreeView", "Thumbscrew")

# fmt: off
ScrewParameters = {"Type", "Diameter",
                   "MatchOuter", "Thread", "LeftHanded", "Length"}
ScrewParametersLC = {"Type", "Diameter", "MatchOuter",
                     "Thread", "LeftHanded", "Length", "LengthCustom"}
RodParameters = {"Type", "Diameter", "MatchOuter", "Thread",
                 "LeftHanded", "lengthArbitrary",  "DiameterCustom", "PitchCustom"}
NutParameters = {"Type", "Diameter", "MatchOuter", "Thread", "LeftHanded"}
WoodInsertParameters = {"Type", "Diameter", "MatchOuter", "Thread", "LeftHanded"}
HeatInsertParameters = {"Type", "Diameter", "lengthArbitrary", "ExternalDiam", "MatchOuter", "Thread", "LeftHanded"}
WasherParameters = {"Type", "Diameter", "MatchOuter"}
PCBStandoffParameters = {"Type", "Diameter", "MatchOuter", "Thread",
                         "LeftHanded", "ThreadLength", "LenByDiamAndWidth", "LengthCustom", "widthCode"}
PCBSpacerParameters = {"Type", "Diameter", "MatchOuter", "Thread",
                       "LeftHanded", "LenByDiamAndWidth", "LengthCustom", "widthCode"}
PEMPressNutParameters = {"Type", "Diameter",
                         "MatchOuter", "Thread", "LeftHanded", "ThicknessCode"}
PEMStandoffParameters = {"Type", "Diameter", "MatchOuter",
                         "Thread", "LeftHanded", "Length", "blindness"}
RetainingRingParameters = {"Type", "Diameter", "MatchOuter"}
PinParameters = {"Type", "Diameter", "Length", "LengthCustom", "LeftHanded", "Thread"}
TSlotNutParameters = { "Type", "Diameter", "MatchOuter",
                        "Thread", "LeftHanded", "SlotWidth" }
TSlotBoltParameters = { "Type", "Diameter", "Length", "LengthCustom",
                       "MatchOuter", "Thread", "LeftHanded", "SlotWidth" }
HexKeyParameters = { "Type", "Diameter", "MatchOuter", "KeySize" }
NailParameters = { "Type", "Diameter", "MatchOuter", }
# this is a list of all possible fastener attribs
FastenerAttribs = ['Type', 'Diameter', 'Thread', 'LeftHanded', 'MatchOuter', 'Length',
                   'LengthCustom', 'Width', 'DiameterCustom', 'PitchCustom', 'Tcode',
                   'Blind', 'ScrewLength', "SlotWidth", 'ExternalDiam', 'KeySize']


# Names of fasteners groups translated once before FSScrewCommandTable created.
# For make FSScrewCommandTable more compact and readable
HexHeadGroup = translate("FastenerCmd", "Hex head")
HexagonSocketGroup = translate("FastenerCmd", "Hexagon socket")
HexalobularSocketGroup = translate("FastenerCmd", "Hexalobular socket")
SlottedGroup = translate("FastenerCmd", "Slotted")
HCrossGroup = translate("FastenerCmd", "H cross")
NutGroup = translate("FastenerCmd", "Nut")
WasherGroup = translate("FastenerCmd", "Washer")
OtherHeadGroup = translate("FastenerCmd", "Misc head")
ThreadedRodGroup = translate("FastenerCmd", "ThreadedRod")
InsertGroup = translate("FastenerCmd", "Inserts")
RetainingRingGroup = translate("FastenerCmd", "Retaining Rings")
TSlotGroup = translate("FastenerCmd", "T-Slot Fasteners")
SetScrewGroup = translate("FastenerCmd", "Set screws")
NailGroup = translate("FastenerCmd", "Nails")
PinGroup = translate("FastenerCmd", "Pins")
ThumbScrewGroup = translate("FastenerCmd", "Thumb screws")

CMD_HELP = 0
CMD_GROUP = 1
CMD_PARAMETER_GRP = 2
CMD_STD_GROUP = 3

FSScrewCommandTable = {
    # type - (help, group, parameter-group, standard-group)

    # HexHeadGroup

    "ASMEB18.2.1.1": (translate("FastenerCmd", "UNC Square bolts"), OtherHeadGroup, ScrewParametersLC),
    "ASMEB18.2.1.6": (translate("FastenerCmd", "UNC Hex head screws"), HexHeadGroup, ScrewParametersLC),
    "ASMEB18.2.1.8": (translate("FastenerCmd", "UNC Hex head screws with flange"), HexHeadGroup, ScrewParametersLC),
    "DIN571": (translate("FastenerCmd", "Hex head wood screw"), HexHeadGroup, ScrewParametersLC),
    "DIN933": (translate("FastenerCmd", "Hex head screw"), HexHeadGroup, ScrewParametersLC),
    "DIN961": (translate("FastenerCmd", "Hex head screw"), HexHeadGroup, ScrewParametersLC),
    "EN1662": (translate("FastenerCmd", "Hexagon bolt with flange, small series"), HexHeadGroup, ScrewParametersLC),
    "EN1665": (translate("FastenerCmd", "Hexagon bolt with flange, heavy series"), HexHeadGroup, ScrewParametersLC),
    "ISO4014": (translate("FastenerCmd", "Hex head bolt - Product grades A and B"), HexHeadGroup, ScrewParametersLC),
    "ISO4015": (translate("FastenerCmd", "Hexagon head bolts with reduced shank"), HexHeadGroup, ScrewParametersLC),
    "ISO4016": (translate("FastenerCmd", "Hex head bolts - Product grade C"), HexHeadGroup, ScrewParametersLC),
    "ISO4017": (translate("FastenerCmd", "Hex head screw - Product grades A and B"), HexHeadGroup, ScrewParametersLC),
    "ISO4018": (translate("FastenerCmd", "Hex head screws - Product grade C"), HexHeadGroup, ScrewParametersLC),
    "ISO4162": (translate("FastenerCmd", "Hexagon bolts with flange - Small series - Product grade A with driving feature of product grade B"), HexHeadGroup, ScrewParametersLC),
    "ISO8676": (translate("FastenerCmd", "Hex head screws with fine pitch thread"), HexHeadGroup, ScrewParametersLC),
    "ISO8765": (translate("FastenerCmd", "Hex head bolt with fine pitch thread"), HexHeadGroup, ScrewParametersLC),
    "ISO15071": (translate("FastenerCmd", "Hexagon bolts with flange - Small series - Product grade A"), HexHeadGroup, ScrewParametersLC),
    "ISO15072": (translate("FastenerCmd", "Hexagon bolts with flange with fine pitch thread - Small series - Product grade A"), HexHeadGroup, ScrewParametersLC),

    # HexagonSocketGroup

    "ASMEB18.3.1A": (translate("FastenerCmd", "UNC Hex socket head cap screws"), HexagonSocketGroup, ScrewParametersLC),
    "ASMEB18.3.1G": (translate("FastenerCmd", "UNC Hex socket head cap screws with low head"), HexagonSocketGroup, ScrewParametersLC),
    "ASMEB18.3.2": (translate("FastenerCmd", "UNC Hex socket countersunk head screws"), HexagonSocketGroup, ScrewParametersLC),
    "ASMEB18.3.3A": (translate("FastenerCmd", "UNC Hex socket button head screws"), HexagonSocketGroup, ScrewParametersLC),
    "ASMEB18.3.3B": (translate("FastenerCmd", "UNC Hex socket button head screws with flange"), HexagonSocketGroup, ScrewParametersLC),
    "ASMEB18.3.4": (translate("FastenerCmd", "UNC Hexagon socket head shoulder screws"), HexagonSocketGroup, ScrewParametersLC),
    "DIN6912": (translate("FastenerCmd", "Hexagon socket head cap screws with low head with centre"), HexagonSocketGroup, ScrewParametersLC),
    "DIN7984": (translate("FastenerCmd", "Hexagon socket head cap screws with low head"), HexagonSocketGroup, ScrewParametersLC),
    "ISO2936": (translate("FastenerCmd", "Hexagon socket screw keys"), HexagonSocketGroup, HexKeyParameters),
    "ISO4762": (translate("FastenerCmd", "Hexagon socket head cap screw"), HexagonSocketGroup, ScrewParametersLC),
    "ISO7379": (translate("FastenerCmd", "Hexagon socket head shoulder screw"), HexagonSocketGroup, ScrewParametersLC),
    "ISO7380-1": (translate("FastenerCmd", "Hexagon socket button head screw"), HexagonSocketGroup, ScrewParametersLC),
    "ISO7380-2": (translate("FastenerCmd", "Hexagon socket button head screws with collar"), HexagonSocketGroup, ScrewParametersLC),
    "ISO10642": (translate("FastenerCmd", "Hexagon socket countersunk head screw"), HexagonSocketGroup, ScrewParametersLC),

    # HexalobularSocketGroup

    "ISO14579": (translate("FastenerCmd", "Hexalobular socket head cap screws"), HexalobularSocketGroup, ScrewParametersLC),
    "ISO14580": (translate("FastenerCmd", "Hexalobular socket cheese head screws"), HexalobularSocketGroup, ScrewParametersLC),
    "ISO14581": (translate("FastenerCmd", "Hexalobular socket countersunk flat head screws"), HexalobularSocketGroup, ScrewParametersLC),
    "ISO14582": (translate("FastenerCmd", "Hexalobular socket countersunk head screws, high head"), HexalobularSocketGroup, ScrewParametersLC),
    "ISO14583": (translate("FastenerCmd", "Hexalobular socket pan head screws"), HexalobularSocketGroup, ScrewParametersLC),
    "ISO14584": (translate("FastenerCmd", "Hexalobular socket raised countersunk head screws"), HexalobularSocketGroup, ScrewParametersLC),

    # SlottedGroup

    "ASMEB18.6.1.2": (translate("FastenerCmd", "Slotted flat countersunk head wood screws"), SlottedGroup, ScrewParametersLC),
    "ASMEB18.6.1.4": (translate("FastenerCmd", "Slotted oval countersunk head wood screws"), SlottedGroup, ScrewParametersLC),
    "ASMEB18.6.3.1A": (translate("FastenerCmd", "UNC slotted countersunk flat head screws"), SlottedGroup, ScrewParametersLC),
    "ASMEB18.6.3.4A": (translate("FastenerCmd", "UNC Slotted oval countersunk head screws"), SlottedGroup, ScrewParametersLC),
    "ASMEB18.6.3.9A": (translate("FastenerCmd", "UNC Slotted pan head screws"), SlottedGroup, ScrewParametersLC),
    "ASMEB18.6.3.10A": (translate("FastenerCmd", "UNC Slotted fillister head screws"), SlottedGroup, ScrewParametersLC),
    "ASMEB18.6.3.12A": (translate("FastenerCmd", "UNC Slotted truss head screws"), SlottedGroup, ScrewParametersLC),
    "ASMEB18.6.3.16A": (translate("FastenerCmd", "UNC Slotted round head screws"), SlottedGroup, ScrewParametersLC),
    "DIN84": (translate("FastenerCmd", "(Superseded by ISO 1207) Slotted cheese head screw"), SlottedGroup, ScrewParametersLC),
    "DIN96":   (translate("FastenerCmd", "Slotted half round head wood screw"), SlottedGroup, ScrewParametersLC),
    "GOST1144-1": (translate("FastenerCmd", "(Type 1) Half — round head wood screw"), SlottedGroup, ScrewParametersLC),
    "GOST1144-2": (translate("FastenerCmd", "(Type 2) Half — round head wood screw"), SlottedGroup, ScrewParametersLC),
    "ISO1207": (translate("FastenerCmd", "Slotted cheese head screw"), SlottedGroup, ScrewParametersLC),
    "ISO1580": (translate("FastenerCmd", "Slotted pan head screw"), SlottedGroup, ScrewParametersLC),
    "ISO2009": (translate("FastenerCmd", "Slotted countersunk flat head screw"), SlottedGroup, ScrewParametersLC),
    "ISO2010": (translate("FastenerCmd", "Slotted raised countersunk head screw"), SlottedGroup, ScrewParametersLC),

    # HCrossGroup

    "ASMEB18.6.1.3": (translate("FastenerCmd", "Cross recessed flat countersunk head wood screws"), HCrossGroup, ScrewParametersLC),
    "ASMEB18.6.1.5": (translate("FastenerCmd", "Cross recessed oval countersunk head wood screws"), HCrossGroup, ScrewParametersLC),
    "ASMEB18.6.3.1B": (translate("FastenerCmd", "UNC Cross recessed countersunk flat head screws"), HCrossGroup, ScrewParametersLC),
    "ASMEB18.6.3.4B": (translate("FastenerCmd", "UNC Cross recessed oval countersunk head screws"), HCrossGroup, ScrewParametersLC),
    "ASMEB18.6.3.9B": (translate("FastenerCmd", "UNC Cross recessed pan head screws"), HCrossGroup, ScrewParametersLC),
    "ASMEB18.6.3.10B": (translate("FastenerCmd", "UNC Cross recessed fillister head screws"), HCrossGroup, ScrewParametersLC),
    "ASMEB18.6.3.12C": (translate("FastenerCmd", "UNC Cross recessed truss head screws"), HCrossGroup, ScrewParametersLC),
    "ASMEB18.6.3.16B": (translate("FastenerCmd", "UNC Cross recessed round head screws"), HCrossGroup, ScrewParametersLC),
    "DIN967": (translate("FastenerCmd", "Cross recessed pan head screws with collar"), HCrossGroup, ScrewParametersLC),
    "DIN7996": (translate("FastenerCmd", "Cross recessed pan head wood screw"), HCrossGroup, ScrewParametersLC),
    "GOST1144-3": (translate("FastenerCmd", "(Type 3) Half — round head wood screw"), HCrossGroup, ScrewParametersLC),
    "GOST1144-4": (translate("FastenerCmd", "(Type 4) Half — round head wood screw"), HCrossGroup, ScrewParametersLC),
    "ISO7045": (translate("FastenerCmd", "Pan head screws type H cross recess"), HCrossGroup, ScrewParametersLC),
    "ISO7046": (translate("FastenerCmd", "Countersunk flat head screws H cross r."), HCrossGroup, ScrewParametersLC),
    "ISO7047": (translate("FastenerCmd", "Raised countersunk head screws H cross r."), HCrossGroup, ScrewParametersLC),
    "ISO7048": (translate("FastenerCmd", "Cheese head screws with type H cross r."), HCrossGroup, ScrewParametersLC),
    "ISO7049-C": (translate("FastenerCmd", "Pan head self tapping screws with conical point, type H cross r."), HCrossGroup, ScrewParametersLC),
    "ISO7049-F": (translate("FastenerCmd", "Pan head self tapping screws with flat point, type H cross r."), HCrossGroup, ScrewParametersLC),
    "ISO7049-R": (translate("FastenerCmd", "Pan head self tapping screws with rounded point type H cross r."), HCrossGroup, ScrewParametersLC),

    # OtherHeadGroup

    "ASMEB18.2.1.1": (translate("FastenerCmd", "UNC Square bolts"), OtherHeadGroup, ScrewParametersLC),
    "ASMEB18.5.2": (translate("FastenerCmd", "UNC Round head square neck bolts"), OtherHeadGroup, ScrewParametersLC),
    "DIN478": (translate("FastenerCmd", "Square head bolts with collar"), OtherHeadGroup, ScrewParametersLC),
    "DIN603": (translate("FastenerCmd", "Mushroom head square neck bolts"), OtherHeadGroup, ScrewParametersLC),
    "ISO2342": (translate("FastenerCmd", "headless screws with shank"), OtherHeadGroup, ScrewParametersLC),

    # SetScrewGroup

    "ASMEB18.3.5A": (translate("FastenerCmd", "UNC Hexagon socket set screws with flat point"), SetScrewGroup, ScrewParametersLC),
    "ASMEB18.3.5B": (translate("FastenerCmd", "UNC Hexagon socket set screws with cone point"), SetScrewGroup, ScrewParametersLC),
    "ASMEB18.3.5C": (translate("FastenerCmd", "UNC Hexagon socket set screws with dog point"), SetScrewGroup, ScrewParametersLC),
    "ASMEB18.3.5D": (translate("FastenerCmd", "UNC Hexagon socket set screws with cup point"), SetScrewGroup, ScrewParametersLC),
    "ISO4026": (translate("FastenerCmd", "Hexagon socket set screws with flat point"), SetScrewGroup, ScrewParametersLC),
    "ISO4027": (translate("FastenerCmd", "Hexagon socket set screws with cone point"), SetScrewGroup, ScrewParametersLC),
    "ISO4028": (translate("FastenerCmd", "Hexagon socket set screws with dog point"), SetScrewGroup, ScrewParametersLC),
    "ISO4029": (translate("FastenerCmd", "Hexagon socket set screws with cup point"), SetScrewGroup, ScrewParametersLC),
    "ISO4766": (translate("FastenerCmd", "Slotted socket set screws with flat point"), SetScrewGroup, ScrewParametersLC),
    "ISO7434": (translate("FastenerCmd", "Slotted socket set screws with cone point"), SetScrewGroup, ScrewParametersLC),
    "ISO7435": (translate("FastenerCmd", "Slotted socket set screws with long dog point"), SetScrewGroup, ScrewParametersLC),
    "ISO7436": (translate("FastenerCmd", "Slotted socket set screws with cup point"), SetScrewGroup, ScrewParametersLC),

    # ThumbscrewGroup

    "DIN464": (translate("FastenerCmd", "Knurled thumb screws, high type"), ThumbScrewGroup, ScrewParametersLC),
    "DIN465": (translate("FastenerCmd", "Slotted knurled thumb screws, high type"), ThumbScrewGroup, ScrewParametersLC),
    "DIN653": (translate("FastenerCmd", "Knurled thumb screws, low type"), ThumbScrewGroup, ScrewParametersLC),

    # NutGroup

    "ASMEB18.2.2.1A": (translate("FastenerCmd", "UNC Hex Machine screw nuts"), NutGroup, NutParameters),
    "ASMEB18.2.2.1B": (translate("FastenerCmd", "UNC Square machine screw nuts"), NutGroup, NutParameters),
    "ASMEB18.2.2.2": (translate("FastenerCmd", "UNC Square nuts"), NutGroup, NutParameters),
    "ASMEB18.2.2.4A": (translate("FastenerCmd", "UNC Hexagon nuts"), NutGroup, NutParameters),
    "ASMEB18.2.2.4B": (translate("FastenerCmd", "UNC Hexagon thin nuts"), NutGroup, NutParameters),
    "ASMEB18.2.2.5": (translate("FastenerCmd", "UNC Hex slotted nuts"), NutGroup, NutParameters),
    "ASMEB18.2.2.12": (translate("FastenerCmd", "UNC Hex flange nuts"), NutGroup, NutParameters),
    "ASMEB18.2.2.13": (translate("FastenerCmd", "UNC Hex coupling nuts"), NutGroup, NutParameters),
    "ASMEB18.6.9A": (translate("FastenerCmd", "Wing nuts, type A"), NutGroup, NutParameters),
    "DIN315": (translate("FastenerCmd", "Wing nuts"), NutGroup, NutParameters),
    "DIN557": (translate("FastenerCmd", "Square nuts"), NutGroup, NutParameters),
    "DIN562": (translate("FastenerCmd", "Square nuts"), NutGroup, NutParameters),
    "DIN917": (translate("FastenerCmd", "Cap nuts, thin style"), NutGroup, NutParameters),
    "DIN928": (translate("FastenerCmd", "Square weld nuts"), NutGroup, NutParameters),
    "DIN929": (translate("FastenerCmd", "Hexagonal weld nuts"), NutGroup, NutParameters),
    "DIN934": (translate("FastenerCmd", "(Superseded by ISO 4035 and ISO 8673) Hexagon thin nuts, chamfered"), NutGroup, NutParameters),
    "DIN935": (translate("FastenerCmd", "Slotted / Castle nuts"), NutGroup, NutParameters),
    "DIN985": (translate("FastenerCmd", "Nyloc nuts"), NutGroup, NutParameters),
    "DIN1587": (translate("FastenerCmd", "Cap nuts"), NutGroup, NutParameters),
    "DIN6330": (translate("FastenerCmd", "Hexagon nuts with a height of 1,5 d"), NutGroup, NutParameters),
    "DIN6331": (translate("FastenerCmd", "Hexagon nuts with collar height 1,5 d"), NutGroup, NutParameters),
    "DIN6334": (translate("FastenerCmd", "Elongated hexagon nuts"), NutGroup, NutParameters),
    "DIN7967": (translate("FastenerCmd", "Self locking counter nuts"), NutGroup, WasherParameters),
    "EN1661": (translate("FastenerCmd", "Hexagon nuts with flange"), NutGroup, NutParameters),
    "GOST11860-1": (translate("FastenerCmd", "(Type 1) Cap nuts"), NutGroup, NutParameters),
    "ISO4032": (translate("FastenerCmd", "Hexagon nuts, Style 1"), NutGroup, NutParameters),
    "ISO4033": (translate("FastenerCmd", "Hexagon nuts, Style 2"), NutGroup, NutParameters),
    "ISO4034": (translate("FastenerCmd", "Hexagon nuts, Style 1"), NutGroup, NutParameters),
    "ISO4035": (translate("FastenerCmd", "Hexagon thin nuts, chamfered"), NutGroup, NutParameters),
    # "ISO4036": (translate("FastenerCmd", "Hexagon thin nuts, unchamfered"), NutGroup, NutParameters),
    "ISO4161": (translate("FastenerCmd", "Hexagon nuts with flange"), NutGroup, NutParameters),
    "ISO7040": (translate("FastenerCmd", "Prevailing torque type hexagon nuts (with non-metallic insert)"), NutGroup, NutParameters),
    "ISO7041": (translate("FastenerCmd", "Prevailing torque type hexagon nuts (with non-metallic insert), style 2"), NutGroup, NutParameters),
    "ISO7043": (translate("FastenerCmd", "Prevailing torque type hexagon nuts with flange (with non-metallic insert)"), NutGroup, NutParameters),
    "ISO7044": (translate("FastenerCmd", "Prevailing torque type all-metal hexagon nuts with flange"), NutGroup, NutParameters),
    "ISO7719": (translate("FastenerCmd", "Prevailing torque type all-metal hexagon regular nuts"), NutGroup, NutParameters),
    "ISO7720": (translate("FastenerCmd", "Prevailing torque type all-metal hexagon nuts, style 2"), NutGroup, NutParameters),
    "ISO8673": (translate("FastenerCmd", "Hexagon regular nuts (style 1) with metric fine pitch thread — Product grades A and B"), NutGroup, NutParameters),
    "ISO8674": (translate("FastenerCmd", "Hexagon high nuts (style 2) with metric fine pitch thread "), NutGroup, NutParameters),
    "ISO8675": (translate("FastenerCmd", "Hexagon thin nuts chamfered (style 0) with metric fine pitch thread — Product grades A and B"), NutGroup, NutParameters),
    "ISO10511": (translate("FastenerCmd", "Prevailing torque type hexagon thin nuts (with non-metallic insert)"), NutGroup, NutParameters),
    "ISO10512": (translate("FastenerCmd", "Prevailing torque type hexagon nuts (with non-metallic insert) - fine pitch thread"), NutGroup, NutParameters),
    "ISO10513": (translate("FastenerCmd", "Prevailing torque type all-metal hexagon nuts with fine pitch thread"), NutGroup, NutParameters),
    "ISO10663": (translate("FastenerCmd", "Hexagon nuts with flange - fine pitch thread"), NutGroup, NutParameters),
    "ISO12125": (translate("FastenerCmd", "Prevailing torque type hexagon nuts with flange (with non-metallic insert) - fine pitch thread"), NutGroup, NutParameters),
    "ISO12126": (translate("FastenerCmd", "Prevailing torque type all-metal hexagon nuts with flange - fine pitch thread"), NutGroup, NutParameters),
    "ISO21670": (translate("FastenerCmd", "Hexagon weld nuts with flange"), NutGroup, NutParameters),
    "SAEJ483a1": (translate("FastenerCmd", "Low cap nuts"), NutGroup, NutParameters),
    "SAEJ483a2": (translate("FastenerCmd", "High cap nuts"), NutGroup, NutParameters),

    # TSlotGroup

    "DIN508": (translate("FastenerCmd", "T-Slot nuts"), TSlotGroup, TSlotNutParameters),
    "GN505": (translate("FastenerCmd", "GN 505 Serrated Quarter-Turn T-Slot nuts"), TSlotGroup, TSlotNutParameters),
    "GN505.4": (translate("FastenerCmd", "GN 505.4 Serrated T-Slot Bolts"), TSlotGroup, TSlotBoltParameters),
    "GN506": (translate("FastenerCmd", "GN 506 T-Slot nuts to swivel in"), TSlotGroup, TSlotNutParameters),
    "GN507": (translate("FastenerCmd", "GN 507 T-Slot sliding nuts"), TSlotGroup, TSlotNutParameters),
    "ISO299": (translate("FastenerCmd", "T-Slot nuts"), TSlotGroup, TSlotNutParameters),

    # WasherGroup

    "ASMEB18.21.1.12A": (translate("FastenerCmd", "UN washers, narrow series"), WasherGroup, WasherParameters),
    "ASMEB18.21.1.12B": (translate("FastenerCmd", "UN washers, regular series"), WasherGroup, WasherParameters),
    "ASMEB18.21.1.12C": (translate("FastenerCmd", "UN washers, wide series"), WasherGroup, WasherParameters),
    "DIN6319C": (translate("FastenerCmd", "Spherical washer"), WasherGroup, WasherParameters),
    "DIN6319D": (translate("FastenerCmd", "Conical seat"), WasherGroup, WasherParameters),
    "DIN6319G": (translate("FastenerCmd", "Conical seat"), WasherGroup, WasherParameters),
    "DIN6340": (translate("FastenerCmd", "Washers for clamping devices"), WasherGroup, WasherParameters),
    "ISO7089": (translate("FastenerCmd", "Plain washers - Normal series"), WasherGroup, WasherParameters),
    "ISO7090": (translate("FastenerCmd", "Plain Washers, chamfered - Normal series"), WasherGroup, WasherParameters),
    # "ISO7091": (translate("FastenerCmd", "Plain washer - Normal series - Product Grade C"), WasherGroup, WasherParameters),   # same as 7089??
    "ISO7092": (translate("FastenerCmd", "Plain washers - Small series"), WasherGroup, WasherParameters),
    "ISO7093-1": (translate("FastenerCmd", "Plain washers - Large series"), WasherGroup, WasherParameters),
    "ISO7094": (translate("FastenerCmd", "Plain washers - Extra large series"), WasherGroup, WasherParameters),
    "ISO8738": (translate("FastenerCmd", "Plain washers for clevis pins"), WasherGroup, WasherParameters),
    "NFE27-619": (translate("FastenerCmd", "NFE27-619 Countersunk washer"), WasherGroup, WasherParameters),

    # ThreadedRodGroup

    "ScrewTapInch": (translate("FastenerCmd", "Inch threaded rod for tapping holes"), ThreadedRodGroup, RodParameters),
    "ScrewDieInch": (translate("FastenerCmd", "Tool object to cut external non-metric threads"), ThreadedRodGroup, RodParameters),
    "ThreadedRodInch": (translate("FastenerCmd", "UNC threaded rod"), ThreadedRodGroup, RodParameters),
    "ThreadedRod": (translate("FastenerCmd", "Metric threaded rod"), ThreadedRodGroup, RodParameters),
    "ScrewTap": (translate("FastenerCmd", "Metric threaded rod for tapping holes"), ThreadedRodGroup, RodParameters),
    "ScrewDie": (translate("FastenerCmd", "Tool object to cut external metric threads"), ThreadedRodGroup, RodParameters),

    # InsertGroup

    "IUTHeatInsert": (translate("FastenerCmd", "IUT[A/B/C] Heat Staked Metric Insert"), InsertGroup, HeatInsertParameters),
    "PEMPressNut": (translate("FastenerCmd", "PEM Self Clinching nut"), InsertGroup, PEMPressNutParameters),
    "PEMStandoff": (translate("FastenerCmd", "PEM Self Clinching standoff"), InsertGroup, PEMStandoffParameters),
    "PEMStud": (translate("FastenerCmd", "PEM Self Clinching stud"), InsertGroup, ScrewParameters),
    "PCBSpacer": (translate("FastenerCmd", "Wurth WA-SSTII PCB spacer"), InsertGroup, PCBSpacerParameters),
    "PCBStandoff": (translate("FastenerCmd", "Wurth WA-SSTII  PCB standoff"), InsertGroup, PCBStandoffParameters),
    "4PWTI": (translate("FastenerCmd", "4 Prong Wood Thread Insert (DIN 1624 Tee nuts)"), InsertGroup, WoodInsertParameters),

    # RetainingRingGroup

    "DIN471": (translate("FastenerCmd", "Metric external retaining rings"), RetainingRingGroup, RetainingRingParameters),
    "DIN472": (translate("FastenerCmd", "Metric internal retaining rings"), RetainingRingGroup, RetainingRingParameters),
    "DIN6799": (translate("FastenerCmd", "Metric E-clip retaining rings"), RetainingRingGroup, RetainingRingParameters),

    # NailsGroup

    "DIN1143": (translate("FastenerCmd", "Round plain head nails for use in automatic nailing machines"), NailGroup, NailParameters),
    "DIN1144-A": (translate("FastenerCmd", "Nails for the installation of wood wool composite panels, 20mm round head"), NailGroup, NailParameters),
    "DIN1151-A": (translate("FastenerCmd", "Round plain head wire nails"), NailGroup, NailParameters),
    "DIN1151-B": (translate("FastenerCmd", "Round countersunk head wire nails"), NailGroup, NailParameters),
    "DIN1152": (translate("FastenerCmd", "Round lost head wire nails"), NailGroup, NailParameters),
    "DIN1160-A": (translate("FastenerCmd", "Clout or slate nails"), NailGroup, NailParameters),
    "DIN1160-B": (translate("FastenerCmd", "Clout or slate wide head nails"), NailGroup, NailParameters),

    # pins group
    "ISO1234": (translate("FastenerCmd", "Split pins"), PinGroup, PinParameters),
    "ISO2338": (translate("FastenerCmd", "Parallel pins"), PinGroup, PinParameters),
    "ISO2339": (translate("FastenerCmd", "Taper pins"), PinGroup, PinParameters),
    "ISO2340A": (translate("FastenerCmd", "Clevis pins without head"), PinGroup, PinParameters),
    "ISO2340B": (translate("FastenerCmd", "Clevis pins without head (with split pin holes)"), PinGroup, PinParameters),
    "ISO2341A": (translate("FastenerCmd", "Clevis pins with head"), PinGroup, PinParameters),
    "ISO2341B": (translate("FastenerCmd", "Clevis pins with head (with split pin hole)"), PinGroup, PinParameters),
    "ISO8733": (translate("FastenerCmd", "Parallel pins with internal thread, unhardened"), PinGroup, PinParameters),
    "ISO8734": (translate("FastenerCmd", "Dowel pins"), PinGroup, PinParameters),
    "ISO8735": (translate("FastenerCmd", "Parallel pins with internal thread, hardened"), PinGroup, PinParameters),
    "ISO8736": (translate("FastenerCmd", "Taper pins with internal thread, unhardened"), PinGroup, PinParameters),
    "ISO8737": (translate("FastenerCmd", "Taper pins with external thread, unhardened"), PinGroup, PinParameters),
    "ISO8739": (translate("FastenerCmd", "Full-length grooved pins with pilot"), PinGroup, PinParameters),
    "ISO8740": (translate("FastenerCmd", "Full-length grooved pins with chamfer"), PinGroup, PinParameters),
    "ISO8741": (translate("FastenerCmd", "Half-length reverse taper grooved pins"), PinGroup, PinParameters),
    "ISO8742": (translate("FastenerCmd", "Third-length center grooved pins"), PinGroup, PinParameters),
    "ISO8743": (translate("FastenerCmd", "Half-length center grooved pins"), PinGroup, PinParameters),
    "ISO8744": (translate("FastenerCmd", "Full-length taper grooved pins"), PinGroup, PinParameters),
    "ISO8745": (translate("FastenerCmd", "Half-length taper grooved pins"), PinGroup, PinParameters),
    "ISO8746": (translate("FastenerCmd", "Grooved pins with round head"), PinGroup, PinParameters),
    "ISO8747": (translate("FastenerCmd", "Grooved pins with countersunk head"), PinGroup, PinParameters),
    "ISO8748": (translate("FastenerCmd", "Coiled spring pins, heavy duty"), PinGroup, PinParameters),
    "ISO8750": (translate("FastenerCmd", "Coiled spring pins, standard duty"), PinGroup, PinParameters),
    "ISO8751": (translate("FastenerCmd", "Coiled spring pins, light duty"), PinGroup, PinParameters),
    "ISO8752": (translate("FastenerCmd", "Slotted spring pins, heavy duty"), PinGroup, PinParameters),
    "ISO13337": (translate("FastenerCmd", "Slotted spring pins, light duty"), PinGroup, PinParameters),
}

FatenersStandards = { "ASME", "DIN", "ISO", "SAE", "EN", "GOST"}
FastenersStandardMap = {"ScrewTapInch": "ASME", "ScrewDieInch": "ASME", "ThreadedRodInch": "ASME",
                        "ThreadedRod": "DIN", "ScrewTap": "ISO", "ScrewDie": "ISO" }
# fmt: on


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
    for par in {"Diameter", "Length"}:
        if (par in params):
            sizestr += " x " + par
    return fmtstr.replace("{dimension}", "{" + sizestr[3:] + "}")


class FSScrewObject(FSBaseObject):
    def __init__(self, obj, type, attachTo):
        """Add screw type fastener."""
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
        if not hasattr(obj, "Type"):
            if type is None:  # probably pre V0.4.0 or pre upper case object
                if hasattr(self, "originalType"):
                    type = self.originalType
                if hasattr(obj, "type"):
                    type = obj.type
                    FreeCAD.Console.PrintLog(
                        "using original type: " + type + "\n")
            obj.addProperty("App::PropertyEnumeration", "Type", "Parameters", translate(
                "FastenerCmd", "Fastener type")).Type = self.GetCompatibleTypes(type)
            obj.Type = type
        else:
            type = obj.Type

        if obj.Type == "ISO7380":
            # backward compatibility - remove at FreeCAD version 0.23
            obj.Type = type = "ISO7380-1"
        if obj.Type == "DIN1624":
            # backward compatibility - remove at FreeCAD version 0.23
            type = "4PWTI"
            obj.Type = self.GetCompatibleTypes(type)
            obj.Type = type
        self.familyType = screwMaker.GetTypeName(type)

        if not hasattr(obj, "Diameter"):
            diameters = screwMaker.GetAllDiams(type)
            diameters.insert(0, 'Auto')
            if "DiameterCustom" in FSGetParams(type):
                diameters.append("Custom")
            obj.addProperty("App::PropertyEnumeration", "Diameter", "Parameters", translate(
                "FastenerCmd", "Standard diameter")).Diameter = diameters
            diameter = diameters[1]
            if hasattr(obj, "diameter"):
                # backward compatible to lowercase params
                obj.Diameter = diameter = obj.diameter
        else:
            diameter = obj.Diameter
        params = FSGetParams(type)

        # thread parameters
        if "Thread" in params and not hasattr(obj, "Thread"):
            obj.addProperty("App::PropertyBool", "Thread", "Parameters", translate(
                "FastenerCmd", "Generate real thread")).Thread = False
        if "LeftHanded" in params and not hasattr(obj, 'LeftHanded'):
            obj.addProperty("App::PropertyBool", "LeftHanded", "Parameters", translate(
                "FastenerCmd", "Left handed thread")).LeftHanded = False
        if "MatchOuter" in params and not hasattr(obj, "MatchOuter"):
            obj.addProperty("App::PropertyBool", "MatchOuter", "Parameters", translate(
                "FastenerCmd", "Match outer thread diameter")).MatchOuter = FSParam.GetBool("MatchOuterDiameter")

        # width parameters
        if "widthCode" in params and not hasattr(obj, "Width"):
            obj.addProperty("App::PropertyEnumeration", "Width", "Parameters", translate(
                "FastenerCmd", "Body width code")).Width = screwMaker.GetAllWidthcodes(type, diameter)

        # length parameters
        addCustomLen = "LengthCustom" in params and not hasattr(
            obj, "LengthCustom")
        if "Length" in params or "LenByDiamAndWidth" in params:
            # if diameter == "Auto":
            #     diameter = self.initialDiameter
            if "LenByDiamAndWidth" in params:
                slens = screwMaker.GetAllLengths(
                    type, diameter, addCustomLen, obj.Width)
            else:
                slens = screwMaker.GetAllLengths(type, diameter, addCustomLen)
            if not hasattr(obj, 'Length'):
                obj.addProperty("App::PropertyEnumeration", "Length", "Parameters", translate(
                    "FastenerCmd", "Screw length")).Length = slens
            elif addCustomLen:
                origLen = obj.Length
                obj.Length = slens
                if origLen in slens:
                    obj.Length = origLen
            if addCustomLen:
                obj.addProperty("App::PropertyLength", "LengthCustom", "Parameters", translate(
                    "FastenerCmd", "Custom length")).LengthCustom = self.inswap(slens[0])

        # custom size parameters
        if "lengthArbitrary" in params and not hasattr(obj, "Length"):
            obj.addProperty("App::PropertyLength", "Length", "Parameters", translate(
                "FastenerCmd", "Screw length")).Length = screwMaker.GetTableProperty(type, diameter, "Length", 20.0)
        if "ExternalDiam" in params and not hasattr(obj, "ExternalDiam"):
            obj.addProperty("App::PropertyLength", "ExternalDiam", "Parameters", translate(
                "FastenerCmd", "External Diameter")).ExternalDiam = screwMaker.GetTableProperty(type, diameter, "ExtDia", 8.0)
        if "DiameterCustom" in params and not hasattr(obj, "DiameterCustom"):
            obj.addProperty("App::PropertyLength", "DiameterCustom", "Parameters", translate(
                "FastenerCmd", "Screw major diameter custom")).DiameterCustom = 6
        if "PitchCustom" in params and not hasattr(obj, "PitchCustom"):
            obj.addProperty("App::PropertyLength", "PitchCustom", "Parameters", translate(
                "FastenerCmd", "Screw pitch custom")).PitchCustom = 1.0

        # thickness
        if "ThicknessCode" in params and not hasattr(obj, "Tcode"):
            obj.addProperty("App::PropertyEnumeration", "Tcode", "Parameters", translate(
                "FastenerCmd", "Thickness code")).Tcode = screwMaker.GetAllTcodes(type, diameter)

        # slot width
        if "SlotWidth" in params and not hasattr(obj, "SlotWidth"):
            obj.addProperty("App::PropertyEnumeration", "SlotWidth", "Parameters", translate(
                "FastenerCmd", "Slot width")).SlotWidth = screwMaker.GetAllSlotWidths(type, diameter)

        # hex key length
        if "KeySize" in params and not hasattr(obj, "KeySize"):
            obj.addProperty("App::PropertyEnumeration", "KeySize", "Parameters", translate(
                "FastenerCmd", "Key size")).KeySize = screwMaker.GetAllKeySizes(type, diameter)

        # misc
        if "blindness" in params and not hasattr(obj, "Blind"):
            obj.addProperty("App::PropertyBool", "Blind", "Parameters", translate(
                "FastenerCmd", "Blind Standoff type")).Blind = False
        if "ThreadLength" in params and not hasattr(obj, "ScrewLength"):
            obj.addProperty("App::PropertyLength", "ScrewLength", "Parameters", translate(
                "FastenerCmd", "Threaded part length")).ScrewLength = screwMaker.GetThreadLength(type, diameter)

        self.migrateToUpperCase(obj)
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
        if len(re.findall(r"[.]\d*$", val)) > 0:
            return val.rstrip('0').rstrip('.')
        return val

    def ActiveLength(self, obj):
        if not hasattr(obj, 'Length'):
            return '0'
        if not isinstance(obj.Length, str):
            return self.CleanDecimals(float(obj.Length))
        if obj.Length == 'Custom':
            return self.CleanDecimals(float(obj.LengthCustom))
        return obj.Length

    def paramChanged(self, param, value):
        return getattr(self, param) != value

    def execute(self, fp):
        """Print a short message when doing a recomputation, this method is mandatory."""

        try:
            baseobj = fp.BaseObject[0]
            shape = baseobj.getSubObject(fp.BaseObject[1][0])
        except:
            baseobj = None
            shape = None

        # for backward compatibility: add missing attribute if needed
        # self.VerifyMissingAttrs(fp, fp.Diameter)

        # FreeCAD.Console.PrintLog("MatchOuter:" + str(fp.MatchOuter) + "\n")
        params = FSGetParams(fp.Type)

        # handle type changes
        typechange = False
        if fp.Type != self.Type:
            typechange = True
            curdiam = fp.Diameter
            diameters = screwMaker.GetAllDiams(fp.Type)
            diameters.insert(0, 'Auto')
            if "DiameterCustom" in params:
                diameters.append("Custom")

            if curdiam not in diameters:
                curdiam = 'Auto'
            fp.Diameter = diameters
            fp.Diameter = curdiam

        # handle diameter changes
        if self.PitchCustom is not None and hasattr(fp, "PitchCustom") and str(fp.PitchCustom) != self.PitchCustom:
            fp.Diameter = 'Custom'
        diameterchange = self.Diameter != fp.Diameter
        matchouterchange = hasattr(fp, "MatchOuter") and self.MatchOuter != fp.MatchOuter
        widthchange = hasattr(fp, "Width") and self.Width != fp.Width

        if fp.Diameter == 'Auto' or matchouterchange:
            mo = fp.MatchOuter if hasattr(fp, "MatchOuter") else False
            self.calc_diam = screwMaker.AutoDiameter(
                fp.Type, shape, baseobj, mo)
            fp.Diameter = self.calc_diam
            diameterchange = True
        elif fp.Diameter == 'Custom' and hasattr(fp, "DiameterCustom"):
            self.calc_diam = str(fp.DiameterCustom.Value)
        else:
            self.calc_diam = fp.Diameter

        # handle length changes
        if hasattr(fp, 'Length'):
            if "lengthArbitrary" in params:
                # arbitrary lengths
                if (diameterchange):
                    l = screwMaker.GetTableProperty(fp.Type, fp.Diameter, "Length", fp.Length.Value)
                else:
                    l = fp.Length.Value
                if l < 2.0:
                    l = 2.0
                fp.Length = l
                self.calc_len = str(l)
            else:
                # fixed lengths
                width = None
                if "LenByDiamAndWidth" in params:
                    width = fp.Width
                if self.paramChanged('Length', fp.Length):
                    if fp.Length != 'Custom' and hasattr(fp, 'LengthCustom'):
                        fp.LengthCustom = FastenerBase.LenStr2Num(
                            fp.Length)  # ***
                elif self.LengthCustom is not None and str(fp.LengthCustom) != self.LengthCustom:
                    fp.Length = 'Custom'
                origLen = self.ActiveLength(fp)
                origIsCustom = fp.Length == 'Custom'
                self.calc_diam, l, auto_width = screwMaker.FindClosest(
                    fp.Type, self.calc_diam, origLen, width)
                if self.calc_diam != fp.Diameter:
                    diameterchange = True
                    fp.Diameter = self.calc_diam
                if width != auto_width:
                    widthchange = True
                    fp.Width = screwMaker.GetAllWidthcodes(
                        fp.Type, fp.Diameter)
                    fp.Width = width = auto_width

                if origIsCustom:
                    l = origLen

                if l != origLen or diameterchange or typechange or widthchange:
                    if diameterchange or typechange or widthchange:
                        fp.Length = screwMaker.GetAllLengths(
                            fp.Type, fp.Diameter, hasattr(fp, 'LengthCustom'), width)
                        if hasattr(fp, 'ScrewLength'):
                            fp.ScrewLength = screwMaker.GetThreadLength(
                                fp.Type, fp.Diameter)
                    if origIsCustom:
                        fp.Length = 'Custom'
                    else:
                        fp.Length = l
                        if hasattr(fp, 'LengthCustom'):
                            fp.LengthCustom = FastenerBase.LenStr2Num(l)
                self.calc_len = l
        else:
            self.calc_len = None

        if hasattr(fp, 'ExternalDiam'):
            if (diameterchange):
                fp.ExternalDiam = screwMaker.GetTableProperty(fp.Type, fp.Diameter, "ExtDia", 8.0)

        if diameterchange and "ThicknessCode" in params:
            tcodes = screwMaker.GetAllTcodes(fp.Type, fp.Diameter)
            oldcode = fp.Tcode
            fp.Tcode = tcodes
            if oldcode in tcodes:
                fp.Tcode = oldcode

        if (typechange or diameterchange) and "SlotWidth" in params:
            swidths = screwMaker.GetAllSlotWidths(fp.Type, fp.Diameter)
            oldsw = fp.SlotWidth
            fp.SlotWidth = swidths
            if oldsw in swidths:
                fp.SlotWidth = oldsw

        if diameterchange and "KeySize" in params:
            sizes = screwMaker.GetAllKeySizes(fp.Type, fp.Diameter)
            olds = fp.KeySize
            fp.KeySize = sizes
            if olds in sizes:
                fp.KeySize = olds

        if fp.Diameter == 'Custom' and hasattr(fp, "PitchCustom"):
            self.calc_pitch = fp.PitchCustom.Value
        else:
            self.calc_pitch = None

        screwMaker.updateFastenerParameters()

        self.BackupObject(fp)
        self.baseType = FSGetTypeAlias(self.Type)

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
        if hasattr(fp, 'Length'):
            dispLen = self.ActiveLength(fp)
            label += 'x' + dispLen
            if hasattr(fp, 'Width'):
                dispWidth = 'x' + fp.Width
                label += 'x' + dispWidth
        if hasattr(fp, 'LeftHanded'):
            if self.LeftHanded:
                label += 'LH'
        if hasattr(fp, 'SlotWidth'):
            label += ' x ' + fp.SlotWidth
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
            FastenerBase.FSMoveToObject(fp, shape, fp.Invert, fp.Offset.Value)


class FSViewProviderTree:
    """A View provider for custom icon."""

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
        if hasattr(self.Object, "Type"):
            type = self.Object.Type
        elif hasattr(self.Object.Proxy, "Type"):
            type = self.Object.Proxy.Type
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
                'MenuText': translate("FastenerCmd", "Add ") + GrammaticalTools.ToDativeCase(self.Help),
                'ToolTip': self.Help}

    def Activated(self):
        for selObj in FastenerBase.FSGetAttachableSelections():
            a = FreeCAD.ActiveDocument.addObject("Part::FeaturePython",
                                                 self.TypeName)
            FSScrewObject(a, self.Type, selObj)
            a.Label = a.Proxy.familyType
            if FSParam.GetBool("DefaultFastenerColorActive", False):
                a.ViewObject.DiffuseColor = FSParam.GetUnsigned("DefaultFastenerColor", 0xcccccc00)
            if FSParam.GetBool("DefaultLineWidthActive", False):
                a.ViewObject.LineWidth = FSParam.GetFloat("DefaultLineWidth", 1.0)
            if FSParam.GetBool("DefaultVertexSizeActive", False):
                a.ViewObject.PointSize  = FSParam.GetFloat("DefaultVertexSize", 1.0)

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
        self.originalType = obj.Proxy.Type
        super().onDocumentRestored(obj)


class FSScrewDieObject(FSScrewObject):
    def onDocumentRestored(self, obj):
        self.originalType = obj.Proxy.Type
        super().onDocumentRestored(obj)


class FSThreadedRodObject(FSScrewObject):
    def onDocumentRestored(self, obj):
        self.originalType = obj.Proxy.Type
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

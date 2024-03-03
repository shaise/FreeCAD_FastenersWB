# -*- coding: utf-8 -*-
"""
***************************************************************************
*   Copyright (c) 2024                                                    *
*   Alex Neufeld <alex.d.neufeld@gmail.com>                               *
*                                                                         *
*   This file is a supplement to the FreeCAD CAx development system.      *
*                                                                         *
*   This program is free software; you can redistribute it and/or modify  *
*   it under the terms of the GNU Lesser General Public License (LGPL)    *
*   as published by the Free Software Foundation; either version 2 of     *
*   the License, or (at your option) any later version.                   *
*   for detail see the LICENCE text file.                                 *
*                                                                         *
*   This software is distributed in the hope that it will be useful,      *
*   but WITHOUT ANY WARRANTY; without even the implied warranty of        *
*   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the         *
*   GNU Library General Public License for more details.                  *
*                                                                         *
*   You should have received a copy of the GNU Library General Public     *
*   License along with this macro; if not, write to the Free Software     *
*   Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  *
*   USA                                                                   *
*                                                                         *
***************************************************************************
"""
import os
from collections import defaultdict
import FreeCAD
import FreeCADGui
from TranslateUtils import translate
from FSutils import iconPath
from FastenerBase import FSCommands
from FastenerBase import GetTotalObjectRepeats
from FastenersCmd import FSScrewObject

tr = lambda x: translate("FastenerBOM", x)

# fmt: off
fastener_designations = {
    "4PWTI": tr("Tee nut Inserts for wood, {diameter}"),
    "ASMEB18.2.1.1": tr("Square Head Bolts, ASME B18.2.1, {diameter} x {length}"),
    "ASMEB18.2.1.6": tr("Hex Cap Screws, ASME B18.2.1, {diameter} x {length}"),
    "ASMEB18.2.1.8": tr("Hex Flange Screws, ASME B18.2.1, {diameter} x {length}"),
    "ASMEB18.2.2.1A": tr("Hex Machine Screw Nuts, ASME B18.2.2, {diameter}"),
    "ASMEB18.2.2.1B": tr("Square Machine Screw Nuts, ASME B18.2.2, {diameter}"),
    "ASMEB18.2.2.12": tr("Hex Flange Nuts, ASME B18.2.2, {diameter}"),
    "ASMEB18.2.2.13": tr("Hex Coupling Nuts, ASME B18.2.2, {diameter}"),
    "ASMEB18.2.2.2": tr("Square Nuts, ASME B18.2.2, {diameter}"),
    "ASMEB18.2.2.4A": tr("Hex Nuts, ASME B18.2.2, {diameter}"),
    "ASMEB18.2.2.4B": tr("Hex Jam Nuts, ASME B18.2.2, {diameter}"),
    "ASMEB18.2.2.5": tr("Hex Slotted Nuts, ASME B18.2.2, {diameter}"),
    "ASMEB18.21.1.12A": tr("Plain Washers, Narrow Series, ASME B18.21.1, {diameter}"),
    "ASMEB18.21.1.12B": tr("Plain Washers, Regular Series, ASME B18.21.1, {diameter}"),
    "ASMEB18.21.1.12C": tr("Plain Washers, Wide Series, ASME B18.21.1, {diameter}"),
    "ASMEB18.3.1A": tr("Hexagon Socket Head Cap Screws, ASME B18.3, {diameter} x {length}"),
    "ASMEB18.3.1G": tr("Hexagon Low Head Socket Cap Screws, ASME B18.3, {diameter} x {length}"),
    "ASMEB18.3.2": tr("Hexagon Socket Flat Countersunk Head Cap Screws, ASME B18.3, {diameter} x {length}"),
    "ASMEB18.3.3A": tr("Hexagon Socket Button Head Cap Screws, ASME B18.3, {diameter} x {length}"),
    "ASMEB18.3.3B": tr("Hexagon Socket Flanged Button Head Cap Screws, ASME B18.3, {diameter} x {length}"),
    "ASMEB18.3.4": tr("Hexagon Socket Head Shoulder Screws, ASME B18.3, {diameter} x {length}"),
    "ASMEB18.3.5A": tr("Hexagon Socket Set Screws, Flat Point, ASME B18.3, {diameter} x {length}"),
    "ASMEB18.3.5B": tr("Hexagon Socket Set Screws, Cone Point, ASME B18.3, {diameter} x {length}"),
    "ASMEB18.3.5C": tr("Hexagon Socket Set Screws, Dog Point, ASME B18.3, {diameter} x {length}"),
    "ASMEB18.3.5D": tr("Hexagon Socket Set Screws, Cup Point, ASME B18.3, {diameter} x {length}"),
    "ASMEB18.5.2": tr("Round Head Square Neck Bolts,  ASME B18.5, {diameter} x {length}"),
    "ASMEB18.6.1.2": tr("Slotted Flat Countersunk Head Wood Screws,  ASME B18.6.1, {diameter} x {length}"),
    "ASMEB18.6.1.3": tr("Type 1 Cross Recessed Flat Countersunk Head Wood Screws,  ASME B18.6.1, {diameter} x {length}"),
    "ASMEB18.6.1.4": tr("Slotted Oval Countersunk Head Wood Screws,  ASME B18.6.1, {diameter} x {length}"),
    "ASMEB18.6.1.5": tr("Type 1 Cross Recessed Oval Countersunk Head Wood Screws,  ASME B18.6.1, {diameter} x {length}"),
    "ASMEB18.6.3.10A": tr("Slotted Fillister Head Machine Screws,  ASME B18.6.3, {diameter} x {length}"),
    "ASMEB18.6.3.1A": tr("Slotted Flat Countersunk Head Machine Screws,  ASME B18.6.3, {diameter} x {length}"),
    "ASMEB18.6.3.10B": tr("Type 1 Cross Recessed Fillister Head Machine Screws,  ASME B18.6.3, {diameter} x {length}"),
    "ASMEB18.6.3.1B": tr("Type 1 Cross Recessed Flat Countersunk Head Machine Screws,  ASME B18.6.3, {diameter} x {length}"),
    "ASMEB18.6.3.12A": tr("Slotted Truss Head Machine Screws,  ASME B18.6.3, {diameter} x {length}"),
    "ASMEB18.6.3.12C": tr("Type 1 Cross Recessed Truss Head Machine Screws,  ASME B18.6.3, {diameter} x {length}"),
    "ASMEB18.6.3.16A": tr("Slotted Round Head Machine Screws,  ASME B18.6.3, {diameter} x {length}"),
    "ASMEB18.6.3.16B": tr("Type 1 Cross Recessed Round Head Machine Screws,  ASME B18.6.3, {diameter} x {length}"),
    "ASMEB18.6.3.4A": tr("Slotted Oval Countersunk Head Machine Screws,  ASME B18.6.3, {diameter} x {length}"),
    "ASMEB18.6.3.4B": tr("Type 1 Cross Recessed Oval Countersunk Head Machine Screws,  ASME B18.6.3, {diameter} x {length}"),
    "ASMEB18.6.3.9A": tr("Slotted Pan Head Machine Screws,  ASME B18.6.3, {diameter} x {length}"),
    "ASMEB18.6.3.9B": tr("Type 1 Cross Recessed Pan Head Machine Screws,  ASME B18.6.3, {diameter} x {length}"),
    "ASMEB18.6.9A": tr("ASME B18.6.9, {diameter} Type A Wing Nut"),
    "DIN84": tr("Cheese head screw DIN 84 - {diameter} x {length}"),
    "DIN96": tr("Wood screw DIN 96 - {diameter} x {length}"),
    "DIN315": tr("Wing nut DIN 315 - {diameter}"),
    "DIN471": tr("Retaining ring DIN 471 - {diameter}"),
    "DIN472": tr("Retaining ring DIN 472 - {diameter}"),
    "DIN478": tr("Square head bolt DIN 478 - {diameter} x {length}"),
    "DIN508": tr("T-Slot Nut DIN 508 - {diameter}"),
    "DIN557": tr("Square nut DIN 557 - {diameter}"),
    "DIN562": tr("Square nut DIN 562 - {diameter}"),
    "DIN571": tr("Wood screw DIN 571 - {diameter} x {length}"),
    "DIN603": tr("Mushroom head square neck bolt  DIN 603 - {diameter} x {length}"),
    "DIN917": tr("Cap nut DIN 917 - {diameter}"),
    "DIN928": tr("Square weld nut DIN 928 - {diameter}"),
    "DIN929": tr("Hexagon weld nut DIN 929 - {diameter}"),
    "DIN933": tr("Hexagon head screw DIN 933 - {diameter} x {length}"),
    "DIN934": tr("Hexagon nut DIN 934 - {diameter}"),
    "DIN935": tr("Hexagon castle nut DIN 935 - {diameter}"),
    "DIN961": tr("Hexagon head screw DIN 961 - {diameter} x {length}"),
    "DIN967": tr("Pan head screw DIN 967 - {diameter} x {length} - H"),
    "DIN985": tr("Prevailing torque type hexagon thin nut DIN 985 - {diameter}"),
    "DIN1160-A": tr("Wire nail - DIN 1160 - A - {diameter}"),
    "DIN1160-B": tr("Wire nail - DIN 1160 - B - {diameter}"),
    "DIN1587": tr("Cap nut - DIN 1587 - {diameter}"),
    "DIN6319C": tr("Spherical washer - DIN 6319 - C - {diameter}"),
    "DIN6319D": tr("Conical seat - DIN 6319 - D - {diameter}"),
    "DIN6319G": tr("Conical seat - DIN 6319 - G - {diameter}"),
    "DIN6330": tr("Hexagon nut DIN 6330 - {diameter}"),
    "DIN6331": tr("Hexagon nut with flange DIN 6331 - {diameter}"),
    "DIN6334": tr("Hexagon nut DIN 6334 - {diameter}"),
    "DIN6340": tr("Washer DIN 6340 - {diameter}"),
    "DIN6799": tr("Retaining ring DIN 6799 - {diameter}"),
    "DIN6912": tr("Hexagon socket head cap screw DIN 6912 - {diameter} x {length}"),
    "DIN7967": tr("Self locking counter nut DIN 7967 - {diameter}"),
    "DIN7984": tr("Hexagon socket head cap screw DIN 7984 - {diameter} x {length}"),
    "DIN7996": tr("Wood screw DIN 7996 - {diameter} x {length}"),
    "EN1661": tr("Hexagon nut with flange EN 1661 - {diameter}"),
    "EN1662": tr("Hexagon head screw with flange EN 1662 - {diameter}"),
    "EN1665": tr("Hexagon head screw with flange EN 1665 - {diameter}"),
    "GN505": tr("T-Slot Nut GN 505 - {diameter} x {slotWidth}"),
    "GN505.4": tr("T-Slot Bolt GN 505.4 - {diameter} x {slotWidth} x {length}"),
    "GN506": tr("T-Slot Nut GN 506 - {diameter} x {slotWidth}"),
    "GN507": tr("T-Slot Nut GN 507 - {diameter} x {slotWidth}"),
    "GOST1144-1": tr("Wood screw GOST 1144-1 - {diameter} x {length}"),
    "GOST1144-2": tr("Wood screw GOST 1144-2 - {diameter} x {length}"),
    "GOST1144-3": tr("Wood screw GOST 1144-3 - {diameter} x {length}"),
    "GOST1144-4": tr("Wood screw GOST 1144-4 - {diameter} x {length}"),
    "GOST11860-1": tr("Cap nut - GOST 11860-1 - {diameter}"),
    "ISO299": tr("T-Slot Nut ISO 299 - {diameter} x {slotWidth}"),
    "ISO1207": tr("Cheese head screw ISO 1207 - {diameter} x {length}"),
    "ISO1234": tr("Split Pin ISO 1234 - {diameter} x {length}"),
    "ISO1580": tr("Pan head screw ISO 1580 - {diameter} x {length}"),
    "ISO2009": tr("Countersunk flat head screw ISO 2009 - {diameter} x {length}"),
    "ISO2010": tr("Countersunk raised head screw ISO 2010 - {diameter} x {length}"),
    "ISO2338": tr("Parallel pin ISO 2338 - {diameter} x {length}"),
    "ISO2339": tr("Taper pin ISO 2339 - {diameter} x {length}"),
    "ISO2340A": tr("Clevis Pin ISO 2340 - A - {diameter} x {length}"),
    "ISO2340B": tr("Clevis Pin ISO 2340 - B - {diameter} x {length}"),
    "ISO2341A": tr("Clevis Pin ISO 2341 - A - {diameter} x {length}"),
    "ISO2341B": tr("Clevis Pin ISO 2341 - B - {diameter} x {length}"),
    "ISO2342": tr("Headless screw ISO 2342 - {diameter} x {length}"),
    "ISO2936": tr("Socket screw key ISO 2936 - {diameter}"),
    "ISO4014": tr("Hexagon head bolt ISO 4014 - {diameter} x {length}"),
    "ISO4017": tr("Hexagon head screw ISO 4017 - {diameter} x {length}"),
    "ISO4026": tr("Hexagon socket set screw ISO 4026 - {diameter} x {length}"),
    "ISO4027": tr("Hexagon socket set screw ISO 4027 - {diameter} x {length}"),
    "ISO4028": tr("Hexagon socket set screw ISO 4028 - {diameter} x {length}"),
    "ISO4029": tr("Hexagon socket set screw ISO 4029 - {diameter} x {length}"),
    "ISO4032": tr("Hexagon regular nut ISO 4032 - {diameter}"),
    "ISO4033": tr("Hexagon high nut ISO 4033 - {diameter}"),
    "ISO4034": tr("Hexagon regular nut ISO 4034 - {diameter}"),
    "ISO4035": tr("Hexagon thin nut ISO 4035 - {diameter}"),
    "ISO4161": tr("Hexagon nut with flange ISO 4161 - {diameter}"),
    "ISO4762": tr("Hexagon socket head cap screw ISO 4762 - {diameter} x {length}"),
    "ISO4766": tr("Set Screw ISO 4766 - {diameter} x {length}"),
    "ISO7040": tr("Prevailing torque type hexagon regular nut ISO 7040 - {diameter}"),
    "ISO7041": tr("Prevailing torque type hexagon nut ISO 7041 - {diameter}"),
    "ISO7043": tr("Prevailing torque type hexagon nut with flange ISO 7043 - {diameter}"),
    "ISO7044": tr("Prevailing torque type hexagon nut with flange ISO 7044 - {diameter}"),
    "ISO7045": tr("Pan head screw ISO 7045 - {diameter} x {length} - H"),
    "ISO7046": tr("Countersunk flat head screw ISO 7046-1 - {diameter} x {length} - H"),
    "ISO7047": tr("Countersunk raised head screw ISO 7047 - {diameter} x {length} - H"),
    "ISO7048": tr("Cheese head screw ISO 7048 - {diameter} x {length} - H"),
    "ISO7049-C": tr("Tapping screw ISO 7049 - {diameter} x {length} - C - H"),
    "ISO7049-F": tr("Tapping screw ISO 7049 - {diameter} x {length} - F - H"),
    "ISO7049-R": tr("Tapping screw ISO 7049 - {diameter} x {length} - R - H"),
    "ISO7089": tr("Washer ISO 7089 - {diameter}"),
    "ISO7090": tr("Washer ISO 7090 - {diameter}"),
    "ISO7092": tr("Washer ISO 7092 - {diameter}"),
    "ISO7093-1": tr("Washer ISO 7093-1 - {diameter}"),
    "ISO7094": tr("Washer ISO 7094 - {diameter}"),
    "ISO7379": tr("Hexagon socket head shoulder screw ISO 7379 - {diameter} x {length}"),
    "ISO7380-1": tr("Hexagon socket button head screw ISO 7380-1 - {diameter} x {length}"),
    "ISO7380-2": tr("Hexagon socket button head screw ISO 7380-2 - {diameter} x {length}"),
    "ISO7434": tr("Set screw ISO 7434 - {diameter} x {length}"),
    "ISO7435": tr("Set screw ISO 7435 - {diameter} x {length}"),
    "ISO7436": tr("Set screw ISO 7436 - {diameter} x {length}"),
    "ISO7719": tr("Prevailing torque type hexagon regular nut ISO 7719 - {diameter}"),
    "ISO7720": tr("Prevailing torque type hexagon nut ISO 7720 - {diameter}"),
    "ISO8673": tr("Hexagon regular nut ISO 8673 - {diameter}"),
    "ISO8674": tr("Hexagon high nut ISO 8674 - {diameter}"),
    "ISO8675": tr("Hexagon thin nut ISO 8675 - {diameter}"),
    "ISO8676": tr("Hexagon head screw ISO 8676 - {diameter} x {length}"),
    "ISO8733": tr("Parallel pin ISO 8733 - {diameter} x {length}"),
    "ISO8734": tr("Parallel pin ISO 8734 - {diameter} x {length}"),
    "ISO8735": tr("Parallel pin ISO 8735 - {diameter} x {length}"),
    "ISO8736": tr("Taper pin ISO 8736 - {diameter} x {length}"),
    "ISO8737": tr("Taper pin ISO 8737 - {diameter} x {length}"),
    "ISO8738": tr("Washer ISO 8738 - {diameter}"),
    "ISO8739": tr("Grooved pin ISO 8739 - {diameter} x {length}"),
    "ISO8740": tr("Grooved pin ISO 8740 - {diameter} x {length}"),
    "ISO8741": tr("Grooved pin ISO 8741 - {diameter} x {length}"),
    "ISO8742": tr("Grooved pin ISO 8742 - {diameter} x {length}"),
    "ISO8743": tr("Grooved pin ISO 8743 - {diameter} x {length}"),
    "ISO8744": tr("Grooved pin ISO 8744 - {diameter} x {length}"),
    "ISO8745": tr("Grooved pin ISO 8745 - {diameter} x {length}"),
    "ISO8746": tr("Grooved pin ISO 8746 - {diameter} x {length}"),
    "ISO8747": tr("Grooved pin ISO 8747 - {diameter} x {length}"),
    "ISO8748": tr("Spring pin ISO 8748 - {diameter} x {length}"),
    "ISO8750": tr("Spring pin ISO 8750 - {diameter} x {length}"),
    "ISO8751": tr("Spring pin ISO 8751 - {diameter} x {length}"),
    "ISO8752": tr("Spring pin ISO 8752 - {diameter} x {length}"),
    "ISO10511": tr("Prevailing torque type hexagon thin nut ISO 10511 - {diameter}"),
    "ISO10512": tr("Prevailing torque type hexagon regular nut ISO 10512 - {diameter}"),
    "ISO10513": tr("Prevailing torque type hexagon high nut ISO 10513 - {diameter}"),
    "ISO10642": tr("Hexagon socket countersunk head screw ISO 10642 - {diameter} x {length}"),
    "ISO10663": tr("Hexagon nut with flange ISO 10663 - {diameter}"),
    "ISO12125": tr("Prevailing torque type hexagon nut with flange ISO 12125 - {diameter}"),
    "ISO12126": tr("Prevailing torque type hexagon nut with flange ISO 12126 - {diameter}"),
    "ISO13337": tr("Spring pin ISO 13337 - {diameter} x {length}"),
    "ISO14579": tr("Hexalobular socket head cap screw ISO 14579 - {diameter} x {length}"),
    "ISO14580": tr("Hexalobular socket cheese head screw ISO 14580 - {diameter} x {length}"),
    "ISO14582": tr("Countersunk head screw ISO 14582 - {diameter} x {length}"),
    "ISO14583": tr("Hexalobular socket pan head screw ISO 14583 - {diameter} x {length}"),
    "ISO14584": tr("Hexalobular socket raised countersunk head screw ISO 14584 - {diameter} x {length}"),
    "ISO21670": tr("Weld nut ISO 21670 - {diameter}"),
    "IUTHeatInsert": tr("IUT[A/B/C] Heat staking insert - {diameter}"),
    "NFE27-619": tr("Solid metal finishing washers NFE27-619 - {diameter}"),
    "PCBSpacer": tr("Wurth WA-SSTII PCB Spacer - {diameter} x {length}"),
    "PCBStandoff": tr("Wurth WA-SSTIII PCB Standoff - {diameter} x {length}"),
    "PEMPressNut": tr("PEM self clinching nut - {diameter} x {tcode}"),
    "PEMStandoff": tr("PEM self clinching standoff - {diameter} x {length}"),
    "PEMStud": tr("PEM self clinching stud - {diameter} x {length}"),
    "SAEJ483a1": tr("Low Crown Acorn Hex Nuts, SAEJ483A, {diameter}"),
    "SAEJ483a2": tr("High Crown Acorn Hex Nuts, SAEJ483A, {diameter}"),
    "ThreadedRod": tr("Threaded rod DIN 975 - {diameter} x {length}"),
    "ThreadedRodInch": tr("UNC Threaded Rod, {diameter} x {length}"),
}
# fmt: on


class FSMakeBomCommand:
    """Generate fasteners bill of materials"""

    def GetResources(self):
        icon = os.path.join(iconPath, "IconBOM.svg")
        return {
            "Pixmap": icon,
            "MenuText": translate("FastenerBase", "Generate BOM"),
            "ToolTip": translate("FastenerBase", "Generate fasteners bill of material"),
        }

    def Activated(self):
        bom_items = defaultdict(int)  # starts at zero when a key is not in the dict
        doc = FreeCAD.ActiveDocument
        # setup the header of the spreadsheet
        sheet = doc.addObject("Spreadsheet::Sheet", "Fasteners_BOM")
        sheet.Label = translate("FastenerBOM", "Fasteners_BOM")
        sheet.setColumnWidth("A", 300)
        sheet.set("A1", translate("FastenerBOM", "Type"))
        sheet.set("B1", translate("FastenerBOM", "Qty"))
        sheet.setAlignment("A1:B1", "center|vcenter|vimplied")
        sheet.setStyle("A1:B1", "bold")

        fastener_objects_in_document = [
            x
            for x in doc.Objects
            if hasattr(x, "Proxy") and isinstance(x.Proxy, FSScrewObject)
        ]
        for obj in fastener_objects_in_document:
            # get total count
            fastener_attributes = dict(obj.Proxy.__dict__)  # make a copy
            # format custom lengths nicely
            if hasattr(obj, "lengthCustom") and obj.length == "Custom":
                if obj.Proxy.baseType.startswith(
                    "ASME"
                ) or obj.Proxy.baseType.startswith("SAE"):
                    nice_custom_length = (
                        str(round(obj.lengthCustom.getValueAs("in"), 3)) + "in"
                    )
                else:
                    nice_custom_length = str(
                        round(obj.lengthCustom.getValueAs("mm"), 2)
                    )
                fastener_attributes["length"] = nice_custom_length
            # handle threaded rods
            elif obj.Proxy.baseType == "ThreadedRod":
                if obj.diameter != "Custom":
                    dia_str = obj.diameter
                else:
                    dia_str = "M" + str(round(obj.diameterCustom.getValueAs("mm"), 2))
                len_val = obj.length
                len_str = str(round(len_val.getValueAs("mm"), 2))
                fastener_attributes["length"] = len_str
                fastener_attributes["diameter"] = dia_str
            elif obj.Proxy.baseType == "ThreadedRodInch":
                if obj.diameter != "Custom":
                    dia_str = obj.diameter
                else:
                    dia_str = str(round(obj.diameterCustom.getValueAs("in"), 3)) + "in"
                len_val = obj.length
                len_str = str(round(len_val.getValueAs("in"), 3)) + "in"
                fastener_attributes["length"] = len_str
                fastener_attributes["diameter"] = dia_str

            key = fastener_designations[obj.Proxy.baseType].format(
                **fastener_attributes
            )
            # handle left-handed fasteners:
            if hasattr(obj, "leftHanded") and obj.leftHanded:
                key += " - LH"
            count = GetTotalObjectRepeats(obj)
            bom_items[key] += count

        line = 2
        for fastener in sorted(bom_items.keys()):
            sheet.set(f"A{line}", fastener)
            sheet.set(f"B{line}", str(bom_items[fastener]))
            line += 1
        doc.recompute()
        return

    def IsActive(self):
        return FreeCADGui.ActiveDocument is not None


FreeCADGui.addCommand("FSMakeBOM", FSMakeBomCommand())
FSCommands.append("FSMakeBOM", "command")

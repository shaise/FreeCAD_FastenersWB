# -*- coding: utf-8 -*-
###################################################################################
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
###################################################################################

from urllib.response import addclosehook
from FreeCAD import Gui
import FreeCAD, FreeCADGui, Part, os

__dir__ = os.path.dirname(__file__)
iconPath = os.path.join(__dir__, 'Icons')
import screw_maker

import FastenerBase
from FastenerBase import FSBaseObject
import ScrewMaker

screwMaker = ScrewMaker.Instance()



ScrewParameters = { "type", "diameter", "matchOuter", "thread", "leftHanded", "length" }
ScrewParametersLC = { "type", "diameter", "matchOuter", "thread", "leftHanded", "length", "lengthCustom" }
RodParameters = { "type", "diameter", "matchOuter", "thread", "leftHanded", "lengthArbitrary",  "diameterCustom", "pitchCustom" }
NutParameters = { "type", "diameter", "matchOuter", "thread", "leftHanded"}
WasherParameters = { "type", "diameter", "matchOuter" }
PCBStandoffParameters = {"type", "diameter", "matchOuter", "thread", "leftHanded", "threadLength", "lenByDiamAndWidth", "lengthCustom", "widthCode" }
PCBSpacerParameters = {"type", "diameter", "matchOuter", "thread", "leftHanded", "lenByDiamAndWidth", "lengthCustom", "widthCode" }
PEMPressNutParameters = {"type", "diameter", "matchOuter", "thread", "leftHanded", "thicknessCode" }
PEMStandoffParameters = {"type", "diameter", "matchOuter", "thread", "leftHanded", "length", "blindness" }

CMD_HELP = 0
CMD_GROUP = 1
CMD_PARAMETER_GRP = 2
FSScrewCommandTable = {
    # type:     help,                      group,      parameter-group
    "ISO4017": ("ISO 4017 Hex head screw", "Hex head", ScrewParametersLC), 
    "ISO4014": ("ISO 4014 Hex head bolt", "Hex head", ScrewParametersLC), 
    "EN1662": ("EN 1662 Hexagon bolt with flange, small series", "Hex head", ScrewParametersLC), 
    "EN1665": ("EN 1665 Hexagon bolt with flange, heavy series", "Hex head", ScrewParametersLC), 
    "DIN571": ("DIN 571 Hex head wood screw", "Hex head", ScrewParametersLC), 

    "ISO4762": ("ISO4762 Hexagon socket head cap screw", "Hexagon socket", ScrewParametersLC), 
    "DIN7984": ("DIN 7984 Hexagon socket head cap screws with low head", "Hexagon socket", ScrewParametersLC), 
    "DIN6912": ("DIN 6912 Hexagon socket head cap screws with low head with centre", "Hexagon socket", ScrewParametersLC), 
    "ISO7380-1": ("ISO 7380 Hexagon socket button head screw", "Hexagon socket", ScrewParametersLC), 
    "ISO7380-2": ("ISO 7380 Hexagon socket button head screws with collar", "Hexagon socket", ScrewParametersLC), 
    "ISO10642": ("ISO 10642 Hexagon socket countersunk head screw", "Hexagon socket", ScrewParametersLC), 
    "ISO7379": ("ISO 7379 Hexagon socket head shoulder screw", "Hexagon socket", ScrewParametersLC), 
    "ISO4026": ("ISO 4026 Hexagon socket set screws with flat point", "Hexagon socket", ScrewParametersLC), 
    "ISO4027": ("ISO 4027 Hexagon socket set screws with cone point", "Hexagon socket", ScrewParametersLC), 
    "ISO4028": ("ISO 4028 Hexagon socket set screws with dog point", "Hexagon socket", ScrewParametersLC), 
    "ISO4029": ("ISO 4029 Hexagon socket set screws with cup point", "Hexagon socket", ScrewParametersLC), 

    "ISO14579": ("ISO 14579 Hexalobular socket head cap screws", "Hexalobular socket", ScrewParametersLC), 
    "ISO14580": ("ISO 14580 Hexalobular socket cheese head screws", "Hexalobular socket", ScrewParametersLC), 
#    "ISO14581": ("ISO 14581 Hexalobular socket countersunk flat head screws", "Hexalobular socket", ScrewParametersLC), 
    "ISO14582": ("ISO 14582 Hexalobular socket countersunk head screws, high head", "Hexalobular socket", ScrewParametersLC), 
    "ISO14583": ("ISO 14583 Hexalobular socket pan head screws", "Hexalobular socket", ScrewParametersLC), 
    "ISO14584": ("ISO 14584 Hexalobular socket raised countersunk head screws", "Hexalobular socket", ScrewParametersLC), 

    "ISO2009": ("ISO 2009 Slotted countersunk flat head screw", "Slotted", ScrewParametersLC), 
    "ISO2010": ("ISO 2010 Slotted raised countersunk head screw", "Slotted", ScrewParametersLC), 
    "ISO1580": ("ISO 1580 Slotted pan head screw", "Slotted", ScrewParametersLC), 
    "ISO1207": ("ISO 1207 Slotted cheese head screw", "Slotted", ScrewParametersLC), 

    "DIN967": ("DIN 967 Cross recessed pan head screws with collar", "H cross", ScrewParametersLC), 
    "ISO7045": ("ISO 7045 Pan head screws type H cross recess", "H cross", ScrewParametersLC), 
    "ISO7046": ("ISO 7046 Countersunk flat head screws H cross r.", "H cross", ScrewParametersLC), 
    "ISO7047": ("ISO 7047 Raised countersunk head screws H cross r.", "H cross", ScrewParametersLC), 
    "ISO7048": ("ISO 7048 Cheese head screws with type H cross r.", "H cross", ScrewParametersLC), 

    "ISO4032": ("ISO 4032 Hexagon nuts, Style 1", "Nut", NutParameters), 
    "ISO4033": ("ISO 4033 Hexagon nuts, Style 2", "Nut", NutParameters), 
    "ISO4035": ("ISO 4035 Hexagon thin nuts, chamfered", "Nut", NutParameters), 
#    "ISO4036": ("ISO 4035 Hexagon thin nuts, unchamfered", "Nut", NutParameters), 
    "EN1661": ("EN 1661 Hexagon nuts with flange", "Nut", NutParameters), 
    "DIN917": ("DIN917 Cap nuts, thin style", "Nut", NutParameters), 
    "DIN1587": ("DIN 1587 Cap nuts", "Nut", NutParameters), 
    "DIN557": ("DIN 557 Square nuts", "Nut", NutParameters), 
    "DIN562": ("DIN 562 Square nuts", "Nut", NutParameters), 
    "DIN985": ("DIN 985 Nyloc nuts", "Nut", NutParameters), 

    "ISO7089": ("ISO 7089 Washer", "Washer", WasherParameters), 
    "ISO7090": ("ISO 7090 Plain Washers, chamfered - Normal series", "Washer", WasherParameters), 
#    "ISO7091": ("ISO 7091 Plain washer - Normal series Product Grade C", "Washer", WasherParameters),   # same as 7089??
    "ISO7092": ("ISO 7092 Plain washers - Small series", "Washer", WasherParameters), 
    "ISO7093-1": ("ISO 7093-1 Plain washers - Large series", "Washer", WasherParameters), 
    "ISO7094": ("ISO 7094 Plain washers - Extra large series", "Washer", WasherParameters), 
    "NFE27-619": ("NFE27-619 Countersunk washer", "Washer", WasherParameters), 

# Inch

    "ASMEB18.2.1.6": ("ASME B18.2.1 UNC Hex head screws", "Hex head", ScrewParametersLC), 
    "ASMEB18.2.1.8": ("ASME B18.2.1 UNC Hex head screws with flange", "Hex head", ScrewParametersLC), 

    "ASMEB18.3.1A": ("ASME B18.3 UNC Hex socket head cap screws", "Hexagon socket", ScrewParametersLC), 
    "ASMEB18.3.1G": ("ASME B18.3 UNC Hex socket head cap screws with low head", "Hexagon socket", ScrewParametersLC), 
    "ASMEB18.3.2": ("ASME B18.3 UNC Hex socket countersunk head screws", "Hexagon socket", ScrewParametersLC), 
    "ASMEB18.3.3A": ("ASME B18.3 UNC Hex socket button head screws", "Hexagon socket", ScrewParametersLC), 
    "ASMEB18.3.3B": ("ASME B18.3 UNC Hex socket button head screws with flange", "Hexagon socket", ScrewParametersLC), 
    "ASMEB18.3.4": ("ASME B18.3 UNC Hexagon socket head shoulder screws", "Hexagon socket", ScrewParametersLC), 
    "ASMEB18.3.5A": ("ASME B18.3 UNC Hexagon socket set screws with flat point", "Hexagon socket", ScrewParametersLC), 
    "ASMEB18.3.5B": ("ASME B18.3 UNC Hexagon socket set screws with cone point", "Hexagon socket", ScrewParametersLC), 
    "ASMEB18.3.5C": ("ASME B18.3 UNC Hexagon socket set screws with dog point", "Hexagon socket", ScrewParametersLC), 
    "ASMEB18.3.5D": ("ASME B18.3 UNC Hexagon socket set screws with cup point", "Hexagon socket", ScrewParametersLC), 

    "ASMEB18.6.3.1A": ("ASME B18.6.3 UNC slotted countersunk flat head screws", "Slotted", ScrewParametersLC), 

    "ASMEB18.5.2": ("ASME B18.5 UNC Round head square neck bolts", "Other head", ScrewParametersLC), 

    "ASMEB18.2.2.1A": ("ASME B18.2.2 UNC Machine screw nuts", "Nut", NutParameters), 
    "ASMEB18.2.2.4A": ("ASME B18.2.2 UNC Hexagon nuts", "Nut", NutParameters), 
    "ASMEB18.2.2.4B": ("ASME B18.2.2 UNC Hexagon thin nuts", "Nut", NutParameters), 

    "ASMEB18.21.1.12A": ("ASME B18.21.1 UN washers, narrow series", "Washer", WasherParameters), 
    "ASMEB18.21.1.12B": ("ASME B18.21.1 UN washers, regular series", "Washer", WasherParameters), 
    "ASMEB18.21.1.12C": ("ASME B18.21.1 UN washers, wide series", "Washer", WasherParameters), 

    "ScrewTap": ("Metric threaded rod for tapping holes", "ThreadedRod", RodParameters), 
    "ScrewTapInch": ("Inch threaded rod for tapping holes", "ThreadedRod", RodParameters), 
    "ScrewDie": ("Tool object to cut external metric threads", "ThreadedRod", RodParameters), 
    "ScrewDieInch": ("Tool object to cut external non-metric threads", "ThreadedRod", RodParameters), 
    "ThreadedRod": ("DIN 975 metric threaded rod", "ThreadedRod", RodParameters), 
    "ThreadedRodInch": ("UNC threaded rod", "ThreadedRod", RodParameters), 
    "PEMPressNut": ("PEM Self Clinching nut", "PEM Inserts", PEMPressNutParameters), 
    "PEMStandoff": ("PEM Self Clinching standoff", "PEM Inserts", PEMStandoffParameters), 
    "PEMStud": ("PEM Self Clinching stud", "PEM Inserts", ScrewParameters),
    "PCBStandoff": ("Wurth WA-SSTII  PCB standoff", "PEM Inserts", PCBStandoffParameters), 
    "PCBSpacer": ("Wurth WA-SSTII PCB spacer", "PEM Inserts", PCBSpacerParameters), 
    "IUTHeatInsert": ("IUT[A/B/C] Heat Staked Metric Insert", "PEM Inserts", NutParameters), 
}

def GetParams(type):
    if not type in FSScrewCommandTable:
        return {}
    return FSScrewCommandTable[type][CMD_PARAMETER_GRP]

class FastenerAttribs:
    def __init__(self, *args):
        # backup attribs - all possible object properties
        self.type = None
        self.diameter = None
        self.thread = None
        self.leftHanded = None
        self.matchOuter = None
        self.length = None
        self.lengthCustom = None
        self.width = None
        self.diameterCustom = None
        self.pitchCustom = None
        self.tcode = None
        self.blind = None
        self.screwLength = None
        
        # calculated attribs
        self.familyType = ""
        self.calc_diam = None
        self.calc_pitch = None
        self.calc_len = None

        # some extra params
        self.dimTable = None
    
    def GetBackupAttribNames(self):
        return ['type', 'diameter', 'thread', 'leftHanded', 'matchOuter', 'length', 'lengthCustom', 'width', 
            'diameterCustom', 'pitchCustom', 'tcode', 'blind', 'screwLength']

    def BackupObject(self, obj):
        for attr in self.GetBackupAttribNames():
            if hasattr(obj, attr):
                setattr(self, attr, getattr(obj, attr))

    # get a hash key for the params (for cashing similar objects)
    def GetKey(self):
        key = ""
        for attr in self.GetBackupAttribNames():
            val = getattr(self, attr)
            if val is not None:
                key += attr + ":" + str(val) + "|"
        return key.rstrip("|")
       

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

    def VerifyMissingAttrs(self, obj, type = None):
        self.updateProps(obj)
        # the backup attribs holds a copy of the object attribs. It is used to detect which attrib was
        # changed when executing the command. It should hold all possible object attribs. Unused ones will be None
        if not hasattr(self, 'backupAttrs'):
            self.backupAttrs = FastenerAttribs()
        ba = self.backupAttrs
        
        # basic parameters
        # all objects must have type - since they all use the same command
        if not hasattr(obj, "type"):
            if type is None: # probably pre V0.4.0 object
                if hasattr(self,"originalType"):
                    type = self.originalType
                    FreeCAD.Console.PrintMessage("using original type: " + type + "\n")
            obj.addProperty("App::PropertyEnumeration", "type", "Parameters", "Screw type").type = self.GetCompatibleTypes(type)
            obj.type = type
        else:
            type = obj.type
        
        if obj.type == "ISO7380":
            obj.type = type = "ISO7380-1"  # backward compatibility - remove at FreeCAD version 0.23 
        ba.familyType = screwMaker.GetTypeName(type)
 
        if not hasattr(obj, "diameter"):
            diameters = screwMaker.GetAllDiams(type)
            diameters.insert(0, 'Auto')
            if "diameterCustom" in GetParams(type):
                diameters.append("Custom")
            obj.addProperty("App::PropertyEnumeration", "diameter", "Parameters", "Standard diameter").diameter = diameters
            diameter = diameters[1]
        else:
            diameter = obj.diameter
        params = GetParams(type)

        # thread parameters
        if "thread" in params and not hasattr(obj, "thread"):
            obj.addProperty("App::PropertyBool", "thread", "Parameters", "Generate real thread").thread = False
        if "leftHanded" in params and not hasattr(obj, 'leftHanded'):
            obj.addProperty("App::PropertyBool", "leftHanded", "Parameters", "Left handed thread").leftHanded = False
        if "matchOuter" in params and not hasattr(obj, "matchOuter"):
            obj.addProperty("App::PropertyBool", "matchOuter", "Parameters", "Match outer thread diameter").matchOuter = FastenerBase.FSMatchOuter

        # width parameters
        if "widthCode" in params and not hasattr(obj, "width"):
            obj.addProperty("App::PropertyEnumeration", "width", "Parameters", "Body width code").width = screwMaker.GetAllWidthcodes(type, diameter)

        # length parameters
        addCustomLen = "lengthCustom" in params and not hasattr(obj, "lengthCustom")
        if "length" in params or "lenByDiamAndWidth" in params:
            # if diameter == "Auto":
            #     diameter = self.initialDiameter
            if "lenByDiamAndWidth" in params:
                slens = screwMaker.GetAllLengths(type, diameter, addCustomLen, obj.width)
            else:
                slens = screwMaker.GetAllLengths(type, diameter, addCustomLen)
            if not hasattr(obj, 'length'):
                obj.addProperty("App::PropertyEnumeration", "length", "Parameters", "Screw length").length = slens
            elif addCustomLen :
                origLen = obj.length
                obj.length = slens
                if origLen in slens:
                    obj.length = origLen
            if addCustomLen:
                obj.addProperty("App::PropertyLength", "lengthCustom", "Parameters", "Custom length").lengthCustom = self.inswap(slens[0])

        # custom size parameters
        if "lengthArbitrary" in params and not hasattr(obj, "length"):
            obj.addProperty("App::PropertyLength", "length", "Parameters", "Screw length").length = 20.0
        if "diameterCustom" in params and not hasattr(obj, "diameterCustom"):
            obj.addProperty("App::PropertyLength", "diameterCustom", "Parameters", "Screw major diameter custom").diameterCustom = 6
        if "pitchCustom" in params and not hasattr(obj, "pitchCustom"):
            obj.addProperty("App::PropertyLength", "pitchCustom", "Parameters", "Screw pitch custom").pitchCustom = 1.0

        # thickness
        if "thicknessCode" in params and not hasattr(obj, "tcode"):
            obj.addProperty("App::PropertyEnumeration", "tcode", "Parameters", "Thickness code").tcode = screwMaker.GetAllTcodes(type, diameter)

        # misc
        if "blindness" in params and not hasattr(obj, "blind"):
            obj.addProperty("App::PropertyBool", "blind", "Parameters", "Blind Standoff type").blind = False
        if "threadLength" in params and not hasattr(obj, "screwLength"):
            obj.addProperty("App::PropertyLength", "screwLength", "Parameters", "Threaded part length").screwLength = screwMaker.GetThreadLength(type, diameter)

        ba.BackupObject(obj)

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
        return str(val).rstrip("0").rstrip('.')

    def ActiveLength(self, obj):
        if not hasattr(obj, 'length'):
            return '0'
        if type(obj.length) != type(""):
            return self.CleanDecimals(float(obj.length))
        if obj.length == 'Custom':
            return self.CleanDecimals(float(obj.lengthCustom))
        return obj.length

    def paramChanged(self, param, value):
        # if not hasattr(self.backupAttrs, param):
        #     return True
        return getattr(self.backupAttrs, param) != value

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
        ba = self.backupAttrs
 
        # handle type changes
        typechange = False
        if fp.type != ba.type:
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
        diameterchange = ba.diameter != fp.diameter
        matchouterchange = ba.matchOuter != fp.matchOuter
        widthchange = hasattr(fp, "width") and ba.width != fp.width


        if fp.diameter == 'Auto' or matchouterchange:
            ba.calc_diam = screwMaker.AutoDiameter(fp.type, shape, baseobj, fp.matchOuter)
            fp.diameter = ba.calc_diam
            diameterchange = True
        elif fp.diameter == 'Custom' and hasattr(fp, "diameterCustom"):
            ba.calc_diam = str(fp.diameterCustom.Value)
        else:
            ba.calc_diam = fp.diameter

        # handle length changes
        if hasattr(fp, 'length'):
            if "lengthArbitrary" in params:
                # arbitrary lengths
                l = fp.length.Value
                if l < 2.0:
                    l = 2.0
                    fp.length = 2.0
                ba.calc_len = str(l)
            else:
                # fixed lengths
                width = None
                if "lenByDiamAndWidth" in params:
                    width = fp.width
                if self.paramChanged('length', fp.length):
                    if fp.length != 'Custom' and hasattr(fp, 'lengthCustom'):
                        fp.lengthCustom = FastenerBase.LenStr2Num(fp.length)  # ***
                elif ba.lengthCustom is not None and fp.lengthCustom != ba.lengthCustom:
                    fp.length = 'Custom'
                origLen = self.ActiveLength(fp)
                origIsCustom = fp.length == 'Custom'
                ba.calc_diam, l, auto_width = screwMaker.FindClosest(fp.type, ba.calc_diam, origLen, width)
                if ba.calc_diam != fp.diameter:
                    diameterchange = True
                    fp.diameter = ba.calc_diam
                if width != auto_width:
                    widthchange = True
                    fp.width = screwMaker.GetAllWidthcodes(fp.type, fp.diameter)
                    fp.width = width = auto_width

                if origIsCustom:
                    l = origLen

                if l != origLen or diameterchange or typechange or widthchange:
                    if diameterchange or typechange or widthchange:
                        fp.length = screwMaker.GetAllLengths(fp.type, fp.diameter, hasattr(fp, 'lengthCustom'), width)
                        if hasattr(fp, 'screwLength'):
                            fp.screwLength = screwMaker.GetThreadLength(fp.type, fp.diameter)
                    if origIsCustom:
                        fp.length = 'Custom'
                    else:
                        fp.length = l
                        if hasattr(fp, 'lengthCustom'):
                            fp.lengthCustom = l
                ba.calc_len = l
        else:
            ba.calc_len = None

        if diameterchange and "thicknessCode" in params:
            tcodes = screwMaker.GetAllTcodes(fp.type, fp.diameter)
            oldcode = fp.tcode
            fp.tcode = tcodes
            if oldcode in tcodes:
                fp.tcode = oldcode

        if fp.diameter == 'Custom' and hasattr(fp, "pitchCustom"):
            ba.calc_pitch = fp.pitchCustom.Value
        else:
            ba.calc_pitch = None

        screwMaker.updateFastenerParameters()

        ba.BackupObject(fp)

        # Here we are generating a new key if is not present in cache. This key is also used in method 
        # FastenerBase.FSCacheRemoveThreaded. This way it will allow to correctly recompute 
        # the threaded screws and nuts in case of changing the 3D Printing settings in Fasteners Workbench.
        (key, s) = FastenerBase.FSGetKey(ba.GetKey())
        if s is None:
            s = screwMaker.createFastener(ba)
            FastenerBase.FSCache[key] = s
        else:
            FreeCAD.Console.PrintLog("Using cached object\n")

        dispDiam = self.CleanDecimals(ba.calc_diam)
        if hasattr(fp, 'length'):
            dispLen = self.ActiveLength(fp)
            dispWidth = ""
            if hasattr(fp, 'width'):
                dispWidth = 'x' + fp.width
            label = dispDiam + dispWidth + 'x' + dispLen
            if ba.leftHanded:
                label += 'LH'
            label += '-' + ba.familyType
            fp.Label = label
        else:
            fp.Label = dispDiam + '-' + ba.familyType

        # ba.familyType = s[1]
        fp.Shape = s

        if shape is not None:
            # feature = FreeCAD.ActiveDocument.getObject(self.Proxy)
            # fp.Placement = FreeCAD.Placement() # reset placement
            FastenerBase.FSMoveToObject(fp, shape, fp.invert, fp.offset.Value)

    # def getItemText():
    #  return ba.familyType


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
        icon = os.path.join(iconPath, self.Type + '.svg')
        return {'Pixmap': icon,
                # the name of a svg file available in the resources
                'MenuText': "Add " + self.Help,
                'ToolTip': self.Help}

    def Activated(self):
        for selObj in FastenerBase.FSGetAttachableSelections():
            a = FreeCAD.ActiveDocument.addObject("Part::FeaturePython",
                                                 self.TypeName)
            FSScrewObject(a, self.Type, selObj)
            a.Label = a.Proxy.backupAttrs.familyType
            FSViewProviderTree(a.ViewObject)
        FreeCAD.ActiveDocument.recompute()
        return

    def IsActive(self):
        return Gui.ActiveDocument is not None

def FSAddScrewCommand(type):
    cmd = 'FS' + type
    Gui.addCommand(cmd, FSScrewCommand(type, FSScrewCommandTable[type][CMD_HELP]))
    FastenerBase.FSCommands.append(cmd, "screws", FSScrewCommandTable[type][CMD_GROUP])

# generate all commands
for key in FSScrewCommandTable:
    FSAddScrewCommand(key)

# for backward compatibility, add old objects as derivative of FSScrewObject
class FSWasherObject(FSScrewObject):
    pass
class FSScrewRodObject(FSScrewObject):
    def onDocumentRestored(self, obj):
        self.originalType=obj.Proxy.type
        super().onDocumentRestored(obj)
    
class FSScrewDieObject(FSScrewObject):
    def onDocumentRestored(self, obj):
        self.originalType=obj.Proxy.type
        super().onDocumentRestored(obj)

class FSThreadedRodObject(FSScrewObject):
    def onDocumentRestored(self, obj):
        self.originalType=obj.Proxy.type
        super().onDocumentRestored(obj)

## add fastener types
FastenerBase.FSAddFastenerType("Screw")
FastenerBase.FSAddFastenerType("Washer", False)
FastenerBase.FSAddFastenerType("Nut", False)
FastenerBase.FSAddFastenerType("ThreadedRod", True, False)
FastenerBase.FSAddFastenerType("PressNut", False)
FastenerBase.FSAddFastenerType("Standoff")
FastenerBase.FSAddFastenerType("Stud")
FastenerBase.FSAddFastenerType("HeatSet", False)
for item in ScrewMaker.screwTables:
    FastenerBase.FSAddItemsToType(ScrewMaker.screwTables[item][0], item)

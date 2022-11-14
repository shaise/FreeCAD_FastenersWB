# -*- coding: utf-8 -*-
###############################################################################
#
#  FastenerBase.py
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
from FreeCAD import Base
from PySide import QtGui
import FreeCAD
import FreeCADGui
import Part
import os
import math
import sys
from pathlib import Path
import DraftVecUtils
import re
from TranslateUtils import translate
from FSutils import csv2dict
from FSutils import iconPath
from FSutils import fsdatapath

matchOuterButton = None
matchOuterButtonText = translate("FastenerBase", 'Match for pass hole')
matchInnerButton = None
matchInnerButtonText = translate("FastenerBase", 'Match for tap hole')


# function to open a csv file and convert it to a dictionary
FsData = {}
FsTitles = {}
filelist = Path(fsdatapath).glob('*.csv')
for item in filelist:
    tables = csv2dict(str(item), item.stem, fieldsnamed=True)
    for tablename in tables.keys():
        if tablename == 'titles':
            FsTitles.update(tables[tablename])
        else:
            FsData[tablename] = tables[tablename]


class FSBaseObject:
    '''Base Class for all fasteners'''

    def __init__(self, obj, attachTo):
        obj.addProperty("App::PropertyDistance", "offset",
                        "Parameters", "Offset from surface").offset = 0.0
        obj.addProperty("App::PropertyBool", "invert",
                        "Parameters", "Invert screw direction").invert = False
        obj.addProperty("App::PropertyXLinkSub", "baseObject",
                        "Parameters", "Base object").baseObject = attachTo

    def updateProps(self, obj):
        if obj.getTypeIdOfProperty("baseObject") != "App::PropertyXLinkSub":
            linkedObj = obj.baseObject
            obj.removeProperty("baseObject")
            obj.addProperty("App::PropertyXLinkSub", "baseObject",
                            "Parameters", "Base object").baseObject = linkedObj


class FSGroupCommand:
    def __init__(self, cmds, menuText, toolTip):
        self.commands = cmds
        self.menuText = menuText
        self.toolTip = toolTip

    def GetCommands(self):
        # a tuple of command names that you want to group
        return tuple(self.commands)
        # return ('FSFlip', 'FSMove', 'FSSimple', 'FSFillet')

    def GetResources(self):
        return {'MenuText': self.menuText, 'ToolTip': self.toolTip}

    def IsActive(self):
        return Gui.ActiveDocument is not None
    # def Activated(self, index): # index is an int in the range [0, len(GetCommands)


FSParam = FreeCAD.ParamGet("User parameter:BaseApp/Preferences/Mod/Fasteners")
# GroupButtonMode: 0 = none, 1 = separate toolbar 2 = drop down buttons
GroupButtonMode = FSParam.GetInt("ScrewToolbarGroupMode", 1)


class FSCommandList:
    def __init__(self):
        self.commands = {}

    def append(self, cmd, group="screws", subgroup=None):
        if not (group in self.commands):
            self.commands[group] = []
        self.commands[group].append((cmd, subgroup))

    def getCommands(self, group):
        cmdlist = []
        cmdsubs = {}
        for cmd in self.commands[group]:
            command, subgroup = cmd
            if subgroup is not None and GroupButtonMode > 0:
                if not (subgroup in cmdsubs):
                    cmdsubs[subgroup] = []
                    if GroupButtonMode == 2:
                        cmdlist.append(subgroup) # .replace(" ", ""))
                        cmdlist.append("Separator")
                cmdsubs[subgroup].append(command)
            else:
                cmdlist.append(command)
        for subcommand in cmdsubs:
            if GroupButtonMode == 2:
                Gui.addCommand(subcommand, #.replace(" ", ""),
                    FSGroupCommand(cmdsubs[subcommand], subcommand, subcommand))
            else:
                cmdlist.append((subcommand, #.replace(" ", ""),
                               cmdsubs[subcommand], subcommand))
        return cmdlist


FSCommands = FSCommandList()
FSClassIcons = {}
FSLastInvert = False


def FSGetCommands(group="screws"):
    return FSCommands.getCommands(group)


# fastener types

class FSFastenerType:
    def __init__(self, typeName, hasLength, lengthFixed):
        self.typeName = typeName
        self.hasLength = hasLength
        self.lengthFixed = lengthFixed
        self.items = []


FSFastenerTypeDB = {}


def FSAddFastenerType(typeName, hasLength=True, lengthFixed=True):
    FSFastenerTypeDB[typeName] = FSFastenerType(
        typeName, hasLength, lengthFixed)


def FSAddItemsToType(typeName, item):
    if not (typeName in FSFastenerTypeDB):
        return
    FSFastenerTypeDB[typeName].items.append(item)


# common helpers

def FSScrewStr(obj):
    '''Return the textual representation of the screw diameter x length
    + optional handedness ([M]<dia>x<len>[LH]), also accounting for
    custom size properties'''
    dia = obj.diameter if obj.diameter != 'Custom' else obj.diameterCustom
    if isinstance(dia, FreeCAD.Units.Quantity):
        dia = str(float(dia.Value)).rstrip('0').rstrip('.')
    length = obj.length if obj.length != 'Custom' else obj.lengthCustom
    if isinstance(length, FreeCAD.Units.Quantity):
        length = str(float(length.Value)).rstrip('0').rstrip('.')
    desc = dia + "x" + length
    if obj.leftHanded:
        desc += 'LH'
    return desc


# show traceback of system error
def FSShowError():
    lastErr = sys.exc_info()
    tb = lastErr[2]
    tbnext = tb
    x = 10
    while tbnext is not None and x > 0:
        FreeCAD.Console.PrintError(
            "At " + tbnext.tb_frame.f_code.co_filename + " Line " + str(tbnext.tb_lineno) + "\n")
        tbnext = tbnext.tb_next
        x = x - 1
    FreeCAD.Console.PrintError(
        str(lastErr[1]) + ": " + lastErr[1].__doc__ + "\n")


# get instance of a toolbar item
def FSGetToolbarItem(tname, iname):
    mw = QtGui.QApplication.activeWindow()
    tb = None
    for c in mw.children():
        if isinstance(c, QtGui.QToolBar) and c.windowTitle() == tname:
            tb = c
            break
    if tb is None:
        return None
    for c in tb.children():
        if isinstance(c, QtGui.QToolButton) and c.text() == iname:
            return c
    return None


# fastener chach - prevent recreation of same fasteners
FSCache = {}


def FSGetKey(*args):
    obj = None
    key = 'FS'
    for arg in args:
        if not arg is None:
            key = key + '|' + str(arg)
    if key in FSCache:
        FreeCAD.Console.PrintLog("Using cached shape for: " + key + "\n")
        return (key, FSCache[key])
    return (key, None)


# removes all cached fasteners with real thread
def FSCacheRemoveThreaded():
    for key in list(FSCache.keys()):
        if key.find('thread:True') > 0:
            FreeCAD.Console.PrintLog("Removing cached shape: " + key + "\n")
            del FSCache[key]

# extruct the diameter code (metric/imperial) from the given string


def CleanM(m):
    res = re.findall("M[\d.]+|#\d+|[\d /]+in|[\d.]+ mm", m)
    # FreeCAD.Console.PrintMessage(m + " -> " + res[0] + "\n")
    return res[0]


def MToFloat(m):
    return float(CleanM(m).lstrip("M"))

# accepts formats: 'Mx', '(Mx)' 'YYYMx' 'Mx-YYY'


def DiaStr2Num(DiaStr):
    DiaStr = CleanM(DiaStr)
    return FsData["DiaList"][DiaStr][0]

# inch tolerant version of length string to number converter


def LenStr2Num(LenStr):
    # inch diameters of format 'x y/z\"'
    if 'in' in LenStr:
        components = LenStr.strip('in').split(' ')
        total = 0
        for item in components:
            if '/' in item:
                subcmpts = item.split('/')
                total += float(subcmpts[0]) / float(subcmpts[1])
            else:
                total += float(item)
        DiaFloat = total * 25.4
    # if there are no identifying unit chars, default to mm
    else:
        LenStr = LenStr.strip(" m")
        DiaFloat = float(LenStr)
    return DiaFloat


def FSRemoveDigits(txt):
    res = ''
    for c in txt:
        if not c.isdigit():
            res += c
    return res


# get total count of a selected object taking arrays/links into account
def GetTotalObjectRepeats(obj):
    cnt = 1 if obj.Visibility else 0

    for parent in obj.InList:
        if parent.TypeId in ('App::LinkElement', 'App::DocumentObjectGroup'):
            continue

        numreps = 0

        if parent.TypeId == 'App::Part':
            if obj.Visibility:
                cnt -= 1  # obj has already been counted, without this we would count it twice
                numreps = 1
        elif parent.TypeId == 'App::Link':
            if parent.ElementCount > 0:
                numreps = parent.VisibilityList.count(
                    True)  # note: VisibilityList is a tuple
            else:
                numreps = 1
        # Draft clones and arrays:
        elif not hasattr(parent, 'Proxy'):
            continue
        elif not hasattr(parent.Proxy, 'Type'):
            continue
        elif parent.Proxy.Type == 'Clone':
            numreps = 1
        elif parent.Proxy.Type in ('Array', 'PathArray', 'PointArray'):
            # All Link arrays (ortho, polar, circular, path and point) can be
            # expanded to control the visibility of individual elements via its
            # VisibilityList. A Link array that has never been expanded has an
            # empty VisibilityList so we need to check for that.
            if hasattr(parent, 'VisibilityList') and parent.VisibilityList:
                numreps = parent.VisibilityList.count(True)
            # path arrays, point arrays and all Link arrays have a Count property:
            elif hasattr(parent, 'Count'):
                numreps = parent.Count
            # non-Link ortho arrays:
            elif parent.ArrayType == 'ortho':
                numreps = parent.NumberX * parent.NumberY * parent.NumberZ
            # non-Link polar arrays:
            elif parent.ArrayType == 'polar':
                numreps = parent.NumberPolar
            # non-Link circular arrays are not handled.

        if numreps != 0:
            parentreps = GetTotalObjectRepeats(parent)
            # print('Parent:' + parent.Name + '/' + parent.TypeId + ', Reps:' + str(parentreps))
            cnt += numreps * parentreps

    return cnt


class FSFaceMaker:
    '''Create a face point by point on the x,z plane'''

    def __init__(self):
        self.Reset()

    def Reset(self):
        self.edges = []
        self.firstPoint = None

    def AddPoint(self, x, z):
        curPoint = FreeCAD.Base.Vector(x, 0, z)
        if self.firstPoint is None:
            self.firstPoint = curPoint
        else:
            self.edges.append(Part.makeLine(self.lastPoint, curPoint))
        self.lastPoint = curPoint
        # FreeCAD.Console.PrintLog("Add Point: " + str(curPoint) + "\n")

    def StartPoint(self, x, z):
        self.Reset()
        self.AddPoint(x, z)

    # add an arc starting at last point and going through x1,z1 and x2,z2
    def AddArc(self, x1, z1, x2, z2):
        midPoint = FreeCAD.Base.Vector(x1, 0, z1)
        endPoint = FreeCAD.Base.Vector(x2, 0, z2)
        self.edges.append(
            Part.Arc(self.lastPoint, midPoint, endPoint).toShape())
        self.lastPoint = endPoint

    # add an arc starting at last point, with relative center xc, zc and angle a
    def AddArc2(self, xc, zc, a):
        # convert to radians
        a = math.radians(a)
        # get absolute center
        xac = self.lastPoint.x + xc
        zac = self.lastPoint.z + zc
        # start angle
        sa = math.atan2(-zc, -xc)
        # radius
        r = math.sqrt(xc * xc + zc * zc)
        # middle point
        sa += a / 2.0
        # FreeCAD.Console.PrintLog("ang1: " + str(math.degrees(sa)) + "\n")
        x1 = xac + r * math.cos(sa)
        z1 = zac + r * math.sin(sa)
        # end point
        sa += a / 2.0
        # FreeCAD.Console.PrintLog("ang2: " + str(math.degrees(sa)) + "\n")
        x2 = xac + r * math.cos(sa)
        z2 = zac + r * math.sin(sa)
        self.AddArc(x1, z1, x2, z2)

    # add B-Spline starting at last point and going through (x1,z1) (x2,z2) ... (xn,zn)
    # example: contour.AddBSpline(0, 0, 0, 1, 1, 0)
    def AddBSpline(self, *args):
        l = len(args)
        if l < 4 or (l & 1) == 1:
            FreeCAD.Console.PrintError(
                "FSFaceMaker.AddBSpline: invalid num of args, must be even number >= 4")
            return
        pt = self.lastPoint
        pts = []
        pts.append(pt)
        for i in range(0, l, 2):
            pt = FreeCAD.Base.Vector(args[i], 0, args[i + 1])
            pts.append(pt)
        self.edges.append(Part.BSplineCurve(pts).toShape())
        self.lastPoint = pt

    def AddPoints(self, *args):
        for arg in args:
            if len(arg) == 2:
                self.AddPoint(arg[0], arg[1])
            elif len(arg) == 3:
                self.AddArc2(arg[0], arg[1], arg[2])
            elif len(arg) == 4:
                self.AddArc(arg[0], arg[1], arg[2], arg[3])

    def GetWire(self):
        return Part.Wire(self.edges)

    def GetClosedWire(self):
        self.edges.append(Part.makeLine(self.lastPoint, self.firstPoint))
        w = Part.Wire(self.edges)
        return w

    def GetFace(self):
        w = self.GetClosedWire()
        return Part.Face(w)


def FSAutoDiameterM(holeObj, table, tablepos):
    res = 'M5'
    if holeObj is not None and hasattr(holeObj, 'Curve') and hasattr(holeObj.Curve, 'Radius'):
        d = holeObj.Curve.Radius * 2
        mindif = 10.0
        for m in table:
            if tablepos == -1:
                dia = DiaStr2Num(m) + 0.1
            else:
                dia = table[m][tablepos] + 0.1
            if dia > d:
                dif = dia - d
                if dif < mindif:
                    mindif = dif
                    res = m
    return res


class FSViewProviderIcon:
    """A View provider for custom icon"""

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
        for type in FSClassIcons:
            if isinstance(self.Object.Proxy, type):
                return os.path.join(iconPath, FSClassIcons[type])
        return None


def GetEdgeName(obj, edge):
    i = 1
    for e in obj.Edges:
        if e.isSame(edge):
            return 'Edge' + str(i)
        i = i + 1
    return None


def PositionDone(center, radius, done_list, tol=1e-6):
    '''Check if the `position` of an edge is already processed by comparing
    its center and radius against data in a list
    '''

    for itm in done_list:
        if center.isEqual(itm[0], tol) and math.isclose(radius, itm[1], abs_tol=tol):
            return True
    return False


def FSGetAttachableSelections():
    asels = []
    for selObj in Gui.Selection.getSelectionEx():
        baseObjectNames = selObj.SubElementNames
        obj = selObj.Object
        grp = obj.getParentGeoFeatureGroup()
        if grp is not None and hasattr(grp, "TypeId") and grp.TypeId == "PartDesign::Body":
            obj = grp
        position_done_list = []  # list with sublists to store the center and radius
        # of processed edges to avoid duplicate fasteners

        for baseObjectName in baseObjectNames:
            shape = obj.Shape.getElement(baseObjectName)

            # add explicitly selected edges
            if hasattr(shape, "Curve"):
                if not hasattr(shape.Curve, "Center"):
                    continue
                if not hasattr(shape.Curve, "Radius"):
                    continue
                if PositionDone(shape.Curve.Center, shape.Curve.Radius, position_done_list):
                    continue
                asels.append((obj, [baseObjectName]))
                position_done_list.append(
                    [shape.Curve.Center, shape.Curve.Radius])
                FreeCAD.Console.PrintLog(
                    "Linking to " + obj.Name + "[" + baseObjectName + "].\n")

            # add edges of selected faces
            elif isinstance(shape, Part.Face):
                outer_edge_list = shape.OuterWire.Edges
                for edge in shape.Edges:
                    if not hasattr(edge, "Curve"):
                        continue
                    if not hasattr(edge.Curve, "Center"):
                        continue
                    if not hasattr(edge.Curve, "Radius"):
                        continue
                    if PositionDone(edge.Curve.Center, edge.Curve.Radius, position_done_list):
                        continue
                    for outer_edge in outer_edge_list:
                        if outer_edge.isSame(edge):
                            edge = None
                            break
                    if edge is None:
                        continue
                    edgeName = GetEdgeName(obj.Shape, edge)
                    if edgeName is None:
                        continue
                    asels.append((obj, [edgeName]))
                    position_done_list.append(
                        [edge.Curve.Center, edge.Curve.Radius])
                    FreeCAD.Console.PrintLog(
                        "Linking to " + obj.Name + "[" + edgeName + "].\n")

    if len(asels) == 0:
        asels.append(None)
    return asels


def FSMoveToObject(ScrewObj_m, attachToObject, invert, offset):
    Pnt1 = None
    Axis1 = None
    Axis2 = None
    s = attachToObject
    if hasattr(s, "Curve"):
        if hasattr(s.Curve, "Center"):
            Pnt1 = s.Curve.Center
            Axis1 = s.Curve.Axis
            # FreeCAD.Console.PrintMessage("center: "+ str(Pnt1) + "\n")
    if hasattr(s, 'Surface'):
        # print 'the object is a face!'
        if hasattr(s.Surface, 'Axis'):
            Axis1 = s.Surface.Axis

    if hasattr(s, 'Point'):
        FreeCAD.Console.PrintLog(
            "the object seems to be a vertex! " + str(s.Point) + "\n")
        Pnt1 = s.Point

    if Axis1 is not None:
        if invert:
            Axis1 = Base.Vector(0, 0, 0) - Axis1

        Pnt1 = Pnt1 + Axis1 * offset
        # FreeCAD.Console.PrintLog( "Got Axis1: " + str(Axis1) + "\n")
        Axis2 = Base.Vector(0.0, 0.0, 1.0)
        Axis2_minus = Base.Vector(0.0, 0.0, -1.0)

        # Calculate angle
        if Axis1 == Axis2:
            normvec = Base.Vector(1.0, 0.0, 0.0)
            result = 0.0
        else:
            if Axis1 == Axis2_minus:
                normvec = Base.Vector(1.0, 0.0, 0.0)
                result = math.pi
            else:
                # Calculate axis of rotation = normvec
                normvec = Axis1.cross(Axis2)
                normvec.normalize()  # Normalize for quaternion calculations
                # normvec_rot = normvec
                result = DraftVecUtils.angle(
                    Axis1, Axis2, normvec)  # Angle calculation
        sin_res = math.sin(result / 2.0)
        cos_res = math.cos(result / 2.0)
        normvec.multiply(-sin_res)  # Calculation of the quaternion elements

        # FreeCAD.Console.PrintMessage( "Angle = "+ str(math.degrees(result)) + "\n")
        # FreeCAD.Console.PrintMessage("Normal vector: "+ str(normvec) + "\n")

        pl = FreeCAD.Placement()
        pl.Rotation = (normvec.x, normvec.y, normvec.z,
                       cos_res)  # Rotation quaternion

        # FreeCAD.Console.PrintMessage("pl mit Rot: "+ str(pl) + "\n")
        ScrewObj_m.Placement = FreeCAD.Placement()
        ScrewObj_m.Placement.Rotation = pl.Rotation.multiply(
            ScrewObj_m.Placement.Rotation)
        ScrewObj_m.Placement.move(Pnt1)

###############################################################################
#                         Common actions on fasteners                         #
###############################################################################

################################ Flip command #################################

class FSFlipCommand:
    """Flip Screw command"""

    def GetResources(self):
        icon = os.path.join(iconPath, 'IconFlip.svg')
        return {
            'Pixmap': icon,  # the name of a svg file available in the resources
            'MenuText': translate("FastenerBase", "Invert fastener"),
            'ToolTip': translate("FastenerBase", "Invert fastener orientation")
        }

    def Activated(self):
        selObjs = self.GetSelection()
        if len(selObjs) == 0:
            return
        for selObj in selObjs:
            FreeCAD.Console.PrintLog("sel obj: " + str(selObj.invert) + "\n")
            selObj.invert = not selObj.invert
        FreeCAD.ActiveDocument.recompute()
        return

    def IsActive(self):
        selObjs = self.GetSelection()
        return len(selObjs) > 0

    def GetSelection(self):
        screwObj = []
        for selobj in Gui.Selection.getSelectionEx():
            obj = selobj.Object
            # FreeCAD.Console.PrintLog("sel obj: " + str(obj) + "\n")
            if hasattr(obj, 'Proxy') and isinstance(obj.Proxy, FSBaseObject):
                if obj.baseObject is not None:
                    screwObj.append(obj)
        return screwObj


Gui.addCommand('FSFlip', FSFlipCommand())
FSCommands.append('FSFlip', "command")

################################ Move command #################################

class FSMoveCommand:
    """Move Screw command"""

    def GetResources(self):
        icon = os.path.join(iconPath, 'IconMove.svg')
        return {
            'Pixmap': icon,  # the name of a svg file available in the resources
            'MenuText': translate("FastenerBase", "Move fastener"),
            'ToolTip': translate("FastenerBase", "Move fastener to a new location")
        }

    def Activated(self):
        selObj = self.GetSelection()
        if selObj[0] is None:
            return
        selObj[0].baseObject = selObj[1]
        FreeCAD.ActiveDocument.recompute()
        return

    def IsActive(self):
        selObj = self.GetSelection()
        if selObj[0] is not None:
            return True
        return False

    def GetSelection(self):
        screwObj = None
        edgeObj = None
        for selObj in Gui.Selection.getSelectionEx():
            obj = selObj.Object
            if hasattr(obj, 'Proxy') and isinstance(obj.Proxy, FSBaseObject):
                screwObj = obj
        aselects = FSGetAttachableSelections()
        if len(aselects) > 0:
            edgeObj = aselects[0]
        return screwObj, edgeObj


Gui.addCommand('FSMove', FSMoveCommand())
FSCommands.append('FSMove', "command")

########################### Make Simple command ###############################

class FSMakeSimpleCommand:
    """Move Screw command"""

    def GetResources(self):
        icon = os.path.join(iconPath, 'IconShape.svg')
        return {
            'Pixmap': icon,  # the name of a svg file available in the resources
            'MenuText': translate("FastenerBase", "Simplify shape"),
            'ToolTip': translate("FastenerBase", "Change object to simple non-parametric shape")
        }

    def Activated(self):
        for selObj in Gui.Selection.getSelectionEx():
            obj = selObj.Object
            FreeCAD.Console.PrintLog("sel shape: " + str(obj.Shape) + "\n")
            if isinstance(obj.Shape, (Part.Solid, Part.Compound)):
                FreeCAD.Console.PrintLog("simplify shape: " + obj.Name + "\n")
                cobj = FreeCAD.ActiveDocument.addObject(
                    "Part::Feature", obj.Label + "_Copy")
                cobj.Shape = obj.Shape
                Gui.ActiveDocument.getObject(obj.Name).Visibility = False
        FreeCAD.ActiveDocument.recompute()
        return

    def IsActive(self):
        if len(Gui.Selection.getSelectionEx()) > 0:
            return True
        return False


Gui.addCommand('FSSimple', FSMakeSimpleCommand())
FSCommands.append('FSSimple', "command")

######################## MatchTypeInner/Outer commands ########################

FSParam.SetBool("MatchOuterDiameter", False)

class FSMatchTypeInnerCommand:
    def Activated(self):
        matchOuterButton = FSGetToolbarItem(
            "FS Commands", matchOuterButtonText)
        matchInnerButton = FSGetToolbarItem(
            "FS Commands", matchInnerButtonText)
        matchInnerButton.setChecked(True)
        matchOuterButton.setChecked(False)
        FSParam.SetBool("MatchOuterDiameter", False)
        FreeCAD.Console.PrintLog("Set auto diameter to match inner thread\n")

    def GetResources(self):
        return {
            'Pixmap': os.path.join(iconPath, 'IconMatchTypeInner.svg'),
            'MenuText': matchInnerButtonText,
            # ,'Checkable': True
            'ToolTip': translate("FastenerBase", 'Match screws by inner thread diameter (Tap hole)')
        }

class FSMatchTypeOuterCommand:
    def Activated(self):
        matchOuterButton = FSGetToolbarItem(
            "FS Commands", matchOuterButtonText)
        matchInnerButton = FSGetToolbarItem(
            "FS Commands", matchInnerButtonText)
        matchInnerButton.setChecked(False)
        matchOuterButton.setChecked(True)
        FSParam.SetBool("MatchOuterDiameter", True)
        FreeCAD.Console.PrintLog("Set auto diameter to match outer thread\n")

    def GetResources(self):
        return {
            'Pixmap': os.path.join(iconPath, 'IconMatchTypeOuter.svg'),
            'MenuText': matchOuterButtonText,
            # ,'Checkable': False
            'ToolTip': translate("FastenerBase", 'Match screws by outer thread diameter (Pass hole)')
        }


FreeCADGui.addCommand('FSMatchTypeInner', FSMatchTypeInnerCommand())
FreeCADGui.addCommand('FSMatchTypeOuter', FSMatchTypeOuterCommand())
FSCommands.append('FSMatchTypeInner', "command")
FSCommands.append('FSMatchTypeOuter', "command")

def InitCheckables():
    match_outer = FSParam.GetBool("MatchOuterDiameter")
    matchOuterButton = FSGetToolbarItem("FS Commands", matchOuterButtonText)
    matchInnerButton = FSGetToolbarItem("FS Commands", matchInnerButtonText)
    matchOuterButton.setCheckable(True)
    matchInnerButton.setCheckable(True)
    matchOuterButton.setChecked(match_outer)
    matchInnerButton.setChecked(not match_outer)
    
########################## Generate BOM command ###############################

class FSMakeBomCommand:
    """Generate fasteners bill of material"""

    def GetResources(self):
        icon = os.path.join(iconPath, 'IconBOM.svg')
        return {'Pixmap': icon,
                # the name of a svg file available in the resources
                'MenuText': translate("FastenerBase", "Generate BOM"),
                'ToolTip': translate("FastenerBase", "Generate fasteners bill of material")}

    def Activated(self):
        self.fastenerDB = {}
        sheet = FreeCAD.ActiveDocument.addObject('Spreadsheet::Sheet',
                                                 'Fasteners_BOM')
        sheet.Label = translate("FastenerBase", 'Fasteners_BOM')
        sheet.setColumnWidth('A', 200)
        sheet.set('A1', translate("FastenerBase", "Type"))
        sheet.set('B1', translate("FastenerBase", "Qty"))
        for obj in FreeCAD.ActiveDocument.Objects:
            name = FSRemoveDigits(obj.Name)
            # get total count
            cnt = GetTotalObjectRepeats(obj)
            # FreeCAD.Console.PrintLog("Using method: Add" + name + "\n")
            method = getattr(self, 'Add' + name, lambda x, y: "nothing")
            method(obj, cnt)
            # FreeCAD.Console.PrintLog('Add ' + str(cnt) + " " + obj.Name  + "\n")
        line = 2
        for fastener in sorted(self.fastenerDB.keys()):
            sheet.set('A' + str(line), fastener)
            sheet.set('B' + str(line), str(self.fastenerDB[fastener]))
            line += 1
        FreeCAD.ActiveDocument.recompute()
        return

    def AddFastener(self, fastener, cnt):
        if fastener in self.fastenerDB:
            self.fastenerDB[fastener] = self.fastenerDB[fastener] + cnt
        else:
            self.fastenerDB[fastener] = cnt

    def AddScrew(self, obj, cnt):
        desc = obj.type + translate("FastenerBase",
                                    " Screw ") + FSScrewStr(obj)
        self.AddFastener(desc, cnt)

    def AddNut(self, obj, cnt):
        if hasattr(obj, 'type'):
            type = obj.type
        else:
            type = 'ISO4033'
        self.AddFastener(type + translate("FastenerBase",
                         " Nut ") + obj.diameter, cnt)

    def AddWasher(self, obj, cnt):
        self.AddFastener(obj.type + translate("FastenerBase",
                         " Washer ") + obj.diameter, cnt)

    def AddThreadedRod(self, obj, cnt):
        desc = translate("FastenerBase", "Threaded Rod ") + FSScrewStr(obj)
        self.AddFastener(desc, cnt)

    def AddPressNut(self, obj, cnt):
        self.AddFastener(translate("FastenerBase", "PEM PressNut ") +
                         obj.diameter + "-" + obj.tcode, cnt)

    def AddStandoff(self, obj, cnt):
        self.AddFastener(translate("FastenerBase", "PEM Standoff ") +
                         obj.diameter + "x" + obj.length, cnt)

    def AddStud(self, obj, cnt):
        self.AddFastener(translate("FastenerBase", "PEM Stud ") +
                         obj.diameter + "x" + obj.length, cnt)

    def AddPcbStandoff(self, obj, cnt):
        self.AddFastener(
            translate("FastenerBase", "PCB Standoff ") +
            obj.diameter + "x" + obj.width + "x" + obj.length,
            cnt)

    def AddHeatSet(self, obj, cnt):
        self.AddFastener(
            translate("FastenerBase", "Heat Set Insert ") + obj.diameter, cnt)

    def AddRetainingRing(self, obj, cnt):
        self.AddFastener(obj.type + translate("FastenerBase",
                         " Retaining Ring ") + obj.diameter, cnt)

    def IsActive(self):
        return Gui.ActiveDocument is not None


Gui.addCommand('FSMakeBOM', FSMakeBomCommand())
FSCommands.append('FSMakeBOM', "command")

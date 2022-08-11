#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  screw_maker2_0.py
#


"""
Macro to generate screws with FreeCAD.
Version 1.4 from 1st of September 2013
Version 1.5 from 23rd of December 2013
Corrected hex-heads above M12 not done.
Version 1.6 from 15th of March 2014
Added PySide support

Version 1.7 from April 2014
fixed bool type error. (int is not anymore accepted at linux)
fixed starting point of real thread at some screw types.

Version 1.8 from July 2014
first approach for a faster real thread

Version 1.9 / 2.0 July 2015
new calculation of starting point of thread
shell-based approach for screw generation
added:
ISO 14582 Hexalobular socket countersunk head screws, high head
ISO 14584 Hexalobular socket raised countersunk head screws
ISO 7380-2 Hexagon socket button head screws with collar
DIN 967 Cross recessed pan head screws with collar
ISO 4032 Hexagon nuts, Style 1
ISO 4033 Hexagon nuts, Style 2
ISO 4035 Hexagon thin nuts, chamfered
EN 1661 Hexagon nuts with flange
ISO 7094 definitions  Plain washers - Extra large series
ISO 7092 definitions  Plain washers - Small series
ISO 7093-1 Plain washer - Large series
Screw-tap to drill inner threads in parts with user defined length

ScrewMaker can now also used as a python module.
The following shows how to generate a screw from a python script:
  import screw_maker2_0

  threadDef = 'M3.5'
  o = screw_maker2_0.Screw()
  t = screw_maker2_0.Screw.setThreadType(o,'real')
  # Creates a Document-Object with label describing the screw
  d = screw_maker2_0.Screw.createScrew(o, 'ISO1207', threadDef, '20', 'real')

  # creates a shape in memory
  t = screw_maker2_0.Screw.setThreadType(o,'real')
  s = screw_maker1_9d.Screw.makeCountersunkHeadScrew(o, 'ISO14582', threadDef, 40.0)
  Part.show(s)



to do: check ISO7380 usage of rs and rt, actual only rs is used
check chamfer angle on hexogon heads and nuts
***************************************************************************
*   Copyright (c) 2013, 2014, 2015                                        *
*   Ulrich Brammer <ulrich1a[at]users.sourceforge.net>                    *
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

__author__ = "Ulrich Brammer <ulrich1a@users.sourceforge.net>"



import errno
import FreeCAD, FreeCADGui, Part, math, os
from FreeCAD import Base
import DraftVecUtils
from pathlib import Path
import importlib

from utils import csv2dict


#import FSmakeCountersunkHeadScrew
#from FSmakeCountersunkHeadScrew import *

DEBUG = False # set to True to show debug messages; does not work, still todo.

# import fastener data
__dir__ = os.path.dirname(__file__)
fsdatapath = os.path.join(__dir__, 'FsData')

# function to open a csv file and convert it to a dictionary


FsData = {}
filelist = Path(fsdatapath).glob('*.csv')
for item in filelist:
    item_dict = csv2dict(str(item), fieldsnamed=True)
    FsData[item.stem] = item_dict


class Screw:
    def __init__(self):
        self.objAvailable = True
        self.Tuner = 510
        self.leftHanded = False
        # thread scaling for 3D printers
        # scaled_diam = diam * ScaleA + ScaleB
        self.sm3DPrintMode = False
        self.smNutThrScaleA = 1.0
        self.smNutThrScaleB = 0.0
        self.smScrewThrScaleA = 1.0
        self.smScrewThrScaleB = 0.0

    def createScrew(self, ST_text, ND_text, NL_text, threadType, fastenerParams, shapeOnly=False, leftHanded=False):
        # self.simpThread = self.SimpleScrew.isChecked()
        # self.symThread = self.SymbolThread.isChecked()
        # self.rThread = self.RealThread.isChecked()
        #FreeCAD.Console.PrintMessage(ST_text + "\n")
        Type_text = fastenerParams[0]
        function = fastenerParams[6]
        if not self.objAvailable:
            return None
        try:
            l = self.getLength(NL_text)
            if not hasattr(self, function):
                module = "FsFunctions.FS" + function
                setattr(Screw, function, getattr(importlib.import_module(module), function))
        except ValueError:
            # print "Error! nom_dia and length values must be valid numbers!"
            FreeCAD.Console.PrintMessage("Error! nom_dia and length values must be valid numbers!\n")
            return None

        if threadType == 'real':
            self.rThread = True
        else:
            self.rThread = False

        self.dimTable = fastenerParams[1][ND_text]
        self.leftHanded = leftHanded
        self.fastenerLen = l
        self.fastenerType = ST_text
        self.fastenerDiam = ND_text
        doc = FreeCAD.activeDocument()

        if function != "" :
            function = "self." + function + "()"
            screw = eval(function)
            done = True
        else:
            FreeCAD.Console.PrintMessage("No suitable function for " + ST_text + " Screw Type!\n")
            return None
        if '(' in ND_text:
            ND_text = ND_text.lstrip('(').rstrip(')')

        if Type_text == 'Screw':
            label = ST_text + "-" + ND_text + "x" + NL_text + "_"
        else:
            if Type_text == 'Nut':
                label = ST_text + '-' + ND_text + '_'
            else:
                if Type_text == ('Screw-Tap' or 'Screw-Die' or 'Threaded-Rod'):
                    label = ST_text + '-' + ND_text + 'x' + NL_text + '_'
                else:  # washer
                    label = ST_text + '-' + ND_text.lstrip('M') + '_'
        if shapeOnly:
            return screw
        ScrewObj = doc.addObject("Part::Feature")
        ScrewObj.Label = label
        ScrewObj.Shape = screw
        # FreeCAD.Console.PrintMessage("Placement: "+ str(ScrewObj.Placement) +"\n")
        # FreeCAD.Console.PrintMessage("The label: "+ label +"\n")
        self.moveScrew(ScrewObj)
        # ScrewObj.Label = label
        doc.recompute()
        # Part.show(screw)
        return ScrewObj

    def moveScrew(self, ScrewObj_m):
        # FreeCAD.Console.PrintMessage("In Move Screw: " + str(ScrewObj_m) + "\n")

        mylist = FreeCAD.Gui.Selection.getSelectionEx()
        if mylist.__len__() == 1:
            # check selection
            # FreeCAD.Console.PrintMessage("Selections: " + str(mylist.__len__()) + "\n")
            Pnt1 = None
            Axis1 = None
            Axis2 = None

            for o in Gui.Selection.getSelectionEx():
                # for s in o.SubElementNames:
                # FreeCAD.Console.PrintMessage( "name: " + str(s) + "\n")
                for s in o.SubObjects:
                    # FreeCAD.Console.PrintMessage( "object: "+ str(s) + "\n")
                    if hasattr(s, "Curve"):
                        # FreeCAD.Console.PrintMessage( "The Object is a Curve!\n")
                        if hasattr(s.Curve, "Center"):
                            """
                   FreeCAD.Console.PrintMessage( "The object has a Center!\n")
                   FreeCAD.Console.PrintMessage( "Curve attribute. "+ str(s.__getattribute__('Curve')) + "\n")
                   FreeCAD.Console.PrintMessage( "Center: "+ str(s.Curve.Center) + "\n")
                   FreeCAD.Console.PrintMessage( "Axis: "+ str(s.Curve.Axis) + "\n")
                   """
                            Pnt1 = s.Curve.Center
                            Axis1 = s.Curve.Axis
                    if hasattr(s, 'Surface'):
                        # print 'the object is a face!'
                        if hasattr(s.Surface, 'Axis'):
                            Axis1 = s.Surface.Axis

                    if hasattr(s, 'Point'):
                        # FreeCAD.Console.PrintMessage( "the object seems to be a vertex! "+ str(s.Point) + "\n")
                        Pnt1 = s.Point

            if Axis1 is not None:
                # FreeCAD.Console.PrintMessage( "Got Axis1: " + str(Axis1) + "\n")
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
                        normvec = Axis1.cross(Axis2)  # Calculate axis of rotation = normvec
                        normvec.normalize()  # Normalize for quaternion calculations
                        # normvec_rot = normvec
                        result = DraftVecUtils.angle(Axis1, Axis2, normvec)  # Winkelberechnung
                sin_res = math.sin(result / 2.0)
                cos_res = math.cos(result / 2.0)
                normvec.multiply(-sin_res)  # Calculation of the quaternion elements
                # FreeCAD.Console.PrintMessage( "Angle = "+ str(math.degrees(result)) + "\n")
                # FreeCAD.Console.PrintMessage("Normal vector: "+ str(normvec) + "\n")

                pl = FreeCAD.Placement()
                pl.Rotation = (normvec.x, normvec.y, normvec.z, cos_res)  # Drehungs-Quaternion

                # FreeCAD.Console.PrintMessage("pl mit Rot: "+ str(pl) + "\n")
                # neuPlatz = Part2.Object.Placement.multiply(pl)
                neuPlatz = ScrewObj_m.Placement
                # FreeCAD.Console.PrintMessage("the Position     "+ str(neuPlatz) + "\n")
                neuPlatz.Rotation = pl.Rotation.multiply(ScrewObj_m.Placement.Rotation)
                neuPlatz.move(Pnt1)
                # FreeCAD.Console.PrintMessage("the rot. Position: "+ str(neuPlatz) + "\n")


    # make ISO 2009 Slotted countersunk flat head screws
    # make ISO 2010 Slotted raised countersunk head screws
    # make ISO 1580 Pan head slotted screw (Code is nearly identical to iso1207)
    # make ASMEB18.6.3.1A Slotted countersunk flat head screws
    def makeSlottedScrew(self):
        dia = self.getDia(self.fastenerDiam, False)
        SType = self.fastenerType
        l = self.fastenerLen
        if SType == 'ISO1580':
            # FreeCAD.Console.PrintMessage("the head with l: " + str(l) + "\n")
            P, a, b, dk_max, da, k, n_min, r, rf, t_min, x = self.dimTable
            # FreeCAD.Console.PrintMessage("the head with iso: " + str(dk_max) + "\n")
            ht = k

            # Length for calculation of head fillet
            sqrt2_ = 1.0 / math.sqrt(2.0)
            r_fil = rf
            beta = math.radians(5.0)  # angle of pan head edge
            alpha = math.radians(90.0 - (90.0 + 5.0) / 2.0)
            tan_beta = math.tan(beta)
            # top head diameter without fillet
            rK_top = dk_max / 2.0 - k * tan_beta
            fillet_center_x = rK_top - r_fil + r_fil * tan_beta
            fillet_center_z = k - r_fil
            fillet_arc_x = fillet_center_x + r_fil * math.sin(alpha)
            fillet_arc_z = fillet_center_z + r_fil * math.cos(alpha)
            # FreeCAD.Console.PrintMessage("rK_top: " + str(rK_top) + "\n")

            # Head Points
            Pnt0 = Base.Vector(0.0, 0.0, k)
            Pnt2 = Base.Vector(fillet_center_x, 0.0, k)
            Pnt3 = Base.Vector(fillet_arc_x, 0.0, fillet_arc_z)
            Pnt4 = Base.Vector(fillet_center_x + r_fil * math.cos(beta), 0.0, fillet_center_z + r_fil * math.sin(beta))
            Pnt5 = Base.Vector(dk_max / 2.0, 0.0, 0.0)
            Pnt6 = Base.Vector(dia / 2.0 + r, 0.0, 0.0)  # start of fillet between head and shank
            Pnt7 = Base.Vector(dia / 2.0 + r - r * sqrt2_, 0.0, -r + r * sqrt2_)  # arc-point of fillet
            # Pnt8 = Base.Vector(dia/2.0,0.0,-r)        # end of fillet
            PntR = Base.Vector(dia / 2.0, 0.0, -r)  # end of fillet
            PntT0 = Base.Vector(0.0, 0.0, -r)  # helper point for real thread

            edge1 = Part.makeLine(Pnt0, Pnt2)
            edge2 = Part.Arc(Pnt2, Pnt3, Pnt4).toShape()
            edge3 = Part.makeLine(Pnt4, Pnt5)
            edge4 = Part.makeLine(Pnt5, Pnt6)
            edge5 = Part.Arc(Pnt6, Pnt7, PntR).toShape()
            headWire = Part.Wire([edge1, edge2, edge3, edge4, edge5])

        if SType == 'ISO2009' or SType == 'ISO2010' or SType == 'ASMEB18.6.3.1A':
            if SType == 'ISO2009' or SType == 'ISO2010':
                P, a, b, dk_theo, dk_mean, k, n_min, r, t_mean, x = self.dimTable
            elif SType == 'ASMEB18.6.3.1A':
                P, b, dk_theo, dk_mean, k, n_min, r, t_mean = self.dimTable
            dk_max = dk_theo
            t_min = t_mean
            ht = 0.0  # Head height of flat head
            if SType == 'ISO2010':
                rf, t_mean, cT, mH, mZ = FsData["Raised_countersunk_def"][self.fastenerDiam]
                # Lengths and angles for calculation of head rounding
                beta = math.asin(dk_mean / 2.0 / rf)  # angle of head edge
                tan_beta = math.tan(beta)
                alpha = beta / 2.0  # half angle
                # height of raised head top
                ht = rf - (dk_mean / 2.0) / tan_beta
                h_arc_x = rf * math.sin(alpha)
                h_arc_z = ht - rf + rf * math.cos(alpha)

            cham = (dk_theo - dk_mean) / 2.0
            rad225 = math.radians(22.5)
            rad45 = math.radians(45.0)
            rtan = r * math.tan(rad225)
 
            # Head Points
            Pnt0 = Base.Vector(0.0, 0.0, ht)
            Pnt1 = Base.Vector(dk_mean / 2.0, 0.0, 0.0)
            Pnt2 = Base.Vector(dk_mean / 2.0, 0.0, -cham)
            Pnt3 = Base.Vector(dia / 2.0 + r - r * math.cos(rad45), 0.0, -k - rtan + r * math.sin(rad45))
            # Arc-points
            Pnt4 = Base.Vector(dia / 2.0 + r - r * (math.cos(rad225)), 0.0, -k - rtan + r * math.sin(rad225))
            PntR = Base.Vector(dia / 2.0, 0.0, -k - rtan)
            # PntA = Base.Vector(dia/2.0,0.0,-a_point)
            PntT0 = Base.Vector(0.0, 0.0, -k - rtan)  # helper point for real thread

            if SType == 'ISO2010':  # make raised head rounding
                Pnt0arc = Base.Vector(h_arc_x, 0.0, h_arc_z)
                edge1 = Part.Arc(Pnt0, Pnt0arc, Pnt1).toShape()
            else:
                edge1 = Part.makeLine(Pnt0, Pnt1)  # make flat head

            edge2 = Part.makeLine(Pnt1, Pnt2)
            edge3 = Part.makeLine(Pnt2, Pnt3)
            edgeArc = Part.Arc(Pnt3, Pnt4, PntR).toShape()
            headWire = Part.Wire([edge1, edge2, edge3, edgeArc])

        flat_len = l + PntT0.z
        thread_start = -l + b
        PntA = Base.Vector(dia / 2.0, 0.0, thread_start)  # Start of thread

        if self.rThread:
            edgeZ1 = Part.makeLine(PntR, PntT0)
            edgeZ0 = Part.makeLine(PntT0, Pnt0)
            aWire = Part.Wire([headWire, edgeZ1, edgeZ0])

        else:
            # bolt points
            PntB1 = Base.Vector(dia / 2.0, 0.0, -l)
            PntB2 = Base.Vector(0.0, 0.0, -l)

            edgeB2 = Part.makeLine(PntB1, PntB2)
            edgeZ0 = Part.makeLine(PntB2, Pnt0)

            if thread_start >= PntT0.z:
                edgeB1 = Part.makeLine(PntR, PntB1)
                aWire = Part.Wire([headWire, edgeB1, edgeB2, edgeZ0])
            else:
                edgeRA = Part.makeLine(PntR, PntA)
                edgeB1 = Part.makeLine(PntA, PntB1)
                aWire = Part.Wire([headWire, edgeRA, edgeB1, edgeB2, edgeZ0])

        aFace = Part.Face(aWire)
        head = aFace.revolve(Base.Vector(0.0, 0.0, 0.0), Base.Vector(0.0, 0.0, 1.0), 360)
        # FreeCAD.Console.PrintMessage("the head with revolve: " + str(dia) + "\n")

        # Parameter for slot-recess: dk_max, n_min, k, t_min
        slot = Part.makePlane(dk_max, n_min, \
                              Base.Vector(dk_max / 2.0, -n_min / 2.0, ht + 1.0), Base.Vector(0.0, 0.0, -1.0))
        slot = slot.extrude(Base.Vector(0.0, 0.0, -t_min - 1.0))
        # Part.show(slot)
        head = head.cut(slot)
        # FreeCAD.Console.PrintMessage("the head cut: " + str(dia) + "\n")
        # Part.show(head)

        # FreeCAD.Console.PrintMessage("flatlen:" + str(flat_len) + "   b:" + str(b) + "   r:" + str(r) + "   a:" + str(a_point) + "\n")
        if self.rThread:
            rthread = self.makeShellthread(dia, P, flat_len, False, PntT0.z, b)
            headFaces = []
            if SType == 'ISO2009' or SType == 'ASMEB18.6.3.1A':
                for i in range(0, len(head.Faces) - 2):
                    headFaces.append(head.Faces[i])
                headFaces.append(head.Faces[len(head.Faces) - 1])

            if SType == 'ISO1580' or SType == 'ISO2010':
                for i in range(0, len(head.Faces) - 1):
                    headFaces.append(head.Faces[i])
            # Part.show(Part.Shell(headFaces))
        
            for threadFace in rthread.Faces:
                headFaces.append(threadFace)

            newHeadShell = Part.Shell(headFaces)
            # Part.show(newHeadShell)
            head = Part.Solid(newHeadShell)

        return head

    # ISO 7045 Pan head screws with type H or type Z cross recess
    # ISO 14583 Hexalobular socket pan head screws
    def makePanHeadScrew(self):
        SType = self.fastenerType
        l = self.fastenerLen
        dia = self.getDia(self.fastenerDiam, False)
        # FreeCAD.Console.PrintMessage("the head with l: " + str(l) + "\n")
        FreeCAD.Console.PrintMessage("the head with diam: " + str(self.fastenerDiam) + "\n")
        P, a, b, dk_max, da, k, r, rf, x, cT, mH, mZ = FsData["iso7045def"][self.fastenerDiam]
        # FreeCAD.Console.PrintMessage("the head with iso: " + str(dk_max) + "\n")

        # Lengths and angles for calculation of head rounding
        beta = math.asin(dk_max / 2.0 / rf)  # angle of head edge
        # print 'beta: ', math.degrees(beta)
        tan_beta = math.tan(beta)

        if SType == 'ISO14583':
            tt, A, t_mean = self.dimTable
            beta_A = math.asin(A / 2.0 / rf)  # angle of recess edge
            tan_beta_A = math.tan(beta_A)

            alpha = (beta_A + beta) / 2.0  # half angle
            # print 'alpha: ', math.degrees(alpha)
            # height of head edge
            he = k - A / 2.0 / tan_beta_A + (dk_max / 2.0) / tan_beta
            # print 'he: ', he
            h_arc_x = rf * math.sin(alpha)
            h_arc_z = k - A / 2.0 / tan_beta_A + rf * math.cos(alpha)
            # FreeCAD.Console.PrintMessage("h_arc_z: " + str(h_arc_z) + "\n")
        else:
            alpha = beta / 2.0  # half angle
            # print 'alpha: ', math.degrees(alpha)
            # height of head edge
            he = k - rf + (dk_max / 2.0) / tan_beta
            # print 'he: ', he
            h_arc_x = rf * math.sin(alpha)
            h_arc_z = k - rf + rf * math.cos(alpha)
            # FreeCAD.Console.PrintMessage("h_arc_z: " + str(h_arc_z) + "\n")

        thread_start = l - b
        # FreeCAD.Console.PrintMessage("The transition at a: " + str(a) + " turns " + str(turns) + "\n")

        sqrt2_ = 1.0 / math.sqrt(2.0)

        # Head Points
        Pnt1 = Base.Vector(h_arc_x, 0.0, h_arc_z)
        Pnt2 = Base.Vector(dk_max / 2.0, 0.0, he)
        Pnt3 = Base.Vector(dk_max / 2.0, 0.0, 0.0)
        Pnt4 = Base.Vector(dia / 2.0 + r, 0.0, 0.0)  # start of fillet between head and shank
        Pnt5 = Base.Vector(dia / 2.0 + r - r * sqrt2_, 0.0, -r + r * sqrt2_)  # arc-point of fillet
        Pnt6 = Base.Vector(dia / 2.0, 0.0, -r)  # end of fillet
        Pnt7 = Base.Vector(dia / 2.0, 0.0, -thread_start)  # Start of thread
        # FreeCAD.Console.PrintMessage("Points defined a_point: " + str(a_point) + "\n")

        if SType == 'ISO14583':
            # Pnt0 = Base.Vector(0.0,0.0,k-A/4.0)
            Pnt0 = Base.Vector(0.0, 0.0, k - A / 8.0)
            PntFlat = Base.Vector(A / 8.0, 0.0, k - A / 8.0)
            PntCham = Base.Vector(A / 1.99, 0.0, k)
            edgeCham0 = Part.makeLine(Pnt0, PntFlat)
            edgeCham1 = Part.makeLine(PntFlat, PntCham)
            edgeCham2 = Part.Arc(PntCham, Pnt1, Pnt2).toShape()
            # edge1 = Part.Wire([edgeCham0,edgeCham1,edgeCham2])
            edge1 = Part.Wire([edgeCham0, edgeCham1])
            edge2 = Part.makeLine(Pnt2, Pnt3)
            edge2 = Part.Wire([edgeCham2, edge2])
            # Part.show(edge2)

            # Here is the next approach to shorten the head building time
            # Make two helper points to create a cutting tool for the
            # recess and recess shell.
            PntH1 = Base.Vector(A / 1.99, 0.0, 2.0 * k)
            PntH2 = Base.Vector(0.0, 0.0, 2.0 * k)
            edgeH1 = Part.makeLine(PntCham, PntH1)
            edgeH2 = Part.makeLine(PntH1, PntH2)
            edgeH3 = Part.makeLine(PntH2, Pnt0)

        else:
            Pnt0 = Base.Vector(0.0, 0.0, k)
            edge1 = Part.Arc(Pnt0, Pnt1, Pnt2).toShape()  # make round head
            edge2 = Part.makeLine(Pnt2, Pnt3)

            # Here is the next approach to shorten the head building time
            # Make two helper points to create a cutting tool for the
            # recess and recess shell.
            PntH1 = Base.Vector(dk_max / 2.0, 0.0, 2.0 * k)
            PntH2 = Base.Vector(0.0, 0.0, 2.0 * k)
            edgeH1 = Part.makeLine(Pnt2, PntH1)
            edgeH2 = Part.makeLine(PntH1, PntH2)
            edgeH3 = Part.makeLine(PntH2, Pnt0)

        edge3 = Part.makeLine(Pnt3, Pnt4)
        edge4 = Part.Arc(Pnt4, Pnt5, Pnt6).toShape()
        # FreeCAD.Console.PrintMessage("Edges made h_arc_z: " + str(h_arc_z) + "\n")

        # if self.RealThread.isChecked():
        if self.rThread:
            aWire = Part.Wire([edge2, edge3, edge4])
        else:
            # bolt points
            PntB1 = Base.Vector(dia / 2.0, 0.0, -l)
            PntB2 = Base.Vector(0.0, 0.0, -l)
            edgeB2 = Part.makeLine(PntB1, PntB2)
            if thread_start <= (r + 0.00001):
                edgeB1 = Part.makeLine(Pnt6, PntB1)
                aWire = Part.Wire([edge2, edge3, edge4, edgeB1, edgeB2])
            else:
                edge5 = Part.makeLine(Pnt6, Pnt7)
                edgeB1 = Part.makeLine(Pnt7, PntB1)
                aWire = Part.Wire([edge2, edge3, edge4, edge5, edgeB1, edgeB2])

        hWire = Part.Wire([edge1, edgeH1, edgeH2, edgeH3])  # Cutter for recess-Shell
        hFace = Part.Face(hWire)
        hCut = hFace.revolve(Base.Vector(0.0, 0.0, 0.0), Base.Vector(0.0, 0.0, 1.0), 360)
        # Part.show(hWire)

        headShell = aWire.revolve(Base.Vector(0.0, 0.0, 0.0), Base.Vector(0.0, 0.0, 1.0), 360)
        # head = Part.Solid(headShell)
        # Part.show(aWire)
        # FreeCAD.Console.PrintMessage("the head with revolve: " + str(dia) + "\n")
        headFaces = headShell.Faces

        if SType == 'ISO14583':
            recess, recessShell = self.makeIso10664_3(tt, t_mean, k)
            recessShell = recessShell.cut(hCut)
            topFace = hCut.Faces[1]
            topFace = topFace.cut(recess)
            # Part.show(topFace)
            # Part.show(recessShell)
            # Part.show(headShell)
            headFaces.append(topFace.Faces[0])
            # headFaces.append(hCut.Faces[2])

        else:
            # Lengths and angles for calculation of recess positioning
            beta_cr = math.asin(mH / 2.0 / rf)  # angle of recess edge
            tan_beta_cr = math.tan(beta_cr)
            # height of cross recess cutting
            hcr = k - rf + (mH / 2.0) / tan_beta_cr
            # print 'hcr: ', hcr

            # Parameter for cross-recess type H: cT, mH
            recess, recessShell = self.makeCross_H3(cT, mH, hcr)
            recessShell = recessShell.cut(hCut)
            topFace = hCut.Faces[0]
            topFace = topFace.cut(recess)
            # Part.show(topFace)
            # Part.show(recessShell)
            # Part.show(headShell)
            headFaces.append(topFace.Faces[0])

        # Part.show(hCut)
        headFaces.extend(recessShell.Faces)

        # if self.RealThread.isChecked():
        if self.rThread:
            # head = self.cutIsoThread(head, dia, P, turns, l)
            rthread = self.makeShellthread(dia, P, l - r, False, -r, b)
            # head = head.fuse(rthread)
            # Part.show(rthread)
            for threadFace in rthread.Faces:
                headFaces.append(threadFace)

        newHeadShell = Part.Shell(headFaces)
        # Part.show(newHeadShell)
        head = Part.Solid(newHeadShell)

        return head

    # make Cheese head screw
    # ISO 1207 slotted screw
    # ISO 7048 cross recessed screw
    # ISO 14580 Hexalobular socket cheese head screws
    def makeCheeseHeadScrew(self):
        SType = self.fastenerType
        l = self.fastenerLen
        dia = self.getDia(self.fastenerDiam, False)

        # FreeCAD.Console.PrintMessage("the head with l: " + str(l) + "\n")
        if SType == 'ISO1207' or SType == 'ISO14580':
            P, a, b, dk, dk_mean, da, k, n_min, r, t_min, x = self.dimTable
        if SType == 'ISO7048':
            P, a, b, dk, dk_mean, da, k, r, x, cT, mH, mZ = self.dimTable
        if SType == 'ISO14580':
            tt, k, A, t_min = self.dimTable

        # FreeCAD.Console.PrintMessage("the head with iso: " + str(dk) + "\n")

        # Length for calculation of head fillet
        r_fil = r * 2.0
        beta = math.radians(5.0)  # angle of cheese head edge
        alpha = math.radians(90.0 - (90.0 + 5.0) / 2.0)
        tan_beta = math.tan(beta)
        # top head diameter without fillet
        rK_top = dk / 2.0 - k * tan_beta
        fillet_center_x = rK_top - r_fil + r_fil * tan_beta
        fillet_center_z = k - r_fil
        fillet_arc_x = fillet_center_x + r_fil * math.sin(alpha)
        fillet_arc_z = fillet_center_z + r_fil * math.cos(alpha)
        # FreeCAD.Console.PrintMessage("rK_top: " + str(rK_top) + "\n")

        thread_start = l - b
        sqrt2_ = 1.0 / math.sqrt(2.0)

        # Head Points
        Pnt2 = Base.Vector(fillet_center_x, 0.0, k)
        Pnt3 = Base.Vector(fillet_arc_x, 0.0, fillet_arc_z)
        Pnt4 = Base.Vector(fillet_center_x + r_fil * math.cos(beta), 0.0, fillet_center_z + r_fil * math.sin(beta))
        Pnt5 = Base.Vector(dk / 2.0, 0.0, 0.0)
        Pnt6 = Base.Vector(dia / 2.0 + r, 0.0, 0.0)  # start of fillet between head and shank
        Pnt7 = Base.Vector(dia / 2.0 + r - r * sqrt2_, 0.0, -r + r * sqrt2_)  # arc-point of fillet
        Pnt8 = Base.Vector(dia / 2.0, 0.0, -r)  # end of fillet
        Pnt9 = Base.Vector(dia / 2.0, 0.0, -thread_start)  # Start of thread
        # FreeCAD.Console.PrintMessage("Points defined fillet_center_x: " + str(fillet_center_x) + "\n")

        if SType == 'ISO14580':
            # Pnt0 = Base.Vector(0.0,0.0,k-A/4.0) #Center Point for countersunk
            Pnt0 = Base.Vector(0.0, 0.0, k - A / 8.0)  # Center Point for flat countersunk
            PntFlat = Base.Vector(A / 8.0, 0.0, k - A / 8.0)  # End of flat part
            Pnt1 = Base.Vector(A / 1.99, 0.0, k)  # countersunk edge at head
            edgeCham0 = Part.makeLine(Pnt0, PntFlat)
            edgeCham1 = Part.makeLine(PntFlat, Pnt1)
            edgeCham2 = Part.makeLine(Pnt1, Pnt2)
            edge1 = Part.Wire([edgeCham1, edgeCham2])  # make head with countersunk
            PntH1 = Base.Vector(A / 1.99, 0.0, 2.0 * k)

        else:
            Pnt0 = Base.Vector(0.0, 0.0, k)
            edge1 = Part.makeLine(Pnt0, Pnt2)  # make flat head

        edge2 = Part.Arc(Pnt2, Pnt3, Pnt4).toShape()
        edge3 = Part.makeLine(Pnt4, Pnt5)
        edge4 = Part.makeLine(Pnt5, Pnt6)
        edge5 = Part.Arc(Pnt6, Pnt7, Pnt8).toShape()
        # FreeCAD.Console.PrintMessage("Edges made fillet_center_z: " + str(fillet_center_z) + "\n")

        if SType == 'ISO1207':
            # Parameter for slot-recess: dk, n_min, k, t_min
            recess = Part.makePlane(dk, n_min, \
                                    Base.Vector(dk / 2.0, -n_min / 2.0, k + 1.0), Base.Vector(0.0, 0.0, -1.0))
            recess = recess.extrude(Base.Vector(0.0, 0.0, -t_min - 1.0))

            if self.rThread:
                Pnt11 = Base.Vector(0.0, 0.0, -r)  # helper point for real thread
                edgeZ1 = Part.makeLine(Pnt8, Pnt11)
                edgeZ0 = Part.makeLine(Pnt11, Pnt0)
                aWire = Part.Wire([edge1, edge2, edge3, edge4, edge5, \
                                   edgeZ1, edgeZ0])
            else:
                # bolt points
                PntB1 = Base.Vector(dia / 2.0, 0.0, -l)
                PntB2 = Base.Vector(0.0, 0.0, -l)

                edgeB2 = Part.makeLine(PntB1, PntB2)

                if thread_start <= r:
                    edgeB1 = Part.makeLine(Pnt8, PntB1)
                    aWire = Part.Wire([edge1, edge2, edge3, edge4, edge5, \
                                       edgeB1, edgeB2])
                else:
                    edge6 = Part.makeLine(Pnt8, Pnt9)
                    edgeB1 = Part.makeLine(Pnt9, PntB1)
                    aWire = Part.Wire([edge1, edge2, edge3, edge4, edge5, edge6, \
                                       edgeB1, edgeB2])

            aFace = Part.Face(aWire)
            head = aFace.revolve(Base.Vector(0.0, 0.0, 0.0), Base.Vector(0.0, 0.0, 1.0), 360.0)
            head = head.cut(recess)
            # FreeCAD.Console.PrintMessage("the head cut: " + str(dia) + "\n")
            # Part.show(head)
            if self.rThread:
                screwFaces = []
                for i in range(0, len(head.Faces) - 1):
                    screwFaces.append(head.Faces[i])
                rthread = self.makeShellthread(dia, P, l - r, False, -r, b)
                for threadFace in rthread.Faces:
                    screwFaces.append(threadFace)

                screwShell = Part.Shell(screwFaces)
                head = Part.Solid(screwShell)



        else:
            if self.rThread:
                aWire = Part.Wire([edge1, edge2, edge3, edge4, edge5])
            else:
                # bolt points
                PntB1 = Base.Vector(dia / 2.0, 0.0, -l)
                PntB2 = Base.Vector(0.0, 0.0, -l)

                edgeB2 = Part.makeLine(PntB1, PntB2)

                if thread_start <= r:
                    edgeB1 = Part.makeLine(Pnt8, PntB1)
                    aWire = Part.Wire([edge1, edge2, edge3, edge4, edge5, \
                                       edgeB1, edgeB2])
                else:
                    edge6 = Part.makeLine(Pnt8, Pnt9)
                    edgeB1 = Part.makeLine(Pnt9, PntB1)
                    aWire = Part.Wire([edge1, edge2, edge3, edge4, edge5, edge6, \
                                       edgeB1, edgeB2])

            # aFace =Part.Face(aWire)
            headShell = aWire.revolve(Base.Vector(0.0, 0.0, 0.0), Base.Vector(0.0, 0.0, 1.0), 360.0)
            # FreeCAD.Console.PrintMessage("the head with revolve: " + str(dia) + "\n")

            if SType == 'ISO7048':
                # hCut should be just a cylinder
                hCut = Part.makeCylinder(fillet_center_x, k, Pnt0)
                recess, recessShell = self.makeCross_H3(cT, mH, k)
                recessShell = recessShell.cut(hCut)
                topFace = headShell.Faces[0].cut(recess)
                screwFaces = [topFace.Faces[0]]
                screwFaces.extend(recessShell.Faces)
            if SType == 'ISO14580':
                # Ring-cutter for recess shell
                PntH2 = Base.Vector(A / 8.0, 0.0, 2.0 * k)
                edgeH1 = Part.makeLine(Pnt1, PntH1)
                edgeH2 = Part.makeLine(PntH1, PntH2)
                edgeH3 = Part.makeLine(PntH2, PntFlat)
                hWire = Part.Wire([edgeCham1, edgeH1, edgeH2, edgeH3])  # Cutter for recess-Shell
                hFace = Part.Face(hWire)
                hCut = hFace.revolve(Base.Vector(0.0, 0.0, 0.0), Base.Vector(0.0, 0.0, 1.0), 360)
                # Part.show(hWire)

                recess, recessShell = self.makeIso10664_3(tt, t_min, k)
                recessShell = recessShell.cut(hCut)
                topFace = headShell.Faces[0].cut(recess)
                screwFaces = [topFace.Faces[0]]
                screwFaces.extend(recessShell.Faces)

            for i in range(1, len(headShell.Faces)):
                screwFaces.append(headShell.Faces[i])

            if self.rThread:
                # head = self.cutIsoThread(head, dia, P, turns, l)
                rthread = self.makeShellthread(dia, P, l - r, False, -r, b)
                # head = head.fuse(rthread)
                # Part.show(rthread)
                for threadFace in rthread.Faces:
                    screwFaces.append(threadFace)

            screwShell = Part.Shell(screwFaces)
            head = Part.Solid(screwShell)

        return head

    # make the ISO 4017 Hex-head-screw
    # make the ISO 4014 Hex-head-bolt
    # make the ASMEB18.2.1.6 Hex-head-bolt
    def makeHexHeadBolt(self):
        dia = self.getDia(self.fastenerDiam, False)
        l = self.fastenerLen
        #FreeCAD.Console.PrintMessage("the head with thread type: " + str(ThreadType) + "\n")
        if self.fastenerType == 'ISO4017':
            P, c, dw, e, k, r, s = self.dimTable
            b = l

        if self.fastenerType == 'ISO4014':
            P, b1, b2, b3, c, dw, e, k, r, s = self.dimTable
            if l <= 125.0:
                b = b1
            else:
                if l <= 200.0:
                    b = b2
                else:
                    b = b3

        if self.fastenerType == 'ASMEB18.2.1.6':
            b, P, c, dw, e, k, r, s = self.dimTable
            if l > 6 * 25.4:
                b += 6.35

        a = l - b
        sqrt2_ = 1.0 / math.sqrt(2.0)
        cham = (e - s) * math.sin(math.radians(15))  # needed for chamfer at head top

        # Head Points  Usage of k, s, cham, c, dw, dia, r, a
        # FreeCAD.Console.PrintMessage("the head with halfturns: " + str(halfturns) + "\n")
        Pnt0 = Base.Vector(0.0, 0.0, k)
        Pnt2 = Base.Vector(s / 2.0, 0.0, k)
        Pnt3 = Base.Vector(s / math.sqrt(3.0), 0.0, k - cham)
        Pnt4 = Base.Vector(s / math.sqrt(3.0), 0.0, c)
        Pnt5 = Base.Vector(dw / 2.0, 0.0, c)
        Pnt6 = Base.Vector(dw / 2.0, 0.0, 0.0)
        Pnt7 = Base.Vector(dia / 2.0 + r, 0.0, 0.0)  # start of fillet between head and shank
        Pnt8 = Base.Vector(dia / 2.0 + r - r * sqrt2_, 0.0, -r + r * sqrt2_)  # arc-point of fillet
        Pnt9 = Base.Vector(dia / 2.0, 0.0, -r)  # end of fillet
        Pnt10 = Base.Vector(dia / 2.0, 0.0, -a)  # Start of thread

        edge1 = Part.makeLine(Pnt0, Pnt2)
        edge2 = Part.makeLine(Pnt2, Pnt3)
        edge3 = Part.makeLine(Pnt3, Pnt4)
        edge4 = Part.makeLine(Pnt4, Pnt5)
        edge5 = Part.makeLine(Pnt5, Pnt6)
        edge6 = Part.makeLine(Pnt6, Pnt7)
        edge7 = Part.Arc(Pnt7, Pnt8, Pnt9).toShape()

        # create cutting tool for hexagon head
        # Parameters s, k, outer circle diameter =  e/2.0+10.0
        extrude = self.makeHextool(s, k, s * 2.0)

        # if self.RealThread.isChecked():
        if self.rThread:
            Pnt11 = Base.Vector(0.0, 0.0, -r)  # helper point for real thread
            edgeZ1 = Part.makeLine(Pnt9, Pnt11)
            edgeZ0 = Part.makeLine(Pnt11, Pnt0)
            aWire = Part.Wire([edge1, edge2, edge3, edge4, edge5, edge6, edge7, \
                               edgeZ1, edgeZ0])

            aFace = Part.Face(aWire)
            head = aFace.revolve(Base.Vector(0.0, 0.0, 0.0), Base.Vector(0.0, 0.0, 1.0), 360.0)
            # FreeCAD.Console.PrintMessage("the head with revolve: " + str(dia) + "\n")

            # Part.show(extrude)
            head = head.cut(extrude)
            # FreeCAD.Console.PrintMessage("the head cut: " + str(dia) + "\n")
            # Part.show(head)

            headFaces = []
            for i in range(18):
                headFaces.append(head.Faces[i])

            rthread = self.makeShellthread(dia, P, l - r, True, -r, b)
            # Part.show(rthread)
            for tFace in rthread.Faces:
                headFaces.append(tFace)
            headShell = Part.Shell(headFaces)
            head = Part.Solid(headShell)

        else:
            # bolt points
            cham_t = P * math.sqrt(3.0) / 2.0 * 17.0 / 24.0

            PntB0 = Base.Vector(0.0, 0.0, -a)
            PntB1 = Base.Vector(dia / 2.0, 0.0, -l + cham_t)
            PntB2 = Base.Vector(dia / 2.0 - cham_t, 0.0, -l)
            PntB3 = Base.Vector(0.0, 0.0, -l)

            edgeB1 = Part.makeLine(Pnt10, PntB1)
            edgeB2 = Part.makeLine(PntB1, PntB2)
            edgeB3 = Part.makeLine(PntB2, PntB3)

            edgeZ0 = Part.makeLine(PntB3, Pnt0)
            if a <= r:
                edgeB1 = Part.makeLine(Pnt9, PntB1)
                aWire = Part.Wire([edge1, edge2, edge3, edge4, edge5, edge6, edge7, \
                                   edgeB1, edgeB2, edgeB3, edgeZ0])

            else:
                edge8 = Part.makeLine(Pnt9, Pnt10)
                edgeB1 = Part.makeLine(Pnt10, PntB1)
                aWire = Part.Wire([edge1, edge2, edge3, edge4, edge5, edge6, edge7, edge8, \
                                   edgeB1, edgeB2, edgeB3, edgeZ0])

            aFace = Part.Face(aWire)
            head = aFace.revolve(Base.Vector(0.0, 0.0, 0.0), Base.Vector(0.0, 0.0, 1.0), 360.0)
            # FreeCAD.Console.PrintMessage("the head with revolve: " + str(dia) + "\n")

            # Part.show(extrude)
            head = head.cut(extrude)
            # FreeCAD.Console.PrintMessage("the head cut: " + str(dia) + "\n")

        return head

    # DIN 7998 Wood Thread
    # zs: z position of start of the threaded part
    # ze: z position of end of the flat portion of screw (just where the tip starts) 
    # zt: z position of screw tip
    # ro: outer radius
    # ri: inner radius
    # p:  thread pitch
    def makeDin7998Thread(self, zs, ze, zt, ri, ro, p):
        epsilon = 0.03                          # epsilon needed since OCCT struggle to handle overlaps
        tph = ro - ri                           # thread profile height
        tphb = tph / math.tan(math.radians(60)) # thread profile half base
        tpratio = 0.5                           # size ratio between tip start thread and standard thread 
        tph2 = tph * tpratio
        tphb2 = tphb * tpratio
        tipH = ze - zt
        # tip thread profile
        Pnt0a = FreeCAD.Vector(0.0, 0.0, -tphb2)
        Pnt1a = FreeCAD.Vector(0.0, 0.0, tphb2)
        Pnt2a = FreeCAD.Vector(2.0 * tphb2, 0.0, tphb2)

        edge1a = Part.makeLine(Pnt0a, Pnt1a)
        edge2a = Part.makeLine(Pnt1a, Pnt2a)
        edge3a = Part.makeLine(Pnt2a, Pnt0a)

        aWire = Part.Wire([edge1a, edge2a, edge3a])
        aWire.translate(FreeCAD.Vector(epsilon, 0.0, 3.0 * tphb2))

        # top thread profile
        Pnt0b = FreeCAD.Vector(0.0, 0.0, -tphb)
        Pnt1b = FreeCAD.Vector(0.0, 0.0, tphb)
        Pnt2b = FreeCAD.Vector(tph, 0.0, 0.0)

        edge1b = Part.makeLine(Pnt0b, Pnt1b)
        edge2b = Part.makeLine(Pnt1b, Pnt2b)
        edge3b = Part.makeLine(Pnt2b, Pnt0b)

        bWire = Part.Wire([edge1b, edge2b, edge3b])
        #bWire.translate(FreeCAD.Vector(ri - epsilon, 0.0, ze + tphb))
        bWire.translate(FreeCAD.Vector(ri - epsilon, 0.0, tphb + tipH))
        
        # create helix for tip thread part
        numTurns = math.floor(tipH / p)
        #Part.show(hlx)
        hlx = Part.makeLongHelix(p, numTurns * p, 5, 0, self.leftHanded)
        sweep = Part.BRepOffsetAPI.MakePipeShell(hlx)
        sweep.setFrenetMode(True)
        sweep.setTransitionMode(1)  # right corner transition
        sweep.add(aWire)
        sweep.add(bWire)
        if sweep.isReady():
            sweep.build()
            sweep.makeSolid()
            tip_solid = sweep.shape()
            tip_solid.translate(FreeCAD.Vector(0.0, 0.0, zt))
            #Part.show(tip_solid)
        else:
            raise RuntimeError("Failed to create woodscrew tip thread")

        # create helix for body thread part
        hlx = Part.makeLongHelix(p, zs - ze, 5, 0, self.leftHanded)
        hlx.translate(FreeCAD.Vector(0.0, 0.0, tipH))
        sweep = Part.BRepOffsetAPI.MakePipeShell(hlx)
        sweep.setFrenetMode(True)
        sweep.setTransitionMode(1)  # right corner transition
        sweep.add(bWire)
        if sweep.isReady():
            sweep.build()
            sweep.makeSolid()
            body_solid = sweep.shape()
            body_solid.translate(FreeCAD.Vector(0.0, 0.0, zt))
            #Part.show(body_solid)
        else:
            raise RuntimeError("Failed to create woodscrew body thread")

        thread_solid = body_solid.fuse(tip_solid)
        # rotate the thread solid to prevent OCC errors due to cylinder seams aligning
        thread_solid.rotate(Base.Vector(0, 0, 0), Base.Vector(0, 0, 1), 180)
        #Part.show(thread_solid, "thread_solid")
        return thread_solid



    # DIN 571 wood-screw
    def makeWoodScrew(self):
        SType = self.fastenerType
        l = self.fastenerLen
        dia = float(self.fastenerDiam.split()[0])
        ds, da, d3, k, s, P = self.dimTable
        d = dia / 2.0
        d3h = d3 / 2.0
        r = (da-ds)/2.0
        e = s/math.cos(math.radians(30))
        sqrt2_ = 1.0 / math.sqrt(2.0)
        cham = (e - s) * math.sin(math.radians(15))  # needed for chamfer at head top
        
        Pnt0 = Base.Vector(0.0, 0.0, k)
        Pnt2 = Base.Vector(s / 2.0, 0.0, k)
        Pnt3 = Base.Vector(s / math.sqrt(3.0), 0.0, k - cham)
        Pnt4 = Base.Vector(s / math.sqrt(3.0), 0.0, 0.0)
        Pnt7 = Base.Vector(d + r, 0.0, 0.0)  # start of fillet between head and shank
        Pnt8 = Base.Vector(d + r - r * sqrt2_, 0.0, -r + r * sqrt2_)  # arc-point of fillet
        Pnt9 = Base.Vector(d, 0.0, -r)  # end of fillet

        edge1 = Part.makeLine(Pnt0, Pnt2)
        edge2 = Part.makeLine(Pnt2, Pnt3)
        edge3 = Part.makeLine(Pnt3, Pnt4)
        edge4 = Part.makeLine(Pnt4, Pnt7)
        edge5 = Part.Arc(Pnt7, Pnt8, Pnt9).toShape()

        # create cutting tool for hexagon head
        # Parameters s, k, outer circle diameter =  e/2.0+10.0
        extrude = self.makeHextool(s, k, s * 2.0)

        #if self.rThread:
        #  pass
        #else:
        if self.rThread:
            dt = d3 / 2.0
        else:
            dt = d
        angle = math.radians(20)
        x2 = dt * math.cos(angle)
        z2 = dt * math.sin(angle)
        z3 = x2 / math.tan(angle)
        ftl = l - z2 - z3 # flat part (total length - tip)
        PntB0 = Base.Vector(d, 0.0, 0.4 * -ftl)
        PntB1 = Base.Vector(dt, 0.0, -ftl)
        PntB2 = Base.Vector(dt * math.cos(angle / 2.0),
                            0.0,
                            -l + z2 + z3 - d * math.sin(angle / 2.0))
        PntB3 = Base.Vector(x2, 0.0, -l + z3)
        PntB4 = Base.Vector(0.0, 0.0, -l)
        
        edge6 = Part.makeLine(Pnt9, PntB0)
        edge8 = Part.Arc(PntB1, PntB2, PntB3).toShape()
        edge9 = Part.makeLine(PntB3, PntB4)
        edgeZ0 = Part.makeLine(PntB4, Pnt0)
        
        if self.rThread:
            PntB0t = Base.Vector(dt, 0.0, 0.4 * -ftl - (d - dt))
            edge7 = Part.makeLine(PntB0, PntB0t)
            edge7t = Part.makeLine(PntB0t, PntB1)
            aWire = Part.Wire([edge1, edge2, edge3, edge4, edge5, edge6,\
                           edge7, edge7t, edge8, edge9, edgeZ0])
        else:
            edge7 = Part.makeLine(PntB0, PntB1)
            aWire = Part.Wire([edge1, edge2, edge3, edge4, edge5, edge6,\
                           edge7, edge8, edge9, edgeZ0])
        
        aFace = Part.Face(aWire)
        head = aFace.revolve(Base.Vector(0.0, 0.0, 0.0), Base.Vector(0.0, 0.0, 1.0), 360.0)
        head = head.cut(extrude)
        if self.rThread:
            thread = self.makeDin7998Thread(0.4 * -ftl, -ftl, -l, d3h, d, P)
            #Part.show(thread)
            head = head.fuse(thread)
        
        return head

      
    # EN 1662 Hex-head-bolt with flange - small series
    # EN 1665 Hexagon bolts with flange, heavy series
    # ASMEB18.2.1.8 Hexagon bolts with flange, heavy series
    def makeHexHeadWithFlunge(self):
        dia = self.getDia(self.fastenerDiam, False)
        SType = self.fastenerType
        l = self.fastenerLen
        # FreeCAD.Console.PrintMessage("the head with l: " + str(l) + "\n")
        if SType == 'EN1662' or SType == 'EN1665':
            P, b0, b1, b2, b3, c, dc, dw, e, k, kw, f, r1, s = self.dimTable
        elif SType == 'ASMEB18.2.1.8':
            b0, P, c, dc, kw, r1, s = self.dimTable
            b = b0
        if l < b0:
            b = l - 2 * P
        elif SType != 'ASMEB18.2.1.8':
            if l <= 125.0:
                b = b1
            else:
                if l <= 200.0:
                    b = b2
                else:
                    b = b3

        # FreeCAD.Console.PrintMessage("the head with isoEN1662: " + str(c) + "\n")
        cham = s * (2.0 / math.sqrt(3.0) - 1.0) * math.sin(math.radians(25))  # needed for chamfer at head top

        thread_start = l - b
        sqrt2_ = 1.0 / math.sqrt(2.0)

        # Flange is made with a radius of c
        beta = math.radians(25.0)
        tan_beta = math.tan(beta)

        # Calculation of Arc points of flange edge using dc and c
        arc1_x = dc / 2.0 - c / 2.0 + (c / 2.0) * math.sin(beta)
        arc1_z = c / 2.0 + (c / 2.0) * math.cos(beta)

        hF = arc1_z + (arc1_x - s / 2.0) * tan_beta  # height of flange at center

        kmean = arc1_z + (arc1_x - s / math.sqrt(3.0)) * tan_beta + kw * 1.1 + cham
        # kmean = k * 0.95

        # Hex-Head Points
        # FreeCAD.Console.PrintMessage("the head with math a: " + str(a_point) + "\n")
        PntH0 = Base.Vector(0.0, 0.0, kmean * 0.9)
        PntH1 = Base.Vector(s / 2.0 * 0.8 - r1 / 2.0, 0.0, kmean * 0.9)
        PntH1a = Base.Vector(s / 2.0 * 0.8 - r1 / 2.0 + r1 / 2.0 * sqrt2_, 0.0,
                             kmean * 0.9 + r1 / 2.0 - r1 / 2.0 * sqrt2_)
        PntH1b = Base.Vector(s / 2.0 * 0.8, 0.0, kmean * 0.9 + r1 / 2.0)
        PntH2 = Base.Vector(s / 2.0 * 0.8, 0.0, kmean - r1)
        PntH2a = Base.Vector(s / 2.0 * 0.8 + r1 - r1 * sqrt2_, 0.0, kmean - r1 + r1 * sqrt2_)
        PntH2b = Base.Vector(s / 2.0 * 0.8 + r1, 0.0, kmean)
        PntH3 = Base.Vector(s / 2.0, 0.0, kmean)
        # PntH4 = Base.Vector(s/math.sqrt(3.0),0.0,kmean-cham)   #s/math.sqrt(3.0)
        # PntH5 = Base.Vector(s/math.sqrt(3.0),0.0,c)
        # PntH6 = Base.Vector(0.0,0.0,c)

        edgeH1 = Part.makeLine(PntH0, PntH1)
        edgeH2 = Part.Arc(PntH1, PntH1a, PntH1b).toShape()
        edgeH3 = Part.makeLine(PntH1b, PntH2)
        edgeH3a = Part.Arc(PntH2, PntH2a, PntH2b).toShape()
        edgeH3b = Part.makeLine(PntH2b, PntH3)

        hWire = Part.Wire([edgeH1, edgeH2, edgeH3, edgeH3a, edgeH3b])
        topShell = hWire.revolve(Base.Vector(0.0, 0.0, 0.0), Base.Vector(0.0, 0.0, 1.0), 360)
        # Part.show(hWire)
        # Part.show(topShell)

        # create a cutter ring to generate the chamfer at the top of the hex
        chamHori = s / math.sqrt(3.0) - s / 2.0
        PntC1 = Base.Vector(s / 2.0 - chamHori, 0.0, kmean + kmean)
        PntC2 = Base.Vector(s / math.sqrt(3.0) + chamHori, 0.0, kmean + kmean)
        PntC3 = Base.Vector(s / 2.0 - chamHori, 0.0, kmean + cham)
        PntC4 = Base.Vector(s / math.sqrt(3.0) + chamHori, 0.0, kmean - cham - cham)  # s/math.sqrt(3.0)
        edgeC1 = Part.makeLine(PntC3, PntC1)
        edgeC2 = Part.makeLine(PntC1, PntC2)
        edgeC3 = Part.makeLine(PntC2, PntC4)
        edgeC4 = Part.makeLine(PntC4, PntC3)
        cWire = Part.Wire([edgeC4, edgeC1, edgeC2, edgeC3])
        cFace = Part.Face(cWire)
        chamCut = cFace.revolve(Base.Vector(0.0, 0.0, 0.0), Base.Vector(0.0, 0.0, 1.0), 360)
        # Part.show(cWire)
        # Part.show(chamCut)

        # create hexagon
        mhex = Base.Matrix()
        mhex.rotateZ(math.radians(60.0))
        polygon = []
        vhex = Base.Vector(s / math.sqrt(3.0), 0.0, kmean)
        for i in range(6):
            polygon.append(vhex)
            vhex = mhex.multiply(vhex)
        polygon.append(vhex)
        hexagon = Part.makePolygon(polygon)
        hexFace = Part.Face(hexagon)
        solidHex = hexFace.extrude(Base.Vector(0.0, 0.0, c - kmean))
        # Part.show(solidHex)
        hexCham = solidHex.cut(chamCut)
        # Part.show(hexCham)

        topFaces = topShell.Faces

        topFaces.append(hexCham.Faces[6])
        topFaces.append(hexCham.Faces[12])
        topFaces.append(hexCham.Faces[14])
        topFaces.append(hexCham.Faces[13])
        topFaces.append(hexCham.Faces[8])
        topFaces.append(hexCham.Faces[2])
        topFaces.append(hexCham.Faces[1])

        hexFaces = [hexCham.Faces[5], hexCham.Faces[11], hexCham.Faces[10]]
        hexFaces.extend([hexCham.Faces[9], hexCham.Faces[3], hexCham.Faces[0]])
        hexShell = Part.Shell(hexFaces)

        # Center of flange:
        Pnt0 = Base.Vector(0.0, 0.0, hF)
        Pnt1 = Base.Vector(s / 2.0, 0.0, hF)

        # arc edge of flange:
        Pnt2 = Base.Vector(arc1_x, 0.0, arc1_z)
        Pnt3 = Base.Vector(dc / 2.0, 0.0, c / 2.0)
        Pnt4 = Base.Vector((dc - c) / 2.0, 0.0, 0.0)

        Pnt5 = Base.Vector(dia / 2.0 + r1, 0.0, 0.0)  # start of fillet between head and shank
        Pnt6 = Base.Vector(dia / 2.0 + r1 - r1 * sqrt2_, 0.0, -r1 + r1 * sqrt2_)  # arc-point of fillet
        Pnt7 = Base.Vector(dia / 2.0, 0.0, -r1)  # end of fillet
        Pnt8 = Base.Vector(dia / 2.0, 0.0, -thread_start)  # Start of thread

        edge1 = Part.makeLine(Pnt0, Pnt1)
        edge2 = Part.makeLine(Pnt1, Pnt2)
        edge3 = Part.Arc(Pnt2, Pnt3, Pnt4).toShape()
        edge4 = Part.makeLine(Pnt4, Pnt5)
        edge5 = Part.Arc(Pnt5, Pnt6, Pnt7).toShape()

        # make a cutter for the hexShell
        PntHC1 = Base.Vector(0.0, 0.0, arc1_z)
        PntHC2 = Base.Vector(0.0, 0.0, 0.0)

        edgeHC1 = Part.makeLine(Pnt2, PntHC1)
        edgeHC2 = Part.makeLine(PntHC1, PntHC2)
        edgeHC3 = Part.makeLine(PntHC2, Pnt0)

        HCWire = Part.Wire([edge2, edgeHC1, edgeHC2, edgeHC3, edge1])
        HCFace = Part.Face(HCWire)
        hex2Cut = HCFace.revolve(Base.Vector(0.0, 0.0, 0.0), Base.Vector(0.0, 0.0, 1.0), 360)

        hexShell = hexShell.cut(hex2Cut)
        # Part.show(hexShell)

        topFaces.extend(hexShell.Faces)

        # bolt points
        cham_t = P * math.sqrt(3.0) / 2.0 * 17.0 / 24.0

        PntB0 = Base.Vector(0.0, 0.0, -thread_start)
        PntB1 = Base.Vector(dia / 2.0, 0.0, -l + cham_t)
        PntB2 = Base.Vector(dia / 2.0 - cham_t, 0.0, -l)
        PntB3 = Base.Vector(0.0, 0.0, -l)

        edgeB2 = Part.makeLine(PntB1, PntB2)
        edgeB3 = Part.makeLine(PntB2, PntB3)

        # if self.RealThread.isChecked():
        if self.rThread:
            aWire = Part.Wire([edge2, edge3, edge4, edge5])
            boltIndex = 4

        else:
            if thread_start <= r1:
                edgeB1 = Part.makeLine(Pnt7, PntB1)
                aWire = Part.Wire([edge2, edge3, edge4, edge5, edgeB1, edgeB2, edgeB3])
                boltIndex = 7
            else:
                edgeB1 = Part.makeLine(Pnt8, PntB1)
                edge6 = Part.makeLine(Pnt7, Pnt8)
                aWire = Part.Wire([edge2, edge3, edge4, edge5, edge6, \
                                   edgeB1, edgeB2, edgeB3])
                boltIndex = 8

        # aFace =Part.Face(aWire)
        # Part.show(aWire)
        headShell = aWire.revolve(Base.Vector(0.0, 0.0, 0.0), Base.Vector(0.0, 0.0, 1.0), 360)
        # FreeCAD.Console.PrintMessage("the head with revolve: " + str(dia) + "\n")
        # Part.show(headShell)
        chamFace = headShell.Faces[0].cut(solidHex)
        # Part.show(chamFace)

        topFaces.append(chamFace.Faces[0])
        for i in range(1, boltIndex):
            topFaces.append(headShell.Faces[i])

        if self.rThread:
            rthread = self.makeShellthread(dia, P, l - r1, True, -r1, b)
            for tFace in rthread.Faces:
                topFaces.append(tFace)
            headShell = Part.Shell(topFaces)
            screw = Part.Solid(headShell)
        else:
            screwShell = Part.Shell(topFaces)
            screw = Part.Solid(screwShell)

        return screw


    # make ISO 4762 Allan Screw head
    # DIN 7984 Allan Screw head
    # ISO 14579 Hexalobular socket head cap screws
    # ASMEB18.3.1A Allan Screw head
    def makeCylinderHeadScrew(self):
        SType = self.fastenerType
        l = self.fastenerLen
        dia = self.getDia(self.fastenerDiam, False)
        # FreeCAD.Console.PrintMessage("der 4762Kopf mit l: " + str(l) + "\n")
        # FreeCAD.Console.PrintMessage("the head with iso r: " + str(r) + "\n")
        if SType == 'ISO14579':
            P, b, dk_max, da, ds_mean, e, lf, k, r, s_mean, t, v, dw, w = FsData["iso4762def"][self.fastenerDiam]
            tt, A, t = self.dimTable
            # Head Points 30° countersunk
            # Pnt0 = Base.Vector(0.0,0.0,k-A/4.0) #Center Point for countersunk
            Pnt0 = Base.Vector(0.0, 0.0, k - A / 8.0)  # Center Point for flat countersunk
            PntFlat = Base.Vector(A / 8.0, 0.0, k - A / 8.0)  # End of flat part
            Pnt1 = Base.Vector(A / 1.99, 0.0, k)  # countersunk edge at head
            edgeCham0 = Part.makeLine(Pnt0, PntFlat)
            edgeCham1 = Part.makeLine(PntFlat, Pnt1)
            edge1 = Part.Wire([edgeCham0, edgeCham1])

            # Here is the next approach to shorten the head building time
            # Make two helper points to create a cutting tool for the
            # recess and recess shell.
            PntH1 = Base.Vector(A / 1.99, 0.0, 2.0 * k)

        elif SType == 'DIN7984' or SType == 'ASMEB18.3.1G':
            if SType == 'DIN7984':
                P, b, dk_max, da, ds_min, e, k, r, s_mean, t, v, dw = self.dimTable
            elif SType == 'ASMEB18.3.1G':
                P, b, A, H, C_max, J, T, K, r = (x*25.4 for x in self.dimTable)
                dk_max = A
                k = H
                v = C_max
                s_mean = J
                t = T
                dw = A - K
            e_cham = 2.0 * s_mean / math.sqrt(3.0)
            # Head Points 45° countersunk
            Pnt0 = Base.Vector(0.0, 0.0, k - e_cham / 1.99 / 2.0)  # Center Point for countersunk
            PntFlat = Base.Vector(e_cham / 1.99 / 2.0, 0.0, k - e_cham / 1.99 / 2.0)  # End of flat part
            Pnt1 = Base.Vector(e_cham / 1.99, 0.0, k)  # countersunk edge at head
            edgeCham0 = Part.makeLine(Pnt0, PntFlat)
            edgeCham1 = Part.makeLine(PntFlat, Pnt1)
            edge1 = Part.Wire([edgeCham0, edgeCham1])
            PntH1 = Base.Vector(e_cham / 1.99, 0.0, 2.0 * k)

        elif SType == 'DIN6912':
            P, b, dk_max, da, ds_min, e, k, r, s_mean, t, t2, v, dw = self.dimTable
            e_cham = 2.0 * s_mean / math.sqrt(3.0)
            # Head Points 45° countersunk
            Pnt0 = Base.Vector(0.0, 0.0, k - e_cham / 1.99 / 2.0)  # Center Point for countersunk
            PntFlat = Base.Vector(e_cham / 1.99 / 2.0, 0.0, k - e_cham / 1.99 / 2.0)  # End of flat part
            Pnt1 = Base.Vector(e_cham / 1.99, 0.0, k)  # countersunk edge at head
            edgeCham0 = Part.makeLine(Pnt0, PntFlat)
            edgeCham1 = Part.makeLine(PntFlat, Pnt1)
            edge1 = Part.Wire([edgeCham0, edgeCham1])
            PntH1 = Base.Vector(e_cham / 1.99, 0.0, 2.0 * k)

        elif SType == 'ISO4762' or SType == 'ASMEB18.3.1A':
            if SType == 'ISO4762':
                P, b, dk_max, da, ds_mean, e, lf, k, r, s_mean, t, v, dw, w = self.dimTable
            if SType == 'ASMEB18.3.1A':
                P, b, dk_max, k, r, s_mean, t, v, dw = self.dimTable
            e_cham = 2.0 * s_mean / math.sqrt(3.0)
            # Head Points 45° countersunk
            Pnt0 = Base.Vector(0.0, 0.0, k - e_cham / 1.99 / 2.0)  # Center Point for countersunk
            PntFlat = Base.Vector(e_cham / 1.99 / 2.0, 0.0, k - e_cham / 1.99 / 2.0)  # End of flat part
            Pnt1 = Base.Vector(e_cham / 1.99, 0.0, k)  # countersunk edge at head
            edgeCham0 = Part.makeLine(Pnt0, PntFlat)
            edgeCham1 = Part.makeLine(PntFlat, Pnt1)
            edge1 = Part.Wire([edgeCham0, edgeCham1])
            PntH1 = Base.Vector(e_cham / 1.99, 0.0, 2.0 * k)

        PntH2 = Base.Vector(0.0, 0.0, 2.0 * k)
        edgeH1 = Part.makeLine(Pnt1, PntH1)
        edgeH2 = Part.makeLine(PntH1, PntH2)
        edgeH3 = Part.makeLine(PntH2, Pnt0)
        hWire = Part.Wire([edge1, edgeH1, edgeH2, edgeH3])  # Cutter for recess-Shell
        hFace = Part.Face(hWire)
        hCut = hFace.revolve(Base.Vector(0.0, 0.0, 0.0), Base.Vector(0.0, 0.0, 1.0), 360)
        # Part.show(hWire)
 
        sqrt2_ = 1.0 / math.sqrt(2.0)
        # depth = s_mean / 3.0

        thread_start = l - b
        # rad30 = math.radians(30.0)
        # Head Points
        Pnt2 = Base.Vector(dk_max / 2.0 - v, 0.0, k)  # start of fillet
        Pnt3 = Base.Vector(dk_max / 2.0 - v + v * sqrt2_, 0.0, k - v + v * sqrt2_)  # arc-point of fillet
        Pnt4 = Base.Vector(dk_max / 2.0, 0.0, k - v)  # end of fillet
        Pnt5 = Base.Vector(dk_max / 2.0, 0.0, (dk_max - dw) / 2.0)  # we have a chamfer here
        Pnt6 = Base.Vector(dw / 2.0, 0.0, 0.0)  # end of chamfer
        Pnt7 = Base.Vector(dia / 2.0 + r, 0.0, 0.0)  # start of fillet between head and shank
        Pnt8 = Base.Vector(dia / 2.0 + r - r * sqrt2_, 0.0, -r + r * sqrt2_)  # arc-point of fillet
        Pnt9 = Base.Vector(dia / 2.0, 0.0, -r)  # end of fillet
        Pnt10 = Base.Vector(dia / 2.0, 0.0, -thread_start)  # start of thread

        edge1 = Part.makeLine(Pnt0, Pnt1)
        edge2 = Part.makeLine(Pnt1, Pnt2)
        edge3 = Part.Arc(Pnt2, Pnt3, Pnt4).toShape()
        edge4 = Part.makeLine(Pnt4, Pnt5)
        edge5 = Part.makeLine(Pnt5, Pnt6)
        edge6 = Part.makeLine(Pnt6, Pnt7)
        edge7 = Part.Arc(Pnt7, Pnt8, Pnt9).toShape()

        if self.rThread:
            aWire = Part.Wire([edge2, edge3, edge4, edge5, edge6, edge7])

        else:
            # bolt points
            cham_t = P * math.sqrt(3.0) / 2.0 * 17.0 / 24.0

            PntB1 = Base.Vector(dia / 2.0, 0.0, -l + cham_t)
            PntB2 = Base.Vector(dia / 2.0 - cham_t, 0.0, -l)
            PntB3 = Base.Vector(0.0, 0.0, -l)

            # edgeB1 = Part.makeLine(Pnt10,PntB1)
            edgeB2 = Part.makeLine(PntB1, PntB2)
            edgeB3 = Part.makeLine(PntB2, PntB3)

            if thread_start <= (r + 0.0001):
                edgeB1 = Part.makeLine(Pnt9, PntB1)
                aWire = Part.Wire([edge2, edge3, edge4, edge5, edge6, edge7, \
                                   edgeB1, edgeB2, edgeB3])
            else:
                edge8 = Part.makeLine(Pnt9, Pnt10)
                edgeB1 = Part.makeLine(Pnt10, PntB1)
                aWire = Part.Wire([edge2, edge3, edge4, edge5, edge6, edge7, edge8, \
                                   edgeB1, edgeB2, edgeB3])
            # Part.show(aWire)

        headShell = aWire.revolve(Base.Vector(0.0, 0.0, 0.0), Base.Vector(0.0, 0.0, 1.0), 360)
        # head = Part.Solid(headShell)
        # Part.show(aWire)
        # FreeCAD.Console.PrintMessage("the head with revolve: " + str(dia) + "\n")
        headFaces = headShell.Faces

        # Hex cutout
        if SType == 'ISO14579':
            # recess = self.makeIso10664(tt, t, k) # hexalobular recess
            recess, recessShell = self.makeIso10664_3(tt, t, k)  # hexalobular recess
        elif SType == 'DIN6912':
            recess, recessShell = self.makeAllen2(s_mean, t, k, t2)  # hex with center
        else:
            recess, recessShell = self.makeAllen2(s_mean, t, k)

        recessShell = recessShell.cut(hCut)
        topFace = hCut.Faces[1]
        # topFace = hCut.Faces[0]
        topFace = topFace.cut(recess)
        # Part.show(topFace)
        # Part.show(recessShell)
        # Part.show(headShell)
        headFaces.append(topFace.Faces[0])
        # headFaces.append(hCut.Faces[2])

        # allenscrew = head.cut(recess)
        # Part.show(hCut)
        headFaces.extend(recessShell.Faces)

        # if self.RealThread.isChecked():
        if self.rThread:
            # head = self.cutIsoThread(head, dia, P, turns, l)
            rthread = self.makeShellthread(dia, P, l - r, True, -r, b)
            # Part.show(rthread)
            for tFace in rthread.Faces:
                headFaces.append(tFace)
            headShell = Part.Shell(headFaces)
            allenscrew = Part.Solid(headShell)
        else:
            headShell = Part.Shell(headFaces)
            allenscrew = Part.Solid(headShell)

        return allenscrew

    # make ISO 7379 Hexagon socket head shoulder screw
    def makeShoulderScrew(self):
        SType = self.fastenerType
        l = self.fastenerLen
        #if SType == 'ISO7379' or SType == 'ASMEB18.3.4':
        P, d1, d3, l2, l3, SW = self.dimTable
        d2 = self.getDia(self.fastenerDiam, False)
        l1 = l
        # define the fastener head and shoulder
        # applicable for both threaded and unthreaded versions
        point1 = Base.Vector(0, 0, l1 + l3)
        point2 = Base.Vector(d3 / 2 - 0.04 * d3, 0, l3 + l1)
        point3 = Base.Vector(d3 / 2, 0, l3 - 0.04 * d3 + l1)
        point4 = Base.Vector(d3 / 2, 0, l1)
        point5 = Base.Vector(d1 / 2, 0, l1)
        point6 = Base.Vector(d1 / 2 - 0.04 * d1, 0, l1 - 0.1 * l3)
        point7 = Base.Vector(d1 / 2, 0, l1 - 0.2 * l3)
        point8 = Base.Vector(d1 / 2, 0, 0)
        point9 = Base.Vector(d2 / 2, 0, 0)
        edge1 = Part.makeLine(point1, point2)
        edge2 = Part.makeLine(point2, point3)
        edge3 = Part.makeLine(point3, point4)
        edge4 = Part.makeLine(point4, point5)
        edge5 = Part.Arc(point5, point6, point7).toShape()
        edge6 = Part.makeLine(point7, point8)
        edge7 = Part.makeLine(point8, point9)
        top_face_profile = Part.Wire([edge1])
        top_face = top_face_profile.revolve(Base.Vector(0, 0, 0), Base.Vector(0, 0, 1), 360)
        head_shoulder_profile = Part.Wire([edge2, edge3, edge4, edge5, edge6, edge7])
        if not self.rThread:
            # if a modelled thread is not desired:
            # add a cylindrical section to represent the threads
            point10 = Base.Vector(d2 / 2 - 0.075 * d2, 0, -0.075 * l2)
            point11 = Base.Vector(d2 / 2, 0, -0.15 * l2)
            point12 = Base.Vector(d2 / 2, 0, -1 * l2 + 0.1 * d2)
            point13 = Base.Vector(d2 / 2 - 0.1 * d2, 0, -1 * l2)
            point14 = Base.Vector(0, 0, -1 * l2)
            edge8 = Part.Arc(point9, point10, point11).toShape()
            edge9 = Part.makeLine(point11, point12)
            edge10 = Part.makeLine(point12, point13)
            edge11 = Part.makeLine(point13, point14)
            # append the wire with the added section
            p_profile = Part.Wire([head_shoulder_profile, edge8, edge9, edge10, edge11])
            # revolve the profile into a shell object
            p_shell = p_profile.revolve(Base.Vector(0, 0, 0), Base.Vector(0, 0, 1), 360)
        else:
            # if we need a modelled thread:
            # the revolved profile is only the head and shoulder
            p_profile = head_shoulder_profile
            p_shell = p_profile.revolve(Base.Vector(0, 0, 0), Base.Vector(0, 0, 1), 360)
            # calculate the number of thread half turns
            # make the threaded section
            shell_thread = self.makeShellthread(d2, P, l2, True, 0)
            # FixMe: can be made better by cutting thread helix. 

            # combine the top & threaded section
            p_faces = p_shell.Faces
            p_faces.extend(shell_thread.Faces)
            p_shell = Part.Shell(p_faces)
        # make a hole for a hex key in the head
        hex_solid, hex_shell = self.makeAllen2(SW, l3 * 0.4, l3 + l1)
        top_face = top_face.cut(hex_solid)
        p_faces = p_shell.Faces
        p_faces.extend(top_face.Faces)
        hex_shell.translate(Base.Vector(0, 0, -1))
        p_faces.extend(hex_shell.Faces)
        p_shell = Part.Shell(p_faces)
        screw = Part.Solid(p_shell)
        # chamfer the hex recess
        cham_p1 = Base.Vector(0, 0, l3 + l1)
        cham_p2 = Base.Vector(SW / math.sqrt(3), 0, l3 + l1)
        cham_p3 = Base.Vector(0, 0, l3 + l1 - SW / math.sqrt(3))  # 45 degree chamfer
        cham_e1 = Part.makeLine(cham_p1, cham_p2)
        cham_e2 = Part.makeLine(cham_p2, cham_p3)
        cham_profile = Part.Wire([cham_e1, cham_e2])
        cham_shell = cham_profile.revolve(Base.Vector(0, 0, 0), Base.Vector(0, 0, 1), 360)
        cham_solid = Part.Solid(cham_shell)
        screw = screw.cut(cham_solid)
        return screw

    # make ISO 7380-1 Button head Screw
    # make ISO 7380-2 Button head Screw with collar
    # make DIN 967 cross recessed pan head Screw with collar
    # make ASMEB18.3.3A UNC Hex socket button head screws
    # make ASMEB18.3.3B UNC Hex socket button head screws with flange
    def makeButtonHeadScrew(self):
        SType = self.fastenerType
        l = self.fastenerLen
        dia = self.getDia(self.fastenerDiam, False)
        # todo: different radii for screws with thread to head or with shaft?
        sqrt2_ = 1.0 / math.sqrt(2.0)

        if SType == 'DIN967':
            P, b, c, da, dk, r, k, rf, x, cT, mH, mZ = self.dimTable

            rH = rf  # radius of button arc
            alpha = math.acos((rf - k + c) / rf)

            # Head Points
            Pnt0 = Base.Vector(0.0, 0.0, k)
            PntArc = Base.Vector(rf * math.sin(alpha / 2.0), 0.0,
                                 k - rf + rf * math.cos(alpha / 2.0))  # arc-point of button
            Pnt1 = Base.Vector(rf * math.sin(alpha), 0.0, c)  # end of button arc
            PntC0 = Base.Vector((dk) / 2.0, 0.0, c)  # collar points
            PntC2 = Base.Vector((dk) / 2.0, 0.0, 0.0)  # collar points
            Pnt4 = Base.Vector(dia / 2.0 + r, 0.0, 0.0)  # start of fillet between head and shank

            edge1 = Part.Arc(Pnt0, PntArc, Pnt1).toShape()
            edgeC0 = Part.makeLine(Pnt1, PntC0)
            edgeC1 = Part.makeLine(PntC0, PntC2)
            edge2 = Part.Wire([edgeC0, edgeC1])
            edge3 = Part.makeLine(PntC2, Pnt4)
            # Points for recessShell cutter
            PntH0 = Base.Vector(0.0, 0.0, 2.0 * k)
            PntH1 = Base.Vector(rf * math.sin(alpha), 0.0, 2.0 * k)
            recess, recessShell = self.makeCross_H3(cT, mH, k)

        else:
            if SType == 'ISO7380-1':
                P, b, a, da, dk, dk_mean, s_mean, t_min, r, k, e, w = self.dimTable

                # Bottom of recess
                e_cham = 2.0 * s_mean / math.sqrt(3.0) / 0.99
                # depth = s_mean / 3.0

                ak = -(4 * k ** 2 + e_cham ** 2 - dk ** 2) / (8 * k)  # helper value for button arc
                rH = math.sqrt((dk / 2.0) ** 2 + ak ** 2)  # radius of button arc
                alpha = (math.atan(2 * (k + ak) / e_cham) + math.atan((2 * ak) / dk)) / 2

                Pnt2 = Base.Vector(rH * math.cos(alpha), 0.0, -ak + rH * math.sin(alpha))  # arc-point of button
                Pnt3 = Base.Vector(dk / 2.0, 0.0, 0.0)  # end of fillet
                Pnt4 = Base.Vector(dia / 2.0 + r, 0.0, 0.0)  # start of fillet between head and shank
                edge3 = Part.makeLine(Pnt3, Pnt4)

            if SType == 'ASMEB18.3.3A':
                P, b, da, dk, s_mean, t_min, r, k = self.dimTable
                # Bottom of recess
                e_cham = 2.0 * s_mean / math.sqrt(3.0) / 0.99
                # depth = s_mean / 3.0
                ak = -(4 * k ** 2 + e_cham ** 2 - dk ** 2) / (8 * k)  # helper value for button arc
                rH = math.sqrt((dk / 2.0) ** 2 + ak ** 2)  # radius of button arc
                alpha = (math.atan(2 * (k + ak) / e_cham) + math.atan((2 * ak) / dk)) / 2
                Pnt2 = Base.Vector(rH * math.cos(alpha), 0.0, -ak + rH * math.sin(alpha))  # arc-point of button
                Pnt3 = Base.Vector(dk / 2.0, 0.0, 0.0)  # end of fillet
                Pnt4 = Base.Vector(dia / 2.0 + r, 0.0, 0.0)  # start of fillet between head and shank
                edge3 = Part.makeLine(Pnt3, Pnt4)

            if SType == 'ISO7380-2' or SType == 'ASMEB18.3.3B':
                if SType == 'ISO7380-2':
                    P, b, c, da, dk, dk_c, s_mean, t_min, r, k, e, w = self.dimTable
                if SType == 'ASMEB18.3.3B':
                    P, b, c, dk, dk_c, s_mean, t_min, r, k = self.dimTable

                # Bottom of recess
                e_cham = 2.0 * s_mean / math.sqrt(3.0) / 0.99
                # depth = s_mean / 3.0

                ak = -(4 * (k - c) ** 2 + e_cham ** 2 - dk ** 2) / (8 * (k - c))  # helper value for button arc
                rH = math.sqrt((dk / 2.0) ** 2 + ak ** 2)  # radius of button arc
                alpha = (math.atan(2 * (k - c + ak) / e_cham) + math.atan((2 * ak) / dk)) / 2

                Pnt2 = Base.Vector(rH * math.cos(alpha), 0.0, c - ak + rH * math.sin(alpha))  # arc-point of button
                Pnt3 = Base.Vector(dk / 2.0, 0.0, c)  # end of fillet
                Pnt4 = Base.Vector(dia / 2.0 + r, 0.0, 0.0)  # start of fillet between head and shank
                PntC0 = Base.Vector((dk_c - c) / 2.0, 0.0, c)  # collar points
                PntC1 = Base.Vector(dk_c / 2.0, 0.0, c / 2.0)  # collar points
                PntC2 = Base.Vector((dk_c - c) / 2.0, 0.0, 0.0)  # collar points

                edgeC0 = Part.makeLine(Pnt3, PntC0)
                edgeC1 = Part.Arc(PntC0, PntC1, PntC2).toShape()
                edge3 = Part.makeLine(PntC2, Pnt4)
                edge3 = Part.Wire([edgeC0, edgeC1, edge3])

            # Head Points
            Pnt0 = Base.Vector(e_cham / 4.0, 0.0, k - e_cham / 4.0)  # Center Point for chamfer
            Pnt1 = Base.Vector(e_cham / 2.0, 0.0, k)  # inner chamfer edge at head
            # Points for recessShell cutter
            PntH0 = Base.Vector(e_cham / 4.0, 0.0, 2.0 * k)
            PntH1 = Base.Vector(e_cham / 2.0, 0.0, 2.0 * k)

            edge1 = Part.makeLine(Pnt0, Pnt1)
            edge2 = Part.Arc(Pnt1, Pnt2, Pnt3).toShape()
            recess, recessShell = self.makeAllen2(s_mean, t_min, k)

        thread_start = l - b

        Pnt5 = Base.Vector(dia / 2.0 + r - r * sqrt2_, 0.0, -r + r * sqrt2_)  # arc-point of fillet
        Pnt6 = Base.Vector(dia / 2.0, 0.0, -r)  # end of fillet
        Pnt7 = Base.Vector(dia / 2.0, 0.0, -thread_start)  # start of thread

        edge4 = Part.Arc(Pnt4, Pnt5, Pnt6).toShape()
        edge5 = Part.makeLine(Pnt6, Pnt7)

        if SType == 'DIN967':
            # bolt points
            PntB1 = Base.Vector(dia / 2.0, 0.0, -l)
            PntB2 = Base.Vector(0.0, 0.0, -l)
            edgeB2 = Part.makeLine(PntB1, PntB2)
        else:
            # bolt points
            cham_b = P * math.sqrt(3.0) / 2.0 * 17.0 / 24.0

            PntB1 = Base.Vector(dia / 2.0, 0.0, -l + cham_b)
            PntB2 = Base.Vector(dia / 2.0 - cham_b, 0.0, -l)
            PntB3 = Base.Vector(0.0, 0.0, -l)

            edgeB2 = Part.makeLine(PntB1, PntB2)
            edgeB3 = Part.makeLine(PntB2, PntB3)
            edgeB2 = Part.Wire([edgeB2, edgeB3])

        if self.rThread:
            aWire = Part.Wire([edge2, edge3, edge4])
        else:
            if thread_start <= r:
                edgeB1 = Part.makeLine(Pnt6, PntB1)
                aWire = Part.Wire([edge2, edge3, edge4, edgeB1, edgeB2])
            else:
                edge5 = Part.makeLine(Pnt6, Pnt7)
                edgeB1 = Part.makeLine(Pnt7, PntB1)
                aWire = Part.Wire([edge2, edge3, edge4, edge5, edgeB1, edgeB2])

        # Part.show(aWire)
        headShell = aWire.revolve(Base.Vector(0.0, 0.0, 0.0), Base.Vector(0.0, 0.0, 1.0), 360)
        # Part.show(headShell)
        headFaces = headShell.Faces

        edgeH1 = Part.makeLine(Pnt1, PntH1)
        edgeH2 = Part.makeLine(PntH1, PntH0)
        edgeH3 = Part.makeLine(PntH0, Pnt0)
        hWire = Part.Wire([edge1, edgeH1, edgeH2, edgeH3])  # Cutter for recess-Shell
        hFace = Part.Face(hWire)
        hCut = hFace.revolve(Base.Vector(0.0, 0.0, 0.0), Base.Vector(0.0, 0.0, 1.0), 360)
        # Part.show(hWire)
        topFace = hCut.Faces[0]

        recessShell = recessShell.cut(hCut)
        topFace = topFace.cut(recess)
        # Part.show(topFace)
        # Part.show(recessShell)
        # Part.show(headShell)
        headFaces.append(topFace.Faces[0])
        headFaces.extend(recessShell.Faces)

        if self.rThread:
            if SType == 'DIN967':
                rthread = self.makeShellthread(dia, P, l - r, False, -r, b)
            else:
                rthread = self.makeShellthread(dia, P, l - r, True, -r, b)
            for threadFace in rthread.Faces:
                headFaces.append(threadFace)

            screwShell = Part.Shell(headFaces)
            screw = Part.Solid(screwShell)
        else:
            screwShell = Part.Shell(headFaces)
            screw = Part.Solid(screwShell)

        return screw

    # make ISO 4026 Hexagon socket set screws with flat point
    # make ISO 4027 Hexagon socket set screws with cone point
    # make ISO 4028 Hexagon socket set screws with dog point
    # make ISO 4029 Hexagon socket set screws with cup point
    # make ASMEB18.3.5A UNC Hexagon socket set screws with flat point
    # make ASMEB18.3.5B UNC Hexagon socket set screws with cone point
    # make ASMEB18.3.5C UNC Hexagon socket set screws with dog point
    # make ASMEB18.3.5D UNC Hexagon socket set screws with cup point
    def makeSetScrew(self):
        SType = self.fastenerType
        l = self.fastenerLen
        if SType == 'ISO4026' or SType == 'ISO4027' or SType == 'ISO4029':
            P, t, dp, dt, df, s = self.dimTable
        elif SType == 'ISO4028':
            P, t, dp, df, z, s = self.dimTable
        elif SType[:-1] == 'ASMEB18.3.5':
            P, t, dp, dt, df, s, z = self.dimTable
        d = self.getDia(self.fastenerDiam, False)
        d = d * 1.01
        # generate the profile of the set-screw
        if SType == 'ISO4026' or SType == 'ASMEB18.3.5A':
            p0 = Base.Vector(0, 0, 0)
            p1 = Base.Vector(df / 2, 0, 0)
            p2 = Base.Vector(d / 2, 0, -1 * ((d - df) / 2))
            p3 = Base.Vector(d / 2, 0, -1 * l + ((d - dp) / 2))
            p4 = Base.Vector(dp / 2, 0, -1 * l)
            p5 = Base.Vector(0, 0, -1 * l)
            e1 = Part.makeLine(p0, p1)
            e2 = Part.makeLine(p1, p2)
            e3 = Part.makeLine(p2, p3)
            e4 = Part.makeLine(p3, p4)
            e5 = Part.makeLine(p4, p5)
            p_profile = Part.Wire([e2, e3, e4, e5])
        elif SType == 'ISO4027' or SType == 'ASMEB18.3.5B':
            p0 = Base.Vector(0, 0, 0)
            p1 = Base.Vector(df / 2, 0, 0)
            p2 = Base.Vector(d / 2, 0, -1 * ((d - df) / 2))
            p3 = Base.Vector(d / 2, 0, -1 * l + ((d - dt) / 2))
            p4 = Base.Vector(dt / 2, 0, -1 * l)
            p5 = Base.Vector(0, 0, -1 * l)
            e1 = Part.makeLine(p0, p1)
            e2 = Part.makeLine(p1, p2)
            e3 = Part.makeLine(p2, p3)
            e4 = Part.makeLine(p3, p4)
            e5 = Part.makeLine(p4, p5)
            p_profile = Part.Wire([e2, e3, e4, e5])
        elif SType == 'ISO4028' or SType == 'ASMEB18.3.5C':
            # the shortest available dog-point set screws often have
            # shorter dog-points. There  is not much hard data accessible for this
            # approximate by halving the dog length for short screws
            if l < 1.5 * d:
                z = z * 0.5
            p0 = Base.Vector(0, 0, 0)
            p1 = Base.Vector(df / 2, 0, 0)
            p2 = Base.Vector(d / 2, 0, -1 * ((d - df) / 2))
            p3 = Base.Vector(d / 2, 0, -1 * l + ((d - dp) / 2 + z))
            p4 = Base.Vector(dp / 2, 0, -1 * l + z)
            p5 = Base.Vector(dp / 2, 0, -1 * l)
            p6 = Base.Vector(0, 0, -1 * l)
            e1 = Part.makeLine(p0, p1)
            e2 = Part.makeLine(p1, p2)
            e3 = Part.makeLine(p2, p3)
            e4 = Part.makeLine(p3, p4)
            e5 = Part.makeLine(p4, p5)
            e6 = Part.makeLine(p5, p6)
            p_profile = Part.Wire([e2, e3, e4, e5, e6])
        elif SType == 'ISO4029' or SType == 'ASMEB18.3.5D':
            p0 = Base.Vector(0, 0, 0)
            p1 = Base.Vector(df / 2, 0, 0)
            p2 = Base.Vector(d / 2, 0, -1 * ((d - df) / 2))
            p3 = Base.Vector(d / 2, 0, -1 * l + ((d - dp) / 2))
            p4 = Base.Vector(dp / 2, 0, -1 * l)
            p5 = Base.Vector(0, 0, -1 * l + math.sqrt(3) / 6 * dp)
            e1 = Part.makeLine(p0, p1)
            e2 = Part.makeLine(p1, p2)
            e3 = Part.makeLine(p2, p3)
            e4 = Part.makeLine(p3, p4)
            e5 = Part.makeLine(p4, p5)
            p_profile = Part.Wire([e2, e3, e4, e5])

        p_shell = p_profile.revolve(Base.Vector(0, 0, 0), Base.Vector(0, 0, 1), 360)
        # generate a top face with a hex-key recess
        top_face_profile = Part.Wire([e1])
        top_face = top_face_profile.revolve(Base.Vector(0, 0, 0), Base.Vector(0, 0, 1), 360)
        hex_solid, hex_shell = self.makeAllen2(s, t - 1, 0)
        top_face = top_face.cut(hex_solid)
        p_faces = p_shell.Faces
        p_faces.extend(top_face.Faces)
        hex_shell.translate(Base.Vector(0, 0, -1))
        p_faces.extend(hex_shell.Faces)
        p_shell = Part.Shell(p_faces)
        screw = Part.Solid(p_shell)
        # chamfer the hex recess
        cham_p1 = Base.Vector(0, 0, 0)
        cham_p2 = Base.Vector(s / math.sqrt(3), 0, 0)
        cham_p3 = Base.Vector(0, 0, 0 - s / math.sqrt(3))  # 45 degree chamfer
        cham_e1 = Part.makeLine(cham_p1, cham_p2)
        cham_e2 = Part.makeLine(cham_p2, cham_p3)
        cham_profile = Part.Wire([cham_e1, cham_e2])
        cham_shell = cham_profile.revolve(Base.Vector(0, 0, 0), Base.Vector(0, 0, 1), 360)
        cham_solid = Part.Solid(cham_shell)
        screw = screw.cut(cham_solid)
        # produce a modelled thread if necessary
        if self.rThread:
            # make the threaded section
            d = d / 1.01
            shell_thread = self.makeShellthread(d, P, l, False, 0)
            # FixMe: can be made simpler by cutting tyhread helix. 
            thr_p1 = Base.Vector(0, 0, 0)
            thr_p2 = Base.Vector(d / 2, 0, 0)
            thr_e1 = Part.makeLine(thr_p1, thr_p2)
            thr_cap_profile = Part.Wire([thr_e1])
            thr_cap = thr_cap_profile.revolve(Base.Vector(0, 0, 0), Base.Vector(0, 0, 1), 360)
            thr_faces = shell_thread.Faces
            thr_faces.extend(thr_cap.Faces)
            thread_shell = Part.Shell(thr_faces)
            thread_solid = Part.Solid(thread_shell)
            # Part.show(thread_solid)
            screw = screw.common(thread_solid)
        return screw

    # ASMEB18.5.2 UNC Round head square neck bolts
    def makeCarriageBolt(self):
        SType = self.fastenerType
        l = self.fastenerLen
        d = self.getDia(self.fastenerDiam, False)
        if SType == 'ASMEB18.5.2':
            tpi, _, A, H, O, P, _, _ = self.dimTable
            A, H, O, P = (25.4 * x for x in (A, H, O, P))
            pitch = 25.4 / tpi
            if l <= 152.4:
                L_t = d * 2 + 6.35
            else:
                L_t = d * 2 + 12.7
        # lay out points for head generation
        p1 = Base.Vector(0, 0, H)
        head_r = A / math.sqrt(2)
        p2 = Base.Vector(head_r * math.sin(math.pi / 8), 0, H - head_r + head_r * math.cos(math.pi / 8))
        p3 = Base.Vector(A / 2, 0, 0)
        p4 = Base.Vector(math.sqrt(2) / 2 * O, 0, 0)
        p5 = Base.Vector(math.sqrt(2) / 2 * O, 0, -1 * P + (math.sqrt(2) / 2 * O - d / 2))
        p6 = Base.Vector(d / 2, 0, -1 * P)
        # arcs must be converted to shapes in order to be merged with other line segments
        a1 = Part.Arc(p1, p2, p3).toShape()
        l2 = Part.makeLine(p3, p4)
        l3 = Part.makeLine(p4, p5)
        l4 = Part.makeLine(p5, p6)
        wire1 = Part.Wire([a1, l2, l3, l4])
        head_shell = wire1.revolve(Base.Vector(0, 0, 0), Base.Vector(0, 0, 1), 360)
        flat_len = l - P
        if not self.rThread:
            # simplified threaded section
            p7 = Base.Vector(d / 2, 0, -l + d / 10)
            p7a = Base.Vector(d / 2, 0, -l + L_t)
            p8 = Base.Vector(d / 2 - d / 10, 0, -l)
            p9 = Base.Vector(0, 0, -l)
            l6 = Part.makeLine(p7, p8)
            l7 = Part.makeLine(p8, p9)
            if (flat_len <= L_t):
                l5 = Part.makeLine(p6, p7)
                thread_profile_wire = Part.Wire([l5, l6, l7])
            else:
                l5a = Part.makeLine(p6, p7a)
                l5b = Part.makeLine(p7a, p7)
                thread_profile_wire = Part.Wire([l5a, l5b, l6, l7])
            shell_thread = thread_profile_wire.revolve(Base.Vector(0, 0, 0), Base.Vector(0, 0, 1), 360)
        else:
            # modeled threaded section
            shell_thread = self.makeShellthread(d, pitch, flat_len, False, -P, L_t)
        p_shell = Part.Shell(head_shell.Faces + shell_thread.Faces)
        p_solid = Part.Solid(p_shell)
        # cut 4 flats under the head
        d_mod = d + 0.0002
        outerBox = Part.makeBox(A * 4, A * 4, P + 0.0001, Base.Vector(-A * 2, -A * 2, -P + 0.0001))
        innerBox = Part.makeBox(d_mod, d_mod, P * 3, Base.Vector(-d_mod / 2, -d_mod / 2, -P * 2))
        tool = outerBox.cut(innerBox)
        p_solid = p_solid.cut(tool)
        #for i in range(4):
        #    p_solid = p_solid.cut(
        #        Part.makeBox(d, A, P, Base.Vector(d / 2, -1 * A / 2, -1 * P)).rotate(Base.Vector(0, 0, 0),
        #                                                                             Base.Vector(0, 0, 1), i * 90))
        # removeSplitter is equivalent to the 'Refine' option for FreeCAD PartDesign objects
        # return p_solid.removeSplitter()
        return p_solid # not refining so thread location will be visible when not using real thread

    def makeHextool(self, s_hex, k_hex, cir_hex):
        # makes a cylinder with an inner hex hole, used as cutting tool
        # create hexagon face
        mhex = Base.Matrix()
        mhex.rotateZ(math.radians(60.0))
        polygon = []
        vhex = Base.Vector(s_hex / math.sqrt(3.0), 0.0, -k_hex * 0.1)
        for i in range(6):
            polygon.append(vhex)
            vhex = mhex.multiply(vhex)
        polygon.append(vhex)
        hexagon = Part.makePolygon(polygon)
        hexagon = Part.Face(hexagon)

        # create circle face
        circ = Part.makeCircle(cir_hex / 2.0, Base.Vector(0.0, 0.0, -k_hex * 0.1))
        circ = Part.Face(Part.Wire(circ))

        # Create the face with the circle as outline and the hexagon as hole
        face = circ.cut(hexagon)

        # Extrude in z to create the final cutting tool
        exHex = face.extrude(Base.Vector(0.0, 0.0, k_hex * 1.2))
        # Part.show(exHex)
        return exHex

    def makeShellthread(self, dia, P, blen, withcham, ztop, tlen = -1):
        """
    Construct a 60 degree screw thread with diameter dia,
    pitch P. 
    blen is the length of the shell body.
    tlen is the length of the threaded part (-1 = same as body length).
    if withcham == True, the end of the thread is nicely chamfered.
    The thread is constructed z-up, as a shell, with the top circular
    face removed. The top of the shell is centered @ (0, 0, ztop)
    """
        # make a cylindrical solid, then cut the thread profile from it
        H = math.sqrt(3) / 2 * P
        # move the very bottom of the base up a tiny amount
        # prevents some too-small edges from being created
        correction = 1e-5
        if tlen < 0:
            tlen = blen
        base_pnts = list(map(lambda x: Base.Vector(x),
                             [
                                 [dia / 2, 0, 0],
                                 [dia / 2, 0, -blen + P / 2],
                                 [dia / 2 - P / 2, 0, -blen + correction],
                                 [0, 0, -blen + correction],
                                 [0, 0, 0],
                                 [dia / 2, 0, -blen + correction]
                             ]))
        if withcham:
            base_profile = Part.Wire([
                Part.makeLine(base_pnts[0], base_pnts[1]),
                Part.makeLine(base_pnts[1], base_pnts[2]),
                Part.makeLine(base_pnts[2], base_pnts[3]),
                Part.makeLine(base_pnts[3], base_pnts[4]),
                Part.makeLine(base_pnts[4], base_pnts[0]),
            ])
        else:
            base_profile = Part.Wire([
                Part.makeLine(base_pnts[0], base_pnts[5]),
                Part.makeLine(base_pnts[5], base_pnts[3]),
                Part.makeLine(base_pnts[3], base_pnts[4]),
                Part.makeLine(base_pnts[4], base_pnts[0]),
            ])
        base_shell = base_profile.revolve(
            Base.Vector(0, 0, 0),
            Base.Vector(0, 0, 1),
            360)
        base_body = Part.makeSolid(base_shell)
        trotations = blen // P + 1

        # create a sketch profile of the thread
        # ref: https://en.wikipedia.org/wiki/ISO_metric_screw_thread
        fillet_r = P * math.sqrt(3) / 12
        helix_height = trotations * P
        pnts = list(map(lambda x: Base.Vector(x),
                        [
                            [dia / 2 + math.sqrt(3) * 3 / 80 * P, 0, -0.475 * P],
                            [dia / 2 - 0.625 * H, 0, -1 * P / 8],
                            [dia / 2 - 0.625 * H - 0.5 * fillet_r, 0, 0],
                            [dia / 2 - 0.625 * H, 0, P / 8],
                            [dia / 2 + math.sqrt(3) * 3 / 80 * P, 0, 0.475 * P]
                        ]))
        thread_profile_wire = Part.Wire([
            Part.makeLine(pnts[0], pnts[1]),
            Part.Arc(pnts[3], pnts[2], pnts[1]).toShape(),
            Part.makeLine(pnts[3], pnts[4]),
            Part.makeLine(pnts[4], pnts[0])])
        thread_profile_wire.translate(Base.Vector(0, 0, -1 * helix_height))
        # make the helical paths to sweep along
        # NOTE: makeLongHelix creates slightly conical
        # helices unless the 4th parameter is set to 0!
        main_helix = Part.makeLongHelix(P, helix_height, dia / 2, 0, self.leftHanded)
        lead_out_helix = Part.makeLongHelix(P, P / 2, dia / 2 + 0.5 * (5 / 8 * H + 0.5 * fillet_r), 0, self.leftHanded)
        main_helix.rotate(Base.Vector(0, 0, 0), Base.Vector(1, 0, 0), 180)
        lead_out_helix.translate(Base.Vector(0.5 * (-1 * (5 / 8 * H + 0.5 * fillet_r)), 0, 0))
        sweep_path = Part.Wire([main_helix, lead_out_helix])
        # use Part.BrepOffsetAPI to sweep the thread profile
        # ref: https://forum.freecadweb.org/viewtopic.php?t=21636#p168339
        sweep = Part.BRepOffsetAPI.MakePipeShell(sweep_path)
        sweep.setFrenetMode(True)
        sweep.setTransitionMode(1)  # right corner transition
        sweep.add(thread_profile_wire)
        if sweep.isReady():
            sweep.build()
        else:
            # geometry couldn't be generated in a useable form
            raise RuntimeError("Failed to create shell thread: could not sweep thread")
        sweep.makeSolid()
        swept_solid = sweep.shape()
        # translate swept path slightly for backwards compatibility
        toffset = blen - tlen + P / 2
        minoffset = 5 * P / 8
        if (toffset < minoffset):
            toffset = minoffset

        swept_solid.translate(Base.Vector(0, 0, -toffset))
        # perform the actual boolean operations
        base_body.rotate(Base.Vector(0, 0, 0), Base.Vector(0, 0, 1), 90)
        threaded_solid = base_body.cut(swept_solid)
        if toffset < 0:
            # one more component: a kind of 'cap' to improve behaviour with
            # large offset values
            cap_bottom_point = Base.Vector(0, 0, - dia / 2)
            cap_profile = Part.Wire([
                Part.makeLine(base_pnts[4], base_pnts[0]),
                Part.makeLine(base_pnts[0], cap_bottom_point),
                Part.makeLine(cap_bottom_point, base_pnts[4])])
            cap_shell = cap_profile.revolve(
                Base.Vector(0, 0, 0),
                Base.Vector(0, 0, 1),
                360)
            cap_solid = Part.makeSolid(cap_shell)
            # threaded_solid = threaded_solid.fuse(cap_solid)
            threaded_solid.removeSplitter
        # remove top face(s) and convert to a shell
        result = Part.Shell([x for x in threaded_solid.Faces \
                             if not abs(x.CenterOfMass[2]) < 1e-7])
        result.translate(Base.Vector(0, 0, ztop))
        return result

    # if da is not None: make Shell for a nut else: make a screw tap
    def makeInnerThread_2(self, d, P, rotations, da, l):
        d = float(d)
        bot_off = 0.0  # nominal length

        if d > 52.0:
            fuzzyValue = 5e-5
        else:
            fuzzyValue = 0.0

        H = P * math.cos(math.radians(30))  # Thread depth H
        r = d / 2.0

        helix = Part.makeLongHelix(P, P, d * self.Tuner / 1000.0, 0, self.leftHanded)  # make just one turn, length is identical to pitch
        helix.translate(FreeCAD.Vector(0.0, 0.0, -P * 9.0 / 16.0))

        extra_rad = P

        # points for inner thread profile
        ps0 = (r, 0.0, 0.0)
        ps1 = (r - H * 5.0 / 8.0, 0.0, -P * 5.0 / 16.0)
        ps2 = (r - H * 5.0 / 8.0, 0.0, -P * 9.0 / 16.0)
        ps3 = (r, 0.0, -P * 14.0 / 16.0)
        ps4 = (r + H * 1 / 24.0, 0.0, -P * 31.0 / 32.0)  # Center of Arc
        ps5 = (r, 0.0, -P)

        ps6 = (r + extra_rad, 0.0, -P)
        ps7 = (r + extra_rad, 0.0, 0.0)

        edge0 = Part.makeLine(ps0, ps1)
        edge1 = Part.makeLine(ps1, ps2)
        edge2 = Part.makeLine(ps2, ps3)
        edge3 = Part.Arc(FreeCAD.Vector(ps3), FreeCAD.Vector(ps4), FreeCAD.Vector(ps5)).toShape()
        edge4 = Part.makeLine(ps5, ps6)
        edge5 = Part.makeLine(ps6, ps7)
        edge6 = Part.makeLine(ps7, ps0)

        W0 = Part.Wire([edge0, edge1, edge2, edge3, edge4, edge5, edge6])
        # Part.show(W0, 'W0')

        makeSolid = True
        isFrenet = True
        pipe0 = Part.Wire(helix).makePipeShell([W0], makeSolid, isFrenet)
        # pipe1 = pipe0.copy()

        TheFaces = []
        TheFaces.append(pipe0.Faces[0])
        TheFaces.append(pipe0.Faces[1])
        TheFaces.append(pipe0.Faces[2])
        TheFaces.append(pipe0.Faces[3])
        # topHeliFaces = [pipe0.Faces[6], pipe0.Faces[8]]
        # innerHeliFaces = [pipe0.Faces[5]]
        # bottomFaces = [pipe0.Faces[4], pipe0.Faces[7]]

        TheShell = Part.Shell(TheFaces)
        # singleThreadShell = TheShell.copy()
        # print "Shellpoints: ", len(TheShell.Vertexes)
        if da is None:
            commonbox = Part.makeBox(d + 4.0 * P, d + 4.0 * P, 3.0 * P)
            commonbox.translate(FreeCAD.Vector(-(d + 4.0 * P) / 2.0, -(d + 4.0 * P) / 2.0, -(3.0) * P))
            topShell = TheShell.common(commonbox)
            top_edges = []
            top_z = -1.0e-5

            for kante in topShell.Edges:
                if kante.Vertexes[0].Point.z >= top_z and kante.Vertexes[1].Point.z >= top_z:
                    top_edges.append(kante)
                    # Part.show(kante)
            top_wire = Part.Wire(Part.__sortEdges__(top_edges))
            top_face = Part.Face(top_wire)

            TheFaces = [top_face.Faces[0]]
            TheFaces.extend(topShell.Faces)

            for i in range(rotations - 2):
                TheShell.translate(FreeCAD.Vector(0.0, 0.0, - P))
                for flaeche in TheShell.Faces:
                    TheFaces.append(flaeche)

            # FreeCAD.Console.PrintMessage("Base-Shell: " + str(i) + "\n")
            # Make separate faces for the tip of the screw
            botFaces = []
            for i in range(rotations - 2, rotations, 1):
                TheShell.translate(FreeCAD.Vector(0.0, 0.0, - P))

                for flaeche in TheShell.Faces:
                    botFaces.append(flaeche)
            # FreeCAD.Console.PrintMessage("Bottom-Shell: " + str(i) + "\n")
            # FreeCAD.Console.PrintMessage("without chamfer: " + str(i) + "\n")

            commonbox = Part.makeBox(d + 4.0 * P, d + 4.0 * P, 3.0 * P)
            commonbox.translate(FreeCAD.Vector(-(d + 4.0 * P) / 2.0, -(d + 4.0 * P) / 2.0, -(rotations) * P + bot_off))
            # commonbox.translate(FreeCAD.Vector(-(d+4.0*P)/2.0, -(d+4.0*P)/2.0,-(rotations+3)*P+bot_off))
            # Part.show(commonbox)

            BotShell = Part.Shell(botFaces)
            # Part.show(BotShell)

            BotShell = BotShell.common(commonbox)
            # BotShell = BotShell.cut(commonbox)
            bot_edges = []
            bot_z = 1.0e-5 - (rotations) * P + bot_off

            for kante in BotShell.Edges:
                if kante.Vertexes[0].Point.z <= bot_z and kante.Vertexes[1].Point.z <= bot_z:
                    bot_edges.append(kante)
                    # Part.show(kante)
            bot_wire = Part.Wire(Part.__sortEdges__(bot_edges))

            bot_face = Part.Face(bot_wire)
            bot_face.reverse()

            for flaeche in BotShell.Faces:
                TheFaces.append(flaeche)
            # if da is not None:
            # for flaeche in cham_Shell.Faces:
            # TheFaces.append(flaeche)
            # else:
            TheFaces.append(bot_face)
            TheShell = Part.Shell(TheFaces)
            TheSolid = Part.Solid(TheShell)
            # print self.Tuner, " ", TheShell.ShapeType, " ", TheShell.isValid(), " rotations: ", rotations, " Shellpoints: ", len(TheShell.Vertexes)
            return TheSolid

        else:
            # Try to make the inner thread shell of a nut
            cham_i = 2 * H * math.tan(math.radians(15.0))  # inner chamfer

            # points for chamfer: cut-Method
            pch0 = (da / 2.0 - 2 * H, 0.0, +cham_i)  # bottom chamfer
            pch1 = (da / 2.0, 0.0, 0.0)  #
            pch2 = (da / 2.0, 0.0, - 2.1 * P)
            pch3 = (da / 2.0 - 2 * H, 0.0, - 2.1 * P)  #

            # pch2 =  (da/2.0, 0.0, l)
            # pch3 =  (da/2.0 - 2*H, 0.0, l - cham_i)

            edgech0 = Part.makeLine(pch0, pch1)
            edgech1 = Part.makeLine(pch1, pch2)
            edgech2 = Part.makeLine(pch2, pch3)
            edgech3 = Part.makeLine(pch3, pch0)

            Wch_wire = Part.Wire([edgech0, edgech1, edgech2, edgech3])
            bottom_Face = Part.Face(Wch_wire)
            # bottom_Solid = bottom_Face.revolve(Base.Vector(0.0,0.0,-(rotations-1)*P),Base.Vector(0.0,0.0,1.0),360)
            bottom_Solid = bottom_Face.revolve(Base.Vector(0.0, 0.0, 0.0), Base.Vector(0.0, 0.0, 1.0), 360)
            # Part.show(cham_Solid, 'cham_Solid')
            # Part.show(Wch_wire)
            bottomChamferFace = bottom_Solid.Faces[0]

            # points for chamfer: cut-Method
            pch0t = (da / 2.0 - 2 * H, 0.0, l - cham_i)  # top chamfer
            pch1t = (da / 2.0, 0.0, l)  #
            pch2t = (da / 2.0, 0.0, l + 4 * P)
            pch3t = (da / 2.0 - 2 * H, 0.0, l + 4 * P)  #

            edgech0t = Part.makeLine(pch0t, pch1t)
            edgech1t = Part.makeLine(pch1t, pch2t)
            edgech2t = Part.makeLine(pch2t, pch3t)
            edgech3t = Part.makeLine(pch3t, pch0t)

            Wcht_wire = Part.Wire([edgech0t, edgech1t, edgech2t, edgech3t])
            top_Face = Part.Face(Wcht_wire)
            top_Solid = top_Face.revolve(Base.Vector(0.0, 0.0, (rotations - 1) * P), Base.Vector(0.0, 0.0, 1.0), 360)
            # Part.show(top_Solid, 'top_Solid')
            # Part.show(Wch_wire)
            topChamferFace = top_Solid.Faces[0]

            threeThreadFaces = TheFaces.copy()
            for k in range(1):
                TheShell.translate(FreeCAD.Vector(0.0, 0.0, P))
                for threadFace in TheShell.Faces:
                    threeThreadFaces.append(threadFace)

            chamferShell = Part.Shell(threeThreadFaces)
            # Part.show(chamferShell, 'chamferShell')
            # Part.show(bottomChamferFace, 'bottomChamferFace')

            bottomPart = chamferShell.cut(bottom_Solid)
            # Part.show(bottomPart, 'bottomPart')
            bottomFuse, bottomMap = bottomChamferFace.generalFuse([chamferShell], fuzzyValue)
            # print ('bottomMap: ', bottomMap)
            # chamFuse, chamMap = chamferShell.generalFuse([bottomChamferFace])
            # print ('chamMap: ', chamMap)
            # Part.show(bottomFuse, 'bottomFuse')
            # Part.show(bottomMap[0][0], 'bMap0')
            # Part.show(bottomMap[0][1], 'bMap1')
            innerThreadFaces = [bottomMap[0][1]]
            for face in bottomPart.Faces:
                innerThreadFaces.append(face)
            # bottomShell = Part.Shell(innerThreadFaces)
            # Part.show(bottomShell)
            bottomFaces = []
            # TheShell.translate(FreeCAD.Vector(0.0, 0.0, P))
            for k in range(1, rotations - 2):
                TheShell.translate(FreeCAD.Vector(0.0, 0.0, P))
                for threadFace in TheShell.Faces:
                    innerThreadFaces.append(threadFace)
            # testShell = Part.Shell(innerThreadFaces)
            # Part.show(testShell, 'testShell')

            chamferShell.translate(FreeCAD.Vector(0.0, 0.0, (rotations - 1) * P))
            # Part.show(chamferShell, 'chamferShell')
            # Part.show(topChamferFace, 'topChamferFace')
            topPart = chamferShell.cut(top_Solid)
            # Part.show(topPart, 'topPart')
            for face in topPart.Faces:
                innerThreadFaces.append(face)

            topFuse, topMap = topChamferFace.generalFuse([chamferShell], fuzzyValue)
            # print ('topMap: ', topMap)
            # Part.show(topMap[0][0], 'tMap0')
            # Part.show(topMap[0][1], 'tMap1')
            # Part.show(topFuse, 'topFuse')
            innerThreadFaces.append(topMap[0][1])

            # topFaces = []
            # for face in topPart.Faces:
            #  topFaces.append(face)
            # topFaces.append(topMap[0][1])
            # testTopShell = Part.Shell(topFaces)
            # Part.show(testTopShell, 'testTopShell')

            threadShell = Part.Shell(innerThreadFaces)
            # Part.show(threadShell, 'threadShell')

            return threadShell

    # make the ISO 4032 Hex-nut
    # make the ISO 4033 Hex-nut
    def makeHexNut(self):
        SType = self.fastenerType
        dia = self.getDia(self.fastenerDiam, True)
        #         P, tunIn, tunEx
        # Ptun, self.tuning, tunEx = tuningTable[ThreadType]
        if SType[:3] == 'ISO':
            # P, c, damax,  dw,    e,     m,   mw,   s_nom
            P, c, da, dw, e, m, mw, s = self.dimTable
        elif SType == 'ASMEB18.2.2.1A':
            P, da, e, m, s = self.dimTable
        elif SType == 'ASMEB18.2.2.4A':
            P, da, e, m_a, m_b, s = self.dimTable
            m = m_a
        elif SType == 'ASMEB18.2.2.4B':
            P, da, e, m_a, m_b, s = self.dimTable
            m = m_b

        residue, turns = math.modf(m / P)
        # halfturns = 2*int(turns)

        if residue > 0.0:
            turns += 1.0
        if SType == 'ISO4033' and self.fastenerDiam == '(M14)':
            turns -= 1.0
        if SType == 'ISO4035' and self.fastenerDiam == 'M56':
            turns -= 1.0

        sqrt2_ = 1.0 / math.sqrt(2.0)
        cham = (e - s) * math.sin(math.radians(15))  # needed for chamfer at nut top
        H = P * math.cos(math.radians(30))  # Gewindetiefe H
        cham_i_delta = da / 2.0 - (dia / 2.0 - H * 5.0 / 8.0)
        cham_i = cham_i_delta * math.tan(math.radians(15.0))

        if self.rThread:
            Pnt0 = Base.Vector(da / 2.0 - 2.0 * cham_i_delta, 0.0, m - 2.0 * cham_i)
            Pnt7 = Base.Vector(da / 2.0 - 2.0 * cham_i_delta, 0.0, 0.0 + 2.0 * cham_i)
        else:
            Pnt0 = Base.Vector(dia / 2.0 - H * 5.0 / 8.0, 0.0, m - cham_i)
            Pnt7 = Base.Vector(dia / 2.0 - H * 5.0 / 8.0, 0.0, 0.0 + cham_i)

        Pnt1 = Base.Vector(da / 2.0, 0.0, m)
        Pnt2 = Base.Vector(s / 2.0, 0.0, m)
        Pnt3 = Base.Vector(s / math.sqrt(3.0), 0.0, m - cham)
        Pnt4 = Base.Vector(s / math.sqrt(3.0), 0.0, cham)
        Pnt5 = Base.Vector(s / 2.0, 0.0, 0.0)
        Pnt6 = Base.Vector(da / 2.0, 0.0, 0.0)

        edge0 = Part.makeLine(Pnt0, Pnt1)
        edge1 = Part.makeLine(Pnt1, Pnt2)
        edge2 = Part.makeLine(Pnt2, Pnt3)
        edge3 = Part.makeLine(Pnt3, Pnt4)
        edge4 = Part.makeLine(Pnt4, Pnt5)
        edge5 = Part.makeLine(Pnt5, Pnt6)
        edge6 = Part.makeLine(Pnt6, Pnt7)
        edge7 = Part.makeLine(Pnt7, Pnt0)

        # create cutting tool for hexagon head
        # Parameters s, k, outer circle diameter =  e/2.0+10.0
        extrude = self.makeHextool(s, m, s * 2.0)

        aWire = Part.Wire([edge0, edge1, edge2, edge3, edge4, edge5, edge6, edge7])
        # Part.show(aWire)
        aFace = Part.Face(aWire)
        head = aFace.revolve(Base.Vector(0.0, 0.0, 0.0), Base.Vector(0.0, 0.0, 1.0), 360.0)
        # Part.show(head)

        # Part.show(extrude)
        nut = head.cut(extrude)
        # Part.show(nut, 'withoutTread')

        if self.rThread:
            # if (dia < 1.6)or (dia > 52.0):
            if (dia < 1.6) or (dia > 64.0):
                # if (dia < 3.0):
                threadCutter = self.makeInnerThread_2(dia, P, int(turns + 1), None, m)
                threadCutter.translate(Base.Vector(0.0, 0.0, turns * P + 0.5 * P))
                # Part.show(threadCutter, 'threadCutter')
                nut = nut.cut(threadCutter)
                # chamFace = nut.Faces[0].cut(threadCutter)
                # Part.show(chamFace, 'chamFace0_')
            else:
                nutFaces = [nut.Faces[2]]
                for i in range(4, 25):
                    nutFaces.append(nut.Faces[i])
                # Part.show(Part.Shell(nutFaces), 'OuterNutshell')

                threadShell = self.makeInnerThread_2(dia, P, int(turns), da, m)
                # threadShell.translate(Base.Vector(0.0, 0.0,turns*P))
                # Part.show(threadShell, 'threadShell')
                nutFaces.extend(threadShell.Faces)

                nutShell = Part.Shell(nutFaces)
                nut = Part.Solid(nutShell)
                # Part.show(nutShell)
        return nut

    # EN 1661 Hexagon nuts with flange
    # chamfer at top of hexagon is wrong = more than 30°
    def makeHexNutWFlunge(self):
        dia = self.getDia(self.fastenerDiam, True)
        P, da, c, dc, dw, e, m, mw, r1, s = self.dimTable

        residue, turns = math.modf(m / P)
        # halfturns = 2*int(turns)

        if residue > 0.0:
            turns += 1.0

        # FreeCAD.Console.PrintMessage("the nut with isoEN1661: " + str(c) + "\n")
        cham = s * (2.0 / math.sqrt(3.0) - 1.0) * math.sin(math.radians(25))  # needed for chamfer at head top

        sqrt2_ = 1.0 / math.sqrt(2.0)

        # Flange is made with a radius of c
        beta = math.radians(25.0)
        tan_beta = math.tan(beta)

        # Calculation of Arc points of flange edge using dc and c
        arc1_x = dc / 2.0 - c / 2.0 + (c / 2.0) * math.sin(beta)
        arc1_z = c / 2.0 + (c / 2.0) * math.cos(beta)

        hF = arc1_z + (arc1_x - s / 2.0) * tan_beta  # height of flange at center

        # kmean = arc1_z + (arc1_x - s/math.sqrt(3.0)) * tan_beta + mw * 1.1 + cham
        # kmean = k * 0.95

        # Hex-Head Points
        # FreeCAD.Console.PrintMessage("the nut with kmean: " + str(m) + "\n")
        PntH0 = Base.Vector(da / 2.0, 0.0, m)
        PntH1 = Base.Vector(s / 2.0, 0.0, m)
        edgeH1 = Part.makeLine(PntH0, PntH1)

        hWire = Part.Wire([edgeH1])
        topShell = hWire.revolve(Base.Vector(0.0, 0.0, 0.0), Base.Vector(0.0, 0.0, 1.0), 360)
        # Part.show(hWire)
        # Part.show(topShell)

        # create a cutter ring to generate the chamfer at the top of the hex
        chamHori = s / math.sqrt(3.0) - s / 2.0
        PntC1 = Base.Vector(s / 2.0 - chamHori, 0.0, m + m)
        PntC2 = Base.Vector(s / math.sqrt(3.0) + chamHori, 0.0, m + m)
        PntC3 = Base.Vector(s / 2.0 - chamHori, 0.0, m + cham)
        PntC4 = Base.Vector(s / math.sqrt(3.0) + chamHori, 0.0, m - cham - cham)  # s/math.sqrt(3.0)
        edgeC1 = Part.makeLine(PntC3, PntC1)
        edgeC2 = Part.makeLine(PntC1, PntC2)
        edgeC3 = Part.makeLine(PntC2, PntC4)
        edgeC4 = Part.makeLine(PntC4, PntC3)
        cWire = Part.Wire([edgeC4, edgeC1, edgeC2, edgeC3])
        cFace = Part.Face(cWire)
        chamCut = cFace.revolve(Base.Vector(0.0, 0.0, 0.0), Base.Vector(0.0, 0.0, 1.0), 360)
        # Part.show(cWire)
        # Part.show(chamCut)

        # create hexagon
        mhex = Base.Matrix()
        mhex.rotateZ(math.radians(60.0))
        polygon = []
        vhex = Base.Vector(s / math.sqrt(3.0), 0.0, m)
        for i in range(6):
            polygon.append(vhex)
            vhex = mhex.multiply(vhex)
        polygon.append(vhex)
        hexagon = Part.makePolygon(polygon)
        hexFace = Part.Face(hexagon)
        solidHex = hexFace.extrude(Base.Vector(0.0, 0.0, c - m))
        # Part.show(solidHex)
        hexCham = solidHex.cut(chamCut)
        # Part.show(hexCham)

        topFaces = topShell.Faces

        topFaces.append(hexCham.Faces[1])
        topFaces.append(hexCham.Faces[2])
        topFaces.append(hexCham.Faces[8])
        topFaces.append(hexCham.Faces[13])
        topFaces.append(hexCham.Faces[14])
        topFaces.append(hexCham.Faces[12])
        topFaces.append(hexCham.Faces[6])

        hexFaces = [hexCham.Faces[5], hexCham.Faces[11], hexCham.Faces[10]]
        hexFaces.extend([hexCham.Faces[9], hexCham.Faces[3], hexCham.Faces[0]])
        hexShell = Part.Shell(hexFaces)

        H = P * math.cos(math.radians(30))  # Thread depth H
        cham_i_delta = da / 2.0 - (dia / 2.0 - H * 5.0 / 8.0)
        cham_i = cham_i_delta * math.tan(math.radians(15.0))

        # Center of flange:
        Pnt0 = Base.Vector(0.0, 0.0, hF)
        Pnt1 = Base.Vector(s / 2.0, 0.0, hF)

        # arc edge of flange:
        Pnt2 = Base.Vector(arc1_x, 0.0, arc1_z)
        Pnt3 = Base.Vector(dc / 2.0, 0.0, c / 2.0)
        Pnt4 = Base.Vector((dc - c) / 2.0, 0.0, 0.0)
        Pnt5 = Base.Vector(da / 2.0, 0.0, 0.0)  # start of fillet between flat and thread

        edge1 = Part.makeLine(Pnt0, Pnt1)
        edge2 = Part.makeLine(Pnt1, Pnt2)
        edge3 = Part.Arc(Pnt2, Pnt3, Pnt4).toShape()
        edge4 = Part.makeLine(Pnt4, Pnt5)

        # make a cutter for the hexShell
        PntHC1 = Base.Vector(0.0, 0.0, arc1_z)
        PntHC2 = Base.Vector(0.0, 0.0, 0.0)

        edgeHC1 = Part.makeLine(Pnt2, PntHC1)
        edgeHC2 = Part.makeLine(PntHC1, PntHC2)
        edgeHC3 = Part.makeLine(PntHC2, Pnt0)

        HCWire = Part.Wire([edge2, edgeHC1, edgeHC2, edgeHC3, edge1])
        HCFace = Part.Face(HCWire)
        hex2Cut = HCFace.revolve(Base.Vector(0.0, 0.0, 0.0), Base.Vector(0.0, 0.0, 1.0), 360)

        hexShell = hexShell.cut(hex2Cut)
        # Part.show(hexShell)

        topFaces.extend(hexShell.Faces)

        if self.rThread and (dia > 4.0):
            aWire = Part.Wire([edge2, edge3, edge4])
            boltIndex = 3

        else:
            if self.rThread:
                Pnt7 = Base.Vector(dia / 2.1 - H * 5.0 / 8.0, 0.0, m - cham_i)
                Pnt6 = Base.Vector(dia / 2.1 - H * 5.0 / 8.0, 0.0, 0.0 + cham_i)

            else:
                Pnt7 = Base.Vector(dia / 2.0 - H * 5.0 / 8.0, 0.0, m - cham_i)
                Pnt6 = Base.Vector(dia / 2.0 - H * 5.0 / 8.0, 0.0, 0.0 + cham_i)
            edge5 = Part.makeLine(Pnt5, Pnt6)
            edge6 = Part.makeLine(Pnt6, Pnt7)
            edge7 = Part.makeLine(Pnt7, PntH0)
            aWire = Part.Wire([edge2, edge3, edge4, edge5, edge6, edge7])
            boltIndex = 6

        # aFace =Part.Face(aWire)
        # Part.show(aWire)
        headShell = aWire.revolve(Base.Vector(0.0, 0.0, 0.0), Base.Vector(0.0, 0.0, 1.0), 360)
        # FreeCAD.Console.PrintMessage("the head with revolve: " + str(dia) + "\n")
        # Part.show(headShell)
        chamFace = headShell.Faces[0].cut(solidHex)
        # Part.show(chamFace)

        topFaces.append(chamFace.Faces[0])
        for i in range(1, boltIndex):
            topFaces.append(headShell.Faces[i])

        if self.rThread:
            if dia < 5.0:
                nutShell = Part.Shell(topFaces)
                nut = Part.Solid(nutShell)
                # Part.show(nut, 'unthreadedNut')
                threadCutter = self.makeInnerThread_2(dia, P, int(turns + 1), None, m)
                threadCutter.translate(Base.Vector(0.0, 0.0, turns * P + 0.5 * P))
                # Part.show(threadCutter, 'threadCutter')
                nut = nut.cut(threadCutter)

            else:
                threadShell = self.makeInnerThread_2(dia, P, int(turns), da, m)
                # threadShell.translate(Base.Vector(0.0, 0.0,turns*P))
                # Part.show(threadShell)
                for tFace in threadShell.Faces:
                    topFaces.append(tFace)
                headShell = Part.Shell(topFaces)
                nut = Part.Solid(headShell)
        else:
            nutShell = Part.Shell(topFaces)
            nut = Part.Solid(nutShell)

        return nut

    def makeThinCupNut(self):
        dia = self.getDia(self.fastenerDiam, True)
        P, g2, h, r, s, t, w = self.dimTable

        H = P * math.cos(math.radians(30)) * 5.0 / 8.0 # Gewindetiefe H
        if self.rThread: H *= 1.1
        e = s / math.sqrt(3) * 2.0
        cham_i = H * math.tan(math.radians(15.0))
        cham_o = (e - s) * math.tan(math.radians(15.0))
        d = dia / 2.0
          
        Pnt0 = Base.Vector(d - H, 0.0, cham_i)
        Pnt1 = Base.Vector(d, 0.0, 0.0)
        Pnt2 = Base.Vector(s / 2.0, 0.0, 0.0)
        Pnt3 = Base.Vector(e / 2.0, 0.0, cham_o)
        Pnt4 = Base.Vector(e / 2.0, 0.0, h - r + math.sqrt(r * r - e * e / 4.0))
        Pnt5 = Base.Vector(e / 4.0, 0.0, h - r + math.sqrt(r * r - e * e / 16.0))
        Pnt6 = Base.Vector(0.0, 0.0, h)
        Pnt7 = Base.Vector(0.0, 0.0, h-w)
        Pnt8 = Base.Vector(d - H, 0.0, t)

        edge0 = Part.makeLine(Pnt0, Pnt1)
        edge1 = Part.makeLine(Pnt1, Pnt2)
        edge2 = Part.makeLine(Pnt2, Pnt3)
        edge3 = Part.makeLine(Pnt3, Pnt4)
        edge4 = Part.Arc(Pnt4, Pnt5, Pnt6).toShape()
        edge5 = Part.makeLine(Pnt6, Pnt7)
        edge6 = Part.makeLine(Pnt7, Pnt8)
        edge7 = Part.makeLine(Pnt8, Pnt0)

        aWire = Part.Wire([edge0, edge1, edge2, edge3, edge4, edge5, edge6, edge7])
        # Part.show(aWire)
        aFace = Part.Face(aWire)
        head = aFace.revolve(Base.Vector(0.0, 0.0, 0.0), Base.Vector(0.0, 0.0, 1.0), 360.0)
        extrude = self.makeHextool(s, h, s * 2.0)
        nut = head.cut(extrude)

        if self.rThread:
          turns = int(math.floor(t/P))
          threadCutter = self.makeInnerThread_2(dia, P, turns, None, t)
          threadCutter.translate(Base.Vector(0.0, 0.0, turns * P))
          nut = nut.cut(threadCutter)

        return nut

    def makeCupNut(self):
        """
        Creates a cap (or 'acorn') nut.
        Supported Types:
          - DIN1587
        """
        SType = self.fastenerType
        dia = self.getDia(self.fastenerDiam, True)
        if SType == "DIN1587":
            P, d_k, h, m, s, t = self.dimTable
        else:
            raise RuntimeError("unknown screw type")
        pnts = list(
            map(
                lambda x: Base.Vector(x),
                [
                    [0, 0, 1.1 * dia / 4],
                    [1.1 * dia / 2, 0, 0],
                    [s / 2, 0, 0],
                    [s * math.sqrt(3) / 3, 0, 0.045 * s],
                    [s * math.sqrt(3) / 3, 0, m - 0.045 * s],
                    [s / 2, 0, m],
                    [d_k / 2, 0, m],
                    [d_k / 2, 0, h - d_k / 2],
                    [d_k / 2 * math.sqrt(2) / 2, 0, h - d_k / 2 + d_k / 2 * math.sqrt(2) / 2],
                    [0, 0, h],
                ],
            )
        )
        profile = Part.Wire(
            [
                Part.makeLine(pnts[0], pnts[1]),
                Part.makeLine(pnts[1], pnts[2]),
                Part.makeLine(pnts[2], pnts[3]),
                Part.makeLine(pnts[3], pnts[4]),
                Part.makeLine(pnts[4], pnts[5]),
                Part.makeLine(pnts[5], pnts[6]),
                Part.makeLine(pnts[6], pnts[7]),
                Part.Arc(pnts[7], pnts[8], pnts[9]).toShape(),
                Part.makeLine(pnts[9], pnts[0]),
            ]
        )
        shell = profile.revolve(Base.Vector(0, 0, 0), Base.Vector(0, 0, 1), 360)
        solid = Part.Solid(shell)
        # create an additional solid to cut the hex flats with
        mhex = Base.Matrix()
        mhex.rotateZ(math.radians(60.0))
        polygon = []
        vhex = Base.Vector(s / math.sqrt(3), 0, 0)
        for i in range(6):
            polygon.append(vhex)
            vhex = mhex.multiply(vhex)
        polygon.append(vhex)
        hexagon = Part.makePolygon(polygon)
        hexFace = Part.Face(hexagon)
        solidHex = hexFace.extrude(Base.Vector(0.0, 0.0, h * 1.1))
        solid = solid.common(solidHex)
        # cut the threads
        tap_tool = self.makeScrewTap("ScrewTap", self.fastenerDiam, t)
        tap_tool.rotate(Base.Vector(0, 0, 0), Base.Vector(1, 0, 0), 180)
        tap_tool.translate(Base.Vector(0, 0, -1 * P))
        tc_points = list(
            map(
                lambda x: Base.Vector(x),
                [
                    (0, 0, t - P),
                    (1.1 * dia / 2, 0, t - P - 1.1 * dia / 8),
                    (1.1 * dia / 2, 0, h),
                    (0, 0, h)
                ]
            )
        )
        thread_chamfer_profile = Part.Wire(
            [
                Part.makeLine(tc_points[0], tc_points[1]),
                Part.makeLine(tc_points[1], tc_points[2]),
                Part.makeLine(tc_points[2], tc_points[3]),
                Part.makeLine(tc_points[3], tc_points[0]),
            ]
        )
        cham_shell = thread_chamfer_profile.revolve(
            Base.Vector(0, 0, 0),
            Base.Vector(0, 0, 1),
            360
        )
        thread_chamfer = Part.Solid(cham_shell)
        tap_tool = tap_tool.cut(thread_chamfer)
        solid = solid.cut(tap_tool)
        return solid

    # make ISO 7380-1 Button head Screw
    # make ISO 7380-2 Button head Screw with collar
    # make DIN 967 cross recessed pan head Screw with collar
    def makeScrewTap(self, SType='ScrewTap', ThreadType='M6', l=25.0, customPitch=None, customDia=None):
        if ThreadType != 'Custom':
            dia = self.getDia(ThreadType, True)
            if SType == "ScrewTap":
                P, tunIn, tunEx = FsData["tuningTable"][ThreadType]
            elif SType == 'ScrewTapInch':
                P = FsData["asmeb18.3.1adef"][ThreadType][0]
        else:  # custom pitch and diameter
            P = customPitch
            if self.sm3DPrintMode:
                dia = self.smNutThrScaleA * customDia + self.smNutThrScaleB
            else:
                dia = customDia
        residue, turns = math.modf(l / P)
        # FreeCAD.Console.PrintMessage("turns:" + str(turns) + "res: " + str(residue) + "\n")
        if residue > 0.00001:
            turns += 1.0
        if self.rThread:
            screwTap = self.makeInnerThread_2(dia, P, int(turns), None, 0.0)
            # screwTap.translate(Base.Vector(0.0, 0.0, (1-residue)*P))
        else:
            H = P * math.cos(math.radians(30))  # Thread depth H
            r = dia / 2.0

            # points for inner thread profile
            adjusted_l = turns * P
            Pnt0 = Base.Vector(0.0, 0.0, 0)
            Pnt1 = Base.Vector(r - H * 5.0 / 8.0, 0.0, 0)
            Pnt2 = Base.Vector(r - H * 5.0 / 8.0, 0.0, -adjusted_l)
            Pnt3 = Base.Vector(0.0, 0.0, -adjusted_l)

            edge1 = Part.makeLine(Pnt0, Pnt1)
            edge2 = Part.makeLine(Pnt1, Pnt2)
            edge3 = Part.makeLine(Pnt2, Pnt3)
            aWire = Part.Wire([edge1, edge2, edge3])
            headShell = aWire.revolve(Base.Vector(0.0, 0.0, 0.0), Base.Vector(0.0, 0.0, 1.0), 360.0)
            screwTap = Part.Solid(headShell)
        return screwTap

    # make object to cut external threads on a shaft
    def makeScrewDie(self, SType="ScrewDie", ThreadType='M6', l=25.0, customPitch=None, customDia=None):
        if ThreadType != "Custom":
            dia = self.getDia(ThreadType, False)
            if SType == "ScrewDie":
                P, tunIn, tunEx = FsData["tuningTable"][ThreadType]
            elif SType == "ScrewDieInch":
                P = FsData["asmeb18.3.1adef"][ThreadType][0]
        else:  # custom pitch and diameter
            P = customPitch
            if self.sm3DPrintMode:
                dia = self.smScrewThrScaleA * customDia + self.smScrewThrScaleB
            else:
                dia = customDia
        if self.rThread:
            cutDia = dia * 0.75
        else:
            cutDia = dia
        refpoint = Base.Vector(0, 0, -1 * l)
        screwDie = Part.makeCylinder(dia * 1.1 / 2, l, refpoint)
        screwDie = screwDie.cut(Part.makeCylinder(cutDia / 2, l, refpoint))
        if self.rThread:
            shell_thread = self.makeShellthread(dia, P, l, False, 0)
            thr_p1 = Base.Vector(0, 0, 0)
            thr_p2 = Base.Vector(dia / 2, 0, 0)
            thr_e1 = Part.makeLine(thr_p1, thr_p2)
            thr_cap_profile = Part.Wire([thr_e1])
            thr_cap = thr_cap_profile.revolve(Base.Vector(0, 0, 0), Base.Vector(0, 0, 1), 360)
            #Part.show(thr_cap)
            #Part.show(shell_thread)
            thr_faces = shell_thread.Faces
            thr_faces.extend(thr_cap.Faces)
            thread_shell = Part.Shell(thr_faces)
            thread_solid = Part.Solid(thread_shell)
            screwDie = screwDie.cut(thread_solid)
        return screwDie

    # make a length of standard threaded rod
    def makeThreadedRod(self, SType="ThreadedRod", ThreadType='M6', l=25.0, customPitch=None, customDia=None):
        if ThreadType != 'Custom':
            dia = self.getDia(ThreadType, False)
            if SType == 'ThreadedRod':
                P, tunIn, tunEx = FsData['tuningTable'][ThreadType]
            elif SType == 'ThreadedRodInch':
                P = FsData['asmeb18.3.1adef'][ThreadType][0]
        else:  # custom pitch and diameter
            P = customPitch
            if self.sm3DPrintMode:
                dia = self.smScrewThrScaleA * customDia + self.smScrewThrScaleB
            else:
                dia = customDia
        dia = dia * 1.01
        cham = P
        p0 = Base.Vector(0, 0, 0)
        p1 = Base.Vector(dia / 2 - cham, 0, 0)
        p2 = Base.Vector(dia / 2, 0, 0 - cham)
        p3 = Base.Vector(dia / 2, 0, -1 * l + cham)
        p4 = Base.Vector(dia / 2 - cham, 0, -1 * l)
        p5 = Base.Vector(0, 0, -1 * l)
        e1 = Part.makeLine(p0, p1)
        e2 = Part.makeLine(p1, p2)
        e3 = Part.makeLine(p2, p3)
        e4 = Part.makeLine(p3, p4)
        e5 = Part.makeLine(p4, p5)
        p_profile = Part.Wire([e1, e2, e3, e4, e5])
        p_shell = p_profile.revolve(Base.Vector(0.0, 0.0, 0.0), Base.Vector(0.0, 0.0, 1.0), 360.0)
        screw = Part.Solid(p_shell)
        if self.rThread:
            # make the threaded section
            shell_thread = self.makeShellthread(dia, P, l, False, 0)
            thr_p1 = Base.Vector(0, 0, 0)
            thr_p2 = Base.Vector(dia / 2, 0, 0)
            thr_e1 = Part.makeLine(thr_p1, thr_p2)
            thr_cap_profile = Part.Wire([thr_e1])
            thr_cap = thr_cap_profile.revolve(Base.Vector(0, 0, 0), Base.Vector(0, 0, 1), 360)
            thr_faces = shell_thread.Faces
            thr_faces.extend(thr_cap.Faces)
            thread_shell = Part.Shell(thr_faces)
            thread_solid = Part.Solid(thread_shell)
            screw = screw.common(thread_solid)
        return screw

    def cutChamfer(self, dia_cC, P_cC, l_cC):
        cham_t = P_cC * math.sqrt(3.0) / 2.0 * 17.0 / 24.0
        PntC0 = Base.Vector(0.0, 0.0, -l_cC)
        PntC1 = Base.Vector(dia_cC / 2.0 - cham_t, 0.0, -l_cC)
        PntC2 = Base.Vector(dia_cC / 2.0 + cham_t, 0.0, -l_cC + cham_t + cham_t)
        PntC3 = Base.Vector(dia_cC / 2.0 + cham_t, 0.0, -l_cC - P_cC - cham_t)
        PntC4 = Base.Vector(0.0, 0.0, -l_cC - P_cC - cham_t)

        edgeC1 = Part.makeLine(PntC0, PntC1)
        edgeC2 = Part.makeLine(PntC1, PntC2)
        edgeC3 = Part.makeLine(PntC2, PntC3)
        edgeC4 = Part.makeLine(PntC3, PntC4)
        edgeC5 = Part.makeLine(PntC4, PntC0)
        CWire = Part.Wire([edgeC1, edgeC2, edgeC3, edgeC4, edgeC5])
        # Part.show(CWire)
        CFace = Part.Face(CWire)
        cyl = CFace.revolve(Base.Vector(0.0, 0.0, 0.0), Base.Vector(0.0, 0.0, 1.0), 360)
        return cyl

    # cross recess type H
    def makeCross_H3(self, CrossType='2', m=6.9, h=0.0):
        # m = diameter of cross at top of screw at reference level for penetration depth
        b, e_mean, g, f_mean, r, t1, alpha, beta = FsData["iso4757def"][CrossType]

        rad265 = math.radians(26.5)
        rad28 = math.radians(28.0)
        tg = (m - g) / 2.0 / math.tan(rad265)  # depth at radius of g
        t_tot = tg + g / 2.0 * math.tan(rad28)  # total depth

        # print 'tg: ', tg,' t_tot: ', t_tot
        hm = m / 4.0
        hmc = m / 2.0
        rmax = m / 2.0 + hm * math.tan(rad265)

        Pnt0 = Base.Vector(0.0, 0.0, hm)
        Pnt1 = Base.Vector(rmax, 0.0, hm)
        Pnt3 = Base.Vector(0.0, 0.0, 0.0)
        Pnt4 = Base.Vector(g / 2.0, 0.0, -tg)
        Pnt5 = Base.Vector(0.0, 0.0, -t_tot)

        edge1 = Part.makeLine(Pnt0, Pnt1)
        edge3 = Part.makeLine(Pnt1, Pnt4)
        edge4 = Part.makeLine(Pnt4, Pnt5)
        # FreeCAD.Console.PrintMessage("Edges made Pnt2: " + str(Pnt2) + "\n")

        aWire = Part.Wire([edge1, edge3, edge4])
        crossShell = aWire.revolve(Pnt3, Base.Vector(0.0, 0.0, 1.0), 360)
        # FreeCAD.Console.PrintMessage("Peak-wire revolved: " + str(e_mean) + "\n")
        cross = Part.Solid(crossShell)
        # Part.show(cross)

        # the need to cut 4 corners out of the above shape.
        # Definition of corner
        # The angles 92 degrees and alpha are defined on a plane which has
        # an angle of beta against our coordinate system.
        # The projected angles are needed for easier calculation!
        rad_alpha = math.radians(alpha / 2.0)
        rad92 = math.radians(92.0 / 2.0)
        rad_beta = math.radians(beta)

        rad_alpha_p = math.atan(math.tan(rad_alpha) / math.cos(rad_beta))
        rad92_p = math.atan(math.tan(rad92) / math.cos(rad_beta))

        tb = tg + (g - b) / 2.0 * math.tan(rad28)  # depth at dimension b
        rbtop = b / 2.0 + (hmc + tb) * math.tan(rad_beta)  # radius of b-corner at hm
        rbtot = b / 2.0 - (t_tot - tb) * math.tan(rad_beta)  # radius of b-corner at t_tot

        dre = e_mean / 2.0 / math.tan(rad_alpha_p)  # delta between corner b and corner e in x direction
        # FreeCAD.Console.PrintMessage("delta calculated: " + str(dre) + "\n")

        dx = m / 2.0 * math.cos(rad92_p)
        dy = m / 2.0 * math.sin(rad92_p)

        PntC0 = Base.Vector(rbtop, 0.0, hmc)
        PntC1 = Base.Vector(rbtot, 0.0, -t_tot)
        PntC2 = Base.Vector(rbtop + dre, +e_mean / 2.0, hmc)
        PntC3 = Base.Vector(rbtot + dre, +e_mean / 2.0, -t_tot)
        PntC4 = Base.Vector(rbtop + dre, -e_mean / 2.0, hmc)
        PntC5 = Base.Vector(rbtot + dre, -e_mean / 2.0, -t_tot)

        PntC6 = Base.Vector(rbtop + dre + dx, +e_mean / 2.0 + dy, hmc)
        # PntC7 = Base.Vector(rbtot+dre+dx,+e_mean/2.0+dy,-t_tot)
        PntC7 = Base.Vector(rbtot + dre + 2.0 * dx, +e_mean + 2.0 * dy, -t_tot)
        PntC8 = Base.Vector(rbtop + dre + dx, -e_mean / 2.0 - dy, hmc)
        # PntC9 = Base.Vector(rbtot+dre+dx,-e_mean/2.0-dy,-t_tot)
        PntC9 = Base.Vector(rbtot + dre + 2.0 * dx, -e_mean - 2.0 * dy, -t_tot)

        # wire_hm = Part.makePolygon([PntC0,PntC2,PntC6,PntC8,PntC4,PntC0])
        # face_hm =Part.Face(wire_hm)
        # Part.show(face_hm)

        wire_t_tot = Part.makePolygon([PntC1, PntC3, PntC7, PntC9, PntC5, PntC1])
        # Part.show(wire_t_tot)
        edgeC1 = Part.makeLine(PntC0, PntC1)
        # FreeCAD.Console.PrintMessage("edgeC1 with PntC9" + str(PntC9) + "\n")

        makeSolid = True
        isFrenet = False
        corner = Part.Wire(edgeC1).makePipeShell([wire_t_tot], makeSolid, isFrenet)
        # Part.show(corner)

        rot_axis = Base.Vector(0., 0., 1.0)
        sin_res = math.sin(math.radians(90) / 2.0)
        cos_res = math.cos(math.radians(90) / 2.0)
        rot_axis.multiply(-sin_res)  # Calculation of Quaternion-Elements
        # FreeCAD.Console.PrintMessage("Quaternion-Elements" + str(cos_res) + "\n")

        pl_rot = FreeCAD.Placement()
        pl_rot.Rotation = (rot_axis.x, rot_axis.y, rot_axis.z, cos_res)  # Rotation-Quaternion 90° z-Axis

        crossShell = crossShell.cut(corner)
        # Part.show(crossShell)
        cutplace = corner.Placement

        cornerFaces = []
        cornerFaces.append(corner.Faces[0])
        cornerFaces.append(corner.Faces[1])
        cornerFaces.append(corner.Faces[3])
        cornerFaces.append(corner.Faces[4])

        cornerShell = Part.Shell(cornerFaces)
        cornerShell = cornerShell.common(cross)
        addPlace = cornerShell.Placement

        crossFaces = cornerShell.Faces

        for i in range(3):
            cutplace.Rotation = pl_rot.Rotation.multiply(corner.Placement.Rotation)
            corner.Placement = cutplace
            crossShell = crossShell.cut(corner)
            addPlace.Rotation = pl_rot.Rotation.multiply(cornerShell.Placement.Rotation)
            cornerShell.Placement = addPlace
            for coFace in cornerShell.Faces:
                crossFaces.append(coFace)

        # Part.show(crossShell)
        for i in range(1, 6):
            crossFaces.append(crossShell.Faces[i])

        crossShell0 = Part.Shell(crossFaces)

        crossFaces.append(crossShell.Faces[0])
        crossShell = Part.Shell(crossFaces)

        cross = Part.Solid(crossShell)

        # FreeCAD.Console.PrintMessage("Placement: " + str(pl_rot) + "\n")

        cross.Placement.Base = Base.Vector(0.0, 0.0, h)
        crossShell0.Placement.Base = Base.Vector(0.0, 0.0, h)
        # Part.show(crossShell0)
        # Part.show(cross)
        return cross, crossShell0

    # Allen recess cutting tool
    # Parameters used: s_mean, k, t_min, dk
    def makeAllen2(self, s_a=3.0, t_a=1.5, h_a=2.0, t_2=0.0):
        # h_a  top height location of cutting tool
        # s_a hex width
        # t_a dept of the allen
        # t_2 depth of center-bore

        if t_2 == 0.0:
            depth = s_a / 3.0
            e_cham = 2.0 * s_a / math.sqrt(3.0)
            # FreeCAD.Console.PrintMessage("allen tool: " + str(s_a) + "\n")

            # Points for an arc at the peak of the cone
            rCone = e_cham / 4.0
            hyp = (depth * math.sqrt(e_cham ** 2 / depth ** 2 + 1.0) * rCone) / e_cham
            radAlpha = math.atan(e_cham / depth)
            radBeta = math.pi / 2.0 - radAlpha
            zrConeCenter = hyp - depth - t_a
            xArc1 = math.sin(radBeta) * rCone
            zArc1 = zrConeCenter - math.cos(radBeta) * rCone
            xArc2 = math.sin(radBeta / 2.0) * rCone
            zArc2 = zrConeCenter - math.cos(radBeta / 2.0) * rCone
            zArc3 = zrConeCenter - rCone

            # The round part of the cutting tool, we need for the allen hex recess
            PntH1 = Base.Vector(0.0, 0.0, -t_a - depth - depth)
            PntH2 = Base.Vector(e_cham, 0.0, -t_a - depth - depth)
            PntH3 = Base.Vector(e_cham, 0.0, -t_a + depth)
            PntH4 = Base.Vector(0.0, 0.0, -t_a - depth)

            PntA1 = Base.Vector(xArc1, 0.0, zArc1)
            PntA2 = Base.Vector(xArc2, 0.0, zArc2)
            PntA3 = Base.Vector(0.0, 0.0, zArc3)

            edgeA1 = Part.Arc(PntA1, PntA2, PntA3).toShape()

            edgeH1 = Part.makeLine(PntH1, PntH2)
            edgeH2 = Part.makeLine(PntH2, PntH3)
            edgeH3 = Part.makeLine(PntH3, PntA1)
            edgeH4 = Part.makeLine(PntA3, PntH1)

            hWire = Part.Wire([edgeH1, edgeH2, edgeH3, edgeA1, edgeH4])
            hex_depth = -1.0 - t_a - depth * 1.1
        else:
            e_cham = 2.0 * s_a / math.sqrt(3.0)
            d_cent = s_a / 3.0
            depth_cent = d_cent * math.tan(math.pi / 6.0)
            depth_cham = (e_cham - d_cent) * math.tan(math.pi / 6.0)

            Pnts = [
                Base.Vector(0.0, 0.0, -t_2 - depth_cent),
                Base.Vector(0.0, 0.0, -t_2 - depth_cent - depth_cent),
                Base.Vector(e_cham, 0.0, -t_2 - depth_cent - depth_cent),
                Base.Vector(e_cham, 0.0, -t_a + depth_cham),
                Base.Vector(d_cent, 0.0, -t_a),
                Base.Vector(d_cent, 0.0, -t_2)
            ]

            edges = []
            for i in range(0, len(Pnts) - 1):
                edges.append(Part.makeLine(Pnts[i], Pnts[i + 1]))
            edges.append(Part.makeLine(Pnts[5], Pnts[0]))

            hWire = Part.Wire(edges)
            hex_depth = -1.0 - t_2 - depth_cent * 1.1

        # Part.show(hWire)
        hFace = Part.Face(hWire)
        roundtool = hFace.revolve(Base.Vector(0.0, 0.0, 0.0), Base.Vector(0.0, 0.0, 1.0), 360)

        # create hexagon
        mhex = Base.Matrix()
        mhex.rotateZ(math.radians(60.0))
        polygon = []
        vhex = Base.Vector(s_a / math.sqrt(3.0), 0.0, 1.0)
        for i in range(6):
            polygon.append(vhex)
            vhex = mhex.multiply(vhex)
        polygon.append(vhex)
        hexagon = Part.makePolygon(polygon)
        hexFace = Part.Face(hexagon)
        solidHex = hexFace.extrude(Base.Vector(0.0, 0.0, hex_depth))
        allen = solidHex.cut(roundtool)
        # Part.show(allen)

        allenFaces = [allen.Faces[0]]
        for i in range(2, len(allen.Faces)):
            allenFaces.append(allen.Faces[i])
        allenShell = Part.Shell(allenFaces)
        solidHex.Placement.Base = Base.Vector(0.0, 0.0, h_a)
        allenShell.Placement.Base = Base.Vector(0.0, 0.0, h_a)

        return solidHex, allenShell

    # ISO 10664 Hexalobular internal driving feature for bolts and screws
    def makeIso10664_3(self, RType='T20', t_hl=3.0, h_hl=0):
        # t_hl depth of the recess
        # h_hl top height location of Cutting tool
        A, B, Re = FsData["iso10664def"][RType]
        sqrt_3 = math.sqrt(3.0)
        depth = A / 4.0
        offSet = 1.0

        # Chamfer cutter for the hexalobular recess
        PntH1 = Base.Vector(0.0, 0.0, -t_hl - depth - 1.0)
        # PntH2 = Base.Vector(A/2.0*1.02,0.0,-t_hl-depth-1.0)
        # PntH3 = Base.Vector(A/2.0*1.02,0.0,-t_hl)
        PntH2 = Base.Vector(A, 0.0, -t_hl - depth - 1.0)
        PntH3 = Base.Vector(A, 0.0, -t_hl + depth)
        PntH4 = Base.Vector(0.0, 0.0, -t_hl - depth)

        # Points for an arc at the peak of the cone
        rCone = A / 4.0
        hyp = (depth * math.sqrt(A ** 2 / depth ** 2 + 1.0) * rCone) / A
        radAlpha = math.atan(A / depth)
        radBeta = math.pi / 2.0 - radAlpha
        zrConeCenter = hyp - depth - t_hl
        xArc1 = math.sin(radBeta) * rCone
        zArc1 = zrConeCenter - math.cos(radBeta) * rCone
        xArc2 = math.sin(radBeta / 2.0) * rCone
        zArc2 = zrConeCenter - math.cos(radBeta / 2.0) * rCone
        zArc3 = zrConeCenter - rCone

        PntA1 = Base.Vector(xArc1, 0.0, zArc1)
        PntA2 = Base.Vector(xArc2, 0.0, zArc2)
        PntA3 = Base.Vector(0.0, 0.0, zArc3)

        edgeA1 = Part.Arc(PntA1, PntA2, PntA3).toShape()

        edgeH1 = Part.makeLine(PntH1, PntH2)
        edgeH2 = Part.makeLine(PntH2, PntH3)
        edgeH3 = Part.makeLine(PntH3, PntA1)
        edgeH4 = Part.makeLine(PntA3, PntH1)

        hWire = Part.Wire([edgeH1, edgeH2, edgeH3, edgeA1])
        cutShell = hWire.revolve(Base.Vector(0.0, 0.0, 0.0), Base.Vector(0.0, 0.0, 1.0), 360)
        cutTool = Part.Solid(cutShell)

        Ri = -((B + sqrt_3 * (2. * Re - A)) * B + (A - 4. * Re) * A) / (4. * B - 2. * sqrt_3 * A + (4. * sqrt_3 - 8.) * Re)
        # print '2nd  Ri last solution: ', Ri
        beta = math.acos(A / (4 * Ri + 4 * Re) - (2 * Re) / (4 * Ri + 4 * Re)) - math.pi / 6
        # print 'beta: ', beta
        Rh = (sqrt_3 * (A / 2.0 - Re)) / 2.0
        Re_x = A / 2.0 - Re + Re * math.sin(beta)
        Re_y = Re * math.cos(beta)
        Ri_y = B / 4.0
        Ri_x = sqrt_3 * B / 4.0

        mhex = Base.Matrix()
        mhex.rotateZ(math.radians(60.0))
        hexlobWireList = []

        PntRe0 = Base.Vector(Re_x, -Re_y, offSet)
        PntRe1 = Base.Vector(A / 2.0, 0.0, offSet)
        PntRe2 = Base.Vector(Re_x, Re_y, offSet)
        edge0 = Part.Arc(PntRe0, PntRe1, PntRe2).toShape()
        # Part.show(edge0)
        hexlobWireList.append(edge0)

        PntRi = Base.Vector(Ri_x, Ri_y, offSet)
        PntRi2 = mhex.multiply(PntRe0)
        edge1 = Part.Arc(PntRe2, PntRi, PntRi2).toShape()
        # Part.show(edge1)
        hexlobWireList.append(edge1)

        for i in range(5):
            PntRe1 = mhex.multiply(PntRe1)
            PntRe2 = mhex.multiply(PntRe2)
            edge0 = Part.Arc(PntRi2, PntRe1, PntRe2).toShape()
            hexlobWireList.append(edge0)
            PntRi = mhex.multiply(PntRi)
            PntRi2 = mhex.multiply(PntRi2)
            if i == 5:
                edge1 = Part.Arc(PntRe2, PntRi, PntRe0).toShape()
            else:
                edge1 = Part.Arc(PntRe2, PntRi, PntRi2).toShape()
            hexlobWireList.append(edge1)
        hexlobWire = Part.Wire(hexlobWireList)
        # Part.show(hWire)

        face = Part.Face(hexlobWire)

        # Extrude in z to create the cutting tool for the screw-head-face
        Helo = face.extrude(Base.Vector(0.0, 0.0, -t_hl - depth - offSet))
        # Make the recess-shell for the screw-head-shell

        hexlob = Helo.cut(cutTool)
        # Part.show(hexlob)
        hexlobFaces = [hexlob.Faces[0]]
        for i in range(2, 15):
            hexlobFaces.append(hexlob.Faces[i])

        hexlobShell = Part.Shell(hexlobFaces)

        hexlobShell.Placement.Base = Base.Vector(0.0, 0.0, h_hl)
        Helo.Placement.Base = Base.Vector(0.0, 0.0, h_hl)

        return Helo, hexlobShell

    def setThreadType(self, TType='simple'):
        self.simpThread = False
        self.symThread = False
        self.rThread = False
        if TType == 'simple':
            self.simpThread = True
        if TType == 'symbol':
            self.symThread = True
        if TType == 'real':
            self.rThread = True

    def setTuner(self, myTuner=511):
        self.Tuner = myTuner

    def getDia(self, ThreadType, isNut):
        threadstring = ThreadType.strip("()")
        dia = FsData["DiaList"][threadstring][0]
        if self.sm3DPrintMode:
            if isNut:
                dia = self.smNutThrScaleA * dia + self.smNutThrScaleB
            else:
                dia = self.smScrewThrScaleA * dia + self.smScrewThrScaleB
        return dia

    def getLength(self, LenStr):
        # washers and nuts pass an int (1), for their unused length attribute
        # handle this circumstance if necessary
        if type(LenStr) == int:
            return LenStr
        # otherwise convert the string to a number using predefined rules
        if 'in' not in LenStr:
            LenFloat = float(LenStr)
        else:
            components = LenStr.strip('in').split(' ')
            total = 0
            for item in components:
                if '/' in item:
                    subcmpts = item.split('/')
                    total += float(subcmpts[0]) / float(subcmpts[1])
                else:
                    total += float(item)
            LenFloat = total * 25.4
        return LenFloat

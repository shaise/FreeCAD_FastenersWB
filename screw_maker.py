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
*   Refactor by shai 2022                                                 *
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


import FreeCAD
import Part
import math
from FreeCAD import Base
import importlib
import FastenerBase
from FastenerBase import FsData
from FastenerBase import FSFaceMaker

DEBUG = False  # TODO: set to True to show debug messages; does not work.

# some common constants
sqrt2 = math.sqrt(2.0)
sqrt3 = math.sqrt(3.0)
cos30 = math.cos(math.radians(30.0))


class Screw:
    def __init__(self):
        self.objAvailable = True
        self.Tuner = 510
        self.LeftHanded = False
        # thread scaling for 3D printers
        # scaled_diam = diam * ScaleA + ScaleB
        self.sm3DPrintMode = False
        self.smNutThrScaleA = 1.0
        self.smNutThrScaleB = 0.0
        self.smScrewThrScaleA = 1.0
        self.smScrewThrScaleB = 0.0

    def createScrew(self, function, fastenerAttribs):
        # self.simpThread = self.SimpleScrew.isChecked()
        # self.symThread = self.SymbolThread.isChecked()
        # FreeCAD.Console.PrintMessage(NL_text + "\n")
        if not self.objAvailable:
            return None
        try:
            if fastenerAttribs.calc_len is not None:
                fastenerAttribs.calc_len = self.getLength(
                    fastenerAttribs.calc_len)
            if not hasattr(self, function):
                module = "FsFunctions.FS" + function
                setattr(Screw, function, getattr(
                    importlib.import_module(module), function))
        except ValueError:
            # print "Error! nom_dia and length values must be valid numbers!"
            FreeCAD.Console.PrintMessage(
                "Error! nom_dia and length values must be valid numbers!\n")
            return None

        if (fastenerAttribs.Diameter == "Custom"):
            fastenerAttribs.dimTable = None
        else:
            fastenerAttribs.dimTable = FsData[fastenerAttribs.baseType +
                                              "def"][fastenerAttribs.Diameter]
        self.LeftHanded = fastenerAttribs.LeftHanded
        # self.fastenerLen = l
        # fa.baseType = ST_text
        # fa.calc_diam = ND_text
        # self.customPitch = customPitch
        # self.customDia = customDia
        doc = FreeCAD.activeDocument()

        if function != "":
            function = "self." + function + "(fastenerAttribs)"
            screw = eval(function)
            done = True
        else:
            FreeCAD.Console.PrintMessage(
                "No suitable function for " + fastenerAttribs.Type + " Screw Type!\n")
            return None
        # Part.show(screw)
        return screw

    def makeDin7998Thread(
        self, zs: float, ze: float, zt: float, ri: float, ro: float, p: float,
        isFlat: bool = False
    ) -> Part.Shape:
        """create a DIN 7998 Wood Thread
        Parameters:
        - zs: z position of start of the threaded part
        - ze: z position of end of the flat portion of screw (just where the tip starts)
        - zt: z position of screw tip
        - ro: outer radius
        - ri: inner radius
        - p:  thread pitch
        """
        # epsilon needed since OCCT struggle to handle overlaps
        epsilon = 0.03
        tph = ro - ri                           # thread profile height
        tphb = tph / math.tan(math.radians(60))  # thread profile half base
        # size ratio between tip start thread and standard thread
        tpratio = 0.5
        tph2 = tph * tpratio
        tphb2 = tphb * tpratio
        tipH = ze - zt

        # tip thread profile
        fm = FastenerBase.FSFaceMaker()
        fm.AddPoints((0.0, -tphb2), (0.0, tphb2), (2.0 * tphb2, tphb2))
        aWire = fm.GetClosedWire()
        aWire.translate(FreeCAD.Vector(epsilon, 0.0, 3.0 * tphb2))

        # top thread profile
        fm.Reset()
        fm.AddPoints((0.0, -tphb), (0.0, tphb), (tph, 0.0))
        bWire = fm.GetClosedWire()
        bWire.translate(FreeCAD.Vector(ri - epsilon, 0.0, tphb + tipH))

        # Only make the tip helix when the point is not flat
        if not isFlat:
            # create helix for tip thread part
            numTurns = math.floor(tipH / p) or 1
            FreeCAD.Console.PrintMessage(str(numTurns))
            # Part.show(hlx)
            hlx = Part.makeLongHelix(p, numTurns * p, 5, 0, self.LeftHanded)
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
                # Part.show(tip_solid)
            else:
                raise RuntimeError("Failed to create woodscrew tip thread")


        # create helix for body thread part
        hlx = Part.makeLongHelix(p, zs - ze, 5, 0, self.LeftHanded)
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
            # Part.show(body_solid)
        else:
            raise RuntimeError("Failed to create woodscrew body thread")

        if isFlat:
            thread_solid = body_solid
        else:
            thread_solid = body_solid.fuse(tip_solid)
        # rotate the thread solid to prevent OCC errors due to cylinder seams aligning
        thread_solid.rotate(Base.Vector(0, 0, 0), Base.Vector(0, 0, 1), 180)
        #Part.show(thread_solid, "thread_solid")
        return thread_solid

    @staticmethod
    def GetInnerThreadMinDiameter(
        dia: float, P: float, addEpsilon: float=0.001
    ) -> float:
        H = P * cos30  # Thread depth H
        return dia - H * 5.0 / 4.0 + addEpsilon

    def CreateThreadCutter(self, dia: float, P: float, blen: float) -> Part.Shape:
        """Returns a shape that can be subtracted from a shaft to create a
        standard 60 degree screw thread.
        Parameters:
        - dia: major diameter fo the threads
          (e.g: this would be 6.0 for an M6 thread with nominal dimensions)
        - P: thread pitch
        - blen: thread length. The actual returned shape will be slightly
          longer, to ensure that a thread of the specified length can be
          cut without errors at it's ends

        The shape is created at the origin, extending in the -Z direction.
        """
        # create a sketch profile of the thread
        # ref: https://en.wikipedia.org/wiki/ISO_metric_screw_thread
        H = math.sqrt(3) / 2 * P
        trotations = blen // P + 1
        fillet_r = P * math.sqrt(3) / 12
        helix_height = trotations * P
        dia2 = dia / 2

        fm = FastenerBase.FSFaceMaker()
        fm.AddPoint(dia2 + sqrt3 * 3 / 80 * P, -0.475 * P)
        fm.AddPoint(dia2 - 0.625 * H, -1 * P / 8)
        fm.AddArc(dia2 - 0.625 * H - 0.5 * fillet_r,
                  0, dia2 - 0.625 * H, P / 8)
        fm.AddPoint(dia2 + sqrt3 * 3 / 80 * P, 0.475 * P)
        thread_profile_wire = fm.GetClosedWire()
        thread_profile_wire.translate(Base.Vector(0, 0, -1 * helix_height))
        # make the helical paths to sweep along
        # NOTE: makeLongHelix creates slightly conical
        # helices unless the 4th parameter is set to 0!
        helix = Part.makeLongHelix(
            P, helix_height, dia / 2, 0, self.LeftHanded)
        helix.rotate(Base.Vector(0, 0, 0), Base.Vector(1, 0, 0), 180)
        sweep = Part.BRepOffsetAPI.MakePipeShell(helix)
        sweep.setFrenetMode(True)
        sweep.setTransitionMode(1)  # right corner transition
        sweep.add(thread_profile_wire)
        if sweep.isReady():
            sweep.build()
        else:
            # geometry couldn't be generated in a usable form
            raise RuntimeError(
                "Failed to create shell thread: could not sweep thread")
        sweep.makeSolid()
        threads = sweep.shape()
        threads.translate(Base.Vector(0.0, 0.0, P / 2))
        return threads

    def CreateInnerThreadCutter(self, dia: float, P: float, blen: float) -> Part.Shape:
        H = P * cos30  # Thread depth H
        r = dia / 2.0

        # make just one turn, length is identical to pitch
        helix = Part.makeLongHelix(
            P, blen, r, 0, self.LeftHanded
        )

        # points for inner thread profile
        fm = FastenerBase.FSFaceMaker()
        fm.AddPoint(
            r - 0.875 * H + 0.025 * P * sqrt3,
            P / 2 * 0.95 + P * 1 / 16
        )
        fm.AddPoint(r, P * 2.0 / 16.0)
        fm.AddArc(r + H * 1 / 24.0, P * 2.0 / 32.0, r, 0)
        fm.AddPoint(
            r - 0.875 * H + 0.025 * P * sqrt3,
            -P / 2 * 0.95 + P * 1 / 16
        )
        W0 = fm.GetClosedWire()
        W0.translate(Base.Vector(0, 0, -P * 9.0 / 16.0))

        makeSolid = True
        isFrenet = True
        cutTool = Part.Wire(helix).makePipeShell([W0], makeSolid, isFrenet)
        return cutTool

    def CreateKnurlCutter(self, outDia: float, inDia: float, zbase: float, height: float, leftHanded: bool) -> Part.Shape:
        ro = outDia / 2.0
        ri = inDia / 2.0
        p = outDia * 3.1415
        tan_a2 = 1.2 # tan(50)

        # make just one turn, length is identical to pitch
        helix = Part.makeLongHelix(
            p, height, ro, 0, leftHanded
        )

        # create base triangle
        d2 = outDia - ri
        y2 = (d2 - ri) * tan_a2
        p1 = FreeCAD.Base.Vector(ri, 0, 0)
        p2 = FreeCAD.Base.Vector(d2, y2, 0)
        p3 = FreeCAD.Base.Vector(d2, -y2, 0)
        l1 = Part.makeLine(p1, p2)
        l2 = Part.makeLine(p2, p3)
        l3 = Part.makeLine(p3, p1)
        w = Part.Wire([l1,l2, l3])

        cutElement = Part.Wire(helix).makePipeShell([w], True, True)
        cutElement.translate(Base.Vector(0, 0, zbase))
        cutElements = [cutElement]
        ang = math.atan(y2 / d2) * 114.6 # 2 * 180 / pi
        numCuts = int(360.0 / ang)
        elementAng = 360 / numCuts

        for i in range(1, numCuts):
            nextElement = cutElement.copy().rotate(Base.Vector(0,0,0), Base.Vector(0,0,1), i * elementAng)
            cutElements.append(nextElement)
        cutTool = Part.Compound(cutElements)
        return cutTool

    def CreateBlindThreadCutter(self, dia: float, P: float, blen: float) -> Part.Shape:
        """Returns a shape that can be subtracted from a shaft to create a
        standard 60 degree screw thread.
        Parameters:
        - dia: major diameter fo the threads
          (e.g: this would be 6.0 for an M6 thread with nominal dimensions)
        - P: thread pitch
        - blen: thread length. The actual returned shape will be slightly
          longer, to ensure that a thread of the specified length can be
          cut without errors at it's ends

        The shape is created at the origin, extending in the -Z direction.
        It has a tapered lead out at the top of the shape, to simulate the
        partially threaded section of a cut or rolled screw thread.
        """
        # create a sketch profile of the thread
        # ref: https://en.wikipedia.org/wiki/ISO_metric_screw_thread
        H = math.sqrt(3) / 2 * P
        trotations = blen // P + 1
        fillet_r = P * math.sqrt(3) / 12
        helix_height = trotations * P
        dia2 = dia / 2

        fm = FastenerBase.FSFaceMaker()
        fm.AddPoint(dia2 + sqrt3 * 3 / 80 * P, -0.475 * P)
        fm.AddPoint(dia2 - 0.625 * H, -1 * P / 8)
        fm.AddArc(dia2 - 0.625 * H - 0.5 * fillet_r,
                  0, dia2 - 0.625 * H, P / 8)
        fm.AddPoint(dia2 + sqrt3 * 3 / 80 * P, 0.475 * P)
        thread_profile_wire = fm.GetClosedWire()
        thread_profile_wire.translate(Base.Vector(0, 0, -1 * helix_height - P * 0.6))
        # make the helical paths to sweep along
        # NOTE: makeLongHelix creates slightly conical
        # helices unless the 4th parameter is set to 0!
        main_helix = Part.makeLongHelix(
            P, helix_height, dia / 2, 0, self.LeftHanded)
        lead_out_helix = Part.makeLongHelix(
            P, P / 2, dia / 2 + 0.55 * (5 / 8 * H + 0.5 * fillet_r), 0, self.LeftHanded)
        main_helix.rotate(Base.Vector(0, 0, 0), Base.Vector(1, 0, 0), 180)
        lead_out_helix.translate(Base.Vector(
            0.55 * (-1 * (5 / 8 * H + 0.5 * fillet_r)), 0, 0))
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
            # geometry couldn't be generated in a usable form
            raise RuntimeError(
                "Failed to create shell thread: could not sweep thread")
        sweep.makeSolid()
        threads = sweep.shape()
        top_remover = Part.makeBox(
            2 * dia,
            2 * dia,
            2 * dia,
            Base.Vector(-dia, -dia, -P * 0.1)
        )
        threads = threads.cut(top_remover)
        return threads

    def CreateBlindInnerThreadCutter(
        self, dia: float, P: float, blen: float
    ) -> Part.Shape:
        """create a blind inner thread cutter,
        For use with a boolean cut operation.
        The solid is oriented z-up and placed at the origin.
        Parameters:
        dia: outer diameter of threads
        P: thread pitch
        blen: usable threaded length, measured from the base of the cutter
        """
        # simulate a 118 degree drill point at the end of the solid
        conic_height = 0.55 * dia / math.tan(math.radians(59))
        if blen <= conic_height:
            raise ValueError(
                f"Can't create thread cutter of diameter {dia} & height {blen}"
            )
        threads = self.CreateInnerThreadCutter(dia, P, blen + conic_height)
        inner_rad = dia / 2 - 0.625 * sqrt3 / 2 * P
        core = Part.makeCylinder(inner_rad, blen + 1.1 * conic_height + 1)
        core.translate(Base.Vector(0.0, 0.0, -1.0))
        obj = core.fuse(threads)
        fm = FastenerBase.FSFaceMaker()
        fm.AddPoint(0.0, 0.0)
        fm.AddPoint(0.55 * dia, 0.0)
        fm.AddPoint(0.55 * dia, blen)
        fm.AddPoint(0.0, blen + conic_height)
        drill = self.RevolveZ(fm.GetFace())
        obj = obj.common(drill)
        return Part.Solid(obj)

    @staticmethod
    def RevolveZ(profile: Part.Shape, angle=360) -> Part.Shape:
        """Returns the revolution of {profile} around the Z-axis,
        through an included angle of {angle} degrees
        """
        return profile.revolve(Base.Vector(0, 0, 0), Base.Vector(0, 0, 1), angle)

    @staticmethod
    def makeHexPrism(width: float, height: float) -> Part.Shape:
        """create a regular hexagonal prism
        Parameters:
        - width: width across flats.
          (the cross-corner width is width * 2 / sqrt(3))
        - height: overall height of the prism
        """
        # create hexagon face
        mhex = Base.Matrix()
        mhex.rotateZ(math.radians(60.0))
        polygon = []
        vhex = Base.Vector(width / math.sqrt(3.0), 0.0, 0.0)
        for i in range(6):
            polygon.append(vhex)
            vhex = mhex.multiply(vhex)
        polygon.append(vhex)
        hexagon = Part.makePolygon(polygon)
        hexagon = Part.Face(hexagon)
        # Extrude in z to create the final shape
        solid = hexagon.extrude(Base.Vector(0.0, 0.0, height))
        return solid

    @classmethod
    def makeHCrossRecess(cls, CrossType: str, m: float) -> Part.Shape:
        """Create a Cross recess of type H.
        Oriented in the Z direction , with outer diameter m at Z=0.
        Parameters:
        - CrossType: "0", "1", "2", "3", and "4" are supported.
        - m: Functional outer diameter of the recess.
             This also affects the overall height of the resulting shape.
        """
        b, e_mean, g, f_mean, r, t1, alpha, beta = FsData["iso4757def"][CrossType]

        rad265 = math.radians(26.5)
        rad28 = math.radians(28.0)
        tg = (m - g) / 2.0 / math.tan(rad265)  # depth at radius of g
        t_tot = tg + g / 2.0 * math.tan(rad28)  # total depth

        hm = m / 4.0
        hmc = m / 2.0
        rmax = m / 2.0 + hm * math.tan(rad265)

        fm = FSFaceMaker()
        fm.AddPoints((0.0, hm), (rmax, hm), (g / 2.0, -tg), (0.0, -t_tot))
        aFace = fm.GetFace()
        cross = cls.RevolveZ(aFace)

        # we need to cut 4 corners out of the above shape.
        # Definition of corner:
        # The angles 92 degrees and alpha are defined on a plane which has
        # an angle of beta against our coordinate system.
        # The projected angles are needed for easier calculation!
        rad_alpha = math.radians(alpha / 2.0)
        rad92 = math.radians(92.0 / 2.0)
        rad_beta = math.radians(beta)

        rad_alpha_p = math.atan(math.tan(rad_alpha) / math.cos(rad_beta))
        rad92_p = math.atan(math.tan(rad92) / math.cos(rad_beta))

        tb = tg + (g - b) / 2.0 * math.tan(rad28)  # depth at dimension b
        # radius of b-corner at hm
        rbtop = b / 2.0 + (hmc + tb) * math.tan(rad_beta)
        # radius of b-corner at t_tot
        rbtot = b / 2.0 - (t_tot - tb) * math.tan(rad_beta)

        # delta between corner b and corner e in x direction
        dre = e_mean / 2.0 / math.tan(rad_alpha_p)

        dx = m / 2.0 * math.cos(rad92_p)
        dy = m / 2.0 * math.sin(rad92_p)

        PntC0 = Base.Vector(rbtop, 0.0, hmc)
        PntC1 = Base.Vector(rbtot, 0.0, -t_tot)
        PntC3 = Base.Vector(rbtot + dre, +e_mean / 2.0, -t_tot)
        PntC5 = Base.Vector(rbtot + dre, -e_mean / 2.0, -t_tot)
        PntC7 = Base.Vector(rbtot + dre + 2.0 * dx, +e_mean + 2.0 * dy, -t_tot)
        PntC9 = Base.Vector(rbtot + dre + 2.0 * dx, -e_mean - 2.0 * dy, -t_tot)

        wire_t_tot = Part.makePolygon(
            [PntC1, PntC3, PntC7, PntC9, PntC5, PntC1])
        edgeC1 = Part.makeLine(PntC0, PntC1)
        makeSolid = True
        isFrenet = False
        corner = Part.Wire(edgeC1).makePipeShell(
            [wire_t_tot], makeSolid, isFrenet)
        for i in range(4):
            cross = cross.cut(
                corner.rotated(
                    Base.Vector(0, 0, 0),
                    Base.Vector(0, 0, 1),
                    90 * i
                )
            )
        return Part.Solid(cross)

    @classmethod
    def makeHexRecess(cls, width: float, depth: float, chamfer: bool) -> Part.Shape:
        """create a standard internal hexagonal driving feature (or 'Allen' recess)
        Parameters:
        - width: dimension across flats of the recess shape.
        - depth: usable depth of the recess. the returned shape has a larger overall
          height due to a tapered point at the bottom
        - chamfer: if True, a 45 degree chamfer is added at the top part of the shape
        """
        prism = cls.makeHexPrism(width, 3.0 * depth)
        prism.rotate(Base.Vector(0.0, 0.0, depth / 2), Base.Vector(1.0, 0.0, 0.0), 180)
        cone1 = Part.makeCone(
            (3 * depth + width) / math.sqrt(3) + depth * math.sqrt(3),
            width * 0.08,
            2 * depth + width / 3 - 0.08 * width * math.sqrt(3) / 3,
            Base.Vector(0.0, 0.0, depth),
            Base.Vector(0.0, 0.0, -1.0),
            360
        )
        recess = prism.common(cone1)
        if chamfer:
            r_3 = width * 0.49
            r_2 = 1.005 * width / math.sqrt(3)
            r_1 = depth / math.tan(math.radians(45)) + r_2
            h_1 = math.tan(math.radians(45)) * (r_2 - r_3)
            cone2 = Part.makeCone(
                r_1,
                r_3,
                depth + h_1,
                Base.Vector(0.0, 0.0, depth),
                Base.Vector(0.0, 0.0, -1.0),
                360
            )
            recess = recess.fuse(cone2)
        return Part.Solid(recess)

    @staticmethod
    def makeHexalobularRecess(
        drive_size: str, depth: float, chamfer: bool
    ) -> Part.Shape:
        """create an ISO 10664 Hexalobular internal driving feature for bolts and screws
        Parameters:
        - drive_size: e.g: "T20", "T100", etc.
        - depth: usable depth of the recess. the returned shape has a larger overall
          height due to a tapered point at the bottom
        - chamfer: if True, a chamfer is added at the top part of the shape
        """
        A, B, Re = FsData["iso10664def"][drive_size]
        sqrt_3 = math.sqrt(3.0)
        Ri = -((B + sqrt_3 * (2. * Re - A)) * B + (A - 4. * Re) * A) / \
            (4. * B - 2. * sqrt_3 * A + (4. * sqrt_3 - 8.) * Re)
        beta = math.acos(A / (4 * Ri + 4 * Re) - (2 * Re) /
                        (4 * Ri + 4 * Re)) - math.pi / 6
        Re_x = A / 2.0 - Re + Re * math.sin(beta)
        Re_y = Re * math.cos(beta)
        Ri_y = B / 4.0
        Ri_x = sqrt_3 * B / 4.0
        mhex = Base.Matrix()
        mhex.rotateZ(math.radians(60.0))
        hexlobWireList = []

        PntRe0 = Base.Vector(Re_x, -Re_y, depth)
        PntRe1 = Base.Vector(A / 2.0, 0.0, depth)
        PntRe2 = Base.Vector(Re_x, Re_y, depth)
        edge0 = Part.Arc(PntRe0, PntRe1, PntRe2).toShape()
        hexlobWireList.append(edge0)

        PntRi = Base.Vector(Ri_x, Ri_y, depth)
        PntRi2 = mhex.multiply(PntRe0)
        edge1 = Part.Arc(PntRe2, PntRi, PntRi2).toShape()
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

        face = Part.Face(hexlobWire)

        # Extrude in z to create the cutting tool for the screw-head-face
        prism = face.extrude(Base.Vector(0.0, 0.0, -3 * depth))
        # add chamfers to surfaces
        width = sqrt_3 * A / 2
        cone1 = Part.makeCone(
            (3 * depth + width) / sqrt_3 + depth * sqrt_3,
            width * 0.08,
            2 * depth + width / 3 - 0.08 * width * sqrt_3 / 3,
            Base.Vector(0.0, 0.0, depth),
            Base.Vector(0.0, 0.0, -1.0),
            360
        )
        recess = prism.common(cone1)
        if chamfer:
            # 18 degree chamfer at top of recess cutter
            cone2 = Part.makeCone(
                0.505 * A + depth / math.tan(math.radians(18)),
                0.49 * B,
                depth + (0.505 * A - 0.49 * B) * math.tan(math.radians(18)),
                Base.Vector(0.0, 0.0, depth),
                Base.Vector(0.0, 0.0, -1.0),
                360
            )
            recess = recess.fuse(cone2).removeSplitter()
        return Part.Solid(recess)

    @staticmethod
    def makeSlotRecess(width: float, depth: float, head_diameter: float) -> Part.Shape:
        """Create a Cutting tool to add a slot driving feature to a screw head
        Parameters:
        - width: the width of the slot
        - depth: slot depth - the returned shape extends by this amount below Z=0
        - head_diameter: the head diameter of the specified screw
        """
        shape = Part.makeBox(
            head_diameter + 10,
            width,
            depth * 2,
            Base.Vector(-(head_diameter + 10) / 2, -width / 2, -depth)
        )
        return shape

    def getDia(self, ThreadDiam: str, isNut: bool) -> float:
        """returns a numerical diameter given a value in string format
        Parameters:
        - ThreadDiam: e.g: "1/4in" or "#6" or "M6" or "ST 6.3"
        - isNut: if true, calculates the diameter for an internal thread,
          as would be found on a standard hex-nut

        This function takes into account the 3D-print compensation settings
        of the instance, if they are enabled. for example, if:
          self.smNutThrScaleA = 1.1
          self.smNutThrScaleB = 0.05
        then:
          self.getDia("M6", True) == 6.65  # 6 * 1.1 + 0.05
        """
        if isinstance(ThreadDiam, str):
            threadstring = ThreadDiam.strip("()")
            dia = FsData["DiaList"][threadstring][0]
        else:
            dia = ThreadDiam
        if self.sm3DPrintMode:
            if isNut:
                dia = self.smNutThrScaleA * dia + self.smNutThrScaleB
            else:
                dia = self.smScrewThrScaleA * dia + self.smScrewThrScaleB
        return dia

    # NOTE:
    # - On ISO 724 is presemted a table with the cooresponding minor
    #   and pitch diameters (d_1, d_2) for a given pair of major diameter and
    #   pitch (D, P), getDia1() amd getDia2() implement that correspondance.
    # - On ISO 262 is presented tha available pitches for a given diameter.
    # - On ISO 965-1 is presented the tolerances for metric screw thread.
    def getDia1(self, D: float, P: float) -> float:
        """Returns the basic minor diameter of metric thread according to ISO 68-1
        d_1 = D - 2 * 5/8 * H
        Parameters:
        - D: major diameter
        - P: pitch
        """
        H_5_8 = FsData["ISO68-1def"][str(P)][1]
        return D - 2 * H_5_8

    def getDia2(self, D: float, P: float) -> float:
        """Returns the basic pitch diameter of metric thread according to ISO 68-1
        d_2 = D - 2 * 3/8 * H
        Parameters:
        - D: major diameter
        - P: pitch
        """
        H_3_8 = FsData["ISO68-1def"][str(P)][2]
        return D - 2 * H_3_8

    def getLength(self, LenStr: str) -> float:
        """Convert a length string to a corresponding numeric value."""
        # washers and nuts pass an int (1), for their unused length attribute
        # handle this circumstance if necessary
        if isinstance(LenStr, int):
            return LenStr
        # otherwise convert the string to a number using predefined rules
        if "in" not in LenStr:
            LenFloat = float(LenStr.strip("()"))
        else:
            components = LenStr.strip("in").split(" ")
            total = 0
            for item in components:
                if "/" in item:
                    subcmpts = item.split("/")
                    total += float(subcmpts[0]) / float(subcmpts[1])
                else:
                    total += float(item)
            LenFloat = total * 25.4
        return LenFloat

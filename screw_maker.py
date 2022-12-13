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

DEBUG = False  # set to True to show debug messages; does not work, still todo.

# some common constants
sqrt3 = math.sqrt(3)
cos30 = math.cos(math.radians(30))


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

        if (fastenerAttribs.diameter == "Custom"):
            fastenerAttribs.dimTable = None
        else:
            fastenerAttribs.dimTable = FsData[fastenerAttribs.type +
                                              "def"][fastenerAttribs.diameter]
        self.leftHanded = fastenerAttribs.leftHanded
        # self.fastenerLen = l
        # fa.type = ST_text
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
                "No suitable function for " + fastenerAttribs.type + " Screw Type!\n")
            return None
        # Part.show(screw)
        return screw

    # DIN 7998 Wood Thread
    # zs: z position of start of the threaded part
    # ze: z position of end of the flat portion of screw (just where the tip starts)
    # zt: z position of screw tip
    # ro: outer radius
    # ri: inner radius
    # p:  thread pitch
    def makeDin7998Thread(self, zs, ze, zt, ri, ro, p):
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

        # create helix for tip thread part
        numTurns = math.floor(tipH / p)
        # Part.show(hlx)
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
            # Part.show(tip_solid)
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
            # Part.show(body_solid)
        else:
            raise RuntimeError("Failed to create woodscrew body thread")

        thread_solid = body_solid.fuse(tip_solid)
        # rotate the thread solid to prevent OCC errors due to cylinder seams aligning
        thread_solid.rotate(Base.Vector(0, 0, 0), Base.Vector(0, 0, 1), 180)
        #Part.show(thread_solid, "thread_solid")
        return thread_solid

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
        circ = Part.makeCircle(
            cir_hex / 2.0, Base.Vector(0.0, 0.0, -k_hex * 0.1))
        circ = Part.Face(Part.Wire(circ))

        # Create the face with the circle as outline and the hexagon as hole
        face = circ.cut(hexagon)

        # Extrude in z to create the final cutting tool
        exHex = face.extrude(Base.Vector(0.0, 0.0, k_hex * 1.2))
        # Part.show(exHex)
        return exHex

    def GetInnerThreadMinDiameter(self, dia, P, addEpsilon=0.001):
        H = P * cos30  # Thread depth H
        return dia - H * 5.0 / 4.0 + addEpsilon

    def CreateInnerThreadCutter(self, dia, P, blen):
        H = P * cos30  # Thread depth H
        r = dia / 2.0

        # make just one turn, length is identical to pitch
        helix = Part.makeLongHelix(
            P, blen, r, 0, self.leftHanded
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

    def CreateThreadCutter(self, dia, P, blen):
        # make a cylindrical solid, then cut the thread profile from it
        H = math.sqrt(3) / 2 * P
        # move the very bottom of the base up a tiny amount
        # prevents some too-small edges from being created
        trotations = blen // P + 1

        # create a sketch profile of the thread
        # ref: https://en.wikipedia.org/wiki/ISO_metric_screw_thread
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
        main_helix = Part.makeLongHelix(
            P, helix_height, dia / 2, 0, self.leftHanded)
        lead_out_helix = Part.makeLongHelix(
            P, P / 2, dia / 2 + 0.5 * (5 / 8 * H + 0.5 * fillet_r), 0, self.leftHanded)
        main_helix.rotate(Base.Vector(0, 0, 0), Base.Vector(1, 0, 0), 180)
        lead_out_helix.translate(Base.Vector(
            0.5 * (-1 * (5 / 8 * H + 0.5 * fillet_r)), 0, 0))
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
        return sweep.shape()

    def CreateBlindInnerThreadCutter(self, dia: float, P: float, blen: float):
        """create a blind inner thread cutter,
        for use with a boolean cut operation.

        the solid is oriented z-up and placed at the origin.

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

    def RevolveZ(self, profile, angle=360):
        return profile.revolve(Base.Vector(0, 0, 0), Base.Vector(0, 0, 1), angle)

    def makeShellthread(self, dia, P, blen, withcham, ztop, tlen=-1):
        """
        Construct a 60 degree screw thread with diameter dia,
        pitch P. 
        blen is the length of the shell body.
        tlen is the length of the threaded part (-1 = same as body length).
        if withcham == True, the end of the thread is nicely chamfered.
        The thread is constructed z-up, as a shell, with the top circular
        face removed. The top of the shell is centered @ (0, 0, ztop)
        """
        correction = 1e-5
        if tlen < 0:
            tlen = blen
        dia2 = dia / 2
        corr_blen = blen - correction

        # create base body
        pnt0 = (dia2, 0)
        pnt1 = (dia2,  -blen + P / 2)
        pnt2 = (dia2 - P / 2, -corr_blen)
        pnt3 = (0, -corr_blen)
        pnt4 = (0, 0)
        pnt5 = (dia2, -corr_blen)
        fm = FastenerBase.FSFaceMaker()
        fm.AddPoints(pnt0)
        if withcham:
            fm.AddPoints(pnt1, pnt2)
        else:
            fm.AddPoints(pnt5)
        fm.AddPoints(pnt3, pnt4)

        base_profile = fm.GetClosedWire()
        base_shell = self.RevolveZ(base_profile)
        base_body = Part.makeSolid(base_shell)

        swept_solid = self.CreateThreadCutter(dia, P, blen)
        # translate swept path slightly for backwards compatibility
        toffset = blen - tlen + P / 2
        minoffset = 5 * P / 8
        if (toffset < minoffset):
            toffset = minoffset

        swept_solid.translate(Base.Vector(0, 0, -toffset))
        # perform the actual boolean operations
        base_body.rotate(Base.Vector(0, 0, 0), Base.Vector(0, 0, 1), 90)
        threaded_solid = base_body.cut(swept_solid)
        # remove top face(s) and convert to a shell
        result = Part.Shell([x for x in threaded_solid.Faces
                             if not abs(x.CenterOfMass[2]) < 1e-7])
        result.translate(Base.Vector(0, 0, ztop))
        return result

    # cross recess type H
    def makeCross_H3(self, CrossType='2', m=6.9, h=0.0):
        key, res = FastenerBase.FSGetKey("CrossRecess", CrossType, m, h)
        if res is not None:
            return res
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

        fm = FastenerBase.FSFaceMaker()
        fm.AddPoints((0.0, hm), (rmax, hm), (g / 2.0, -tg), (0.0, -t_tot))
        aWire = fm.GetWire()
        crossShell = self.RevolveZ(aWire)
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
        # radius of b-corner at hm
        rbtop = b / 2.0 + (hmc + tb) * math.tan(rad_beta)
        # radius of b-corner at t_tot
        rbtot = b / 2.0 - (t_tot - tb) * math.tan(rad_beta)

        # delta between corner b and corner e in x direction
        dre = e_mean / 2.0 / math.tan(rad_alpha_p)
        # FreeCAD.Console.PrintMessage("delta calculated: " + str(dre) + "\n")

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
        # Part.show(wire_t_tot)
        edgeC1 = Part.makeLine(PntC0, PntC1)
        # FreeCAD.Console.PrintMessage("edgeC1 with PntC9" + str(PntC9) + "\n")

        makeSolid = True
        isFrenet = False
        corner = Part.Wire(edgeC1).makePipeShell(
            [wire_t_tot], makeSolid, isFrenet)
        # Part.show(corner)

        rot_axis = Base.Vector(0., 0., 1.0)
        sin_res = math.sin(math.radians(90) / 2.0)
        cos_res = math.cos(math.radians(90) / 2.0)
        rot_axis.multiply(-sin_res)  # Calculation of Quaternion-Elements
        # FreeCAD.Console.PrintMessage("Quaternion-Elements" + str(cos_res) + "\n")

        pl_rot = FreeCAD.Placement()
        # Rotation-Quaternion 90° z-Axis
        pl_rot.Rotation = (rot_axis.x, rot_axis.y, rot_axis.z, cos_res)

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
            cutplace.Rotation = pl_rot.Rotation.multiply(
                corner.Placement.Rotation)
            corner.Placement = cutplace
            crossShell = crossShell.cut(corner)
            addPlace.Rotation = pl_rot.Rotation.multiply(
                cornerShell.Placement.Rotation)
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
        FastenerBase.FSCache[key] = (cross, crossShell0)
        return cross, crossShell0

    # Allen recess cutting tool
    # Parameters used: s_mean, k, t_min, dk
    def makeAllen2(self, s_a=3.0, t_a=1.5, h_a=2.0, t_2=0.0):
        # h_a  top height location of cutting tool
        # s_a hex width
        # t_a dept of the allen
        # t_2 depth of center-bore

        key, res = FastenerBase.FSGetKey("Allen2Tool", s_a, t_a, h_a, t_2)
        if res is not None:
            # reset placement should original objects were moved
            res[0].Placement = FreeCAD.Placement(
                FreeCAD.Vector(0, 0, h_a), FreeCAD.Rotation(0, 0, 0, 1))
            res[1].Placement = FreeCAD.Placement(
                FreeCAD.Vector(0, 0, h_a), FreeCAD.Rotation(0, 0, 0, 1))
            return res

        fm = FastenerBase.FSFaceMaker()
        if t_2 == 0.0:
            depth = s_a / 3.0
            e_cham = 2.0 * s_a / math.sqrt(3.0)
            # FreeCAD.Console.PrintMessage("allen tool: " + str(s_a) + "\n")

            # Points for an arc at the peak of the cone
            rCone = e_cham / 4.0
            hyp = (depth * math.sqrt(e_cham ** 2 /
                   depth ** 2 + 1.0) * rCone) / e_cham
            radAlpha = math.atan(e_cham / depth)
            radBeta = math.pi / 2.0 - radAlpha
            zrConeCenter = hyp - depth - t_a
            xArc1 = math.sin(radBeta) * rCone
            zArc1 = zrConeCenter - math.cos(radBeta) * rCone
            xArc2 = math.sin(radBeta / 2.0) * rCone
            zArc2 = zrConeCenter - math.cos(radBeta / 2.0) * rCone
            zArc3 = zrConeCenter - rCone

            # The round part of the cutting tool, we need for the allen hex recess
            fm.AddPoint(0.0, -t_a - depth - depth)
            fm.AddPoint(e_cham, -t_a - depth - depth)
            fm.AddPoint(e_cham, -t_a + depth)
            fm.AddPoint(xArc1, zArc1)
            fm.AddArc(xArc2, zArc2, 0.0, zArc3)
            hex_depth = -1.0 - t_a - depth * 1.1
        else:
            e_cham = 2.0 * s_a / math.sqrt(3.0)
            d_cent = s_a / 3.0
            depth_cent = d_cent * math.tan(math.pi / 6.0)
            depth_cham = (e_cham - d_cent) * math.tan(math.pi / 6.0)

            fm.AddPoint(0.0, -t_2 - depth_cent)
            fm.AddPoint(0.0, -t_2 - depth_cent - depth_cent)
            fm.AddPoint(e_cham, -t_2 - depth_cent - depth_cent)
            fm.AddPoint(e_cham, -t_a + depth_cham)
            fm.AddPoint(d_cent, -t_a)
            fm.AddPoint(d_cent, -t_2)
            hex_depth = -1.0 - t_2 - depth_cent * 1.1

        hFace = fm.GetFace()
        roundtool = self.RevolveZ(hFace)

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

        FastenerBase.FSCache[key] = (solidHex, allenShell)
        return solidHex, allenShell

    # ISO 10664 Hexalobular internal driving feature for bolts and screws
    def makeIso10664_3(self, RType='T20', t_hl=3.0, h_hl=0):
        # t_hl depth of the recess
        # h_hl top height location of Cutting tool

        key, res = FastenerBase.FSGetKey("HexalobularTool", RType, t_hl, h_hl)
        if res is not None:
            return res

        A, B, Re = FsData["iso10664def"][RType]
        sqrt_3 = math.sqrt(3.0)
        depth = A / 4.0
        offSet = 1.0

        # Chamfer cutter for the hexalobular recess
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

        fm = FastenerBase.FSFaceMaker()
        fm.AddPoint(0.0, -t_hl - depth - 1.0)
        fm.AddPoint(A, -t_hl - depth - 1.0)
        fm.AddPoint(A, -t_hl + depth)
        fm.AddPoint(xArc1, zArc1)
        fm.AddArc(xArc2, zArc2, 0.0, zArc3)

        hFace = fm.GetFace()
        cutTool = self.RevolveZ(hFace)

        Ri = -((B + sqrt_3 * (2. * Re - A)) * B + (A - 4. * Re) * A) / \
            (4. * B - 2. * sqrt_3 * A + (4. * sqrt_3 - 8.) * Re)
        # print '2nd  Ri last solution: ', Ri
        beta = math.acos(A / (4 * Ri + 4 * Re) - (2 * Re) /
                         (4 * Ri + 4 * Re)) - math.pi / 6
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

        FastenerBase.FSCache[key] = (Helo, hexlobShell)
        return Helo, hexlobShell

    def getDia(self, ThreadDiam, isNut):
        if type(ThreadDiam) == type(""):
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

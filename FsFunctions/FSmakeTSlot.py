# -*- coding: utf-8 -*-
"""
***************************************************************************
*   Copyright (c) 2022, 2023                                              *
*   Original code by:                                                     *
*   hasecilu <hasecilu[at]tuta.io>                                        *
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
import math
import Part
from FreeCAD import Base
import FastenerBase
from screw_maker import FsData, sqrt2, sqrt3

def makeBaseBody(a, e1, e2, f, h, k):
    """ T-Slot points, transversal cut """
    fm = FastenerBase.FSFaceMaker()
    fm.AddPoint(0.0, 0.0)
    fm.AddPoint(a / 2, 0.0)
    fm.AddPoint(a / 2, -h + k)
    fm.AddPoint(e2 / 2, -h + k)
    fm.AddPoint(e2 / 2, -h + f)
    fm.AddPoint(e2 / 2 - f, -h)
    fm.AddPoint(0, -h)
    # half face on +X semiaxis
    halfFace = fm.GetFace()
    # translate to plane y = -e1 / 2 to extrude up to y = e1 / 2
    halfFace.translate(Base.Vector(0.0, -e1 / 2, 0.0))

    solid = halfFace.extrude(Base.Vector(0.0, e1, 0.0))
    solid = solid.fuse(
        solid.mirror(
            Base.Vector(0, 0, 0),
            Base.Vector(1, 0, 0)
        )
    ).removeSplitter()
    return solid

def cutCorners(fastener, radio, depth):
    """
    Cut corners on upper face to enable turn,
    delimited by 2 perpendicular rects and a quarter circunference
    """
    p0 = Base.Vector(0.0, -radio, 0.0)
    p1= Base.Vector(radio, -radio, 0.0)
    p2 = Base.Vector(radio, 0.0, 0.0)
    x = radio * (sqrt2 / 2)
    p3 = Base.Vector(x, -x, 0.0)

    edge0 = Part.makeLine(p0, p1)
    edge1 = Part.makeLine(p1, p2)
    curve = Part.Arc(p2, p3, p0).toShape()

    aWire = Part.Wire([edge0, edge1, curve])
    aFace = Part.Face(aWire)
    corner = aFace.extrude(Base.Vector(0.0, 0.0, -depth))
    # Part.show(corner) # See profile
    fastener = fastener.cut(corner).removeSplitter()

    myMat = Base.Matrix()
    myMat.rotateZ(math.pi)
    corner.transformShape(myMat)
    fastener = fastener.cut(corner).removeSplitter()

    return fastener

def makeHole(self, fastener, fa, dia, h, P):
    """ Hole with chamfer """
    da = 1.05 * dia
    inner_rad = dia / 2 - P * 0.625 * sqrt3 / 2
    inner_cham_ht = math.tan(math.radians(15)) * (da / 2 - inner_rad)
    fm = FastenerBase.FSFaceMaker()
    fm.AddPoint(0.0, 0.0)
    fm.AddPoint(da / 2, 0.0)
    fm.AddPoint(inner_rad, -inner_cham_ht)
    fm.AddPoint(inner_rad, -h + inner_cham_ht)
    fm.AddPoint(da / 2, -h)
    fm.AddPoint(0.0, -h)
    hole = self.RevolveZ(fm.GetFace())
    fastener = fastener.cut(hole)
    if fa.thread:
        thread_cutter = self.CreateInnerThreadCutter(dia, P, h + P)
        thread_cutter.rotate(
            Base.Vector(0.0, 0.0, 0.0), Base.Vector(1.0, 0.0, 0.0), 180
        )
        fastener = fastener.cut(thread_cutter)

    return fastener

def makeTSlot(self, fa):  # dynamically loaded method of class Screw
    """
    Creates fasteners suited for T-Slot Aluminum profiles or steel tabletops.
    Supported types:
    - ISO 299:  T-slots and corresponding bolts; (ISO 299 = DIN 508)
    - DIN 508:  T-Slot nut for tabletops, don't fit Aluminum profiles
    - GN 505:   Serrated Quarter-Turn T-Slot Nuts
    - GN 505.4: Serrated T-Slot Bolts
    - GN 506:   T-Slot nut to swivel in for Aluminum Profiles
    - GN 507:   T-Slot sliding nut for Aluminum Profiles
    """
    d = fa.calc_diam # String value, ex: M6
    if fa.baseType == "GN505.4":
        dia = self.getDia(fa.calc_diam, False) # Converted numeric value
    else:
        dia = self.getDia(fa.calc_diam, True) # Converted numeric value
    P = FsData["ISO262def"][fa.diameter][0]

    # NOTE: - All dimensions depend on the slot width NOT in the diameter
    # with exception of the pitch and that's why the data files are a mess.
    # - The slot width of fasteners made for Aluminum profiles are denoted
    # as: "20 series", "30 series", "40 series", "45 series" and the ones
    # that are not are denoted with their dimension: "6 mm", "8 mm", "10 mm" etc.
    sWidth = fa.slotWidth
    i = FastenerBase.FsTitles[fa.baseType + "slotwidths"].index(sWidth)
    a = FsData[fa.baseType + "slotwidths"][d][i]

    if fa.baseType == "DIN508":
        e1 = FsData[fa.baseType + "e"][d][i]
        e2 = e1
        f = FsData[fa.baseType + "f"][d][i]
        h = FsData[fa.baseType + "h"][d][i]
        k = FsData[fa.baseType + "k"][d][i]

        fastener = makeBaseBody(a, e1, e2, f, h, k)
        return makeHole(self, fastener, fa, dia, h, P)

    if fa.baseType[:5] == "GN505":
        e1 = FsData[fa.baseType + "e1"][d][i]
        e2 = FsData[fa.baseType + "e2"][d][i]
        h = FsData[fa.baseType + "h"][d][i]
        k = FsData[fa.baseType + "k"][d][i]
        f = 0.125 * e2  # constant calculated with official GN step file

        # Bolt and nut share geometries

        if fa.thread:
            k = k - 0.05 * e1 # Take into account strips height

        fastener = makeBaseBody(a, e1, e2, f, h, k)
        # Cut corners in the upper face to enable rotation on slot
        # a = e1
        fastener = cutCorners(fastener, a/2, h-k)
        # Cut corners from the middle face
        fastener = cutCorners(fastener, e2 / 2, h)

        if fa.thread:
            # Add strips
            p0 = Base.Vector(-e2 / 2, e1 / 2, -h + k)
            p1 = Base.Vector(-e2 / 2, (e1 / 2) - 0.1 * e1, -h + k)
            p2 = Base.Vector(-e2 / 2, (e1 / 2) - 0.05 * e1, -h + k + 0.05 * e1)

            edge0 = Part.makeLine(p0, p1)
            edge1 = Part.makeLine(p1, p2)
            edge2 = Part.makeLine(p2, p0)

            aWire = Part.Wire([edge0, edge1, edge2])
            aFace = Part.Face(aWire)
            strip = aFace.extrude(Base.Vector(e2, 0.0, 0.0))
            fastener = fastener.fuse(strip).removeSplitter()
            for _ in range(9):
                myMat = Base.Matrix()
                strip.translate(Base.Vector(0, -0.1 * e1, 0))
                fastener = fastener.fuse(strip).removeSplitter()

        # Draw a triangle on x = e2 / 2
        # to cut opposite corners on the bottom
        fm = FastenerBase.FSFaceMaker()
        fm.AddPoint((e2 / 2) - f, -h)
        fm.AddPoint(e2 / 2, -h)
        fm.AddPoint(e2 / 2, -h + f )
        qring = self.RevolveZ(fm.GetFace(), angle=-90)
        fastener = fastener.cut(qring) # first corner

        myMat = Base.Matrix()
        myMat.rotateZ(math.pi)
        qring.transformShape(myMat)
        fastener = fastener.cut(qring) # second corner

        if fa.baseType == "GN505":
            fastener = makeHole(self, fastener, fa, dia, h, P)
        elif fa.baseType == "GN505.4":
            length = fa.calc_len

            # We have to rotate the fastener because
            # the thread should be down
            myMat = Base.Matrix()
            myMat.rotateX(math.pi)
            fastener = fastener.transformShape(myMat)

            fm = FastenerBase.FSFaceMaker()
            fm.AddPoint(0.0, 0.0)
            fm.AddPoint(dia / 2 + 0.02 * dia, 0.0)
            fm.AddArc2(0.0, -0.02 * dia, 90)
            fm.AddPoint(dia / 2, -length + dia / 10)
            fm.AddPoint(dia * 4 / 10, -length)
            fm.AddPoint(0.0, -length)
            L = self.RevolveZ(fm.GetFace()) # body
            fastener = fastener.fuse(L)

            thread_length = length
            if fa.thread:
                thread_cutter = self.CreateBlindThreadCutter(dia, P, thread_length)
                fastener = fastener.cut(thread_cutter)

        return fastener

    # TODO: Add new sizes
    # The current data is from Elesa+Ganter
    # there are other sizes in the market but
    # the dimensions data is not complete.
    # Buy and measure.
    if fa.baseType == "GN506":
        d2 = FsData[fa.baseType + "d2"][d][i]
        e1 = FsData[fa.baseType + "e1"][d][i]
        e2 = FsData[fa.baseType + "e2"][d][i]
        h1 = FsData[fa.baseType + "h1"][d][i]
        h2 = FsData[fa.baseType + "h2"][d][i]
        h3 = FsData[fa.baseType + "h3"][d][i]
        m = FsData[fa.baseType + "m"][d][i]

        fm = FastenerBase.FSFaceMaker()
        fm.AddPoint(0.0, 0.0)
        fm.AddPoint(a / 2, 0.0)
        fm.AddPoint(a / 2, -h3)
        fm.AddPoint(e2 / 2, -h3)
        fm.AddBSpline(e2 / 2, -h3 - (h1-h3) / 4, e2 / 4, -h1, 0, -h1)
        # half face on +X semiaxis
        halfFace = fm.GetFace()
        # translate to plane y = -m to extrude e1 units
        halfFace.translate(Base.Vector(0.0, -m, 0.0))

        fastener = halfFace.extrude(Base.Vector(0.0, e1, 0.0))
        fastener = fastener.fuse(
            fastener.mirror(
                Base.Vector(0, 0, 0),
                Base.Vector(1, 0, 0)
            )
        ).removeSplitter()

        s = FastenerBase.FSFaceMaker()
        s.AddPoint(0.0, d2 / 2)
        s.AddArc(d2 / 2, 0.0, 0.0, -d2 / 2)
        sph = self.RevolveZ(s.GetFace())
        sph.translate(Base.Vector(0.0, e1 - 2 * m, h2 - h1))

        fastener = fastener.fuse(sph)

        return makeHole(self, fastener, fa, dia, h1, P)

    if fa.baseType == "GN507":
        e1 = FsData[fa.baseType + "e1"][d][i]
        e2 = FsData[fa.baseType + "e2"][d][i]
        h = FsData[fa.baseType + "h"][d][i]
        k = FsData[fa.baseType + "k"][d][i]
        f = 0.125 * e2  # constant calculated with official GN step file
        fastener = makeBaseBody(a, e1, e2, f, h, k)
        return makeHole(self, fastener, fa, dia, h, P)

    raise NotImplementedError(f"Unknown fastener type: {fa.baseType}")

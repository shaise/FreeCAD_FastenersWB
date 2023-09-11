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
from screw_maker import *
import FastenerBase


def makeBaseBody(a, e1, e2, f, h, k):
    # T-Slot points, transversal cut
    fm = FastenerBase.FSFaceMaker()
    fm.AddPoint(e2 / 2 - f, -h)
    fm.AddPoint(e2 / 2, -h + f)
    fm.AddPoint(e2 / 2, -h + k)
    fm.AddPoint(a / 2, -h + k)
    fm.AddPoint(a / 2, 0.0)
    fm.AddPoint(-a / 2, 0.0)
    fm.AddPoint(-a / 2, -h + k)
    fm.AddPoint(-e2 / 2, -h + k)
    fm.AddPoint(-e2 / 2, -h + f)
    fm.AddPoint(-e2 / 2 + f, -h)
    face = fm.GetFace()
    # translate to plane y = -e1 / 2 to extrude up to y = e1 / 2
    face.translate(Base.Vector(0.0, -e1 / 2, 0.0))

    return face.extrude(Base.Vector(0.0, e1, 0.0))

# Cut corner delimited by 2 perpendicular rects and a quarter circunference
def cutCorner(fastener, radio, depth):
    sqrt2 = math.sqrt(2)
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
    fastener = fastener.cut(corner)

    myMat = Base.Matrix()
    myMat.rotateZ(math.pi)
    corner.transformShape(myMat)
    fastener = fastener.cut(corner)

    return fastener

def makeHole(self, fastener, fa, dia, h, P):
    # Hole with chamfer
    sqrt3 = math.sqrt(3)
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
    - DIN508 T-Slot nut for tabletops, don't fit Aluminum profiles
    - GN505 Serrated Quarter-Turn T-Slot Nuts
    - GN505.4 Serrated T-Slot Bolts
    - GN507 T-Slot nut for Aluminum Profiles
    """
    d = fa.calc_diam # String value, ex: M6
    dia = self.getDia(fa.calc_diam, True) # Converted numeric value

    # All dimensions depend on the slot width NOT in the diameter
    # with exception of the pitch
    swidth = fa.slotWidth # 8mm/10mm
    i = FastenerBase.FsTitles[fa.type + "slotwidths"].index(swidth)
    a = FsData[fa.type + "slotwidths"][d][i]
    h = FsData[fa.type + "h"][d][i]
    P = FsData[fa.type + "P"][d][i]

    if fa.type == "DIN508":
        e1 = FsData[fa.type + "e"][d][i]
        e2 = e1
        f = FsData[fa.type + "f"][d][i]
        k = FsData[fa.type + "k"][d][i]

        fastener = makeBaseBody(a, e1, e2, f, h, k)
        return makeHole(self, fastener, fa, dia, h, P)
    elif fa.type[:2] == "GN":
        e1 = FsData[fa.type + "e1"][d][i]
        e2 = FsData[fa.type + "e2"][d][i]
        k = FsData[fa.type + "k"][d][i]
        f = 0.125 * e2  # constant calculated with official GN step file

        if fa.type == "GN507":
            fastener = makeBaseBody(a, e1, e2, f, h, k)
            return makeHole(self, fastener, fa, dia, h, P)
        elif fa.type[:5] == "GN505":
            k = k - 0.05 * e1 # Take into account strips height

            fastener = makeBaseBody(a, e1, e2, f, h, k)

            # Cut corners in the upper face to enable rotation on slot
            # a = e1
            fastener = cutCorner(fastener, a/2, h-k)

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
            fastener = fastener.fuse(strip)
            for x in range(9):
                myMat = Base.Matrix()
                strip.translate(Base.Vector(0, -0.1 * e1, 0))
                fastener = fastener.fuse(strip)

            if fa.type == "GN505":
                fastener = makeHole(self, fastener, fa, dia, h, P)
            
            # Cut corners to allow free rotation
            # Cut corners in the middle face
            fastener = cutCorner(fastener, e2 / 2, h)
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

            if fa.type == "GN505.4":
                length = fa.calc_len

                # We have to rotate the fastener because 
                # the threa dshoul be down
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
    else:
        raise NotImplementedError(f"Unknown fastener type: {fa.type}")


# -*- coding: utf-8 -*-
"""
***************************************************************************
*   Copyright (c) 2013, 2014, 2015                                        *
*   Original code by:                                                     *
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
from screw_maker import *
import FastenerBase

# make T-Slot nut
# DIN508
# GN505
# GN507

# Cut corner delimited by 2 perpendicular rects and a quarter circunference
def cutCorner(nut, radio, depth):
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
    nut = nut.cut(corner)

    myMat = Base.Matrix()
    myMat.rotateZ(math.pi)
    corner.transformShape(myMat)
    nut = nut.cut(corner)

    return nut

def makeTSlotNut(self, fa):  # dynamically loaded method of class Screw
    SType = fa.type
    d = fa.calc_diam # String value, ex: M6
    dia = self.getDia(fa.calc_diam, True) # Converted numeric value

    if SType[:3] == "DIN":
        # a, e_max, f, h, k_max, P
        a, e, f, h, k, P = fa.dimTable
        e1 = e  # e1 is depth, y plane
        e2 = e  # e2 is width, x plane
    elif SType[:2] == "GN":
        # All dimensions depend on the slot width NOT in the diameter
        swidth = fa.slotWidth # 8mm/10mm
        i = FastenerBase.FsTitles[fa.type + "slotwidths"].index(swidth)

        a = FsData[fa.type + "slotwidths"][d][i]
        e1 = FsData[fa.type + "e1"][d][i]
        e2 = FsData[fa.type + "e2"][d][i]
        h = FsData[fa.type + "h"][d][i]
        k = FsData[fa.type + "k"][d][i]
        if SType == "GN505":
            k = k - 0.05 * e1 # Take into account strips height
        P = FsData[fa.type + "P"][d][i]

        # f is the horizontal component of the chamfer
        f = 0.125 * e2  # constant calculated with official GN step file

    # T-Slot nut Points, transversal cut
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
    nut = face.extrude(Base.Vector(0.0, e1, 0.0))

    if SType == "GN505":
        # Cut corners in the upper face to enable rotation on slot
        # a = e1
        nut = cutCorner(nut, a/2, h-k)
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
        nut = nut.fuse(strip)
        for x in range(9):
            myMat = Base.Matrix()
            strip.translate(Base.Vector(0, -0.1 * e1, 0))
            nut = nut.fuse(strip)

    # Hole with chamfer
    sqrt3 = math.sqrt(3)
    da = 1.05 * dia
    inner_rad = dia / 2 - P * 0.625 * sqrt3 / 2
    inner_cham_ht = math.tan(math.radians(15)) * (da / 2 - inner_rad)
    fm.Reset()
    fm.AddPoint(0.0, 0.0)
    fm.AddPoint(da / 2, 0.0)
    fm.AddPoint(inner_rad, -inner_cham_ht)
    fm.AddPoint(inner_rad, -h + inner_cham_ht)
    fm.AddPoint(da / 2, -h)
    fm.AddPoint(0.0, -h)
    hole = self.RevolveZ(fm.GetFace())
    nut = nut.cut(hole)
    if fa.thread:
        thread_cutter = self.CreateInnerThreadCutter(dia, P, h + P)
        thread_cutter.rotate(
            Base.Vector(0.0, 0.0, 0.0), Base.Vector(1.0, 0.0, 0.0), 180
        )
        nut = nut.cut(thread_cutter)

    if SType == "GN505":
        # Cut corners in the middle face
        nut = cutCorner(nut, e2 / 2, h)
        # Draw a triangle on x = e2 / 2
        # to cut opposite corners on the bottom
        fm.Reset()
        fm.AddPoint((e2 / 2) - f, -h)
        fm.AddPoint(e2 / 2, -h)
        fm.AddPoint(e2 / 2, -h + f )
        qring = self.RevolveZ(fm.GetFace(), angle=-90)
        nut = nut.cut(qring)

        myMat = Base.Matrix()
        myMat.rotateZ(math.pi)
        qring.transformShape(myMat)
        nut = nut.cut(qring)

    return nut

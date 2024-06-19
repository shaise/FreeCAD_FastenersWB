# -*- coding: utf-8 -*-
"""
***************************************************************************
*   Copyright (c) 2024                                                    *
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
from screw_maker import FsData
from FastenerBase import FSFaceMaker


def makeThumbScrew(self, fa):
    """Create a thumb screw.

    Supported types:
    - DIN 464: Knurled thumb screws, high type
    - DIN 465: Knurled thumb screws
    - DIN 653: Flat knurled thumb screws
    """
    SType = fa.baseType
    length = fa.calc_len
    dia = self.getDia(fa.calc_diam, False)
    P = FsData["ISO262def"][fa.Diameter][0]
    if SType in ["DIN464", "DIN465"]:
        _, c, dk, _, _, ds, _, h, _, _, k, _, n, _, _, r, t, _, _, knurl = fa.dimTable
        kn0 = h - k
        kn = k
        # NOTE: The required undercut needed is "Gewindefreistich DIN 76 - A" Regelfall
        # roundness for P from 1 to 2 is 0.6 => rr = 0.6
        g = self.getDia1(dia, P)
        rr = 0.6
        f1 = 3 * P
        f2 = 4.5 * P
        fm = FSFaceMaker()
        fm.AddPoint(0.0, h)
        if fa.Diameter in ["M1", "M1.2", "M1.4", "M1.6", "M2"]:
            fm.AddPoint(dk / 2, h)
            fm.AddPoint(dk / 2, h - k)
        else:
            fm.AddPoint(dk / 2 - c, h)
            fm.AddPoint(dk / 2, h - c)
            fm.AddPoint(dk / 2, h - k + c)
            fm.AddPoint(dk / 2 - c, h - k)
        fm.AddPoint(ds / 2 + r, h - k)
        fm.AddArc2(0.0, -r, 90)
        fm.AddPoint(ds / 2, 0.0)
        fm.AddPoint(g / 2 + rr, 0.0)
        fm.AddArc2(0.0, -rr, 90)
        fm.AddPoint(g / 2, -f1)
        fm.AddPoint(dia / 2, -f2)
        fm.AddPoint(dia / 2, -length + dia / 10)
        fm.AddPoint(dia / 2 - dia / 10, -length)
        fm.AddPoint(0.0, -length)
        thread_dz = -f1
        thread_l = length - f1
    elif SType == "DIN653":
        _, c, dk, _, _, ds, _, e, k, _, r, knurl = fa.dimTable
        kn0 = e
        kn = k
        # NOTE: The required undercut needed is "Gewindefreistich DIN 76 - A" Regelfall
        g = self.getDia1(dia, P)
        rr = (dia - g) / 2  # 0.6 from table doesn't work
        f1 = 3 * P
        f2 = 4.5 * P
        fm = FSFaceMaker()
        # Head
        if fa.Diameter in ["M1", "M1.2", "M1.4", "M1.6", "M2"]:
            if fa.Diameter != "M2":
                kn0 = 0
                fm.AddPoint(0.0, k)
                fm.AddPoint(dk / 2, k)
                fm.AddPoint(dk / 2, 0)
            else:
                fm.AddPoint(0.0, k + e)
                fm.AddPoint(dk / 2, k + e)
                fm.AddPoint(dk / 2, e)
        else:
            fm.AddPoint(0.0, k + e)
            fm.AddPoint(dk / 2 - c, k + e)
            fm.AddPoint(dk / 2, k + e - c)
            fm.AddPoint(dk / 2, e + c)
            fm.AddPoint(dk / 2 - c, e)
        # Shoulder
        if fa.Diameter not in ["M1", "M1.2", "M1.4", "M1.6"]:
            fm.AddPoint(ds / 2 + r, e)
            fm.AddArc2(0.0, -r, 90)
            fm.AddPoint(ds / 2, 0.0)
        # Shaft
        if fa.Diameter in ["M1", "M1.2", "M1.4", "M1.6"]:
            fm.AddPoint(dia / 2 + r, 0.0)
            fm.AddArc2(0.0, -r, 90)
            fm.AddPoint(dia / 2, -length)
            fm.AddPoint(0.0, -length)
            thread_dz = 0
            thread_l = length
        else:
            fm.AddArc2(0.0, -rr, 90)
            fm.AddPoint(g / 2, -f1)
            fm.AddPoint(dia / 2, -f2)
            fm.AddPoint(dia / 2, -length + dia / 10)
            fm.AddPoint(dia / 2 - dia / 10, -length)
            fm.AddPoint(0.0, -length)
            thread_dz = -f1
            thread_l = length - f1
    else:
        raise NotImplementedError(f"Unknown fastener type: {fa.Type}")

    screw = self.RevolveZ(fm.GetFace())

    # Make recess
    if SType == "DIN465":
        recess = self.makeSlotRecess(n, t, dk)
        recess.translate(Base.Vector(0.0, 0.0, h))
        screw = screw.cut(recess)

    # produce a modelled knurling & thread if necessary
    if fa.Thread:
        knurling_cutter = straightCutter(dk, 0.975 * dk, kn0, kn)
        screw = screw.cut(knurling_cutter)
        thread_cutter = self.CreateThreadCutter(dia, P, thread_l)
        thread_cutter.translate(Base.Vector(0.0, 0.0, thread_dz))
        screw = screw.cut(thread_cutter)

    return screw


def straightCutter(outDia: float, inDia: float, zbase: float, height: float):
    """Cut a circular array of triangular prisms to obtain a straight knurling."""
    # TODO: Make Screw.CreateKnurlCutter() accepts straight knurling
    # Knurling should be DIN 82 RAA

    # create base triangle, angle is 90°
    d2 = outDia - inDia / 2.0
    y2 = d2 - inDia / 2.0
    p1 = Base.Vector(inDia / 2.0, 0, 0)
    p2 = Base.Vector(d2, y2, 0)
    p3 = Base.Vector(d2, -y2, 0)
    l1 = Part.makeLine(p1, p2)
    l2 = Part.makeLine(p2, p3)
    l3 = Part.makeLine(p3, p1)
    w = Part.Wire([l1, l2, l3])
    face = Part.Face(w)
    cutElement = face.extrude(Base.Vector(0.0, 0.0, height))
    cutElement.translate(Base.Vector(0.0, 0, zbase))

    # FIXME: Ideally the number of elements should be greater
    # to avoid having "gaps" between cuts. Good enough for now.
    cutElements = [cutElement]
    ang = math.atan(y2 / d2) * 114.6  # 2 * 180 / pi
    numCuts = int(360.0 / ang)
    elementAng = 360 / numCuts

    for i in range(1, numCuts):
        nextElement = cutElement.copy().rotate(
            Base.Vector(0, 0, 0), Base.Vector(0, 0, 1), i * elementAng
        )
        cutElements.append(nextElement)
    cutTool = Part.Compound(cutElements)
    return cutTool

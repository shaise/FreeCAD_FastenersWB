# -*- coding: utf-8 -*-
"""
***************************************************************************
*   Copyright (c) 2022                                                    *
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
from screw_maker import *


def makeWingNut(self, fa):
    """Creates an internally threaded nut with 'wings', used for
    hand-tightening.
    Supported types:
    - DIN 315 wing nuts
    - ASME B18.6.9 wing nuts, type A
    """
    if fa.baseType == "DIN315":
        P, d2, d3, e, m, g, h = fa.dimTable
        wing_r = g / 4
    elif fa.baseType == "ASMEB18.6.9A":
        TPI, A, B, C, D, E, G = fa.dimTable
        P = 1 / TPI * 25.4
        d2 = E * 25.4
        d3 = D * 25.4
        e = A * 25.4
        m = G * 25.4
        g = C * 25.4
        h = B * 25.4
        wing_r = g / 5
    else:
        raise NotImplementedError(f"Unknown fastener type: {fa.Type}")
    # create the main body of the nut
    fm = FSFaceMaker()
    fm.AddPoint(0.0, 0.0)
    fm.AddPoint(d2 / 2, 0.0)
    fm.AddPoint(d3 / 2, m)
    fm.AddPoint(0.0, m)
    shape = self.RevolveZ(fm.GetFace())
    shape = shape.makeFillet(P / 2, shape.Edges)
    # create the profile of one of the wings
    fm.Reset()
    fm.AddPoint(d2 / 4, g * 0.75)
    fm.AddPoint(d2 / 4 + (h - g * 0.75) * math.tan(math.radians(20)), h)
    fm.AddArc(0.375 * e, 0.95 * h, e / 2, 0.8 * h)
    fm.AddArc((d2 + e) / 4, 0.25 * h, d2 / 4, g / 4)
    wing = fm.GetFace().extrude(Base.Vector(0.0, g, 0.0))
    wing.translate(Base.Vector(0.0, -g / 2, 0.0))
    wing = wing.makeFillet(wing_r, wing.Edges)
    shape = shape.fuse(wing)
    wing.rotate(Base.Vector(0.0, 0.0, 0.0), Base.Vector(0.0, 0.0, 1.0), 180)
    shape = shape.fuse(wing)
    # cut the hole for the threads
    dia = self.getDia(fa.calc_diam, True)
    id = self.GetInnerThreadMinDiameter(dia, P, 0.0)
    bore_cham_ht = (dia * 1.05 - id) / 2 * math.tan(math.radians(30))
    fm.Reset()
    fm.AddPoint(0.0, 0.0)
    fm.AddPoint(dia / 2, 0.0)
    fm.AddPoint(id / 2, bore_cham_ht)
    fm.AddPoint(id / 2, m - bore_cham_ht)
    fm.AddPoint(dia / 2, m)
    fm.AddPoint(0.0, m)
    bore_cutter = self.RevolveZ(fm.GetFace())
    shape = shape.cut(bore_cutter)
    # add modeled threads if necessary
    if fa.Thread:
        thread_cutter = self.CreateInnerThreadCutter(dia, P, m + 2 * P)
        shape = shape.cut(thread_cutter)
    return shape

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


def makeCastleNut(self, fa):
    """Creates a castle or slotted nut.
    Supported types:
    - DIN 935 slotted & castle nuts
    - ASME B18.2.2 slotted nuts
    """
    if fa.baseType == "DIN935":
        if fa.calc_diam in ["M4", "M5", "M6", "M7", "M8", "M10"]:
            return _makeSlottedNut(self, fa)
        else:
            return _makeCastleNut(self, fa)
    elif fa.baseType == "ASMEB18.2.2.5":
        return _makeSlottedNut(self, fa)
    else:
        raise NotImplementedError(f"Unknown fastener type: {fa.baseType}")


def _makeCastleNut(self, fa):
    if fa.baseType == "DIN935":
        P, m, w, s, n, d_e_max, ns = fa.dimTable
    else:
        raise NotImplementedError(f"Unknown fastener type: {fa.baseType}")
    dia = self.getDia(fa.calc_diam, True)
    inner_rad = dia / 2 - P * 0.625 * math.sqrt(3) / 2
    outer_rad = 0.505 * dia
    inner_cham_ht = math.tan(math.radians(15)) * (outer_rad - inner_rad)
    # create the nut profile
    fm = FSFaceMaker()
    fm.AddPoint(inner_rad, m - inner_cham_ht)
    fm.AddPoint(outer_rad, m)
    fm.AddPoint(d_e_max / 2, m)
    # fm.AddPoint(s / 2, w)
    fil_r = (s - d_e_max) / (2 * (1 - math.cos(math.radians(60))))
    fil_h = fil_r * math.sin(math.radians(60))
    fm.AddPoint(d_e_max / 2, w + fil_h)
    fm.AddArc2(fil_r, 0.0, 60)
    fm.AddPoint(s / 2 + w * math.sqrt(3) / 2, w / 2)
    fm.AddPoint(s / 2, 0.0)
    fm.AddPoint(outer_rad, 0.0)
    fm.AddPoint(inner_rad, inner_cham_ht)
    shape = self.RevolveZ(fm.GetFace())
    shape = shape.common(self.makeHexPrism(s, m))
    # create the slot cutter profile
    fm.Reset()
    fm.AddPoint(-n / 2, m)
    fm.AddPoint(-n / 2, w + n / 2)
    fm.AddArc2(n / 2, 0.0, 180)
    fm.AddPoint(n / 2, m)
    slot_cutter = fm.GetFace().extrude(Base.Vector(0.0, 1.2 * s, 0))
    # translate the cutter slightly upward to avoid visual errors due to
    # surface intersections
    slot_cutter.translate(Base.Vector(0.0, -0.6 * s, 0.05 * P))
    for i in range(int(ns / 2)):
        slot_cutter.rotate(Base.Vector(0.0, 0.0, 0.0),
                           Base.Vector(0.0, 0.0, 1.0), 360 / ns)
        shape = shape.cut(slot_cutter)
    if fa.Thread:
        thread_cutter = self.CreateInnerThreadCutter(dia, P, m + P)
        shape = shape.cut(thread_cutter)
    return shape


def _makeSlottedNut(self, fa):
    if fa.baseType == "DIN935":
        P, m, w, s, n, d_e_max, ns = fa.dimTable
    elif fa.baseType == "ASMEB18.2.2.5":
        TPI,  F,  H,  T,  S = fa.dimTable
        P = 1 / TPI * 25.4
        m = 25.4 * H
        w = 25.4 * T
        s = 25.4 * F
        n = S * 25.4
        ns = 6
    else:
        raise NotImplementedError(f"Unknown fastener type: {fa.baseType}")
    dia = self.getDia(fa.calc_diam, True)
    inner_rad = dia / 2 - P * 0.625 * math.sqrt(3) / 2
    outer_rad = 0.505 * dia
    inner_cham_ht = math.tan(math.radians(15)) * (outer_rad - inner_rad)
    # create the nut profile
    fm = FSFaceMaker()
    fm.AddPoint(inner_rad, m - inner_cham_ht)
    fm.AddPoint(outer_rad, m)
    fm.AddPoint(s / 2, m)
    fm.AddPoint(s / 2 + m * math.sqrt(3) / 2, m / 2)
    fm.AddPoint(s / 2, 0.0)
    fm.AddPoint(outer_rad, 0.0)
    fm.AddPoint(inner_rad, inner_cham_ht)
    shape = self.RevolveZ(fm.GetFace())
    shape = shape.common(self.makeHexPrism(s, m))
    # create the slot cutter profile
    fm.Reset()
    fm.AddPoint(-n / 2, m)
    fm.AddPoint(-n / 2, w + n / 2)
    fm.AddArc2(n / 2, 0.0, 180)
    fm.AddPoint(n / 2, m)
    slot_cutter = fm.GetFace().extrude(Base.Vector(0.0, 1.2 * s, 0))
    slot_cutter.translate(Base.Vector(0.0, -0.6 * s, 0.0))
    for i in range(int(ns / 2)):
        slot_cutter.rotate(Base.Vector(0.0, 0.0, 0.0),
                           Base.Vector(0.0, 0.0, 1.0), 360 / ns)
        shape = shape.cut(slot_cutter)
    if fa.Thread:
        thread_cutter = self.CreateInnerThreadCutter(dia, P, m + P)
        shape = shape.cut(thread_cutter)
    return shape

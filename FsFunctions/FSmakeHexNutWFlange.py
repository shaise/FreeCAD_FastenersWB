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


def makeHexNutWFlange(self, fa):
    """Creates a hexagon nut with a flanged base.
    Supported types:
    - EN1661 nuts with flange
    - ASME B18.2.2 UNC flanged nuts
    - DIN6331 Hexagon nuts with collar height 1,5 d
    """

    match fa.baseType:
        case "EN1661" | "ASMEB18.2.2.12" | "ISO4161" | "ISO10663":
            return _makeHexNutWithTaperedFlange(self, fa)
        case "DIN6331":
            return _makeHexNutWithSquareFlange(self, fa)
        case _:
            raise NotImplementedError(f"Unknown fastener type: {fa.Type}")


def _makeHexNutWithTaperedFlange(self, fa):
    dia = self.getDia(fa.calc_diam, True)
    if fa.baseType == "EN1661":
        P, da, c, dc, _, _, m, _, _, s = fa.dimTable
        flange_edge_rounded = True
    elif fa.baseType == "ASMEB18.2.2.12":
        TPI, F, B, H, J, K = fa.dimTable
        P = 1 / TPI * 25.4
        s = F * 25.4
        dc = B * 25.4
        da = 1.05 * dia
        m = H * 25.4
        c = K * 25.4
        flange_edge_rounded = False
    elif fa.baseType in ["ISO4161", "ISO10663"]:
        (
            P,
            c_min,
            d_a_max,
            d_a_min,
            d_c_max,
            _,
            _,
            m_max,
            _,
            _,
            s_max,
            _,
            _,
        ) = fa.dimTable
        c = c_min
        da = (d_a_max + d_a_min) / 2
        dc = d_c_max
        m = m_max
        s = s_max
        flange_edge_rounded = True
    inner_rad = dia / 2 - P * 0.625 * sqrt3 / 2
    inner_cham_ht = math.tan(math.radians(15)) * (da / 2 - inner_rad)
    # create the body of the nut
    fm = FastenerBase.FSFaceMaker()
    fm.AddPoint(inner_rad, m - inner_cham_ht)
    fm.AddPoint(da / 2, m)
    fm.AddPoint(s / 2, m)
    fm.AddPoint(s / 2 + sqrt3 * m, 0)
    fm.AddPoint(da / 2, 0)
    fm.AddPoint(inner_rad, inner_cham_ht)
    nut_body = self.RevolveZ(fm.GetFace())
    # cut the hex flats with a boolean subtraction
    nut_body = nut_body.common(self.makeHexPrism(s, m))
    # add the flange with a boolean fuse
    fm.Reset()
    fm.AddPoint((da + s) / 4, 0.0)
    if flange_edge_rounded:
        fm.AddPoint((dc + sqrt3 * c) / 2, 0.0)
        fm.AddPoint((dc - c) / 2, 0.0)
        fm.AddArc2(0, c / 2, 150)
        fm.AddPoint(
            (da + s) / 4,
            sqrt3 / 3 * ((dc - c) / 2 + c / (4 - 2 * sqrt3) - (da + s) / 4),
        )
    else:
        fm.AddPoint(dc / 2, 0.0)
        fm.AddPoint(dc / 2, c)
        fm.AddPoint(
            (da + s) / 4, c + (dc / 2 - (da + s) / 4) * math.tan(math.radians(30))
        )
    face = fm.GetFace()
    flange = self.RevolveZ(face)
    nut_body = nut_body.fuse(flange).removeSplitter()

    if fa.Thread:
        thread_cutter = self.CreateInnerThreadCutter(dia, P, m + P)
        nut_body = nut_body.cut(thread_cutter)
    return nut_body


def _makeHexNutWithSquareFlange(self, fa):
    dia = self.getDia(fa.calc_diam, True)

    if fa.baseType == "DIN6331":
        P, a, d1, damin, damax, m, s = fa.dimTable

    da = (damax + damin) / 2.0
    tan30 = math.tan(math.radians(30.0))
    inner_rad = (dia - 1.0825 * P) / 2.0
    inner_chamfer_X = da / 2.0 - inner_rad
    inner_chamfer_Z = inner_chamfer_X * tan30
    outer_chamfer_X = (d1 - s) / 2.0
    outer_chamfer_Z = outer_chamfer_X * tan30

    fm = FastenerBase.FSFaceMaker()
    fm.AddPoint(0.0, -1.0)
    fm.AddPoint(inner_rad + inner_chamfer_X, -1.0)
    fm.AddPointRelative(0.0, 1.0)
    fm.AddPoint(inner_rad, inner_chamfer_Z)
    fm.AddPoint(inner_rad, m - inner_chamfer_Z)
    fm.AddPoint(inner_rad + inner_chamfer_X, m)
    fm.AddPoint(s / 2.0, m)
    fm.AddPoint(d1 / 2.0, m - outer_chamfer_Z)
    fm.AddPoint(d1 / 2.0, m + 1.0)
    fm.AddPoint(0.0, m + 1.0)

    import Part

    nut_body = self.makeHexPrism(s, m)
    collar = Part.makeCylinder(d1 / 2.0, a)
    cutoff_body = self.RevolveZ(fm.GetFace())
    nut_body = nut_body.fuse(collar)
    nut_body = nut_body.cut(cutoff_body).removeSplitter()

    if fa.Thread:
        thread_cutter = self.CreateInnerThreadCutter(dia, P, m + P)
        nut_body = nut_body.cut(thread_cutter)
    return nut_body

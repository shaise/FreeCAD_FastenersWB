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
    """
    dia = self.getDia(fa.calc_diam, True)
    if fa.type == "EN1661":
        P, da, c, dc, _, _, m, _, _, s = fa.dimTable
        flange_edge_rounded = True
    elif fa.type == "ASMEB18.2.2.12":
        TPI, F, B, H, J, K = fa.dimTable
        P = 1 / TPI * 25.4
        s = F * 25.4
        dc = B * 25.4
        da = 1.05 * dia
        m = H * 25.4
        c = K * 25.4
        flange_edge_rounded = False
    sqrt3 = math.sqrt(3)
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
        fm.AddPoint((da + s) / 4, sqrt3 / 3 * ((dc - c) /
                    2 + c / (4 - 2 * sqrt3) - (da + s) / 4))
    else:
        fm.AddPoint(dc / 2, 0.0)
        fm.AddPoint(dc / 2, c)
        fm.AddPoint((da + s) / 4, c + (dc / 2 - (da + s) / 4) *
                    math.tan(math.radians(30)))
    face = fm.GetFace()
    flange = self.RevolveZ(face)
    nut_body = nut_body.fuse(flange).removeSplitter()
    if fa.thread:
        thread_cutter = self.CreateInnerThreadCutter(dia, P, m + P)
        nut_body = nut_body.cut(thread_cutter)
    return nut_body

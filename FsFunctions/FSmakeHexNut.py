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


def makeHexNut(self, fa):
    """Creates a basic hexagonal nut.
    Supported types:
    - ISO 4032 hexagon nuts
    - ISO 4033 hexagon high nuts
    - ISO 4035 hexagon thin nuts, chamfered
    - ASME B18.2.2 machine screw, thin, and regular hexagon nuts
    - DIN 6334 3xD length hexagon nuts
    - ASME B18.2.2 coupling nuts
    """
    SType = fa.type
    dia = self.getDia(fa.calc_diam, True)
    if SType[:3] == 'ISO' or SType == "DIN934":
        P, c, da, dw, e, m, mw, s = fa.dimTable
    elif SType == 'ASMEB18.2.2.1A':
        P, da, e, m, s = fa.dimTable
    elif SType == 'ASMEB18.2.2.4A':
        P, da, e, m_a, m_b, s = fa.dimTable
        m = m_a
    elif SType == 'ASMEB18.2.2.4B':
        P, da, e, m_a, m_b, s = fa.dimTable
        m = m_b
    elif SType == "DIN6334":
        P, da, m, s = fa.dimTable
    elif SType == "ASMEB18.2.2.13":
        TPI, F, H = fa.dimTable
        P = 1 / TPI * 25.4
        m = H * 25.4
        s = F * 25.4
        da = dia
    da = self.getDia(da, True)
    sqrt2_ = 1.0 / math.sqrt(2.0)
    # needed for chamfer at nut top
    cham = s * (math.sqrt(3) / 3 - 1 / 2) * math.tan(math.radians(22.5))
    H = P * math.cos(math.radians(30))
    cham_i_delta = da / 2.0 - (dia / 2.0 - H * 5.0 / 8.0)
    cham_i = cham_i_delta * math.tan(math.radians(15.0))
    # layout the nut profile, then create a revolved solid
    fm = FastenerBase.FSFaceMaker()
    fm.AddPoint(dia / 2.0 - H * 5.0 / 8.0, m - cham_i)
    fm.AddPoint(da / 2.0, m)
    fm.AddPoint(s / 2.0, m)
    fm.AddPoint(s / math.sqrt(3.0), m - cham)
    fm.AddPoint(s / math.sqrt(3.0), cham)
    fm.AddPoint(s / 2.0, 0.0)
    fm.AddPoint(da / 2.0, 0.0)
    fm.AddPoint(dia / 2.0 - H * 5.0 / 8.0, 0.0 + cham_i)
    head = self.RevolveZ(fm.GetFace())
    # create cutting tool for hexagon head
    extrude = self.makeHexPrism(s, m)
    nut = head.common(extrude)
    # add modeled threads if necessary
    if fa.thread:
        thread_cutter = self.CreateInnerThreadCutter(dia, P, m + P)
        nut = nut.cut(thread_cutter)
    return nut

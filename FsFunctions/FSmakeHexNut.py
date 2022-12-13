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
# make the ISO 4032 Hex-nut
# make the ISO 4033 Hex-nut


def makeHexNut(self, fa):  # dynamically loaded method of class Screw
    SType = fa.type
    dia = self.getDia(fa.calc_diam, True)
    if SType[:3] == 'ISO':
        # P, c, damax,  dw,    e,     m,   mw,   s_nom
        P, c, da, dw, e, m, mw, s = fa.dimTable
    elif SType == 'ASMEB18.2.2.1A':
        P, da, e, m, s = fa.dimTable
    elif SType == 'ASMEB18.2.2.4A':
        P, da, e, m_a, m_b, s = fa.dimTable
        m = m_a
    elif SType == 'ASMEB18.2.2.4B':
        P, da, e, m_a, m_b, s = fa.dimTable
        m = m_b

    da = self.getDia(da, True)
    sqrt2_ = 1.0 / math.sqrt(2.0)
    # needed for chamfer at nut top
    cham = (e - s) * math.sin(math.radians(15))
    H = P * math.cos(math.radians(30))  # Gewindetiefe H
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
    extrude = self.makeHextool(s, m, s * 2.0)
    nut = head.cut(extrude)
    # add modeled threads if necessary
    if fa.thread:
        thread_cutter = self.CreateInnerThreadCutter(dia, P, m + P)
        nut = nut.cut(thread_cutter)
    return nut

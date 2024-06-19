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


def makeThinCupNut(self, fa):
    """DIN917 Cap nuts, thin style"""
    dia = self.getDia(fa.calc_diam, True)
    P, g2, h, r, s, t, w = fa.dimTable

    H = P * math.cos(math.radians(30)) * 5.0 / 8.0
    if fa.Thread: H *= 1.1
    e = s / math.sqrt(3) * 2.0
    cham_i = H * math.tan(math.radians(15.0))
    cham_o = (e - s) * math.tan(math.radians(15.0))
    d = dia / 2.0

    fm = FastenerBase.FSFaceMaker()
    fm.AddPoint(d, 0.0)
    fm.AddPoint(s / 2.0, 0.0)
    fm.AddPoint(e / 2.0, cham_o)
    fm.AddPoint(e / 2.0, h - r + math.sqrt(r * r - e * e / 4.0))
    fm.AddArc(
        e / 4.0,
        h - r + math.sqrt(r * r - e * e / 16.0),
        0.0,
        h
    )
    fm.AddPoint(0.0, h-w)
    fm.AddPoint(0.0, d * math.tan(math.radians(15)))
    head = self.RevolveZ(fm.GetFace())
    extrude = self.makeHexPrism(s, h)
    nut = head.common(extrude)

    if fa.Thread:
        threadCutter = self.CreateBlindInnerThreadCutter(dia, P, t - 1.5 * P)
    else:
        fm.Reset()
        fm.AddPoint(0.0, 0.0)
        fm.AddPoint(d - H, 0.0)
        fm.AddPoint(d - H, t - P)
        fm.AddPoint(0.0, t - P + (d - H) / math.tan(math.radians(59)))
        threadCutter = self.RevolveZ(fm.GetFace())
    nut = nut.cut(threadCutter)
    return nut

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


def makeSquareBolt(self, fa):
    """Creates a screw with a simple square head.
    Supported types:
    - ASME B18.2.1 square head bolts
    """
    dia = self.getDia(fa.calc_diam, False)
    length = fa.calc_len
    if fa.baseType == "ASMEB18.2.1.1":
        TPI, F, H, R, L_T1, L_T2 = fa.dimTable
        r = R * 25.4
        s = F * 25.4
        k = H * 25.4
        P = 1 / TPI * 25.4
        if length <= 6 * 25.4:
            b = L_T1 * 25.4
        else:
            b = L_T2 * 25.4
    else:
        raise NotImplementedError(f"Unknown fastener type: {fa.baseType}")
    # lay out the fastener profile
    fm = FSFaceMaker()
    fm.AddPoint(0.0, k)
    fm.AddPoint(s / 2, k)
    fm.AddPoint(s / 2 + k / math.tan(math.radians(30)), 0.0)
    fm.AddPoint(dia / 2 + r, 0.0)
    fm.AddArc2(0.0, -r, 90)
    if length - r > b:  # partially threaded fastener
        thread_length = b
        if not fa.Thread:
            fm.AddPoint(dia / 2, -1 * (length - b))
    else:
        thread_length = length - r
    fm.AddPoint(dia / 2, -length + dia / 10)
    fm.AddPoint(dia * 4 / 10, -length)
    fm.AddPoint(0.0, -length)
    shape = self.RevolveZ(fm.GetFace())
    head_square = Part.makeBox(s, s, 2 * k + length)
    head_square.translate(Base.Vector(-s / 2, -s / 2, -length - k))
    shape = shape.common(head_square)
    if fa.Thread:
        thread_cutter = self.CreateBlindThreadCutter(dia, P, thread_length)
        thread_cutter.translate(
            Base.Vector(0.0, 0.0, -1 * (length - thread_length))
        )
        shape = shape.cut(thread_cutter)
    return shape

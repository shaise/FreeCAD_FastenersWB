# -*- coding: utf-8 -*-
"""
***************************************************************************
*   Copyright (c) 2023                                                    *
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


def makeTaperedPin(self, fa):
    if fa.Type == "ISO2339":
        d_1, a, surface = fa.dimTable
        length = fa.calc_len
        d_2 = d_1 + (length -2*a)/ 50
        r_1 = d_1
        r_2 = a / 2 + d_1 + (0.02 * length) ** 2 / (8 * a)
        ang_1 = math.degrees(math.asin(d_1 / 2 / r_1))
        ang_2 = math.degrees(math.asin(d_2 / 2 / r_2))
        fm = FSFaceMaker()
        fm.AddPoint(0.0, 0.0)
        fm.AddArc(
            r_2 * math.sin(math.pi / 12), r_2 * (math.cos(math.pi / 12) - 1), d_2 / 2, -a
        )
        fm.AddPoint(d_1 / 2, a - length)
        fm.AddArc(
            r_1 * math.sin(math.pi / 12),
            r_1 * (1 - math.cos(math.pi / 12)) - length,
            0.0,
            -length,
        )
        shape = self.RevolveZ(fm.GetFace())
        return shape
    elif fa.Type == "DIN1":
        d_1, c, r, surface = fa.dimTable
        length = fa.calc_len
        d_b = d_1 + (length)/ 50
        ang_1 = math.degrees(math.asin(d_1 / 2 / r))
        ang_2 = math.degrees(math.asin(d_b / 2 / r))
        fm = FSFaceMaker()
        fm.AddPoint(0.0, 0.0)
        fm.AddArc(
            r * math.sin(math.pi / 12), r * (math.cos(math.pi / 12) - 1), d_b / 2, -c
        )
        fm.AddPoint(d_1 / 2, -length)
        fm.AddArc(
            r * math.sin(math.pi / 12),
            r * (1 - math.cos(math.pi / 12)) - (length + c),
            0.0,
            - (length + c),
        )
        shape = self.RevolveZ(fm.GetFace())
        return shape
    else:
        raise NotImplementedError(f"Unknown fastener type: {fa.Type}")


def stdDesignatorTaperedPin(self, fa):
    designator = None
    length = fa.calc_len
    lengthStr = f"{length:.0f}"
    if fa.baseType == "ISO2339":
        d_1, a, surface = fa.dimTable
        if length % 1 != 0:
            designator = f"Taper pin ISO 2339 - {fa.Surface} - {d_1} x {length}"
        else:
            designator = f"Taper pin ISO 2339 - {fa.Surface} - {d_1} x {lengthStr}"
    if fa.baseType == "DIN1":
        dia, cham, radius, tolerance = fa.dimTable
        if length % 1 != 0:
            designator = f"Taper pin DIN 1 - {fa.Surface} {dia} x {length}"
        else:
            designator = f"Taper pin DIN 1 - {fa.Surface} {dia} x {lengthStr}"
        d_1, c, r, surface = fa.dimTable
    return designator

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


def makeDowelPin(self, fa):
    if fa.Type in ["ISO8734", "ISO2338"]:
        if  fa.Type in ["ISO2338"]:
            dia, cham, tolerance = fa.dimTable
        else:
            dia, cham = fa.dimTable
        length = fa.calc_len
        fm = FSFaceMaker()
        cham_d = tan15 * cham
        fm.AddPoint(0.0, 0.0)
        fm.AddPoint(dia / 2 - cham_d, 0.0)
        fm.AddPoint(dia / 2, -cham)
        fm.AddPoint(dia / 2, cham - length)
        fm.AddPoint(dia / 2 - cham_d, -length)
        fm.AddPoint(0.0, -length)
        shape = self.RevolveZ(fm.GetFace())
        return shape
    elif fa.Type in ["DIN7"]:
        dia, cham, radius, tolerance = fa.dimTable
        length = fa.calc_len
        fm = FSFaceMaker()
        if fa.Tolerance is not None and fa.Tolerance == "m6":
            cham_d = tan15 * cham
            fm.AddPoint(0.0, 0.0)
            fm.AddArc(
                radius * math.sin(math.pi / 12), radius * (math.cos(math.pi / 12) - 1), dia / 2, -cham
            )
            fm.AddPoint(dia / 2, -(length + cham))
            fm.AddArc(
                radius * math.sin(math.pi / 12),
                radius * (1 - math.cos(math.pi / 12)) - (length + 2 *cham),
                0.0,
                - (length + 2*cham),
            )
            shape = self.RevolveZ(fm.GetFace())
        if fa.Tolerance is not None and fa.Tolerance == "h8":
            cham_d = tan15 * cham
            fm.AddPoint(0.0, 0.0)
            fm.AddPoint(dia / 2 - cham_d, 0.0)
            fm.AddPoint(dia / 2, -cham)
            fm.AddPoint(dia / 2, -(length + cham))
            fm.AddPoint(dia / 2 - cham_d, -(length + 2*cham))
            fm.AddPoint(0.0, -(length + 2*cham))
            shape = self.RevolveZ(fm.GetFace())
        elif fa.Tolerance is not None and fa.Tolerance == "h11":
            fm.AddPoint(0.0, 0.0)
            fm.AddPoint(dia / 2, 0)
            fm.AddPoint(dia / 2, -length)
            fm.AddPoint(0.0, -length)
            shape = self.RevolveZ(fm.GetFace())
        return shape
    else:
        raise NotImplementedError(f"Unknown fastener type: {fa.Type}")


def stdDesignatorDowelPin(self, fa):
    designator = None
    length = fa.calc_len
    lengthStr = f"{length:.0f}"
    if fa.baseType == "ISO2338":
        dia, cham, tolerance = fa.dimTable
        if length % 1 != 0:
            designator = f"Parallel pin ISO 2338 - {dia}{fa.Tolerance} x {length}"
        else:
            designator = f"Parallel pin ISO 2338 - {dia}{fa.Tolerance} x {lengthStr}"
    if fa.baseType == "ISO8734":
        dia, cham = fa.dimTable
        if length % 1 != 0:
            designator = f"Parallel pin ISO 8734 - {dia} x {length}"
        else:
            designator = f"Parallel pin ISO 8734 - {dia} x {lengthStr}"
    if fa.baseType == "DIN7":
        dia, cham, radius, tolerance = fa.dimTable
        if length % 1 != 0:
            designator = f"Taper pin DIN 7 - {dia}{fa.Tolerance} x {length}"
        else:
            designator = f"Taper pin DIN 7 - {dia}{fa.Tolerance} x {lengthStr}"
    return designator

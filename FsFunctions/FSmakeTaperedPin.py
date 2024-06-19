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
        d_1, a = fa.dimTable
    else:
        raise NotImplementedError(f"Unknown fastener type: {fa.Type}")
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

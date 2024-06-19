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
import math
import FreeCAD as Base
import Part


def makeTaperGroovedPin(self, fa):
    length = fa.calc_len
    if fa.Type == "ISO8744":
        d_1, a = fa.dimTable
        groove_l = length
    elif fa.Type == "ISO8745":
        d_1, a = fa.dimTable
        groove_l = length / 2
    else:
        raise NotImplementedError(f"Unknown fastener type: {fa.Type}")
    fm = FSFaceMaker()
    fm.AddPoint(0.0, 0.0)
    fm.AddArc2(0.0, -d_1, -90)
    fm.AddPoint(d_1, -2 * length)
    fm.AddPoint(0.0, -2 * length)
    shape = self.RevolveZ(fm.GetFace())
    shape = shape.common(
        shape.mirror(Base.Vector(0.0, 0.0, -length / 2), Base.Vector(0.0, 0.0, 1.0))
    )
    shape = shape.common(
        Part.makeCylinder(
            d_1 / 2,
            1.1 * length,
            Base.Vector(0.0, 0.0, 0.05 * length),
            Base.Vector(0.0, 0.0, -1.0),
        )
    )
    fm.Reset()
    groove_d = d_1 / 12
    fm.AddPoint(d_1 / 2 - groove_d, 0.0)
    fm.AddPoint(d_1 / 2, math.tan(math.radians(35)) * groove_d)
    fm.AddPoint(d_1 / 2, -math.tan(math.radians(35)) * groove_d)
    groove_cutter = fm.GetFace().extrude(Base.Vector(1.01*groove_d, -1.01*groove_l, 0.0))
    groove_cutter.rotate(Base.Vector(0.0, 0.0, 0.0), Base.Vector(1.0, 0.0, 0.0), -90)
    groove_cutter.translate(
        Base.Vector(0.0, 0.0, -length)
    )
    for i in range(3):
        shape = shape.cut(
            groove_cutter.rotated(
                Base.Vector(0.0, 0.0, 0.0), Base.Vector(0.0, 0.0, 1.0), 120 * i
            )
        )
    return shape

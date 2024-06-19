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


def makeGroovedParallelPin(self, fa):
    if fa.Type == "ISO8740":
        d_1, c_1, c_2, a = fa.dimTable
    else:
        raise NotImplementedError(f"Unknown fastener type: {fa.Type}")
    length = fa.calc_len
    fm = FSFaceMaker()
    fm.AddPoint(0.0, 0.0)
    fm.AddArc2(0.0, -d_1, -30)
    fm.AddPoint(d_1 / 2, c_2 - length)
    intermediate_rad = d_1 / 2 - math.tan(math.pi / 8) * (c_2 - c_1)
    fm.AddPoint(intermediate_rad, c_1 - length)
    bottom_angle = math.degrees(math.atan(intermediate_rad / (d_1 - (c_2 - c_1))))
    fm.AddArc2(-intermediate_rad, d_1 - (c_2 - c_1), -bottom_angle)
    shape = self.RevolveZ(fm.GetFace())
    # add the grooves
    fm.Reset()
    fm.AddPoint(0.0, 0.0)
    fm.AddPoint(d_1 / 12, math.tan(math.radians(35)) * d_1 / 12)
    fm.AddPoint(d_1 / 12, -math.tan(math.radians(35)) * d_1 / 12)
    groove_profile = fm.GetFace()
    groove_profile.rotate(Base.Vector(0.0, 0.0, 0.0), Base.Vector(1.0, 0.0, 0.0), -90)
    groove_profile.translate(Base.Vector(5 * d_1 / 12, 0.0, 0.0))
    groove_cutter = groove_profile.extrude(Base.Vector(0.0, 0.0, -length))
    for i in range(3):
        shape = shape.cut(
            groove_cutter.rotated(
                Base.Vector(0.0, 0.0, 0.0), Base.Vector(0.0, 0.0, 1.0), 120 * i
            )
        )
    return shape

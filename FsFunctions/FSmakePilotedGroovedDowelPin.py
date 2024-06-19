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


def makePilotedGroovedDowelPin(self, fa):
    length = fa.calc_len
    if fa.Type == "ISO8739":
        d_1, d_2, c, a = fa.dimTable
    else:
        raise NotImplementedError(f"Unknown fastener type: {fa.Type}")
    fm = FSFaceMaker()
    fm.AddPoint(0.0, 0.0)
    fm.AddPoint(d_2 / 2, 0.0)
    cham_ht = (d_2 - d_1) / 2 / math.tan(math.radians(15))
    fm.AddPoint(d_2 / 2, -length + c + cham_ht)
    fm.AddPoint(d_1 / 2, c - length)
    fm.AddPoint(d_1 / 2, -length)
    fm.AddPoint(0.0, -length)
    shape = self.RevolveZ(fm.GetFace())
    # add the rounded ends
    fm.Reset()
    fm.AddPoint(0.0, 1000.0)
    fm.AddPoint(d_1, 1000.0)
    fm.AddPoint(d_1, -length + d_1)
    fm.AddArc2(-d_1, 0.0, -90)
    bottom_cutter = self.RevolveZ(fm.GetFace())
    shape = shape.common(bottom_cutter)
    shape = shape.common(
        bottom_cutter.mirror(
            Base.Vector(0.0, 0.0, -length / 2), Base.Vector(0.0, 0.0, 1.0)
        )
    )
    # add the grooves
    fm.Reset()
    fm.AddPoint(0.0, 0.0)
    dp = d_2 / 12
    fm.AddPoint(dp, math.tan(math.radians(35)) * dp)
    fm.AddPoint(dp, -math.tan(math.radians(35)) * dp)
    groove_profile = fm.GetFace()
    groove_profile.rotate(Base.Vector(0.0, 0.0, 0.0), Base.Vector(1.0, 0.0, 0.0), -90)
    groove_profile.translate(Base.Vector(d_2 / 2 - dp, 0.0, 0.0))
    groove_cutter = groove_profile.extrude(Base.Vector(0.0, 0.0, -length))
    fm.Reset()
    fm.AddPoint(d_2 / 2 - dp, c + cham_ht - length)
    fm.AddPoint(d_2 / 2 - dp + c + cham_ht, -length)
    fm.AddPoint(d_2 / 2 - dp, -length)
    inter = self.RevolveZ(fm.GetFace())
    groove_cutter = groove_cutter.cut(inter)
    for i in range(3):
        shape = shape.cut(
            groove_cutter.rotated(
                Base.Vector(0.0, 0.0, 0.0), Base.Vector(0.0, 0.0, 1.0), 120 * i
            )
        )
    return shape

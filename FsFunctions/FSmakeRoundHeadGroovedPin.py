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


def makeRoundHeadGroovedPin(self, fa):
    if fa.Type == "ISO8746":
        d_1_max, d_1_min, d_k_max, d_k_min, k_max, k_min, r, c = fa.dimTable
        d_1 = (d_1_max + d_1_min) / 2
        d_k = (d_k_max + d_k_min) / 2
        k = (k_max + k_min) / 2
        a = math.radians((15 + 30) / 2)
    else:
        raise NotImplementedError(f"Unknown fastener type: {fa.Type}")
    length = fa.calc_len
    fm = FSFaceMaker()
    fm.AddPoint(0.0, k)
    th = math.atan((d_k / 2) / (r - k))
    fm.AddArc(r * math.sin(th / 2), k + r * (math.cos(th / 2) - 1), d_k / 2, 0.0)
    fm.AddPoint(d_1 / 2, 0.0)
    fm.AddPoint(d_1 / 2, -length + c)
    fm.AddPoint(d_1 / 2 - c * math.tan(a), -length)
    fm.AddPoint(0.0, -length)
    profile = fm.GetFace()
    shape = self.RevolveZ(profile)
    # add the grooves
    fm.Reset()
    fm.AddPoint(0.0, 0.0)
    dp = d_1 / 12
    fm.AddPoint(dp, math.tan(math.radians(35)) * dp)
    fm.AddPoint(dp, -math.tan(math.radians(35)) * dp)
    groove_profile = fm.GetFace()
    groove_profile.rotate(Base.Vector(0.0, 0.0, 0.0), Base.Vector(1.0, 0.0, 0.0), -90)
    groove_profile.translate(Base.Vector(d_1 / 2 - dp, 0.0, 0.0))
    groove_cutter = groove_profile.extrude(Base.Vector(0.0, 0.0, -length))
    fm.Reset()
    fm.AddPoint(0.0, 0.0)
    fm.AddPoint(1.1 * d_1 / 2, 0.0)
    fm.AddPoint(1.1 * d_1 / 2, -d_1 / 6)
    fm.AddPoint(0.0, -d_1 / 6 - 1.1 * d_1 / (2 * math.tan(math.radians(35))))
    inter = self.RevolveZ(fm.GetFace()).rotated(
        Base.Vector(0.0, 0.0, 0.0), Base.Vector(0.0, 0.0, 1.0), 180
    )
    groove_cutter = groove_cutter.cut(inter)
    for i in range(3):
        shape = shape.cut(
            groove_cutter.rotated(
                Base.Vector(0.0, 0.0, 0.0), Base.Vector(0.0, 0.0, 1.0), 120 * i
            )
        )
    return shape

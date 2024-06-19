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


def makeInternalThreadedDowelPin(self, fa):
    if fa.Type == "ISO8733":
        d_1, c_1, c_2, d_2, P, d_3, t_1, t_2, t_3 = fa.dimTable
        end = "square"
    elif fa.Type == "ISO8735":
        d_1, a, c, d_2, P, d_3, t_1, t_2, t_3 = fa.dimTable
        c_1 = a
        c_2 = c
        end = "round"
    else:
        raise NotImplementedError(f"Unknown fastener type: {fa.Type}")
    length = fa.calc_len
    fm = FSFaceMaker()
    cham_top = math.tan(math.radians(15)) * c_1
    cham_bottom = math.tan(math.radians(15)) * c_2
    fm.AddPoint(0.0, -t_2)
    d_4 = self.GetInnerThreadMinDiameter(d_2, P)
    fm.AddPoint(d_4 / 2, d_4 / (2 * math.tan(math.radians(59))) - t_2)
    fm.AddPoint(d_4 / 2, -t_3 - math.tan(math.radians(30)) * (d_3 - d_4))
    fm.AddPoint(d_3 / 2, -t_3)
    fm.AddPoint(d_3 / 2, 0.0)
    fm.AddPoint(d_1 / 2 - cham_top, 0.0)
    fm.AddPoint(d_1 / 2, -c_1)
    fm.AddPoint(d_1 / 2, c_2 - length)
    fm.AddPoint(d_1 / 2 - cham_bottom, -length)
    fm.AddPoint(0.0, -length)
    shape = self.RevolveZ(fm.GetFace())
    if end == "round":
        fm.Reset()
        fm.AddPoint(0.0,1000.0)
        fm.AddPoint(d_1,1000.0)
        fm.AddPoint(d_1,-length+d_1)
        fm.AddArc2(-d_1,0.0,-90)
        bottom_cutter = self.RevolveZ(fm.GetFace())
        shape = shape.common(bottom_cutter)
    if fa.Thread:
        thread_cutter = self.CreateBlindInnerThreadCutter(d_2, P, t_1)
        thread_cutter.rotate(
            Base.Vector(0.0, 0.0, 0.0), Base.Vector(0.0, 1.0, 0.0), 180
        )
        shape = shape.cut(thread_cutter)
    return shape

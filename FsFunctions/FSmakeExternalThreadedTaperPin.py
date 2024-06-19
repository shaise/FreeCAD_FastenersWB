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


def makeExternalThreadedTaperPin(self, fa):
    length = fa.calc_len
    if fa.Type == "ISO8737":
        d_1, a, b, d_2, P, d_3, z = fa.dimTable
        d_5 = d_1 + (length - a-b) / 50
    else:
        raise NotImplementedError(f"Unknown fastener type: {fa.Type}")
    fm = FSFaceMaker()
    fm.AddPoint(0.0, b+a)
    fm.AddPoint(d_3/2, b+a)
    fm.AddPoint(d_3/2,b+a-z)
    fm.AddPoint(d_2/2,b+a-z-(d_2-d_3)/2)
    fm.AddPoint(d_2/2,a)
    fm.AddPoint(d_5/2,0.0)
    fm.AddPoint(d_1/2,-length)
    fm.AddPoint(0.0,-length)
    shape = self.RevolveZ(fm.GetFace())
    shape = shape.makeFillet(d_1*0.05, [e for e in shape.Edges if (e.CenterOfMass.z + length) < 1e-5])
    fm.Reset()
    fm.AddPoint(0.0, -length)
    fm.AddPoint(d_2, -length)
    fm.AddPoint(d_2, a+b-d_2)
    fm.AddArc2(-d_2,0.0,90)
    shape = shape.common(self.RevolveZ(fm.GetFace()))
    if fa.Thread:
        thread_cutter = self.CreateBlindThreadCutter(d_2, P, b)
        thread_cutter.rotate(Base.Vector(0.0, 0.0, 0.0), Base.Vector(0.0, 1.0, 0.0), 180)
        thread_cutter.translate(Base.Vector(0.0, 0.0, a))
        shape = shape.cut(thread_cutter)
    return shape

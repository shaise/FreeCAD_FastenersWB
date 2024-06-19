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


def makeSlottedSpringPin(self, fa):
    if fa.Type == "ISO8752" or fa.Type == "ISO13337":
        d_1, d_2, a, s = fa.dimTable
    else:
        raise NotImplementedError(f"Unknown fastener type: {fa.Type}")
    length = fa.calc_len
    fm = FSFaceMaker()
    d_3 = d_1 - s
    fm.AddPoint(d_1 / 2 - s, 0.0)
    fm.AddPoint(d_3 / 2, 0.0)
    fm.AddPoint(d_1 / 2, -a)
    fm.AddPoint(d_1 / 2, -length + a)
    fm.AddPoint(d_3 / 2, -length)
    fm.AddPoint(d_1 / 2 - s, -length)
    unrevolved_ang = math.degrees(math.asin(0.25 * s / (d_1 / 2 - s)))
    profile = fm.GetFace()
    profile.rotate(
        Base.Vector(0.0, 0.0, 0.0), Base.Vector(0.0, 0.0, 1.0), 0.5 * unrevolved_ang
    )
    shape = self.RevolveZ(profile, 360 - unrevolved_ang)
    return shape

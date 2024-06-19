# -*- coding: utf-8 -*-
"""
***************************************************************************
*   Copyright (c) 2013, 2014, 2015                                        *
*   Original code by:                                                     *
*   Ulrich Brammer <ulrich1a[at]users.sourceforge.net>                    *
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


def makeButtonHeadScrew(self, fa):
    """Create a cap screw with a round 'button' head
    Supported types:
    - ISO 7380-1 Button head Screw
    - ASMEB18.3.3A UNC Hex socket button head screws
    """
    SType = fa.baseType
    length = fa.calc_len
    dia = self.getDia(fa.calc_diam, False)
    if SType == 'ISO7380-1':
        P, b, a, da, dk, dk_mean, s_mean, t_min, r, k, e, w = fa.dimTable
    elif SType == 'ASMEB18.3.3A':
        P, b, da, dk, s_mean, t_min, r, k = fa.dimTable
    # Bottom of recess
    e_cham = 2.0 * s_mean / math.sqrt(3.0) * 1.005
    # helper value for button arc
    ak = -(4 * k ** 2 + e_cham ** 2 - dk ** 2) / (8 * k)
    # radius of button arc
    rH = math.sqrt((dk / 2.0) ** 2 + ak ** 2)
    alpha = (math.atan(2 * (k + ak) / e_cham) + math.atan((2 * ak) / dk)) / 2
    # lay out fastener profile
    fm = FastenerBase.FSFaceMaker()
    fm.AddPoint(0.0, k)
    fm.AddPoint(e_cham / 2.0, k)
    fm.AddArc(
        rH * math.cos(alpha),
        -ak + rH * math.sin(alpha),
        dk / 2.0,
        0.0
    )
    fm.AddPoint(dia / 2 + r, 0.0)
    fm.AddArc2(0.0, -r, 90)
    if length - r > b:  # partially threaded fastener
        thread_length = b
        if not fa.Thread:
            fm.AddPoint(dia / 2, -1 * (length - b))
    else:
        thread_length = length - r
    fm.AddPoint(dia / 2, -length + dia / 10)
    fm.AddPoint(dia * 4 / 10, -length)
    fm.AddPoint(0.0, -length)
    # revolve the profile to a solid and cut the recess out
    shape = self.RevolveZ(fm.GetFace())
    recess = self.makeHexRecess(s_mean, t_min, True)
    recess.translate(Base.Vector(0.0, 0.0, k))
    shape = shape.cut(recess)
    # add modelled threads if needed
    if fa.Thread:
        thread_cutter = self.CreateBlindThreadCutter(dia, P, thread_length)
        thread_cutter.translate(
            Base.Vector(0.0, 0.0, -1 * (length - thread_length))
        )
        shape = shape.cut(thread_cutter)
    return shape

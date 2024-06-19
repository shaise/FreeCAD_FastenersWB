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


def makeScrewTap(self, fa):
    """negative-threaded rod for tapping holes"""
    ThreadType = fa.calc_diam
    if fa.Diameter != 'Custom':
        dia = self.getDia(ThreadType, True)
        if fa.baseType == "ScrewTap":
            P, tunIn, tunEx = fa.dimTable
        elif fa.baseType == 'ScrewTapInch':
            P = fa.dimTable[0]
    else:  # custom pitch and diameter
        P = fa.calc_pitch
        if self.sm3DPrintMode:
            dia = self.smNutThrScaleA * \
                float(fa.calc_diam) + self.smNutThrScaleB
        else:
            dia = float(fa.calc_diam)
    tap = Part.makeCylinder(
        dia / 2 - 0.625 * math.sqrt(3) / 2 * P,
        fa.calc_len + 2
    )
    tap.translate(Base.Vector(0.0, 0.0, -1.0))
    if fa.Thread:
        threads = self.CreateInnerThreadCutter(dia, P, fa.calc_len + P)
        tap = tap.fuse(threads)
    tap.rotate(
        Base.Vector(0.0, 0.0, 0.0),
        Base.Vector(1.0, 0.0, 0.0),
        180
    )
    cyl = Part.makeCylinder(
        dia,
        fa.calc_len,
        Base.Vector(0.0, 0.0, 0.0),
        Base.Vector(0.0, 0.0, -1.0),
        360
    )
    solid = Part.Solid(cyl.common(tap))
    return solid

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
import FastenerBase


# EN 1661 Hexagon nuts with flange
def makeHexNutWFlange(self, fa):  # dynamically loaded method of class Screw
    dia = self.getDia(fa.calc_diam, True)
    P, da, c, dc, dw, e, m, mw, r1, s = fa.dimTable
    sqrt3 = math.sqrt(3)
    inner_rad = dia / 2 - P * 0.625 * sqrt3 / 2
    inner_cham_ht = math.tan(math.radians(15)) * (da / 2 - inner_rad)
    # create the body of the nut
    fm = FastenerBase.FSFaceMaker()
    fm.AddPoint(inner_rad, m - inner_cham_ht)
    fm.AddPoint(da / 2, m)
    fm.AddPoint(s / 2, m)
    fm.AddPoint(s / 2 + sqrt3 * m, 0)
    fm.AddPoint(da / 2, 0)
    fm.AddPoint(inner_rad, inner_cham_ht)
    nut_body = self.RevolveZ(fm.GetFace())
    # cut the hex flats with a boolean subtraction
    nut_body = nut_body.cut(self.makeHextool(s, m, s * 5))
    # add the flange with a boolean fuse
    fm.Reset()
    fm.AddPoint((da + s) / 4, 0.0)
    fm.AddPoint((dc + sqrt3 * c) / 2, 0.0)
    fm.AddPoint((dc - c) / 2, 0.0)
    fm.AddArc2(0, c / 2, 150)
    fm.AddPoint((da + s) / 4, sqrt3 / 3 * ((dc - c) /
                2 + c / (4 - 2 * sqrt3) - (da + s) / 4))
    face = fm.GetFace()
    flange = self.RevolveZ(face)
    nut_body = nut_body.fuse(flange).removeSplitter()
    if fa.thread:
        thread_cutter = self.CreateInnerThreadCutter(dia, P, m + P)
        nut_body = nut_body.cut(thread_cutter)
    return nut_body

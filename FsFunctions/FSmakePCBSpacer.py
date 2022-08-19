# -*- coding: utf-8 -*-
"""
***************************************************************************
*   Copyright (c) 2022                                                    *
*   Shai Seger <shaise[at]gmail>                                          *
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

# PCB spacers / Wurth standard WA-SSTII 

cos30 = math.cos(math.radians(30))

def pspMakeFace(m, sw, l, id, th):
    l = float(l)
    id2 = id / 2.0
    sw2 = float(sw) / 2.0
    m2 = m / 2.0
    d2 = 0.95 * sw2 / cos30
    l1 = l - (d2 - sw2) / 2.0
    dd = m2 - id2
    p = 10
    if p + 0.5 > l / 2.0:
        p = l / 2.0 - 0.5
    p1 = p - id2

    fm = FastenerBase.FSFaceMaker()
    fm.AddPoints((id2, l - dd), (id2 + dd, l), (sw2, l), (d2, l1), (d2, dd), (sw2, 0), (id2 + dd, 0), (id2, dd))
    if l > th:
        # separate holes
        fm.AddPoints((id2, p1), (0, p), (0, l - p), (id2, l - p1))
    return fm.GetFace()


def makePCBSpacer(self, fa):
    diam = fa.calc_diam
    width = fa.width
    flen = fa.calc_len

    FreeCAD.Console.PrintLog("Making PCB spacer" + diam + "x" + str(flen) + "x" + str(width) + "\n")

    th, id = fa.dimTable

    m = FastenerBase.MToFloat(diam)
    f = pspMakeFace(m, width, flen, id, th)
    p = f.revolve(Base.Vector(0.0, 0.0, 0.0), Base.Vector(0.0, 0.0, 1.0), 360)
    w = float(width)
    l = float(flen)
    htool = self.makeHextool(w, l, w * 2)
    htool.translate(Base.Vector(0.0, 0.0, - 0.1))
    shape = p.cut(htool)
    return shape

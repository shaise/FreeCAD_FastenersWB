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

# PCB standoffs / Wurth standard WA-SSTII

cos30 = math.cos(math.radians(30))


def psMakeFace(m, sw, lo, l, id):
    id2 = id / 2.0
    sw2 = float(sw) / 2.0
    m2 = m / 2.0
    d2 = 0.95 * sw2 / cos30
    l1 = l - (d2 - sw2) / 2.0
    dd = m2 - id2
    lo1 = -0.6
    lo2 = lo1 - dd
    lo3 = dd - lo
    p = l - 10
    if p < 1:
        p = 1
    p1 = p + id2

    fm = FastenerBase.FSFaceMaker()
    fm.AddPoints(
        (0, p),
        (id2, p1),
        (id2, l - dd),
        (id2 + dd, l),
        (sw2, l),
        (d2, l1),
        (d2, 0),
        (id2, 0),
        (id2, lo1),
        (m2, lo2),
        (m2, lo3),
        (id2, -lo),
        (0, -lo),
    )
    return (fm.GetFace(), p1)


def makePCBStandoff(self, fa):
    diam = fa.calc_diam
    width = fa.Width
    screwlen = FastenerBase.LenStr2Num(fa.ScrewLength)
    flen = float(fa.calc_len)
    FreeCAD.Console.PrintLog(
        "Making PCB standof"
        + str(diam)
        + "x"
        + str(flen)
        + "x"
        + str(width)
        + "x"
        + str(screwlen)
        + "\n"
    )
    diain = self.getDia(fa.calc_diam, True)
    diaout = self.getDia(fa.calc_diam, False)
    P = FsData["ISO262def"][fa.Diameter][0]
    id = self.GetInnerThreadMinDiameter(diain, P)
    f, thrPos = psMakeFace(diaout, width, screwlen, flen, id)
    p = self.RevolveZ(f)
    w = float(width)
    htool = self.makeHexPrism(w, flen + screwlen)
    htool.translate(Base.Vector(0.0, 0.0, -screwlen - 0.1))
    shape = p.common(htool)
    if fa.Thread:
        # outer thread
        tool = self.CreateBlindThreadCutter(diaout, P, screwlen)
        b = Part.makeBox(20, 20, 10, Base.Vector(-10.0, -10.0, -0.6))
        tool = tool.cut(b)
        shape = shape.cut(tool)
        tool1 = self.CreateInnerThreadCutter(diain, P, flen - thrPos)
        tool1.rotate(
            Base.Vector(0.0, 0.0, 0.0),
            Base.Vector(1.0, 0.0, 0.0),
            180
        )
        tool1.translate(Base.Vector(0.0, 0.0, flen))
        shape = shape.cut(tool1)
    return shape

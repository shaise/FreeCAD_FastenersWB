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


def pspMakeFace(m, sw, l, id, thl):
    id2 = id / 2.0
    sw2 = sw / 2.0
    m2 = m / 2.0
    d2 = 0.95 * sw2 / cos30
    l1 = l - (d2 - sw2) / 2.0
    dd = m2 - id2
    thl1 = thl - id2

    fm = FastenerBase.FSFaceMaker()
    fm.AddPoints(
        (id2, l - dd),
        (id2 + dd, l),
        (sw2, l),
        (d2, l1),
        (d2, dd),
        (sw2, 0),
        (id2 + dd, 0),
        (id2, dd),
    )
    if thl > 0:
        # separate holes
        fm.AddPoints((id2, thl1), (0, thl), (0, l - thl), (id2, l - thl1))
    return fm.GetFace()


def makePCBSpacer(self, fa):
    diam = fa.calc_diam
    width = fa.Width
    flen = fa.calc_len

    FreeCAD.Console.PrintLog(
        "Making PCB spacer" + diam + "x" + str(flen) + "x" + str(width) + "\n"
    )

    th, _ = fa.dimTable
    dia = self.getDia(fa.calc_diam, True)
    P = FsData["ISO262def"][fa.Diameter][0]
    id = self.GetInnerThreadMinDiameter(dia, P)
    w = float(width)
    l = float(flen)
    if l > th:
        # separate thread holes on both sides
        thl = 10
        if thl + 0.5 > l / 2.0:
            thl = l / 2.0 - 0.5
    else:
        thl = 0

    f = pspMakeFace(dia * 1.05, w, l, id, thl)
    p = self.RevolveZ(f)
    htool = self.makeHexPrism(w, l)
    htool.translate(Base.Vector(0.0, 0.0, - 0.1))
    fSolid = p.common(htool)
    if fa.Thread:
        if thl > 0:  # blind & threaded from both sides
            threadCutter = self.CreateInnerThreadCutter(dia, P, thl - dia / 2)
            fSolid = fSolid.cut(threadCutter)
            threadCutter.rotate(
                Base.Vector(0.0, 0.0, l / 2),
                Base.Vector(1.0, 0.0, 0.0),
                180
            )
        else:  # has through hole, fully threaded
            threadCutter = self.CreateInnerThreadCutter(dia, P, l + P)
        fSolid = fSolid.cut(threadCutter)
    return fSolid

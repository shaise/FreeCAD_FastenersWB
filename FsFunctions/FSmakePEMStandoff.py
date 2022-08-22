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

tan30 = math.tan(math.radians(30))

# PEM Self Clinching standoffs types: SO/SOS/SOA/SO4

def soMakeFace(b, c, h, d, l1, bl, isBlind):
    h10 = h / 10.0
    h102 = h10 + h10 / 2
    c12 = c / 12.5
    c20 = c / 20.0
    c40 = c / 40.0
    b = b / 2
    c = c / 2
    d = d / 2
    ch1 = b - d
    ch2 = d * tan30
    l2 = l1 - bl
    c1 = c - c40
    c2 = c - c20
    l3 = h10 * 2 + (c12 + c20) * 2

    fm = FastenerBase.FSFaceMaker()
    if isBlind:
        fm.AddPoints((0, 0), (0, -h102), (d, -(h102 + ch2)), (d, -(l1 - ch1)), (b, -l1))
    else:
        fm.AddPoints((b, 0), (d, -ch1), (d, -(l2 - ch1)), (b, -l2))
        if (l1 - l2) > 0.01:
            fm.AddPoint(b, -l1)
    fm.AddPoint(c, -l1)
    if l3 < l1:
        fm.AddPoints((c, -l3), (c1, -l3), (c1, -(l3 - c20)), (c, -(l3 - c20)))
    fm.AddPoints((c, -(h10 * 2 + c12 + c20)), (c1, -(h10 * 2 + c12 + c20)), (c1, -(h10 * 2 + c12)), (c, -(h10 * 2 + c12))
            ,(c, -h10 * 2), (c2, -h10 * 2), (c2, -h10), (h * 0.6, -h10), (h * 0.6, 0))
    return fm.GetFace()

def makePEMStandoff(self, fa):
    l = fa.calc_len
    plen = fa.length
    b, c, h, d, lmin, lmax = fa.dimTable
    if fa.blind and l < 6:
        l = 6
        plen = "6"

    bl = FsData[fa.type + "length"][plen][0]
    f = soMakeFace(b, c, h, d, l, bl, fa.blind)
    p = f.revolve(Base.Vector(0.0, 0.0, 0.0), Base.Vector(0.0, 0.0, 1.0), 360)
    htool = self.makeHextool(h, 3, h * 2)
    htool.translate(Base.Vector(0.0, 0.0, -2.0))
    fSolid = p.cut(htool)
    if fa.thread:
        dia = self.getDia(fa.calc_diam, True)
        P = FsData["MetricPitchTable"][fa.diameter][0]
        turns = int(l / P) + 2
        threadCutter = self.makeInnerThread_2(dia, P, turns, None, l)
        if (fa.blind):
            threadCutter.translate(Base.Vector(0.0, 0.0, -d))
        else:
            threadCutter.translate(Base.Vector(0.0, 0.0, P))
        # Part.show(threadCutter, 'threadCutter')
        fSolid = fSolid.cut(threadCutter)

    return fSolid


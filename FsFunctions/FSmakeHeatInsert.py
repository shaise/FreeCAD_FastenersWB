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

# Heat Staked Threaded Insert types: IUT


def iutMakeFace(d, a, e, c, c1, k1, k2, k3, k4, k5):
    fm = FastenerBase.FSFaceMaker()
    fm.AddPoints(
        (d, 0),
        (e, 0),
        (e, k1),
        (c, k1),
        (c, k2),
        (e, k2),
        (e, k3),
        (c1, k4),
        (c1, k5),
        (c, k5),
        (c, a),
        (d, a),
    )
    return fm.GetFace()


def makeHeatInsert(self, fa):
    D, A, E, C, s1, s2 = fa.dimTable
    oD = self.getDia(fa.Diameter, True)
    P = FsData["ISO262def"][fa.Diameter][0]
    iD = self.GetInnerThreadMinDiameter(oD, P)
 
    len =  FastenerBase.LenStr2Num(fa.Length)
    extDiam = FastenerBase.LenStr2Num(fa.ExternalDiam)
    scale = len / A
    a = -len
    d = iD / 2
    e = extDiam / 2
    c = (extDiam - E + C) / 2
    ch = c / 3
    c1 = c - d / 10
    k1 = -(A - ch - s1 - s2) * scale / 2
    k2 = k1 - s1 * scale
    k4 = k1 * 2 - s1 * scale
    k3 = k4 + (e - c1) * scale
    k5 = k4 - s2 * scale

    fFace = iutMakeFace(d, a, e, c, c1, k1, k2, k3, k4, k5)
    fSolid = self.RevolveZ(fFace)


    if fa.Thread:
        dia = self.getDia(fa.calc_diam, True)
        thread_cutter = self.CreateInnerThreadCutter(dia, P, A + P)
        thread_cutter.rotate(
            Base.Vector(0.0, 0.0, 0.0), Base.Vector(1.0, 0.0, 0.0), 180
        )
        fSolid = fSolid.cut(thread_cutter)
        knurlCut = self.CreateKnurlCutter(extDiam, c * 2, k1 - 0.01, -k1 + 0.02, False)
        fSolid = fSolid.cut(knurlCut)
        knurlCut = self.CreateKnurlCutter(extDiam, c * 2, k4 - 0.01, -k1 + 0.02, True)
        fSolid = fSolid.cut(knurlCut)
    return fSolid

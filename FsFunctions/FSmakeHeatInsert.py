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


def iutMakeFace(D, a, E, C, s1, s2):
    d = D / 2
    e = E / 2
    c = C / 2
    ch = C / 6
    k1 = (a - ch - s1 - s2) / 2
    k2 = k1 + s1 + k1
    sd = (e - d) / 2

    fm = FastenerBase.FSFaceMaker()
    fm.AddPoints(
        (d, 0),
        (e, 0),
        (e, -k1),
        (e - sd, -k1),
        (e - sd, -k1 - s1),
        (e, -k1 - s1),
        (e, -k2),
        (e - sd, -k2),
        (e - sd, -k2 - s2),
        (c, -k2 - s2),
        (c, -a),
        (d, -a),
    )
    return fm.GetFace()


def makeHeatInsert(self, fa):
    D, A, E, C, s1, s2 = fa.dimTable
    oD = self.getDia(fa.diameter, True)
    P = FsData["MetricPitchTable"][fa.diameter][0]
    iD = self.GetInnerThreadMinDiameter(oD, P)
    fFace = iutMakeFace(iD, A, E, C, s1, s2)
    fSolid = self.RevolveZ(fFace)
    if fa.thread:
        dia = self.getDia(fa.calc_diam, True)
        thread_cutter = self.CreateInnerThreadCutter(dia, P, A + P)
        thread_cutter.rotate(
            Base.Vector(0.0, 0.0, 0.0), Base.Vector(1.0, 0.0, 0.0), 180
        )
        fSolid = fSolid.cut(thread_cutter)
    return fSolid

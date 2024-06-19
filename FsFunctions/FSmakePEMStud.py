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

cos30 = math.cos(math.radians(30))

# PEM Self Clinching studs types: FH/FHS/FHA

def fhMakeFace(m, h, d, l):
    h10 = h / 10.0
    h20 = h / 20.0
    m25 = m * 0.025
    hs = 0.8 + 0.125 * m
    he = 0.8 + 0.2 * m
    h = h / 2.0
    m = m / 2.0
    d = d / 2.0
    h85 = h * 0.85
    m9 = m * 0.9
    mr = m9 - m25 * (1.0 - cos30)
    ch1 = m - d

    fm = FastenerBase.FSFaceMaker()
    fm.AddPoints((0, 0), (h - h20, 0))
    fm.AddArc(h, - h20, h - h20, -h10)
    fm.AddPoints((h - h20, -(h10 + h20)), (m, -(h10 + h20)), (m, -hs), (m9, -(hs + m25)))
    fm.AddArc(mr, -(hs + m25 * 1.5), m9, -(hs + m25 * 2))
    fm.AddPoint(m, -he)
    fm.AddPoints((m, -(l - ch1)), (m - ch1, -l), (0, -l))
    return (fm.GetFace(), -he)


def makePEMStud(self, fa):
    l = fa.calc_len
    dia = self.getDia(fa.calc_diam, False)
    h, s, d = fa.dimTable

    profile, thStart = fhMakeFace(dia, h, d, l)
    rev = self.RevolveZ(profile)
    if not fa.Thread:
        return rev
    # real thread
    P = FsData["ISO262def"][fa.Diameter][0]
    rthread = self.CreateBlindThreadCutter(dia, P, l + thStart)
    rthread.translate(Base.Vector(0.0, 0.0, thStart))
    rev = rev.cut(rthread)
    return Part.Solid(rev)


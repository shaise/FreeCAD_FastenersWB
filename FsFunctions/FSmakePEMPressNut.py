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

# PEM Self Clinching nuts types: S/SS/CLS/CLSS/SP

def clMakeFace(do, di, a, c, e, t):
    do = do / 2
    di = di / 2
    ch1 = do - di
    ch2 = ch1 / 2
    if ch2 < 0.2:
        ch2 = 0.2
    c = c / 2
    e = e / 2
    c2 = (c + e) / 2
    sl = a / 20
    a2 = a / 2

    fm = FastenerBase.FSFaceMaker()
    fm.AddPoint(di, -a + ch1)
    fm.AddPoint(do, -a)
    fm.AddPoint(c, -a)
    fm.AddPoint(c, -a * 0.75, )
    fm.AddPoint(c - sl, -a2)
    fm.AddPoint(c2, -a2)
    fm.AddPoint(c2, 0)
    fm.AddPoint(e, 0)
    fm.AddPoint(e, t - ch2)
    fm.AddPoint(e - ch2, t)
    fm.AddPoint(do, t)
    fm.AddPoint(di, t - ch1)
    return fm.GetFace()


def makePEMPressNut(self, fa):
    diam = fa.calc_diam
    code = fa.Tcode

    i = FastenerBase.FsTitles[fa.baseType + "tcodes"].index(code)

    c, e, t, _ = fa.dimTable
    a = FsData[fa.baseType + "tcodes"][diam][i]
    if a == 0:
        return None
    do = self.getDia(diam, True)
    P = FsData["ISO262def"][diam][0]
    di = self.GetInnerThreadMinDiameter(do, P)
    fFace = clMakeFace(do * 1.05, di, a, c, e, t)
    fSolid = self.RevolveZ(fFace)
    if fa.Thread:
        dia = self.getDia(diam, True)
        H = a + t
        thread_cutter = self.CreateInnerThreadCutter(dia, P, H * 2)
        thread_cutter.translate(Base.Vector(0.0, 0.0, -H * 0.75))
        fSolid = fSolid.cut(thread_cutter)
    return fSolid

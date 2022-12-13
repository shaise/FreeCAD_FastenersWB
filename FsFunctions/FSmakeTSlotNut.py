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

# make T-Slot nut
# DIN508
# GN507


def makeTSlotNut(self, fa):  # dynamically loaded method of class Screw
    SType = fa.type
    dia = self.getDia(fa.calc_diam, True)

    if SType[:3] == "DIN":
        # a, e_max, f, h, k_max, P
        a, e, f, h, k, P = fa.dimTable
        e1 = e  # e1 is depth, y plane
        e2 = e  # e2 is width, x plane
    elif SType[:2] == "GN":
        a, e1, e2, h, k, P = fa.dimTable
        f = 0.125 * e2  # constant calculated with official GN step file

    # T-Slot nut Points, transversal cut
    fm = FastenerBase.FSFaceMaker()
    fm.AddPoint(e2 / 2 - f, -h)
    fm.AddPoint(e2 / 2, -h + f)
    fm.AddPoint(e2 / 2, -h + k)
    fm.AddPoint(a / 2, -h + k)
    fm.AddPoint(a / 2, 0.0)
    fm.AddPoint(-a / 2, 0.0)
    fm.AddPoint(-a / 2, -h + k)
    fm.AddPoint(-e2 / 2, -h + k)
    fm.AddPoint(-e2 / 2, -h + f)
    fm.AddPoint(-e2 / 2 + f, -h)
    face = fm.GetFace()
    # translate to plane y = -e1 / 2 to extrude up to y = e1 / 2
    face.translate(Base.Vector(0.0, -e1 / 2, 0.0))
    nut = face.extrude(Base.Vector(0.0, e1, 0.0))

    sqrt3 = math.sqrt(3)
    da = 1.05 * dia
    inner_rad = dia / 2 - P * 0.625 * sqrt3 / 2
    inner_cham_ht = math.tan(math.radians(15)) * (da / 2 - inner_rad)
    fm.Reset()
    fm.AddPoint(0.0, 0.0)
    fm.AddPoint(da / 2, 0.0)
    fm.AddPoint(inner_rad, -inner_cham_ht)
    fm.AddPoint(inner_rad, -h + inner_cham_ht)
    fm.AddPoint(da / 2, -h)
    fm.AddPoint(0.0, -h)
    hole = self.RevolveZ(fm.GetFace())
    nut = nut.cut(hole)
    if fa.thread:
        thread_cutter = self.CreateInnerThreadCutter(dia, P, h + P)
        thread_cutter.rotate(
            Base.Vector(0.0, 0.0, 0.0), Base.Vector(1.0, 0.0, 0.0), 180
        )
        nut = nut.cut(thread_cutter)
    return nut

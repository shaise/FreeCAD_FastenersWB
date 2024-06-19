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


def makeShoulderScrew(self, fa):
    """creates a screw with a cylindrical head and a round shoulder section

    supported types:
    - ISO 7379 shoulder screws
    - ASMEB18.3.4 shoulder screws
    """
    SType = fa.baseType
    length = fa.calc_len
    P, d1, d3, l2, l3, SW = fa.dimTable
    d2 = self.getDia(fa.calc_diam, False)
    l1 = length
    # define the fastener head and shoulder
    fm = FSFaceMaker()
    fm.AddPoint(0, l1 + l3)
    fm.AddPoint(d3 / 2 - 0.04 * d3, l3 + l1)
    fm.AddPoint(d3 / 2, l3 - 0.04 * d3 + l1)
    fm.AddPoint(d3 / 2, l1)
    fm.AddPoint(d1 / 2, l1)
    fm.AddArc(d1 / 2 - 0.04 * d1, l1 - 0.1 * l3, d1 / 2, l1 - 0.2 * l3)
    fm.AddPoint(d1 / 2, 0)
    fm.AddPoint(d2 / 2, 0)
    fm.AddArc(d2 / 2 - 0.075 * d2, -0.075 * l2, d2 / 2, -0.15 * l2)
    fm.AddPoint(d2 / 2, -1 * l2 + 0.1 * d2)
    fm.AddPoint(d2 / 2 - 0.1 * d2, -1 * l2)
    fm.AddPoint(0, -1 * l2)
    screw = self.RevolveZ(fm.GetFace())
    # cut a hexagonal driving feature
    recess = self.makeHexRecess(SW, l3 * 0.4, True)
    recess.translate(Base.Vector(0.0, 0.0, l1 + l3))
    screw = screw.cut(recess)
    # add modelled threads if needed
    if fa.Thread:
        thread_cutter = self.CreateBlindThreadCutter(d2, P, l2)
        screw = screw.cut(thread_cutter)
    return screw

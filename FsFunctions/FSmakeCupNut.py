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

# DIN1587 : cap (or 'acorn') nut

def makeCupNut(self): # dynamically loaded method of class Screw
    SType = self.fastenerType
    dia = self.getDia(self.fastenerDiam, True)
    if SType == "DIN1587":
        P, d_k, h, m, s, t = self.dimTable
    else:
        raise RuntimeError("unknown screw type")
    pnts = list(
        map(
            lambda x: Base.Vector(x),
            [
                [0, 0, 1.1 * dia / 4],
                [1.1 * dia / 2, 0, 0],
                [s / 2, 0, 0],
                [s * math.sqrt(3) / 3, 0, 0.045 * s],
                [s * math.sqrt(3) / 3, 0, m - 0.045 * s],
                [s / 2, 0, m],
                [d_k / 2, 0, m],
                [d_k / 2, 0, h - d_k / 2],
                [d_k / 2 * math.sqrt(2) / 2, 0, h - d_k / 2 + d_k / 2 * math.sqrt(2) / 2],
                [0, 0, h],
            ],
        )
    )
    profile = Part.Wire(
        [
            Part.makeLine(pnts[0], pnts[1]),
            Part.makeLine(pnts[1], pnts[2]),
            Part.makeLine(pnts[2], pnts[3]),
            Part.makeLine(pnts[3], pnts[4]),
            Part.makeLine(pnts[4], pnts[5]),
            Part.makeLine(pnts[5], pnts[6]),
            Part.makeLine(pnts[6], pnts[7]),
            Part.Arc(pnts[7], pnts[8], pnts[9]).toShape(),
            Part.makeLine(pnts[9], pnts[0]),
        ]
    )
    shell = profile.revolve(Base.Vector(0, 0, 0), Base.Vector(0, 0, 1), 360)
    solid = Part.Solid(shell)
    # create an additional solid to cut the hex flats with
    mhex = Base.Matrix()
    mhex.rotateZ(math.radians(60.0))
    polygon = []
    vhex = Base.Vector(s / math.sqrt(3), 0, 0)
    for i in range(6):
        polygon.append(vhex)
        vhex = mhex.multiply(vhex)
    polygon.append(vhex)
    hexagon = Part.makePolygon(polygon)
    hexFace = Part.Face(hexagon)
    solidHex = hexFace.extrude(Base.Vector(0.0, 0.0, h * 1.1))
    solid = solid.common(solidHex)
    # cut the threads
    tap_tool = self.makeScrewTap("ScrewTap", self.fastenerDiam, t)
    tap_tool.rotate(Base.Vector(0, 0, 0), Base.Vector(1, 0, 0), 180)
    tap_tool.translate(Base.Vector(0, 0, -1 * P))
    tc_points = list(
        map(
            lambda x: Base.Vector(x),
            [
                (0, 0, t - P),
                (1.1 * dia / 2, 0, t - P - 1.1 * dia / 8),
                (1.1 * dia / 2, 0, h),
                (0, 0, h)
            ]
        )
    )
    thread_chamfer_profile = Part.Wire(
        [
            Part.makeLine(tc_points[0], tc_points[1]),
            Part.makeLine(tc_points[1], tc_points[2]),
            Part.makeLine(tc_points[2], tc_points[3]),
            Part.makeLine(tc_points[3], tc_points[0]),
        ]
    )
    cham_shell = thread_chamfer_profile.revolve(
        Base.Vector(0, 0, 0),
        Base.Vector(0, 0, 1),
        360
    )
    thread_chamfer = Part.Solid(cham_shell)
    tap_tool = tap_tool.cut(thread_chamfer)
    solid = solid.cut(tap_tool)
    return solid

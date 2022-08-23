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

def makeCupNut(self, fa): # dynamically loaded method of class Screw
    SType = fa.type
    dia = self.getDia(fa.calc_diam, True)
    if SType == "DIN1587":
        P, d_k, h, m, s, t, w = fa.dimTable
    else:
        raise RuntimeError("unknown screw type")
    sq3 = math.sqrt(3)
    ec = (2 - sq3) * s / 6
    pnts = list(
        map(
            lambda x: Base.Vector(x),
            [
                [0, 0, 1.1 * dia / 4],
                [1.1 * dia / 2, 0, 0],
                [s / 2, 0, 0],
                [s * sq3 / 3, 0, ec],
                [s * sq3 / 3, 0, m - ec],
                [d_k / 2, 0, (m - ec) + (2 * s - sq3 * d_k) / 6 ],
                [d_k / 2, 0, h - d_k / 2 ],
                [d_k / 2 * math.sqrt(2) / 2, 0, h - d_k / 2 + d_k / 2 * math.sqrt(2) / 2],
                [0, 0, h]
            ]
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
            Part.Arc(pnts[6], pnts[7], pnts[8]).toShape(),
            Part.makeLine(pnts[8], pnts[0])
        ]
    )
    shell = self.RevolveZ(profile)
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
    if fa.thread:
        turns = math.ceil((h-w) / P)
        tap_tool = self.makeInnerThread_2(dia, P, int(turns), None, None)
        tap_tool.translate(Base.Vector(0, 0, h-w))
        tc_points = list(
            map(
                lambda x: Base.Vector(x),
                [
                    (0, 0, h-w),
                    (1.1 * dia / 2, 0, t),
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
        cham_shell = self.RevolveZ(thread_chamfer_profile)
        thread_chamfer = Part.Solid(cham_shell)
        tap_tool = tap_tool.cut(thread_chamfer)
        solid = solid.cut(tap_tool)
    else:
        hole_pts = [ Base.Vector(x, 0, y) for x, y in [
            [0, 0],
            [0, h-w],
            [dia/2.0, t],
            [dia/2.0, 0]
        ] ]
        hole_profile = Part.Wire( [
            Part.makeLine(hole_pts[0], hole_pts[1]),
            Part.makeLine(hole_pts[1], hole_pts[2]),
            Part.makeLine(hole_pts[2], hole_pts[3]),
            Part.makeLine(hole_pts[3], hole_pts[0])
        ] )
        hole = Part.Solid(self.RevolveZ(hole_profile))
        solid = solid.cut(hole)
    return solid

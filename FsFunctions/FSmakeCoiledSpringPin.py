# -*- coding: utf-8 -*-
"""
***************************************************************************
*   Copyright (c) 2023                                                    *
*   Alex Neufeld <alex.d.neufeld@gmail.com>                               *
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


def makeCoiledSpringPin(self, fa):
    if fa.Type in ["ISO8748", "ISO8750", "ISO8751"]:
        d_1, d_2, a, s = fa.dimTable
    else:
        raise NotImplementedError(f"Unknown fastener type: {fa.Type}")
    length = fa.calc_len
    fm = FSFaceMaker()
    fm.AddPoint(d_1 / 2-s, -a)
    fm.AddPoint(d_2 / 2 - s, 0.0)
    fm.AddPoint(d_2 / 2, 0.0)
    fm.AddPoint(d_1/2,-a)
    fm.AddPoint(d_1 / 2, a-length)
    fm.AddPoint(d_2/2,-length)
    fm.AddPoint(d_2 / 2 - s, -length)
    fm.AddPoint(d_1 / 2 - s, a-length)
    # create a swept spiral profile
    # NOTE: counter-intuitively, during testing, adding MORE reference points to the
    # spline increased the performance of the swept solid, while also eliminating
    # degenerate results for some sizes. Don't reduce r and expect a simple perf boost!
    r = 100
    turns = 2.25
    points = []
    for i in range(int(r * turns) + 1):
        # using d_2 for the reference radius is important here. The sweep path should
        # intersect with some point of the initial profile, otherwise the profile may be
        # transformed in unexpected ways during the sweep process
        points.append(
            Base.Vector(
                # multiply by 1.01 to avoid self-intersecting faces in the spiral
                #            |
                #            v
                (d_2 / 2 - 1.01 * s * i / r) * math.cos(-i / r * 2 * math.pi),
                (d_2 / 2 - 1.01 * s * i / r) * math.sin(-i / r * 2 * math.pi),
                0.0,
            )
        )
    # ref: https://forum.freecad.org/viewtopic.php?t=47282
    # Part.BSplineCurve([poles],              #[vector]
    #                 [multiplicities],     #[int]
    #                 [knots],              #[float]
    #                 periodic,             #bool
    #                 degree,               #int
    #                 [weights],            #[float]
    #                 checkRational)        #bool
    spiral = Part.BSplineCurve(points, None, None, False, 3, None, False)
    sweep = Part.BRepOffsetAPI.MakePipeShell(Part.Wire([spiral.toShape()]))
    sweep.setFrenetMode(True)
    sweep.add(fm.GetClosedWire())
    if sweep.isReady():
        sweep.build()
    else:
        # geometry couldn't be generated in a usable form
        raise RuntimeError("Failed to create sweep!")
    sweep.makeSolid()
    shape = sweep.shape()
    return shape

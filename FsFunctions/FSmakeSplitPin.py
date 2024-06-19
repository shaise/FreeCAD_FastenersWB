# -*- coding: utf-8 -*-
"""
***************************************************************************
*   Copyright (c) 2023:                                                    *
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


def makeSplitPin(self, fa):
    if fa.Type == "ISO1234":
        a, b, c, d = fa.dimTable
    else:
        raise NotImplementedError(f"Unknown fastener type: {fa.Type}")
    length = fa.calc_len
    # dia = FsData["DiaList"][fa.calc_diam][0]
    fm = FSFaceMaker()
    # lay out the swept profile of the pin (an almost-half circle)
    fm.AddPoint(d / 2 * math.cos(math.pi * 0.008), d / 2 * math.sin(math.pi * 0.008))
    fm.AddArc(
        0.0, d / 2, d / 2 * math.cos(math.pi * 0.992), d / 2 * math.sin(math.pi * 0.992)
    )
    sweep_profile = fm.GetClosedWire()
    sweep_profile.rotate(Base.Vector(0.0, 0.0, 0.0), Base.Vector(1.0, 0.0, 0.0), -90)
    sweep_profile.rotate(Base.Vector(0.0, 0.0, 0.0), Base.Vector(0.0, 0.0, 1.0), -90)
    sweep_profile.translate(Base.Vector(0.0, 0.0, -length))
    # create the sweep path
    fm.Reset()
    r_1 = (4 * b**2 - 4 * b * c + d**2) / (4 * c - 4 * d)
    th = 2 * math.atan((c - d) / (2 * b - c))
    fm.AddPoint(d / 2, -length)
    fm.AddPoint(d / 2, 0.0)
    fm.AddArc2(r_1, 0.0, -math.degrees(th))
    fm.AddArc2(-c / 2 * math.cos(th), c / 2 * math.sin(th), 180 + 2 * math.degrees(th))
    fm.AddArc2(-r_1 * math.cos(th), -r_1 * math.sin(th), -math.degrees(th))
    fm.AddPoint(-d / 2, -(length + a))
    sweep_path = fm.GetWire()
    # create the swept solid
    sweep = Part.BRepOffsetAPI.MakePipeShell(sweep_path)
    sweep.setFrenetMode(True)
    sweep.add(sweep_profile)
    if sweep.isReady():
        sweep.build()
    else:
        # geometry couldn't be generated in a usable form
        raise RuntimeError("Failed to create shell thread: could not sweep thread")
    sweep.makeSolid()
    # chamfer the leading end of the pin
    shape = sweep.shape()
    to_cham = [
        edge
        for edge in shape.Edges
        if abs(edge.CenterOfMass.z + length) < 1e-5
        or abs(edge.CenterOfMass.z + length + a) < 1e-5
    ]
    shape = shape.makeChamfer(d / 6, to_cham)
    return shape

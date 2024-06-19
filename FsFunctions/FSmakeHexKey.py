# -*- coding: utf-8 -*-
"""
***************************************************************************
*   Copyright (c) 2024:                                                   *
*   Original code by:                                                     *
*   hasecilu <hasecilu[at]tuta.io>                                        *
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
import math
import Part
from FreeCAD import Base
import FastenerBase
from screw_maker import FsData, sqrt3

def makeHexKey(self, fa):
    """
    Make hex keys
    Implemented:
    - ISO 2936: Hexagon socket screw keys
    """
    if fa.Type == "ISO2936":
        # Width across flats
        s = float(fa.calc_diam)
        r = max(1.5, s)
        l2, f = fa.dimTable
        keySize = fa.KeySize
        i = FastenerBase.FsTitles[fa.baseType + "keysizes"].index(keySize)
        l1 = FsData[fa.baseType + "keysizes"][fa.calc_diam][i]

        fm = FastenerBase.FSFaceMaker()
        # r = (s / 2) / sin(60°)
        for i in range(6):
            fm.AddPoint((s * sqrt3 / 3) * math.cos(i * math.pi / 3),
                        (s * sqrt3 / 3) * math.sin(i * math.pi / 3))
        hexagon = fm.GetClosedWire()
        hexagon.rotate(Base.Vector(0.0, 0.0, 0.0), Base.Vector(0.0, 0.0, 1.0), -90)
        hexagon.translate(Base.Vector(-l2, 0.0, 0.0))

        # create the sweep path
        fm.Reset()
        fm.AddPoint(-l2, 0.0)
        fm.AddPoint(-r, 0.0)
        fm.AddArc2(0, -r, -90)
        fm.AddPoint(0.0, -l1)
        sweep_path = fm.GetWire()

        # create the swept solid
        sweep = Part.BRepOffsetAPI.MakePipeShell(sweep_path)
        sweep.setFrenetMode(True)
        sweep.add(hexagon)
        if sweep.isReady():
            sweep.build()
        else:
            # geometry couldn't be generated in a usable form
            raise RuntimeError("Failed to create shell thread: could not sweep thread")
        sweep.makeSolid()
        key = sweep.shape()

        # Draw a triangle and make a ring to chamfer
        fm.Reset()
        fm.AddPoint((s * sqrt3 / 3) - f, 0.0)
        fm.AddPoint((s * sqrt3 / 3), 0.0)
        fm.AddPoint((s * sqrt3 / 3), f)
        chamfer = self.RevolveZ(fm.GetFace())
        chamfer.translate(Base.Vector(0.0, 0.0, -l1))
        key = key.cut(chamfer)
        chamfer.translate(Base.Vector(0.0, 0.0, l1))
        chamfer.rotate(Base.Vector(0.0, 0.0, 0.0), Base.Vector(0.0, 1.0, 0.0), 90)
        chamfer.translate(Base.Vector(-l2, 0.0, 0.0))
        key = key.cut(chamfer)

        return key

    raise NotImplementedError(f"Unknown fastener type: {fa.Type}")

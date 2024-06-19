# -*- coding: utf-8 -*-
"""
***************************************************************************
*   Copyright (c) 2022                                                    *
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


def makeExternalRetainingRing(self, fa):
    """creates a retaining ring - returns a solid object
    supported types:
      DIN 471 - metric external retaining rings
    """
    SType = fa.baseType
    if SType == "DIN471":
        S, d3, a_Max, b, d5_Min, d2 = fa.dimTable
    else:
        raise NotImplementedError(f"Unknown fastener type: {fa.Type}")
    small_sizes = ["3 mm", "4 mm", "5 mm", "6 mm", "7 mm", "8 mm", "9 mm"]
    if fa.Diameter in small_sizes:
        pnt1 = Base.Vector(d5_Min/2, -1*math.sqrt(d3**2-d5_Min**2)/2)
        pnt2 = Base.Vector(d5_Min/2, -1*math.sqrt(d3**2-d5_Min**2)/2-a_Max)
        pnt3 = Base.Vector(
            d5_Min*(1/2+math.sqrt(2)/2),
            -1*math.sqrt(d3**2-d5_Min**2)/2-a_Max
            + d5_Min*(1-math.sqrt(2)/2)
        )
        pnt4 = Base.Vector(
            d5_Min*1.5,
            -1*math.sqrt(d3**2-d5_Min**2)/2-a_Max+d5_Min
        )
        r_b = d3/2 + 0.8*b
        offset = b/5
        pnt5 = Base.Vector(
            d5_Min*1.5,
            offset - math.sqrt(r_b**2-(1.5*d5_Min)**2)
        )
        pnt6 = Base.Vector(r_b, offset)
        pnt7 = Base.Vector(0, d3/2+b)
        pnt8 = Base.Vector(0, d3/2)
        pnt9 = Base.Vector(d3/2, 0)
        drill_center = Base.Vector(
            d5_Min*0.5,
            -1*math.sqrt(d3**2-d5_Min**2)/2-a_Max+d5_Min
        )
        profile = Part.Wire([
            Part.makeLine(pnt1, pnt2),
            Part.Arc(pnt2, pnt3, pnt4).toShape(),
            Part.makeLine(pnt4, pnt5),
            Part.Arc(pnt5, pnt6, pnt7).toShape(),
            Part.makeLine(pnt7, pnt8),
            Part.Arc(pnt8, pnt9, pnt1).toShape(),
        ])
        solid = Part.Solid(
            Part.makeFace(profile, "Part::FaceMakerSimple").extrude(Base.Vector(0, 0, S))
        )
        edges_to_fillet = [
            edge for edge in solid.Edges if
            (edge.CenterOfMass.distanceToPoint(pnt5) < 1e-3 + S/2)
        ]
        solid = solid.makeFillet(d5_Min, edges_to_fillet)
        drill = Part.makeCylinder(d5_Min/2, S, drill_center)
        solid = solid.cut(drill)
        solid = solid.fuse(
            solid.mirror(
                Base.Vector(0, 0, 0),
                Base.Vector(1, 0, 0)
            )
        ).removeSplitter()
        return solid

    else:
        pnt1 = Base.Vector(
            d5_Min/2,
            -1*math.sqrt(d3**2-d5_Min**2)/2
        )
        pnt2 = Base.Vector(
            d5_Min/2,
            -1*math.sqrt(d3**2-d5_Min**2)/2-a_Max
        )
        r_o = math.sqrt(pnt2[0]**2+pnt2[1]**2)
        pnt3 = Base.Vector(
            r_o*math.cos(math.radians(285)),
            r_o*math.sin(math.radians(285))
        )
        pnt4 = Base.Vector(
            r_o*math.cos(math.radians(295)),
            r_o*math.sin(math.radians(295))
        )
        r_b = (d3 + b + a_Max/2)/2
        offset = b/5
        adjust_sizes = ["10 mm", "11 mm", "12 mm", "13 mm", "14 mm", "15 mm"]
        pnt5_adjust = 5 if fa.Diameter in adjust_sizes else 0
        pnt5 = Base.Vector(
            r_b*math.cos(math.radians(300+pnt5_adjust)),
            offset + r_b*math.sin(math.radians(300+pnt5_adjust))
        )
        pnt6 = Base.Vector(r_b, offset)
        pnt7 = Base.Vector(0, d3/2+b)
        pnt8 = Base.Vector(0, d3/2)
        pnt9 = Base.Vector(d3/2, 0)
        drill_center = Base.Vector(
            r_b*math.cos(math.radians(285+pnt5_adjust/2)),
            offset + r_b*math.sin(math.radians(285+pnt5_adjust/2))
        )
        profile = Part.Wire([
            Part.makeLine(pnt1, pnt2),
            Part.Arc(pnt2, pnt3, pnt4).toShape(),
            Part.makeLine(pnt4, pnt5),
            Part.Arc(pnt5, pnt6, pnt7).toShape(),
            Part.makeLine(pnt7, pnt8),
            Part.Arc(pnt8, pnt9, pnt1).toShape(),
        ])
        solid = Part.Solid(
            Part.makeFace(profile, "Part::FaceMakerSimple").extrude(Base.Vector(0, 0, S))
        )
        edges_to_fillet = [
            edge for edge in solid.Edges if
            (edge.CenterOfMass.distanceToPoint(pnt4) < 1e-3 + S/2) or
            (edge.CenterOfMass.distanceToPoint(pnt5) < 1e-3 + S/2)
        ]
        solid = solid.makeFillet(d5_Min, edges_to_fillet[0:1])
        solid = solid.makeFillet(d5_Min, edges_to_fillet[1:])
        drill = Part.makeCylinder(d5_Min/2, S, drill_center)
        solid = solid.cut(drill)
        solid = solid.fuse(
            solid.mirror(
                Base.Vector(0, 0, 0),
                Base.Vector(1, 0, 0)
            )
        ).removeSplitter()
        return solid

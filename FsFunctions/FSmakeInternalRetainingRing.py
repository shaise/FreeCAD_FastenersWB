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


def makeInternalRetainingRing(self, fa):
    """creates a retaining ring - returns a solid object
    supported types:
      DIN 472 - metric internal retaining rings
    """
    SType = fa.baseType
    if SType == "DIN472":
        S, d_3, a_Max, b, d5_Min, d2 = fa.dimTable
    else:
        raise NotImplementedError(f"Unknown fastener type: {fa.Type}")
    small_sizes = [
        "8 mm", "9 mm", "10 mm", "11 mm", "12 mm",
        "13 mm", "14 mm", "15 mm", "16 mm", "17 mm",
        "18 mm", "19 mm", "20 mm", "21 mm", "22 mm",
        "23 mm", "24 mm"
    ]
    if fa.Diameter in small_sizes:
        offset = b/4
        pnt1 = Base.Vector(0, d_3/2 - b)
        pnt2 = Base.Vector(0, d_3/2)
        pnt3 = Base.Vector(d_3/2, 0)
        pnt4 = Base.Vector(
            d_3/2*math.cos(math.radians(280)),
            d_3/2*math.sin(math.radians(280))
        )
        pnt5 = Base.Vector(
            (d_3/2 - a_Max/2)*math.cos(math.radians(280)),
            (d_3/2 - a_Max/2)*math.sin(math.radians(280))
        )
        lug_angle = 2*math.atan(a_Max/(d_3-a_Max))
        lug_center = Base.Vector(
            (d_3/2 - a_Max/2)*math.cos(math.radians(280)+lug_angle/2),
            (d_3/2 - a_Max/2)*math.sin(math.radians(280)+lug_angle/2)
        )
        pnt6 = Base.Vector(
            (d_3/2 - a_Max)*math.cos(math.radians(280)+lug_angle/2),
            (d_3/2 - a_Max)*math.sin(math.radians(280)+lug_angle/2)
        )
        theta = math.radians(280)+lug_angle
        pnt7 = lug_center + Base.Vector(
            (a_Max/2)*math.cos(theta-math.radians(270)),
            (a_Max/2)*math.sin(theta-math.radians(270))
        )
        r_i = d_3/2-b+offset
        pnt8x = math.cos(theta)**2 * \
            (
                math.sqrt(r_i**2/math.cos(theta)**2 - offset**2) -
                offset*math.tan(theta)
            )
        pnt8 = Base.Vector(pnt8x, pnt8x*math.tan(theta))
        pnt9 = Base.Vector(r_i, -1*offset)
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
        possible_edges = [edge for edge in solid.Edges if
                          abs(edge.Length - S) < 1e-7]
        xpos_list = [edge.CenterOfMass.x for edge in possible_edges]
        max_index = xpos_list.index(max(xpos_list))
        edge_to_fillet = possible_edges[max_index]
        solid = solid.makeFillet(d5_Min, [edge_to_fillet, ])
        hole = Part.makeCylinder(d5_Min/2, S, lug_center)
        solid = solid.cut(hole)
        solid = solid.fuse(
            solid.mirror(
                Base.Vector(0, 0, 0),
                Base.Vector(1, 0, 0)
            )
        ).removeSplitter()
        return solid

    else:
        offset = b/5
        pnt1 = Base.Vector(0, d_3/2 - b)
        pnt2 = Base.Vector(0, d_3/2)
        pnt3 = Base.Vector(d_3/2, 0)
        pnt4 = Base.Vector(
            d_3/2*math.cos(math.radians(280)),
            d_3/2*math.sin(math.radians(280))
        )
        pnt5 = Base.Vector(
            (d_3/2 - a_Max)*math.cos(math.radians(280)),
            (d_3/2 - a_Max)*math.sin(math.radians(280))
        )
        lug_angle = 2*math.asin(0.425*a_Max/(d_3/2 - a_Max/2))
        pnt6 = Base.Vector(
            (d_3/2 - a_Max)*math.cos(math.radians(280)+lug_angle/2),
            (d_3/2 - a_Max)*math.sin(math.radians(280)+lug_angle/2)
        )
        theta = math.radians(280)+lug_angle
        pnt7 = Base.Vector(
            (d_3/2 - a_Max)*math.cos(theta),
            (d_3/2 - a_Max)*math.sin(theta)
        )
        r_i = d_3/2-b+offset
        pnt8x = math.cos(theta)**2 * \
            (
                math.sqrt(r_i**2/math.cos(theta)**2 - offset**2) -
                offset*math.tan(theta)
            )
        pnt8 = Base.Vector(pnt8x, pnt8x*math.tan(theta))
        pnt9 = Base.Vector(r_i, -1*offset)
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
        possible_edges = [edge for edge in solid.Edges if
                          abs(edge.Length - S) < 1e-7]
        xpos_list = [edge.CenterOfMass.x for edge in possible_edges]
        max_index = xpos_list.index(max(xpos_list))
        edge_to_fillet = possible_edges[max_index]
        solid = solid.makeFillet(d5_Min, [edge_to_fillet, ])
        lug_center = Base.Vector(
            (d_3/2 - a_Max/2)*math.cos(math.radians(280)+lug_angle/2),
            (d_3/2 - a_Max/2)*math.sin(math.radians(280)+lug_angle/2)
        )
        hole = Part.makeCylinder(d5_Min/2, S, lug_center)
        solid = solid.cut(hole)
        solid = solid.fuse(
            solid.mirror(
                Base.Vector(0, 0, 0),
                Base.Vector(1, 0, 0)
            )
        ).removeSplitter()
        return solid

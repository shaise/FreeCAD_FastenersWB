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


def makeEClip(self, fa):
    """creates an "E-clip" retaining ring - returns a solid object
    supported types:
      DIN 6799 - metric E-clips
    """
    SType = fa.baseType
    if SType == "DIN6799":
        groove_dia, shaft_dia_min, shaft_dia_max, \
            d3_max, S, a = fa.dimTable
    else:
        raise NotImplementedError(f"Unknown fastener type: {fa.Type}")
    solid = Part.makeCylinder(
        d3_max/2,
        S,
        Base.Vector(0, 0, 0),
        Base.Vector(0, 0, 1),
        180
    )
    solid = solid.rotate(
        Base.Vector(0, 0, 0),
        Base.Vector(0, 0, 1),
        270
    )
    cutter_1 = Part.makeCylinder(groove_dia/2, S)
    solid = solid.cut(cutter_1)
    cutter_2 = Part.makeCylinder(
        groove_dia/2+0.3*(d3_max-groove_dia),
        S,
        Base.Vector(0, 0, 0),
        Base.Vector(0, 0, 1),
        65
    )
    edges_to_fillet = [edge for edge in cutter_2.Edges if
                       abs(edge.Length - S) < 1e-5]
    cutter_2 = cutter_2.makeFillet((d3_max-groove_dia)/10, edges_to_fillet)
    solid = solid.cut(cutter_2)
    if groove_dia <= 5:
        adjust = -6
    else:
        adjust = 0
    pnt1 = Base.Vector(0, 0)
    pnt2 = Base.Vector(0.5*d3_max*math.tan(math.radians(20+adjust)), 0)
    pnt3 = Base.Vector(d3_max*math.tan(math.radians(20+adjust)), -0.5*d3_max)
    pnt4 = Base.Vector(0, -0.5*d3_max)
    cutter_3_profile = Part.Wire([
        Part.makeLine(pnt1, pnt2),
        Part.makeLine(pnt2, pnt3),
        Part.makeLine(pnt3, pnt4),
        Part.makeLine(pnt4, pnt1),
    ])
    cutter_3 = Part.Solid(
        Part.makeFace(cutter_3_profile, "Part::FaceMakerSimple").extrude(Base.Vector(0, 0, S))
    )
    solid = solid.cut(cutter_3)
    ypos_list = [edge.CenterOfMass.y for edge in solid.Edges]
    min_index = ypos_list.index(min(ypos_list))
    edge_to_fillet = solid.Edges[min_index]
    solid = solid.makeFillet((d3_max-groove_dia)/10, [edge_to_fillet, ])
    solid = solid.fuse(
        solid.mirror(
            Base.Vector(0, 0, 0),
            Base.Vector(1, 0, 0)
        )
    ).removeSplitter()
    return solid

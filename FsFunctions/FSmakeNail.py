# -*- coding: utf-8 -*-
"""
***************************************************************************
*   Copyright (c) 2024                                                    *
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
from FastenerBase import FSFaceMaker


def makeNail(self, fa):
    """
    Make a nail

    Supported types:
    - DIN1160[A/B]: Clout or slate nails
    """
    if fa.baseType[:7] == "DIN1160":
        return makeDIN1160(self, fa)

    raise NotImplementedError(f"Unknown fastener type: {fa.baseType}")


def makeDIN1160(self, fa):
    """
    Make a DIN1160[A/B] nail.
    """
    d, l, _, d2 = fa.dimTable

    return self.RevolveZ(makePointFace(d, l, d2, d / 5))


def makePointFace(dia, length, head_w, head_th, angle=20):
    """Make the face for a point end nail."""
    tip_length = (dia / 2) / math.tan(math.radians(angle / 2))
    r = dia / 10
    fm = FSFaceMaker()
    fm.AddPoint(0.0, head_th)
    fm.AddPoint(head_w, head_th)
    fm.AddPoint(head_w, 0.0)
    fm.AddPoint(dia + r, 0.0)
    fm.AddArc2(0.0, -r, 90)  # small fillet
    fm.AddPoint(dia, -length + tip_length)
    fm.AddPoint(0.0, -length)

    return fm.GetFace()

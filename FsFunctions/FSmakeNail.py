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
    - DIN1143:      Round plain head nails for use in automatic nailing machines
    - DIN1144-A:    Nails for the installation of wood wool composite panels
    - DIN1151[A/B]: Round plain head and countersunk head wire nails
    - DIN1152:      Round lost head wire nails
    - DIN1160[A/B]: Clout or slate nails
    """
    # NOTE: Details left unspecified are to be selected as appropiate

    if fa.baseType[:7] == "DIN1143":
        d1, d2, l = fa.dimTable
        nail = self.RevolveZ(makeCountersunkHeadFace(d1, l, 1.3 * d2, csnk_ang=140))
        # Cutter ring
        fm = FSFaceMaker()
        fm.AddPoint(d2 / 2, 0)
        fm.AddPoint(1.5 * d2 / 2, 0)
        fm.AddPoint(d2 / 2, -d2 / 2)
        return nail.cut(self.RevolveZ(fm.GetFace()))
    elif fa.baseType[:7] == "DIN1144":
        # TODO: type B square head
        d, l = fa.dimTable
        nail = self.RevolveZ(makePlainHeadFace(d, l, 20, 1))
        fm = FSFaceMaker()
        fm.AddPoint(0.0, 0.6 * d)
        fm.AddArc2(0.0, -d / 2, -180)
        return nail.fuse(self.RevolveZ(fm.GetFace()))
    elif fa.baseType[:7] == "DIN1151":
        d, l = fa.dimTable
        if fa.baseType == "DIN1151-A":
            face = makePlainHeadFace(d, l, 2 * d, d / 4)
        else:
            face = makeCountersunkHeadFace(d, l, 3 * d, csnk_ang=120)
        return self.RevolveZ(face)
    elif fa.baseType[:7] == "DIN1152":
        d, l = fa.dimTable
        return self.RevolveZ(makePlainHeadFace(d, l, 1.25 * d, 1.5 * d))
    elif fa.baseType[:7] == "DIN1160":
        d, l, _, d2 = fa.dimTable
        return self.RevolveZ(makePlainHeadFace(d, l, d2, d / 5))

    raise NotImplementedError(f"Unknown fastener type: {fa.baseType}")


def makePlainHeadFace(dia, length, head_w, head_th, p_angle=40):
    """Make the face for a plain head with semi-sphere and point end nail."""
    tip_length = (dia / 2) / math.tan(math.radians(p_angle / 2))
    r = dia / 10
    fm = FSFaceMaker()
    fm.AddPoint(0.0, head_th)
    fm.AddPoint(head_w / 2, head_th)
    fm.AddPoint(head_w / 2, 0.0)
    fm.AddPoint(dia / 2 + r, 0.0)
    fm.AddArc2(0.0, -r, 90)  # small fillet
    fm.AddPoint(dia / 2, -length + tip_length)
    fm.AddPoint(0.0, -length)

    return fm.GetFace()


def makeCountersunkHeadFace(dia, length, head_w, p_angle=40, csnk_ang=120):
    """Make the face for a countersunk head and point end nail."""
    # Calc distance in z to comply with countersunk the angle given
    zz = (head_w - dia) / (2 * math.tan(math.radians(csnk_ang / 2)))
    tip_length = dia / (2 * math.tan(math.radians(p_angle / 2)))
    fm = FSFaceMaker()
    fm.AddPoint(0.0, 0.0)
    fm.AddPoint(head_w / 2, 0.0)
    fm.AddPoint(dia / 2, -zz)
    fm.AddPoint(dia / 2, -length + zz + tip_length)
    fm.AddPoint(0.0, -length + zz)

    return fm.GetFace()

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
import FastenerBase

# ASMEB18.5.2 UNC Round head square neck bolts
# DIN603 Mushroom head square neck bolts
cos22_5 = math.cos(math.radians(22.5))
sin22_5 = math.sin(math.radians(22.5))


def makeCarriageBolt(self, fa):  # dynamically loaded method of class Screw
    SType = fa.baseType
    length = fa.calc_len
    d = self.getDia(fa.calc_diam, False)
    if SType == 'ASMEB18.5.2':
        tpi, _, A, H, O, P, _, _ = fa.dimTable
        A, H, O, P = (25.4 * x for x in (A, H, O, P))
        pitch = 25.4 / tpi
        if length <= 152.4:
            L_t = d * 2 + 6.35
        else:
            L_t = d * 2 + 12.7
    elif SType == 'DIN603':
        pitch, b1, b2, b3, dk_max, dk_min, ds_max, ds_min, f_max, f_min, \
            k_max, k_min, r1_approx, r2_max, r2_max, v_max, v_min = fa.dimTable
        A = (dk_max+dk_min)/2
        H = k_max
        O = v_max
        P = f_max
        if length <= 125:
            L_t = b1
        elif (125 < length) and (length <= 200):
            L_t = b2
        else:  # len > 200
            L_t = b3
    head_r = A / sqrt2
    flat_len = length - P

    # create a profile for head generation.
    # Basially when this profile revolves we get the head solid
    # FSFaceMaker is a nice helper to build a profile from lines and arcs.
    # It make a profile on the x,z plane
    fm = FastenerBase.FSFaceMaker()
    fm.AddPoint(0, H)
    r_fillet = d * 0.05
    # angle for determining an approximate fillet at the outer edge
    theta = math.pi / 4
    fm.AddArc(
        head_r * math.sin(theta / 2),
        head_r * math.cos(theta / 2) - head_r + H,
        A / 2 - r_fillet + r_fillet * math.sin(theta),
        r_fillet * (1 + math.cos(theta)),
    )
    fm.AddArc(A / 2, r_fillet, A / 2 - r_fillet, 0)
    fm.AddPoint(sqrt2 / 2 * O, 0)
    fm.AddPoint(sqrt2 / 2 * O, -1 * P + (sqrt2 / 2 * O - d / 2))
    fm.AddPoint(d / 2, -1 * P)
    if (flat_len > L_t):
        if not fa.Thread:
            fm.AddPoint(d / 2, -length + L_t)
        thread_length = L_t
    else:
        thread_length = flat_len
    fm.AddPoint(d / 2, -length + d / 10)
    fm.AddPoint(d / 2 - d / 10, -length)
    fm.AddPoint(0, -length)
    p_solid = self.RevolveZ(fm.GetFace())
    # cut 4 flats under the head
    d_mod = d + 0.0002
    outerBox = Part.makeBox(
        A * 4,
        A * 4,
        P + 0.0001,
        Base.Vector(-A * 2, -A * 2, -P + 0.0001)
    )
    innerBox = Part.makeBox(
        d_mod,
        d_mod,
        P * 3,
        Base.Vector(-d_mod / 2, -d_mod / 2, -P * 2)
    )
    # add fillets to the square cutting tool
    edgelist = innerBox.Edges
    edges_to_fillet = []
    for edge in edgelist:
        if (
            abs(abs(edge.CenterOfMass.x) - d_mod / 2) < 0.0001 and
            abs(abs(edge.CenterOfMass.y) - d_mod / 2) < 0.0001
        ):
            edges_to_fillet.append(edge)
    innerBox = innerBox.makeFillet(d * 0.08, edges_to_fillet)
    tool = outerBox.cut(innerBox)
    p_solid = p_solid.cut(tool)
    if fa.Thread:
        thread_cutter = self.CreateBlindThreadCutter(d, pitch, thread_length)
        thread_cutter.translate(
            Base.Vector(0.0, 0.0, -1 * (length - thread_length))
        )
        p_solid = p_solid.cut(thread_cutter)
    return Part.Solid(p_solid)

# -*- coding: utf-8 -*-
"""
***************************************************************************
*   Copyright (c) 2023, 2024                                              *
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
from FreeCAD import Base
import FastenerBase
from screw_maker import FsData

def makeSelfTappingScrew(self, fa):
    """
    Make a self tapping screw, used on sheet metal and plastic holes
    Supported types:
    - ISO7049-[C/F/R]: Cross-recessed pan head tapping screws
    """
    if fa.baseType[:7] == "ISO7049":
        return makeISO7049(self, fa)

    raise NotImplementedError(f"Unknown fastener type: {fa.baseType}")

def makeISO7049(self, fa):
    """
    Make an ISO7049 Cross-recessed pan head tapping screw
    Variations:
    - ISO7049-C: Self tapping screw with conical point
    - ISO7049-F: Self tapping screw with flat point
    - ISO7049-R: Self tapping screw with round point
    """
    SType = fa.baseType
    l = fa.calc_len
    # Convert from string "ST x.y" to x.y float
    dia = self.getDia(fa.calc_diam, False)

    # NOTE: The norm ISO1478 defines: "Tapping screws thread"
    # Read data from the thread norm definition
    # instead of duplicating it on the screw definition.
    P, _, _, d2, _, d3, _, _, rR, _, _, _, _ = FsData["iso1478def"][fa.calc_diam]
    _, D, _, K, _, r, _, PH, m, h, _ = fa.dimTable

    b = l # length for the thread from the tip
    full_length = True

    ri = d2 / 2.0   # inner thread radius
    ro = dia / 2.0  # outer thread radius

    # inner radius of screw section
    sr = ro
    if fa.Thread:
        sr = ri

    # length of cylindrical part where thread begins to grow.
    slope_length = ro - ri

    # Sharpness of screw tip is equal 45 degrees. If imagine half of screw tip
    # as a triangle, then acute-angled angle of the triangle (alpha) be which
    # is equal to half of the screw tip angle.
    alpha = 45
    # And the adjacent cathetus be which is equal to least screw radius (sr)
    # Then the opposite cathetus can be getted by formula: tip_length=sr/tg(alpha)
    tip_length = sr / math.tan(math.radians(alpha / 2))
    if SType == "ISO7049-F":
        tip_length = sr - d3 / 2

    fm = FastenerBase.FSFaceMaker()

    # 1) screw head
    fm.AddPoint(0, K)
    fm.AddBSpline(D/2, K, D/2, 0)

    # 2) add rounding under screw head
    rr = r
    fm.AddPoint(ro+rr, 0)      # first point of rounding
    if fa.Thread and full_length:
        fm.AddBSpline(ro, 0, sr, -slope_length) # create spline rounding
    else:
        fm.AddArc2(+0, -rr, 90) # in other cases create arc rounding

    # 3) cylindrical part (place where thread will be added)
    if not full_length:
        if fa.Thread:
            fm.AddPoint(ro, -l+b+slope_length)    # entery point of thread
        fm.AddPoint(sr, -l+b)   # start of full width thread b >= l*0.6

    # 4) tip shape
    if SType == "ISO7049-C":
        fm.AddPoint(sr, -l+tip_length)
        fm.AddPoint(0, -l)
    if SType == "ISO7049-F":
        fm.AddPoint(sr, -l+tip_length)
        fm.AddPoint(d3 / 2, -l)
        fm.AddPoint(0, -l)
    if SType == "ISO7049-R":
        fm.AddPoint(sr, -l+tip_length)
        fm.AddPoint(rR*math.cos(math.radians(alpha)), rR-l)
        fm.AddArc2(-rR*math.cos(math.radians(alpha)),
                   rR*math.sin(math.radians(alpha)), -alpha)

    # make screw solid body by revolve a profile
    screw = self.RevolveZ(fm.GetFace())

    # make cross slot in screw head
    recess = self.makeHCrossRecess(PH, m)
    recess = recess.translate(Base.Vector(0.0, 0.0, h))
    screw = screw.cut(recess)

    # make thread
    if fa.Thread:
        if SType == "ISO7049-C":
            # vanilla usage
            thread = self.makeDin7998Thread(-l+b+slope_length, -l+tip_length,
                                            -l, ri, ro, P)
        if SType == "ISO7049-F":
            # sent flag to omit the tip thread
            thread = self.makeDin7998Thread(-l+b+slope_length, -l+tip_length,
                                            -l, ri, ro, P, True)
        if SType == "ISO7049-R":
            # move the tip a little up to compensate roundness
            thread = self.makeDin7998Thread(-l+b+slope_length, -l+tip_length,
                                            -l+rR, ri, ro, P)
        screw = screw.fuse(thread)

    return screw

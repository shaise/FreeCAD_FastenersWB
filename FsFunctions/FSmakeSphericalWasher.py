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


# make Washer
# DIN6319C Spherical Washer
# DIN6319D Conical Seat
# DIN6319G Conical Seat


def makeSphericalWasher(self, fa):
    """Creates a Spherical Washer / Conical Seat.
    Supported types:
    - DIN6319C Spherical Washer
    - DIN6319D Conical Seat
    - DIN6319G Conical Seat
    """

    if fa.baseType == "DIN6319C":
        d1, d3, d5, f1, h1, h2, r1, csh_diam = fa.dimTable
    
        Phi_Start = math.asin(d1 / (2. * r1))
        Phi_End = math.asin(d3 / (2. * r1))
        Delta_Phi = Phi_End - Phi_Start
        Center_Z = r1 * math.cos(Phi_Start)
    
        Sqrt3 = math.sqrt(3.)
        # comments please see: Doc\DIN6319 Calculation Overlap hz.pdf
        hZ = (Sqrt3 * d5 + math.sqrt(36. * r1**2 - 9. * d1**2) - 4. * Sqrt3 * r1) / 6
    
        fm = FastenerBase.FSFaceMaker()
        fm.StartPoint(d1 / 2., -hZ)
        fm.AddArc2(-d1 / 2., Center_Z, math.degrees(Delta_Phi))
        fm.AddPoint(d3 / 2., h2 - hZ)
        fm.AddPoint(d1 / 2. + f1, h2 - hZ)
        fm.AddPoint(d1 / 2., h2 - f1 - hZ)
    
        washer_body = self.RevolveZ(fm.GetFace())
    
    elif fa.baseType == "DIN6319D" or fa.baseType == "DIN6319G":
        d2, d4, d5, h3 = fa.dimTable
        
        tan30 = math.tan(math.radians(30.))
        chamfer_X = (d5 - d2) / 2.
        chamfer_Z = chamfer_X * tan30
        
        fm = FastenerBase.FSFaceMaker()
        fm.StartPoint(d2 / 2., 0.)
        fm.AddPoint(d4 / 2., 0.)
        fm.AddPoint(d4 / 2., h3)
        fm.AddPoint(d5 / 2., h3)
        fm.AddPoint(d2 / 2., h3 - chamfer_Z)

        washer_body = self.RevolveZ(fm.GetFace())

    return washer_body

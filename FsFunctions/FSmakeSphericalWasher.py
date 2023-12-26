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
        # to determine Hz, use sympy:
        # ``` python
        # from sympy import *
        #
        # vars = d1, d5, dz, hz, hz1, hz2, r1, rx, rz = symbols(
        #     "d1, d5, dz, hz, hz1, hz2, r1, rx, rz"
        # )
        # print(f"Variables:\n{vars}\n")
        # equations = [
        #     Eq(hz, hz1 + hz2),
        #     Eq(tan(pi / 6), hz1 / (d5 / 2 - rx)),
        #     Eq(tan(pi / 6), rx / rz),
        #     Eq(r1, rz + hz2 + dz),
        #     Eq(sin(pi / 6), rx / r1),
        #     Eq(r1**2, (d1 / 2) ** 2 + (r1 - dz) ** 2),
        # ]
        # print("Equations:")
        # for e in equations:
        #     print(e)
        # print("\nGeneral Solution for Hz:")
        # values = solve([*equations], (dz, hz, hz1, hz2, rx, rz), dict=True)[0]
        # print(f"hz={values[hz]}")
        # # known values for size M20
        # known_values = [Eq(d1, 21), Eq(d5, 31), Eq(r1, 27)]
        # print("\nKnown:")
        # for e in known_values:
        #     print(e)
        # values = solve([*equations, *known_values], vars, dict=True)[0]
        # print(f"\nResults:\nhz={values[hz].n()}")
        # ```
        #
        # results:
        # ```
        # Variables:
        # (d1, d5, dz, hz, hz1, hz2, r1, rx, rz)
        #
        # Equations:
        # Eq(hz, hz1 + hz2)
        # Eq(sqrt(3)/3, hz1/(d5/2 - rx))
        # Eq(sqrt(3)/3, rx/rz)
        # Eq(r1, dz + hz2 + rz)
        # Eq(1/2, rx/r1)
        # Eq(r1**2, d1**2/4 + (-dz + r1)**2)
        #
        # General Solution for Hz:
        # hz=sqrt(3)*d5/6 - 2*sqrt(3)*r1/3 + sqrt(-d1**2 + 4*r1**2)/2
        #
        # Known:
        # Eq(d1, 21)
        # Eq(d5, 31)
        # Eq(r1, 27)
        #
        # Results:
        # hz=2.64670056386491
        # ```
        # see also Doc/Dev/DIN6319_calculations.md
        hZ = (sqrt3 * d5 + math.sqrt(36. * r1**2 - 9. * d1**2) - 4. * sqrt3 * r1) / 6

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

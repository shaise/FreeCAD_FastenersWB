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


def makeScrewDie(self, fa):
    """make object to cut external threads on a shaft"""
    ThreadType = fa.calc_diam
    if fa.diameter != "Custom":
        dia = self.getDia(ThreadType, False)
        if fa.type == "ScrewDie":
            P, tunIn, tunEx = fa.dimTable
        elif fa.type == "ScrewDieInch":
            P = fa.dimTable[0]
    else:  # custom pitch and diameter
        P = fa.calc_pitch
        if self.sm3DPrintMode:
            dia = self.smScrewThrScaleA * float(fa.calc_diam) + self.smScrewThrScaleB
        else:
            dia = float(fa.calc_diam)
    if fa.thread:
        cutDia = self.GetInnerThreadMinDiameter(dia, P, 0.0)
    else:
        cutDia = dia
    length = fa.calc_len
    refpoint = Base.Vector(0, 0, -1 * length)
    screwDie = Part.makeCylinder(dia * 1.1 / 2, length, refpoint)
    screwDie = screwDie.cut(Part.makeCylinder(cutDia / 2, length, refpoint))
    if fa.thread:
        thread_cutter = self.CreateInnerThreadCutter(dia, P, length + 2 * P)
        thread_cutter.rotate(
            Base.Vector(0.0, 0.0, 0.0),
            Base.Vector(1.0, 0.0, 0.0),
            180
        )
        screwDie = screwDie.cut(thread_cutter)
    return screwDie

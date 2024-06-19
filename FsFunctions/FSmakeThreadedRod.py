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


def makeThreadedRod(self, fa):
    """make a length of standard threaded rod"""
    ThreadType = fa.calc_diam
    if fa.Diameter != 'Custom':
        dia = self.getDia(ThreadType, False)
        if fa.baseType == 'ThreadedRod':
            P, tunIn, tunEx = fa.dimTable
        elif fa.baseType == 'ThreadedRodInch':
            P = fa.dimTable[0]
    else:  # custom pitch and diameter
        P = fa.calc_pitch
        if self.sm3DPrintMode:
            dia = self.smScrewThrScaleA * float(fa.calc_diam) + self.smScrewThrScaleB
        else:
            dia = float(fa.calc_diam)
    #dia = dia * 1.01
    cham = P
    length = fa.calc_len
    fm = FSFaceMaker()
    fm.AddPoint(0, 0)
    fm.AddPoint(dia / 2 - cham, 0)
    fm.AddPoint(dia / 2, 0 - cham)
    fm.AddPoint(dia / 2, -1 * length + cham)
    fm.AddPoint(dia / 2 - cham, -1 * length)
    fm.AddPoint(0, -1 * length)
    screw = self.RevolveZ(fm.GetFace())
    if fa.Thread:
        # make the threaded section
        thread_cutter = self.CreateThreadCutter(dia, P, length)
        screw = screw.cut(thread_cutter)
    return screw

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

# make object to cut external threads on a shaft
def makeScrewDie(self, fa): # dynamically loaded method of class Screw
    ThreadType = fa.calc_diam
    if ThreadType != "Custom":
        dia = self.getDia(ThreadType, False)
        if fa.type == "ScrewDie":
            P, tunIn, tunEx = fa.dimTable
        elif fa.type == "ScrewDieInch":
            P = fa.dimTable[0]
    else:  # custom pitch and diameter
        P = fa.calc_pitch
        if self.sm3DPrintMode:
            dia = self.smScrewThrScaleA * fa.calc_diam + self.smScrewThrScaleB
        else:
            dia = fa.calc_diam
    if fa.thread:
        cutDia = dia * 0.75
    else:
        cutDia = dia
    l = fa.calc_len
    refpoint = Base.Vector(0, 0, -1 * l)
    screwDie = Part.makeCylinder(dia * 1.1 / 2, l, refpoint)
    screwDie = screwDie.cut(Part.makeCylinder(cutDia / 2, l, refpoint))
    if fa.thread:
        shell_thread = self.makeShellthread(dia, P, l, False, 0)
        thr_p1 = Base.Vector(0, 0, 0)
        thr_p2 = Base.Vector(dia / 2, 0, 0)
        thr_e1 = Part.makeLine(thr_p1, thr_p2)
        thr_cap_profile = Part.Wire([thr_e1])
        thr_cap = self.RevolveZ(thr_cap_profile)
        #Part.show(thr_cap)
        #Part.show(shell_thread)
        thr_faces = shell_thread.Faces
        thr_faces.extend(thr_cap.Faces)
        thread_shell = Part.Shell(thr_faces)
        thread_solid = Part.Solid(thread_shell)
        screwDie = screwDie.cut(thread_solid)
    return screwDie

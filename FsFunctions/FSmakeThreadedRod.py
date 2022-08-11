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

# make a length of standard threaded rod

def makeThreadedRod(self): # dynamically loaded method of class Screw
    ThreadType = self.fastenerDiam
    if ThreadType != 'Custom':
        dia = self.getDia(ThreadType, False)
        if self.fastenerType == 'ThreadedRod':
            P, tunIn, tunEx = FsData['tuningTable'][ThreadType]
        elif self.fastenerType == 'ThreadedRodInch':
            P = FsData['asmeb18.3.1adef'][ThreadType][0]
    else:  # custom pitch and diameter
        P = self.customPitch
        if self.sm3DPrintMode:
            dia = self.smScrewThrScaleA * self.customDia + self.smScrewThrScaleB
        else:
            dia = self.customDia
    dia = dia * 1.01
    cham = P
    l = self.fastenerLen
    p0 = Base.Vector(0, 0, 0)
    p1 = Base.Vector(dia / 2 - cham, 0, 0)
    p2 = Base.Vector(dia / 2, 0, 0 - cham)
    p3 = Base.Vector(dia / 2, 0, -1 * l + cham)
    p4 = Base.Vector(dia / 2 - cham, 0, -1 * l)
    p5 = Base.Vector(0, 0, -1 * l)
    e1 = Part.makeLine(p0, p1)
    e2 = Part.makeLine(p1, p2)
    e3 = Part.makeLine(p2, p3)
    e4 = Part.makeLine(p3, p4)
    e5 = Part.makeLine(p4, p5)
    p_profile = Part.Wire([e1, e2, e3, e4, e5])
    p_shell = p_profile.revolve(Base.Vector(0.0, 0.0, 0.0), Base.Vector(0.0, 0.0, 1.0), 360.0)
    screw = Part.Solid(p_shell)
    if self.rThread:
        # make the threaded section
        shell_thread = self.makeShellthread(dia, P, l, False, 0)
        thr_p1 = Base.Vector(0, 0, 0)
        thr_p2 = Base.Vector(dia / 2, 0, 0)
        thr_e1 = Part.makeLine(thr_p1, thr_p2)
        thr_cap_profile = Part.Wire([thr_e1])
        thr_cap = thr_cap_profile.revolve(Base.Vector(0, 0, 0), Base.Vector(0, 0, 1), 360)
        thr_faces = shell_thread.Faces
        thr_faces.extend(thr_cap.Faces)
        thread_shell = Part.Shell(thr_faces)
        thread_solid = Part.Solid(thread_shell)
        screw = screw.common(thread_solid)
    return screw

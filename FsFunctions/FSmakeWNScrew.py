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

sin45 = math.sin(math.radians(45))

def add14xxStem(obj, fm, dia, core_dia, len, clean_len, isRealThread, diagStartx = 0.0):
    r1 = dia / 2
    r2 = ((dia / 20) // 0.05) * 0.05
    cd2 = core_dia / 2.0
    thl = (r1 - cd2) / 2.0
    if diagStartx > 0.0: 
        # cone under-head shape
        r2 *= 2
        r2sin45 = r2 * sin45
        diagx = cd2 + r2 - r2sin45
        diagy = diagx - diagStartx
        fm.AddPoint(diagx, diagy)
        fm.AddArc2(r2sin45, -r2sin45, 45)
    else:
        # flat under-head shape 
        fm.AddPoint(cd2 + r2, 0)
        fm.AddArc2(0, -r2, 90)
    if not isRealThread:
        # create psudo thread
        fm.AddPoint(cd2, -clean_len)
        fm.AddPoint(r1, -clean_len - thl)
        fm.AddPoint(r1, -len + thl)
    fm.AddPoint(cd2, -len)
    fm.AddPoint(0, -len)
    sectionFace = fm.GetFace()
    # Part.show(sectionFace)
    shape = obj.RevolveZ(sectionFace)
    return shape

def makeWN1451Body(obj, calc_diam, dia, core_dia, len, clean_len, isRealThread):
    d, k, DriveSize, t_mean, s = FsData["WN1451head"][calc_diam]
    d2 = d / 2.0
    p1 = d2 * 13.0 / 25.0
    p2 = d2 * 18.0 / 25.0
    p3 = d2 * 20.0 / 25.0
    k2 = s + (k - s) / 2
    fm = FSFaceMaker()
    fm.AddPoint(0.0, k)
    fm.AddPoint(p1, k)
    fm.AddArc(p2, k2, p3 , s)
    fm.AddPoint(d2 , s)
    fm.AddPoint(d2 , 0)
    shape = add14xxStem(obj, fm, dia, core_dia, len, clean_len, isRealThread)
    recess = obj.makeHexalobularRecess(DriveSize, t_mean, True)
    recess.translate(Base.Vector(0, 0, k))
    shape = shape.cut(recess)
    return shape

def makeWN1452Body(obj, calc_diam, dia, core_dia, len, clean_len, isRealThread):
    d, k, DriveSize, t_mean = FsData["WN1452head"][calc_diam]
    d2 = d / 2.0
    p1 = d2 * 14.0 / 23.0
    p2 = d2 * 20.0 / 23.0
    s = k * 2.0 / 3.0
    k2 = s + (k - s) / 2
    r2 = ((dia / 20) // 0.05) * 0.05
    fm = FSFaceMaker()
    fm.AddPoint(0.0, k)
    fm.AddPoint(p1, k)
    fm.AddArc(p2, k2, d2 , s)
    fm.AddPoint(d2 , r2)
    fm.AddArc2(-r2, 0, -90)
    shape = add14xxStem(obj, fm, dia, core_dia, len, clean_len, isRealThread)
    recess = obj.makeHexalobularRecess(DriveSize, t_mean, True)
    recess.translate(Base.Vector(0, 0, k))
    shape = shape.cut(recess)
    return shape

def makeWN1453Body(obj, calc_diam, dia, core_dia, len, clean_len, isRealThread):
    d, c, f, DriveSize, t_mean = FsData["WN1453head"][calc_diam]
    # overriding d and c as it seems the datasheet numbers are wrong
    d = dia * 36.0 / 23.0
    c = f / 5
    d2 = d / 2.0
    p1 = d2 * 10.0 / 16.0
    p2 = d2 * 14.0 / 16.0
    f2 = c + (f - c) / 2
    fm = FSFaceMaker()
    fm.AddPoint(0.0, f)
    fm.AddPoint(p1, f)
    fm.AddArc(p2, f2, d2 , c)
    fm.AddPoint(d2 , 0)
    clean_len = clean_len / 2.0 + d2 - core_dia / 2.0
    shape = add14xxStem(obj, fm, dia, core_dia, len, clean_len, isRealThread, d2)
    recess = obj.makeHexalobularRecess(DriveSize, t_mean, True)
    recess.translate(Base.Vector(0, 0, f))
    shape = shape.cut(recess)
    return shape, clean_len

def makeWN1423Body(obj, calc_diam, dia, core_dia, len, clean_len, isRealThread):
    d, c, DriveSize, t_mean = FsData["WN1423head"][calc_diam]
    d2 = d / 2.0
    fm = FSFaceMaker()
    fm.AddPoint(0.0, c)
    fm.AddPoint(d2, c)
    fm.AddPoint(d2 , 0)
    print ("diag=",d2 - core_dia)
    clean_len = clean_len / 2.0 + d2 - core_dia / 2.0
    shape = add14xxStem(obj, fm, dia, core_dia, len, clean_len, isRealThread, d2)
    recess = obj.makeHexalobularRecess(DriveSize, t_mean, True)
    recess.translate(Base.Vector(0, 0, c))
    shape = shape.cut(recess)
    return shape, clean_len

def makeWN1411Body(obj, calc_diam, dia, core_dia, len, clean_len, isRealThread, recessType):
    d, k, s, hcrw, crs = FsData["WN1411head"][calc_diam]
    d2 = d / 2.0
    p1 = d2 * 19.0 / 28.0
    p2 = d2 * 23.0 / 28.0
    k2 = s + (k - s) / 2
    fm = FSFaceMaker()
    fm.AddPoint(0.0, k)
    fm.AddArc(p1, k2, p2 , s)
    fm.AddPoint(d2 , s)
    fm.AddPoint(d2 , 0)
    shape = add14xxStem(obj, fm, dia, core_dia, len, clean_len, isRealThread)
    if recessType == "A":
        recess = obj.makeHCrossRecess(crs, hcrw)
    # else it is a Z cross recess - not implemented yet
    recess.translate(Base.Vector(0, 0, k))
    shape = shape.cut(recess)
    return shape

def makeWN1412Body(obj, calc_diam, dia, core_dia, len, clean_len, isRealThread, recessType):
    d, k, hcrw, crs = FsData["WN1412head"][calc_diam]
    d2 = d / 2.0
    p1 = d2 * 19.0 / 23.0
    s = k * 0.4
    k2 = s + (k - s) / 2
    r2 = ((dia / 16) // 0.05) * 0.05
    fm = FSFaceMaker()
    fm.AddPoint(0.0, k)
    fm.AddArc(p1, k2, d2 , s)
    fm.AddPoint(d2 , r2)
    fm.AddArc2(-r2, 0, -90)
    shape = add14xxStem(obj, fm, dia, core_dia, len, clean_len, isRealThread)
    if recessType == "A":
        recess = obj.makeHCrossRecess(crs, hcrw)
    # else it is a Z cross recess - not implemented yet
    recess.translate(Base.Vector(0, 0, k))
    shape = shape.cut(recess)
    return shape

def makeWN1413Body(obj, calc_diam, dia, core_dia, len, clean_len, isRealThread, recessType):
    d, c, hcrw, crs = FsData["WN1413head"][calc_diam]
    d2 = d / 2.0
    fm = FSFaceMaker()
    fm.AddPoint(0.0, c)
    fm.AddPoint(d2, c)
    fm.AddPoint(d2 , 0)
    print ("diag=",d2 - core_dia)
    clean_len = clean_len / 2.0 + d2 - core_dia / 2.0
    shape = add14xxStem(obj, fm, dia, core_dia, len, clean_len, isRealThread, d2)
    if recessType == "A":
        recess = obj.makeHCrossRecess(crs, hcrw)
    # else it is a Z cross recess - not implemented yet
    recess.translate(Base.Vector(0, 0, c))
    shape = shape.cut(recess)
    return shape, clean_len

def makeWN1446Body(obj, calc_diam, dia, core_dia, len, clean_len, isRealThread):
    af, k = FsData["WN1446head"][calc_diam]
    d2 = af * 1.14 / 2.0
    p1 = d2 * 16.0 / 21.0
    s = 0.76 * k
    r = d2 * 3.0 / 21.0
    fm = FSFaceMaker()
    fm.AddPoint(0.0, s)
    fm.AddPoint(p1, s)
    fm.AddPoint(p1, k)
    fm.AddPoint(d2 - r, k)    
    fm.AddArc2(0, -r, -90)
    fm.AddPoint(d2 , r)
    fm.AddArc2(-r, 0, -90)
    shape = add14xxStem(obj, fm, dia, core_dia, len, clean_len, isRealThread)
    tool = obj.makeHexCutter(af * 2, af, k + 1.0)
    tool.translate(Base.Vector(0, 0, -0.01))
    shape = shape.cut(tool)
    return shape

def makeWN1447Body(obj, calc_diam, dia, core_dia, len, clean_len, isRealThread):
    af, k, d, s = FsData["WN1447head"][calc_diam]
    d2 = d / 2.0
    din = af * 1.16 / 2.0
    p1 = din * 16.0 / 21.0
    s1 = 0.84 * k
    r = din * 3.0 / 21.0
    fm = FSFaceMaker()
    fm.AddPoint(0.0, s1)
    fm.AddPoint(p1, s1)
    fm.AddPoint(p1, k)
    fm.AddPoint(din - r, k)    
    fm.AddArc2(0, -r, -90)
    fm.AddPoint(din , s + 0.01)
    fm.AddPoint(d2 , s + 0.01)
    fm.AddPoint(d2 , 0)
    shape = add14xxStem(obj, fm, dia, core_dia, len, clean_len, isRealThread)
    tool = obj.makeHexCutter(d2 * 2, af, k)
    tool.translate(Base.Vector(0, 0, s))
    shape = shape.cut(tool)
    return shape


def makeWNScrew(self, fa):
    """make a length of standard threaded rod"""
    dia = self.getDia(fa.calc_diam, False)
    len = fa.calc_len
    rad = dia / 2
    P, core_dia = fa.dimTable
    #clean_len = dia if len > 3 * P else rad
    clean_len = dia / 3
    if fa.baseType == "WN1451":
        screw = makeWN1451Body(self, fa.calc_diam, dia, core_dia, len, clean_len, fa.Thread)
    elif fa.baseType == "WN1452":
        screw = makeWN1452Body(self, fa.calc_diam, dia, core_dia, len, clean_len, fa.Thread)
    elif fa.baseType == "WN1453":
        screw, clean_len = makeWN1453Body(self, fa.calc_diam, dia, core_dia, len, clean_len, fa.Thread)
    elif fa.baseType == "WN1423":
        screw, clean_len = makeWN1423Body(self, fa.calc_diam, dia, core_dia, len, clean_len, fa.Thread)
    elif fa.baseType == "WN1411A": # or fa.baseType == "WN1411B"
        screw = makeWN1411Body(self, fa.calc_diam, dia, core_dia, len, clean_len, fa.Thread, "A")
    elif fa.baseType == "WN1412A": # or fa.baseType == "WN1412B"
        screw = makeWN1412Body(self, fa.calc_diam, dia, core_dia, len, clean_len, fa.Thread, "A")
    elif fa.baseType == "WN1413A": # or fa.baseType == "WN1413B"
        screw, clean_len = makeWN1413Body(self, fa.calc_diam, dia, core_dia, len, clean_len, fa.Thread, "A")
    elif fa.baseType == "WN1446":
        screw = makeWN1446Body(self, fa.calc_diam, dia, core_dia, len, clean_len, fa.Thread)
    elif fa.baseType == "WN1447":
        screw = makeWN1447Body(self, fa.calc_diam, dia, core_dia, len, clean_len, fa.Thread)

    if fa.Thread:
        tool = self.CreateWNThreadTool(dia, P, core_dia, len - clean_len)
        tool.translate(Base.Vector(0,0,-len + 0.01))
        screw = screw.fuse(tool)
    return screw

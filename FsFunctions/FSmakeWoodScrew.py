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

def makeWoodScrew(self, fa): # dynamically loaded method of class Screw
    SType = fa.type
    if SType == "DIN571":
        return makeDIN571(self, fa)
    elif SType == "DIN96" or SType == "GOST1144-1" or SType == "GOST1144-2":
        return makeDIN96_GOST1144(self, fa)

# DIN 571 wood-screw

def makeDIN571(screw_obj, fa):
    SType = fa.type
    l = fa.calc_len
    dia = float(fa.calc_diam.split()[0])
    ds, da, d3, k, s, P = fa.dimTable
    d = dia / 2.0
    d3h = d3 / 2.0
    r = (da-ds)/2.0
    e = s/math.cos(math.radians(30))
    sqrt2_ = 1.0 / math.sqrt(2.0)
    cham = (e - s) * math.sin(math.radians(15))  # needed for chamfer at head top
    
    Pnt0 = Base.Vector(0.0, 0.0, k)
    Pnt2 = Base.Vector(s / 2.0, 0.0, k)
    Pnt3 = Base.Vector(s / math.sqrt(3.0), 0.0, k - cham)
    Pnt4 = Base.Vector(s / math.sqrt(3.0), 0.0, 0.0)
    Pnt7 = Base.Vector(d + r, 0.0, 0.0)  # start of fillet between head and shank
    Pnt8 = Base.Vector(d + r - r * sqrt2_, 0.0, -r + r * sqrt2_)  # arc-point of fillet
    Pnt9 = Base.Vector(d, 0.0, -r)  # end of fillet

    edge1 = Part.makeLine(Pnt0, Pnt2)
    edge2 = Part.makeLine(Pnt2, Pnt3)
    edge3 = Part.makeLine(Pnt3, Pnt4)
    edge4 = Part.makeLine(Pnt4, Pnt7)
    edge5 = Part.Arc(Pnt7, Pnt8, Pnt9).toShape()

    # create cutting tool for hexagon head
    # Parameters s, k, outer circle diameter =  e/2.0+10.0
    extrude = screw_obj.makeHextool(s, k, s * 2.0)

    #if fa.thread:
    #  pass
    #else:
    if fa.thread:
        dt = d3 / 2.0
    else:
        dt = d
    angle = math.radians(20)
    x2 = dt * math.cos(angle)
    z2 = dt * math.sin(angle)
    z3 = x2 / math.tan(angle)
    ftl = l - z2 - z3 # flat part (total length - tip)
    PntB0 = Base.Vector(d, 0.0, 0.4 * -ftl)
    PntB1 = Base.Vector(dt, 0.0, -ftl)
    PntB2 = Base.Vector(dt * math.cos(angle / 2.0),
                        0.0,
                        -l + z2 + z3 - d * math.sin(angle / 2.0))
    PntB3 = Base.Vector(x2, 0.0, -l + z3)
    PntB4 = Base.Vector(0.0, 0.0, -l)
    
    edge6 = Part.makeLine(Pnt9, PntB0)
    edge8 = Part.Arc(PntB1, PntB2, PntB3).toShape()
    edge9 = Part.makeLine(PntB3, PntB4)
    edgeZ0 = Part.makeLine(PntB4, Pnt0)
    
    if fa.thread:
        PntB0t = Base.Vector(dt, 0.0, 0.4 * -ftl - (d - dt))
        edge7 = Part.makeLine(PntB0, PntB0t)
        edge7t = Part.makeLine(PntB0t, PntB1)
        aWire = Part.Wire([edge1, edge2, edge3, edge4, edge5, edge6,\
                        edge7, edge7t, edge8, edge9, edgeZ0])
    else:
        edge7 = Part.makeLine(PntB0, PntB1)
        aWire = Part.Wire([edge1, edge2, edge3, edge4, edge5, edge6,\
                        edge7, edge8, edge9, edgeZ0])
    
    aFace = Part.Face(aWire)
    # Part.show(aFace)
    head = screw_obj.RevolveZ(aFace)
    head = head.cut(extrude)
    if fa.thread:
        thread = screw_obj.makeDin7998Thread(0.4 * -ftl, -ftl, -l, d3h, d, P)
        #Part.show(thread)
        head = head.fuse(thread)
    
    return head

# DIN 96 or GOST1144 wood-screw

def makeDIN96_GOST1144(screw_obj, fa):
    l = fa.calc_len
        SType = fa.type
    b = 0.4
    # 2 and 4 type of GOST1144 fasteners have a thread along the entire length
    if SType == "GOST1144-2" and l<=22 :
        b = 0.005
    dia = float(fa.calc_diam.split()[0])
    dk, k, n, t, d3, P = fa.dimTable
    d = dia / 2.0
    d32 = d3 / 2.0

    # calc head
    r = (4*k*k+dk*dk)/(8*k)
    zm = math.sqrt(1-dk*dk/(16*r*r))*r - (r-k)

    # calc screw
    if fa.thread:
        dt = d3 / 2.0
    else:
        dt = d
    angle = math.radians(20)
    x2 = dt * math.cos(angle)
    z2 = dt * math.sin(angle)
    z3 = x2 / math.tan(angle)
    ftl = l - z2 - z3 # flat part (total length - tip)

    # make profile
    fm = FastenerBase.FSFaceMaker()
    fm.AddPoints(
        (0, k),
        (dk/4, zm, dk/2, 0),
        (d, 0),
        (d, -b*ftl))
    if fa.thread:
        fm.AddPoints((dt, -b*ftl-(d-dt)))
    fm.AddPoints(
        (dt, -ftl),
        (dt*math.cos(angle/2), -l + z2 + z3 - d*math.sin(angle/2), x2, -l+z3),
        (0, -l))
    profile = fm.GetFace()

    # make screw body
    screw = screw_obj.RevolveZ(profile)

    # make slot
    slot = Part.makeBox(dk, n, t+1,
                        Base.Vector(-dk/2, -n/2, k-t))
    screw = screw.cut(slot)

    # make thread
    if fa.thread:
        thread = screw_obj.makeDin7998Thread(b * -ftl, -ftl, -l, d32, d, P)
        screw = screw.fuse(thread)

    return screw

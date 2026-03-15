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


def makeButtonHeadScrew(self, fa):
    """Create a cap screw with a round 'button' head

    Supported types:
    - ISO 7380-1 Button head screw
    - ASMEB18.3.3A UNC hex socket button head screws

    Thread diameter formulas (Dipak):
      ASME/inch : thread_dia = dia - 0.15 / TPI
      Metric    : thread_dia = dia - 0.15 * P
    """
    SType   = fa.baseType
    length  = fa.calc_len
    dia     = self.getDia(fa.calc_diam, False)
    is_asme = SType.startswith("ASME")

    # ── Unpack dimTable ───────────────────────────────────────────────────
    if SType == 'ISO7380-1':
        P_tbl, b_tbl, a, da, dk, dk_mean, s_mean, t_min, r, k, e, w = fa.dimTable
    elif SType == 'ASMEB18.3.3A':
        P_tbl, b_tbl, da, dk, s_mean, t_min, r, k = fa.dimTable
    else:
        raise NotImplementedError(f"Unknown fastener type: {SType}")

    # ── Pitch override (ThreadPitch mm / ThreadTPI) ───────────────────────
    raw_pitch = getattr(fa, "calc_pitch", None)
    P = raw_pitch if (raw_pitch is not None and raw_pitch > 0.0) else P_tbl

    # ── Thread length override (ThreadLength from dashboard) ──────────────
    raw_tlen = getattr(fa, "calc_thread_length", 0.0) or 0.0
    b = min(float(raw_tlen), length) if raw_tlen > 0.0 else b_tbl

    # ── Thread diameter ───────────────────────────────────────────────────
    # ASME/inch : thread_dia = dia - 0.15 / TPI
    # Metric    : thread_dia = dia - 0.15 * P
    if is_asme:
        tpi = getattr(fa, "calc_tpi", None)
        if not tpi or tpi <= 0:
            tpi = round(25.4 / P_tbl)
        thread_dia = dia - (0.15 / tpi)
        log_extra  = f"TPI={tpi}"
    else:
        thread_dia = dia - 0.15 * P
        log_extra  = f"P={P:.3f}mm"

    tr = thread_dia / 2.0

    FreeCAD.Console.PrintMessage(
        f"[Dipak] Threading: dia={dia:.4f}mm, "
        f"thread_dia={thread_dia:.4f}mm, {log_extra}, "
        f"allowance={dia - thread_dia:.4f}mm, "
        f"thread_length={b:.2f}mm\n"
    )

    # ── Head geometry ─────────────────────────────────────────────────────
    e_cham = 2.0 * s_mean / sqrt3 * 1.005
    ak     = -(4 * k ** 2 + e_cham ** 2 - dk ** 2) / (8 * k)
    rH     = math.sqrt((dk / 2.0) ** 2 + ak ** 2)
    alpha  = (math.atan(2 * (k + ak) / e_cham) + math.atan((2 * ak) / dk)) / 2

    # ── Revolve profile ───────────────────────────────────────────────────
    # Head uses full dia. Arc ends at (dia/2, -r); step inward to tr at
    # same z so the entire shaft is at thread_dia → volume changes correctly.
    fm = FastenerBase.FSFaceMaker()
    fm.AddPoint(0.0,          k)
    fm.AddPoint(e_cham / 2.0, k)
    fm.AddArc(
        rH * math.cos(alpha),
        -ak + rH * math.sin(alpha),
        dk / 2.0,
        0.0
    )
    fm.AddPoint(dia / 2 + r,  0.0)
    fm.AddArc2(0.0, -r, 90)             # ends at (dia/2, -r)
    fm.AddPoint(tr, -r)                 # step in to thread radius at same z

    if length - r > b:                  # partially threaded
        thread_length = b
        if not fa.Thread:
            fm.AddPoint(tr, -1 * (length - b))
    else:
        thread_length = length - r

    fm.AddPoint(tr,           -length + dia / 10)
    fm.AddPoint(dia * 4 / 10, -length)
    fm.AddPoint(0.0,          -length)

    shape = self.RevolveZ(fm.GetFace())

    # ── Cut hex recess into head ──────────────────────────────────────────
    recess = self.makeHexRecess(s_mean, t_min, True)
    recess.translate(Base.Vector(0.0, 0.0, k))
    shape = shape.cut(recess)

    # ── Thread cutter ─────────────────────────────────────────────────────
    if fa.Thread:
        thread_cutter = self.CreateBlindThreadCutter(thread_dia, P, thread_length)
        thread_cutter.translate(Base.Vector(0.0, 0.0, -1 * (length - thread_length)))
        shape = shape.cut(thread_cutter)

    return shape
# -*- coding: utf-8 -*-
"""
***************************************************************************
*   Copyright (c) 2022                                                    *
*   Alex Neufeld <alex.d.neufeld@gmail.com>                               *
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


def makeSquareBolt(self, fa):
    """Creates a screw with a simple square head.
    Supported types:
    - ASME B18.2.1 square head bolts

    Thread diameter formula (Dipak):
      ASME/inch : thread_dia = dia - 0.15 / TPI
    """
    dia    = self.getDia(fa.calc_diam, False)
    length = fa.calc_len

    if fa.baseType == "ASMEB18.2.1.1":
        TPI_tbl, F, H, R, L_T1, L_T2 = fa.dimTable
        r     = R    * 25.4
        s     = F    * 25.4
        k     = H    * 25.4
        P_tbl = 25.4 / TPI_tbl
        b_tbl = (L_T1 if length <= 6 * 25.4 else L_T2) * 25.4
    else:
        raise NotImplementedError(f"Unknown fastener type: {fa.baseType}")

    # ── Pitch override (ThreadTPI from dashboard) ─────────────────────────
    # fa.calc_pitch = 25.4/TPI set by FastenersCmd when user sets ThreadTPI.
    # fa.calc_tpi   = TPI integer, set by FastenersCmd.
    # If no override → use standard table values.
    raw_pitch = getattr(fa, "calc_pitch", None)
    P = raw_pitch if (raw_pitch is not None and raw_pitch > 0.0) else P_tbl

    # ── Thread length override (ThreadLength from dashboard) ──────────────
    raw_tlen = getattr(fa, "calc_thread_length", 0.0) or 0.0
    b = min(float(raw_tlen), length) if raw_tlen > 0.0 else b_tbl

    # ── Thread diameter: ASME inch formula ────────────────────────────────
    # thread_dia = dia - 0.15 / TPI
    # TPI = user override (fa.calc_tpi) or standard table TPI.
    tpi = getattr(fa, "calc_tpi", None)
    if not tpi or tpi <= 0:
        tpi = round(25.4 / P_tbl)          # standard TPI from table
    thread_dia = dia - (0.15 / tpi)
    tr         = thread_dia / 2.0

    FreeCAD.Console.PrintMessage(
        f"[Dipak] Threading: dia={dia:.4f}mm, "
        f"thread_dia={thread_dia:.4f}mm, TPI={tpi}, "
        f"allowance={dia - thread_dia:.4f}mm, "
        f"thread_length={b:.2f}mm\n"
    )

    # ── Revolve profile ───────────────────────────────────────────────────
    # Head uses full dia. Arc ends at (dia/2, -r); step inward to tr at
    # same z so the entire shaft is at thread_dia → volume changes correctly.
    fm = FSFaceMaker()
    fm.AddPoint(0.0,                                  k)
    fm.AddPoint(s / 2,                                k)
    fm.AddPoint(s / 2 + k / math.tan(math.radians(30)), 0.0)
    fm.AddPoint(dia / 2 + r,                          0.0)
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

    # ── Square head cut ───────────────────────────────────────────────────
    head_square = Part.makeBox(s, s, 2 * k + length)
    head_square.translate(Base.Vector(-s / 2, -s / 2, -length - k))
    shape = shape.common(head_square)

    # ── Thread cutter ─────────────────────────────────────────────────────
    if fa.Thread:
        thread_cutter = self.CreateBlindThreadCutter(thread_dia, P, thread_length)
        thread_cutter.translate(Base.Vector(0.0, 0.0, -1 * (length - thread_length)))
        shape = shape.cut(thread_cutter)

    return shape
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


def makeHexHeadBolt(self, fa):
    """Creates a bolt with a hexagonal head

    Supported types:
    - DIN 933 / DIN 961 / ISO 4014 / 4016 / 4017 / 4018
    - ISO 8676 / 8765 / ASMEB18.2.1.6

    Thread diameter formulas (Dipak):
      ASME/inch : thread_dia = dia - 0.15 / TPI
      Metric    : thread_dia = dia - 0.15 * P
    """
    dia    = self.getDia(fa.calc_diam, False)
    length = fa.calc_len
    is_asme = fa.baseType.startswith("ASME")

    # ── Unpack dimTable ───────────────────────────────────────────────────
    if fa.baseType in ("DIN933", "DIN961", "ISO4017", "ISO8676"):
        P_tbl, c, dw, e, k, r, s = fa.dimTable
        b_tbl = length
    elif fa.baseType == "ISO4018":
        P_tbl, _, _, c, _, dw, e, k, _, _, _, r, s, _ = fa.dimTable
        b_tbl = length
    elif fa.baseType == "ISO4014":
        P_tbl, b1, b2, b3, c, dw, e, k, r, s = fa.dimTable
        b_tbl = b1 if length <= 125.0 else (b2 if length <= 200.0 else b3)
    elif fa.baseType == "ISO4016":
        P_tbl, b1, b2, b3, c, _, _, _, dw, e, k, _, _, _, r, s, _ = fa.dimTable
        b_tbl = b1 if length <= 125.0 else (b2 if length <= 200.0 else b3)
    elif fa.baseType == "ISO8765":
        P_tbl, b1, b2, b3, c = fa.dimTable[:5]
        dw = fa.dimTable[11]
        e  = fa.dimTable[13]
        k  = fa.dimTable[15]
        r  = fa.dimTable[22]
        s  = fa.dimTable[23]
        b_tbl = b1 if length <= 125.0 else (b2 if length <= 200.0 else b3)
    elif fa.baseType == "ASMEB18.2.1.6":
        b_tbl, P_tbl, c, dw, e, k, r, s = fa.dimTable
        if length > 6 * 25.4:
            b_tbl += 6.35
    else:
        raise NotImplementedError(f"Unknown fastener type: {fa.Type}")

    # ── Pitch override (from ThreadPitch mm / ThreadTPI) ──────────────────
    raw_pitch = getattr(fa, "calc_pitch", None)
    P = raw_pitch if (raw_pitch is not None and raw_pitch > 0.0) else P_tbl

    # ── Thread length override (from ThreadLength property) ───────────────
    raw_tlen = getattr(fa, "calc_thread_length", 0.0) or 0.0
    b = min(float(raw_tlen), length) if raw_tlen > 0.0 else b_tbl

    # ── Thread diameter ───────────────────────────────────────────────────
    # ASME/inch : thread_dia = dia - 0.15 / TPI
    #             TPI = user override (fa.calc_tpi) or standard (25.4 / P_tbl)
    # Metric    : thread_dia = dia - 0.15 * P   (P in mm)
    if is_asme:
        tpi = getattr(fa, "calc_tpi", None)
        if not tpi or tpi <= 0:
            tpi = round(25.4 / P_tbl)          # standard TPI from table
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

    # ── Revolve profile ───────────────────────────────────────────────────
    # Head uses full dia. After the fillet arc (ends at dia/2, -r) we step
    # inward to tr at the same z so the entire shaft is at thread_dia.
    cham = (e - s) * math.sin(math.radians(15))

    fm = FSFaceMaker()
    fm.AddPoint(0.0,           k)
    fm.AddPoint(s / 2.0,       k)
    fm.AddPoint(s / sqrt3,     k - cham)
    fm.AddPoint(s / sqrt3,     c)
    fm.AddPoint(dw / 2.0,      c)
    fm.AddPoint(dw / 2.0,      0.0)
    fm.AddPoint(dia / 2.0 + r, 0.0)
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

    # ── Hex head cut ──────────────────────────────────────────────────────
    extrude = self.makeHexPrism(s, k + length + 2)
    extrude.translate(Base.Vector(0.0, 0.0, -length - 1))
    shape = shape.common(extrude)

    # ── Thread cutter ─────────────────────────────────────────────────────
    if fa.Thread:
        thread_cutter = self.CreateBlindThreadCutter(thread_dia, P, thread_length)
        thread_cutter.translate(Base.Vector(0.0, 0.0, -1 * (length - thread_length)))
        shape = shape.cut(thread_cutter)

    return shape
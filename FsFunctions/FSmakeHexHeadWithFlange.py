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


def makeHexHeadWithFlange(self, fa):
    """Create a fastener with a flanged hexagonal head

    Supported types:
    - ISO 4162  hexagon bolts with flange
    - ISO 15071 hexagon bolts with flange
    - ISO 15072 flanged hex head bolts with fine threads
    - EN 1662   hex-head-bolt with flange - small series
    - EN 1665   hexagon bolts with flange, heavy series
    - ASMEB18.2.1.8 hexagon bolts with flange, heavy series

    Thread diameter formulas (Dipak):
      ASME/inch : thread_dia = dia - 0.15 / TPI
      Metric    : thread_dia = dia - 0.15 * P
    """
    dia     = self.getDia(fa.calc_diam, False)
    SType   = fa.baseType
    length  = fa.calc_len
    is_asme = SType.startswith("ASME")

    # ── Unpack dimTable ───────────────────────────────────────────────────
    if SType in ("EN1662", "EN1665"):
        P_tbl, b0, b1, b2, b3, c, dc, dw, e, k, kw, f, r1, s = fa.dimTable

    elif SType == "ASMEB18.2.1.8":
        b0, P_tbl, c, dc, kw, r1, s = fa.dimTable

    elif SType in ("ISO4162", "ISO15071"):
        P_tbl, b0, b1, b2, b3, c = fa.dimTable[:6]
        dc  = fa.dimTable[8]
        kw  = fa.dimTable[15]
        r1  = fa.dimTable[17]
        s   = fa.dimTable[22]

    elif SType == "ISO15072":
        P_tbl       = fa.dimTable[0]
        b0, b1, b2, b3, c = fa.dimTable[3:8]
        dc  = fa.dimTable[10]
        kw  = fa.dimTable[17]
        r1  = fa.dimTable[19]
        s   = fa.dimTable[24]

    else:
        raise NotImplementedError(f"Unknown fastener type: {fa.Type}")

    # ── Standard thread length (b) from table ─────────────────────────────
    if length < b0:
        b_tbl = length - r1
    elif SType == "ASMEB18.2.1.8":
        b_tbl = b0
    else:
        b_tbl = b1 if length <= 125.0 else (b2 if length <= 200.0 else b3)

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

    # ── Head geometry constants ───────────────────────────────────────────
    cham    = s * (2.0 / sqrt3 - 1.0) * math.sin(math.radians(25))
    sqrt2_  = 1.0 / sqrt2
    beta    = math.radians(25.0)
    tan_beta = math.tan(beta)
    arc1_x  = dc / 2.0 - c / 2.0 + (c / 2.0) * math.sin(beta)
    arc1_z  = c / 2.0 + (c / 2.0) * math.cos(beta)
    kmean   = arc1_z + (arc1_x - s / sqrt3) * tan_beta + kw * 1.1 + cham

    # ── Hex head revolve ──────────────────────────────────────────────────
    fm = FSFaceMaker()
    fm.AddPoint(0.0, kmean * 0.9)
    fm.AddPoint(s / 2.0 * 0.8 - r1 / 2.0, kmean * 0.9)
    fm.AddArc(
        s / 2.0 * 0.8 - r1 / 2.0 + r1 / 2.0 * sqrt2_,
        kmean * 0.9 + r1 / 2.0 - r1 / 2.0 * sqrt2_,
        s / 2.0 * 0.8,
        kmean * 0.9 + r1 / 2.0,
    )
    fm.AddPoint(s / 2.0 * 0.8, kmean - r1)
    fm.AddArc(
        s / 2.0 * 0.8 + r1 - r1 * sqrt2_,
        kmean - r1 + r1 * sqrt2_,
        s / 2.0 * 0.8 + r1,
        kmean,
    )
    fm.AddPoint(s / 2.0, kmean)
    fm.AddPoint(s / 2 + (kmean - 0.1) * sqrt3, 1.0)
    fm.AddPoint(0.0, 0.1)
    head = self.RevolveZ(fm.GetFace())

    # cut the hexagon flats
    hextool = self.makeHexPrism(s, kmean)
    head = head.common(hextool)

    # ── Flange + shaft revolve ────────────────────────────────────────────
    # Shaft uses tr (= thread_dia/2) so the revolved solid is at thread_dia
    # → volume changes correctly.
    # Arc AddArc2(r1, 0, -90) from (tr, -r1) ends at (tr+r1, 0) → flange start.
    fm.Reset()
    fm.AddPoint(0.0,  -length)
    fm.AddPoint(dia * 4 / 10, -length)
    fm.AddPoint(tr,   -length + dia / 10)   # tip taper uses tr

    if length - r1 > b:                     # partially threaded
        thread_length = b
        if not fa.Thread:
            fm.AddPoint(tr, -1 * (length - b))
    else:
        thread_length = length - r1

    fm.AddPoint(tr, -r1)                    # shaft at thread radius down to fillet
    fm.AddArc2(r1, 0.0, -90)               # fillet arc: ends at (tr + r1, 0)
    fm.AddPoint((dc - c) / 2, 0.0)
    fm.AddArc2(0, c / 2, 180 - math.degrees(beta))
    flange_top_ht = math.tan(beta) * (
        (dc - c) / 2 - s * 0.4 + c / 2 / math.tan(beta / 2)
    )
    fm.AddPoint(s * 0.4, flange_top_ht)
    fm.AddPoint(0.0,     flange_top_ht)

    flange = self.RevolveZ(fm.GetFace())
    shape  = head.fuse(flange)

    # ── Thread cutter ─────────────────────────────────────────────────────
    if fa.Thread:
        thread_cutter = self.CreateBlindThreadCutter(thread_dia, P, thread_length)
        thread_cutter.translate(Base.Vector(0.0, 0.0, -1 * (length - thread_length)))
        shape = shape.cut(thread_cutter)

    return shape
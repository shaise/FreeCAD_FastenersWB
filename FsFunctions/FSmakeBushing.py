from screw_maker import *
import math


def makeBushing(self, fa):
    if fa.Type == "ISO4379C":
        d1, d2, b1, b2, C, C1, C2 = fa.dimTable
        inner_radius = d1 / 2
        outer_radius = d2 / 2

        if C1 < 0 or C2 < 0:
            raise ValueError("Chamfer lengths cannot be negative")
        if C2 > 0 and not 0 < C < 90:
            raise ValueError(f"Invalid chamfer angle: {C}")
        if 2 * C1 >= b1 or 2 * C2 >= b1:
            raise ValueError("Chamfer lengths must be less than half the type C bushing length")

        inner_chamfer = C1 * math.tan(math.radians(45))
        outer_chamfer = C2 * math.tan(math.radians(C))
        if inner_radius + inner_chamfer >= outer_radius - outer_chamfer:
            raise ValueError("Chamfers overlap across the type C bushing wall")

        profile = FSFaceMaker()
        profile.AddPoint(inner_radius + inner_chamfer, 0)
        if C1 > 0:
            profile.AddPoint(inner_radius, -C1)
        profile.AddPoint(inner_radius, -b1 + C1)
        if C1 > 0:
            profile.AddPoint(inner_radius + inner_chamfer, -b1)
        if C2 > 0:
            profile.AddPoint(outer_radius - outer_chamfer, -b1)
            profile.AddPoint(outer_radius, -b1 + C2)
            profile.AddPoint(outer_radius, -C2)
            profile.AddPoint(outer_radius - outer_chamfer, 0)
        else:
            profile.AddPoint(outer_radius, -b1)
            profile.AddPoint(outer_radius, 0)
            profile.AddPoint(outer_radius - outer_chamfer, 0)
        return self.RevolveZ(profile.GetFace())
    elif fa.Type == "ISO4379F":
        d1, d2, d3, b1, b2, C, C1, C2, u = fa.dimTable
        inner_radius = d1 / 2
        body_radius = d2 / 2
        flange_radius = d3 / 2

        if d1 <= 0 or d2 <= d1 or d3 <= d2 or b1 <= 0 or b2 <= 0 or b2 >= b1:
            raise ValueError("Invalid type F bushing dimensions")
        if C1 < 0 or C2 < 0 or u < 0:
            raise ValueError("Type F relief and chamfer dimensions cannot be negative")
        if C2 > 0 and not 0 < C < 90:
            raise ValueError(f"Invalid chamfer angle: {C}")
        if 2 * C1 >= b1 or C2 >= b1 - b2:
            raise ValueError("Chamfer lengths exceed the type F bushing length")

        inner_chamfer = C1 * math.tan(math.radians(45))
        outer_chamfer = C2 * math.tan(math.radians(C))
        if inner_radius + inner_chamfer >= body_radius - outer_chamfer:
            raise ValueError("Type F inner and outer chamfers overlap")
        relief_depth = 0.2
        body_length = b1 - b2
        if body_radius - relief_depth <= inner_radius:
            raise ValueError("Type F relief exceeds the bushing wall")
        if u > 0 and u + C2 >= body_length:
            raise ValueError("Type F relief overlaps the outer chamfer")

        profile = FSFaceMaker()
        if C1 > 0:
            profile.AddPoint(inner_radius + inner_chamfer, b2)
            profile.AddPoint(inner_radius, b2 - C1)
        else:
            profile.AddPoint(inner_radius, b2)
        profile.AddPoint(inner_radius, -b1 + b2 + C1)
        if C1 > 0:
            profile.AddPoint(inner_radius + inner_chamfer, -b1 + b2)
        if C2 > 0:
            profile.AddPoint(body_radius - outer_chamfer, -b1 + b2)
            profile.AddPoint(body_radius, -b1 + b2 + C2)
        else:
            profile.AddPoint(body_radius, -b1 + b2)
        profile.AddPoint(body_radius, -u)
        if u > 0:
            profile.AddPoint(body_radius - relief_depth, -u)
            profile.AddPoint(body_radius - relief_depth, 0)
            profile.AddPoint(body_radius, 0)
        profile.AddPoint(flange_radius, 0)
        profile.AddPoint(flange_radius, b2)
        return self.RevolveZ(profile.GetFace())
    else:
        raise NotImplementedError(f"Unknown fastener type: {fa.Type}")

#!/usr/bin/env python3
"""
8220 Hawthorne Ave, Miami Beach FL 33141 — single source of truth for geometry.

Floor 1 is TRACED from the architect's sheet A-1 "EXISTING UNIT FLOOR PLAN"
(scale 1/4"=1'-0"), not guessed. The sheet is dimensionless as supplied, so the
trace was calibrated by scaling the traced polygon until its enclosed area
equals the 2,874 sf of living area on the MLS/Zillow record. That yields
0.0657 ft per traced pixel and an overall envelope of 48'-8" x 72'-1".
Every room size below follows from that one calibration -> VERIFY on site with
a tape before anything is drawn for permit.

Coordinate system (feet):
    X  = 0 at the WEST exterior wall, increasing east.       (0 .. 48.7)
    Y  = 0 at the REAR (canal) exterior wall, increasing toward the street.
    Z  = 0 at existing grade, up.
Plans are drawn with Y increasing DOWNWARD so they read like sheet A-1
(canal at the top of the page, Hawthorne Ave at the bottom).
"""

FT_PER_PX = 0.06571          # calibration constant (see docstring)
W = 48.7                     # overall envelope width  (48'-8")
D = 72.1                     # overall envelope depth  (72'-1")
LOT_W, LOT_D = 60.0, 150.0   # from the boundary survey
BFE = 8.0                    # Flood Zone AE base flood elevation (NGVD)

# ---------------------------------------------------------------- height stack
# Scheme A = addition stays under the 50%-of-value "substantial improvement"
# threshold, so the existing slab may remain where it is.
FF1      = 1.0               # existing finished floor above grade (assumed)
FLOOR_TO_FLOOR = 10.5        # FF1 -> FF2 ; also sets the stair (17R @ 7.4")
FF2      = FF1 + FLOOR_TO_FLOOR      # 11.5
PLATE2   = 9.0               # second-floor ceiling height
ROOF     = FF2 + PLATE2 + 0.9        # 21.4  top of roof deck
PARAPET  = ROOF + 2.5                # 23.9  top of parapet  (fits a 24' cap)
EAVE1    = FF1 + 9.4                 # existing one-story roof line

# --------------------------------------------------- EXISTING ENVELOPE (traced)
# Stepped outline: full-width at the canal end, notched at the street end.
ENVELOPE_1 = [
    (0.0, 0.0), (48.7, 0.0), (48.7, 72.1), (36.6, 72.1), (36.6, 53.7),
    (28.7, 53.7), (28.7, 49.4), (17.5, 49.4), (17.5, 58.3), (0.0, 58.3),
]

# ------------------------------------------------- GROUND FLOOR (traced rooms)
# name, x0, x1, y0, y1
ROOMS_1 = [
    ("SUNROOM",       0.0, 25.8,  0.0, 19.8),
    ("W.I.C.",       26.2, 33.8,  1.3, 21.5),
    ("MASTER BR",    33.8, 48.7,  0.0, 11.0),
    ("WORK AREA",    35.5, 48.7, 11.0, 22.8),   # the dashed permit scope on A-1
    ("DINING ROOM",  33.8, 48.7, 22.8, 31.7),
    ("GUEST BEDROOM", 0.0, 17.5, 19.8, 58.3),
    ("LIVING ROOM",  17.5, 36.6, 21.8, 49.4),
    ("KITCHEN",      36.6, 48.7, 31.7, 53.7),
    ("UTILITY ROOM", 36.6, 48.7, 53.7, 72.1),
]

# Interior partitions that read as continuous on A-1. The ones flagged bearing
# are the candidates for carrying new second-floor load straight down.
# x0, y0, x1, y1, bearing?
WALLS_1 = [
    (25.8,  0.0, 25.8, 21.5, True),    # sunroom / W.I.C. spine
    (33.8,  0.0, 33.8, 31.7, True),    # W.I.C. / master-dining spine
    (17.5, 19.8, 17.5, 58.3, True),    # guest bedroom / living spine  <- long
    (36.6, 31.7, 36.6, 72.1, True),    # living / kitchen spine        <- long
    ( 0.0, 19.8, 17.5, 19.8, False),   # sunroom / guest bedroom
    (25.8, 21.5, 33.8, 21.5, False),
    (33.8, 22.8, 48.7, 22.8, False),   # work area / dining
    (33.8, 31.7, 36.6, 31.7, False),
    (36.6, 53.7, 48.7, 53.7, False),   # kitchen / utility
]

# Exterior openings read off A-1.  wall, along0, along1, sill, head
#   wall 'N' = canal/rear (Y=0)   'S' = street/front   'W' = X=0   'E' = X=48.7
OPENINGS_1 = [
    ("N",  3.5,  8.5, 2.5, 8.0), ("N", 12.0, 17.0, 2.5, 8.0),
    ("N", 20.0, 25.0, 2.5, 8.0), ("N", 39.0, 44.0, 2.5, 8.0),
    ("W",  3.0,  7.0, 0.0, 7.0),                       # sunroom door to canal
    ("W", 26.0, 34.0, 2.5, 7.0),                       # guest bedroom
    ("E", 34.0, 40.0, 3.0, 7.5), ("E", 58.0, 66.0, 3.0, 7.5),
    ("S1", 1.5, 10.5, 2.5, 7.0),                       # guest bedroom, Y=58.3
    ("S2", 38.9, 46.1, 2.5, 7.0),                      # utility room, Y=72.1
    ("F",  38.0, 42.0, 0.0, 7.0),                      # front entry door
]

# ----------------------------------------------- SECOND FLOOR (proposed design)
# Footprint: flush with the existing west, east and rear CBS walls so the load
# path is direct; the street end stops at Y=42.0 and steps back at the SE corner
# so the two-story mass reads as one story from Hawthorne Ave.
ENVELOPE_2 = [(0.0, 0.0), (48.7, 0.0), (48.7, 42.0), (0.0, 42.0)]
FRONT_BEAM_Y = 42.0          # new beam line; picks up X = 0 / 17.5 / 36.6 / 48.7

# name, x0, x1, y0, y1, kind   (kind: 'room' | 'wet' | 'circ' | 'terrace')
ROOMS_2 = [
    ("CANAL TERRACE",   0.0, 16.0,  0.0, 13.0, "terrace"),
    ("PRIMARY BEDROOM",16.0, 38.0,  0.0, 20.0, "room"),
    ("PRIMARY BATH",   38.0, 48.7,  0.0, 12.0, "wet"),
    ("W.I.C.",         38.0, 48.7, 12.0, 22.0, "room"),
    ("STUDY",           0.0, 16.0, 13.0, 22.0, "room"),
    ("GALLERY",         2.0, 40.0, 22.0, 28.0, "circ"),
    ("LAUNDRY/MECH",   40.0, 48.7, 22.0, 28.0, "wet"),
    ("BEDROOM 2",       0.0, 15.0, 28.0, 42.0, "room"),
    ("BATH 3",         15.0, 23.0, 28.0, 34.0, "wet"),
    ("BATH 2",         15.0, 23.0, 34.0, 42.0, "wet"),
    ("BEDROOM 3",      23.0, 33.0, 28.0, 42.0, "room"),
    ("STAIR",          33.0, 38.0, 28.0, 42.0, "circ"),
    ("FRONT TERRACE",  38.0, 48.7, 28.0, 42.0, "terrace"),
]

# Stair: straight run against the existing living/kitchen spine wall (X=36.6),
# bottom riser at Y=42 in the living room, rising toward the canal.
STAIR = dict(x0=33.0, x1=36.6, y_bottom=42.0, y_top=28.0, risers=17,
             riser=FLOOR_TO_FLOOR / 17 * 12, tread=10.5)

OPENINGS_2 = [
    ("N",  17.0, 37.0, 1.0, 8.5),                      # primary, glass to canal
    ("N",  40.0, 46.0, 3.5, 8.0),
    ("W",  14.0, 21.0, 2.5, 7.5),
    ("W",  30.0, 40.0, 2.5, 7.5),
    ("E",   2.0,  9.0, 3.5, 8.0), ("E", 13.0, 20.0, 3.5, 7.5),
    ("S",   1.0, 13.0, 2.5, 7.5), ("S", 24.0, 32.0, 2.5, 7.5),
]

def area(poly):
    s = 0.0
    for i in range(len(poly)):
        x0, y0 = poly[i]; x1, y1 = poly[(i + 1) % len(poly)]
        s += x0 * y1 - x1 * y0
    return abs(s) / 2.0

def room_area(r):
    return (r[2] - r[1]) * (r[4] - r[3])

AREA_1 = area(ENVELOPE_1)
AREA_2_GROSS = area(ENVELOPE_2)
AREA_2_COND = sum(room_area(r) for r in ROOMS_2 if r[5] != "terrace")
AREA_2_TERRACE = sum(room_area(r) for r in ROOMS_2 if r[5] == "terrace")

if __name__ == "__main__":
    print(f"existing envelope   {W:.1f}' x {D:.1f}'   {AREA_1:,.0f} sf")
    for r in ROOMS_1:
        print(f"   {r[0]:<15} {r[2]-r[1]:5.1f}' x {r[4]-r[3]:5.1f}' = {room_area(r):6.0f} sf")
    print(f"\nsecond floor gross under roof      {AREA_2_GROSS:,.0f} sf")
    print(f"second floor conditioned           {AREA_2_COND:,.0f} sf")
    print(f"second floor terraces              {AREA_2_TERRACE:,.0f} sf")
    for r in ROOMS_2:
        print(f"   {r[0]:<16} {r[2]-r[1]:5.1f}' x {r[4]-r[3]:5.1f}' = {room_area(r):6.0f} sf  {r[5]}")
    tot = AREA_1 + AREA_2_COND
    print(f"\ntotal conditioned after addition   {tot:,.0f} sf")
    print(f"FAR on the 9,000 sf lot            {tot/ (LOT_W*LOT_D):.3f}")
    print(f"stair  {STAIR['risers']}R @ {STAIR['riser']:.2f}\"  x  {STAIR['risers']-1}T @ {STAIR['tread']}\""
          f"  = {(STAIR['risers']-1)*STAIR['tread']/12:.1f}' run")
    print(f"top of parapet                     {PARAPET:.1f}' above grade")

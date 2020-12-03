#  (C) Copyright 2020 Anthony D. Dutoi
#
#  This file is part of TonyUtil.
#
#  TonyUtil is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
import math
from .int_round import int_round



def color_wheel(phi):
    """ maps angle (in radians) to rainbow color wheel, optimized to have constant brightness (can always be improved) """
    color = {}
    color["red"]    = 0xee, 0x33, 0x33
    color["orange"] = 0xdd, 0x55, 0
    color["yellow"] = 0x88, 0x88, 0
    color["green"]  = 0x22, 0x99, 0x22
    color["blue"]   = 0x33, 0x88, 0xff
    color["purple"] = 0xcc, 0x44, 0xee
    position ={}
    position["red1"]   = -1
    position["orange"] = -2/3 - 0.1
    position["yellow"] = -1/3 + 0.05
    position["green"]  =  0
    position["blue"]   = +1/3 - 0.1
    position["purple"] = +2/3 - 0.05
    position["red2"]   = +1
    phi /= math.pi
    if   phi<position["orange"]:
        D = position["orange"] - position["red1"]
        w = (phi - position["red1"]) / D
        v = 1 - w
        r1, g1, b1 = color["red"]
        r2, g2, b2 = color["orange"]
        rr = int_round(v*r1 + w*r2)
        gg = int_round(v*g1 + w*g2)
        bb = int_round(v*b1 + w*b2)
    elif phi<position["yellow"]:
        D = position["yellow"] - position["orange"]
        w = (phi - position["orange"]) / D
        v = 1 - w
        r1, g1, b1 = color["orange"]
        r2, g2, b2 = color["yellow"]
        rr = int_round(v*r1 + w*r2)
        gg = int_round(v*g1 + w*g2)
        bb = int_round(v*b1 + w*b2)
    elif phi<position["green"]:
        D = position["green"] - position["yellow"]
        w = (phi - position["yellow"]) / D
        v = 1 - w
        r1, g1, b1 = color["yellow"]
        r2, g2, b2 = color["green"]
        rr = int_round(v*r1 + w*r2)
        gg = int_round(v*g1 + w*g2)
        bb = int_round(v*b1 + w*b2)
    elif phi<position["blue"]:
        D = position["blue"] - position["green"]
        w = (phi - position["green"]) / D
        v = 1 - w
        r1, g1, b1 = color["green"]
        r2, g2, b2 = color["blue"]
        rr = int_round(v*r1 + w*r2)
        gg = int_round(v*g1 + w*g2)
        bb = int_round(v*b1 + w*b2)
    elif phi<position["purple"]:
        D = position["purple"] - position["blue"]
        w = (phi - position["blue"]) / D
        v = 1 - w
        r1, g1, b1 = color["blue"]
        r2, g2, b2 = color["purple"]
        rr = int_round(v*r1 + w*r2)
        gg = int_round(v*g1 + w*g2)
        bb = int_round(v*b1 + w*b2)
    else:
        D = position["red2"] - position["purple"]
        w = (phi - position["purple"]) / D
        v = 1 - w
        r1, g1, b1 = color["purple"]
        r2, g2, b2 = color["red"]
        rr = int_round(v*r1 + w*r2)
        gg = int_round(v*g1 + w*g2)
        bb = int_round(v*b1 + w*b2)
    return "#{:02x}{:02x}{:02x}".format(rr,gg,bb)

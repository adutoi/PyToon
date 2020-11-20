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
    red    = 0xcc, 0x33, 0x33
    orange = 0xcc, 0x55, 0
    yellow = 0x99, 0x88, 0
    green  = 0,    0x77, 0x11
    blue   = 0x66, 0x77, 0xff
    purple = 0xbb, 0x11, 0xee
    phi /= math.pi
    if   phi<-2/3:
        w = 3*(phi + 1)
        v = 1 - w
        r1, g1, b1 = red
        r2, g2, b2 = orange
        rr = int_round(v*r1 + w*r2)
        gg = int_round(v*g1 + w*g2)
        bb = int_round(v*b1 + w*b2)
    elif phi<-1/3:
        w = 3*(phi + 2/3)
        v = 1 - w
        r1, g1, b1 = orange
        r2, g2, b2 = yellow
        rr = int_round(v*r1 + w*r2)
        gg = int_round(v*g1 + w*g2)
        bb = int_round(v*b1 + w*b2)
    elif phi< 0:
        w = 3*(phi + 1/3)
        v = 1 - w
        r1, g1, b1 = yellow
        r2, g2, b2 = green
        rr = int_round(v*r1 + w*r2)
        gg = int_round(v*g1 + w*g2)
        bb = int_round(v*b1 + w*b2)
    elif phi< 1/3:
        w = 3*phi
        v = 1 - w
        r1, g1, b1 = green
        r2, g2, b2 = blue
        rr = int_round(v*r1 + w*r2)
        gg = int_round(v*g1 + w*g2)
        bb = int_round(v*b1 + w*b2)
    elif phi< 2/3:
        w = 3*(phi - 1/3)
        v = 1 - w
        r1, g1, b1 = blue
        r2, g2, b2 = purple
        rr = int_round(v*r1 + w*r2)
        gg = int_round(v*g1 + w*g2)
        bb = int_round(v*b1 + w*b2)
    else:
        w = 3*(phi - 2/3)
        v = 1 - w
        r1, g1, b1 = purple
        r2, g2, b2 = red
        rr = int_round(v*r1 + w*r2)
        gg = int_round(v*g1 + w*g2)
        bb = int_round(v*b1 + w*b2)
    return "#{:02x}{:02x}{:02x}".format(rr,gg,bb)

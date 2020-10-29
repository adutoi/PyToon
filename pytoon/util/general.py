#  (C) Copyright 2020 Anthony D. Dutoi
#
#  This file is part of PyToon.
#
#  PyToon is free software: you can redistribute it and/or modify
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
from .external import struct, as_tuple, as_dict, int_round, shell, code_template    # here for further export (this is where they would be defined if written locally)



def echo(arg):
    """ a dummy function that simply returns its argument """
    return arg

def nested(*, outer, inner):
    """ nests single-parameter functions """
    def nest(arg):
        return outer(inner(arg))
    return nest



float_eq = lambda x,y:  math.isclose(x,y, rel_tol=1e-14)



def valid_real_number(variable, condition):
    x, name = variable
    condition_expression, textual_condition = condition 
    if isinstance(x, int):
        num_x = int(x)    # a special case that should not change behavior significantly (but saves some flops/memory/rounding issues) ... cast in case x is a bool
    else:
        try:
            num_x = float(x)
        except (TypeError, ValueError):
            raise ValueError( "{} must be convertible to float: {}".format(name, repr(x)) )
    if not condition_expression(num_x):
        raise ValueError( "{} must be {}: {}".format(name, textual_condition, repr(x)) )
    return num_x



# Really, point and the description of the curve to reach it should not be packed together in this way.
# At least it should be struct(point=(x,y), curve=struct(curve=?, ...))

def valid_point(pt):
    try:
        x, y = pt
    except ValueError:
        try:
            x, y, p = pt
            _ = p.curve
        except (ValueError, AttributeError):
            raise ValueError( "invalid format for point or segment to point identifier: {}".format(repr(pt)) )
        if p.curve=="arc":
            rx   = valid_real_number((p.rx, "perpendicular component of arc radius"), (lambda z: True, "anything"))
            ry   = valid_real_number((p.ry, "parallel component of arc radius"),      (lambda z: z>=0, "non-negative"))
            skew = valid_real_number((p.skew, "skew of arc radii"), (lambda z: -90<z<90, "between -90 and 90, exclusive"))
            p = struct(curve="arc", rx=rx, ry=ry, skew=skew)
        else:
            raise NotImplementedError( "curve type \'{}\' has not yet been implemented: {}".format(p.curve, repr(pt)) )
    else:
        p = None
    x = valid_real_number((x, "x component of point"), (lambda z: True, "anything"))
    y = valid_real_number((y, "y component of point"), (lambda z: True, "anything"))
    if p is None:
        return (x, y)
    else:
        return (x, y, p)

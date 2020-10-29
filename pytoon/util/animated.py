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



def is_animated(prop):
    """ checks if prop is an iterable of 2-tuple-like objects, where the first component is an increasing 'time' between 0 and 1, inclusive """
    try:
        times = [t for t,v in prop]
    except (TypeError, ValueError):
        return False
    else:
        if len(times)==0:
            return False    # otherwise gets confused by empty dashes array
        if len(times)==1 and times[0]==None:
            return True
        answer = True
        t0 = -1
        for t in times:
            if not (0<=t<=1 and t>t0):  answer = False
            t0 = t
        return answer

def animated(prop):
    """ represents a prop as formally animated, even if it is constant """
    if is_animated(prop):
        return prop
    else:
        return [(None, prop)]

def deanimated(prop):
    """ checks that formally animated sequence really represents a static value and returns it """
    if is_animated(prop):
        if len(prop)==1:
            t, p = prop[0]
            if t is None:
                return p
            else:
                raise ValueError("passed value does not represent a static property represented as animated")
        else:
            raise ValueError("passed value does not represent a static property represented as animated")
    else:
        raise ValueError("passed value does not represent a static property represented as animated")



def validator(parser):
    """ wraps a property parser/validator to make it work for animated properties as well """
    def valid(prop, allow_animated=True):
        if is_animated(prop):
            if allow_animated:
                return [(t,parser(p)) for t,p in prop]
            else:
                raise TypeError("animated property data given for single time point")
        else:
            return parser(prop)
    return valid

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
from . import util



class animated(object):
    def __init__(self, f, *, Dt, _clock=None, _postprocess=None):
        self._f           = f
        self._Dt          = Dt
        self._clock       = _clock
        self._postprocess = _postprocess
    def __call__(self, _t_):
        varval = util.variable_evaluator({"_t_": self._clock(_t_)})    # will fail if clock has not been installed (by wrapper below)
        value = varval(self._f)
        if self._postprocess:  value = self._postprocess(value)
        return value
    def n_intervals(self, ta, tz, n_min=0):
        N = n_min
        if self._Dt is not None:
            N = max(N, 1, util.int_round( (self._clock(tz)-self._clock(ta)) / self._Dt ))    # will fail if clock has not been installed (by wrapper below)
        return N
    def _value_(self, substitutions):
        varval = util.variable_evaluator(substitutions)
        return animated(varval(self._f), Dt=varval(self._Dt))

def wrapper(obj, *, clock=None, postprocess=None):
    if isinstance(obj, animated):
        if not clock:        clock       = obj._clock
        if not postprocess:  postprocess = obj._postprocess
        return animated(obj._f, Dt=obj._Dt, _clock=clock, _postprocess=postprocess)
    else:
        return animated(obj, Dt=None, _clock=clock, _postprocess=postprocess)

def combine(op, a, b):
    if a._clock is not b._clock:
        raise RuntimeError("cannot combine animated properties with different clocks")    # hard to see how this would ever happen, but ...
    if (a._Dt is None) and (b._Dt is None):
        Dt = None
    elif a._Dt is None:
        Dt = b._Dt
    elif b._Dt is None:
        Dt = a._Dt
    else:
        Dt = min(a._Dt, b._Dt)
    return animated(lambda _t_: op(a(_t_), b(_t_)), Dt=Dt, _clock=a._clock)

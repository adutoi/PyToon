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



# This is just one step more explicit than passing around tuples, where you have to keep track
# of the order, but have a lighter syntax than dictionaries.  Variants of unpacking, splatting,
# and double-splatting are supported, also for subsets of the stored values.  See syntax in commments.
# In unpacking/splatting, you could rely on the dict order, but it is a bad idea.

def as_tuple(to_tuple):  return to_tuple._as_tuple()
def as_dict(to_dict):  return to_dict._as_dict()

class struct(object):
    def __init__(self, **kwargs):
        object.__setattr__(self, "_dict", kwargs)    # because self._dict = kwargs would give infinite recursion
    # Makes the struct behave like a namespace (implicitly restricts allowed keys of internal dict)
    # >>> a = struct(attr1=arg1, attr2=arg2, attr3=arg3, ...)
    # >>> a.later = another
    # >>> (a.attr1 is arg1) and (a.later is another)
    def __setattr__(self, attr, value):
        self._dict[attr] = value
        return value
    def __getattr__(self, attr):
        try:
            return self._dict[attr]
        except KeyError:
            raise AttributeError(repr(attr))
    def __delattr__(self, attr):
        try:
            del self._dict[attr]
        except KeyError:
            raise AttributeError(repr(attr))
    # allows the taking of a sub-namespace
    def __call__(self, *attrs):
        kwargs = {attr:self._dict[attr] for attr in attrs}
        return struct(**kwargs)
    def __repr__(self):
        arguments = ", ".join("{}={}".format(k,repr(v)) for k,v in self._dict.items())
        return "{}({})".format(type(self).__name__, arguments)
    # allow for (partial) unpacking via
    # x, y = as_tuple(a("attr1", "attr2"))
    # and therefore (partial) splatting as
    # f(*as_tuple(a("attr1", "attr2")))
    def _as_tuple(self):
        return tuple(self._dict.values())
    # allow for (partial) double-splatting via
    # f(**as_dict(a("attr1", "attr2")))
    def _as_dict(self):
        return dict(self._dict)

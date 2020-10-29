#    (C) Copyright 2019 Anthony D. Dutoi
# 
#    This file is part of TonyUtil.
# 
#    TonyUtil is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
# 
#    TonyUtil is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
# 
#    You should have received a copy of the GNU General Public License
#    along with TonyUtil.  If not, see <http://www.gnu.org/licenses/>.
#
from fractions import Fraction

"""\
Objects of class physical_quantity should behave like numerical values with associated physical units.

In fact the implementation is more general, which could be useful, but also requires some (modest)
thought by the user.  A physical_quantity is just a number that is associated with rational powers
of some set of generic, symbolic multipliers, given as strings in as simple list, named unit_symbols.
In order for two physical_quantity objects to enter into a binary operation together, they must
have been constructed with the same instance of this list.  Within that binary operation the numerical
values and rational powers associated with each multiplier are manipulated accordingly.

It is not expected that a user will ever create a physical_quantity directly, but rather, the function
unit_system creates some base quantities that are used to construct all further physical_quantity
objects.  unit_system takes a variable number of objects, each of which is a string that gives
the symbol associated with a base measurment unit.  It returns a tuple containing the same number
of objects as arguments given, where each member of the tuple is a physical_quantity that represents
one of those units.  These may be multiplied by scalars to construct other physical quantities with
units in much the same way they are written on paper.

UPDATE: unit_system now returns an extra member which is scalar unity, which facilitates named constants.

The user must be aware that these objects know nothing of physics.  The units are just generic
multipliers, and so if overcomplete unit systems are used, you can get some wierd looking results.
That said, the results will still be accurate its just that the units will be written out in a 
way that no (competent) human would ever choose.

If a physical_quantity is printed, it will be printed with its units to their appropriate power,
there are some extra string functions defined to allow for better formatting of the numerical part too.

A final little dash of sugar is the use of the .symbolic member function in association with
the .in_ member function.  The former may be called on any physical quantity to give it a "name"
(for example, even though the atomic unit system might be being used, a quantity with the size
of 1 eV might be built and named as such).  Any such named quantity can be given as the first
argument of the .in_ function, so that the quantity is rendered to a string with a numerical value
in those units with that unit appended.  This works even if the two quantities are not of the same
dimension because the "leftover" units are retained (so the answer will just be strange looking if you
did the wrong thing).
"""




class physical_quantity(object):
    def __init__(self, numerical, unit_pows, unit_symbols):
        self.numerical    = numerical
        self.unit_pows    = list(unit_pows)	# must copy because might be member of another physical_quantity (also must be mutable, given the way the functions below work)
        self.unit_symbols = unit_symbols	# must not copy because the *identity* of this object must match other operands
        if len(unit_pows)!=len(unit_symbols):  raise ValueError("one, and only one, power must be given for the base unit of each physical dimension")
        for p in unit_pows:
            if not isinstance(p,Fraction):  raise ValueError("powers of fundamental units must be rational numbers")
        self.symbol = "(" + str(self) + ")"	# This is just better than leaving it blank
    def symbolic(self,symbol):
        self.symbol = symbol
        return self	# returning self is just syntactic sugar
    def __float__(self):
        unitless = True
        for u_pow in self.unit_pows:
            if u_pow!=0:  unitless = False
        if not unitless:  raise RuntimeError("value with units cannot be converted to pure scalar as float")
        return self.numerical
    def __add__(self, x):
        value = physical_quantity(self.numerical, self.unit_pows, self.unit_symbols)
        try:
            value.numerical += x.numerical	# assume it is another physical_quantity ...
        except:
            try:
                return x + self    # calls __radd__ to handle potential addition of pure scalar
            except:
                raise TypeError("must be another physical_quantity (unless quantity is unitless)")
        else:
            if x.unit_symbols is not value.unit_symbols:  raise AssertionError("only operations on quantities within same unit system are supported")		# implicitly guarantees that unit_pows of value and x have same length, since always checked
            if value.unit_pows!=x.unit_pows:  raise ArithmeticError("cannot add quantities of different dimensions")
            self.symbol = "(" + str(value) + ")"	# better than nothing
        return value
    def __radd__(self, x):
        return physical_quantity(x+float(self), self.unit_pows, self.unit_symbols)  # should only be called for addition to a scalar
    def __sub__(self, x):
        value = physical_quantity(self.numerical, self.unit_pows, self.unit_symbols)
        try:
            value.numerical -= x.numerical	# assume it is another physical_quantity ...
        except:
            try:
                return -x + self    # calls __radd__ to handle potential subtraction of pure scalar
            except:
                raise TypeError("must be another physical_quantity (unless quantity is unitless)")
        else:
            if x.unit_symbols is not value.unit_symbols:  raise AssertionError("only operations on quantities within same unit system are supported")		# implicitly guarantees that unit_pows of value and x have same length, since always checked
            if value.unit_pows!=x.unit_pows:  raise ArithmeticError("cannot subtract quantities of different dimensions")
            self.symbol = "(" + str(value) + ")"	# better than nothing
        return value
    def __rsub__(self, x):
        return physical_quantity(x-float(self), self.unit_pows, self.unit_symbols)  # should only be called for subtraction from a scalar
    def __mul__(self, x):
        value = physical_quantity(self.numerical, self.unit_pows, self.unit_symbols)
        try:
            value.numerical *= x.numerical	# assume it is another physical_quantity ...
        except:
            value.numerical *= x		# ... or a pure numerical scalar
            value.symbolic(self.symbol + " " + str(x))	# better than nothing
        else:
            if x.unit_symbols is not value.unit_symbols:  raise AssertionError("only operations on quantities within same unit system are supported")		# implicitly guarantees that unit_pows of value and x have same length, since always checked
            for i,xpow in enumerate(x.unit_pows):  value.unit_pows[i] += xpow	# it has already been checked by __init__ that these are all rational
            value.symbolic(self.symbol + " " + x.symbol)
        return value
    def __rmul__(self, x):
        value = physical_quantity(self.numerical, self.unit_pows, self.unit_symbols)
        value.numerical *= x	# should only be called for multiplication by a scalar
        value.symbolic(str(x) + " " + self.symbol)	# better than nothing
        return value
    def __neg__(self):
        return -1*self    # calls __rmul__
    def __truediv__(self, x):
        value = physical_quantity(self.numerical, self.unit_pows, self.unit_symbols)
        try:
            value.numerical /= x.numerical	# assume it is another physical_quantity ...
        except:
            value.numerical /= x		# ... or a pure numerical scalar
            value.symbolic(self.symbol + "/" + str(x))  # better than nothing
        else:
            if x.unit_symbols is not value.unit_symbols:  raise AssertionError("only operations on quantities within same unit system are supported")		# implicitly guarantees that unit_pows of value and x have same length, since always checked
            for i,xpow in enumerate(x.unit_pows):  value.unit_pows[i] -= xpow	# it has already been checked by __init__ that these are all rational
            value.symbolic(self.symbol + "/" + x.symbol)
        return value
    def __rtruediv__(self, x):
        value = physical_quantity(self.numerical, self.unit_pows, self.unit_symbols)
        for i in range(len(value.unit_pows)):  value.unit_pows[i] *= -1
        value.numerical = x/value.numerical	# should only be called for division of a scalar
        value.symbolic(str(x) + "/" + self.symbol)	# better than nothing
        return value
    def __pow__(self, n):	# Think I need to double-check that n is rational?  Filter through __init__ ?
        if not isinstance(n,(int,Fraction)):  raise ValueError("powers of physical quantities units must be rational ... use fractions.Fraction")
        value = physical_quantity(self.numerical, self.unit_pows, self.unit_symbols)
        value.numerical = value.numerical**n
        for i in range(len(value.unit_pows)):  value.unit_pows[i] *= n
        value.symbolic("(" + self.symbol + ")" + "**" + str(n))		# better than nothing
        return value
    def __str__(self):
        return self.formatted("{}")
    def formatted(self,format_str):
        return format_str.format(self.numerical) + self._unit_string()
    def in_(self, unit=None, format="{}"):
        to_print = self
        append = ""
        if unit is not None:
            to_print = self / unit
            append = " "+unit.symbol
        return to_print.formatted(format) + append
    def _unit_string(self):
        string = ""
        for u_pow,u_sym in zip(self.unit_pows, self.unit_symbols):
            n, d = u_pow.numerator, u_pow.denominator
            if n!=0:
                if d!=1:
                    string += " " + u_sym + "^(" + str(n) + "/" + str(d) + ")"
                else:
                    if n!=1:
                        string += " " + u_sym + "^" + str(n)
                    else:
                        string += " " + u_sym
        return string





def unit_system(*unit_symbols):
    empty_unit_pows = [Fraction(0,1) for _ in range(len(unit_symbols))]		# safer than [...]*n for mutable types
    unit_pows = list(empty_unit_pows)
    unit_quantities = [physical_quantity(1,unit_pows,unit_symbols).symbolic("")]		# facilitates the creation of named unitless constants (pi, N_A, etc)
    for i,unit in enumerate(unit_symbols):
        unit_pows = list(empty_unit_pows)
        unit_pows[i] = Fraction(1,1)
        unit_quantities += [physical_quantity(1,unit_pows,unit_symbols).symbolic(unit)]
    return unit_quantities

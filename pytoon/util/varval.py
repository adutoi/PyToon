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
from .general import struct, as_dict, nested



# These implement the functionality that allows the user to delay specification of certain entity properties by substituting a string of
# their choice in its stead.  Since evaluation is lazy (done only at render time), the value can be passed in later, usually inherited from
# a parent composite object.  The inner function of variable_evaluator does the actual resolving of the substitution.  It is only meant for
# use on simple, hashable datatypes, (nested) tuples/lists/dicts/structs thereof, or a more complex objects that has the _value_() special
# method defined.  Crazy things might happen if given some more complicated object (unless _value_() is defined).

def variable_evaluator(substitutions, *, inner=None):
    """ provides a function that converts symbolically represented variables (as strings) to their context-dependent values, based on a dictionary of substitutions """
    def varval(obj):
        """ evaluates the context-dependent value of obj (or its components) and returns it; might just be itself, a simple substitution, or a user-implemented alogorithm to decide """
        try:
            value = obj._value_(substitutions)    # if the special method _value_ is implemented the dictionary acts as input for an arbitrary algorithm
        except AttributeError:
            try:
                succeeded = False
                for k,v in substitutions.items():         # otherwise go one by one and see if object is callable with *single* keyword argument from substitutions
                    sucess = True
                    try:
                        value = obj(**{k:v})
                    except:
                        success = False
                    else:
                        if succeeded:
                            raise ValueError("multiple matching arguments for function found")    # not the most useful exception, since will then proceed with trying regular substitition, etc
                        succeeded = True
                if not succeeded:
                    raise ValueError("no matching arguments for function found")
            except ValueError:
                try:
                    value = substitutions[obj]    # if obj is hashable and found as a key in the dictionary, it is substituted
                except (TypeError, KeyError):
                    if isinstance(obj, struct):
                        value = struct(**{ k:varval(v) for k,v in as_dict(obj).items() })    # if it is a struct, recur inside
                    elif isinstance(obj, dict):
                        value = { k:varval(v) for k,v in obj.items() }                       # if it is a dict, recur inside
                    elif isinstance(obj, (tuple, list)):
                        value = type(obj)( varval(i) for i in obj )                          # if it is an iterable (but not str), recur inside
                    else:
                        value = obj                                                          # if none of the above (esp, string or number), leave it alone
        return value
    if inner:
        return nested(outer=varval, inner=inner)
    else:
        return varval

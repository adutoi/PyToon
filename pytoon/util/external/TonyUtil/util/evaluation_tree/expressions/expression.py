#    (C) Copyright 2018, 2020 Anthony D. Dutoi
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
import math
from types import SimpleNamespace as struct
from .. import evaluation_tree

# This file contains utilities for building expression trees based on the common python operators, which are overloaded.
# The resolution of the tree into some result (like a number or printable string) is handled by a dictionary of functions
# whose members correspond to the operations.
# A warning to implementors:  Be really careful that no instance of the expression class (or its children)
# get passed to the back-end implementation.  Since these objects abscond with almost all operations
# including attribute access.



# Basing an objects type on this class defines operators that work on it to recursively build math-like expression trees.
class expression(object):
    def __neg__(self):
        return negative({0: self})
    def __add__(self, other):
        return addition({1: self, 2: other})
    def __radd__(self, other):
        return addition({1: other, 2: self})
    def __sub__(self, other):
        return subtraction({1: self, 2: other})
    def __rsub__(self, other):
        return subtraction({1: other, 2: self})
    def __mul__(self, other):
        return multiplication({1: self, 2: other})
    def __rmul__(self, other):
        return multiplication({1: other, 2: self})
    def __truediv__(self, other):
        return division({1: self, 2: other})
    def __rtruediv__(self, other):
        return division({1: other, 2: self})
    def __pow__(self, other):
        return power({1: self, 2: other})
    def __rpow__(self, other):
        return power({1: other, 2: self})
    def __eq__(self, other):
        return equality({1: self, 2: other})
    def __call__(self, *args):
        return call({"callable": self, **{k:v for k,v in enumerate(args)}})
    def __getitem__(self, index):
        return subscript({"subscriptable": self, "index":index})
    def __getattr__(self, attr):
        return member({"namespace": self, "attribute": attr})



# Called to resolve the terminal elements of an expression tree, which might be of any type (not necessarily based on tree_node or expression).
def evaluate_variable(value, label, context):
    return context.action_dict["variable"](value, label, context.context)

# A thin wrapper with expression-building operations defined.  Can also be used as a base class, where ._value presents the resolving information.
# If you have an instance of expression class (or child), it must have _evaluate defined directly, or else its attempted access builds another expression.
class variable(expression):
    def __init__(self, value):
        self._value = value
    def _evaluate(self, label, context):
        return evaluate_variable(self._value, label, context)



# A base class for non-terminal (operation) nodes in the expression tree, based on both expression and tree_node
class operation(evaluation_tree.tree_node, expression):
    def __init__(self, args):
        evaluation_tree.tree_node.__init__(self, args)
    def _implementation(self, label, context):
        raw_context, action = context.action_dict[type(self).__name__](label, context.context)
        new_context = struct(action_dict=context.action_dict, evaluate_terminus=evaluate_variable, context=raw_context)
        return new_context, action

# Concrete classes representing operations (non-terminal elements) within an expression tree.
# - usually be instantiated automatically/recursively
class negative(operation):        pass
class addition(operation):        pass
class subtraction(operation):     pass
class multiplication(operation):  pass
class division(operation):        pass
class power(operation):           pass
class equality(operation):        pass
class call(operation):            pass
class subscript(operation):       pass
class member(operation):          pass
# - instantiated explictly by user
class array(operation):           pass
class mapping(operation):         pass
class ternary(operation):         pass
class abs_value(operation):       pass    # special because pencil and paper notation ...
class square_rt(operation):       pass    # ... is not usually that of a function call



# Some common mathematical functions, suitable for use in expressions
def ifelse(q,t,f):  return ternary({"conditional": q, "if_true": t, "if_false": f})
def sqrt(x):  return square_rt({0: x})
def absv(x):  return abs_value({0: x})
exp   = variable(math.exp)
log   = variable(math.log)
log10 = variable(math.log10)
sin   = variable(math.sin)
asin  = variable(math.asin)
cos   = variable(math.cos)
acos  = variable(math.acos)
tan   = variable(math.tan)
atan  = variable(math.atan)



# Returns a function that resolves an expression based on functions in the specified namespace, having the same names as the operation classes.
# These functions have the same signature as a node _implementation, taking a label and context, and returning a new context and an action on resolved subnodes.
def resolver(action_namespace, root_context=None):
    def resolve(expr):
        return evaluation_tree.evaluate(expr, context=struct(action_dict=action_namespace.__dict__,  evaluate_terminus=evaluate_variable, context=root_context))
    return resolve

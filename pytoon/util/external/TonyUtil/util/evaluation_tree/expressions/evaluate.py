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
import operator
import math
from . import expression



def _binary(args, op):
    a1 = args[1]
    a2 = args[2]
    return op(a1,a2)

class evaluate(object):
    def variable(value, position, context):
        return value
    def negative(position, context):
        def action(args):
            a = args[0]
            return -a
        return context, action
    def addition(position, context):
        def action(args):
            return _binary(args, operator.add)
        return context, action
    def subtraction(position, context):
        def action(args):
            return _binary(args, operator.sub)
        return context, action
    def multiplication(position, context):
        def action(args):
            return _binary(args, operator.mul)
        return context, action
    def division(position, context):
        def action(args):
            return _binary(args, operator.truediv)
        return context, action
    def power(position, context):
        def action(args):
            return _binary(args, operator.pow)
        return context, action
    def equality(position, context):
        def action(args):
            return _binary(args, operator.eq)
        return context, action
    def call(position, context):
        def action(args):
            f = args["callable"]
            x = [args[key] for key in range(len(args)-1)]
            return f(*x)
        return context, action
    def subscript(position, context):
        def action(args):
            a = args["subscriptable"]
            i = args["index"]
            return a[i]
        return context, action
    def member(position, context):
        def action(args):
            o = args["namespace"]
            m = args["attribute"]
            return getattr(o,m)
        return context, action
    def array(position, context):
        def action(args):
            return [args[key] for key in range(len(args))]
        return context, action
    def mapping(position, context):
        def action(args):
            return args
        return context, action
    def abs_value(position, context):
        def action(args):
            a = args[0]
            return abs(a)
        return context, action
    def square_rt(position, context):
        def action(args):
            a = args[0]
            return math.sqrt(a)
        return context, action
    def ternary(position, context):
        def action(args):
            q = args["conditional"]
            t = args["if_true"]
            f = args["if_false"]
            return (t if q else f)
        return context, action

resolve = expression.resolver(evaluate)

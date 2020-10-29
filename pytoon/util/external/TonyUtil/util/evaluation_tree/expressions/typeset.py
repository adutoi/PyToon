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



class context_class(object):
    def __init__(self, parent=None, templates=None):
        self.parent = parent
        self.templates = templates
    def subcontext(self, parent):
        return context_class(parent, self.templates)



def variable(value, position, context):
    try:
        negative = value<0
    except TypeError:
        negative = False
    try:
        _ = float(value)                                  # assume it is some kind of number
    except (TypeError, ValueError):
        try:
            string = value.__name__                       # assume it is the name of a function
        except AttributeError:
            string = context.templates["var"](value)      # assume it is a symbolic variable
        else:
            string = context.templates["fnc"](string)
    else:
        try:
            n, d = value.numerator, value.denominator
        except AttributeError:
            string = context.templates["num"](value)
        else:
            if d==1:
                string = context.templates["num"](n)
            else:
                string = context.templates["div"](context.templates["num"](n), context.templates["num"](d))
    encapsulate = False
    if negative and context.parent=="negative":
        encapsulate = True
    if negative and context.parent=="ternary":
        encapsulate = True
    if negative and context.parent=="power" and position==1:
        encapsulate = True
    if negative and context.parent in ("addition", "subtraction", "multiplication") and position==2:
        encapsulate = True
    if encapsulate:
        string = context.templates["par"](string)
    return string

def negative(position, context):
    def action(args):
        a = args[0]
        string =  context.templates["neg"](a)
        encapsulate = False
        if context.parent=="negative":
            encapsulate = True
        if context.parent=="ternary":
            encapsulate = True
        if context.parent=="power" and position==1:
            encapsulate = True
        if context.parent in ("addition", "subtraction",  "multiplication") and position==2:
            encapsulate = True
        if encapsulate:
            string = context.templates["par"](string)
        return string
    return context.subcontext(parent="negative"), action

def addition(position, context):
    def action(args):
        a1 = args[1]
        a2 = args[2]
        string = context.templates["add"](a1,a2)
        encapsulate = False
        if context.parent in ("negative", "multiplication", "ternary"):
            encapsulate = True
        if context.parent=="subtraction" and position==2:
            encapsulate = True
        if context.parent=="power" and position==1:
            encapsulate = True
        if encapsulate:
            string = context.templates["par"](string)
        return string
    return context.subcontext(parent="addition"), action

def subtraction(position, context):
    def action(args):
        a1 = args[1]
        a2 = args[2]
        string = context.templates["sub"](a1,a2)
        encapsulate = False
        if context.parent in ("negative", "multiplication", "ternary"):
            encapsulate = True
        if context.parent=="subtraction" and position==2:
            encapsulate = True
        if context.parent=="power" and position==1:
            encapsulate = True
        if encapsulate:
            string = context.templates["par"](string)
        return string
    return context.subcontext(parent="subtraction"), action

def multiplication(position, context):
    def action(args):
        a1 = args[1]
        a2 = args[2]
        string = context.templates["mul"](a1,a2)
        encapsulate = False
        if context.parent=="ternary":
            encapsulate = True
        if context.parent=="power" and position==1:
            encapsulate = True
        if encapsulate:
            string = context.templates["par"](string)
        return string
    return context.subcontext(parent="multiplication"), action

def division(position, context):
    def action(args):
        a1 = args[1]
        a2 = args[2]
        string = context.templates["div"](a1,a2)
        encapsulate = False
        if context.parent=="ternary":
            encapsulate = True
        if context.parent=="power" and position==1:
            encapsulate = True
        if encapsulate:
            string = context.templates["par"](string)
        return string
    return context.subcontext(parent="division"), action

def power(position, context):
    def action(args):
        a1 = args[1]
        a2 = args[2]
        string = context.templates["pow"](a1,a2)
        encapsulate = False
        if context.parent=="ternary":
            encapsulate = True
        if encapsulate:
            string = context.templates["par"](string)
        return string
    return context.subcontext(parent="power"), action

def equality(position, context):
    def action(args):
        a1 = args[1]
        a2 = args[2]
        string = context.templates["eql"](a1,a2)
        encapsulate = False
        if context.parent=="ternary":
            encapsulate = True
        if encapsulate:
            string = context.templates["par"](string)
        return string
    return context.subcontext(parent="equality"), action

def call(position, context):
    def action(args):
        f = args["callable"]
        x = [args[key] for key in range(len(args)-1)]
        return context.templates["cll"](f,x)
    return context.subcontext(parent="call"), action

def subscript(position, context):
    def action(args):
        a = args["subscriptable"]   
        i = args["index"]
        return context.templates["scr"](a,i)
    return context.subcontext(parent="subscript"), action

def member(position, context):
    def action(args):
        o = args["namespace"]
        m = args["attribute"]
        return context.templates["mem"](o,m)
    return context.subcontext(parent="member"), action

def array(position, context):
    def action(args):
        elements = [args[key] for key in range(len(args))]
        return context.templates["arr"](elements)
    return context.subcontext(parent="array"), action

def mapping(position, context):
    def action(args):
        pairs = [context.templates["ass"](k,v) for k,v in args.items()]
        return context.templates["map"](pairs)
    return context.subcontext(parent="mapping"), action

def abs_value(position, context):
    def action(args):
        a = args[0]
        return context.templates["abs"](a)
    return context.subcontext(parent="abs_value"), action

def square_rt(position, context):
    def action(args):
        a = args[0]
        return context.templates["sqt"](a)
    return context.subcontext(parent="square_rt"), action

def ternary(position, context):
    def action(args):
        q = args["conditional"]
        t = args["if_true"]
        f = args["if_false"]
        return context.templates["par"](context.templates["ift"](q,t,f))    # just be safe with parentheses, since ugly anyway
    return context.subcontext(parent="ternary"), action

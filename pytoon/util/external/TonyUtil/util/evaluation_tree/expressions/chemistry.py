#    (C) Copyright 2020 Anthony D. Dutoi
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
from . import expression



class context_class(object):
    def __init__(self, parent=None, parent_context=None):
        self.parent = parent
        self.parent_context = parent_context
    def subcontext(self, parent):
        return context_class(parent, self)



class typeset_html(object):
    def variable(value, position, context):
        try:
            _ = float(value)
        except (TypeError, ValueError):
            string = str(value)
            if context.parent=="multiplication" and position==2:
                string = "<sub><em>{}</em></sub>".format(string)
        else:
            if context.parent=="multiplication":
                try:
                    n, d = value.numerator, value.denominator
                except AttributeError:
                    string = str(value)
                else:
                    if d==1:
                        string = str(n)
                    else:
                        string = "<sup>{}</sup>&frasl;<sub>{}</sub>".format(n,d)
                if position==1:
                    if context.parent_context is not None:
                        if context.parent_context.parent=="addition":
                            string = "&bull;{}".format(string)
                if position==2:
                    string = "<sub>{}</sub>".format(string)
            if (context.parent=="power" or context.parent=="subscript") and position==2:
                if value>1:    string = "{}+".format(value)
                if value==+1:  string = "+"
                if value== 0:  string = "0"
                if value==-1:  string = "&minus;"
                if value<-1:   string = "{}&minus;".format(abs(value))
        return string
    def addition(position, context):
        def action(args):
            a1 = args[1]
            a2 = args[2]
            string = "{}{}".format(a1,a2)
            if context.parent=="multiplication" and position==1:
                string = "({})".format(string)
            return string
        return context.subcontext(parent="addition"), action
    def multiplication(position, context):
        def action(args):
            a1 = args[1]
            a2 = args[2]
            string = "{}{}".format(a1,a2)
            return string
        return context.subcontext(parent="multiplication"), action
    def power(position, context):
        def action(args):
            a1 = args[1]
            a2 = args[2]
            return "{}<sup>{}</sup>".format(a1,a2)
        return context.subcontext(parent="power"), action
    def call(position, context):
        def action(args):
            substance = args["callable"]
            state     = [args[key] for key in range(len(args)-1)]
            return "{} ({})".format(substance, ", ".join("{}".format(s) for s in state))
        return context.subcontext(parent="call"), action
    def subscript(position, context):
        def action(args):
            substance = args["subscriptable"]
            charge    = args["index"]
            if charge=="":
                 return "[{}]".format(substance)
            else:
                return "[{}]<sup>{}</sup>".format(substance,charge)
        return context, action




class typeset_latex(object):
    def variable(value, position, context):
        try:
            _ = float(value)
        except (TypeError, ValueError):
            string = str(value)
            if context.parent=="multiplication" and position==2:
                string = "$_{}$".format(string)
        else:
            if context.parent=="multiplication":
                try:
                    n, d = value.numerator, value.denominator
                except AttributeError:
                    string = str(value)
                else:
                    if d==1:
                        string = str(n)
                    else:
                        string = "\\\\frac{{{}}}{{{}}}".format(n,d)
                if position==1:
                    if context.parent_context is not None:
                        if context.parent_context.parent=="addition":
                            string = "$\\\\cdot{}$".format(string)
                    else:
                        string = "${}$".format(string)
                if position==2:
                    string = "$_{{{}}}$".format(string)
            if (context.parent=="power" or context.parent=="subscript") and position==2:
                if value>1:    string = "{}+".format(value)
                if value==+1:  string = "+"
                if value== 0:  string = "0"
                if value==-1:  string = "-"
                if value<-1:   string = "{}-".format(abs(value))
        return string
    def addition(position, context):
        def action(args):
            a1 = args[1]
            a2 = args[2]
            string = "{}{}".format(a1,a2)
            if context.parent=="multiplication" and position==1:
                string = "({})".format(string)
            return string
        return context.subcontext(parent="addition"), action
    def multiplication(position, context):
        def action(args):
            a1 = args[1]
            a2 = args[2]
            string = "{}{}".format(a1,a2)
            return string
        return context.subcontext(parent="multiplication"), action
    def power(position, context):
        def action(args):
            a1 = args[1]
            a2 = args[2]
            return "{}$^{{{}}}$".format(a1,a2)
        return context.subcontext(parent="power"), action
    def call(position, context):
        def action(args):
            substance = args["callable"]
            state     = [args[key] for key in range(len(args)-1)]
            return "{} ({})".format(substance, ", ".join("\\\\textit{{{}}}".format(s) for s in state))
        return context.subcontext(parent="call"), action
    def subscript(position, context):
        def action(args):
            substance = args["subscriptable"]
            charge    = args["index"]
            if charge=="":
                 return "[{}]".format(substance)
            else:
                return "[{}]$^{{{}}}$".format(substance,charge)
        return context, action






html  = expression.resolver(typeset_html, context_class())
latex = expression.resolver(typeset_latex, context_class())

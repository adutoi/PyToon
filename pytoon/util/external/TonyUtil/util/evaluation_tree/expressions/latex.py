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
from . import expression
from . import typeset



templates = {
    "var": lambda s:     "{{{}}}".format(s),
    "num": lambda a:     "{{{}}}".format(a),
    "neg": lambda a:     "-{{{}}}".format(a),
    "add": lambda a1,a2: "{} + {}".format(a1,a2),
    "sub": lambda a1,a2: "{} - {}".format(a1,a2),
    "mul": lambda a1,a2: "{} \\times {}".format(a1,a2),
    "div": lambda a1,a2: "\\frac{{{}}}{{{}}}".format(a1,a2),
    "pow": lambda a1,a2: "{}^{{{}}}".format(a1,a2),
    "fnc": lambda f:     "\\text{{{}}}".format(f),
    "arr": lambda e:     "\\left[{}\\right]".format(", ".join(e)),
    "ass": lambda k,v:   "{}: {}".format(k,v),
    "map": lambda e:     "\\left{{{}\\right}}".format(", ".join(e)),
    "cll": lambda f,x:   "{}\\left({}\\right)".format(f, ", ".join(x)),
    "scr": lambda a,i:   "{}_{}".format(a,i),
    "abs": lambda a:     "\\left|{}\\right|".format(a),
    "sqt": lambda a:     "\\sqrt{{{}}}".format(a),
    "par": lambda s:     "\\left({}\\right)".format(s)
}



resolve = expression.resolver(typeset, typeset.context_class(templates=templates))

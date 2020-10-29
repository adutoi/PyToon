#  (C) Copyright 2013, 2020 Anthony D. Dutoi
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
from . import base


# This stuff has not been updated since some major overhauls of the calling code, so it may not work



# This prints at the top of the python script, making it take a filename argument for
# the image output (which would be identical to the input, if it has a .py extension).

py_header = """\
import os
import sys
from pytoon import draw

def create_output(scriptname, args):
    def usage():
        print("Usage:  python {} [-f] <outfilename>".format(scriptname))
        print("<outfilename> is the name of the output file, including an extention, which determines the format of the image.")
        print("Use -f to force overwriting of <outfilename>.")
    if len(args)==3:
        if args[1]!="-f":
            usage()
            sys.exit()
        force = True
        filename = args[2]
    elif len(args)==2:
        force = False
        filename = args[1]
    else:
        usage()
        sys.exit()
    try:
        filestem, ext = os.path.splitext(filename)
    except:
        usage()
        raise
    if not force and os.path.exists(filename):
        sys.exit("Output file already exists.  Use -f to force overwriting of {}".format(filename))
    try:
        canvas = {".svg": draw.svg, ".py": draw.py}[ext](filestem)
    except:
        print("Invalid or unimplemented extension")
        raise
    return canvas

canvas = create_output(__file__, sys.argv)
"""

py_footer = """
canvas.finish()
"""



# The render class can be so simple because all of the arguments to these functions are extremely
# simple in nature, just nested namespace (.util.struct) objects, terminating at simple datatypes,
# like strings and numbers, so .format() knows what to do with them automatically.
# By the time any of these methods are called, we can assume that arguments are validated, complete structures.

class renderer(base.renderer):
    """ resolves and buffers the drawing calls back into python code (for debugging?) """
    def __init__(self, stream):
        base.renderer.__init__(self, stream)
        self._stream.write(py_header)
    def _finish(self):
        self._stream.write(py_footer)
    def path(self, lstyle, fstyle, points):
        self._stream.write("canvas.path({}, {}, {})\n".format(lstyle, fstyle, points))
    def image(self, filename, size, position, rotate):
        self._stream.write("canvas.image({}, {}, {}, {})\n".format(filename, size, position, rotate))
    def line(self, lstyle, begin, end):
        self._stream.write("canvas.line({}, {}, {})\n".format(lstyle, begin, end))
    def polygon(self, lstyle, fstyle, points):
        self._stream.write("canvas.polygon({}, {}, {})\n".format(lstyle, fstyle, points))
    def arc(self, lstyle, fstyle, begin, end, radius, skew):
        self._stream.write("canvas.arc({}, {}, {}, {}, {}, {})\n".format(lstyle, fstyle, begin, end, radius, skew))
    def circle(self, lstyle, fstyle, center, radius):
        self._stream.write("canvas.circle({}, {}, {}, {})\n".format(lstyle, fstyle, center, radius))

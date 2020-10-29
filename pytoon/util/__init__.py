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

from .external   import svg_code, js_code    # would be free-standing module files, so import directly to this level
from .general    import struct, as_tuple, as_dict, int_round, echo, nested, float_eq, valid_real_number, valid_point, shell, code_template
from .varval     import variable_evaluator
from .animated   import is_animated, animated, deanimated
from .colors     import colordef, gray_rgb, color_parser
from .styles     import linestyle, fillstyle, style_parsers
from .image      import image_file

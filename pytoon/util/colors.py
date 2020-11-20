#  (C) Copyright 2013, 2018, 2020 Anthony D. Dutoi
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
from .external import named_colors, color_wheel
from .general  import struct, int_round, valid_real_number

no_color = (None, "none", "transparent", "clear")    # also used in styles.py (None should be interpreted as "not specified", whereas "none" is explicitly no color)



def colordef(rgb, a):
    """ takes an an RGB code in #RRGGBB format and an alpha value between 0 and 1 (inclusive) and rolls them into a single structure """
    return struct(rgb=rgb, a=a)



def _valid_alpha(a):
    """ ensures that a is a valid value for an alpha channel (including None) """
    if a is not None:
        a = valid_real_number((a, "alpha channel of color"), (lambda x: 0<=x<=1, "None or convertible to a float between 0 and 1, inclusive"))
    return a

def _validate_rgb(code):
    """ ensures that a string of the has the form #RRGGBB and represents a valid RGB code """
    if isinstance(code, str):
        if (len(code)==7 and code[0]=="#"):
            try:
                int(code[1:], base=16)
            except ValueError:
                raise ValueError( "supposed hex part of RGB code does not parse: {}".format(repr(code)) )
        else:
            raise ValueError( "badly formatted RGB code: {}".format(repr(code)) )
    else:
        raise ValueError( "RGB code should be a string: {}".format(repr(code)) )
    return



def _rgb_code(color_name):
    """ converts a valid color-name string to an RGB code, or returns argument if already a valid RGB code """
    code = color_name
    try:
        _validate_rgb(code)
    except ValueError:
        try:
            code = named_colors[color_name]
        except KeyError:
            raise ValueError( "invalid color name or RGB code: {}".format(repr(color_name)) )
    return code

def _gray(rgb):
    """ maps an already validated RGB code in #RRGGBB format to an RGB code in grayscale (if not already) """
    rr, gg, bb = ( int(hexInt, base=16) for hexInt in (rgb[1:3], rgb[3:5], rgb[5:7]) )
    if rr==gg==bb:
        return rgb    # if it is already a grayscale color, leave it alone
    else:
        yy = "{:02X}".format(int_round( 0.2126*rr + 0.7152*gg + 0.0722*bb ))    # see http://en.wikipedia.org/wiki/Grayscale
        return "#{}{}{}".format(yy, yy, yy)

def _render_color(grayscale):
    """ provides a function that converts a color name (or code) to an RGB code, optionally in grayscale, depending on the boolean argument """
    def render(color):
        """ converts a color name to an RGB code{} """.format(" in grayscale" if grayscale else "")
        if color in no_color:
            return "none"
        else:
            rgb = _rgb_code(color)             # checks that color name or code is valid and converts it, if necessary
            if grayscale:  rgb = _gray(rgb)    # potential coversion to grayscale RGB code (no argument validation)
            return rgb
    return render

gray_rgb = _render_color(grayscale=True)    # for export to the outside world



def _parse_color_string(color, rgb_render):
    """ converts color string with alpha multiplier to a (grayscale) color structure, given a renderer that processes color names/codes """
    if color is None:
        return colordef("none", 0)
    # from here on, assume it is a string
    a = None
    try:
        fields = [ field.strip() for field in color.split("*") ]
    except AttributeError:
        raise ValueError( "expected color represented as None or string: {}".format(repr(color)) )
    else:
        try:
            rgb, = fields
        except ValueError:
            try:
                field1, field2 = fields
            except ValueError:
                raise ValueError( "the * notation in color string requires exactly two operands: {}".format(repr(color)) )
            else:
                try:
                    a = _valid_alpha(field1)        # a must logically be a number (not None) here
                except ValueError:
                    try:
                        a = _valid_alpha(field2)    # a must logically be a number (not None) here
                    except ValueError:
                        raise ValueError( "one operand of * in color string must be a number: {}".format(repr(color)) )
                    rgb = field1
                else:
                    rgb = field2
        rgb = rgb_render(rgb)      # rgb_render (passed in) converts a valid color name to an RGB code (or raises exception), potentially in grayscale
        if rgb=="none":  a = 0     # if color is none, a should be zero for consistency, but not necessarily the other way around
    return colordef(rgb, a)

def color_parser(*, grayscale):
    """ provides a function that validates color structures, or promotes color string with alpha multiplier, perhaps converting to grayscale, depending on boolean """
    rgb_render = _render_color(grayscale)
    def parse(color):
        try:
            rgb, a = color.rgb, color.a
        except AttributeError:
            try:
                color_struct = _parse_color_string(color, rgb_render)    # The main event, assuming not just acting as just a validator
            except ValueError:
                raise ValueError( "color must be color structure or valid string description: {}".format(repr(color)) )
        else:
            rgb = rgb_render(rgb)    # validates rgb and potentially converts to grayscale
            if rgb=="none":  a = 0   # if color is none, a should be zero for consistency, but not necessarily the other way around
            color_struct = colordef(rgb, _valid_alpha(a))    # validates a
        return color_struct
    return parse

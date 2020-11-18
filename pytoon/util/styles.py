#  (C) Copyright 2012, 2020 Anthony D. Dutoi
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
from .general  import struct, as_dict, as_tuple, valid_real_number
from .animated import is_animated, animated, validator
from .colors   import color_parser, no_color



class style(struct):    # based on struct because member data *is* the public interface (freeform, then parsed and checked at time of concrete resolution)
    """ provides some in-common methods for streamlining dealing with animated properties """
    def has_animated(self):
        """ answers whether the style has any animated components (not counting excluded ones) """
        return any(is_animated(v) for k,v in as_dict(self).items() if k not in self._exclude)
    def animated(self):
        """ returns a copy where all components (except those excluded) are formally animated, even those that are constant """
        descriptors = {k:animated(v) for k,v in as_dict(self).items() if k not in self._exclude}
        return type(self)(self, **descriptors)    # copy with updates



class linestyle(style):
    """ rolls a color, weight, dash descriptor into a single structure """
    _exclude = []    # used by base class, essentially means that all fields represent animatable properties
    def __init__(self, _lstyle=None, *, color=None, weight=None, dash=None):
        c, w, d = "black", 1, "solid"
        if _lstyle:  c, w, d = as_tuple(_lstyle("color", "weight", "dash"))
        if color  is not None:  c = color
        if weight is not None:  w = weight
        if dash   is not None:  d = dash
        struct.__init__(self, color=c, weight=w, dash=d)
    def _populate_field(self, field, validators, allow_animated, _allow_recur=True):
        """ a private function that the parser static method can use to build linestyle objects; calls itself recursively """
        # takes a (tuple of) field descriptor(s), decides what it(they) describe(s), and assigns it(them) to appropriate field of the line style
        valid_color, valid_dash, valid_weight = validators
        try:
            tmp = valid_color(field, allow_animated)
        except ValueError:
            try:
                tmp = valid_dash(field, allow_animated)
            except ValueError:
                try:
                    tmp = valid_weight(field, allow_animated)
                except ValueError:
                    if _allow_recur and not isinstance(field, str):   # strings give an infinite loop, and, if not parsed by valid_color or valid_dash, then it is an error
                        try:
                            for fld in field:  self._populate_field(fld, validators, allow_animated, False)    # since it was not a primitive field, maybe it was a tuple of valid values
                        except (TypeError, ValueError):
                            raise ValueError( "line style parameter(s) not recognized as valid data type or value: {}".format(repr(field)) )
                    else:
                        raise ValueError( "line style parameter(s) not recognized as valid data type or value: {}".format(repr(field)) )
                else:
                    self.weight = tmp
            else:
                self.dash = tmp
        else:
            self.color = tmp
        return self    # the (modified) input object (for convenience)
    @staticmethod
    def _render_dash(dash):
        """ converts named dash type to dash tuple or validates given representation as iterable """
        if   dash=="solid":  parsed_dash = tuple()
        elif dash=="dotted": parsed_dash = (1,1)
        elif dash=="dashed": parsed_dash = (4,4)
        else:
            try:
                parsed_dash = tuple( valid_real_number((d, "dash length"), (lambda x: x>0, "positive")) for d in dash )
            except (TypeError, ValueError):
                raise ValueError( "dash descriptor is expected to be an iterable of positive float-convertibles, or valid textual descriptor: {}".format(repr(dash)) )
            if len(parsed_dash)%2!=0:
                raise ValueError( "dash descriptor array must have an even number of elements: {}".format(repr(dash)) )
        return parsed_dash
    @staticmethod
    def parser(render_color):
        """ provides a function that validates or builds linestyle stuctures, given a function that validates color or builds color structures """
        valid_color  = validator(render_color)    # render_color (passed in) validates color structures or promotes strings, perhaps converting to grayscale
        valid_dash   = validator(linestyle._render_dash)
        valid_weight = validator(lambda f: valid_real_number((f, "line weight"), (lambda x: x>=0, "non-negative"))) 
        def parse(style, _allow_animated=True):
            if is_animated(style):
                if _allow_animated:
                    parsed_style = [(t, parse(s, False)) for t,s in style]    # promote the individuals to complete linestyle structures
                    color  = [(t, s.color)  for t,s in parsed_style]          #
                    weight = [(t, s.weight) for t,s in parsed_style]          # aggregate insides of individual linestyles into one linestyle structure
                    dash   = [(t, s.dash)   for t,s in parsed_style]          #
                    parsed_style = linestyle(color=color, weight=weight, dash=dash)
                else:
                    raise TypeError("animated property data given for single time point")
            else:
                try:
                    parsed_style = linestyle(
                        color  = valid_color( style.color,  _allow_animated),
                        weight = valid_weight(style.weight, _allow_animated),
                        dash   = valid_dash(  style.dash,   _allow_animated)
                    )
                except (AttributeError, ValueError):
                    lstyle = parse(linestyle())    # promotes/validates default parameters before partial replacement(w promoted/validated values)
                    parsed_style = lstyle._populate_field(style, (valid_color, valid_dash, valid_weight), _allow_animated)    # also works when style is a tuple of descriptors in any order
            return parsed_style
        return parse



def _colorstop(percent, color):
    """ rolls a percentage and a color into a single object """
    return struct(percent=percent, color=color)

def _parse_colorstop(stop, render_color):
    """ promotes a color-stop 2-tuple to a _colorstop structure, or validates a _colorstop structure, given a function that validates color or builds color structures """
    try:
        _ = stop.percent
    except:
        try:
            percent, color = stop
        except:
            raise ValueError( "gradient color stop must be color-stop structure or percentage-color 2-tuple: {}".format(repr(stop)) )
        parsed_stop = _parse_colorstop(_colorstop(percent, color))    # Will validate and promote internal values
    else:
        stop_color = "none" if (stop.color in no_color) else stop.color
        parsed_stop = _colorstop(
            valid_real_number((stop.percent, "stop percentage"), (lambda x: 0<=x<=100, "between 0 and 100, inclusive")),
            render_color(stop_color)    # render_color (passed in) validates color structures or promotes strings, perhaps converting to grayscale
        )
    return parsed_stop

def _parse_orientation(orientation):
    return orientation    # eventually, this should do something useful



class fillstyle(style):
    """ rolls descriptors of a fill style into a single structure """
    _exclude = ["fill"]    # used by base class, essentially means that only .fill does not represent animatable property
    def __init__(self, _fstyle=None, *, _fill=None, **kwargs):    # _fill name is sign not to use directly.  Users should use static methods to instantiate wo copying.
        if _fstyle and _fill:
            raise RuntimeError("attempt to update fill type on copy is not interpretable ... use static methods instead of direct instantiation")
        if not (_fstyle or _fill):
            raise RuntimeError("uninterpretable use case for fillstyle.__init__ ... use static methods instead of direct instantiation")
        if _fstyle:
            descriptors = as_dict(_fstyle)
            for k,v in kwargs.items():
                if   k=="fill":         raise RuntimeError("attempt to update fill type on copy is not interpretable")
                elif k in descriptors:  descriptors[k] = v
                else:                   raise RuntimeError("attempt to update undefined fill descriptor upon copy")
        else:
            descriptors = dict(kwargs)
            descriptors["fill"] = _fill
        struct.__init__(self, **descriptors)
    @staticmethod
    def none():
        """ returns a structure that represents no fill """
        return fillstyle(_fill="none")
    @staticmethod
    def solid(color="black"):
        """ returns a structure that represents a solid fill """
        return fillstyle(_fill="solid",  color=color)
    @staticmethod
    def radial(radius=100, begin="black", end="transparent"):
        """ returns a structure that represents a fill with a radial gradient """
        return fillstyle(_fill="radialgradient", radius=radius, begin=begin, end=end)
    @staticmethod
    def linear(colors=[(0,"black"),(100,"transparent")], orientation="up-down"):
        """ returns a structure that represents a fill with a linear gradient """
        return fillstyle(_fill="lineargradient", colors=list(colors), orientation=orientation)    # copy colors for safety since lists are mutable
    @staticmethod
    def parser(render_color):
        """ provides a function that validates or builds fill stuctures, given a function that validates color or builds color structures """
        valid_color  = validator(render_color)    # render_color (passed in) validates color structures or promotes strings, perhaps converting to grayscale
        def parse(style):
            try:
                _ = style.fill
            except:
                if style in no_color:
                    parsed_style = fillstyle.none()
                else:
                    parsed_style = fillstyle.solid(color=valid_color(style))
            else:
                if   style.fill=="none":
                    parsed_style = fillstyle.none()
                elif style.fill=="solid":
                    parsed_style = fillstyle.solid(color=valid_color(style.color))
                elif style.fill=="radialgradient":
                    style_begin = "none" if (style.begin in no_color) else style.begin
                    style_end   = "none" if (style.end   in no_color) else style.end
                    parsed_style = fillstyle.radial(
                        valid_real_number((style.radius, "gradient radius"), (lambda x: x>0, "positive")),
                        render_color(style_begin),
                        render_color(style_end)
                    )
                elif style.fill=="lineargradient":
                    colors = [ _parse_colorstop(stop, render_color) for stop in style.colors ]
                    parsed_style = fillstyle.linear(colors, _parse_orientation(orientation))                
                else:
                    raise ValueError( "unrecognized fill gradient type: {}".format(repr(style)) )
            return parsed_style
        return parse    



def style_parsers(*, grayscale):
    """ provides a 2-tuple of functions that validate or build linestyle and fill structures, respectively, perhaps converting colors to grayscale, depending on boolean """
    render_color = color_parser(grayscale=grayscale)
    return struct(color=render_color, linestyle=linestyle.parser(render_color), fillstyle=fillstyle.parser(render_color))

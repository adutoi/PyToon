#  (C) Copyright 2012, 2013, 2020 Anthony D. Dutoi
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
import io
import math
from ..util import struct, float_eq, svg_code, js_code, image_file
from .      import base



### Some local utilities

_map_displacement = lambda x,y: (x,-y)                # Screen coordinates are upside-down, relative to how mathematicians and physical scientists think, ...
_map_rotation     = lambda a:   -a                    # ... and, consequently, so is the sense/sign of rotation.
_flt              = lambda x:   "" if (x is None) else "{:.5g}".format(x)    # defend file size against absurd precision

def _same(values):
    value = values[0]
    try:
        equal = [float_eq(v,value) for v in values]
    except TypeError:
        return False
    else:
        return all(equal)



### parse a structure to determine options for animation controls (also used outside this file, but perhaps misplaced)

def parse_controls(controls):
    if controls is True:       # note the use of 'is'
        controls = struct(button=True)
    if controls is False:      # note the use of 'is'
        controls = struct(button=False)
    try:
        step = controls.step
    except AttributeError:
        step = 0.2             # frame shift, in seconds of real time
    try:
        key_controls = controls.key_controls
    except AttributeError:
        key_controls = None    # None means "not specified" ... therefore defaults (encoded in js_code module)
    try:
        button = controls.button
    except AttributeError:
        button = False         # do not display a button
    try:
        location = controls.location
    except AttributeError:
        location = (0,0)       # start just below the origin
    else:
        button = True          # if a location was give, clearly we want this on
    try:
        scale = controls.scale
    except AttributeError:
        scale = 1              # do not scale
    else:
        button = True          # if a scale was give, clearly we want this on
    x,y = location
    return step, key_controls, button, (x,-y,scale)



### The svg renderer base class (for both complete files and snippets).
# It has two "channels" and keeps track of a running index to make object ids unique.
# By the time any of these methods are called, we can assume that arguments are validated, complete structures.

class renderer_base(base.renderer):
    """ base class to resolve and buffer the drawing calls into svg code """
    def __init__(self):
        self._main     = ""
        self._defs     = ""
        self._def_id   = 0
        self._dims     = 0, 0, 0, 0    # xmin, xmax, ymin, ymax (in screen coordinates)
        self._duration = None
    def duration(self, duration):
        if duration is None:  self._assert_no_controls()
        self._duration = duration
    def path(self, lstyle, fstyle, points, toggle):
        line_rgb, line_alpha, line_weight, line_dash = self._parse_line(lstyle)
        fill_rgb, fill_alpha = self._parse_fill(fstyle)
        if self._duration is None:
            points = self._parse_points(points)
        else:
            points = [(_flt(t),self._parse_points(pts)) for t,pts in points]
        self._main += svg_code.path(points, line_rgb, line_alpha, line_weight, line_dash, fill_rgb, fill_alpha, self._duration)
    def image(self, filename, size, position, rotate, toggle):
        img = image_file(filename)
        x, y = position
        xsize, ysize = size
        x0, y0 = 0., -ysize     # Will rotate around the bottom left corner
        dx, dy = x-x0 , y-y0    # Placement of the unrotated top-left corner (starts at svg 0,0)
        x0, y0 = _map_displacement(x0, y0)
        dx, dy = _map_displacement(dx, dy)
        rotate = _map_rotation(rotate)
        self._main += svg_code.image(img.filename, xsize, ysize, rotate, x0, y0, dx, dy)
        self._adjust_boundaries(x, y)    # is this right?
    def line(self, lstyle, begin, end, toggle):
        return self._line_as_path(lstyle, begin, end, toggle)
    def polygon(self, lstyle, fstyle, points, toggle):
        return self._polygon_as_path(lstyle, fstyle, points, toggle)
    def arc(self, lstyle, fstyle, begin, end, radius, skew, toggle):
        return self._arc_as_path(lstyle, fstyle, begin, end, radius, skew, toggle)
    def circle_deprecated(self, lstyle, fstyle, center, radius, toggle):
        return self._circle_as_path(lstyle, fstyle, center, radius, toggle)
    def circle(self, lstyle, fstyle, center, radius, toggle):
        line_rgb, line_alpha, line_weight, line_dash = self._parse_line(lstyle)
        fill_rgb, fill_alpha = self._parse_fill(fstyle)
        if self._duration is None:
            center_x, center_y = self._parse_point(center)
            self._adjust_boundaries(center_x+radius, center_y+radius)
            self._adjust_boundaries(center_x-radius, center_y-radius)
            radius = _flt(radius)
            center_x, center_y = _flt(center_x), _flt(center_y)
        else:
            # minor bug here since boundaries never adjusted (user can always put in phantom polygon)
            radius = [(_flt(t),_flt(rad))              for t,rad in radius]
            center = [(_flt(t),self._parse_point(ctr)) for t,ctr in center]
            times, centers = zip(*center)
            center_x, center_y = zip(*centers)
            center_x = [("",center_x[0])] if _same(center_x) else list(zip(times,center_x))
            center_y = [("",center_y[0])] if _same(center_y) else list(zip(times,center_y))
        self._main += svg_code.circle(center_x, center_y, radius, line_rgb, line_alpha, line_weight, line_dash, fill_rgb, fill_alpha, self._duration)
    def _parse_point(self, point):
        x, y = _map_displacement(*point)
        self._adjust_boundaries(x, y)
        return x, y
    def _parse_points(self, points):
        x, y = _map_displacement(*(points[0]))
        pt_string = svg_code.path_beg(_flt(x), _flt(y))
        self._adjust_boundaries(x, y)
        for pt in points[1:]:
            if len(pt)==2:
                x, y = _map_displacement(*pt)
                pt_string += svg_code.path_line(_flt(x), _flt(y))
                self._adjust_boundaries(x, y)
            else:
                x0, y0 = x, y
                x, y, p = pt
                x, y = _map_displacement(x, y)
                if p.curve=="arc":
                    dx, dy = x-x0, y-y0
                    skew = _map_rotation(p.skew) + math.atan2(dy,dx) * 180/math.pi
                    cclockwise = 0
                    if p.rx<0:  cclockwise = 1
                    pt_string += svg_code.path_arc(_flt(abs(p.rx)), _flt(p.ry), _flt(skew), cclockwise, _flt(x), _flt(y))
                    self._adjust_boundaries(x,y)    # seems like this should be more sophistacated
                else:
                    raise NotImplementedError(str(p.curve))    # p.curve should already be a string, but just in case
        return pt_string
    def _parse_line(self, lstyle):
        if self._duration is None:
            if (lstyle.color.rgb=="none") or (lstyle.color.a==0) or (lstyle.weight==0):
                return None, None, None, None
            else:
                rgb    = lstyle.color.rgb
                alpha  = None if (lstyle.color.a is None) else _flt(lstyle.color.a)
                weight = _flt(lstyle.weight)
                dash   = None if (len(lstyle.dash)==0) else svg_code.dash(_flt(d*lstyle.weight) for d in lstyle.dash)
                return rgb, alpha, weight, dash
        else:
            rgb   = []
            alpha = []
            for t,color in lstyle.color:
                rgb   += [(t,color.rgb)]
                alpha += [(t,color.a)]
            if   (len(lstyle.color)==1) and ((rgb[0][1]=="none") or (alpha[0][1]==0)):
                return None, None, None, None
            elif (len(lstyle.weight)==1) and (lstyle.weight[0][1]==0):
                return None, None, None, None
            else:
                rgb_values = [v for t,v in rgb]
                if "none" in rgb_values:
                    raise ValueError("cannot set animated RGB value to 'none'; use alpha channel to achieve this effect")
                if (len(alpha)==1) and (alpha[0][1] is None):
                    alpha = None
                else:
                    alpha = [(t, "1" if (a is None) else _flt(a)) for t,a in alpha]    # if animated need explicit value (because not off)
                weight = [(t,_flt(w)) for t,w in lstyle.weight]
                if (len(lstyle.dash)==1) and (len(lstyle.dash[0][1])==0):
                    dash = None
                else:
                    dash = [(t, svg_code.dash(_flt(d*lstyle.weight[0][1]) for d in dd) ) for t,dd in lstyle.dash]
                return rgb, alpha, weight, dash
    def _parse_fill(self, fstyle):
        self._def_id += 1    # does not matter if we burn an unused number
        static_none = svg_code.fillnone
        animated_none = [(None,static_none)]
        if fstyle.fill=="none":
            if self._duration is None:
                return static_none, None
            else:
                return animated_none, None
        elif fstyle.fill=="solid":
            if self._duration is None:
                if (fstyle.color.rgb=="none") or (fstyle.color.a==0):
                    return static_none, None
                else:
                    rgb    = fstyle.color.rgb
                    alpha  = None if (fstyle.color.a is None) else _flt(fstyle.color.a)
                    return rgb, alpha
            else:
                rgb   = []
                alpha = []
                for t,color in fstyle.color:
                    rgb   += [(t,color.rgb)]
                    alpha += [(t,color.a)]
                if   (len(fstyle.color)==1) and ((rgb[0][1]=="none") or (alpha[0][1]==0)):
                    return animated_none, None
                else:
                    rgb_values = [v for t,v in rgb]
                    if "none" in rgb_values:
                        raise ValueError("cannot set animated RGB value to 'none'; use alpha channel to achieve this effect")
                    if (len(alpha)==1) and (alpha[0][1] is None):
                        alpha = None
                    else:
                        alpha = [(t, "1" if (a is None) else _flt(a)) for t,a in alpha]    # if animated need explicit value (because not off)
                    return rgb, alpha
        if False:
            if fstyle.fill=="radialgradient":
                identifier = "RadialGradient{}".format(self._def_id)
                colors  = svg_code.gradcolor(  0, fstyle.beg_color.rgb, fstyle.beg_color.a)
                colors += svg_code.gradcolor(100, fstyle.end_color.rgb, fstyle.end_color.a)
                self._defs += svg_code.rad_grad(identifier, fstyle.radius, colors)
                return svg_code.fillgrad(identifier)
            elif fstyle.fill=="lineargradient":
                colors = "".join(svg_code.gradcolor(c.percent, c.color.rgb, c.color.a) for c in fstyle.colors)
                if fstyle.orientation=="down-up" or fstyle.orientation=="up-down":  x1, y1, x2, y2 = 50, 100,  50,  0
                else:                                                               x1, y1, x2, y2 =  0,  50, 100, 50
                identifier = "LinearGradient{}".format(self._def_id)
                self._defs += svg_code.lin_grad(identifier, x1, y1, x2, y2, colors)
                return svg_code.fillgrad(identifier)
            else:
                raise NotImplementedError(str(fstyle.fill))    # fstyle.fill should already be a string, but just in case
    def _adjust_boundaries(self, x, y):
        xmin, xmax, ymin, ymax = self._dims
        xmin = min(xmin, x)
        xmax = max(xmax, x)
        ymin = min(ymin, y)
        ymax = max(ymax, y)
        self._dims = xmin, xmax, ymin, ymax
    def _resolve_viewbox(self):
        xmin, xmax, ymin, ymax = self._dims
        Dx = xmax-xmin        #        vv- Hardcoded things should always be adjustable ... maybe in config file
        Dy = ymax-ymin        # clean this up and the line of code below ... takes care of skinny images and adds margin
        Dx = max(Dx, 0.05*Dy) # from https://developer.mozilla.org/en-US/docs/Web/SVG/Attribute/viewBox
        Dy = max(Dy, 0.05*Dx) # The value of the viewBox attribute is a list of four numbers: min-x, min-y, width and height.
        margin = 0.1          #
        return " ".join(str(p) for p in (xmin-margin*Dx, ymin-margin*Dy, Dx*(1+2*margin), Dy*(1+2*margin)))



### renderers specifically for full files or snippets

class renderer_full(renderer_base):
    """ class to resolve and buffer the drawing calls into svg code, dumping them into a complete file """
    def __init__(self, filestem, *, title, controls):
        renderer_base.__init__(self)
        self._filestem   = filestem
        self._title      = title
        self._controls   = controls
        self._background = ""
    def finish(self):
        cite_package = "This file was created using the PyToon package by Anthony D. Dutoi [https://github.com/adutoi/PyToon, tonydutoi@gmail.com].\n"
        javascript, thanks = ("", ""), ""
        image_code = self._main
        if self._duration is not None:
            step, key_controls, button, location = parse_controls(self._controls)
            thanks     = js_code.svg_credit
            javascript = js_code.script_in_svg(animate=struct(delta=step, controls=key_controls))
            if button:
                image_code = svg_code.animation(
                    image    = image_code,
                    controls = svg_code.animation_controls(duration=self._duration, control_location=location)
                )
        with open("{}.svg".format(self._filestem), "w") as stream:
            stream.write(
                svg_code.file_format(
                    background      = self._background,
                    viewbox         = self._resolve_viewbox(),
                    documentation   = svg_code.title_description(title=self._title, description=cite_package+thanks),
                    javascript      = javascript,
                    definitions     = svg_code.defintions(defs=self._defs),
                    image_code      = image_code
                )
            )
    def background(self, background):
        if background.rgb!="none":
            if (background.a is not None) and (background.a!=1):
                raise NotImplementedError("only non-alpha solid backgrounds are currently supported (easy fix?)")
            self._background = background.rgb
    def _assert_no_controls(self):
        if self._controls is not None:  raise RuntimeError("animation controls passed to non-animated image")

class renderer_raw(renderer_base):
    """ class to resolve and buffer the drawing calls into svg code, returning fragments as a string """
    def __init__(self):
        renderer_base.__init__(self)
    def finish(self):
        if self._defs:  raise NotImplementedError("sorry defs (fill gradients, etc) not yet supported for raw svg output (say, for animations)")
        return self._main, self._resolve_viewbox()
    def background(self, background):
        raise RuntimeError("raw svg format does not support a background (returns only code snippets)")
    def _assert_no_controls(self):
        pass

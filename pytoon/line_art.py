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
import operator
import math
from . import util
from . import animation
from . import base

assert_different = lambda a,b:  False



# deal with line and fill styles that may be constant or animated, and might, in either case, be specified in some
# abbreviated way (and where property fields may be unknown to us here)

_parsers = util.style_parsers(grayscale=False)    # Promote abbreviated description to constant style struct

class _static_style(object):
    """ handles cases where style struct is static (but might contain animated properties) """
    def __init__(self, style, parse, anim_wrap):
        self._args = parse(style), anim_wrap     # rely on parse(style) raising an exception if style is not an appropriate struct (or promatable to one)
    def __getattr__(self, attr):
        style, anim_wrap = self._args
        return anim_wrap(getattr(style,attr))    # get the appropriate property field and install clock (in case truly a function of time)

class _dynamic_style(object):
    """ handles cases where style struct is itself animated """
    def __init__(self, style, parse, anim_wrap):
        self._args = anim_wrap(style), parse     # install the clock at the "top" level
    def __getattr__(self, attr):
        style, parse = self._args
        return animation.wrapper(style, postprocess=lambda s: getattr(parse(s),attr))    # postprocess gets appropriate property field after time evaluation

def _linestyle(lstyle, anim_wrap):
    def parse(lstyle):
        try:
            return _parsers.linestyle("black" if (lstyle is None) else lstyle)    # promotes constants (raises exception if lstyle is struct with animated components)
        except:
            return util.linestyle(lstyle)    # in case it has animated components, make sure that it is a linestyle struct at least (or will raise exception)
    try:
        return  _static_style(lstyle, parse, anim_wrap)    # if lstyle can be promoted to linestyle struct (with either static or animated components)
    except:
        return _dynamic_style(lstyle, parse, anim_wrap)    # assume it is a function that generates linestyle structs (or things that can be promoted to linestyle structs)

def _fillstyle(fstyle, anim_wrap):
    def parse(fstyle):
        try:
            return _parsers.fillstyle("none" if (fstyle is None) else fstyle)    # promotes constants (raises exception if fstyle is struct with animated components)
        except:
            return util.fillstyle(fstyle)    # in case it has animated components, make sure that it is a fillstyle struct at least (or will raise exception)
    try:
        return  _static_style(fstyle, parse, anim_wrap)    # if fstyle can be promoted to fillstyle struct (with either static or animated components)
    except:
        return _dynamic_style(fstyle, parse, anim_wrap)    # assume it is a function that generates fillstyle structs (or things that can be promoted to fillstyle structs)



# make sense of a (possibly) incomplete description of endpoints by using defaults judiciously

def _segment(begin, displacement, end, wrap):
    add = lambda p,q:  (p[0]+q[0], p[1]+q[1])
    sub = lambda p,q:  (p[0]-q[0], p[1]-q[1])
    Default_begin        = wrap((0,0))
    Default_displacement = wrap((100,100))
    if begin is None:
        begin = Default_begin
        if displacement is None:
            displacement = Default_displacement
        else:
            displacement = wrap(displacement)
        if end is None:
            end = animation.combine(add, begin, displacement)
        else:
            end = wrap(end)
            begin = animation.combine(sub, end, displacement)
    else:
        begin = wrap(begin)
        if displacement is None:
            displacement = Default_displacement
            if end is None:
                end = animation.combine(add, begin, displacement)
            else:
                end = wrap(end)
        elif end is None:
            end = animation.combine(add, begin, wrap(displacement))
        else:
            raise ValueError("specifying begin, displacement, and end for a line is redundant/conflicting")
    return begin, end



# simultaneously handle transformations and animation (because the transformation might be animated)

def _anim_loop(generate_value, same, ta, tz, N):
    def t_frac(t,ta,tz):
        if t is None:
            return None
        else:
            return max(0, min(1, (t-ta)/(tz-ta) ))
    Dt = (tz-ta)/N if N>0 else None    # None essentially means "infinity" or "not animated"
    homogeneous = True
    value  = None
    values = []
    for i in range(N+1):
        t = (ta + i*Dt) if (Dt is not None) else None    # if Dt is None (ie "infinity") property must be truly time independent, or will fail later
        v = generate_value(t)
        values += [( t_frac(t,ta,tz), v )]
        if (value is not None) and not same(v,value):  homogeneous = False
        value = v
    if homogeneous:  return value
    else:            return values

def _static_point(point, transform, t):
    absolute, relative, linescale = transform.mappings(t)
    return absolute(point(t))

def _static_points(points, transform, t):
    absolute, relative, linescale = transform.mappings(t)
    return [absolute(point) for point in points(t)]

def _animated_point(point, transform, ta, tz):
    N = transform.n_intervals(ta, tz)
    N = point.n_intervals(ta, tz, n_min=N)
    generate_value = lambda t: _static_point(point, transform, t)
    return _anim_loop(generate_value, assert_different, ta, tz, N)

def _animated_points(points, transform, ta, tz):
    N = transform.n_intervals(ta, tz)
    N = points.n_intervals(ta, tz, n_min=N)
    generate_value = lambda t: _static_points(points, transform, t)
    return _anim_loop(generate_value, assert_different, ta, tz, N)

def _static_radius(radius, transform, origin, t):
    x0, y0 = origin(t)
    absolute, relative, linescale = transform.mappings(t, (x0,y0))
    (x0,y0), (x1,y1), (x2,y2) = relative((x0,y0)), relative((x0+1,y0)), relative((x0,y0+1))
    return radius(t) * math.sqrt( ((x1-x0)**2 + (y1-y0)**2 + (x2-x0)**2 + (y2-y0)**2) / 2 )    # always defined, =sqrt(Trace( A.T A )/2) for linear transformations

def _animated_radius(radius, transform, origin, ta, tz):
    N = transform.n_intervals(ta, tz)
    N = origin.n_intervals(ta, tz, n_min=N)
    N = radius.n_intervals(ta, tz, n_min=N)
    generate_value = lambda t: _static_radius(radius, transform, origin, t)
    return _anim_loop(generate_value, util.float_eq, ta, tz, N)

def _static_weight(lstyle, transform, origin, t):
    absolute, relative, linescale = transform.mappings(t, origin(t))
    return lstyle.weight(t) * linescale

def _static_lstyle(lstyle, transform, origin, t):
    color  = lstyle.color(t)
    dash   = lstyle.dash(t)
    weight = _static_weight(lstyle, transform, origin, t)
    return util.linestyle(color=color, weight=weight, dash=dash)

def _animated_lstyle(lstyle, transform, origin, ta, tz):
    N = lstyle.color.n_intervals(ta, tz)    # no n_min because color not (yet) affected by transform
    color = _anim_loop(lstyle.color, operator.eq, ta, tz, N)
    #
    N = lstyle.dash.n_intervals(ta, tz)     # no n_min because dash affected by transform only indirectly via line weight (handled at render level)
    dash = _anim_loop(lstyle.dash, operator.eq, ta, tz, N)
    #
    N = transform.n_intervals(ta, tz)
    N = origin.n_intervals(ta, tz, n_min=N)
    N = lstyle.weight.n_intervals(ta, tz, n_min=N)
    generate_value = lambda t: _static_weight(lstyle, transform, origin, t)
    weight = _anim_loop(generate_value, util.float_eq, ta, tz, N)
    return util.linestyle(color=color, weight=weight, dash=dash)

def _static_fstyle(fstyle, t):
    fill = fstyle.fill(t)
    if fill=="none":
        return util.fillstyle.none()
    elif fill=="solid":
        return util.fillstyle.solid(color=fstyle.color(t))
    else:
        raise NotImplementedError("specified fill type is not presently implemented: {}".format(fill))

def _animated_fstyle(fstyle, ta, tz):
    N = fstyle.fill.n_intervals(ta, tz)    # no n_min because fill type not affected by transform
    fill = _anim_loop(fstyle.fill, operator.eq, ta, tz, N)
    if not isinstance(fill, str):
        raise RuntimeError("fill type cannot change in time (but its parameters can) ... or you could try framewise animation (results in larger file sizes)")
    if fill not in ("none", "solid"):
        raise NotImplementedError("specified fill type is not presently implemented: {}".format(fill))
    if fill=="none":
        return util.fillstyle.none()
    elif fill=="solid":
        N = fstyle.color.n_intervals(ta, tz)    # no n_min because color not (yet) affected by transform
        color = _anim_loop(fstyle.color, operator.eq, ta, tz, N)
        return util.fillstyle.solid(color=color)
    else:
        raise NotImplementedError("specified fill type is not presently implemented: {}".format(fill))

def _static_anim(static, anim, time, **kwargs):
        try:
            ta, tz = time
        except TypeError:
            return static(**kwargs, t=time)
        else:
            return anim(**kwargs, ta=ta, tz=tz)

def _render_point(point, transform, time):
    return _static_anim(_static_point, _animated_point, time, point=point, transform=transform)

def _render_points(points, transform, time):
    return _static_anim(_static_points, _animated_points, time, points=points, transform=transform)

def _render_radius(radius, transform, origin, time):
    return _static_anim(_static_radius, _animated_radius, time, radius=radius, transform=transform, origin=origin)

def _render_lstyle(lstyle, transform, origin, time):
    return _static_anim(_static_lstyle, _animated_lstyle, time, lstyle=lstyle, transform=transform, origin=origin)

def _render_fstyle(fstyle, time):
    return _static_anim(_static_fstyle, _animated_fstyle, time, fstyle=fstyle)



# The classes that describe entities (or entity templates) that can be put into composite objects

# An important bit of theory describes how these objects behave under transformation.  Each has a certain number
# of geometric parameters (begin, end, & center points, line widths, etc).  With such a condensed description
# resolving how a user wants them to appear under arbitrary transformations is not possible, so the following
# approach is used, which is robust for transformations that consist only of translations, rotations and
# isotropic scaling.  The 2D parameters given by the user are mapped via the transform given.  A scalar scale
# factor is requested from the transformation and this is used to scale all line widths and radii.  This also
# gives the user the ability to insert transformations that move points closer together or farther apart but
# still return a scale factor of unity, which would leave line widths unscaled, if that were desired.

class line(base.entity):
    """ describes a pytoon line entity """
    def __init__(self, *, begin=None, displacement=None, end=None, lstyle=None, varval=None, transform=None, clock=None, **kwargs):
        base.entity.__init__(self, kwargs, varval, transform, clock, begin=begin, displacement=displacement, end=end, lstyle=lstyle)
    def _draw(self, time, canvas, aux_dir):
        parameters, transform, clock, anim_wrap = self._resolve_parameters()
        lstyle     = _linestyle(parameters.lstyle, anim_wrap)
        begin, end = _segment(parameters.begin, parameters.displacement, parameters.end, anim_wrap)
        lstyle = _render_lstyle(lstyle, transform, begin, time)
        begin  = _render_point(begin, transform, time)
        end    = _render_point(end, transform, time)
        canvas.line(begin=begin, end=end, lstyle=lstyle)

class circle(base.entity):
    """ describes a pytoon circle entity """
    def __init__(self, *, center=None, radius=None, lstyle=None, fstyle=None, varval=None, transform=None, clock=None, **kwargs):
        base.entity.__init__(self, kwargs, varval, transform, clock, center=center, radius=radius, lstyle=lstyle, fstyle=fstyle)
    def _draw(self, time, canvas, aux_dir):
        parameters, transform, clock, anim_wrap = self._resolve_parameters()
        lstyle = _linestyle(parameters.lstyle, anim_wrap)
        fstyle = _fillstyle(parameters.fstyle, anim_wrap)
        radius = anim_wrap( 100  if (parameters.radius is None) else parameters.radius)
        center = anim_wrap((0,0) if (parameters.center is None) else parameters.center)
        lstyle = _render_lstyle(lstyle, transform, center, time)
        fstyle = _render_fstyle(fstyle, time)
        radius = _render_radius(radius, transform, center, time)
        center = _render_point(center, transform, time)
        canvas.circle(center=center, radius=radius, lstyle=lstyle, fstyle=fstyle)

class polygon(base.entity):
    """ describes a pytoon polygon entity """
    def __init__(self, *, points=None, lstyle=None, fstyle=None, varval=None, transform=None, clock=None, **kwargs):
        base.entity.__init__(self, kwargs, varval, transform, clock, points=points, lstyle=lstyle, fstyle=fstyle)
    def _draw(self, time, canvas, aux_dir):
        parameters, transform, clock, anim_wrap = self._resolve_parameters()
        lstyle = _linestyle(parameters.lstyle, anim_wrap)
        fstyle = _fillstyle(parameters.fstyle, anim_wrap)
        points = anim_wrap([(0,0),(50,100),(100,0)] if (parameters.points is None) else parameters.points)
        lstyle = _render_lstyle(lstyle, transform, animation.wrapper(points, postprocess=lambda pts: pts[0]), time)
        fstyle = _render_fstyle(fstyle, time)
        points = _render_points(points, transform, time)
        canvas.polygon(points=points, lstyle=lstyle, fstyle=fstyle)

class path(base.entity):
    """ describes a pytoon path entity """
    def __init__(self, *, points=None, lstyle=None, fstyle=None, varval=None, transform=None, clock=None, **kwargs):
        base.entity.__init__(self, kwargs, varval, transform, clock, points=points, lstyle=lstyle, fstyle=fstyle)
    def _draw(self, time, canvas, aux_dir):
        parameters, transform, clock, anim_wrap = self._resolve_parameters()
        lstyle = _linestyle(parameters.lstyle, anim_wrap)
        fstyle = _fillstyle(parameters.fstyle, anim_wrap)
        points = anim_wrap([(0,0),(50,100),(100,0)] if (parameters.points is None) else parameters.points)
        lstyle = _render_lstyle(lstyle, transform, animation.wrapper(points, postprocess=lambda pts: pts[0]), time)
        fstyle = _render_fstyle(fstyle, time)
        points = _render_points(points, transform, time)
        canvas.path(points=points, lstyle=lstyle, fstyle=fstyle)


#
# arc, arrow, star, square, rectangle
#

# A comment on arrows, polygons and paths.  An arrow is not a polygon (see Marshall Cline's a circle is not an ellipse).  Here this is because they carry
# different information for the logic that intuitively distorts the arrow within the constraints of staying an arrow.  It should not carry around an internal
# polygon because that is redundant information and would also force us to use deepcopy, and we don't want any implicit involuntary deepcopies done on these
# objects.  However, to enforce that an arrow is a special kind of polygon, it is drawn by parsing the internal information and instantiating a polygon.
# Move arrow to a file with squares and rectangles? ... hmm circles and arcs.

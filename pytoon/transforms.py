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
import math
from . import util

"""
The basic idea is to facilitate nested coordinate transformations that automatically
take care of the lazy variable substitution, and where each transformation can be applied
to either to the entire underlying coordinate space in which an entity lives (somewhat
approximately) or only to the external parameters (eg, not line widths).  How the
transformation is applied depends on how it is called and is that is a property of the 
entity being transformed.

To instantiate a transform, the user provides a callable, along with the arguments (as
keyword arguments) that are to be provided to the callable.  These can be dummy strings 
that will be substituted before the user-provided callable is called to provide the 
transformation functions, which are returned in a 3-tuple of functions.  These functions
exectue the actual coordinate transformations dependent on the values of the aforementioned
parameters.

Some theory is relevant before describing what the three different functions do.  There
are two different kinds of transformations, which we will call uniform and positional.
To the extent that it can be implemented by the one designing an entity, a uniform
transformation is a coordinate mapping that should apply to every aspect, including the 
effects of inhomogeneous distortions of space on line widths, etc (more on the limitations 
of that below).  On the other hand, positional transformations move entities around (and
perhaps closer together or farther apart), but do not change their sizes or associated
line widths.  Similarly, entities can be drawn in one of two ways; they either blindly
apply the given transformation to every aspect of the entity or they attempt to make use
of the latter capability to only apply the transform to the external positioning parameters.
In sum, this means that for an entity to undergo anything other than a uniform transformation,
both the transformation and the entity have to be defined as such.  Strange results might
happen (esp, linewidths) if a positional transformation is applied to an entity that is
not aware of them (why would one do that? ... the opposited has a use case though, which is
accounted for).

It needs to be noted that the extent to which a transformation can be truly uniform is limited 
by the  implementation.  As an extreme example, if everything is defined as a filled path, 
with a zero line width (so even lines are long rectangles), and the path points are very close
together (even along the edged of lines), the the transformation will be very good.  However,
if a circle is implemented using just the low-level circle primitive, it will be a circle in the
final rendering no matter how the coordinate space around it is distorted, and, at best, its 
radius will be scaled to somethging reasonable (assuming relative isotropic transformation in
that region).

In order to fulfill the above capabilities, the three functions returned by the user-provided
callable.  For ease, we will call these functions absolute, relative and linescale, respectively.
  absolute:  This function is the most straightforward possibility.  It simply takes a point
and maps it to a different point, which is returned.
  relative:  This function receives two arguments, a point to be mapped and an origin point
in the same coordinate system.  It will take one of two actions depending on the nature of the
transformation.  If it is a uniform transformation, then it should have exactly the same action 
absolute, thereby ignoring the origin point.  If it is a positional transformation, the origin 
point can be used to compute a displacement.  In only case anticipated, the function would then
map the *origin* and return a point that has the same displacement from the mapped origin.  Other
mappings are also theoretically possible.  These would correspond to internal distortions of the
shape that are independent of the positional transformation (but dependent perhaps on the location 
of the origin?).
  linescale:  This function takes only the origin as an argument and returns a (local) scale
factor to be applied to linewidths, which is consistent with the transformation itself.  If
it is a uniform transformation, then the scale should be consistent with this overall transformation
(which really only works perfectly for isotropic scalings ... see limitations above).  If it is a 
positional transformation, then a scale consistent with the internal transformation of the entity
(generally, = 1)  should be returned.

Finally, for implementors: (1) for entities that are not meant to allow for positional-only
transformations, only the absolute function returned is used on all of the points.  For entities
that

"""



class transform(object):
    def __init__(self, mapping, *, _inner=None, _clock=None, _Dt=None, _allow_resolve=True, **kwargs):
        self._mapping       = mapping
        self._parameters    = kwargs
        self._inner         = _inner
        self._clock         = _clock
        self._Dt            = _Dt
        self._allow_resolve = _allow_resolve
    def animated(self, *, Dt):
        return transform(self._mapping, _inner=self._inner, _clock=self._clock, _Dt=Dt, _allow_resolve=self._allow_resolve, **self._parameters)
    def n_intervals(self, ta, tz):
        N = 0 if (not self._inner) else self._inner.n_intervals(ta, tz)
        if self._Dt is not None:
            N = max(N, 1, util.int_round( (self._clock(tz)-self._clock(ta)) / self._Dt ))    # will fail if clock has not been installed (by .animated)
        return N
    def nest(self, inner):
        if self._inner:
            return transform(self._mapping, _inner=self._inner.nest(inner), _clock=self._clock, _Dt=self._Dt, _allow_resolve=self._allow_resolve, **self._parameters)
        else:
            return transform(self._mapping, _inner=inner,                   _clock=self._clock, _Dt=self._Dt, _allow_resolve=self._allow_resolve, **self._parameters)
    def resolve(self, varval, clock=None, reresolve=False):
        inner = None
        if self._inner:
            inner = self._inner.resolve(varval, clock, reresolve)
        if self._allow_resolve:
            params, Dt = varval((self._parameters, self._Dt))
        else:
            clock      = self._clock      # ignore function argument
            params, Dt = self._parameters, self._Dt
            reresolve  = False
        return transform(self._mapping, _inner=inner, _clock=clock, _Dt=Dt, _allow_resolve=reresolve, **params)
    def mappings(self, _t_=None, origin=(0,0)):
        varval = util.variable_evaluator({"_t_": self._clock(_t_)})
        outer_absolute, outer_relative, outer_linescale = self._mapping(**varval(self._parameters))
        if self._inner:
            inner_absolute, inner_relative, inner_linescale = self._inner.mappings(_t_, origin)
            origin = inner_absolute(origin)
        def absolute(point):
            if self._inner:  point = inner_absolute(point)
            return outer_absolute(point)
        def relative(point):
            if self._inner:  point = inner_relative(point)
            return outer_relative(point, origin)
        linescale = outer_linescale(origin)
        if self._inner:  linescale *= inner_linescale
        return absolute, relative, linescale



def uniform_transform(kernel_scale, **symbolic_kwargs):
    def mapping(**concrete_kwargs):
        kernel, scale = kernel_scale(**concrete_kwargs)
        def absolute(point):
            return kernel(point)
        def relative(point, origin):
            return kernel(point)
        def linescale(origin):
            return scale
        return absolute, relative, linescale
    return transform(mapping, **symbolic_kwargs)

def positional_transform(kernel_scale, **symbolic_kwargs):
    def mapping(**concrete_kwargs):
        kernel, scale = kernel_scale(**concrete_kwargs)
        def absolute(point):
            return kernel(point)
        def relative(point, origin):
            (xP,yP), (xO,yO) = point, origin
            (Dx, Dy) = (xP-xO, yP-yO)
            (xO, yO) = kernel(origin)
            return (xO+Dx, yO+Dy)
        def linescale(origin):
            return scale
        return absolute, relative, linescale
    return transform(mapping, **symbolic_kwargs)



def _no_transform():
    def kernel(point):
        return point
    scale = 1
    return kernel, scale

def _translate(displacement):
    Dx, Dy = displacement
    def kernel(point):
        x, y = point
        return (x+Dx, y+Dy)
    scale = 1
    return kernel, scale

def _rotate(angle):
    c = math.cos(angle)
    s = math.sin(angle)
    def kernel(point):
        x, y = point
        return (c*x - s*y, c*y + s*x)
    scale = 1
    return kernel, scale

def _scale(factor, scale_linewidths=True):
    def kernel(point):
        x, y = point
        return (factor*x, factor*y)
    if scale_linewidths:
        scale = factor
    else:
        scale = 1
    return kernel, scale

no_transform = uniform_transform(_no_transform)

def translate(Dx, Dy):
    return uniform_transform(_translate, displacement=(Dx,Dy))

def rotate(angle=None, *, rad=None):
    if angle is rad is None:
        raise ValueError("a value for the rotation angle must be provided")
    elif (angle is not None) and (rad is not None):
        raise ValueError("rotation angle was specified twice")
    elif rad is None:
        rad = angle * math.pi/180
    return uniform_transform(_rotate, angle=rad)

def scale(factor):
    return uniform_transform(_scale, factor=factor)

def zoom(factor):
    return uniform_transform(_scale, factor=factor, scale_linewidths=False)

def stretch(factor):
    return positional_transform(_scale, factor=factor, scale_linewidths=False)





def _parametric(fx, fy):
    if not fx:  fx = lambda u: u
    if not fy:  fy = lambda u: u
    def kernel(point):
        x, y = point
        return (fx(x), fy(y))
    scale = 1
    return kernel, scale

def parametric(*, fx=None, fy=None):
    return positional_transform(_parametric, fx=fx, fy=fy)

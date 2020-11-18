#  (C) Copyright 2012, 2013, 2014, 2015, 2020 Anthony D. Dutoi
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
#
#
#   This is thought of as the "concrete" layer, where the image format is specified first, and then
# the drawing commands are issued sequentially to create that image (though, for technical reasons,
# these might be buffered until a finish command is issued).
#   A higher "abstract" layer will allow for the creation of images first, without specifying their
# format until render time.  In that layer, objects may be created in non-sequential, nested ways.
# Although it is good for the developer to be aware of the upper layer, this layer knows nothing of it.
#
import os
from . import util
from . import renderers



#   These are the functions that are called by the user as draw.svg(), draw.jpg(), draw.py(), etc,
# in order to generate the "canvas" upon which uniform drawing commands are issued.  If assigned
# as canvas=draw.xxx(), these commands look like canvas.line(), canvas.circle(), etc., ending
# in canvas.finish() to finalize the image to disk in the specified format.  The writing to disk might be
# be delayed because the file format may require header definitions for some elements used later.
#   These allow for grayscale option to be given at a low level (globally) to mimic printer that
# physically cannot do color, in spite of whatever way a user might try to get around it.  Of course,
# partially grayscaled images can be created at a higher level using the grayscaling primitives.
#   Here is the philosophy regarding which arguments are passed directly to the __init__ of the renderer:
# If the argument affects the *definition* of the image (duration, background, etc), then it should
# not be passed to the renderer __init__, but it should be taken care of by a method called by the
# _canvas __init__.  If it affects the presentation or metadata (title, animation controls, dpi),
# then it is passed directly to the renderer __init__ to avoid bogging down the _canvas init with
# options that are not relevant to every format.  The reason for not passing all of them directly to
# the renderer __init__ is that some, like the background color might need to be pre-parsed (eg, grayscaled).

def py(filestem, *, background=None, duration=None, grayscale=False):
    """ returns an object that essentially echos the input ... useful for debugging higher code levels """
    return _canvas(renderers.py(filestem), grayscale=grayscale, duration=duration, background=background)    # <-- probably broken (not updated to match calling code)

def jpg(filestem, *, dpi=150, background=None, grayscale=False):
    """ returns an object that translates the uniform drawing interface to jpg format """
    return _canvas(renderers.jpg(filestem, dpi=dpi), grayscale=grayscale, background=background)

def pdf(filestem, *, background=None, grayscale=False):
    """ returns an object that translates the uniform drawing interface to pdf format """
    return _canvas(renderers.pdf(filestem), grayscale=grayscale, background=background)

def svg(filestem, *, title=None, background=None, controls=None, duration=None, grayscale=False):
    """ returns an object that translates the uniform drawing interface to svg code """
    return _canvas(renderers.svg(filestem, title=title, controls=controls), grayscale=grayscale, duration=duration, background=background)

def svg_raw(*, duration=None, grayscale=False):
    """ returns an object that translates the uniform drawing interface to snippets of svg code stored in a string """
    return _canvas(renderers.svg_raw(), grayscale=grayscale, duration=duration)



# This is the class instantiated by the above functions

class _canvas(object):
    """ this class checks user input and manages file creation, given an engine that creates the actual format-specific image-code """
    def __init__(self, renderer, grayscale, *, duration=None, background=None):
        self._renderer    = renderer
        self._parsers     = util.style_parsers(grayscale=grayscale)
        self._animated    = (duration is not None)
        if duration:    self._renderer.duration(duration)
        if background:  self._renderer.background(self._parsers.color(background))
    def line(self, begin, end, lstyle=tuple(), toggle=None):
        begin  = self._valid_point(begin)
        end    = self._valid_point(end)
        lstyle = self._valid_lstyle(lstyle)
        self._renderer.line(lstyle, begin, end, toggle)
    def path(self, points, lstyle=tuple(), fstyle=None, toggle=None):
        points = self._valid_points(points)
        lstyle = self._valid_lstyle(lstyle)
        fstyle = self._valid_fstyle(fstyle)
        self._renderer.path(lstyle, fstyle, points, toggle)
    def polygon(self, points, lstyle=tuple(), fstyle=None, toggle=None):
        points = self._valid_points(points)
        lstyle = self._valid_lstyle(lstyle)
        fstyle = self._valid_fstyle(fstyle)
        self._renderer.polygon(lstyle, fstyle, points, toggle)
    def arc(self, begin, end, radius, skew=0, lstyle=tuple(), fstyle=None, toggle=None):
        rx, ry = radius
        end_arc = *end, util.struct(curve="arc", rx=rx, ry=ry, skew=skew)
        begin   = self._valid_point(begin)
        end_arc = self._valid_point(end_arc)
        x, y, p = end_arc
        end, radius, skew = ((x, y), (p.rx, p.ry), p.skew)
        lstyle = self._valid_lstyle(lstyle)
        fstyle = self._valid_fstyle(fstyle)
        self._renderer.arc(lstyle, fstyle, begin, end, radius, skew, toggle)
    def circle(self, center, radius, lstyle=tuple(), fstyle=None, toggle=None):
        center = self._valid_point(center)
        radius = self._valid_number(radius, "circle radius", (lambda x: x>0, "positive"))
        lstyle = self._valid_lstyle(lstyle)
        fstyle = self._valid_fstyle(fstyle)
        self._renderer.circle(lstyle, fstyle, center, radius, toggle)
    def image(self, imgfile, size, position, rotate=0, toggle=None):
        if not os.path.isfile(filname):
            raise FileNotFoundError(imgfile)    # No guarantee it is an image file, but oh well
        size     = self._valid_point(size)
        position = self._valid_point(position)
        rotate = util.valid_real_number((rotate, "image rotation"), (lambda x: True, "anything"))
        self._renderer.image(imgfile, size, position, rotate, toggle)
    def finish(self):
        return self._renderer.finish()    # return value is specific to renderer (often None)
    def _valid_lstyle(self, lstyle):
        lstyle = self._parsers.linestyle(lstyle)
        if self._animated:
            lstyle = lstyle.animated()
        elif lstyle.has_animated():
            raise RuntimeError("animated property given to resolve single time point")
        return lstyle        
    def _valid_fstyle(self, fstyle):
        fstyle = self._parsers.fillstyle(fstyle)
        if self._animated:
            fstyle = fstyle.animated()
        elif fstyle.has_animated():
            raise RuntimeError("animated property given to resolve single time point")
        return fstyle
    def _valid_number(self, number, name, conditional):
        if self._animated:
            if util.is_animated(number):
                return [(t, util.valid_real_number((n,name),conditional)) for t,n in number]
            else:
                return util.animated(util.valid_real_number((number,name),conditional))
        else:
            if util.is_animated(number):
                raise RuntimeError("animated numerical property given to resolve single time point")
            else:
                return util.valid_real_number((number,name),conditional)
    def _valid_point(self, point):
        if self._animated:
            if util.is_animated(point):
                return [(t, util.valid_point(p)) for t,p in point]
            else:
                return util.animated(util.valid_point(point))
        else:
            if util.is_animated(point):
                raise RuntimeError("animated point given to resolve single time point")
            else:
                return util.valid_point(point)
    def _valid_points(self, points):
        if self._animated:
            try:
                return [(t, [util.valid_point(p) for p in pts]) for t,pts in points]
            except TypeError:
                return util.animated([util.valid_point(p) for p in points])
        else:
            try:
                return [util.valid_point(p) for p in points]
            except TypeError:
                raise RuntimeError("perhaps animated path given to resolve single time point")

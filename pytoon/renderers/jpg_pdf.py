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
from .. import util
from .. import local  # should this move into util?
from .  import svg



# Right now, I do not have independent renderers for pdf and jpg (or anything other than py and svg).
#
# On the one hand, having them all ultimately call the svg driver is a good way to make sure we always
# get the same output.  But, on the other hand, we have to assume that inkscape and ImageMagick are
# reliable as called here, and always installed.  Furthermore it might corrupt my mind if I keep thinking
# about how to acheive a desired effect in an svg output, and I want this to be more abstract, as a matter
# of principle.
#
# For now, this jpg->pdf->svg chaining together works.  It may seem odd that raster graphics are generated
# by converting a pdf, converted from svg, but I have had trouble with using inkscape to directly convert 
# from svg to jpg, for example.  I have, in the past, had luck with
#  inkscape -a=0:0:620:320 -b="white" -f $j.svg -e $j.png
#  convert $j.png $j.jpg
# because inkscape output to png seems more reliable.  However, I seem to have to put in the area of the image.
#
# Another thing not to like at the moment is that this conversion chain eats up intermediate file names
# for the non-target formats, which is probably usually ok, but generally a bad idea.  Below, is some code
# that I started using temporary files, but it kind of broke down when I needed to do the conversions
# in two steps, since the middle file would not be generated by python, and the function for python
# to give you just a temporary name has been deprecated due to race conditions.  A work-around would be
# a temporary directory, but then I lost steam.  We might also just generate a local random directory
# name using try/except if it exists.  Or we might need the user to eventually provide a scratch dir
# anyway for things like text?
#
# In any case, at the point where I clean up the above, I would also like to get rid of my reliance on
# util.shell.bash (if I can't get rid of the pseudo-render concept altogether), but how to do that when
# I rely on calling inkscape and convert.
#
# Finally, it would be at this level and below that I need to do things to make it all windows
# compatible (both in paths and in calling external utilities).  I don't think I need to fix anything
# in the svg renderer though, since svg readers should be robust wrt to \n vs \r\c.
#
# Here's the code mentioned above, which roughly replaces the contents of pdf() above:
# import tempfile
#  stream = tempfile.NamedTemporaryFile("w", suffix=".svg", delete=False)
#  script = util.shell.bash()
#  script("here=`pwd`")
#  script("{inkscape} -D -z --file={tmp} --export-pdf=$here/{filestem}.pdf".format(inkscape=local.inkscape, tmp=stream.name, filestem=filestem))
#  script("rm {tmp}".format(tmp=stream.name))

class _pseudo_renderer(object):
    """ class to resolve and buffer the drawing calls into svg code and then convert to target format """
    def __init__(self, svg_renderer, conversion_script):
        self._svg_renderer      = svg_renderer
        self._conversion_script = conversion_script
    def finish(self):
        self._svg_renderer.finish()
        self._conversion_script.run()
    def background(self, background):
        self._svg_renderer.background(background)
    def duration(self, duration):
        raise RuntimeError("target file format does not support animation")
    def path(self, lstyle, fstyle, points, toggle):
        self._svg_renderer.path(lstyle, fstyle, points, toggle)
    def image(self, filename, size, position, rotate, toggle):
        self._svg_renderer.image(filename, size, position, rotate, toggle)
    def line(self, lstyle, begin, end, toggle):
        self._svg_renderer.line(lstyle, begin, end, toggle)
    def polygon(self, lstyle, fstyle, points, toggle):
        self._svg_renderer.polygon(lstyle, fstyle, points, toggle)
    def arc(self, lstyle, fstyle, begin, end, radius, skew, toggle):
        self._svg_renderer.arc(lstyle, fstyle, begin, end, radius, skew, toggle)
    def circle(self, lstyle, fstyle, center, radius, toggle):
        self._svg_renderer.circle(lstyle, fstyle, center, radius, toggle)

def pdf(filestem):
    """ returns a pseudo-renderer class to resolve and buffer the drawing calls into pdf format (via svg using Inkscape) """
    script = util.shell.bash()
    script("here=`pwd`")
    script("{inkscape} -D -z --file=$here/{filestem}.svg --export-pdf=$here/{filestem}.pdf".format(inkscape=local.inkscape, filestem=filestem))
    script("rm $here/{filestem}.svg".format(filestem=filestem))
    return _pseudo_renderer(svg.renderer_full(filestem, title="", controls=None), script)

def jpg(filestem, *, dpi):
    """ returns a pseudo-renderer class to resolve and buffer the drawing calls into jpg format (via svg and pdf using Inkscape and ImageMagick) """
    script = util.shell.bash()
    script("here=`pwd`")
    script("{inkscape} -D -z --file=$here/{filestem}.svg --export-pdf=$here/{filestem}.pdf".format(inkscape=local.inkscape, filestem=filestem))
    script("rm {filestem}.svg".format(filestem=filestem))
    script("{convert} -density {dpi} {filestem}.pdf {filestem}.jpg".format(convert=local.convert, filestem=filestem, dpi=dpi))
    script("rm {filestem}.pdf".format(filestem=filestem))
    return _pseudo_renderer(svg.renderer_full(filestem, title="", controls=None), script)
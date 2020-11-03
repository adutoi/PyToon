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
import os
from . import util
from . import draw
from . import transforms
from . import animation
from .renderers import parse_svg_animation_controls    # this likely does not belong here.  see note above where it is used



# This is a base class for all pytoon objects that implements the things that they have in common.
#   1. All objects are callable, which produces a new object of the same type, where the arguments
#      to __call__ are interpreted the same as to __init__, except that the defaults of the unspecified
#      arguments are set to the values of the parameters for the called object, instead of their static
#      defaults (except transform and clock which are nested).
#   2. The object can be rendered into an image file, which can be one of a number of dynamically
#      specified format.  The object is not modified by such action, and so continues to be available
#      for further changes or renderings.

class entity(object):
    """ provides the copy-call method, resolves transformations and variable substitutions, and manages interaction with the concrete drawing layer """
    def __init__(self, substitutions, varval, transform, clock, **kwargs):
        self._parameters = kwargs                                                           # parameters that are specific to the derived entity
        self._clock      = util.echo if (clock is None) else clock                          # maps global time to local time
        self._transform  = transforms.no_transform if (transform is None) else transform    # maps internal coordinates to absolute page coordinates (can be nested)
        if (len(substitutions)==0) and (varval is None):                                    # returns substitutions of variables (can be nested)
            self._varval = util.echo
        elif len(substitutions)==0:
            self._varval = varval
        elif varval is None:
            self._varval = util.variable_evaluator(substitutions)
        else:
            self._varval = util.variable_evaluator(substitutions, inner=varval)
    def __call__(self, **kwargs):
        special = ("varval", "transform", "clock")
        new_parameters = dict(self._parameters)    # shallow copy of dict (stores references to original parameter objects)
        substitutions = {}                              #
        for k,v in kwargs.items():                      # Look through all arguments to the call and identify the ones that are entity-specific parameters
            if k in new_parameters:                     # by seeing if there is already such a key in the parameter dict.  If so, use the new value in place
                new_parameters[k] = v                   # of the old one.  If not, it is interpreted as a key-value pair to be used in resolving symbolic
            elif k not in special:                      # variables.  Specification of varval and transform augments the old values, per the code below.
                substitutions[k] = v                    #
        varval = self._varval                                                #
        if "varval" in kwargs and kwargs["varval"] is not None:              # The varval function from the parent object is applied first.  If any substitutions are
            varval = util.nested(outer=kwargs["varval"], inner=varval)       # left unresolved (or mapped to a different, unresolved symbolic value) these are then handled
        if len(substitutions)!=0:                                            # by any varval function passed in here, and finally by one built from "extra" kwargs in call.
            varval = util.variable_evaluator(substitutions, inner=varval)    #
        transform = self._transform                                      # 
        if "transform" in kwargs and kwargs["transform"] is not None:    # This nests the old transform inside the new transform (if extant)
            transform = kwargs["transform"].nest(transform)              #
        clock = self._clock
        if "clock" in kwargs and kwargs["clock"] is not None:
            clock = util.nested(outer=clock, inner=kwargs["clock"])
        return type(self)(**new_parameters, varval=varval, transform=transform, clock=clock)    # return an object of the derived type initialized with modified parameters
    def _resolve_parameters(self):
        # called by _draw of child class to provide fully resolved parameters and transform (and "protected" from further attempts at resolution)
        parameters = util.struct( **self._varval(self._parameters) )
        clock = self._varval(self._clock)    # clock could have ._value_ defined but does not yet work as intended because clock usually nested
        transform = self._transform.resolve(self._varval, clock)
        anim_wrap = lambda obj: animation.wrapper(obj, clock=clock)
        return parameters, transform, clock, anim_wrap
    def S(self, factor):
        return self(transform=transforms.scale(factor))
    def R(self, angle):
        return self(transform=transforms.rotate(angle))
    def T(self, Dx, Dy):
        return self(transform=transforms.translate(Dx,Dy))
    def _draw_it(self, duration, time, canvas, aux_dir):
        try:
            _, _ = time
        except TypeError:
            if     duration:  raise RuntimeError("animation duration specified but time is not an interval")
        else:
            if not duration:  raise RuntimeError("time interval given without specifying duration ... perhaps target format does not support animation")
        os.system("mkdir -p {}".format(aux_dir))
        self._draw(time, canvas, aux_dir)
        return canvas.finish()    # usually returns None
    def py(self, filestem="pytoon_graphic", *, time=None, duration=None, background=None, grayscale=False, aux_dir=None):
        return self._draw_it(
            duration   = duration,
            time       = time,
            canvas     = draw.py(filestem, duration=duration, background=background, grayscale=grayscale),
            aux_dir    = "{}_aux".format(filestem) if (aux_dir is None) else aux_dir
        )
    def jpg(self, filestem="pytoon_graphic", *, time=None, dpi=150, background=None, grayscale=False, aux_dir=None):
        return self._draw_it(
            duration   = None,
            time       = time,
            canvas     = draw.jpg(filestem, dpi=dpi, background=background, grayscale=grayscale),
            aux_dir    = "{}_aux".format(filestem) if (aux_dir is None) else aux_dir
        )
    def pdf(self, filestem="pytoon_graphic", *, time=None, background=None, grayscale=False, aux_dir=None):
        return self._draw_it(
            duration   = None,
            time       = time,
            canvas     = draw.pdf(filestem, background=background, grayscale=grayscale),
            aux_dir    = "{}_aux".format(filestem) if (aux_dir is None) else aux_dir
        )
    def svg_raw(self, *, time=None, duration=None, grayscale=False, aux_dir="pytoon_graphic_aux"):
        return self._draw_it(    # returns image code as string and viewbox, respectively
            duration   = duration,
            time       = time,
            canvas     = draw.svg_raw(duration=duration, grayscale=grayscale),
            aux_dir    = aux_dir
        )
    def svg(self, filestem="pytoon_graphic", *, title=None, time=None, duration=None, global_frames=None, controls=None, background=None, grayscale=False, aux_dir=None):
        # The code inside the 'else' is still pretty dirty, might be misplaced, and might be deprecated altogether.
        # See the comments at the end of this file.
        if global_frames is None:
            return self._draw_it(
                duration   = duration,
                time       = time,
                canvas     = draw.svg(filestem, title=title, duration=duration, controls=controls, background=background, grayscale=grayscale),
                aux_dir    = "{}_aux".format(filestem) if (aux_dir is None) else aux_dir
            )
        else:
            if not duration:
                raise RuntimeError("global-frame animation requested for non-animated image")
            aux_dir = "{}_aux".format(filestem) if (aux_dir is None) else aux_dir
            global_frames += 1    # because the last frame does not get rendered to give smooth looping behavior (make this adjustable?)
            ta, tz = time
            Dt = (tz-ta) / global_frames
            frames_code = ""
            for i in range(global_frames):
                t = ta + i*Dt
                image, viewbox = self.svg_raw(time=t, grayscale=grayscale, aux_dir=aux_dir)
                frames_code += util.svg_code.frame(image_code=image, duration=duration, index=i, count=global_frames)
                if i!=0:
                    if viewbox!=previous_viewbox:  raise RuntimeError("for now, all the frame viewboxes need to be the same (easy to fix!!)")
                previous_viewbox = viewbox
            background = "" if (background is None) else background    # bug here.  this is not parsed
            description = "This file was created using the PyToon package by Anthony D. Dutoi [https://github.com/adutoi/PyToon, tonydutoi@gmail.com].\n" + util.js_code.svg_credit
            step, key_controls, button, location = parse_svg_animation_controls(controls)
            step = 1.001*duration/global_frames
            if button:
                frames_code = util.svg_code.animation(
                    image    = frames_code,
                    controls = util.svg_code.animation_controls(duration=duration, control_location=location)
                )
            open(filestem+".svg", "w").write(
                util.svg_code.file_format(
                    background      = background,
                    viewbox         = viewbox,
                    documentation   = util.svg_code.title_description(title=title, description=description),
                    javascript      = util.js_code.script_in_svg(animate=util.struct(delta=step, controls=key_controls)),
                    definitions     = util.svg_code.defintions(""),    # for now there is a bug here; fill effects not supported.  composite.svg_raw() will raise exception
                    image_code      = frames_code
                )
            )    # file object immediately falls out of scope





# The main issue to resolve is how to handle things like .mpg, .avi, and .mp4 extensions.  We know that at the implementation
# level, they will involve rendering a series of full frames that get strung together.  From a user point of view, it would
# be nice to have these on par with image.jpg(), .pdf() and .svg(), etc.  At an implementation level these should live above
# draw (where a canvas might support an animated object but has no sense of being multiple on its own.  So the question is
# where to put the code.  It would seem reasonable to implement a frame-by-frame .svg version first, and build off of that
# as we have done with the .pdf and .jpg "renderers".  Should I not even try to use .svg_raw and then just parse the .svg
# files on disk, as I would for the others?
#
#   Below, we have remnants of code from a different overall structure that would make avi or mp4 videos.
#   The important thing to realize is that the line:
#     framesPy,background,foreground = make_frames(filestem,func,count,None,ext=('jpg',dpi),texlabels=texlabels)
#   creates a number of jpg files on disk, where framesPy describes the filename template in a str.format-like way.
#   Really, we just want to mine what is below for the ffmpeg call strings
#
## For now, only mjpeg from jpgs.
## How to handle background?
##
#def avi(filestem,func,count,duration,texlabels=None,dpi=None):
#       framesPy,background,foreground = make_frames(filestem,func,count,None,ext=('jpg',dpi),texlabels=texlabels)
#       framesC = ''
#       for c in framesPy:
#               if   c=='{' or c=='}': pass
#               elif c==':':  framesC = framesC + '%'
#               else:         framesC = framesC +  c
#       framerate = int(float(count)/float(duration))
#       script = shell.csh()
#       script(local.ffmpeg + ' -sameq -r {framerate} -i {frames}.jpg -vcodec mjpeg {filestem}.avi'.format(frames=framesC,filestem=filestem,framerate=framerate))
#       script.run()
#       rmtree(filestem)
#
##def mp4(filestem,func,count,duration):
##      avi('temp',func,count,duration)
##      script = shell.csh()
##      script('ffmpeg -i temp.avi -vcodec mpeg4 -b:v 1200k -flags +aic+mv4 temp.mp4')
##      script('ffmpeg -i temp.mp4 -acodec mp2 {filestem}.mp4'.format(filestem=filestem))
##      script('rm temp.avi temp.mp4')
##      script.run()
#
#def mp4(filestem,func,count,duration,texlabels=None,dpi=None):
#       framesPy,background,foreground = make_frames(filestem,func,count,None,ext=('jpg',dpi),texlabels=texlabels)
#       framesC = ''
#       for c in framesPy:
#               if   c=='{' or c=='}': pass
#               elif c==':':  framesC = framesC + '%'
#               else:         framesC = framesC +  c
#       framerate = int(float(count)/float(duration))
#       script = shell.csh()
#       script(local.ffmpeg + ' -r {framerate} -i {frames}.jpg -vcodec mpeg4 {filestem}.mp4'.format(frames=framesC,filestem=filestem,framerate=framerate))
#       script.run()
#       rmtree(filestem)






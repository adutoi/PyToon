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
from ..util      import colordef
from ..composite import composite
from ..line_art  import polygon
from ..animation import animated


# derivations of some formulas found in ./notes/raster.pdf

def rasterize(rgba_Dt, xdim=(-1,1,20), ydim=(-1,1,20), pixel_aspect_ratio=1, width=100):
    # rgba_Dt should be a function of x and y that returns a 2-tuple of rgbs and Dt, where
    # where Dt is the time resolution to use at that point in space and
    # rgba is a function of time (and it can ignore the time argument), returning a 2-tuple
    # which is the rgb code (in #RRGGBB form) and alpha value at that x,y point (at that time);
    # the code can recover if the alpha value is omitted (a value instead of a tuple is returned)
    # by omitting the alpha channel (no transparency).
    #
    Py = pixel_aspect_ratio
    Px = 1 / Py            # hard-coded:  pixel area is 1
    px = (1.001) * Px/2    # fudge factor to overlap edges just slightly ...
    py = (1.001) * Py/2    # ... looks a lot better than leaving even a tiny gap (due to roundings?)
    pixel = polygon(points=[(-px,-py),(px,-py),(px,py),(-px,py)], lstyle=False)
    #
    def color(x, y, layer):
        rgba, Dt = rgba_Dt(x,y)
        if layer=="upper":
            alpha = lambda a: a/2
        else:
            alpha = lambda a: a/(2-a)
        def value(_t_):
            rgb_a = rgba(_t_)
            try:
                rgb, a = rgb_a
            except TypeError:
                rgb, a = rgb_a, 1
            a = 1 if (a is None) else a
            return colordef(rgb=rgb, a=alpha(a))
        return animated(value, Dt=Dt)
    #
    xmin, xmax, Nx = xdim
    ymin, ymax, Ny = ydim
    Dx = (xmax-xmin) / Nx
    Dy = (ymax-ymin) / Ny
    lower = []
    for i in range(Nx+1):
        x = xmin + i*Dx
        for j in range(Ny+1):
            y = ymin + j*Dy
            lower += [ pixel(fstyle=color(x,y,"upper")).T(i*Px, j*Py) ]
    upper = []
    for i in range(Nx):
        x = xmin + (i+1/2)*Dx 
        for j in range(Ny):
            y = ymin + (j+1/2)*Dy
            upper += [pixel(fstyle=color(x,y,"upper")).T((i+1/2)*Px, (j+1/2)*Py)]
    #
    return composite([*lower, *upper]).S(width/(Px*Nx))

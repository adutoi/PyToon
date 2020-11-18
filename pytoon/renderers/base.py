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
from .. import util



#   This optional base class is meant to speed time to implementation of new renderers and cut down on
# maintenance and synchronization issues for similar entities, by eliminating potentially redundant code.
# It provides methods implementing line, polygon, arc, and circle in terms of path, so that the implementor
# has only to implement the path, image, and write methods to fulfill the renderer API, wrapping the private
# methods here in their respective public APIs, with the same signature.
#   It might seem as though paths should be implemented in terms of lines and arcs (or general curved segments).
# Whereas that is a correct decomposition, it is not a correct hierarchy; lines and arcs (for example) are
# simple examples of one-segment paths, not the other way around.  That said, there is a small bait-and-switch
# with respect to the promised convenience of only having to implement path to get the other four methods
# "for free".  By the time the implementor figures out how to implement general paths with arc segments,
# not much intellectual work is spared, but it does save writing redundant code, which is error prone and
# requires an initial time investment and maintenance.
#   Finally, realizing that all line-art can be done in terms of paths alone might make one wonder whether we 
# should not just require the user to work in terms of paths only, or conversely, whether we should implement
# more higher-order primitives (maybe rectangle) here, for "export" to the child classes.  It is a blurry line
# and a matter of opinion, but the goal of any programming project is to be useful, but not so cluttered and
# redundant as to be confusing.  Usefulness would seem to dictate that at least line, arc, circle and polygon
# are supported by default.  The plan is to let future usage dictate what other objects should be added to the
# API (they should be both frequently used and have descriptions that are significantly more compact than what
# is available using the present options).

class renderer(object):
    """ optional base class for image-format-specific renderers, providing some entity implementations in terms others, for convenience """
    def _line_as_path(self, lstyle, begin, end, toggle):
        fill = util.fillstyle.none()
        if self._duration is None:
            points = [begin,end]
        else:
            try:
                begin  = util.deanimated(begin)
                end    = util.deanimated(end)
                points = util.animated([begin,end])
            except ValueError:
                b_times, b = zip(*begin)
                e_times, e = zip(*end)
                try:
                    begin = util.deanimated(begin)
                except ValueError:
                    begin = b
                else:
                    b_times, begin = e_times, [begin]*len(e_times)
                try:
                    end = util.deanimated(end)
                except ValueError:
                    end = e
                else:
                    e_times, end = b_times, [end]*len(b_times)
                if len(begin)==len(end) and all(util.float_eq(b,e) for b,e in zip(b_times,e_times)):
                    times = b_times
                    points = [(t,[b,e]) for t,b,e in zip(times,begin,end)]
                else:
                    # To get rid of this, the implementor needs to not use a path to implement a line (or we could build interpolations here?)
                    raise NotImplementedError("animated line_as_path implementation only works for equivalent frame times for endpoints")
        self.path(lstyle, fill, points, toggle)
    def _polygon_as_path(self, lstyle, fstyle, points, toggle):
        if self._duration is None:
            points = points + [points[0]]    # do not modify original
        else:
            points = [(t, pts+[pts[0]]) for t,pts in points]
        self.path(lstyle, fstyle, points, toggle)
    def _arc_as_path(self, lstyle, fstyle, begin, end, radius, skew, toggle):
        rx, ry = radius
        end = *end, util.struct(curve="arc", rx=rx, ry=ry, skew=skew)    # the way we implement arcs in paths is still a bit of a hack (appending to points)
        self.path(lstyle, fstyle, [begin,end], toggle)
    def _circle_as_path(self, lstyle, fstyle, center, radius, toggle):
        if self._duration is None:
            x, y = center
            a1 = x+radius, y
            b  = x-radius, y, util.struct(curve="arc", rx=radius, ry=radius, skew=0)
            a2 = x+radius, y, util.struct(curve="arc", rx=radius, ry=radius, skew=0)
            points = [a1,b,a2]
        else:
            try:
                center = util.deanimated(center)
                radius = util.deanimated(radius)
                x, y = center
                a1 = x+radius, y
                b  = x-radius, y, util.struct(curve="arc", rx=radius, ry=radius, skew=0)
                a2 = x+radius, y, util.struct(curve="arc", rx=radius, ry=radius, skew=0)
                points = util.animated([a1,b,a2])
            except ValueError:
                c_times, c = zip(*center)
                r_times, r = zip(*radius)
                try:
                    center = util.deanimated(center)
                except ValueError:
                    center = c
                else:
                    c_times, center = r_times, [center]*len(r_times)
                try:
                    radius = util.deanimated(radius)
                except ValueError:
                    radius = r
                else:
                    r_times, radius = c_times, [radius]*len(c_times)
                if len(center)==len(radius) and all(util.float_eq(c,r) for c,r in zip(c_times,r_times)):
                    times = c_times
                    points = []
                    for t,c,r in zip(times,center,radius):
                        x,y = c
                        a1 = x+r, y
                        b  = x-r, y, util.struct(curve="arc", rx=r, ry=r, skew=0)
                        a2 = x+r, y, util.struct(curve="arc", rx=r, ry=r, skew=0)
                        points += [(t,[a1,b,a2])]
                else:
                    # To get rid of this, the implementor needs to not use a path to implement a circle (or we could build interpolations here?)
                    raise NotImplementedError("animated circle_as_path implementation only works for equivalent frame times for center and radius")
        self.path(lstyle, fstyle, points, toggle)

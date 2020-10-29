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
from . import base



class composite(base.entity):
    def __init__(self, entities=[], *, varval=None, transform=None, clock=None, **kwargs):    # mutable type in signature ok b/c never modified in place
        base.entity.__init__(self, kwargs, varval, transform, clock, entities=list(entities))
    def _draw(self, time, canvas, aux_dir):
        parameters, transform, clock, _ = self._resolve_parameters()
        for entity in parameters.entities:
            entity(varval=self._varval, transform=transform, clock=clock)._draw(time, canvas, aux_dir)

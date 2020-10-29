#    (C) Copyright 2017, 2018, 2020 Anthony D. Dutoi
# 
#    This file is part of TonyUtil.
# 
#    TonyUtil is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
# 
#    TonyUtil is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
# 
#    You should have received a copy of the GNU General Public License
#    along with TonyUtil.  If not, see <http://www.gnu.org/licenses/>.
#

def evaluate(node, label=None, context=None):
    try:
        return node._evaluate(label, context)
    except AttributeError:
        return context.evaluate_terminus(node, label, context)

class tree_node(object):
    def __init__(self, subnodes):
        self._counter  = 0
        self._subnodes = {}
        try:
            for label,subnode in subnodes.items():
                self._append(subnode, label)
        except AttributeError:
            for subnode in subnodes:
                self._append(subnode)
    def _append(self, subnode, label=None):
        if label is None:
            label = self._counter
            self._counter += 1
        if label in self._subnodes:
            raise RuntimeError("A subnode already exists with this label.")    # could do a better job avoiding conflicts with generated labels.
        self._subnodes[label] = subnode
        return label
    def _evaluate(self, label, context):
        subcontext, evaluate_node = self._implementation(label, context)
        evaluated_subnodes = {sublabel: evaluate(subnode, sublabel, subcontext) for sublabel,subnode in self._subnodes.items()}
        return evaluate_node(evaluated_subnodes)

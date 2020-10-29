#  (C) Copyright 2020 Anthony D. Dutoi
#
#  This file is part of TonyUtil.
#
#  TonyUtil is free software: you can redistribute it and/or modify
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
import textwrap



def _identify_subblock(line):
    """ if line is a simple {substitution} field id on its own, return the key and the level of indentation, otherwise False """
    line = line.rstrip()
    before = len(line)
    line = line.lstrip()
    after  = len(line)
    indent = " " * (before - after)
    try:
        beg, key, end = line[0], line[1:-1], line[-1]
    except:
        return False
    else:
        if beg=="{" and end=="}" and key.isidentifier():
            return (key, indent)
        else:
            return False

def _identify_subblocks(string):
    """ given a multiline string, identifies lines corresponding to code subblocks, and returns string for .format use, along with dictionary of subblock indents """
    subblocks = []    # will contain a list of (key,indent) 2-tuples
    one_liner = (string[-1] != "\n")
    lines = string.splitlines()
    for i in range(len(lines)):    # loop by index for in-place modification
        subblock = _identify_subblock(lines[i])
        if subblock:
            subblocks += [subblock]
            lines[i] = "{{{}}}".format(subblock[0])    # this field id is no longer indented, and is not followed by a '\n' (assume substitution will be '\n' terminated)
        else:
            lines[i] += "\n"                           # otherwise, leave it alone, except for appending '\n'
    if one_liner:  lines[-1] = lines[-1][:-1]
    return "".join(lines), dict(subblocks)



def _simplify_text(text):
    """ returns text removing common indentation and a single leading or trailing empty line (zero-length or whitespace), if present """
    lines = text.splitlines(keepends=True)
    if not lines[ 0].strip():  lines = lines[ 1:]    # str.strip() throws away all white space including '\n' (str.isspace() is False for empty string)
    if not lines[-1].strip():  lines = lines[:-1]
    string = "".join(lines)
    return textwrap.dedent(string)



def template(text):
    string = _simplify_text(text)
    string, subblocks = _identify_subblocks(string)
    def format_it(indent=0, **kwargs):
        indent = " " * indent
        substitutions = dict(kwargs)    # copy because will do in-place modifications
        for k,i in subblocks.items():
            if len(substitutions[k])>0:
                substitutions[k] = textwrap.indent(substitutions[k], i)
        text = string.format(**substitutions)
        return textwrap.indent(text, indent)
    return format_it

#    (C) Copyright 2018, 2020 Anthony D. Dutoi
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

# This was stolen from my Qode project, where a copy still lives figure out how to get Hg to handle dependencies!

"""\
This module is dedicated to reading input out of python-syntax files that might just contain parameter definitions.

This has the dual benefits of making them quite flexible even without having to write a single line of parser code,
but, at the same time, the contents can be completely limited to parameter declarations (no import statements or other
"overhead"), even while the name of the file is dynamic (which cannot be accomplished easily using either imports of
parameters from the main code, or imports of the main code from the parameter code).

One of the more powerful aspects here is namespacing.  The user can import namespaces into the input file directly,
but also the code that asks for the reading and execution of the input file can pass it its namespace dictionary
(or any other namespace for that matter), making available names from other modules, or perhaps macros to lower
the pain of writing input files.  Finally, there is an as-of-yet unused option of defining some kind of default
namespaces (local to a module, or a class that calls the methods below?).

The only drawback is that any parser errors will come back in "pythonese" which will not make sense to many
end users.  The proposed solution is another function (a plain text parser in the same module that defines input-level
namespaces?) that checks *simple* inputs for sanity (including whether they make physical sense, not just whether they
are parseable).  This check can be turned off by an intro line like (parse_check = False) that triggers the parse checker
to stop checking.  Then more advanced users can do things like embed loops, and other things that the parse checker 
does not like . . . try-except is also probably my friend in this battle.
"""



class _dotdict(dict):    # replace with SimpleNamespace?
    """\
    dot.notation access to dictionary attributes
    Found at http://stackoverflow.com/questions/2352181/how-to-use-a-dot-to-access-members-of-dictionary,
    on 21.May.2015 courtesy of 'derek73'.
    """
    def __getattr__(self,attr):  return self.get(attr)
    __setattr__= dict.__setitem__
    __delattr__= dict.__delitem__



def from_string(string,write_to=None,namespace=None):
    """\
    Takes a string containing python code and executes it using the global namespace given as an argument
    (to expose names in modules like math, without them having to be referenced or imported in the string).
    The names defined inside the executed string are assigned to a namespace which is returned to the user.
    The identfiers in this space may be accessed using the . notation customary for builtin dictionaries.
    """
    if namespace is None:  namespace = globals()
    if write_to  is None:  write_to  = _dotdict({})
    exec(string,namespace,write_to)
    return write_to

def from_file(filename,write_to=None,namespace=None):
    """\
    Just a wrapper for read_input.from_string, but where the contents of an ASCII file are read as the string.
    """
    return from_string(open(filename).read(),write_to,namespace)

def from_argv(fields,write_to=None,namespace=None):
    """\
    Just a wrapper for read_input.from_string, but where a list of statements is executed (such as would be found in argv with no space around = signs)
    """
    string = ""
    for field in fields:  string += field + '\n'
    return from_string(string,write_to,namespace)

#  (C) Copyright 2012, 2013, 2020 Anthony D. Dutoi
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
from .external.outputs.code import template as code

# Right now, this stuff does very specific tasks (supports animations in svg).
# Eventually, I should abstract the more general tasks and leave them here and move anything
# very tailored to pytoon, etc to that code.



# Device interface

def _javascript_keys(listofkeys):
    """ maps a list of control keys to snippets of javascript code """
    # These are the key signals sent out from my laser pointer (and the most common keyboard controls) ... expand as needed.
    keymap = {    
        "space":       "32",
        "left-arrow":  "37",
        "right-arrow": "39",
        "up-arrow":    "38",
        "dn-arrow":    "40",
        "page-up":     "33",
        "page-dn":     "34",
        "B":           "66",
        "P":           "80",
        "R":           "82",
        "escape":      "27",
        "F5":          "116"
    }
    if len(listofkeys)==0:
        return None
    else:
        return "||".join("e.keyCode=={}".format(keymap[key]) for key in listofkeys)



# Sectionation

_javascript_in_svg = code("""
  <script>

    var SVGDocument = null;
    var SVGRoot     = null;
    var svgns       = 'http://www.w3.org/2000/svg';
    var xlinkns     = 'http://www.w3.org/1999/xlink';
    {variables}

    {listeners}

    {functions}

  </script>
""")



# Javascript implementations of controls

def _initialize_listeners_in_svg(variables, listeners, initialize):
    template = code("""
      function Init(evt)
      {{
        SVGDocument = evt.target.ownerDocument;
        SVGRoot     = SVGDocument.documentElement;
        {variables}
        SVGRoot.addEventListener('keyup', function (e) {{{listeners}}}, false);
        {initialize}
      }};
    """)
    return template(
        variables  =      "".join(variables),
        listeners  = "else ".join(listeners),
        initialize =      "".join(initialize)
    )

_animation_functions_in_svg = code("""
  function Toggle()
  {{
    if (SVGRoot.animationsPaused()) {{Play();}}
    else                            {{Pause();}}
  }};

  function Pause()
  {{
    SVGRoot.pauseAnimations();
    pauseButton.setAttributeNS(null, 'display', 'none');
    playButton.setAttributeNS( null, 'display', 'inline');
  }};

  function Play()
  {{
    SVGRoot.unpauseAnimations();
    playButton.setAttributeNS( null, 'display', 'none');
    pauseButton.setAttributeNS(null, 'display', 'inline');
  }};

  function Reset(timepoint)
  {{
    SVGRoot.setCurrentTime(timepoint);
  }};

  function FrameForward()
  {{
    timepoint = SVGRoot.getCurrentTime() + {delta}
    SVGRoot.setCurrentTime(timepoint);
  }};

  function FrameBackward()
  {{
    timepoint = SVGRoot.getCurrentTime() - {delta}
    SVGRoot.setCurrentTime(timepoint);
  }};
""")

_animation_buttons_in_svg = {
    "declare": code("""
      var pauseButton = null;
      var playButton  = null;
    """),
    "set": code("""
      pauseButton = SVGDocument.getElementById('pauseGroup');
      playButton  = SVGDocument.getElementById('playGroup');
    """),
    "init": code("""
      SVGRoot.pauseAnimations();
    """)
}

_animation_listeners  = code("if({toggleKeys}){{Toggle();}}else if({resetKeys}){{Reset(0);}}else if({backKeys}){{FrameBackward();}}else if({forwardKeys}){{FrameForward();}}")



# Assemble the javascript insertion

svg_credit = """\
The scripting to implement the "play/pause" button was adapted with gratitude from an example found online,\nwritten by Doug Schepers [doug@schepers.cc], November 2004.
"""

def script_in_svg(*, animate=None):    # .control members are dictionaries of form {"toggleKeys": ["space"], "resetKeys": ... }
    if not animate:
        return "", ""    # I think this is deprecated and can assume non-None argument
    declare_vars = []
    set_vars     = []
    initialize   = []
    listeners    = []
    functions    = []
    if animate.controls is not None:
        controls = animate.controls
    else:
        controls = {"toggleKeys": ["space","B"], "resetKeys": ["R","escape","F5","P"], "backKeys": ["left-arrow"], "forwardKeys": ["right-arrow"]}
    controls = { k:_javascript_keys(v) for k,v in controls.items() }
    declare_vars += [ _animation_buttons_in_svg["declare"]() ]
    set_vars     += [ _animation_buttons_in_svg["set"]()     ]
    initialize   += [ _animation_buttons_in_svg["init"]()    ]
    listeners    += [ _animation_listeners(**controls) ]
    functions    += [ _animation_functions_in_svg(delta=animate.delta) ]
    jscode = _javascript_in_svg(
        variables = "".join(declare_vars),
        listeners = _initialize_listeners_in_svg(set_vars, listeners, initialize),
        functions = "\n".join(functions)
    )
    return ' onload="Init(evt)"', jscode+"\n"

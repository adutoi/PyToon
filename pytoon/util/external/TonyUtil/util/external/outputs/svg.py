#  (C) Copyright 2012, 2013, 2018, 2020 Anthony D. Dutoi
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
import math
from .external.outputs import code



# Sectionation

#_header = """
#<?xml version="1.0" encoding="UTF-8" standalone="no"?>
#<!DOCTYPE svg PUBLIC "-//W3C//DTD SVG 20001102//EN" "http://www.w3.org/TR/2000/CR-SVG-20001102/DTD/svg-20001102.dtd">
#<svg width="100%" height="100%" viewBox="{viewbox}"\
# xmlns="http://www.w3.org/2000/svg"\
# xmlns:xlink="http://www.w3.org/1999/xlink"\
# xmlns:sodipodi="http://sodipodi.sourceforge.net/DTD/sodipodi-0.dtd"\
# xmlns:inkscape="http://www.inkscape.org/namespaces/inkscape"{javascript}>
#"""
#     vv-This-vv still works, so what is all ^^-this-^^ stuff?

def file_format(*, viewbox, image_code, definitions="", javascript=("",""), background="", documentation=""):
    template = code.template("""
      <svg width="100%" height="100%"{background} viewBox="{viewbox}" xmlns="http://www.w3.org/2000/svg"{javascript_init}>
        {documentation}

        {javascript}
        {definitions}
        {image_code}

      </svg>
    """)
    if documentation:  documentation = "\n" + documentation
    if background:  background = ' style="background-color:{}"'.format(background)    # allow things other than solid colors?
    javascript_init, javascript = javascript
    return template(background=background, viewbox=viewbox, javascript_init=javascript_init, documentation=documentation, javascript=javascript, definitions=definitions, image_code=image_code)

def defintions(defs):
    template = code.template("""
      <defs>
        {defs}
      </defs>
    """)
    if defs:  return template(defs) + "\n"
    else:     return ""

def title_description(title=None, description=None):
    title_template = code.template("""
      <title>{title}</title>
    """)
    description_template = code.template("""
      <desc>
        {description}
      </desc>
    """)
    documentation = ""
    if title:        documentation += title_template(title=title)
    if description:  documentation += description_template(description=description)
    return documentation



# Primitive, repetitive formatting strings

dash = lambda d:  " ".join(d)

_alpha     = lambda a,o:              '' if (a is None) else '" {obj}-opacity="{opacity}'.format(obj=o, opacity=a)

_objcolor  = lambda c,a,o:            '{color}{opacity}'.format(color=c, opacity=_alpha(a,o))
gradcolor  = lambda p,c,a:            '\n  <stop offset="{percent}%" stop-color={color}/>'.format(percent=p, color=_objcolor(c,a,'stop'))

fillnone   =                          'none'
fillgrad   = lambda i:                'url(#{identifier})'.format(identifier=i)

_rad_sub   =                          'cx="{p}%" cy="{p}%" fx="{p}%" fy="{p}%"'.format(p=50)
_lin_sub   = lambda x1,y1,x2,y2:      'x1="{x1}%"  y1="{y1}%" x2="{x2}%" y2="{y2}%"'.format(x1=x1, y1=y1, x2=x2, y2=y2)
rad_grad   = lambda i,r,c:            '\n<radialGradient id={identifier}\n  {subst}\n  r="{radius}">{colors}\n</radialGradient>'.format(identifier=i, subst=_rad_sub, radius=r, colors=c)
lin_grad   = lambda i,x1,y1,x2,y2,c:  '\n<linearGradient id={identifier}\n  {subst}>{colors}\n</linearGradient>'.format(identifier=i, subst=_lin_sub(x1,y1,x2,y2), colors=c)

path_beg   = lambda x,y:              'M {x} {y}'.format(x=x, y=y)
path_line  = lambda x,y:              ' L {x} {y}'.format(x=x, y=y)
path_arc   = lambda rx,ry,s,c,x,y:    ' A {rx} {ry} {skew} 0 {cclockwise} {x} {y}'.format(rx=rx, ry=ry, skew=s, cclockwise=c, x=x, y=y)

image      = lambda f,h,v,a,x,y,dx,dy: '''
<g transform="translate({},{})">
  <g transform="rotate({},{},{})">
    <image xlink:href="{}" x="0" y="0" width="{}" height="{}" preserveAspectRatio="none" />
  </g>
</g>
'''.format(dy,dy,a,x,y,f,h,v)



# General xml tag and specifications/applications

def _xml_tag(tag, props, duration):
    animate = code.template("""
      <animate attributeName="{to_animate}" repeatCount="indefinite" dur="{duration}s"
        KeyTimes="{times}"
        values="
          {values}
        "
      />
    """)
    constant = ""
    animated = ""
    for prop,value in props.items():
        if value is not None:
            if duration is None:
                constant += ' {}="{}"'.format(prop, value)
            elif len(value)==1:
                _, value = value[0]
                if value is not None:
                    constant += ' {}="{}"'.format(prop, value)
            else:
                times, values = zip(*value)
                animated += animate(to_animate=prop, duration=duration, times="; ".join(str(t) for t in times), values=";\n".join(str(v) for v in values)+"\n")
    if animated:
        return code.template("""
          <{tag}{constant}>
            {animated}
          </{tag}>
        """)(tag=tag, constant=constant, animated=animated)
    else:
        return code.template("""
          <{tag}{constant}/>
        """)(tag=tag, constant=constant)

def _shape_props(line_rgb, line_alpha, line_weight, line_dash, fill_rgb, fill_alpha):
    return {
        "stroke":            line_rgb,
        "stroke-opacity":    line_alpha,
        "stroke-width":      line_weight,
        "stroke-dasharray":  line_dash,
        "fill":              fill_rgb,
        "fill-opacity":      fill_alpha
    }

def path(points, line_rgb, line_alpha, line_weight, line_dash, fill_rgb, fill_alpha, duration=None):
    props = _shape_props(line_rgb, line_alpha, line_weight, line_dash, fill_rgb, fill_alpha)
    props.update({
        "d": points
    })
    return _xml_tag("path", props, duration)

def circle(center_x, center_y, radius, line_rgb, line_alpha, line_weight, line_dash, fill_rgb, fill_alpha, duration=None):
    props = _shape_props(line_rgb, line_alpha, line_weight, line_dash, fill_rgb, fill_alpha)
    props.update({
        "r":  radius,
        "cx": center_x,
        "cy": center_y
    })
    return _xml_tag("circle", props, duration)



# Code for building animations

animation = code.template("""
  <g onclick=\"Toggle()\">  <!-- begin animated image -->

    {image}

  </g>                      <!-- end animated image -->

  {controls}
""")

def animation_controls(*, duration, control_location=(0,0,1), dot_count=150, offset=32, length=200, _fudge=0.9999, _flt=lambda x: "{:.5g}".format(x)):
    controls = code.template("""
      <g transform="translate({control_x},{control_y})">
        <g transform="scale({control_scale})">
          <!-- the play/pause button -->
          <a id="playGroup" display="inline" onclick="Play()">
            <circle id="play" cx="15" cy="15" r="12" fill="lightgray" stroke-width="2" stroke="gray"/>
            <polygon points="11,9 22,15 11,21" fill="gray" stroke="gray" stroke-width="2" stroke-linejoin="round"/>
          </a>
          <a id="pauseGroup" display="none" onclick="Pause()">
            <circle id="pause" cx="15" cy="15" r="12" fill="lightgray" stroke-width="2" stroke="gray"/>
            <line x1="12" y1="10" x2="12" y2="20" stroke="gray" stroke-width="4" stroke-linecap="round"/>
            <line x1="19" y1="10" x2="19" y2="20" stroke="gray" stroke-width="4" stroke-linecap="round"/>
          </a>
          <!-- the progress bar -->
          <line x1="12" y1="10" x2="12" y2="20" stroke="gray" stroke-width="4" stroke-linecap="round">
            <animateTransform attributeName="transform" type="translate" from="20 0" to="220 0" begin="0s" dur="{duration}s" repeatCount="indefinite" />
          </line>
          <!-- the timeline as a series of clickable dots -->
          {timeline}
        </g>
      </g>
    """)
    def time_dot(f):
        dot = code.template("""
          <a display="inline" onclick="Reset({timepoint})">
            <circle cx="{timemark}" cy="15" r="2" fill="gray" stroke-width="0" stroke="gray"/>
          </a>
        """)
        return dot(timepoint=_flt(f*duration), timemark=_flt(offset+(f*length)))
    control_x, control_y, control_scale = control_location
    timeline = "".join( time_dot(_fudge*i/dot_count) for i in range(dot_count+1) )
    return controls(duration=duration, timeline=timeline, control_x=control_x, control_y=control_y, control_scale=control_scale)

def frame(*, filename=None, image_code=None, duration=None, index=None, count=None):
    if (filename and image_code) or not (filename or image_code):
        raise RuntimeError("one (and only one) of filename or image_code can be specified to make an animation frame")
    external_image = code.template("""
      <image width="100%" height="100%" xlink:href="{filename}">
        {animate}
      </image>
    """)
    embedded_image = code.template("""
      <g>
        {image_code}
        {animate}
      </g>
    """)
    animate_it = code.template("""
      <animate attributeName='display' values='{display}' dur='{duration}s' begin='0.0s' repeatCount="indefinite"/>
    """)
    if duration:
        display = ["none"]*count
        display[index] = "inline"
        animate  = animate_it(display=";".join(display), duration=duration)
    else:
        animate  = ""
    if filename:
        return external_image(    filename=filename, animate=animate)
    else:
        return embedded_image(image_code=image_code, animate=animate)



# code snippets for "multipage" svgs

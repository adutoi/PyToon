import math
from pytoon import composite, circle, polygon, animated

def c(_t_):
    x = 50 * math.cos(2*math.pi * _t_)
    return (x,0)

image = composite([
    polygon(points=[(-200,-110), (-200,110), (200,110), (200,-110)], lstyle=False, fstyle="tan"),
    circle(center=animated(c,Dt=0.05))
    ])

image.svg(time=(0,1), duration=2)

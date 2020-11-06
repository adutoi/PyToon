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
from math import pi, sin, cos, tan, atan, sqrt, modf
import random
from util import int_round
from pytoon import struct, composite, circle, polygon, positional_transform

rand = lambda: random.uniform(-0.35, 0.35)

def modf_min(x):
    f, i = modf(x)
    if f<-0.5:
        return f+1, i-1
    elif f>=0.5:
        return f-1, i+1
    else:
        return f, i

def distort(L, T, t):
    A = 0.1
    def f(p):
        x, y = p        
        xP = x/L - t/T
        y = y * (1 - A*cos(2*pi*xP))
        xPf, xPi = modf_min(xP)
        xP = xPi + atan(sqrt((1+A)/(1-A)) * tan(pi*xPf)) / pi
        x = L * (xP + t/T)
        return x,y
    return f, 1

X, Y, d = 600, 200, 15

Nx, Ny = int_round(X/d), int_round(Y/d)
Px, Py = [i*X/Nx for i in range(Nx+1)], [i*Y/Ny for i in range(Ny+1)]

positions = []
for x in Px:
    for y in Py:
        positions += [(x+rand()*d, y+rand()*d)]
special = ((Nx+1)*(Ny+1))//2 - (Ny+1)//4 - 1

block              = polygon(lstyle=False, fstyle="#202020")
molecule           = circle(radius=4, lstyle=("black",0.25), fstyle="#3bba9c")
molecules          = [molecule(center=(x,y)) for x,y in positions]
surface            = [(i*X/125,Y*1.05) for i in range(125+1)]

wavy = [i*X/125 for i in range(63)]
wavy = [(x,10) for x in wavy] + [(x,-10) for x in reversed(wavy)]
wavy = polygon(points=wavy, lstyle=("black",0.25), fstyle="green").S(0.40).R(60).T(0,-15)

image = composite([
    composite([
        polygon(points=[(0,-20),*surface,(X,-20)], lstyle=False, fstyle="#233142"),
        *molecules,
        wavy.S(1).T(60,0), wavy.S(1.1).T(150,0), wavy.S(1.2).T(195,0), wavy.S(0.7).T(300,0), wavy.S(1.5).T(470,0), wavy.S(1).T(510,0), wavy.S(0.8).T(530,0)
    ], transform=positional_transform(distort, L=X/2, T="T", t="_t_").animated(Dt=0.1)),
    molecules[special](radius=2, fstyle="red"),
    block(points=[(-10,20),(-10,-15),(X+10,-15),(X+10,20)], fstyle="brown").T(0,-30),
    block(points=[(-15,-46),(-15,Y*1.5),(20,Y*1.5),(20,-46)]),
    block(points=[(X-20,-46),(X-20,Y*1.5),(X+15,Y*1.5),(X+15,-46)])
])

T = 3

image(T=T).svg(title="Wave on the Surface of Water", time=(0,T), duration=T, background="#202020", controls=False)

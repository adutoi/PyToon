#    (C) Copyright 2019 Anthony D. Dutoi
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
import math
from .units import *

# It is worth noting that it does not really matter what one uses as the base units.
# Even though we are doing quantum calculations, we could have set up SI units, and,
# from the outside we would not be able to tell the difference as long as all the symbols
# here are defined and internally consistent.  However, it just seems like a good idea
# to set even the internal working unit system such that the numbers of interest are 
# not particularly large or small.

# The base unit system for our calculations (supplement the electromechanical portion of a.u. with SI temperature)

one, hbar, m_e, a_0, e, K = unit_system("hbar", "m_e", "a_0", "e", "K")

# Other atomic units, derived from our base units

t_0 = (m_e * a_0**2 / hbar).symbolic("t_0")
E_H = (hbar**2 / (m_e * a_0**2)).symbolic("E_H")

# Named scalars
# *If you don't do this, you cannot really equate hartrees and J/mol.  You can equate hartrees/individual and J/mol, but then you need
# to set either mol or individual as your fundamental unit and use N_A to define the other.  Then you are stuck writing things like
# print(energy/individual).in_(kJ_per_mol)
# where individual is a predefined unit and energy is some computed result

mol = (6.02214076e23 * one).symbolic('mol')	# this may not be the standard formal way of looking at a mole, but it is sure a heck of a lot more convenient*
pi  = (math.pi * one).symbolic('pi')

# The SI units in terms of a.u. (so we may convert to/from them)

# m_e = 9.1093837015e-31 kg
# a_0 = 5.29177210903e-11 m
# t_0 = 2.4188843265857e-17 s
kg = (m_e / 9.1093837015e-31).symbolic("kg")
m  = (a_0 / 5.29177210903e-11).symbolic("m")
s  = (t_0 / 2.4188843265857e-17).symbolic("s")
J  = (kg * m**2 / s**2).symbolic("J")
N  = (J / m).symbolic("N")
L  = (m**3 / 1000).symbolic("L")
C  = (e / 1.602176634e-19).symbolic("C")

# Scaled units

g    = (1e-3 * kg).symbolic("g")
pm   = (1e-12 * m).symbolic("pm")
nm   = (1e-9  * m).symbolic("nm")
cm   = (1e-2  * m).symbolic("cm")
km   = (1e3   * m).symbolic("km")
ats  = (1e-18 * s).symbolic("as")	# 'as' is a reserved keyword
fs   = (1e-15 * s).symbolic("fs")
nJ   = (1e-9  * J).symbolic("nJ")
kJ   = (1e3   * J).symbolic("kJ")
mL   = (1e-3  * L).symbolic("mL")

# Other common units

Ang   = (1e-10 * m).symbolic("Ang")
eV    = (1.602176634e-19 * J).symbolic("eV")
cal   = (4.184 * J).symbolic("cal")
kcal  = (1e3 * cal).symbolic("kcal")
invcm = (1 / cm).symbolic("cm^-1")
Hz    = (1 / s).symbolic("Hz")

# Fundamental constants

h   = (2*math.pi * hbar).symbolic("h")
c   = (2.99792458e8 * m / s).symbolic("c")
k_B = (1.38064852e-23 * J / K).symbolic("k_B")

# Is this the best way to do these?

amu = (g / mol).symbolic("amu")
M   = (mol / L).symbolic("M")

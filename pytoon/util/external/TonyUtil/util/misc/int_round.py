#
#  This file is distributed with TonyUtil, but with no claim of copyright by any author other than as implied below.
#
# This utility is based on code by an author identifying as Gribouillis, which was found at:
# http://www.daniweb.com/software-development/python/threads/299459/round-to-nearest-integer
# Failing any copyright or license notice, it is presumed to be in the public domain.
#



# The rational over int(round()) is to move the instability points to the half-integers

def int_round(x):
	"""int_round(number) -> integer Round a number to the nearest integer."""
	y = round(x) - .5
	return int(y) + (y>0)

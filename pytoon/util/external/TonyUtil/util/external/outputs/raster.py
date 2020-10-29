#  (C) Copyright 2012, 2013 Anthony D. Dutoi
#  (excepting components from the public domain, labeled as such below)
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
import struct    # This is from the standard library, not my alias to a SimpleNamespace
from .misc.int_round import int_round



###################################################################################################################
#
#   The core functions bmp_write, row_padding, pack_color, bmp, and the contents of default_bmp_header are
#   *based* on code by authors identifying themselves only as JDM2 and david.hilton,
#   which was found at http://pseentertainmentcorp.com/smf/index.php?topic=2034.0 .
#   Failing any copyright or license notice, it is presumed to be in the public domain.
#   They implement the actual details of creating a rasterized graphics file in .bmp format, which is then
#   convertable to other formats.
#
# important values: offset, headerlength, width, height and colordepth
# This is for a Windows Version 3 DIB header.
# You will likely want to customize the width and height.
default_bmp_header = {
'mn1':66,
'mn2':77,
'filesize':0,
'undef1':0,
'undef2':0,
'offset':122,
'headerlength':108,
'width':0,
'height':0,
'colorplanes':1,
'colordepth':32,
'compression':3,
'imagesize':0,
'res_hor':2834,
'res_vert':2834,
'palette':0,
'importantcolors':0,
'bmask':255,
'gmask':65280,
'rmask':16711680,
'amask':4278190080,
'colorspace':1,
'endpoints':(0,0,1,0,0,1),
'rgamma':0,
'bgamma':0,
'ggamma':1,
'whatisthis':(0,0,0)}
#
def bmp_write(header, pixels, filename):
	'''It takes a header (based on default_bmp_header), 
	the pixel data (from structs, as produced by get_color and row_padding),
	and writes it to filename'''
	header['imagesize'] = len(pixels)
	header['filesize'] = header['offset'] + header['imagesize']
	header_str = b''
	header_str += struct.pack('<B', header['mn1'])
	header_str += struct.pack('<B', header['mn2'])
	header_str += struct.pack('<L', header['filesize'])
	header_str += struct.pack('<H', header['undef1'])
	header_str += struct.pack('<H', header['undef2'])
	header_str += struct.pack('<L', header['offset'])
	header_str += struct.pack('<L', header['headerlength'])
	header_str += struct.pack('<L', header['width'])
	header_str += struct.pack('<L', header['height'])
	header_str += struct.pack('<H', header['colorplanes'])
	header_str += struct.pack('<H', header['colordepth'])
	header_str += struct.pack('<L', header['compression'])
	header_str += struct.pack('<L', header['imagesize'])
	header_str += struct.pack('<L', header['res_hor'])
	header_str += struct.pack('<L', header['res_vert'])
	header_str += struct.pack('<L', header['palette'])
	header_str += struct.pack('<L', header['importantcolors'])
	header_str += struct.pack('<L', header['rmask'])
	header_str += struct.pack('<L', header['gmask'])
	header_str += struct.pack('<L', header['bmask'])
	header_str += struct.pack('<L', header['amask'])
	header_str += struct.pack('<L', header['colorspace'])
	for i in header['endpoints']:  header_str += struct.pack('<L',i)
	header_str += struct.pack('<L', header['rgamma'])
	header_str += struct.pack('<L', header['bgamma'])
	header_str += struct.pack('<L', header['ggamma'])
	for i in header['whatisthis']:  header_str += struct.pack('<L',i)
	#create the outfile
	outfile = open(filename, 'wb')
	#write the header + pixels
	outfile.write(header_str + pixels)
	outfile.close()
#
def row_padding(width, colordepth):
	'''returns any necessary row padding'''
	byte_length = width*colordepth//8
	# how many bytes are needed to make byte_length evenly divisible by 4?
	padding = (4-byte_length)%4 
	padbytes = b''
	for i in range(padding):
		x = struct.pack('<B',0)
		padbytes += x
	return padbytes
#
def pack_color(alpha, red, green, blue):
	'''accepts values from 0-255 for each value, returns a packed string'''
	return struct.pack('<BBBB',blue,green,red,alpha)
#
# expects a structure with the members
#  hdim
#  vdim
#  colors
#  filestem
# where hdim, vdim and filename are relatively self-explanatory static data.
# colors is a member function (or data assigned to a function)
# of two integers which returns an (alpha,R,G,B) tuple,
# where each member of the tuple is an integer in the range [0,255].
#
def bmp_general(data):
	header = default_bmp_header
	header["width"]  = data.hdim
	header["height"] = data.vdim
	#Build the byte array.  This code takes the height
	#and width values from the dictionary above and
	#generates the pixels row by row.  The row_padding
	#stuff is necessary to ensure that the byte count for each
	#row is divisible by 4.  This is part of the specification.
	pixels = b''
	for row in range(data.vdim-1,-1,-1):# (BMPs are L to R from the bottom L row)
		for column in range(data.hdim):
			a,r,g,b = data.colors(column,row)
			pixels += pack_color(a, r, g, b)
		pixels += row_padding(data.hdim, header['colordepth'])
	#call the bmp_write function with the
	#dictionary of header values and the
	#pixels as created above.
	bmp_write(header, pixels, data.filestem+'.bmp')
#
###################################################################################################################



########### In the remaining functions, I (Anthony Dutoi) wrap the above code to bend it to my purposes ###########



# Each of the following results in a file, <'filestem'>.bmp, being written to disk.  These should be thought of as
# utilities for inclusion than in a pytoon drawing.  Later, I may wrap these so that an absolute raster precision may
# be given similar to how I handle curves.
#
# The most general way to specify a raster image would be via an object with the attributes demanded by bmp_general() above,
# which the user has access to, if needed.  The following functions allow one to pass in more primitive objects, and they build
# the object required by bmp_general() and pass it to the bmp_general() function.
# Code design ?:  Does it make sense to wrap an array, just to unwrap it later? ... swap layers?
# (lowest layer is bmp, called by data_bmp, called by func_bmp, with bmp_general calling bmp directly ??)
#
# Eventually I should write the functions jpg_general(), jpg(), data_jpg() and func_jpg() that mirror the action
# of all these by writing a bmp to disk and then invoking ImageMagick via functions in shell.py.
# (Of course, I should write the gif and tiff versions, too).



# This one assumes you have a 2D array of (a,r,g,b) tuples, 'data', where each member of the tuple is an integer in [0,255].
# The array is assumed to be rectangular and twice indexable, where the outer index enumerates rows of the raster image.

class color_array_wrapper:
	def __init__(self,filestem,data):
		self.data     = data
		self.vdim     = len(data)
		self.hdim     = len(data[0])
		self.filestem = filestem
	def colors(self,i,j):  return self.data[j][i]

def bmp(data,filestem):  bmp_general(color_array_wrapper(filestem,data))



# An example color map (also used as the default below), which presumes the input is a real number 
# in the interval [-1,1], and it returns an alpha*RGB code where the color gives the sign (R=neg, G=pos)
# and the darker the color is the higher the magnitude.  If the magnitude exceeds 1, it just maps
# to the darkest color (ie, bigger numbers not distinguisable).
#
# Should I have a separate file for color maps?

def real2RGalpha(v):
	A,R,G,B = (0,0,0,0)
	A = int(math.floor(255*abs(v)))
	if A>255:  A = 255
	if v>0:    G = 255
	else:      R = 255
	return (A,R,G,B)



# This one assumes you have a 2D array of numbers, 'data', and a 'colormap' that you want to use to map them to a color tuple.
# The array is assumed to be rectangular and twice indexable, where the outer index enumerates rows of the raster image.
# The remaining argument allows the user to linearly scale the values in 'data' via Zscale.

class data_array_wrapper:
	def __init__(self,filestem,data,colormap,Zscale):
		self.data     = data
		self.colormap = colormap
		self.Zscale   = Zscale
		self.vdim     = len(data)
		self.hdim     = len(data[0])
		self.filestem = filestem
	def colors(self,i,j):
		return self.colormap( self.Zscale * self.data[j][i] )

def data2bmp(filestem,data,Zscale=1,colormap=real2RGalpha):  bmp_general(data_array_wrapper(filestem,data,colormap,Zscale))



# This one assumes you have a function 'func' of two floating point coordinates to a color, via 'colormap'.  
# The remaining arguments determine the dimensions of the raster image (via Xrange,deltaX and Yrange,deltaY)
# and allow the user to linearly scale the output of 'func' via Zscale.

class function_wrapper:
	def __init__(self,filestem,func,colormap,Xrange,Yrange,deltaX,deltaY,Zscale):
		Xmin,Xmax     = Xrange
		Ymin,Ymax     = Yrange
		self.func     = func
		self.colormap = colormap
		self.Xmin     = Xmin
		self.Ymax     = Ymax
		self.deltaX   = deltaX
		self.deltaY   = deltaY
		self.Zscale   = Zscale
		self.hdim     = int_round( (Xmax-Xmin) / float(deltaX) ) + 1
		self.vdim     = int_round( (Ymax-Ymin) / float(deltaY) ) + 1
		self.filestem = filestem
	def colors(self,i,j):
		x = self.Xmin + i*self.deltaX
		y = self.Ymax - j*self.deltaY
		return self.colormap( self.Zscale * self.func(x,y) )

def func2bmp(filestem,func,Xrange,Yrange,deltaX,deltaY,Zscale=1,colormap=real2RGalpha):
	bmp_general(function_wrapper(filestem,func,colormap,Xrange,Yrange,deltaX,deltaY,Zscale))

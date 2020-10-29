#  (C) Copyright 2013, 2020 Anthony D. Dutoi
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
import os



class image_file(object):
    """ This makes an image file just a bit more abstract than an file on a disk, answering questions about its size, etc """
    def __init__(self, filename):
        self.filename = filename
    def size(self):
        # Output of ImageMagick 'identify' looks like:   file.png PNG 978x253 978x253+0+0 16-bit DirectClass 17.7KB 0.010u 0:00.009
        os.system("identify {filename} > {filename}.ImageMagickIdentify".format(filename=self.filename))
        sizes = open("{}.ImageMagickIdentify".format(self.filename), "r").read().split()[2].split("x")
        os.remove("{}.ImageMagickIdentify".format(self.filename))
        return ( float(s) for s in sizes )

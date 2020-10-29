#    (C) Copyright 2013, 2020 Anthony D. Dutoi
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
import os



# Classes that allows smoother operation with arbitrary command-line utilities.

class _script(object):
	def __init__(self, command):
		self.commands = ""
		self(command)
	def __call__(self, command):
		if command is not None:
			self.commands = self.commands + command + "\n"
	def _run(self, filestem, ext, shebang):
		if filestem is None:
			filestem = "tmp"
		filename = filestem + "." + ext
		if os.path.exists(filename):
			raise NameError('Not willing to overwrite existing file {}'.format(filename))
		script = open(filename, "w")
		script.write("#!{}\n".format(shebang))
		script.write(self.commands)
		script.close()
		os.system("chmod u+x {script}".format(script=filename))
		os.system(os.path.abspath(filename))
		os.system('rm {script}'.format(script=filename))



class bash(_script):
	def __init__(self, command=None):
		_script.__init__(self, command)
	def run(self, filestem=None, local=None):
		if local is not None:
			path = local.absolute_path_to_bash
		else:
			path = "/bin/bash"
		self._run(filestem, "bash", path)

class csh(_script):
	def __init__(self, command=None):
		_script.__init__(self, command)
	def run(self, filestem=None, local=None):
		if local is not None:
			path = local.absolute_path_to_csh
		else:
			path = "/bin/csh"
		self._run(filestem, "csh", path+" -f")

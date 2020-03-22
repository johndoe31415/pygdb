#!/usr/bin/env python3
#	pygdb - Python GDB convenience frontend
#	Copyright (C) 2020-2020 Johannes Bauer
#
#	This file is part of pygdb.
#
#	pygdb is free software; you can redistribute it and/or modify
#	it under the terms of the GNU General Public License as published by
#	the Free Software Foundation; this program is ONLY licensed under
#	version 3 of the License, later versions are explicitly excluded.
#
#	pygdb is distributed in the hope that it will be useful,
#	but WITHOUT ANY WARRANTY; without even the implied warranty of
#	MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#	GNU General Public License for more details.
#
#	You should have received a copy of the GNU General Public License
#	along with pygdb; if not, write to the Free Software
#	Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#
#	Johannes Bauer <JohannesBauer@gmx.de>

import gdb
import json
import os
import time
import base64

if "PYGDB_RUNFILE" in os.environ:
	with open(os.environ["PYGDB_RUNFILE"]) as f:
		pygdb_config = json.load(f)
else:
	pygdb_config = { }

class PyGDBCommand(gdb.Command):
	_CMD_NAME = None
	_HELP_PAGE = None
	_ARGS = None
	_OPTARGS = [ ]

	def __init__ (self):
		gdb.Command.__init__(self, self._CMD_NAME, gdb.COMMAND_USER)

	def invoke(self, arg, from_tty):
		presented_args = arg.split()
		min_arg_count = len(self._ARGS)
		max_arg_count = min_arg_count + len(self._OPTARGS)
		if min_arg_count <= len(presented_args) <= max_arg_count:
			if len(presented_args) < max_arg_count:
				presented_args += [ None ] * (max_arg_count - len(presented_args))
			self.run(*presented_args)
		else:
			print("Supplied %d arguments, but %d expected: %s %s" % (len(presented_args), len(self._ARGS), self._CMD_NAME, " ".join(self._ARGS)))

	def _read_memory(self, symbol, length):
		frame = gdb.selected_frame()
		(symbol, is_field) = gdb.lookup_symbol(symbol)
		address = symbol.value(frame)
		inferior = gdb.inferiors()[0]
		memory = inferior.read_memory(address, length)
		memory = bytes(memory)
		return memory

	@classmethod
	def register(cls, cmdclass):
		cmdclass()
		return cmdclass

@PyGDBCommand.register
class HexdumpCommand(PyGDBCommand):
	_CMD_NAME = "hexdump"
	_HELP_PAGE = "prints a hex dump from 'start' ranging 'length' bytes"
	_ARGS = [ "start", "length" ]

	def run(self, start, length):
		length = Tools.to_int(length)
		data = self._read_memory(start, length)
		HexDump().dump(data)

@PyGDBCommand.register
class CaptureMemoryCommand(PyGDBCommand):
	_CMD_NAME = "capturemem"
	_HELP_PAGE = "captures memory from 'start' ranging 'length' bytes into the capture JSON file"
	_ARGS = [ "start", "length" ]
	_OPTARGS = [ "comment" ]

	def run(self, start, length, comment):
		length = Tools.to_int(length)
		data = self._read_memory(start, length)
		capture = {
			"ts": time.time(),
			"symbol": start,
			"data": base64.b64encode(data).decode("ascii"),
		}
		if comment is not None:
			capture["comment"] = comment
		capturefile = pygdb_config.get("capture", "capture_file.json")
		try:
			with open(capturefile) as f:
				content = json.load(f)
		except (FileNotFoundError, json.decoder.JSONDecodeError):
			content = [ ]
		content.append(capture)
		with open(capturefile, "w") as f:
			json.dump(content, f)

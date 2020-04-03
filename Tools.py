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

class StringParseException(Exception): pass

class Tools():
	_INT_PREFIXES = (
		("0b", 2),
		("0o", 8),
		("0x", 16),
	)

	_INT_SUFFIXES = (
		("k", 1024),
		("M", 1024 * 1024),
		("G", 1024 * 1024 * 1024),
	)

	@classmethod
	def to_int(cls, text):
		system = 10
		for (prefix, prefix_value) in cls._INT_PREFIXES:
			if text.startswith(prefix):
				system = prefix_value
				text = text[len(prefix): ]
				break

		scalar = 1
		for (suffix, suffix_value) in cls._INT_SUFFIXES:
			if text.endswith(suffix):
				scalar = suffix_value
				text = text[:-len(suffix)]
				break

		return scalar * int(text, system)

	@classmethod
	def parse_args(cls, argstr):
		if len(argstr) == 0:
			return [ ]

		result = [ "" ]
		text = list(argstr)
		quote = False
		while len(text) > 0:
			char = text.pop(0)
			if char == " ":
				if quote:
					result[-1] += char
				else:
					result.append("")
			elif char == "\"":
				quote = not quote
			elif char == "\\":
				if len(text) == 0:
					raise StringParseError("Backslash at end of string provided.")
				nextchar = text.pop(0)
				if nextchar in [ "\\", "\"" ]:
					result[-1] += nextchar
				else:
					raise StringParseError("Illegal escape sequence: \\%s" % (nextchar))
			else:
				result[-1] += char
		return result

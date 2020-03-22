# pygdb
pygdb is a simple wrapper around gdb that enriches the gdb console by a number
of features that are useful for reversing.

## Usage
You write a runfile (JSON file) that describes how you want to run your target
and what breakpoints to auto-set on, what to auto-execute on those breakpoints
and so on. The example given in `example_bc.json` shows how the syntax looks like:

```json
{
	"inferior":		"/usr/bin/bc",
	"args":			[ ],
	"env": {
		"foo":	"bar"
	},
	"run": true,
	"break": [
		{
			"on":	"__pselect",
			"execute": [
				"hexdump readfds 0x10"
			]
		}
	]
}
```

This example auto-runs `bc`, sets an additional environment variable, runs it
without arguments, breaks on `__pselect` and, when it does break, performs a
hex dump of the `readfds` array. Then, just run it like this:

```
$ ./rungdb example_bc.json
```

## License
GNU GPL-3.

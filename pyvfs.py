import textwrap

class CommandInterpreter:
    def __init__(self):
        pass

    def interprete(self, parameters):
        command = "help"
        if len(parameters):
            command = parameters.pop(0)
        if hasattr(self, "do_%s" % command):
            getattr(self, "do_%s" % command)( parameters )
        else:
            print("Unknown command '%s'" % command)
            self.do_help([])

    def do_create(self, parameters):
        """Create a new disk image with the given parameters."""
        pass

    def do_help(self, parameters):
        """Print an overview of all available commands."""
        COMMAND_LEADIN = "  "
        COMMAND_LEADOUT = "  "
        CONSOLE_WIDTH = 79

        def get_command_and_help(function):
            command = function.__func__.__name__[3:]    # strip off the 'do_' part
            doclines = function.__doc__.split("\n")
            doclines = map(lambda x: x.strip(), doclines)
            return (command, " ".join(doclines))

        command_names = list(filter(lambda x : x.startswith("do_"), dir(self)))
        commands = map( lambda x: getattr(self, x), command_names )
        commands = list(map( get_command_and_help, commands ))
        command_lengths = map(lambda x: len(x[0]), commands)
        max_length = max( command_lengths )
        indent = len( COMMAND_LEADIN+COMMAND_LEADOUT ) + max_length

        print("PyvirtualFS utility")
        print("")
        for (command, help) in commands:
            help_lines = textwrap.wrap(help,
                                       width = CONSOLE_WIDTH-indent,
                                       subsequent_indent=indent*" ")
            print(COMMAND_LEADIN + ("%-"+ "%us" % max_length) % command
                  + COMMAND_LEADOUT + help_lines[0] )
            for line in help_lines[1:]:
                print(line)

if __name__=="__main__":
    import sys

    cmd_interpreter = CommandInterpreter()
    cmd_interpreter.interprete( sys.argv[1:] )

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
        """Create a new empty disk image of the given size. Give a file name
        for the new image and the size which can be given with a suffix:
            <size>[k|M|G]"""
        def parse_size(s):
            value = s.strip()
            suffix = ""
            if value[-1] in ["k", "M", "G"]:
                suffix = value[-1]
                value = value[:-1]
            try:
                value = int(value)
            except:
                raise ValueError("%s is not a valid size string" % s)
            return value * {"": 1, "k": 1024, 
                            "M": 1024*1024, 
                            "G": 1024*1024*1024}[suffix]
        
        if len(parameters)<2:
            print("'create' command requires a filename and a size")
            return
        filename = parameters[0]
        size = parse_size( parameters[1] )
        from commands import CreateCommand
        cmd = CreateCommand(filename, size)
        cmd.execute()

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

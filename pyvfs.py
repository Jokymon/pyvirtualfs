import textwrap, inspect

def command(wrappee):
    wrappee.__is_command__ = True
    doclines = wrappee.__doc__.format(cmd=wrappee.__name__)
    doclines = doclines.split("\n")
    doclines = list(filter(lambda x: x.strip()!="", doclines))
    wrappee.__shortdoc__ = doclines[0].strip()
    wrappee.__usagedoc__ = ""
    if len(doclines)>1:
        wrappee.__usagedoc__ = doclines[1].strip()
    wrappee.__longdoc__ = ""
    if len(doclines)>2:
        wrappee.__longdoc__ = " ".join(doclines[2:])

    return wrappee

def iscommand(function):
    if inspect.ismethod(function) and hasattr(function, "__is_command__"):
        return True
    return False

class CommandInterpreter:
    def __init__(self):
        pass

    def interprete(self, parameters):
        command = "help"
        if len(parameters):
            command = parameters.pop(0)
        if hasattr(self, command) and iscommand(getattr(self, command)):
            getattr(self, command)( parameters )
        else:
            print("Unknown command '%s'" % command)
            self.help([])

    @command
    def create(self, parameters):
        """Creating empty disk images with a given size.
        
        {cmd} <image_file_name> <size>[k|M|G]

        Create a new empty disk image with the file name <image_file_name>. The
        size of the image can be specified in bytes (without a suffix), in
        kilobytes (suffix 'k'), Megabytes (suffix 'M') or Gigabytes (suffix
        'G')."""
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

    @command
    def help(self, parameters):
        """Print an overview of all available commands."""
        COMMAND_LEADIN = "  "
        COMMAND_LEADOUT = "  "
        CONSOLE_WIDTH = 79

        commands = [ item[1] for item in inspect.getmembers(self, iscommand) ]
        command_lengths = map(lambda x: len(x.__name__), commands)
        max_length = max( command_lengths )
        indent = len( COMMAND_LEADIN+COMMAND_LEADOUT ) + max_length

        print("PyvirtualFS utility")
        print("")
        for cmd in commands:
            help_lines = textwrap.wrap(cmd.__shortdoc__,
                                       width = CONSOLE_WIDTH-indent,
                                       subsequent_indent=indent*" ")
            print(COMMAND_LEADIN + ("%-"+ "%us" % max_length) % cmd.__name__
                  + COMMAND_LEADOUT + help_lines[0] )
            for line in help_lines[1:]:
                print(line)

if __name__=="__main__":
    import sys

    cmd_interpreter = CommandInterpreter()
    cmd_interpreter.interprete( sys.argv[1:] )

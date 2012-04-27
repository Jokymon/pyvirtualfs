import textwrap, inspect

def command(wrappee):
    wrappee.__is_command__ = True
    doclines = wrappee.__doc__.format(cmd=wrappee.__name__)
    doclines = doclines.split("\n")
    doclines = list(filter(lambda x: x.strip()!="", doclines))
    doclines = list(map(str.strip, doclines))
    wrappee.__shortdoc__ = doclines[0]
    wrappee.__usagedoc__ = ""
    if len(doclines)>1:
        wrappee.__usagedoc__ = doclines[1]
    wrappee.__longdoc__ = ""
    if len(doclines)>2:
        wrappee.__longdoc__ = " ".join(doclines[2:])

    return wrappee

def iscommand(function):
    if inspect.ismethod(function) and hasattr(function, "__is_command__"):
        return True
    return False

class CommandInterpreter:
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
    def help(self, parameters):
        """Print an overview of all available commands."""
        COMMAND_LEADIN = "  "
        COMMAND_LEADOUT = "  "
        COMMAND_SHORTDOC_LEADIN = "   "
        CONSOLE_WIDTH = 79

        commands = [ item[1] for item in inspect.getmembers(self, iscommand) ]
        command_names = map(lambda x: x.__name__, commands)
        if len(parameters)==0:
            command_lengths = map(len, command_names)
            max_length = max( command_lengths )
            indent = len( COMMAND_LEADIN+COMMAND_LEADOUT ) + max_length

            print(self.__doc__)
            print("")
            for cmd in commands:
                help_lines = textwrap.wrap(cmd.__shortdoc__,
                                           width = CONSOLE_WIDTH-indent,
                                           subsequent_indent=indent*" ")
                print(COMMAND_LEADIN + ("%-"+ "%us" % max_length) % cmd.__name__
                      + COMMAND_LEADOUT + help_lines[0] )
                for line in help_lines[1:]:
                    print(line)
        elif parameters[0] in command_names:
            cmd = list(filter(lambda x: x.__name__==parameters[0], commands))[0]
            title = "Command '%s'" % cmd.__name__
            print()
            print(title)
            print(len(title)*"=")
            print()
            print("Usage: %s" % cmd.__usagedoc__)
            print()
            help_lines = textwrap.wrap(cmd.__longdoc__,
                                       width = CONSOLE_WIDTH - len(COMMAND_SHORTDOC_LEADIN),
                                       initial_indent = COMMAND_SHORTDOC_LEADIN,
                                       subsequent_indent = COMMAND_SHORTDOC_LEADIN)
            for line in help_lines:
                print(line)
        else:
            print("Unknown command %s" % parameters[0])



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

    def do_help(self, parameters):
        print("Help for this program")

if __name__=="__main__":
    import sys

    cmd_interpreter = CommandInterpreter()
    cmd_interpreter.interprete( sys.argv[1:] )

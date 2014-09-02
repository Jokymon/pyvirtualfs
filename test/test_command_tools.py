from pyvirtualfs.command_tools import *


class TestCommandTools:
    def test_command_wrapper(self):
        @command
        def wrapped_function():
            """Testdocumentation of command {cmd}"""
            pass

        assert iscommand(wrapped_function)
        assert wrapped_function.__doc__ == \
            "Testdocumentation of command wrapped_function"

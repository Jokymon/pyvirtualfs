from command_tools import command, CommandInterpreter

class CreateCommand:
    def __init__(self, outfile, size):
        self.outfile = outfile
        self.size = size

    def execute(self):
        import os
        f = open(self.outfile, "wb")
        f.seek(self.size-1, os.SEEK_SET)
        f.write("\0".encode("utf-8"))
        f.close()

class FdiskCommand(CommandInterpreter):
    """Partition a disk image

    {cmd} <image_file_name> <command> [options]"""
    def __init__(self):
        self.__name__ = "fdisk"
        CommandInterpreter.__init__(self)

    def execute(self, parameters):
        from image_path import ImagePath
        img_path = ImagePath.parse(parameters[0])
 
    @command
    def create(self, parameters):
        """Create a new partition"""
        pass

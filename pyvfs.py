import string
from command_tools import command, CommandInterpreter

class PyvfsCommandInterpreter(CommandInterpreter):
    """PyVirtualFS"""

    def __init__(self):
        self.__name__ = "pyvfs"
        CommandInterpreter.__init__(self)

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
    def mkfs(self, parameters):
        """Create file systems in existing partitions"""
        pass


    @command
    def dump(self, parameters):
        """Dump the details of a disk image.

        {cmd} <image_file_name> l<detail level>

        The amount of details can be controlled with the l<number> parameter.
        1  Show details about the image
        2  Show a first level of details for all contained file systems."""

        from image_path import ImagePath
        img_path = ImagePath.parse(parameters[0])

        level = int(parameters[1][1:])

        from physical import DiskImage, Harddisk

        image = DiskImage( img_path.imagefile, "a" )
        hd = Harddisk( image )
        hd.dump()

        for i in range(4):      # TODO: take the amount of partitions from the actual image
            pi = hd.get_partition_info(i)
            print(" ***** Partition %u *****" % i)
            pi.dump()

        if level>=2:
            for i in range(4):
                fs = hd.get_filesystem(i)
                fs.dump()

    from commands import FdiskCommand
    fdisk = FdiskCommand()

if __name__=="__main__":
    import sys

    cmd_interpreter = PyvfsCommandInterpreter()
    cmd_interpreter.interprete( sys.argv[1:] )

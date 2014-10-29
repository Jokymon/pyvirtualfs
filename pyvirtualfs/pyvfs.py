#!/usr/bin/env python
import string
from pyvirtualfs.command_tools import command, CommandInterpreter
from pyvirtualfs.physical import DiskImage, createPhysicalImageFromImageType
from pyvirtualfs.image_path import ImagePath


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

        if len(parameters) < 2:
            print("'create' command requires a filename and a size")
            return
        filename = parameters[0]
        size = parse_size(parameters[1])
        from commands import CreateCommand
        cmd = CreateCommand(filename, size)
        cmd.execute()

    @command
    def mkfs(self, parameters):
        """Create file systems in existing partitions"""
        img_path = ImagePath.parse(parameters[0])

        image = DiskImage(img_path.imagefile, "a")
        phys = createPhysicalImageFromImageType(img_path.imagetype, image)
        filesystem = phys.get_filesystem(img_path.partition)
        filesystem.format()

    @command
    def dump(self, parameters):
        """Dump the details of a disk image.

        {cmd} <image_file_name> l<detail level>

        The amount of details can be controlled with the l<number> parameter.
        1  Show details about the image
        2  Show a first level of details for all contained file systems."""
        img_path = ImagePath.parse(parameters[0])

        level = int(parameters[1][1:])

        image = DiskImage(img_path.imagefile, "a")
        phys = createPhysicalImageFromImageType(img_path.imagetype, image)
        phys.dump(level=level)

    @command
    def copy(self, parameters):
        """Copy a file from or to a location inside an image"""
        if len(parameters) != 2:
            print("Source and destination file are required")
            return
        # for the moment only allow copying from a real file to a location in
        # an image file
        source_file = open(parameters[0], "rb")
        if sys.version_info[0] >= 3:
            source_data = source_file.read().decode("latin-1")
        else:
            source_data = source_file.read()
        source_file.close()

        img_path = ImagePath.parse(parameters[1])

        image = DiskImage(img_path.imagefile, "a")
        phys = createPhysicalImageFromImageType(img_path.imagetype, image)
        filesystem = phys.get_filesystem(img_path.partition)

        target_file = filesystem.open(img_path.filepath, "w")
        target_file.write(source_data)
        target_file.close()

    from pyvirtualfs.commands import FdiskCommand
    fdisk = FdiskCommand()

def main():
    import sys

    cmd_interpreter = PyvfsCommandInterpreter()
    cmd_interpreter.interprete(sys.argv[1:])

if __name__ == "__main__":
    main()

from pyvirtualfs.command_tools import command, CommandInterpreter


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
    """Managing partitions on a disk image

    {cmd} <command> <image_file_name> [options]"""
    def __init__(self):
        self.__name__ = "fdisk"
        CommandInterpreter.__init__(self)

    def execute(self, parameters):
        from pyvirtualfs.image_path import ImagePath
        img_path = ImagePath.parse(parameters[0])

    @command
    def create(self, parameters):
        """Create a new partition.

        {cmd} <image_url> start=<start_lba> end=<end_lba> type=<type number>
                 [spt=<sectors per track> hpc=<heads per cluster>]"""
        start_lba = None
        end_lba = None
        partition_type = None
        sectors_per_track = 63
        heads_per_cluster = 16

        from pyvirtualfs.image_path import ImagePath, PathParseError
        from pyvirtualfs.tools import int_ex
        try:
            image_url = ImagePath.parse(parameters[0])
        except PathParseError as p:
            print("First argument of create must be an image path with"
                  "a partition")
            print(p.msg)
            return

        for param in parameters[1:]:
            (key, value) = param.split("=")
            if key == "start":
                start_lba = int_ex(value)
            elif key == "end":
                end_lba = int_ex(value)
            elif key == "type":
                partition_type = int_ex(value)
            elif key == "spt":
                sectors_per_track = int_ex(value)
            elif key == "hpc":
                heads_per_cluster = int_ex(value)
            else:
                print("Unknown key name '%s'" % key)
                return

        if start_lba is None:
            print("Need a start LBA for this partition")
            return
        if end_lba is None:
            print("Need an end LBA for this partition")
            return
        if partition_type is None:
            print("Need a type for this partition")
            return

        from pyvirtualfs.physical import DiskImage, Harddisk
        from pyvirtualfs.tools import lba2chs

        assert image_url.imagetype == ImagePath.IMAGE_TYPE_HD
        image = DiskImage(image_url.imagefile, "a")
        hd = Harddisk(image)
        p = hd.get_partition_info(image_url.partition)
        p.type = partition_type
        p.chs_first_sector = lba2chs(start_lba, heads_per_cluster,
                                     sectors_per_track)
        p.chs_last_sector = lba2chs(end_lba, heads_per_cluster,
                                    sectors_per_track)
        p.lba_first_sector = start_lba
        p.sectors_in_partition = end_lba - start_lba + 1
        hd.set_partition_info(image_url.partition, p)

        hd.update_image(0x337a0564)

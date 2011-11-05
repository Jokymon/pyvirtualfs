import os
from tools import *

class PartitionInfo:
    """Class to collect the information of a partition entry"""
    def __init__(self, entry):
        self.bootable             = ord(entry[0])
        self.type                 = ord(entry[4])
        self.chs_first_sector     = char2chs(entry[1:4])
        self.chs_last_sector      = char2chs(entry[5:8])
        self.lba_first_sector     = char2dword(entry[8:12])
        self.sectors_in_partition = char2dword(entry[12:16])

class Partition:
    """Storage for the binary image of a complete partition"""
    def __init__(self, image_fd, partition_info):
        self.partition_info = partition_info
        image_fd.seek( 512 * partition_info.lba_first_sector )
        self.partition = image_fd.read( 512 * partition_info.sectors_in_partition )

class FileInfo:
    def __init__(self):
        self.filename = ""
        # attributes is a list of all attributes that apply to this directory
        # which can be "read_only", "hidden", "system", "archive", "directory"
        self.attributes = []
        self.creation_time = None
        self.last_access_time = None
        self.last_modification_time = None
        # start byte is the first byte of the file relative to the containing
        # partitions start
        self.start_byte = 0
        # size of the file in bytes
        self.size = 0

class FileHandle:
    def __init__(self):
        self._currentpos = 0
        self._open = False

    def close(self):
        pass

    def read(self, size=None):
        pass

    def seek(offset, whence=os.SEEK_SET):
        pass

    def tell(self):
        return self._currentpos

    def write(self, s):
        pass
    

#####################################################################################################

class Ext2Partition(Partition):
    def __init__(self, image_fd, partition_info):
        Partition.__init__(self, image_fd, partition_info)

        self.s_inodes_count = char2dword(self.partition[1024:1028])
        self.s_blocks_count = char2dword(self.partition[1028:1032])

#####################################################################################################

class Harddisk:
    def __init__(self, file_name, mode="r"):
        if not mode in ["r", "a"]:
            raise ValueError("mode string must be one of 'r', 'a', not '%s'" % mode)
        import mmap
        self._image = open(file_name, mode+"+b")
        mmap_access = { "r" : mmap.ACCESS_READ, "a" : mmap.ACCESS_WRITE }[mode]
        self._mmap = mmap.mmap(self._image.fileno(), 0, access=mmap_access)
        self._parse_partition_table()

    def _parse_partition_table(self):
        self._image.seek(0)
        mbr = self._mmap[0:512]

        self.partition_records = [ mbr[446 + i*16: 446 + (i+1)*16] for i in range(4) ]
        self.disk_signature = char2dword( mbr[440:444] )
        self.mbr_signature  = char2word( mbr[510:512] )

    def get_partition_info(self, partition_number):
        return PartitionInfo( self.partition_records[partition_number] )

    def get_partition(self, partition_number):
        pi = self.get_partition_info(partition_number)
        if pi.type==6:
            from fat16 import FAT16Partition
            return FAT16Partition(self._image, pi)
        elif pi.type==0x83:
            # TODO 0x83 is official not always just Ext2, need a cleverer detection
            return Ext2Partition(self._image, pi)
        else:
            return Partition(self._image, pi)
        

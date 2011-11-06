import os, sys
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

    def dump(self, fd=sys.stdout):
        if self.bootable==0x80:
            fd.write("  bootable\n")
        elif self.bootable==0x0:
            fd.write("  non bootable\n")
        else:
            fd.write("  invalid\n")
        fd.write("  CHS of first absolute sector (%u, %u, %u)\n" % self.chs_first_sector)
        fd.write("  Type: %x\n" % self.type)
        fd.write("  CHS of last absolute sector (%u, %u, %u)\n" % self.chs_last_sector)
        fd.write("  LBA of first absolute sector n partition: %u\n" % self.lba_first_sector)
        fd.write("  Number of sectors in partition: %u\n" % self.sectors_in_partition)

class Partition:
    """Storage for the binary image of a complete partition"""
    def __init__(self, mapped_file, partition_info):
        self._mmap = mapped_file
        self.partition_info = partition_info
        start_byte = 512*partition_info.lba_first_sector
        end_byte   = start_byte + 512*partition_info.sectors_in_partition
        self.start_byte = start_byte

    def __getitem__(self, key):
        if type(key)==slice:
            return self._mmap[ self.start_byte + key.start : self.start_byte + key.stop ]
        else:
            return self._mmap[ self.start_byte + key ]

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

class UnknownFileSystem:
    def __init__(self, message):
        self.message = message

    def __str__(self):
        return self.message

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
        return Partition(self._mmap, pi)

    def get_filesystem(self, partition_number):
        pi = self.get_partition_info(partition_number)
        if pi.type==6:
            from fat16 import FAT16Filesystem
            return FAT16Filesystem( self.get_partition(partition_number) )
        elif pi.type==0x83:
            # TODO 0x83 is official not always just Ext2, need a cleverer detection
            from ext2 import Ext2Filesystem
            return Ext2Filesystem( self.get_partition(partition_number) )
        else:
            raise UnknownFileSystem("No filesystem implementation for type %x" % pi.type)
        
        

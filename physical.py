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

    def get_record_entry(self):
        record = "%c%s%c%s%s%s" % (
            chr(self.bootable),
            chs2str(self.chs_first_sector),
            chr(self.type),
            chs2str(self.chs_last_sector),
            dword2str(self.lba_first_sector),
            dword2str(self.sectors_in_partition))
        return record

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
    def __init__(self, image, partition_info):
        self._image = image
        self.partition_info = partition_info
        start_byte = 512*partition_info.lba_first_sector
        end_byte   = start_byte + 512*partition_info.sectors_in_partition
        self.start_byte = start_byte

    def __getitem__(self, key):
        if type(key)==slice:
            return self._image[ self.start_byte + key.start : self.start_byte + key.stop ]
        else:
            return self._image[ self.start_byte + key ]

#####################################################################################################

import sys
if sys.version_info[0]>=3:
    def string2byte(s):
        return bytes( map(ord, s) )
    def byte2string(b):
        return b.decode()
else:
    def string2byte(s):
        return s
    def byte2string(b):
        return b

class DiskImage:
    def __init__(self, file_name, mode="r"):
        # TODO: handle creation of image on mode=="w"
        if not mode in ["r", "a"]:
            raise ValueError("mode string must be one of 'r', 'a', not '%s'" % mode)
        import mmap
        self._image = open(file_name, mode+"+b")
        mmap_access = { "r" : mmap.ACCESS_READ, "a" : mmap.ACCESS_WRITE }[mode]
        self._mmap = mmap.mmap(self._image.fileno(), 0, access=mmap_access)

    def __getitem__(self, index):
        return byte2string(self._mmap.__getitem__(index))

    def __setitem__(self, index, value):
        self._mmap.__setitem__(index, string2byte(value))

#####################################################################################################

class UnknownFileSystem:
    def __init__(self, message):
        self.message = message

    def __str__(self):
        return self.message

class Harddisk:
    def __init__(self, image):
        self._image = image
        self._parse_partition_table()

    def _parse_partition_table(self):
        mbr = self._image[0:512]

        self.partition_records = [ mbr[446 + i*16: 446 + (i+1)*16] for i in range(4) ]
        self._disk_signature = char2dword( mbr[440:444] )
        self._mbr_signature  = char2word( mbr[510:512] )

    def dump(self, fd=sys.stdout):
        fd.write("Disk signature: %X\n" % self._disk_signature)
        fd.write("MBR signature: %X\n" % self._mbr_signature)

    def update_image(self, disk_signature = None):
        """Update the disk image file with the current partition records and an
        optionally given disk_signature"""
        if not disk_signature:
            disk_signature = self._disk_signature
        self._image[440:444] = dword2str( disk_signature )
        self._image[510:512] = word2str( 0xaa55 )
        for i in range(4):
            self._image[446+i*16 : 446+(i+1)*16] = self.partition_records[i]

    def get_partition_info(self, partition_number):
        return PartitionInfo( self.partition_records[partition_number] )

    def set_partition_info(self, partition_number, partition_info):
        self.partition_records[partition_number] = partition_info.get_record_entry()

    def get_partition(self, partition_number):
        pi = self.get_partition_info(partition_number)
        return Partition(self._image, pi)

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

#--------------------------------------------------------------------------------------------
class VolumeDescriptor:
    def __init__(self, entry):
        self.type = ord(entry[0])
        self.standard_id = entry[1:6]
        self.version = ord(entry[6])
    
    def dump(self, fd=sys.stdout):
        fd.write("  type = %u\n" % self.type)
        fd.write("  std_id = %s\n" % self.standard_id)
        fd.write("  version = %u\n" % self.version)

class NAryVolumeDescriptor(VolumeDescriptor):
    def __init__(self, entry):
        VolumeDescriptor.__init__(self, entry)
        self.system_identifier = entry[8:40]
        self.volume_identifier = entry[40:72]
        self.space_size = char2dword(entry[80:84])
        # ...
        self.logical_block_size = char2word(entry[128:130])
        # ...
        self.set_identifier = entry[190:318]
        self.publisher_identifier = entry[318:446]
        self.data_preparer_identifier = entry[446:574]
        self.application_identifier = entry[574:702]
        self.copyright_file_identifier = entry[702:739]

    def dump(self, fd=sys.stdout):
        if self.type==1:
            fd.write("Primary Volume Descriptor\n")
        else:
            fd.write("Secondary Volume Descriptor\n")
        VolumeDescriptor.dump(self, fd)
        fd.write("  system id = %s\n" % self.system_identifier)
        fd.write("  volume id = %s\n" % self.volume_identifier)
        fd.write("  space size = %u\n" % self.space_size)
        # ...
        fd.write("  logical block size = %u\n" % self.logical_block_size)
        # ...
        fd.write("  set identifier = %s\n" % self.set_identifier)
        fd.write("  publisher identifier = %s\n" % self.publisher_identifier)
        fd.write("  data preparer identifier = %s\n" % self.data_preparer_identifier)
        fd.write("  application identifier = %s\n" % self.application_identifier)
        fd.write("  copyright file identifier = %s\n" % self.copyright_file_identifier)

class VolumeDescriptorSetTerminator(VolumeDescriptor):
    def __init__(self, entry):
        VolumeDescriptor.__init__(self, entry)

    def dump(self, fd=sys.stdout):
        fd.write("!!! Volume Descriptor Set Terminator !!!\n")
        VolumeDescriptor.dump(self, fd)

def parseVolumeDescriptor(entry):
    if ord(entry[0]) in [1, 2]:
        return NAryVolumeDescriptor(entry)
    elif ord(entry[0])==255:
        return VolumeDescriptorSetTerminator(entry)
    else:
        return VolumeDescriptor(entry)
        
class CdRom:
    def __init__(self, image):
        self._image = image
        self._parse_volume_descriptors()

    def _parse_volume_descriptors(self):
        offset = 32768
        self._volumedescriptors = []
        vd = parseVolumeDescriptor(self._image[offset:offset+2048])
        vd.dump()
        while not isinstance(vd, VolumeDescriptorSetTerminator):
            self._volumedescriptors.append( vd )
            offset += 2048
            vd = parseVolumeDescriptor(self._image[offset:offset+2048])
            vd.dump()

        

import os
import sys
import mmap
from pyvirtualfs.tools import *
from pyvirtualfs.iso9660 import *
from pyvirtualfs.fat16 import FAT16Filesystem
from pyvirtualfs.ext2 import Ext2Filesystem
from pyvirtualfs.image_path import ImagePath


class PartitionInfo:
    """Class to collect the information of a partition entry"""
    def __init__(self, entry):
        self.bootable             = entry[0]
        self.type                 = entry[4]
        self.chs_first_sector     = list2chs(entry[1:4])
        self.chs_last_sector      = list2chs(entry[5:8])
        self.lba_first_sector     = list2dword(entry[8:12])
        self.sectors_in_partition = list2dword(entry[12:16])

    def get_record_entry(self):
        record = [self.bootable] + \
            chs2list(self.chs_first_sector) + \
            [self.type] + \
            chs2list(self.chs_last_sector) + \
            dword2list(self.lba_first_sector) + \
            dword2list(self.sectors_in_partition)
        return record

    def dump(self, fd=sys.stdout, level=1):
        if self.bootable == 0x80:
            fd.write("  bootable\n")
        elif self.bootable == 0x0:
            fd.write("  non bootable\n")
        else:
            fd.write("  invalid\n")
        fd.write("  CHS of first absolute sector (%u, %u, %u)\n" %
                 self.chs_first_sector)
        fd.write("  Type: %x\n" % self.type)
        fd.write("  CHS of last absolute sector (%u, %u, %u)\n" %
                 self.chs_last_sector)
        fd.write("  LBA of first absolute sector n partition: %u\n" %
                 self.lba_first_sector)
        fd.write("  Number of sectors in partition: %u\n" %
                 self.sectors_in_partition)


class Partition:
    """Storage for the binary image of a complete partition"""
    def __init__(self, image, partition_info):
        self._image = image
        self.partition_info = partition_info
        start_byte = 512*partition_info.lba_first_sector
        end_byte   = start_byte + 512*partition_info.sectors_in_partition
        self.start_byte = start_byte

    def __getitem__(self, key):
        if type(key) == slice:
            return self._image[self.start_byte + key.start:
                               self.start_byte + key.stop]
        else:
            return self._image[self.start_byte + key]

    def __setitem__(self, key, value):
        if type(key) == slice:
            self._image[self.start_byte + key.start:
                        self.start_byte + key.stop] = value
        else:
            self._image[self.start_byte + key] = value

    def __len__(self):
        return 512*self.partition_info.sectors_in_partition

##############################################################################

if sys.version_info[0] >= 3:
    def mmap2intlist(m):
        return list(map(lambda x: x, m))

    def intlist2mmap(l):
        return bytes(l)

    def mmap2int(value):
        return value

    def int2mmap(value):
        return value
else:
    def mmap2intlist(m):
        return map(ord, m)

    def intlist2mmap(l):
        return "".join(map(chr, l))

    def mmap2int(value):
        return ord(value)

    def int2mmap(value):
        return chr(value)


class DiskImage:
    def __init__(self, file_name, mode="r"):
        # TODO: handle creation of image on mode=="w"
        if not mode in ["r", "a"]:
            raise ValueError(
                "mode string must be one of 'r', 'a', not '%s'" % mode)
        self._image = open(file_name, mode+"+b")
        mmap_access = {"r": mmap.ACCESS_READ, "a": mmap.ACCESS_WRITE}[mode]
        self._mmap = mmap.mmap(self._image.fileno(), 0, access=mmap_access)

    def __getitem__(self, index):
        data = self._mmap.__getitem__(index)
        if type(data) == slice:
            return mmap2intlist(data)
        else:
            return mmap2int(data)

    def __setitem__(self, index, value):
        if type(value) == list:
            self._mmap.__setitem__(index, intlist2mmap(value))
        else:
            self._mmap.__setitem__(index, mmap2int(value))

##############################################################################


class UnknownFileSystem(BaseException):
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

        self.partition_records = [mbr[446 + i*16:446 + (i+1)*16]
                                  for i in range(4)]
        self._disk_signature = list2dword(mbr[440:444])
        self._mbr_signature  = list2word(mbr[510:512])

    def dump(self, fd=sys.stdout, level=1):
        fd.write("Disk signature: %X\n" % self._disk_signature)
        fd.write("MBR signature: %X\n" % self._mbr_signature)

        # TODO: take the amount of partitions from the actual image
        for i in range(4):
            pi = self.get_partition_info(i)
            print("***** Partition %u *****" % i)
            pi.dump()

            if level >= 2:
                try:
                    fs = self.get_filesystem(i)
                    fs.dump()
                except UnknownFileSystem:
                    pass

    def update_image(self, disk_signature=None):
        """Update the disk image file with the current partition records and an
        optionally given disk_signature"""
        if not disk_signature:
            disk_signature = self._disk_signature
        self._image[440:444] = dword2list(disk_signature)
        self._image[510:512] = word2list(0xaa55)
        for i in range(4):
            self._image[446+i*16:446+(i+1)*16] = self.partition_records[i]

    def get_partition_info(self, partition_number):
        return PartitionInfo(self.partition_records[partition_number])

    def set_partition_info(self, partition_number, partition_info):
        self.partition_records[partition_number] = \
            partition_info.get_record_entry()

    def get_partition(self, partition_number):
        pi = self.get_partition_info(partition_number)
        return Partition(self._image, pi)

    def get_filesystem(self, partition_number):
        # TODO: get_filesystem should be available for all physical disks
        # created by createPhysicalImageFromImageType --> make an interface
        pi = self.get_partition_info(partition_number)
        if pi.type == 6:
            return FAT16Filesystem(self.get_partition(partition_number))
        elif pi.type == 0x83:
            # TODO 0x83 is official not always just Ext2, need a cleverer
            # detection
            return Ext2Filesystem(self.get_partition(partition_number))
        else:
            raise UnknownFileSystem(
                "No filesystem implementation for type %x" % pi.type)

#-----------------------------------------------------------------------------


class VolumeDescriptor:
    def __init__(self, entry):
        self.type = entry[0]
        self.standard_id = entry[1:6]
        self.version = entry[6]

    def dump(self, fd=sys.stdout, level=1):
        fd.write("  type = %u\n" % self.type)
        fd.write("  std_id = %s\n" % self.standard_id)
        fd.write("  version = %u\n" % self.version)


class NAryVolumeDescriptor(VolumeDescriptor):
    def __init__(self, entry):
        VolumeDescriptor.__init__(self, entry)
        self.system_identifier = entry[8:40]
        self.volume_identifier = entry[40:72]
        self.space_size = list2dword(entry[80:84])
        # ...
        self.logical_block_size = list2word(entry[128:130])
        # ...
        self.set_identifier = entry[190:318]
        self.publisher_identifier = entry[318:446]
        self.data_preparer_identifier = entry[446:574]
        self.application_identifier = entry[574:702]
        self.copyright_file_identifier = entry[702:739]

    def dump(self, fd=sys.stdout, level=1):
        if self.type == 1:
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
        fd.write("  data preparer identifier = %s\n" %
                 self.data_preparer_identifier)
        fd.write("  application identifier = %s\n" %
                 self.application_identifier)
        fd.write("  copyright file identifier = %s\n" %
                 self.copyright_file_identifier)


class VolumeDescriptorSetTerminator(VolumeDescriptor):
    def __init__(self, entry):
        VolumeDescriptor.__init__(self, entry)

    def dump(self, fd=sys.stdout, level=1):
        fd.write("!!! Volume Descriptor Set Terminator !!!\n")
        VolumeDescriptor.dump(self, fd)


def parseVolumeDescriptor(entry):
    if entry[0] in [1, 2]:
        return NAryVolumeDescriptor(entry)
    elif entry[0] == ISO9660_DESCRIPTOR_TYPE_TERMINATOR:
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
            self._volumedescriptors.append(vd)
            offset += 2048
            vd = parseVolumeDescriptor(self._image[offset:offset+2048])
            vd.dump()


def createPhysicalImageFromImageType(imagetype, image):
    """Create a physical representation of the given disk image based on the
    indicated imagetype. For example from image type 'hd' a Harddisk object is
    created."""
    if imagetype == ImagePath.IMAGE_TYPE_HD:
        return Harddisk(image)
    elif imagetype == ImagePath.IMAGE_TYPE_CDROM:
        return CdRom(image)
    raise UnknownFileSystem("Image type %s is not supported" % imagetype)

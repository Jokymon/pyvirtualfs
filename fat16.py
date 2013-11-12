import filesystem
import os, sys
from tools import *
import structures

FAT16_CLUSTER_FREE = 0x0
FAT16_CLUSTER_RESERVED = 0x1
FAT16_CLUSTER_HIGHEST = 0xffef
FAT16_CLUSTER_BADSECTOR = 0xfff6
FAT16_CLUSTER_END_OF_CHAIN = 0xfff8

#####################################################################################################
# FAT16 specific data structures

class FAT16Structure(structures.StructTemplate):
    jump_code = structures.RawField(0, 3)
    oem_name  = structures.StringField(3, 8)
    bytes_per_sector        = structures.UInt16Field(11)
    sectors_per_cluster     = structures.UInt8Field(13)
    reserved_sectors        = structures.UInt16Field(14)
    number_of_fats          = structures.UInt8Field(16)
    max_root_dir_entries    = structures.UInt16Field(17)
    sectors_per_fat         = structures.UInt16Field(22)

class FAT16DirectoryEntry(structures.StructTemplate):
    file_name       = structures.StringField(0, 8)
    file_extension  = structures.StringField(8, 3)
    file_attributes = structures.UInt8Field(11)
    create_time     = structures.UInt16Field(14)
    create_date     = structures.UInt16Field(16)

    modified_time   = structures.UInt16Field(22)
    modified_date   = structures.UInt16Field(24)
    start_cluster   = structures.UInt16Field(26)
    file_size       = structures.UInt32Field(28)

#####################################################################################################
# Implementation of the FAT16 specific classes

class FAT16FileInfo(filesystem.FileInfo):
    def __init__(self):
        filesystem.FileInfo.__init__(self)

    def parse_entry(self, fat16, fat16_entry):
        # We need a reference to the FAT16 to calculate the location of the
        # file inside the partition
        basename = list2string(fat16_entry[0:8])
        suffix = list2string(fat16_entry[8:11])
        self.filename = "%s.%s" % ( basename, suffix )
        attributes = fat16_entry[11]
        if attributes & 0x1:
            self.attributes.append("read_only")
        if attributes & 0x2:
            self.attributes.append("hidden")
        if attributes & 0x4:
            self.attributes.append("system")
        if attributes & 0x10:
            self.attributes.append("directory")
        if attributes & 0x20:
            self.attributes.append("archive")
        # determine the start byte of this file entry
        self.start_cluster = list2word(fat16_entry[26:28]) 
        self.start_byte = (self.start_cluster-2) * fat16.info.sectors_per_cluster * 512
        self.start_byte += fat16.start_of_data

        self.size = list2dword(fat16_entry[28:32])

class FAT16FileHandle(filesystem.FileHandle):
    def __init__(self, fat16, fileinfo):
        filesystem.FileHandle.__init__(self)
        self._fat16 = fat16
        self._fileinfo = fileinfo
        # collect the clusters for this file
        self._clusters = []
        cl = self._fileinfo.start_cluster
        while cl>=2 and cl<=FAT16_CLUSTER_HIGHEST:
            self._clusters.append(cl)
            cl = self._fat16.get_fat_entry(0, cl)

    def close(self):
        pass

    def read(self, size=None):
        if size==None:
            size = self._fileinfo.size

        fat16 = self._fat16
        data = ""
        pos_in_cluster = self._currentpos % (fat16.info.sectors_per_cluster*512)
        cluster_index = int(self._currentpos / (fat16.info.sectors_per_cluster*512))
        # TODO: also add an upper bound for the actual size of the file
        # Here we only read as much data until the boundary of the current cluster
        readsize = min( fat16.info.sectors_per_cluster*512 - pos_in_cluster, size )
        while readsize != 0:
            start_byte = fat16.get_start_byte_from_cluster( self._clusters[cluster_index] )
            data += list2string(fat16.partition[ start_byte : start_byte + readsize ])

            # update the current position
            self._currentpos += readsize
            pos_in_cluster = self._currentpos % (fat16.info.sectors_per_cluster*512)
            cluster_index = self._currentpos / (fat16.info.sectors_per_cluster*512)
            # calculate the next chunk
            size -= readsize
            readsize = min( fat16.info.sectors_per_cluster*512 - pos_in_cluster, size )

        return data

    def seek(offset, whence=os.SEEK_SET):
        pass

    def write(self, s):
        pass

class FAT16Filesystem:
    def __init__(self, partition):
        self.partition = partition

        self.info = FAT16Structure(self.partition, 0)

        # calculate the byte address of cluster 2
        self.start_of_data = self.get_root_directory_address() + self.info.max_root_dir_entries * len(FAT16DirectoryEntry)

        self.root_entries = {}
        root_directory_start = self.get_root_directory_address()
        i = 0
        fi = FAT16FileInfo()
        fi.parse_entry(self, self.partition[root_directory_start + i*32 : root_directory_start + (i+1)*32])
        while fi.filename[0] != '\0':
            self.root_entries[fi.filename] = fi
            i += 1
            fi = FAT16FileInfo()
            fi.parse_entry(self, self.partition[root_directory_start + i*32 : root_directory_start + (i+1)*32])

    def dump(self, fd=sys.stdout):
        fd.write("Content of the FAT:\n")

        fd.write("OEM Name: %s\n" % self.info.oem_name)
        fd.write("Bytes per sector: %u\n" % self.info.bytes_per_sector)
        fd.write("Sectors per cluster: %u\n" % self.info.sectors_per_cluster)
        fd.write("Reserved sectors: %u\n" % self.info.reserved_sectors)
        fd.write("Number of FATs: %u\n" % self.info.number_of_fats)
        fd.write("Sectors per FAT: %u\n" % self.info.sectors_per_fat)
        fd.write("Maximum number of root directory entries: %u\n" % self.info.max_root_dir_entries)
        fd.write("Start byte of data: %u\n" % self.start_of_data)

        fd.write("Files: %s\n" % self._listdir( self.get_root_directory_address() ))

    def get_root_directory_address(self):
        """Returns the starting byte for the root directory inside the
        partition containing this file system"""
        root_address = self.info.bytes_per_sector * self.info.reserved_sectors
        root_address += self.info.number_of_fats * self.info.sectors_per_fat * self.info.bytes_per_sector
        return root_address

    def get_fat_entry(self, fat_no = 0, fat_entry = 0):
        fat_start = self.info.bytes_per_sector * self.info.reserved_sectors
        return list2word( self.partition[ fat_start + fat_entry*2: fat_start+fat_entry*2 + 2 ] )

    def get_start_byte_from_cluster(self, cluster):
        """calculate the start byte of the given cluster number inside the
        partition containing this file system"""
        start_byte = self.start_of_data
        start_byte += (cluster-2) * self.info.sectors_per_cluster * self.info.bytes_per_sector
        return start_byte

    def get_cluster_pos(self, file_position):
        """Convert a position within a file into a tuple consisting of a
        cluster number and a position within that cluster"""
        cluster_index = file_position // (self.info.sectors_per_cluster * self.info.bytes_per_sector)
        pos_in_cluster = file_position % (self.info.sectors_per_cluster * self.info.bytes_per_sector)
        return (cluster_index, pos_in_cluster)

    def listdir(self, directory):
        pass

    def _listdir(self, start_address):
        """Return a list of all files in the directory table starting at
        start_address inside this file system"""
        entries = []

        address = start_address
        entry = FAT16DirectoryEntry(self.partition, address)
        while entry.file_name[0] != '\0':
            if entry.file_name[0] != '\x2e' and (entry.file_attributes & 0x8) != 0x8:
                entries.append( "%s.%s" % (entry.file_name.strip(), entry.file_extension.strip()) )
            address += len(FAT16DirectoryEntry)
            entry = FAT16DirectoryEntry(self.partition, address)
        return entries

    def format(self, oem_name="", bytes_per_sector = 512,
               sectors_per_cluster=4, reserved_sectors=2, number_of_fats=1,
               sectors_per_fat=8):
        self.info.jump_code[0:3] = [0xEB, 0x3C, 0x90]
        self.info.oem_name = oem_name
        self.info.bytes_per_sector = bytes_per_sector
        self.info.sectors_per_cluster = sectors_per_cluster
        self.info.reserved_sectors = reserved_sectors
        self.info.number_of_fats = number_of_fats
        self.info.sectors_per_fat = sectors_per_fat

    def open(self, fname, mode="r"):
        path_elements = fname.split("/")
        dirs = self.root_entries
        for dname in path_elements[:-1]:
            if dname in dirs.keys():
                # open dir
                raise IOError("Subdirectories not yet implemented")
            else:
                raise IOError("No such file or directory: '%s'" % fname)
        if path_elements[-1] in dirs.keys():
            # open the file and return a file handle
            return FAT16FileHandle(self, dirs[path_elements[-1]])
        else:
            raise IOError("No such file or directory: '%s'" % fname)



import filesystem
import os, sys
from tools import *

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
        self.start_byte = (self.start_cluster-2) * fat16.sectors_per_cluster * 512
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
        while cl>=2 and cl<=0xffef:
            self._clusters.append(cl)
            cl = self._fat16.get_fat_entry(0, cl)

    def close(self):
        pass

    def read(self, size=None):
        if size==None:
            size = self._fileinfo.size

        fat16 = self._fat16
        data = ""
        pos_in_cluster = self._currentpos % (fat16.sectors_per_cluster*512)
        cluster_index = self._currentpos / (fat16.sectors_per_cluster*512)
        # TODO: also add an upper bound for the actual size of the file
        # Here we only read as much data until the boundary of the current cluster
        readsize = min( fat16.sectors_per_cluster*512 - pos_in_cluster, size )
        while readsize != 0:
            start_byte = (self._clusters[cluster_index]-2) * fat16.sectors_per_cluster * 512
            start_byte += fat16.start_of_data
            data += fat16[ start_byte : start_byte + readsize ]

            # update the current position
            self._currentpos += readsize
            pos_in_cluster = self._currentpos % (fat16.sectors_per_cluster*512)
            cluster_index = self._currentpos / (fat16.sectors_per_cluster*512)
            # calculate the next chunk
            size -= readsize
            readsize = min( fat16.sectors_per_cluster*512 - pos_in_cluster, size )

        return data

    def seek(offset, whence=os.SEEK_SET):
        pass

    def write(self, s):
        pass
    
class FAT16Filesystem:
    def __init__(self, partition):
        self.partition = partition

        self.oem_name             = self.partition[3:11]
        self.bytes_per_sector     = list2word(self.partition[11:13])
        self.sectors_per_cluster  = self.partition[13]
        self.reserved_sectors     = list2word(self.partition[14:16])
        self.number_of_fats       = self.partition[16]
        self.max_root_dir_entries = list2word(self.partition[17:19])
        self.sectors_per_fat      = list2word(self.partition[22:24])

        # calculate the byte address of cluster 2
        self.start_of_data = 512 * (self.number_of_fats*self.sectors_per_fat + 1 ) # root directory start
        self.start_of_data += self.max_root_dir_entries*32 # add size of root directory

        self.root_entries = {}
        root_directory_start = 512 * ( self.number_of_fats*self.sectors_per_fat+1 )
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

        fd.write("OEM Name: %s\n" % self.oem_name)
        fd.write("Bytes per sector: %u\n" % self.bytes_per_sector)
        fd.write("Sectors per cluster: %u\n" % self.sectors_per_cluster)
        fd.write("Reserved sectors: %u\n" % self.reserved_sectors)
        fd.write("Number of FATs: %u\n" % self.number_of_fats)
        fd.write("Sectors per FAT: %u\n" % self.sectors_per_fat)
        fd.write("Maximum number of root directory entries: %u\n" % self.max_root_dir_entries)
        fd.write("Start byte of data: %u\n" % self.start_of_data)

    def get_fat_entry(self, fat_no = 0, fat_entry = 0):
        fat_start = 512*self.reserved_sectors + fat_no*(512*self.sectors_per_fat)
        return list2word( self.partition[ fat_start + 2*fat_entry : fat_start + 2*fat_entry + 2] )

    def listdir(self, directory):
        pass

    def open(self, fname, mode="r"):
        path_elements = fname.split("/")
        dirs = self.root_entries
        for dname in path_elements[:-1]:
            if dname in dirs.keys():
                # open dir
                raise "Subdirectories not yet implemented"
            else:
                raise IOError("No such file or directory: '%s'" % fname)
        if path_elements[-1] in dirs.keys():
            # open the file and return a file handle
            return FAT16FileHandle(self, dirs[path_elements[-1]])
        else:
            raise IOError("No such file or directory: '%s'" % fname)



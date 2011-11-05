def char2word(s):
    return ord(s[0]) + (ord(s[1])<<8)

def char2dword(s):
    return ord(s[0]) + (ord(s[1])<<8) + (ord(s[2])<<16) + (ord(s[3])<<24)

def char2chs(s):
    head = ord(s[0])
    sector = ord(s[1]) & 0x3f
    cylinder = ord(s[2]) + (( ord(s[1]) & 0xc0 ) << 2)
    return (cylinder, head, sector)

def chs2lba(c, h, s, hpc, spt):
    """Convert a CHS address to LBA where c, h, s are the cylinder, h the head,
    s the sector. hpc is the heads per cylinder, spt is sectors per track"""
    return ((c * hpc) + h) * spt + s-1

#####################################################################################################
import os

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
# Implementation of the FAT16 specific classes

class FAT16FileInfo(FileInfo):
    def __init__(self):
        FileInfo.__init__(self)

    def parse_entry(self, fat16, fat16_entry):
        # We need a reference to the FAT16 to calculate the location of the
        # file inside the partition
        self.filename = "%s.%s" % ( fat16_entry[0:8].strip(), fat16_entry[8:11] )
        attributes = ord(fat16_entry[11])
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
        self.start_cluster = char2word(fat16_entry[26:28]) 
        self.start_byte = (self.start_cluster-2) * fat16.sectors_per_cluster * 512
        self.start_byte += fat16.start_of_data

        self.size = char2dword(fat16_entry[28:32])

class FAT16FileHandle(FileHandle):
    def __init__(self, fat16, fileinfo):
        FileHandle.__init__(self)
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
            data += fat16.partition[ start_byte : start_byte + readsize ]

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
    
class FAT16Partition(Partition):
    def __init__(self, image_fd, partition_info):
        Partition.__init__(self, image_fd, partition_info)

        self.oem_name             = self.partition[3:11]
        self.bytes_per_sector     = char2word(self.partition[11:13])
        self.sectors_per_cluster  = ord(self.partition[13])
        self.reserved_sectors     = char2word(self.partition[14:16])
        self.number_of_fats       = ord(self.partition[16])
        self.max_root_dir_entries = char2word(self.partition[17:19])
        self.sectors_per_fat      = char2word(self.partition[22:24])

        # calculate the byte address of cluster 2
        self.start_of_data = 512 * (self.number_of_fats*self.sectors_per_fat + 1 ) # root directory start
        self.start_of_data += self.max_root_dir_entries*32 # add size of root directory

        self.root_entries = {}
        root_directory_start = 512 * ( self.number_of_fats*self.sectors_per_fat+1 )
        i = 0
        fi = FAT16FileInfo()
        fi.parse_entry(self, self.partition[root_directory_start + i*32 : root_directory_start + (i+1)*32])
        while ord(fi.filename[0]) != 0:
            self.root_entries[fi.filename] = fi
            i += 1
            fi = FAT16FileInfo()
            fi.parse_entry(self, self.partition[root_directory_start + i*32 : root_directory_start + (i+1)*32])

    def get_fat_entry(self, fat_no = 0, fat_entry = 0):
        fat_start = 512*self.reserved_sectors + fat_no*(512*self.sectors_per_fat)
        return char2word( self.partition[ fat_start + 2*fat_entry : fat_start + 2*fat_entry + 2] )

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

        self.partitions = [ mbr[446 + i*16: 446 + (i+1)*16] for i in range(4) ]
        self.disk_signature = char2dword( mbr[440:444] )
        self.mbr_signature  = char2word( mbr[510:512] )

    def get_partition_info(self, partition_number):
        return PartitionInfo( self.partitions[partition_number] )

    def get_partition(self, partition_number):
        pi = self.get_partition_info(partition_number)
        if pi.type==6:
            return FAT16Partition(self._image, pi)
        else:
            return Partition(self._image, pi)
        

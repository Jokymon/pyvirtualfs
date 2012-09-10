import sys
from tools import *

class Ext2Filesystem:
    def __init__(self, partition):
        self.partition = partition

        self.s_inodes_count = list2dword(self.partition[1024:1028])
        self.s_blocks_count = list2dword(self.partition[1028:1032])

    def dump(self, fd=sys.stdout):
        fd.write("Number of INodes: %u\n" % self.s_inodes_count)
        fd.write("Number of Blocks: %u\n" % self.s_blocks_count)



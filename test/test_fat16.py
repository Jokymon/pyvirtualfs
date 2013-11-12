import pytest
from fat16 import *

class TestFat16Filesystem:
    def testClusterPosition_0(self):
        fat = FAT16Filesystem(1024 * [0])
        fat.format()
        (cluster, position) = fat.get_cluster_pos(0)
        assert cluster == 0
        assert position == 0

    def testClusterPosition_start_of_cluster1(self):
        fat = FAT16Filesystem(1024 * [0])
        fat.format()
        (cluster, position) = fat.get_cluster_pos(2048)
        assert cluster == 1
        assert position == 0

    def testClusterPosition_somewhere_in_cluster2(self):
        fat = FAT16Filesystem(1024 * [0])
        fat.format()
        (cluster, position) = fat.get_cluster_pos(4500)
        assert cluster == 2
        assert position == 404

    def testClusterPosition_start_of_cluster1_bigger_sectors(self):
        fat = FAT16Filesystem(1024 * [0])
        fat.format(bytes_per_sector = 1024)
        (cluster, position) = fat.get_cluster_pos(4096)
        assert cluster == 1
        assert position == 0

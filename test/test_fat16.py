import pytest
from fat16 import *


@pytest.fixture
def formatted_partition():
    fat = FAT16Filesystem(1024*1024 * [0])
    fat.format()
    return fat


class TestFat16Filesystem:
    def testClusterPosition_0(self, formatted_partition):
        (cluster, position) = formatted_partition.get_cluster_pos(0)
        assert cluster == 0
        assert position == 0

    def testClusterPosition_start_of_cluster1(self, formatted_partition):
        (cluster, position) = formatted_partition.get_cluster_pos(2048)
        assert cluster == 1
        assert position == 0

    def testClusterPosition_somewhere_in_cluster2(self, formatted_partition):
        (cluster, position) = formatted_partition.get_cluster_pos(4500)
        assert cluster == 2
        assert position == 404

    def testClusterPosition_start_of_cluster1_bigger_sectors(self):
        fat = FAT16Filesystem(1024 * [0])
        fat.format(bytes_per_sector=1024)
        (cluster, position) = fat.get_cluster_pos(4096)
        assert cluster == 1
        assert position == 0

    def testAllocatingCluster(self, formatted_partition):
        cluster = formatted_partition._allocate_cluster()
        assert cluster != 0
        assert formatted_partition.get_fat_entry(2) != 0


class TestFileSystemAPI:
    def testOpenForReadMissingFile(self, formatted_partition):
        assert formatted_partition.listdir("/") == []
        pytest.raises(IOError, formatted_partition.open, "somefile.txt", "r")

    def testCreateNewFile(self, formatted_partition):
        handle = formatted_partition.open("somefile.txt", "w")
        assert formatted_partition.listdir("/") == ["SOMEFILE.TXT"]

    def testOpenForReadExistingFile(self, formatted_partition):
        handle = formatted_partition.open("somefile.txt", "w")
        handle.close()

        handle = formatted_partition.open("somefile.txt", "r")
        assert handle is not None

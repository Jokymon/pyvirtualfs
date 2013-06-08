import pytest
import structures
from physical import DiskImage

class StructureUnderTest(structures.StructTemplate):
    a_byte = structures.UInt8Field(0)
    a_word = structures.UInt16Field(1)
    a_string = structures.StringField(3, 10)

@pytest.fixture
def mmaped_file(tmpdir):
    import mmap, os
    f = open( str(tmpdir.join("mmapfile.bin")), "wb" )
    f.seek(20, os.SEEK_SET)
    f.write("\0".encode("utf-8"))
    f.close()

    image = DiskImage( str(tmpdir.join("mmapfile.bin")), "a" )
    return image

class TestStructuresWithMmap:
    def test_structure_with_diskimage(self, mmaped_file):
        struct = StructureUnderTest(mmaped_file, 0)

        struct.a_byte = 42
        struct.a_word = 0x1234
        struct.a_string = "test"

        assert mmaped_file[0] == 42
        assert mmaped_file[1] == 0x34
        assert mmaped_file[2] == 0x12
        assert chr(mmaped_file[3]) == 't'
        assert chr(mmaped_file[4]) == 'e'
        assert chr(mmaped_file[5]) == 's'
        assert chr(mmaped_file[6]) == 't'

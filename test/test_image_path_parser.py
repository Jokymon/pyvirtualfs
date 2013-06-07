import pytest
import image_path

class TestImagePathParser:
    def testValidFullPath(self):
        path_string = "image://imagefile.img:hd/partition0/directory/somefile.dat"
 
        path = image_path.ImagePath.parse(path_string)
 
        assert path.imagefile == "imagefile.img"
        assert path.imagetype == image_path.ImagePath.IMAGE_TYPE_HD
        assert path.partition == 0
        assert path.filepath  == "/directory/somefile.dat"
 
    def testEmptyPath(self):
        path_string = "image://imagefile.img:hd"
 
        path = image_path.ImagePath.parse(path_string)
 
        assert path.imagefile == "imagefile.img"
        assert path.imagetype == image_path.ImagePath.IMAGE_TYPE_HD
        assert path.partition == None
        assert path.filepath  == "/"
 
    def testValidPathWithoutPartition(self):
        path_string = "image://imagefile.img:hd/directory/somefile.dat"
 
        path = image_path.ImagePath.parse(path_string)
 
        assert path.imagefile == "imagefile.img"
        assert path.imagetype == image_path.ImagePath.IMAGE_TYPE_HD
        assert path.partition == None
        assert path.filepath  == "/directory/somefile.dat"
 
    def testFloppyDiskImage(self):
        path_string = "image://imagefile.img:fd/directory/somefile.dat"
 
        path = image_path.ImagePath.parse(path_string)
 
        assert path.imagefile == "imagefile.img"
        assert path.imagetype == image_path.ImagePath.IMAGE_TYPE_FD
        assert path.partition == None
        assert path.filepath  == "/directory/somefile.dat"

    def testCdromImage(self):
        path_string = "image://imagefile.img:cdrom/directory/somefile.dat"
 
        path = image_path.ImagePath.parse(path_string)
 
        assert path.imagefile == "imagefile.img"
        assert path.imagetype == image_path.ImagePath.IMAGE_TYPE_CDROM
        assert path.partition == None
        assert path.filepath  == "/directory/somefile.dat"

    ################ FAILING CASES ##############################
 
    def testUnsupportedScheme(self):
        path_string = "http://imagefile.img:hd/directory/somefile.dat"
 
        pytest.raises( image_path.PathParseError, image_path.ImagePath.parse, path_string )

    def testMissingImageType(self):
        path_string = "image://imagefile.img/directory/somefile.dat"
 
        pytest.raises( image_path.PathParseError, image_path.ImagePath.parse, path_string )
        

    def testUnsupportedImageType(self):
        path_string = "image://imagefile.img:some_image_type/directory/somefile.dat"
 
        pytest.raises( image_path.PathParseError, image_path.ImagePath.parse, path_string )

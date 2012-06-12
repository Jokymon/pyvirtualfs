import image_path
import unittest

class TestImagePathParser(unittest.TestCase):
    def testValidFullPath(self):
        path_string = "image://imagefile.img:hd/partition0/directory/somefile.dat"
 
        path = image_path.ImagePath.parse(path_string)
 
        self.assert_( path.imagefile == "imagefile.img" )
        self.assert_( path.imagetype == image_path.ImagePath.IMAGE_TYPE_HD )
        self.assert_( path.partition == 0 )
        self.assert_( path.filepath  == "/directory/somefile.dat" )
 
    def testEmptyPath(self):
        path_string = "image://imagefile.img:hd"
 
        path = image_path.ImagePath.parse(path_string)
 
        self.assert_( path.imagefile == "imagefile.img" )
        self.assert_( path.imagetype == image_path.ImagePath.IMAGE_TYPE_HD )
        self.assert_( path.partition == None )
        self.assert_( path.filepath  == "/" )
 
    def testValidPathWithoutPartition(self):
        path_string = "image://imagefile.img:hd/directory/somefile.dat"
 
        path = image_path.ImagePath.parse(path_string)
 
        self.assert_( path.imagefile == "imagefile.img" )
        self.assert_( path.imagetype == image_path.ImagePath.IMAGE_TYPE_HD )
        self.assert_( path.partition == None )
        self.assert_( path.filepath  == "/directory/somefile.dat" )
 
    def testFloppyDiskImage(self):
        path_string = "image://imagefile.img:fd/directory/somefile.dat"
 
        path = image_path.ImagePath.parse(path_string)
 
        self.assert_( path.imagefile == "imagefile.img" )
        self.assert_( path.imagetype == image_path.ImagePath.IMAGE_TYPE_FD )
        self.assert_( path.partition == None )
        self.assert_( path.filepath  == "/directory/somefile.dat" )

    def testCdromImage(self):
        path_string = "image://imagefile.img:cdrom/directory/somefile.dat"
 
        path = image_path.ImagePath.parse(path_string)
 
        self.assert_( path.imagefile == "imagefile.img" )
        self.assert_( path.imagetype == image_path.ImagePath.IMAGE_TYPE_CDROM )
        self.assert_( path.partition == None )
        self.assert_( path.filepath  == "/directory/somefile.dat" )

    ################ FAILING CASES ##############################
 
    def testUnsupportedScheme(self):
        path_string = "http://imagefile.img:hd/directory/somefile.dat"
 
        self.assertRaises( image_path.PathParseError, image_path.ImagePath.parse, path_string )

    def testMissingImageType(self):
        path_string = "image://imagefile.img/directory/somefile.dat"
 
        self.assertRaises( image_path.PathParseError, image_path.ImagePath.parse, path_string )
        

    def testUnsupportedImageType(self):
        path_string = "image://imagefile.img:some_image_type/directory/somefile.dat"
 
        self.assertRaises( image_path.PathParseError, image_path.ImagePath.parse, path_string )
 
if __name__ == "__main__":
    unittest.main()

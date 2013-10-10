import pytest
import image_path
from physical import *
from iso9660 import *

class TestPhysicalFactory:
    def testInvalidImageType(self):
        pytest.raises( UnknownFileSystem,
                       createPhysicalImageFromImageType,
                       image_path.ImagePath.IMAGE_TYPE_INVALID,
                       None )

    def testCreateHarddisk(self):
        phys = createPhysicalImageFromImageType(image_path.ImagePath.IMAGE_TYPE_HD, 
                                                1024*[0])
        assert isinstance(phys, Harddisk)

    def testCreateCdrom(self):
        image = (ISO9660_DATAAREA_OFFSET + ISO9660_DESCRIPTOR_SIZE) * [0]
        image[ISO9660_DATAAREA_OFFSET] = ISO9660_DESCRIPTOR_TYPE_TERMINATOR

        phys = createPhysicalImageFromImageType(image_path.ImagePath.IMAGE_TYPE_CDROM,
                                                image)
        assert isinstance(phys, CdRom)

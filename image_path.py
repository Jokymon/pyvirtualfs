class PathParseError(Exception):
    def __init__(self, msg):
        self.msg = msg

class ImagePath:
    """An ImagePath object represents the path to a file inside an image
    file."""

    IMAGE_TYPE_HD = 1
    IMAGE_TYPE_FD = 2
    IMAGE_TYPE_CDROM = 3
    IMAGE_TYPE_INVALID = 255

    def __init__(self, imagefile, imagetype=IMAGE_TYPE_HD, partition=None, filepath="/"):
        self.imagefile = imagefile
        self.imagetype = imagetype
        self.partition = partition
        self.filepath = filepath

    def __repr__(self):
        return "Imagefile: %s, type: %u, parition: %s, filepath: %s" % \
                (self.imagefile, self.imagetype, self.partition, self.filepath)

    @staticmethod
    def parse(s):
        import sys
        if sys.version_info[0]<=2:
            from urlparse import urlparse
        else:
            from urllib.parse import urlparse as urlparse

        #if pythonversion==2:
        #    urlparse.uses_netloc.append("image")

        parsed = urlparse(s)
        if parsed.scheme!="image":
            raise PathParseError("Only URL scheme image:// is supported")

        if not ":" in parsed.netloc:
            raise PathParseError("Image type hd, fd or cdrom needed after the image file name and a ':'")

        (imagefile, imagetype) = parsed.netloc.split(":")
        path_elements = parsed.path.split("/")
        if len(path_elements)<=1:
            partition = None
            filepath = "/"
        elif path_elements[1].startswith("partition"):
            partition = int(path_elements[1][9:])
            filepath = "/".join([""] + path_elements[2:])
        else:
            partition = None
            filepath = parsed.path

        if imagetype=="hd":
            imagetype = ImagePath.IMAGE_TYPE_HD
        elif imagetype=="fd":
            imagetype = ImagePath.IMAGE_TYPE_FD
        elif imagetype=="cdrom":
            imagetype = ImagePath.IMAGE_TYPE_CDROM
        else:
            raise PathParseError("Image type %s unknown/unspported" % imagetype)

        return ImagePath( imagefile, imagetype, partition, filepath )


class PathParseError(Exception):
    def __init__(self, msg):
        self.msg = msg

class ImagePath:
    """An ImagePath object represents the path to a file inside an image
    file."""
    def __init__(self, imagefile, partition=0, filepath="/"):
        self.imagefile = imagefile
        self.partition = partition
        self.filepath = filepath

    def __repr__(self):
        return "Imagefile: %s, parition: %u, filepath: %s" % 
                (self.imagefile, self.partition, self.filepath)

    @staticmethod
    def parse(s):
        tokens = s.split("::")
        if len(tokens)<1 or len(tokens)>2:
            raise PathParseError("Invalid path")

        image_path = ImagePath( tokens.pop(0) )
        if len(tokens)!=0:
            token = tokens[0]
            # TODO: Handle empty part after ::
            if token[0]=='<':
                end_of_partition = token.find(">")
                if end_of_partition==-1:
                    raise PathParseError("Missing the closing '>' for the partition declaration")
                partition = token[1:end_of_partition]
                try:
                    partition = int(partition)
                except ValueError:
                    raise PathParseError("Partition declaration must be an  integer")
                image_path.partition = partition
                token = token[end_of_partition+1:]
            image_path.filepath = token
        return image_path


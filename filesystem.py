import os

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
    
class Filesystem:
    def open(self, fname, mode):
        pass


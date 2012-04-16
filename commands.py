class CreateCommand:
    def __init__(self, outfile, size):
        self.outfile = outfile
        self.size = size

    def execute(self):
        import os
        f = open(self.outfile, "wb")
        f.seek(self.size-1, os.SEEK_SET)
        f.write("\0".encode("utf-8"))
        f.close()

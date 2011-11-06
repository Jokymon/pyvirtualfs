from optparse import OptionParser
from physical import Harddisk

def create_empty_image(fname, size_in_bytes):
    # TODO check if the file exists
    import os
    f = open(fname, 'wb')
    f.seek(size_in_bytes-1, os.SEEK_SET)
    f.write('\0')
    f.close()

def main():
    parser = OptionParser()
    parser.add_option("-s", "--size", dest="image_size",
                      help="Size of the image in bytes or in k, M, G when giving the corresponding suffix")
    (options, args) = parser.parse_args()
    # TODO: correct parsing of the size suffices

    create_empty_image( "test.bin", int(options.image_size) )

    hd = Harddisk( "test.bin", "a" )
    
    p = hd.get_partition_info(0)
    p.type = 0x83
    p.chs_first_sector = (0, 1, 1)
    p.chs_last_sector = (10, 15, 63)
    p.lba_first_sector = 63
    p.sectors_in_partition = 11025
    hd.set_partition_info( 0, p )

    p = hd.get_partition_info(1)
    p.type = 6
    p.chs_first_sector = (11, 0, 1)
    p.chs_last_sector = (100, 15, 63)
    p.lba_first_sector = 11088
    p.sectors_in_partition = 90720
    hd.set_partition_info( 1, p )

    hd.update_image(0x337a0564)

if __name__=="__main__":
    main()

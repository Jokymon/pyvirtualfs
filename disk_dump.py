from physical import *

hpc = 16 # for the c50m.img
spt = 63 # for the c50m.img

def main():
    import sys
   
    diskimage = DiskImage(sys.argv[1], "r")
    cd = CdRom(diskimage)
    return
    #hd = Harddisk(sys.argv[1], "a")
    #hd.dump()
    
    for i in range(4):
        print "##############################################"
        print "Partition %u" % i
        hd.get_partition_info(i).dump()
        try:
            fs = hd.get_filesystem(i)
            print "----------------------------------------------"
            fs.dump()
        except UnknownFileSystem:
            pass

    #####################################################################################
    ## jump to the root directory

    #for f in fat16.root_entries.values():
    #    print "File: %14s, starts at byte %15u, size %u" % (f.filename, f.start_byte, f.size)

    #test = open("blubber.bin", "wb")
    #start = fat16.root_entries["TEST.BIN"].start_byte
    ## read one cluster
    #data = fat16.partition[start : start + (512*fat16.sectors_per_cluster)]
    #test.write(data)
    #test.close()

    #####################################################################################
    ## dump the boot sector of the first partition
    #test = open("bl_partition1.bin", "wb")
    #test.write(fat16.partition[0:512])
    #test.close()

    #####################################################################################
    ## dump parts of the FAT
    #cluster = fat16.root_entries["TEST.BIN"].start_cluster
    #next = fat16.get_fat_entry(0, cluster)
    #print "Entry of Fat idx %u: 0x%X=0d%u" % (cluster, next, next)
    #if next!=0xffff:
    #    next1 = fat16.get_fat_entry(0, next)
    #    print "Entry of Fat idx %u: 0x%X=0d%u" % (next, next1, next1)

    #f = fat16.open("TEST.BIN", "r")
    #print f._clusters
    #test = open("blubber2.bin", "wb")
    #data = f.read()
    #test.write(data)
    #test.close()

if __name__=="__main__":
    main()

from physical import *

hpc = 16 # for the c50m.img
spt = 63 # for the c50m.img

def main():
    import sys
    
    hd = Harddisk(sys.argv[1], "a")
    partitions = [ hd.get_partition_info(i) for i in range(4) ]
    
    print "Disk signature: %X" % hd.disk_signature
    print "MBR signature: %X" % hd.mbr_signature
    for i in range(4):
        print "----------------------------------------------"
        print "Partition %u" % i
        if partitions[i].bootable==0x80:
            print "  bootable"
        elif partitions[i].bootable==0x0:
            print "  non bootable"
        else:
            print "  invalid"
        print "  CHS of first absolute sector (%u, %u, %u)" % partitions[i].chs_first_sector
        print "  Type: %x" % partitions[i].type
        print "  CHS of last absolute sector (%u, %u, %u)" % partitions[i].chs_last_sector
        print "  LBA of first absolute sector n partition: %u" % partitions[i].lba_first_sector
        print "  Number of sectors in partition: %u" % partitions[i].sectors_in_partition
    
    ####################################################################################
    # jump to the Ext2
    ext2 = Ext2Partition(image, partitions[0])

    print "Number of INodes: %u" % ext2.s_inodes_count
    print "Number of Blocks: %u" % ext2.s_blocks_count

    ####################################################################################
    # jump to the FAT

    #fat16 = hd.get_partition(1)
    #
    #print ""
    #print "Content of the FAT:"
    #
    #print "OEM Name: %s" % fat16.oem_name
    #print "Bytes per sector: %u" % fat16.bytes_per_sector
    #print "Sectors per cluster: %u" % fat16.sectors_per_cluster
    #print "Reserved sectors: %u" % fat16.reserved_sectors
    #print "Number of FATs: %u" % fat16.number_of_fats
    #print "Sectors per FAT: %u" % fat16.sectors_per_fat
    #print "Maximum number of root directory entries: %u" % fat16.max_root_dir_entries
    #print "Start byte of data: %u" % fat16.start_of_data
    #
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

    
    image.close()

if __name__=="__main__":
    main()

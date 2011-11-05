def char2word(s):
    return ord(s[0]) + (ord(s[1])<<8)

def char2dword(s):
    return ord(s[0]) + (ord(s[1])<<8) + (ord(s[2])<<16) + (ord(s[3])<<24)

def char2chs(s):
    head = ord(s[0])
    sector = ord(s[1]) & 0x3f
    cylinder = ord(s[2]) + (( ord(s[1]) & 0xc0 ) << 2)
    return (cylinder, head, sector)

def chs2lba(c, h, s, hpc, spt):
    """Convert a CHS address to LBA where c, h, s are the cylinder, h the head,
    s the sector. hpc is the heads per cylinder, spt is sectors per track"""
    return ((c * hpc) + h) * spt + s-1


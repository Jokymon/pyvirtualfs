def list2word(l):
    return l[0] + l[1]<<8

def list2dword(l):
    return l[0] + l[1]<<8 + l[2]<<16 + l[3]<<24

def list2chs(s):
    head = s[0]
    sector = s[1] & 0x3f
    cylinder = s[2] + (( s[1] & 0xc0 ) << 2)
    return (cylinder, head, sector)

def chs2lba(c, h, s, hpc, spt):
    """Convert a CHS address to LBA where c, h, s are the cylinder, h the head,
    s the sector. hpc is the heads per cylinder, spt is sectors per track"""
    return ((c * hpc) + h) * spt + s-1

def lba2chs(lba, hpc, spt):
    s = (lba % spt) + 1
    h = int(lba / spt) % hpc
    c = int(lba / (spt*hpc))
    return (c, h, s)

def word2list(i):
    return [i & 0xff, (i>>8) & 0xff]

def dword2list(i):
    return [i & 0xff, (i>>8) & 0xff, (i>16) & 0xff, (i>>24) & 0xff]

def chs2list(chs):
    (cylinder, head, sector) = chs
    return [head, sector | ((cylinder>>8) & 0x3), cylinder&0xff ]

def int_ex(s):
    if s.startswith("0x"):
        return int(s[2:], 16)
    else:
        return int(s)

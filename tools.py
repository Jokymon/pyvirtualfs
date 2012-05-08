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

def lba2chs(lba, hpc, spt):
    s = (lba % spt) + 1
    h = int(lba / spt) % hpc
    c = int(lba / (spt*hpc))
    return (c, h, s)

def word2str(i):
    return chr(i & 0xff) + chr( (i>>8) & 0xff )

def dword2str(i):
    return chr(i & 0xff) + chr( (i>>8) & 0xff ) + chr( (i>>16) & 0xff ) + chr( (i>>24) & 0xff )

def chs2str(chs):
    (cylinder, head, sector) = chs
    return chr(head) + chr( sector | ((cylinder>>8) & 0x3) ) + chr( cylinder&0xff )

def int_ex(s):
    if s.startswith("0x"):
        return int(s[2:], 16)
    else:
        return int(s)

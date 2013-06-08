class Field(object):
    def __init__(self, start, size):
        self.start = start
        self.size = size

    def __get__(self, instance, owner):
        start = instance.start_offset + self.start
        values = instance.array[start:start+self.size]
        powers = range(len(values))
        powers = map(lambda x: 256**x, powers)
        summands = map(int.__mul__, values, powers)
        return sum(summands)

    def validate_set_value(self, value):
        if value >= 2**(self.size*8):
            raise ValueError("%u does not fit in this field" % value)

    def __set__(self, instance, value):
        self.validate_set_value(value)
        powers = []
        while value!=0:
            powers.append( int(value % 256) )
            value /= 256
        powers.extend( self.size*[0] )
        start = instance.start_offset + self.start

        instance.array[start:start+self.size] = powers[0:self.size]

class Int8Field(Field):
    def __init__(self, start):
        Field.__init__(self, start, 1)

class UInt8Field(Field):
    def __init__(self, start):
        Field.__init__(self, start, 1)

class UInt16Field(Field):
    def __init__(self, start):
        Field.__init__(self, start, 2)

class StringField(Field):
    def __init__(self, start, length):
        Field.__init__(self, start, length)

    def __get__(self, instance, owner):
        start = instance.start_offset + self.start
        values = instance.array[start:start+self.size]
        return "".join(map(chr, values))

    def __set__(self, instance, value):
        assert len(value)<=self.size
        start = instance.start_offset + self.start
        instance.array[start : start+len(value)] = list(map(ord, value))

class ClassWithLengthMetaType(type):
    def __len__(self):
        return self.clslength()

ClassWithLength = ClassWithLengthMetaType('ClassWithLength', (object, ), {})

class StructTemplate(ClassWithLength):
    def __init__(self, array, start_offset):
        self.array = array
        self.start_offset = start_offset

    @classmethod
    def clslength(cls):
        len = 0
        for attr in cls.__dict__.values():
            if isinstance(attr, Field):
                len += attr.size
        return len

    def __len__(self):
        return len(self.__class__)

class Subrange(object):
    """A sub range behaves like a list. It returns and modifies the values of
    an other list by selecting a subrange of it."""
    def __init__(self, array, start_offset, length):
        self.array = array
        self.start_offset = start_offset
        self.length = length

    def __len__(self):
        return self.length

    def __getitem__(self, key):
        if type(key)==slice:
            return self.array[ self.start_offset + key.start : self.start_offset + key.stop ]
        else:
            return self.array[ self.start_offset + key ]

    def __setitem__(self, key, value):
        if type(key)==slice:
            self.array[ self.start_offset + key.start : self.start_offset + key.stop ] = value
        else:
            self.array[ self.start_offset + key ] = value

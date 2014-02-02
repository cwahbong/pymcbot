import struct

class Primitive:
  """ Base of a type that can be pack/unpack by ``struct'' module.
      You should not create any instance of this class and its
      subclasses.
  """
  format = None

  def __init__(self, *args, **kwargs):
    raise NotImplementedError

  @classmethod
  def pack(cls, data, packet=None):
    return struct.pack(cls.format, 0 if data is None else data)

  @classmethod
  def unpack(cls, buf, offset=0, info=None):
    unpacked = struct.unpack_from(cls.format, buf, offset)[0]
    offset += struct.calcsize(cls.format)
    return unpacked, offset


class Bool(Primitive):
  """ Boolean value.
  """
  format = "!?"


class Byte(Primitive):
  """ 1-byte signed integer.
  """
  format = "!b"


class UnsignedByte(Primitive):
  """ 1-byte unsigned integer.
  """
  format = "!B"


class Short(Primitive):
  """ 2-byte signed integer.
  """
  format = "!h"


class UnsignedShort(Primitive):
  """ 2-byte unsigned integer.
  """
  format = "!H"


class Int(Primitive):
  """ 4-byte signed integer.
  """
  format = "!i"


class Long(Primitive):
  """ 8-byte signed integer.
  """
  format = "!q"


class Float(Primitive):
  """ Single-precision 32-bit IEEE 754 floating point.
  """
  format = "!f"


class Double(Primitive):
  """ Double-precision 64-bit IEEE 754 floating point.
  """
  format = "!d"

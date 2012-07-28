import struct 

""" byte, short, int, long, float, double, string, boolean, array, metadata, slot
"""

class Primitive(object):
  """ Base of a type that can be pack/unpack by ``struct'' module.
  """
  format = None

  @classmethod
  def pack(cls, data):
    return struct.pack(cls.format, data)

  @classmethod
  def unpack(cls, buf, offset=0):
    return struct.unpack(clas.format, buf, offset)


class Bool(Primitive):
  """ Boolean value.
  """
  format = "!?"


class Byte(Primitive):
  """ 1-byte signed integer.
  """
  format = "!b"


class Short(Primitive):
  """ 2-byte signed integer.
  """
  format = "!h"


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



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


class String(object):
  """
  """
  
  @classmethod
  def pack(cls, data):
    data = "" if data is None else data
    utf_data = data.encode("utf_16_be")
    result = Short.pack(len(data))
    result += struct.pack("!{}s".format(len(utf_data)), utf_data)
    return result
  
  @classmethod
  def unpack(cls, buf, offset=0):
    length, offset = Short.unpack(buf, offset)
    utf_length = len((" "*length).encode("utf_16_be"))
    utf_data = struct.unpack_from("!{}s".format(utf_length), buf, offset)[0]
    result = utf_data.decode("utf_16_be")
    offset += utf_length
    return result, offset


class Array(object):

  def __init__(self, type, length):
    self.type = type
    self.length = length

  def pack(self, data):
    pass

  def unpack(self, buf, offset=0):
    pass

class Metadata(object):
  pass


class Slot(object):
  pass



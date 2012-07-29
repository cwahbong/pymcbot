import struct 

""" byte, short, int, long, float, double, string, boolean, array, metadata, slot
"""

class Primitive(object):
  """ Base of a type that can be pack/unpack by ``struct'' module.
      You should not create any instance of this class and its
      subclasses.
  """
  format = None

  def __init__(self*args, **kwargs):
    raise NotImplementedError

  @classmethod
  def pack(cls, data, packet=None):
    return struct.pack(cls.format, data)

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


class String(object):
  """
  """
  
  @classmethod
  def pack(cls, data, packet=None):
    data = "" if data is None else data
    utf_data = data.encode("utf_16_be")
    result = Short.pack(len(data))
    result += struct.pack("!{}s".format(len(utf_data)), utf_data)
    return result
  
  @classmethod
  def unpack(cls, buf, offset=0, info=None):
    length, offset = Short.unpack(buf, offset)
    utf_length = len((" "*length).encode("utf_16_be"))
    utf_data = struct.unpack_from("!{}s".format(utf_length), buf, offset)[0]
    result = utf_data.decode("utf_16_be")
    offset += utf_length
    return result, offset


class Array(object):

  def __init__(self, elem_type, length_info):
    self.elem_type = elem_type
    self.length_info = length_info

  def __length(self, packet=None, info=None):
    if isinstance(self.length_info, int):
      return self.length_info
    if packet is None and info is not None:
      return info[self.length_info]
    elif packet is not None and info is None:
      return getattr(packet, self.length_info)
    raise ValueError

  def pack(self, data, packet=None):
    """ Will use packet to check the length of the data.
    """
    if packet is not None and len(data) != __length(packet):
      raise ValueError("Length of array is not correct.")
    for elem in data:
      self.elem_type.pack(elem)

  def unpack(self, buf, offset=0, info={}):
    for _ in range(self.__length(info)):
      self.elem_type.unpack(self, buf, offset)


class Object(object):
  pass


class MetaData(object):
  pass


class Slot(object):
  pass


class Record(object):
  pass



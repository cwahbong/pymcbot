import struct

def enchantable(item_id):
  if 256<=item_id<=259 or 267<=item_id<=279 or 283<=item_id<=286:
    return True
  if 290<=item_id<=294 or 298<=item_id<=317:
    return True
  if item_id in (261, 359, 346):
    return True
  return False


class LengthType:

  def __init__(self, length_info):
    self.length_info = length_info

  def _length(self, packet=None, info=None):
    if isinstance(self.length_info, int):
      return self.length_info
    if packet is None and info is not None:
      return info[self.length_info]
    elif packet is not None and info is None:
      return getattr(packet, self.length_info)
    raise ValueError


class VarInt:

  def __init__(self):
    raise NotImplementedError

  @classmethod
  def pack(cls, data, packet = None):
    n, m = divmod(data, 128)
    nums = [m]
    while n:
      n, m = divmod(n, 128)
      nums.append(m)
    masked = list(map(lambda n: n | 128, nums[:-1])) + nums[-1:]
    return bytes(masked)

  @classmethod
  def unpack(cls, buf, offset = 0, info = None):
    nums = []
    try:
      while True:
        b = buf[offset]
        offset += 1
        nums.append(b & 0x7F)
        if b & 0x80 == 0:
          break
    except IndexError as e:
      raise struct.error("Raw data length not enough for VarInt.")
    result = 0
    for n in reversed(nums):
      result = 128 * result + n
    return result, offset


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


class Int128:
  MAX64 = 0xFFFFFFFFFFFFFFFF

  def __init__(self):
    raise NotImplementedError

  @classmethod
  def pack(cls, data, packet=None):
    l, r = (data >> 64) & Int128.MAX64, data & Int128.MAX64
    return struct.pack("!QQ", l, r)

  @classmethod
  def unpack(cls, buf, offset=0, info=None):
    l, r = struct.unpack_from("!QQ", buf, offset)
    return l * Int128.MAX64 + r, offset + 16


class String:
  """ UTF8 string prefixed with its byte length (VarInt)
  """

  @classmethod
  def pack(cls, data, packet=None):
    data = "" if data is None else data
    utf = data.encode()
    utf_len = len(utf)
    result = VarInt.pack(utf_len)
    result += struct.pack("!{}s".format(utf_len), utf)
    return result

  @classmethod
  def unpack(cls, buf, offset=0, info=None):
    utf_len, offset = VarInt.unpack(buf, offset)
    utf = struct.unpack_from("!{}s".format(utf_len), buf, offset)[0]
    result = utf.decode()
    offset += utf_len
    return result, offset


class Array(LengthType):

  def __init__(self, elem_type, length_info):
    super(Array, self).__init__(length_info)
    self.elem_type = elem_type

  def pack(self, data, packet=None):
    """ Will use packet to check the length of the data.
    """
    if packet is not None and len(data) != self._length(packet=packet):
      raise ValueError("Length of array is not correct.")
    for elem in data:
      self.elem_type.pack(elem)

  def unpack(self, buf, offset=0, info={}):
    result = []
    for _ in range(self._length(info=info)):
      elem, offset = self.elem_type.unpack(buf, offset, info)
      result.append(elem)
    return result, offset


class Object:

  @classmethod
  def pack(cls, data, packet=None):
    raise NotImplementedError

  @classmethod
  def unpack(cls, buf, offset=0, info={}):
    result = {}
    not_none, offset = Int.unpack(buf, offset, info)
    if not_none:
      result["meta"] = not_none # TODO change "meta" to the aprropriate type by "info"
      result["speed_x"], offset = Short.unpack(buf, offset, info)
      result["speed_y"], offset = Short.unpack(buf, offset, info)
      result["speed_z"], offset = Short.unpack(buf, offset, info)
    return result, offset


class Slot:

  @classmethod
  def pack(cls, data, packet=None):
    if data is None or data["id"]==-1:
      result = Short.pack(-1, packet)
    else:
      result = Short.pack(data["id"])
      result += Byte.pack(data["count"])
      result += Short.pack(data["meta"])
      if enchantable(data["id"]):
        raise NotImplementedError
    return result

  @classmethod
  def unpack(cls, buf, offset=0, info={}):
    result = {}
    result["id"], offset = Short.unpack(buf, offset, info)
    if result["id"] != -1:
      result["count"], offset = Byte.unpack(buf, offset, info)
      result["damage"], offset = Short.unpack(buf, offset, info)
      result["nbt_length"], offset = Short.unpack(buf, offset, info)
      if result["nbt_length"] != -1:
        result["data"], offset = Array(Byte, result["data_length"]).unpack(buf, offset, info)
    return result, offset


class MetaData:
  __types = [Byte, Short, Int, Float, String, Slot]

  @classmethod
  def pack(cls, data, packet=None):
    raise NotImplementedError

  @classmethod
  def unpack(cls, buf, offset=0, info={}):
    result = {}
    x, offset = UnsignedByte.unpack(buf, offset, info)
    while x != 127:
      index, type = x & 0x1F, x>>5
      if 0 <= type < len(cls.__types):
        value, offset = cls.__types[type].unpack(buf, offset, info)
      else:
        raise ValueError("Invalid metadata with type={}".format(type))
      result[index] = (cls.__types[type], value)
      x, offset = UnsignedByte.unpack(buf, offset, info)
    return result, offset


class Multi:

  class Unpacked:
    pass

  def __init__(self, *fields):
    self._fields = fields

  def pack(self, data, packet=None):
    result = bytearray()
    for tp, name in self._fields:
      result += tp.pack(getattr(data, name))
    return result

  def unpack(self, buf, offset=0, info={}):
    result = Multi.Unpacked()
    minfo = dict(info)
    for tp, name in self._fields:
      value, offset = tp.unpack(buf, offset, minfo)
      minfo[name] = value
      setattr(result, name, value)
    return result, offset

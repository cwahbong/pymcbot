from mc.field.primitives import *
from mc.field.compounds import *
from mc.field.numbers import *

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
        result["nbt"], offset = Array(Byte, result["nbt_length"]).unpack(buf, offset, info)
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

import re
import struct
import threading

class repeater(threading.Thread):

  def __init__(self, name=None):
    super(repeater, self).__init__(name=name)
    self.__stop = False

  def repeated(self):
    raise NotImplementedError

  def run(self):
    while not self.__stop and self.repeated():
      pass
    print "{} stopped".format(self.name)

  def stop_later(self):
    self.__stop = True


def enchantable(item_id):
  if 256<=item_id<=259 or 267<=item_id<=279 or 283<=item_id<=286:
    return True
  if 290<=item_id<=294 or 298<=item_id<=317:
    return True
  if item_id in (261, 359, 346):
    return True
  return False

def pack_single(fmt, arg):
  if fmt=="S":
    attr = "" if arg is None else arg
    utf16_attr = attr.encode("utf_16_be")
    #result = struct.pack("!h", len(attr))
    result = pack_single("h", len(attr))
    result += struct.pack("!{}s".format(len(utf16_attr)), utf16_attr)
  elif fmt=="T":
    if arg is None or arg["id"]==-1:
      result = pack_single("h", -1)
    else:
      result = pack_single("h", arg["id"])
      result += pack_single("b", arg["count"])
      result += pack_single("h", arg["damage"])
      if enchantable(arg["id"]):
        raise NotImplementedError
  elif fmt=="M":
    raise NotImplementedError
  elif fmt in "bB?hHiIlLqQfd":
    attr = 0 if arg is None else arg
    nfmt = "!{}".format(fmt)
    result = struct.pack(nfmt, attr)
  else:
    raise ValueError("Invalid fmt '{}'.".format(fmt))
  return result


def unpack_from_single(fmt, buffer, offset=0):
  if fmt=="S":
    length, offset = unpack_from_single("h", buffer, offset)
    utf16_length = len((" "*length).encode("utf_16_be"))
    utf16_attr = struct.unpack_from("!{}s".format(utf16_length), buffer, offset)[0]
    result = utf16_attr.decode("utf_16_be")
    offset += utf16_length
  elif fmt=="T":
    result = {}
    result["id"], offset = unpack_from_single("h", buffer, offset)
    if result["id"]!=-1:
      result["count"], offset = unpack_from_single("b", buffer, offset)
      result["damage"], offset = unpack_from_single("h", buffer, offset)
      if enchantable(result["id"]):
        result["data_length"], offset = unpack_from_single("h", buffer, offset)
        if result["data_length"]!=-1:
          result["data"], offset = struct.unpack_from("!s{}".format(result["data_length"]), buffer, offset)
  elif fmt=="M":
    result = {}
    x, offset = unpack_from_single("B", buffer, offset)
    while x != 127:
      index, type = x & 0x1F, x>>5
      if type==0:
        value, offset = unpack_from_single("b", buffer, offset)
      elif type==1:
        value, offset = unpack_from_single("h", buffer, offset)
      elif type==2:
        value, offset = unpack_from_single("i", buffer, offset)
      elif type==3:
        value, offset = unpack_from_single("f", buffer, offset)
      elif type==4:
        value, offset = unpack_from_single("S", buffer, offset)
      elif type==5:
        value = {}
        value["id"], offset = unpack_from_single("h", buffer, offset)
        value["count"], offset = unpack_from_single("b", buffer, offset)
        value["damage"], offset = unpack_from_single("h", buffer, offset)
      elif type==6:
        value = []
        for _ in range(3):
          v, offset = unpack_from_single("i", buffer, offset)
          value.append(v)
      else:
        raise ValueError("Invalid metadata with type={}".format(type))
      result[index] = (type, value)
      x, offset = unpack_from_single("B", buffer, offset)
  elif fmt in "bB?hHiIlLqQfd":
    result = struct.unpack_from("!{}".format(fmt), buffer, offset)[0]
    offset += struct.calcsize(fmt)
  else:
    raise ValueError("Invalid fmt '{}'.".format(fmt))
  return result, offset


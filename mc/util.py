import re
import struct
import threading
from fields import *

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


def pack_single(fmt, arg):
  if fmt=="S":
    return String.pack(arg)
  elif fmt=="T":
    return Slot.pack(arg)
  elif fmt=="M":
    return MetaData.pack(arg)
  elif fmt in "bB?hHiIlLqQfd":
    attr = 0 if arg is None else arg
    nfmt = "!{}".format(fmt)
    result = struct.pack(nfmt, attr)
  else:
    raise ValueError("Invalid fmt '{}'.".format(fmt))
  return result


def unpack_from_single(fmt, buffer, offset=0):
  if fmt=="S":
    return String.unpack(buffer, offset)
  elif fmt=="T":
    return Slot.unpack(buffer, offset)
  elif fmt=="M":
    return MetaData.unpack(buffer, offset)
  elif fmt in "bB?hHiIlLqQfd":
    result = struct.unpack_from("!{}".format(fmt), buffer, offset)[0]
    offset += struct.calcsize(fmt)
  else:
    raise ValueError("Invalid fmt '{}'.".format(fmt))
  return result, offset


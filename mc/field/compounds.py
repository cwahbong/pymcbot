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

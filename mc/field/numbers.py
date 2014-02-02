import struct

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

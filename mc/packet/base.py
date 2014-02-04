from mc.field.v172 import *

import functools
import logging

_logger = logging.getLogger(__name__)

class BasePacket:

  def __init__(self, pid, name):
    self._pid = pid
    self._name = name


class UnknownPacket(BasePacket):

  def __init__(self, pid, raw):
    super().__init__(pid, "unknown")
    self.raw = raw


class Packet(BasePacket):

  def __init__(self, packets, packet_name, **field_info):
    super().__init__(
        packets._pid[packet_name],
        packet_name,
    )
    kwset = packets._kwset[self._pid]
    if kwset != set(field_info.keys()):
      raise ValueError("The set of field_info keys should be same"
          "as kwset registered."
      )
    for fname, fcontent in field_info.items():
      if fname in kwset:
        setattr(self, fname, fcontent)
      else:
        raise ValueError("``{}'' is not a valid field name.".format(fname))


class Packets:

  def __init__(self):
    self._fields = dict()
    self._kwset = dict()
    self._name = dict()
    self._pid = dict()

  def register(self, *type_infos):
    for type_info in type_infos:
      pid, name, fields = type_info
      self._fields[pid] = fields
      self._kwset[pid] = set(map(lambda p: p[1], fields))
      self._name[pid] = name
      self._pid[name] = pid

  def make(self, _name, **info):
    return Packet(self, _name, **info)

  def pack(self, packet):
    p = VarInt.pack(packet._pid)
    for ftype, fname in self._fields[packet._pid]:
      fcontent = getattr(packet, fname, None) if fname else None
      p += ftype.pack(fcontent)
    result = VarInt.pack(len(p)) + p
    return result

  def unpack(self, raw, offset = 0):
    plen, noffset = VarInt.unpack(raw, offset)
    size = plen + noffset
    if len(raw) < size:
      raise struct.error("Raw data length not enough for packet.")
    pid, noffset = VarInt.unpack(raw, noffset)
    if pid not in self._fields:
      _logger.warning("Packet id {} not supported and skipped.".format(pid))
      return RawPacket(pid, raw[noffset:size]), size
    finfo = dict()
    for ftype, fname in self._fields[pid]:
      fcontent, noffset = ftype.unpack(raw, noffset, finfo)
      if fname:
        finfo[fname] = fcontent
    if noffset != size:
      import binascii
      _logger.warning("noffset != size, possibly parse incorrectly. {},"
         "{}, offset = {}, plen = {}.".format(noffset, size, offset, plen))
      _logger.warning(binascii.hexlify(raw[offset:size]))
    _logger.debug(finfo)
    return Packet(
        self,
        self._name[pid],
        **finfo
    ), size

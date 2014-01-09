from mc.fields import *

import collections
import functools
import sys

CLIENT_TO_SERVER = 0
SERVER_TO_CLIENT = 1

START_STATE   = 0
STATUS_STATE  = 1
LOGIN_STATE   = 2
PLAY_STATE    = 3

_fields = collections.defaultdict(dict)
_kwset = collections.defaultdict(dict)

_name = dict()
_pid = dict()

class Packet:

  def __init__(self, packet_direction, packet_state, packet_name, **field_info):
    self.pid = _pid[packet_name]
    kwset = _kwset[packet_direction, packet_state][self.pid]
    for fname, fcontent in field_info.items():
      if fname in kwset:
        setattr(self, fname, fcontent)
      else:
        raise ValueError("``{}'' is not a valid field name.".format(fname))

  def name(self):
    return _name[self.pid]


def pack(packet, direction, state):
  p = VarInt.pack(packet.pid)
  for ftype, fname in _fields[direction, state][packet.pid]:
    fcontent = getattr(packet, fname, None) if fname else None
    p += ftype.pack(fcontent)
  result = VarInt.pack(len(p)) + p
  print("Packed:", result)
  return result

def unpack(raw, direction, state, offset = 0):
  plen, offset = VarInt.unpack(raw, offset)
  pid, offset = VarInt.unpack(raw, offset)
  finfo = dict()
  for ftype, fname in _fields[direction, state][pid]:
    fcontent, offset = ftype.unpack(raw, offset, finfo)
    if fname:
      finfo[fname] = fcontent
  return Packet(direction, state, _name[pid], **finfo), offset

def register(direction, state, *type_infos):
  for type_info in type_infos:
    pid, name, fields = type_info
    _fields[direction, state][pid] = fields
    _kwset[direction, state][pid] = set(map(lambda p: p[1], fields))
    _name[pid] = name
    _pid[name] = pid
    setattr(sys.modules[__name__], name, functools.partial(
        Packet,
        direction,
        state,
        name
    ))


register(CLIENT_TO_SERVER, START_STATE,
    (0x00, "handshake", [
        (VarInt, "version"),
        (String, "address"),
        (UnsignedShort, "port"),
        (VarInt, "state"),
    ]),
)

"""
register(CLIENT_TO_SERVER, PLAY_STATE,
  # TODO
)

register(SERVER_TO_CLIENT, PLAY_STATE,
  # TODO
)
"""
register(CLIENT_TO_SERVER, STATUS_STATE,
    (0x00, "status_request", []),
    (0x01, "ping", [
        (Long, "time"),
    ]),
)

register(SERVER_TO_CLIENT, STATUS_STATE,
    (0x00, "status_response", [
        (String, "json_response"),
    ]),
    (0x01, "ping", [
        (Long, "time"),
    ]),
)

from mc.fields import *

import collections
import functools
import logging
import sys

_logger = logging.getLogger(__name__)

CLIENT_TO_SERVER = 0
SERVER_TO_CLIENT = 1

_pre = {
    CLIENT_TO_SERVER: "cs_",
    SERVER_TO_CLIENT: "sc_",
}

START_STATE   = 0
STATUS_STATE  = 1
LOGIN_STATE   = 2
PLAY_STATE    = 3

_fields = collections.defaultdict(dict)
_kwset = collections.defaultdict(dict)

_name = collections.defaultdict(dict)
_pid = collections.defaultdict(dict)


class RawPacket:

  def __init__(self, pid, raw):
    self._pid = pid
    self._name = "unknown"
    self.raw = raw


class Packet:

  def __init__(self, packet_direction, packet_state, packet_name, **field_info):
    self._pid = _pid[packet_direction, packet_state][packet_name]
    self._name = packet_name
    kwset = _kwset[packet_direction, packet_state][self._pid]
    for fname, fcontent in field_info.items():
      if fname in kwset:
        setattr(self, fname, fcontent)
      else:
        raise ValueError("``{}'' is not a valid field name.".format(fname))


def pack(packet, direction, state):
  p = VarInt.pack(packet._pid)
  for ftype, fname in _fields[direction, state][packet._pid]:
    fcontent = getattr(packet, fname, None) if fname else None
    p += ftype.pack(fcontent)
  result = VarInt.pack(len(p)) + p
  return result

def unpack(raw, direction, state, offset = 0):
  plen, noffset = VarInt.unpack(raw, offset)
  size = plen + noffset
  if len(raw) < size:
    raise struct.error("Raw data length not enough for packet.")
  pid, noffset = VarInt.unpack(raw, noffset)
  if pid not in _fields[direction, state]:
    _logger.warning("Packet id {} not supported and skipped.".format(pid))
    return RawPacket(pid, raw[noffset:size]), size
  finfo = dict()
  for ftype, fname in _fields[direction, state][pid]:
    fcontent, noffset = ftype.unpack(raw, noffset, finfo)
    if fname:
      finfo[fname] = fcontent
  if noffset != size:
    import binascii
    _logger.warning("noffset != size, possibly parse incorrectly. {},"
       "{}".format(noffset, size))
    _logger.warning(binascii.hexlify(raw[offset:size]))
  _logger.debug(finfo)
  return Packet(
      direction,
      state,
      _name[direction, state][pid],
      **finfo
  ), size

def register(direction, state, *type_infos):
  for type_info in type_infos:
    pid, name, fields = type_info
    _fields[direction, state][pid] = fields
    _kwset[direction, state][pid] = set(map(lambda p: p[1], fields))
    _name[direction, state][pid] = name
    _pid[direction, state][name] = pid
    setattr(sys.modules[__name__], _pre[direction] + name, functools.partial(
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

register(CLIENT_TO_SERVER, LOGIN_STATE,
    (0x00, "login_start", [
        (String, "name"),
    ]),
    (0x01, "encryption_response", [
        (Short, "public_key_length"),
        (Array(Byte, "public_key_length"),
                "public_key"),
        (Short, "token_length"),
        (Array(Byte, "token_length"),
                "verify_token"),
    ]),
)

register(SERVER_TO_CLIENT, LOGIN_STATE,
    (0x00, "disconnect", [
        (String, "json"),
    ]),
    (0x01, "encryption_request", [
        (String, "server_id"),
        (Short, "public_key_length"),
        (Array(Byte, "public_key_length"),
                "public_key"),
        (Short, "token_length"),
        (Array(Byte, "token_length"),
                "verity_token"),
    ]),
    (0x02, "login_success", [
        (String, "uuid"),
        (String, "username"),
    ]),
)

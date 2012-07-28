from mc.fields import *


_fields = {
    "c2s": {},
    "s2c": {},
}

_kwset = {
    "c2s": {},
    "s2c": {},
}

_name = {}

_id = {}


class Packet(object):
  
  def __init__(self, direction, name, **field_info):
    self.id = _id[name]
    kwset = _kwset[direction][self.id]
    for field_name, field_content in field_info.items():
      if field_name in kwset:
        setattr(self, field_name, field_content)
      else:
        raise ValueError("``{}'' is not a valid field name.".format(field_name))


def pack(packet):
  result = UnsignedByte.pack(packet.id)
  for field_type, field_name in _fields[direction][packet.id]:
    field_content = getattr(packet, field_name, None)
    result += field_type.pack(field_content)
  return result


def unpack(rawstring, direction, offset=0):
    id, offset = UnsignedByte.unpack(rawstring, offset)
    field_info = {}
    for field_type, field_name in _fields[direction][id]:
      field_content, offset = field_type.unpack(rawstring, offset)
      field_info[field_name] = field_content
    return Packet(direction, _name[id], **field_info), offset


def register(id, direction, name, fields):
  if direction=="both":
    register(id, "c2s", name, fields)
    register(id, "s2c", name, fields)
  else:
    if direction not in ("c2s", "s2c"):
      raise ValueError("Not a valid direction: {}".format(direction))
    _fields[direction][id] = fields
    _kwset[direction][id] = set(map(lambda p: p[1], fields))
    _name[id] = name
    _id[name] = id


register(0x00, "both", "keep_alive", [(Int, "keepalive_id")])
register(0x01,  "c2s", "login_request", [
    (Int, "version"),
    (String, "username"),
    (String, ""),
    (Int, ""),
    (Int, ""),
    (Byte, ""),
    (UnsignedByte, ""),
    (UnsignedByte, ""),
])
register(0x01,  "s2c", "login_request", [
    (Int, "eid"),
    (String, ""),
    (String, "level_type"),
    (Int, "server_mode"),
    (Int, "dimension"),
    (Byte, "difficulty"),
    (UnsignedByte, ""),
    (UnsignedByte, ""),
])
register(0x02,  "c2s", "handshake", [(String, "username_host")])
register(0x02,  "s2c", "handshake", [(String, "connection_hash")])
register(0x03, "both", "chat_message", [(String, "message")])



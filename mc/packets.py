import struct


class packet(object):
  id = -1

  def __init__(self, direction, **kwargs):
    if direction not in ("c2s", "s2c"):
      raise ValueError("Direction invalid.")
    self.direction = direction
    for (_, attrname) in filter(lambda d: d[1], self.get_datatable()):
      setattr(self, attrname, kwargs[attrname])

  def get_datatable(self):
    return getattr(self.__class__, "data_{}".format(self.direction))

  def pack(self):
    result = struct.pack("!B", self.id)
    for d in self.get_datatable():
      attr = getattr(self, d[1], None)
      if(d[0]=="S"):
        attr = "" if attr is None else attr
        utf16_attr = attr.encode("utf_16_be")
        result += struct.pack("!h", len(attr))
        result += struct.pack("!{}s".format(len(utf16_attr)), utf16_attr)
      else:
        attr = 0 if attr is None else attr
        result += struct.pack("!{}".format(d[0]), attr)
    return result


class keep_alive(packet):
  id = 0x00
  data_c2s = data_s2c = (("i", "keepalive_id"), )


class login_request(packet):
  id = 0x01
  data_c2s = (
      ("i", "version"),
      ("S", "username"),
      ("S", ""),
      ("i", ""),
      ("i", ""),
      ("b", ""),
      ("B", ""),
      ("B", ""),
  )
  data_s2c = (
      ("i", "entity_id"),
      ("S", ""),
      ("S", "level_type"),
      ("i", "server_mode"),
      ("i", "dimension"),
      ("b", "difficulty"),
      ("B", ""),
      ("B", "max_players"),
  )


class handshake(packet):
  id = 0x02
  data_c2s = (("S", "username_host"), )
  data_s2c = (("S", "connection_hash"), )


class chat_message(packet):
  id = 0x03
  data_c2s = data_s2c = (("S", "message"), )


class time_update(packet):
  id = 0x04
  data_c2s = data_s2c = (("l", "time"), )


class entity_equipment(packet):
  id = 0x05
  data_s2c = (
      ("i", "entity_id"),
      ("h", "slot"),
      ("h", "item_id"),
      ("h", "damage"),
  )

###############

class disconnect(packet):
  id = 0xFF
  data_c2s = data_s2c = (("S", "reason"), )



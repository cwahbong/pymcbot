from mc import window

class Handler(object):

  def __init__(self, client):
    self._client = client


class Connection(Handler):

  def on__keep_alive(self, packet):
    self._client._send(packet)
    print "keep alive"

  def on__disconnect(self, packet):
    print "Disconnect, reason:", packet.reason


class PositionLook(Handler):

  def on__spawn_position(self, packet):
    self._client.next_position_look(position={
        "x": packet.x,
        "y": packet.y,
        "z": packet.z,
        "stance": 0.1,
    }, look={
        "yaw": 0.0,
        "pitch": 0.0,
    }, on_ground=True)
    print "Spawn at ({}, {}, {})".format(packet.x, packet.y, packet.z)

  def on__player_position_look(self, packet):
    self._client._send(packet)
    self._client._update_position_look(
        packet.x, packet.y, packet.z, packet.stance,
        packet.yaw, packet.pitch, packet.on_ground
    )


class Slot(Handler):

  def on__set_slot(self, packet):
    if packet.window_id==-1 and packet.slot==-1:
      self._client._mouse_hold = {"id": -1}
    elif packet.window_id==self._client.window_id:
      idx = 0
      for pair in window.layout[self._client.window_type]:
        attr = pair[0]
        num = self._client.other_size if pair[1]<0 else pair[1]
        if idx<=packet.slot<idx+num:
          getattr(self._client, attr)[packet.slot-idx] = packet.slot_data
        idx += num

  def on__set_window_items(self, packet):
    idx = 0
    for pair in window.layout[self._client.window_type]:
      attr = pair[0]
      num = pair[1] if pair[1]!=-1 else packet.count-36
      setattr(self._client, attr, packet.slot_data[idx:idx+num])
      idx += num


class Window(Handler):

  def on__open_window(self, packet):
    self._client.window_id = packet.window_id
    self._client.window_type = SELF if packet.window_id==0 else packet.inventory_type
    self._client.other_size = packet.number_of_slots

  def on__close_window(self, packet):
    self._client.close()


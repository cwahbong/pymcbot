from mc import window

class handler(object):

  def __init__(self, robot):
    self._robot = robot


class keep_alive(handler):

  def on__keep_alive(self, packet):
    self._robot._socket.sendmc(packet)
    print "keep alive"


class position_look(handler):

  pass


class slot(handler):

  def on__set_slot(self, packet):
    if packet.window_id==-1 and packet.slot==-1:
      self._robot._mouse_hold = {"id": -1}
    elif packet.window_id==self._robot.window_id:
      idx = 0
      for pair in window.layout[self._robot.window_type]:
        attr = pair[0]
        num = self._robot.other_size if pair[1]<0 else pair[1]
        if idx<=packet.slot<idx+num:
          getattr(self._robot, attr)[packet.slot-idx] = packet.slot_data
        idx += num

  def on__set_window_items(self, packet):
    idx = 0
    for pair in window.layout[self._robot.window_type]:
      attr = pair[0]
      num = pair[1] if pair[1]!=-1 else packet.count-36
      setattr(self._robot, attr, packet.slot_data[idx:idx+num])
      idx += num


class Window(handler):

  def on__open_window(self, packet):
    self._robot.window_id = packet.window_id
    self._robot.window_type = SELF if packet.window_id==0 else packet.inventory_type
    self._robot.other_size = packet.number_of_slots

  def on__close_window(self, packet):
    self._robot.close()



class handler(object):

  def __init__(self, robot):
    self._robot = robot


class keep_alive(handler):

  def on__keep_alive(self, packet):
    self._robot._socket.sendmc(packet)
    print "keep alive"


class position_updater(handler):

  pass


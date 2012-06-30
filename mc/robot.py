import struct
import threading
import time

from mc import net
from mc.packets import *


class receiver(threading.Thread):

  def __init__(self, socket, name=None):
    super(receiver, self).__init__(name=name)
    self.socket = socket
    self.stop_flag = False

  def run(self):
    while not self.stop_flag:
      packet = self.socket.recvmc()

  def stop_later(self):
    self.stop_flag = True


class robot(object):

  def __init__(self):
    self.socket = net.mcsocket()
    # receiver is a thread, receiving packets and updating the user information.
    self.receiver = receiver(self.socket)

  def login(self, host, port, user, password=""):
    self.socket.connect((host, port))
    self.receiver.start()
    while not self.receiver.is_alive():
      time.sleep(1)
    self.socket.sendmc(handshake(username_host="{};{}:{}".format(user, host, port)))
    self.socket.sendmc(login_request(version=29, username=user))

  def logout(self, message=""):
    self.socket.sendmc(disconnect(reason=message))
    self.socket.close()
    self.receiver.stop_later()

  def getPosition(self):
    return (0, 0, 0)

  def haveItem(self):
    return False


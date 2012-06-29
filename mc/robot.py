import struct

from mc import net
from mc.packets import *

class robot(object):

  def __init__(self):
    self.socket = net.mcsocket()
    # packetreceiver is a thread, receiving packets and updating the user information.
    # self.packetreceiver = 

  def login(self, host, port, user, password=""):
    self.socket.connect((host, port))
    self.socket.sendmc(handshake(username_host="{};{}:{}".format(user, host, port)))
    recv = self.socket.recvmc()
    print recv
    self.socket.sendmc(login_request(version=29, username=user))
    recv = self.socket.recvmc()
    print recv
    # self.packetreceiver.start()

  def logout(self, message=""):
    # self.packetreceiver.stop()
    self.socket.sendmc(disconnect(reason=message))
    self.socket.close()

  def getPosition(self):
    return (0, 0, 0)

  def haveItem(self):
    return False


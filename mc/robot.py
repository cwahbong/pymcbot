import socket
import struct

from mc.packets import *

class robot(object):

  def __init__(self):
    self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    pass

  def login(self, host, port, user, password=""):
    self.socket.connect((host, port))
    self.socket.send(handshake("c2s", username_host="{};{}:{}".format(user, host, port)).pack())
    recv = self.socket.recv(1024)
    self.socket.send(login_request("c2s", version=29, username=user).pack())
    recv = self.socket.recv(1024)

  def logout(self, message=""):
    self.socket.send(disconnect("c2s", reason=message).pack())
    self.socket.close()

  def getPosition(self):
    return (0, 0, 0)

  def haveItem(self):
    return False


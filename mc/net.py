import socket

from mc.packets import *


class mcsocket(object):

  def __init__(self):
    self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    self.connect = self.socket.connect
    self.close = self.socket.close
    self.buf = ""

  def sendmc(self, packet):
    return self.socket.send(pack(packet, "c2s"))

  def recvmc(self):
    if len(self.buf)<1:
      self.buf += self.socket.recv(512)
    packet, size = unpack(self.buf, "s2c")
    print "@mcsocket.recvmc"
    print packet, size
    self.buf = self.buf[size:]
    return packet


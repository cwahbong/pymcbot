import socket

from mc import packets


class mcsocket(object):

  def __init__(self):
    self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    self.connect = self.socket.connect
    self.close = self.socket.close
    self.__buf = ""

  def sendmc(self, packet):
    return self.socket.send(packets.pack(packet, "c2s"))

  def recvmc(self):
    if len(self.__buf)<1:
      self.__buf += self.socket.recv(512)
    packet, size = packets.unpack(self.__buf, "s2c")
    print "@mcsocket.recvmc"
    print packet, size
    self.__buf = self.__buf[size:]
    return packet


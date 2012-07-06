import errno
import socket
import time

from mc import packets


class mcsocket(object):

  def __init__(self):
    self.__socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    self.connect = self.__socket.connect
    self.close = self.__socket.close
    self.__buf = ""

  def sendmc(self, packet):
    return self.__socket.send(packets.pack(packet, "c2s"))

  def recvmc(self):
    try:
      if len(self.__buf)==0:
        self.__buf += self.__socket.recv(256)
      elif len(self.__buf)<256:
        self.__buf += self.__socket.recv(256, socket.MSG_DONTWAIT)
    except socket.error as e:
      if e.errno!=errno.EAGAIN:
        raise e
      time.sleep(0.05)
    if len(self.__buf)==0:
      return None
    packet, size = packets.unpack(self.__buf, "s2c")
    self.__buf = self.__buf[size:]
    return packet


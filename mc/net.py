import errno
import socket
import time

from mc import packets


class mcsocket(object):
  threshold = 8192
  max_fetch = 16384

  def __init__(self):
    self.__socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    self.__buf = ""

  def connect(self, address):
    self.__socket.connect(address)

  def close(self):
    self.__socket.shutdown(socket.SHUT_RDWR)
    self.__socket.close()

  def sendmc(self, packet):
    return self.__socket.send(packets.pack(packet))

  def recvmc(self):
    while True:
      try:
        if len(self.__buf)<self.threshold:
          self.__buf += self.__socket.recv(self.max_fetch)
        if len(self.__buf)==0:
          return None
        p, size = packets.unpack(self.__buf)
        self.__buf = self.__buf[size:]
        return p
      except Exception as e:
        pass


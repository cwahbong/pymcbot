import errno
import socket
import time

from mc import packets


class mcsocket(object):
  origin_fetch = 16

  def __init__(self):
    self.__socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    self.__buf = ""

  def connect(self, address):
    self.__socket.connect(address)

  def close(self):
    self.__socket.shutdown(socket.SHUT_RDWR)
    self.__socket.close()

  def sendmc(self, packet):
    print "send:", packet.name()
    return self.__socket.send(packets.pack(packet))

  def recvmc(self):
    again = False
    fetch = self.origin_fetch
    while True:
      try:
        if again or len(self.__buf)==0:
          self.__buf += self.__socket.recv(fetch)
          if len(self.__buf)==0:
            return None
        p, size = packets.unpack(self.__buf)
        self.__buf = self.__buf[size:]
        print "receive:", p.name(), len(self.__buf)
        return p
      except Exception as e:
        again = True
        fetch *= 2


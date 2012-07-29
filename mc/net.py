import errno
import socket
import time

from mc import packets


class mcsocket(object):

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
    p, size = packets.unpack(self.__buf)
    self.__buf = self.__buf[size:]
    return p


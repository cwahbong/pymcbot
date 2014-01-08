import errno
import logging
import queue
import socket
import time

from mc.packet import v172 as packets
from mc import util

_logger = logging.getLogger(__name__)

PACKET = "packet"
SET_STATE = "set_state"

class _McSender(util.Repeater):

  def __init__(self, socket):
    super().__init__("Sender")
    self._socket = socket
    self._queue = queue.Queue()
    self._state = packets.START_STATE

  def repeated(self):
    if self._queue:
      cmd, content = self._queue.get()
      if cmd == SET_STATE:
        self._state = content
      elif cmd == PACKET:
        raw = packets.pack(content, packets.CLIENT_TO_SERVER, self._state)
        r = self._socket.send(raw)
        if r != len(raw):
          _logger.warning("Num of bytes sent != length or data.")


class _McRecver(util.Repeater):
  fetch = 4096

  def __init__(self, socket):
    super().__init__("Recver")
    self._again = False
    self._buf = ""
    self._socket = socket
    self._queue = queue.Queue()

  def repeated(self):
    if self._buf == 0:
      self._buf += self._socket.recv(self.fetch)
    try:
      packet, size = packets.unpack(self._buf)
      self._buf = self._buf[size:]
      _self._queue.put(packet)
      _logger.debug("Receive packet, type: %s", packet.name())
    except Exception as e:
      print(Exception)

class Connector:
  origin_fetch = 16

  def __init__(self):
    self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    self._sender = _McSender(self._socket)
    self._recver = _McRecver(self._socket)

  def connect(self, address):
    self._socket.connect(address)
    self._sender.start()
    self._recver.start()

  def disconnect(self):
    self._sender.stop_later()
    self._sender.join()

    self._recver.stop_later()
    self._recver.join()

    self._socket.shutdown(socket.SHUT_RDWR)
    self._socket.close()

  def set_state(self, state):
    self._sender._queue.put((SET_STATE, state))

  def send_later(self, packet):
    self._sender._queue.put((PACKET, packet))

  def pop_packet(self):
    return self._recver._queue.get()

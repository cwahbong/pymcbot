import errno
import json
import logging
import os
import queue
import socket

from mc.packet import v172 as packets
from mc import util

_logger = logging.getLogger(__name__)

PACKET = "packet"
SET_STATE = "set_state"

PAUSE_RECV = "pause_recv"

class _McSender(util.Repeater):

  def __init__(self, socket):
    super().__init__("Sender")
    self._socket = socket
    self._state = packets.START_STATE

  def runcmd(self, cmd, content):
    if cmd == SET_STATE:
      self._state = content
    elif cmd == PACKET:
      raw = packets.pack(content, packets.CLIENT_TO_SERVER, self._state)
      r = self._socket.send(raw)
      if r != len(raw):
        _logger.warning("Num of bytes sent != length or data.")

  def noncmd(self):
    pass


class _McRecver(util.Repeater):
  fetch = 4096

  def __init__(self, socket):
    super().__init__("Recver")
    self._need_more = False
    self._pause = True
    self._buf = bytearray()
    self._socket = socket
    self._state = packets.START_STATE
    self._packet_queue = queue.Queue()

  def runcmd(self, cmd, content):
    if cmd == SET_STATE:
      self._state = content
      _logger.debug("Recver new state: {}.".format(self._state))
    elif cmd == PAUSE_RECV:
      self._pause = content
      _logger.debug("Recver pause: {}.".format(self._pause))
    else:
      raise ValueError("cmd error in recver")

  def noncmd(self):
    if self._pause:
      return
    if self._need_more or len(self._buf) == 0:
      try:
        self._buf += self._socket.recv(self.fetch)
      except socket.error as e:
        if e.args[0] != errno.EAGAIN:
          raise e
    if len(self._buf) > 0:
      try:
        packet, size = packets.unpack(self._buf, packets.SERVER_TO_CLIENT, self._state)
        self._buf = self._buf[size:]
        self._packet_queue.put(packet)
        self._need_more = False
        _logger.debug("Receive packet, type: %s", packet.name())
      except Exception as e:
        self._need_more = True
        raise e

class Connector:

  def __init__(self):
    self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    self._sender = _McSender(self._socket)
    self._recver = _McRecver(self._socket)

  def connect(self, address):
    try:
      self._socket.connect(address)
      self._socket.setblocking(False)
      self._sender.start()
      self._recver.start()
    except socket.error as e:
      _logger.error("Socket: {}.".format(os.strerror(e.args[0])))
      return False
    return True

  def disconnect(self):
    self._sender.stop_later()
    self._sender.join()

    self._recver.stop_later()
    self._recver.join()

    self._socket.shutdown(socket.SHUT_RDWR)
    self._socket.close()

  def set_state(self, state):
    self._sender._msg_queue.put((SET_STATE, state))
    self._recver._msg_queue.put((PAUSE_RECV, True))
    self._recver._msg_queue.put((SET_STATE, state))
    self._recver._msg_queue.put((PAUSE_RECV, False))

  def send_later(self, packet):
    self._sender._msg_queue.put((PACKET, packet))

  def pop_packet(self):
    return self._recver._packet_queue.get()


def ping(host, port):
  connector = Connector()

  connected = connector.connect((host, port))
  if not connected:
    return None

  connector.send_later(packets.cs_handshake(
      version = 4,
      address = host,
      port = port,
      state = packets.STATUS_STATE
  ))
  connector.set_state(packets.STATUS_STATE)

  connector.send_later(packets.cs_status_request())
  response = connector.pop_packet()

  connector.disconnect()
  return json.loads(response.json_response)

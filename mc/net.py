import errno
import json
import logging
import os
import queue
import socket
import struct

from mc.packet import v172 as packets
from mc import util

_logger = logging.getLogger(__name__)

PACKET = "packet"
SET_STATE = "set_state"

RECV = "recv"
AUTO_RECV = "auto_recv"

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
    self._auto = False
    self._buf = bytearray()
    self._recv = 0
    self._socket = socket
    self._state = packets.START_STATE
    self._packet_queue = queue.Queue()

  def runcmd(self, cmd, content):
    if cmd == SET_STATE:
      self._state = content
      _logger.debug("Recver new state: {}.".format(self._state))
    elif cmd == AUTO_RECV:
      self._auto = content
      _logger.debug("Recver auto: {}.".format(self._auto))
    elif cmd == RECV:
      self._recv += content
      _logger.debug("Recv {} more packet later.".format(content))
    else:
      raise ValueError("cmd error in recver")

  def noncmd(self):
    if not self._auto and self._recv == 0:
      return
    if self._need_more or len(self._buf) == 0:
      try:
        r = self._socket.recv(self.fetch)
        if len(r) == 0:
          _logger.warning("Disconnected by the server.")
          self.stop_later()
        self._buf += r
      except socket.error as e:
        if e.args[0] != errno.EAGAIN:
          raise e
    if len(self._buf) > 0:
      try:
        self._need_atleast = packets.unpack_peek_size(self._buf)
      except struct.error as e:
        self._need_more = True
        _logger.warning(e)
        return
    if len(self._buf) < self._need_atleast:
      _logger.debug("Need more data to form a packet.")
      self._need_more = True
      return
    try:
      packet, size = packets.unpack(self._buf, packets.SERVER_TO_CLIENT, self._state)
      self._buf = self._buf[size:]
      self._packet_queue.put(packet)
      self._recv -= 1
      self._need_more = False
      _logger.debug("Receive packet, type: %s", packet._name)
    except Exception as e:
      import binascii
      _logger.error(e)
      _logger.error(binascii.hexlify(self._buf))
      raise e


class Connector:

  def __init__(self):
    self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    self._sender = _McSender(self._socket)
    self._recver = _McRecver(self._socket)

  def __enter__(self):
    return self

  def __exit__(self, exc_type, exc_value, traceback):
    self.disconnect()

  def connect(self, address):
    try:
      self._socket.connect(address)
      self._socket.settimeout(1.0)
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
    self._recver._msg_queue.put((SET_STATE, state))

  def send_later(self, packet):
    self._sender._msg_queue.put((PACKET, packet))

  def set_auto_recv(self, auto):
    self._recver._msg_queue.put((AUTO_RECV, auto))

  def recv_later(self, n = 1):
    self._recver._msg_queue.put((RECV, n))

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
  connector.recv_later(1)
  response = connector.pop_packet()

  connector.disconnect()
  return json.loads(response.json_response)

def login(host, port, username):
  connector = Connector()

  connected = connector.connect((host, port))
  if not connected:
    return None, None

  connector.send_later(packets.cs_handshake(
      version = 4,
      address = host,
      port = port,
      state = packets.LOGIN_STATE
  ))
  connector.set_state(packets.LOGIN_STATE)
  connector.send_later(packets.cs_login_start(
      name = username
  ))
  connector.recv_later(1)
  packet = connector.pop_packet()
  encrypted = False
  if packet._name == "encryption_request":
    _logger.warning("Encryption not supported.")
    encrypted = True
  elif packet._name == "login_success":
    _logger.info("User {} loged in.".format(username))
  else:
    _logger.error("Unexpected packet type: {}.".format(packet._name))
    raise ValueError("Unexpected packet type.")
  connector.set_state(packets.PLAY_STATE)
  return connector, encrypted

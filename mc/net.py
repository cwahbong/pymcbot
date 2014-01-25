import collections
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

class _McSender(util.Messenger):

  def __init__(self, socket):
    super().__init__("Sender")
    self._socket = socket
    self._state = packets.START_STATE

  def _runcmd(self, cmd, content):
    if cmd == SET_STATE:
      self._state = content
    elif cmd == PACKET:
      raw = packets.pack(content, packets.CLIENT_TO_SERVER, self._state)
      r = self._socket.send(raw)
      if r != len(raw):
        _logger.warning("Num of bytes sent != length or data.")
    else:
      raise ValueError("cmd error in sender")
    return True


class _McRecver(util.Messenger):
  fetch = 4096

  def __init__(self, socket):
    super().__init__("Recver")
    self._need_atleast = 1
    self._need_more = False
    self._drop_auto = False
    self._buf = bytearray()
    self._socket = socket
    self._state = packets.START_STATE
    self._packet_queue = queue.Queue()

  def _recv(self):
    if self._need_more or len(self._buf) == 0:
      try:
        r = self._socket.recv(self.fetch)
        if len(r) == 0:
          _logger.warning("Disconnected by the server.")
          self.stop_later()
        self._buf += r
      except socket.timeout:
        _logger.warning("Socket timeout.")
    if len(self._buf) > 0:
      try:
        self._need_atleast = packets.unpack_peek_size(self._buf)
      except struct.error as e:
        self._need_more = True
        _logger.warning(e)
        return False
    if len(self._buf) < self._need_atleast:
      _logger.debug("Need more data to form a packet.")
      self._need_more = True
      return False
    try:
      packet, size = packets.unpack(self._buf, packets.SERVER_TO_CLIENT, self._state)
      self._buf = self._buf[size:]
      self._packet_queue.put(packet)
      self._need_more = False
      _logger.debug("Receive packet, type: %s", packet._name)
    except Exception as e:
      import binascii
      _logger.error(e)
      _logger.error(binascii.hexlify(self._buf))
      raise e
    return True

  def _runcmd(self, cmd, content):
    if cmd == SET_STATE:
      self._state = content
      _logger.debug("Recver new state: {}.".format(self._state))
    elif cmd == AUTO_RECV:
      self._drop_auto = not content
      if content:
        if self._drop_auto:
          _logger.info("Stop auto recv")
          return
        self._recv()
        self.message(cmd, content)
    elif cmd == RECV:
      if content > 0:
        success = self._recv()
        if not success:
          self.message(cmd, content)
        elif content > 1:
          self.message(cmd, content - 1)
    else:
      raise ValueError("cmd error in recver")
    return True


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
      self._sender.thread.start()
      self._recver.thread.start()
    except socket.error as e:
      _logger.error("Socket: {}.".format(os.strerror(e.args[0])))
      return False
    return True

  def disconnect(self):
    self._sender.stop_later()
    self._sender.thread.join()

    self._recver.stop_later()
    self._recver.thread.join()

    self._socket.shutdown(socket.SHUT_RDWR)
    self._socket.close()

  def set_state(self, state):
    self._sender.message(SET_STATE, state)
    self._recver.message(SET_STATE, state)

  def send_later(self, packet):
    self._sender.message(PACKET, packet)

  def set_auto_recv(self, auto):
    self._recver.message(AUTO_RECV, auto)

  def recv_later(self, n = 1):
    self._recver.message(RECV, n)

  def pop_packet(self):
    def _pop_now():
      if not self._recver._packet_queue.empty():
        return self._recver._packet_queue.get()
      return None
    if not self._recver.thread.is_alive():
      return _pop_now()
    while True:
      try:
        return self._recver._packet_queue.get(timeout=0.5)
      except queue.Empty:
        if not self._recver.thread.is_alive():
          break
    return _pop_now()


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


class Handler:
  def __init__(self, client, connector):
    self._client = client
    self._connector = connector


class KeepAliveHandler(Handler):
  def __init__(self, client, connector):
    super().__init__(client, connector)

  def keep_alive(self, packet):
    ka = packets.cs_keep_alive(keep_alive_id = packet.keep_alive_id)
    self._connector.send_later(ka)
    _logger.debug("Response a keep_alive packet with id {}.".format(
        ka.keep_alive_id
    ))


class _McDispatcher(util.Repeater):

  def __init__(self, client, connector, handler_factories):
    super().__init__("Handler")
    self._connector = connector
    self._handlers = collections.defaultdict(list)
    pids = packets._pid[packets.SERVER_TO_CLIENT, packets.PLAY_STATE]
    for factory in handler_factories:
      handler = factory(client, connector)
      for name in pids.keys():
        if hasattr(handler, name):
           self._handlers[pids[name]].append(handler)

  def _repeated(self):
    packet = self._connector.pop_packet()
    for handler in self._handlers[packet._pid]:
      getattr(handler, packet._name)(packet)
    return True


class Client:

  def __init__(self):
    pass

  def login(self, host, port, username):
    connector, encrypted = login(host, port, username)
    connector.set_auto_recv(True)
    self._dispatcher = _McDispatcher(self, connector, [
        KeepAliveHandler
    ])
    self._dispatcher.thread.start()

  def logout(self):
    self._dispatcher._connector.disconnect()
    self._dispatcher.stop_later()
    self._dispatcher.thread.join()

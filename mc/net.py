import collections
import errno
import json
import logging
import os
import queue
import socket
import struct
import time

from mc.packet import v172 as packets
from mc.handler import v172 as handlers
from mc import util

_logger = logging.getLogger(__name__)

PACKET = "packet"
SET_STATE = "set_state"

RECV = "recv"
AUTO_RECV = "auto_recv"

POSITION = "position"
LOOK = "look"
POSITION_LOOK = "position_look"
POSITION_LOOK_SERVER = "position_look_server"

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


class _McPositioner(util.Messenger):

  def __init__(self, client, connector):
    super().__init__(name = "Positioner", block = False)
    self._client = client
    self._connector = connector
    self.on_ground = None
    self.yaw = None
    self.pitch = None
    self.x = None
    self.y = None
    self.z = None
    self._need_correction = False

  def _runcmd(self, cmd, content):
    if cmd == POSITION:
      # TODO send cs_player_position()
      pass
    elif cmd == LOOK:
      # TODO send cs_player_look()
      pass
    elif cmd == POSITION_LOOK:
      # TODO send cs_player_position_look()
      pass
    elif cmd == POSITION_LOOK_SERVER:
      self._need_correction = True
      self.x = content.x
      self.y = content.y
      self.z = content.z
      self.yaw = content.yaw
      self.pitch = content.pitch
      self.on_ground = content.on_ground
      ppl = packets.cs_player_position_and_look(
        x = self.x,
        feet_y = self.y - 1.62,
        head_y = self.y,
        z = self.z,
        yaw = self.yaw,
        pitch = self.pitch,
        on_ground = self.on_ground,
      )
      self._connector.send_later(ppl)
    time.sleep(0.05)
    return True

  def _empty(self):
    if self.on_ground is None:
      _logger.info("Position not ready.")
    else:
      _logger.info("No position update.")
      self.on_ground = True
      self._connector.send_later(packets.cs_player(
          on_ground = self.on_ground
      ))
    time.sleep(0.05)
    return True

  def need_correction(self):
    return self._need_correction

  def known_correction(self):
    self.need_correction = False


class Actions:
  def __init__(self, client):
    self._client = client
    self._connector = client.connector

  def next_position_look(self,
      x = None, y = None, z = None,
      yaw = None, pitch = None):
    position = (x is not None) or (y is not None) or (z is not None)
    look = (yaw is not None) or (pitch is not None)
    # TODO tell positioner to handle this

  def click_entity(self, entity_id, right_click = False):
    self._connector.send_later(packets.cs_use_entity(
        target = entity_id,
        mouse = int(right_click)
    ))

  def click_block(self, x, y, z, direction, right_click = False):
    if right_click:
      self._connector.send_later(packets.cs_player_block_placement(
        x = x,
        y = y,
        z = z,
        direction = direction,
        # held_item = ,
        # cursor_position_x,
        # cursor_position_y,
        # cursor_position_z,
    ))
    else:
      pass

  def mousedown_block(self, x, y, z, direction, right_click = False):
    pass

  def mouseup_block(self, x, y, z, direction, right_click = False):
    pass

  def click_window(self, slot, right_click = False):
    # TODO need implement action number
    pass

  def close_window(self):
    self._connector.send_later(packets.cs_close_window(
      window_id = self._client.window_stack[-1]
    ))
    if len(self._client.window_stack) > 1:
      self._client.window_stack.pop()

  def drop(self):
    pass


class Client:

  def __init__(self):
    pass

  def login(self, host, port, username):
    connector, encrypted = login(host, port, username)
    connector.set_auto_recv(True)
    self._connector = connector

    self._dispatcher = _McDispatcher(self, connector, [
        handlers.Connection,
        handlers.WorldStatus,
        handlers.PlayerStatus,
        handlers.Block,
        handlers.Window,
        handlers.Entity,
    ])
    self._positioner = _McPositioner(self, connector)

    # thread must started after all field initialized
    self._dispatcher.thread.start()
    self._positioner.thread.start()

    self.actions = Actions(self._connector)

  def logout(self):
    del self.actions
    self._positioner.stop_later()
    self._positioner.thread.join()

    self._dispatcher.stop_later()
    self._dispatcher.thread.join()

    self._connector.disconnect()

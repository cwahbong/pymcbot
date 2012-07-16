import time
import Queue

from mc import net
from mc import handlers
from mc.packets import *
from mc import util
from mc import window


class _Receiver(util.repeater):

  def __init__(self, mcsocket, handlers=[]):
    super(_Receiver, self).__init__(name="Receiver")
    self.__mcsocket = mcsocket
    self.__handlers = handlers

  def repeated(self):
    packet = self.__mcsocket.recvmc()
    if not packet:
      return False
    for handler in self.__handlers:
      if hasattr(handler, "on__packet"):
        handler.on__packet(packet)
      method_name = "on__{}".format(packet.__class__.__name__)
      if hasattr(handler, method_name):
        getattr(handler, method_name)(packet)
    return True


class _Sender(util.repeater):

  def __init__(self, mcsocket):
    super(_Sender, self).__init__(name="Sender")
    self.__mcsocket = mcsocket
    self.__send_queue = Queue.Queue()

  def repeated(self):
    try:
      packet = self.__send_queue.get_nowait()
      self.__mcsocket.sendmc(packet)
      self.__send_queue.task_done()
    except Queue.Empty:
      time.sleep(0.1)
    return True
      
    """position_changed = self.__client.next_position != self.__client.position
    look_changed = self.__client.next_look != self.__client.look
    info = {"on_ground", self.__client.on_ground}
    if position_changed:
      info.update(self.__client.next_position)
    if look_changed:
      info.update(self.__client.next_look)
    if position_changed:
      if look_changed:
        self.__client._socket.sendmc(player_position_look(**info))
      else:
        self.__client._socket.sendmc(player_position(**info))
    else:
      if look_changed:
        self.__client._socket.sendmc(player_look(**info))
      else:
        self.__client._socket.sendmc(player(**info))
    """

  def send_later(self, packet):
    self.__send_queue.put(packet)


class Client(object):

  def __init__(self, packet_handlers = []):
    packet_handlers += [
        handlers.keep_alive(self),
        handlers.position_look(self),
        handlers.slot(self),
        handlers.Window(self)
    ]
    self.__socket = net.mcsocket()
    self.__sender = _Sender(self.__socket)
    self.__receiver = _Receiver(self.__socket, packet_handlers)
    self.__workers = [
        self.__receiver,
        self.__sender,
    ]
    self.on_ground = True
    self.position = {}
    self.look = {}
    self.entities = []
    self.inventory = []
    self.holds = []
    self.next_position = {}
    self.next_look = {}
    self.window_id = 0
    self.window_type = -1
    self.other_size = 0
    self.main_inventory = None
    self.held_items = None
    # self._slots = None
    self._mouse_hold = {"id": -1}
    self._tid = 1

  def __enter__(self):
    return self

  def __exit__(self, type, value, traceback):
    self.logout(message="Bot logs out automatically.")
    return False

  def _send(self, packet):
    self.__sender.send_later(packet)

  def login(self, host, port, user, password=""):
    self.__socket.connect((host, port))
    for worker in self.__workers:
      worker.start()
    while not self.__receiver.is_alive():
      time.sleep(1)
    self._send(handshake(username_host="{};{}:{}".format(user, host, port)))
    self._send(login_request(version=29, username=user))

  def logout(self, message):
    self._send(disconnect(reason=message))
    for worker in self.__workers:
      worker.stop_later()
      worker.join()
    self.__socket.close()


class Robot(Client):

  def __init__(self):
    super(Robot, self).__init__()

  def craft(self, input):
    pass

  def wear(self, head=None, chest=None, legs=None, feet=None):
    pass

  def unwear(self, head=False, chest=False, legs=False, feet=False):
    pass

  def next_look_position(self, look=None, position=None):
    pass

  def dig(self, position):
    pass
  
  def put(self, position, direction):
    pass

  def open(self, **position):
    """ open a chest...
    """
    info = dict(**position)
    info["direction"] = 0
    info["held_item"] = None
    old_id = self.window_id
    self._send(player_block_placement(**info))
    while old_id==self.window_id:
      time.sleep(0.1)

  def close(self, wait=0.1):
    """ close the thing you are opening...
    """
    if self.window_id:
      self._send(close_window(window_id=self.window_id))
    self.window_id = 0
    self.window_type = -1
    print "CLOSE"
    time.sleep(wait)


  def _confirm_transaction(self, action_number):
    time.sleep(0.1)
    pass

  def _update_slots(self, where, where_id, right):
    def swap():
      self._mouse_hold, getattr(self, where)[where_id] = getattr(self, where)[where_id], self._mouse_hold
    dest = getattr(self, where)[where_id]
    if right:
      if self._mouse_hold["id"]!=-1:
        if dest["id"]==-1:
          print "right click to new"
          dest["id"] = self._mouse_hold["id"]
          dest["count"] = 1
          dest["damage"] = self._mouse_hold["damage"]
          self._mouse_hold["count"] -= 1
        elif self._mouse_hold["id"]==dest["id"] and "count" in dest:
          print "right click - 1"
          dest["count"] += 1
          self._mouse_hold["count"] -= 1
        else:
          print "right click diff"
          swap()
        if self._mouse_hold["count"]==0:
          self._mouse_hold = {"id": -1}
      else:
        # TODO take half, the amout of you take would be bigger if the amount of stack is odd
        raise NotImplementedError
    else:
      if self._mouse_hold["id"]==dest["id"]:
        if self._mouse_hold["id"]!=-1:
          print "left click same"
          if dest["count"]==64:
            swap()
          else:
            give = min(64-dest["count"], self._mouse_hold["id"])
            if self._mouse_hold["count"]==give:
              self._mouse_hold = {"id": -1}
            else:
              self._mouse_hold["count"] -= give
            dest["count"] += give
      else:
        print "left click diff"
        swap()

  def click(self, where, where_id=0, right=False, shift=False):
    right = 1 if right else 0
    print "O", self.other_size
    print "WT", self.window_type
    slot_id = window.slot_id(self.window_type, where, where_id, self.other_size)
    print "S", slot_id
    print "W", where, getattr(self, where), self._tid
    self._send(click_window(window_id=self.window_id, slot=slot_id, right_click=right, action_number=self._tid, shift=shift, clicked_item=getattr(self, where)[where_id]))
    self._confirm_transaction(self._tid)
    self._tid += 1
    self._update_slots(where, where_id, right)

  def swap_slot(self, slot_id_1, slot_id_2):
    self.click(slot_id_1)
    self.click(slot_id_2)
    self.click(slot_id_1)

  def get_stack_num(self, item_id):
    pass

  def send_message(self, message):
    self._send(chat_message(message=message))



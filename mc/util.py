import queue
import threading

STOP = "stop"

class Repeater(threading.Thread):

  def __init__(self, name = None):
    super().__init__(name = name)
    self._msg_queue = queue.Queue()

  def run(self):
    while True:
      if not self._msg_queue.empty():
        cmd, content = self._msg_queue.get()
        if cmd == STOP:
          break
        self.runcmd(cmd, content)
      else:
        self.noncmd()
    print("{} stopped".format(self.name))

  def stop_later(self):
    self._msg_queue.put((STOP, None))


class IdManager(object):

  def __init__(self, module=None):
    self.__name = {}
    self.__type_id = {}
    if module:
      setattr(module, "name", self.name)
      setattr(module, "type_id", self.type_id)

  def name(self, type_id):
    return self.__name[type_id]

  def type_id(self, name):
    return self.__type_id[name]

  def register(self, type_id, name):
    self.__name[type_id] = name
    self.__type_id[name] = type_id

  def list_register(self, tuple_list):
    for t in tuple_list:
      self.register(*t)



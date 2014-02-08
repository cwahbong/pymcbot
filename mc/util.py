import logging
import queue
import threading

_logger = logging.getLogger(__name__)

STOP = "stop"

class Repeater:

  def __init__(self, name):
    self.name = name
    self.thread = threading.Thread(
        target = self,
        name = self.name
    )

  def _repeated(self):
    raise NotImplementedError()

  def __call__(self):
    while self._repeated():
      pass
    _logger.info("Repeater \"{}\" stopped.".format(self.name))


class Messenger(Repeater):

  def __init__(self, name = None, block = True, timeout = None):
    super().__init__(name = name)
    self._msg_queue = queue.Queue()
    self._block = block
    self._timeout = timeout

  def message(self, cmd, content):
    self._msg_queue.put((cmd, content))

  def _repeated(self):
    try:
      cmd, content = self._msg_queue.get(self._block, self._timeout)
      return False if cmd == STOP else self._runcmd(cmd, content)
    except queue.Empty:
      return self._empty()

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


def logConfig(filename = None, stream = None):
  logger = logging.getLogger()
  logger.setLevel(logging.DEBUG)
  formatter = logging.Formatter(
      "%(asctime)s - %(levelname)s - T\"%(threadName)s\""
      " - N\"%(name)s\" - %(message)s"
  )
  if filename is not None:
    fileHandler = logging.FileHandler(filename)
    fileHandler.setLevel(logging.DEBUG)
    fileHandler.setFormatter(formatter)
    logger.addHandler(fileHandler)
  if stream is not None:
    streamHandler = logging.StreamHandler(stream)
    streamHandler.setLevel(logging.WARNING)
    streamHandler.setFormatter(formatter)
    logger.addHandler(streamHandler)

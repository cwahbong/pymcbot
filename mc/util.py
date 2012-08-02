import re
import struct
import threading
from fields import *

class repeater(threading.Thread):

  def __init__(self, name=None):
    super(repeater, self).__init__(name=name)
    self.__stop = False

  def repeated(self):
    raise NotImplementedError

  def run(self):
    while not self.__stop and self.repeated():
      pass
    print "{} stopped".format(self.name)

  def stop_later(self):
    self.__stop = True

import functools

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



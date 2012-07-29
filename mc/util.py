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


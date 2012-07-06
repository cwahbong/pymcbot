import threading
import time

from mc import net
from mc import handlers
from mc.packets import *

class receiver(threading.Thread):

  def __init__(self, mcsocket, handlers=[]):
    super(receiver, self).__init__(name="Receiver")
    self.__socket = mcsocket
    self.__stop = False
    self.__handlers = handlers

  def run(self):
    packet = self.__socket.recvmc()
    while not self.__stop and packet:
      for handler in self.__handlers:
        method_name = "on__{}".format(packet.__class__.__name__)
        if hasattr(handler, method_name):
          getattr(handler, method_name)(packet)
      packet = self.__socket.recvmc()
    print "stopped"

  def stop_later(self):
    self.__stop = True


class client(object):

  def __init__(self, handler_list = []):
    self._socket = net.mcsocket()
    self.__receiver = receiver(self._socket, handler_list)

  def __enter__(self):
    return self

  def __exit__(self, type, value, traceback):
    self.logout(message="Bot logs out automatically.")
    return False

  def login(self, host, port, user, password=""):
    self._socket.connect((host, port))
    self.__receiver.start()
    while not self.__receiver.is_alive():
      time.sleep(1)
    self._socket.sendmc(handshake(username_host="{};{}:{}".format(user, host, port)))
    self._socket.sendmc(login_request(version=29, username=user))

  def logout(self, message):
    self._socket.sendmc(disconnect(reason=message))
    self.__receiver.join()
    self._socket.close()



class robot(client):

  def __init__(self):
    super(robot, self).__init__(handler_list = [
        handlers.keep_alive(self)
    ])

  def send_message(self, message):
    self._socket.sendmc(chat_message(message=message))



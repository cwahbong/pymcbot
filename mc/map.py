""" Map types.
    3D - World
    2D - Plain
    1D - Column
    0D - Block
    Use subscript operator of nD object to get (n-1)D object.
    Note that subscript operator will create object if the given value
    of axis does not exist in the object.
"""


class Block(object):
  """ A block in a map.
  """

  def __init__(self):
    self.type = -1
    self.metadata = -1
    self.light = -1
    self.sky_light = -1


class Column(object):
  """ Give value of Y axis to get a Block.
      Biome also recorded in this class.
      Direction: Y
  """

  def __init__(self):
    self.biome = -1
    self.__y = {}

  def __contains__(self, key):
    return key in self.__y

  def __getitem__(self, key):
    if key not in self.__y:
      self.__y[key] = Block()
    return self.__y[key]

  def __setitem__(self, key, value):
    self.__y[key] = value

  def __delitem__(self, key):
    del self.__y[key]


class Plain(object):
  """ A plain with fixed X axis.
      Give value of Z axis with subscript operator to get a Column.
      Direction: ZY
  """

  def __init__(self):
    self.__zy = {}

  def __contains__(self, key):
    return key in self.__zy

  def __getitem__(self, key):
    if key not in self.__zy:
      self.__zy[key] = Column()
    return self.__zy[key]

  def __setitem__(self, key, value):
    self.__zy[key] = value

  def __delitem__(self, key):
    del self.__zy[key]


class World(object):
  """ Give value of X axis with subscript operator to get a Plain.
      Direction: XZY
  """

  def __init__(self):
    self.__xzy = {}

  def __contains__(self, key):
    return key in self.__xzy

  def __getitem__(self, key):
    if key not in self.__xzy:
      self.__xzy[key] = Plain()
    return self.__xzy[key]

  def __setitem__(self, key, value):
    self.__xzy[key] = value

  def __delitem__(self, key):
    del self.__xzy[key]


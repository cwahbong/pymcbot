class Windows:
  def __init__(self):
    self.stack = list()
    self.by_id = dict()

  def add(self, window):
    self.stack.append(window)
    self.by_id[window.id] = window

  def pop(self, window_id = None):
    if window_id is not None and self.stack[-1].id != window_id:
      logging.warning("Popping non top window.")
    del self.by_id[self.stack[-1].id]
    self.stack.pop()


SELF = -1
CHEST = 0
WORKBENCH = 1
FURNACE = 2
DISPENSER = 3
ENCHANTMENT_TABLE = 4

_self_layout = (
    ("main_inventory", (-36, 27)),
    ("held", (-9, 9)),
)

_layouts = {
    SELF: (
        ("crafting_output", (0, 1)),
        ("crafting_input", (1, 4)),
        ("armor", (5, 4)),
        # alias
        ("armor_head", (5, 1)),
        ("armor_chest", (6, 1)),
        ("armor_legs", (7, 1)),
        ("armor_feet", (8, 1)),
    ),
    CHEST: (
        ("chest", (0, -1)),
    ),
    WORKBENCH: (
        ("crafting_output", (0, 1)),
        ("crafting_input", (1, 9)),
    ),
    FURNACE: (
        ("above_flame", (0, 1)),
        ("fuel", (1, 1)),
        ("output", (2, 1)),
    ),
    DISPENSER: (
        ("content", (0, 9)),
    ),
    ENCHANTMENT_TABLE: (
        ("enchantment_slot", (0, 1)),
    ),
}


class Window:

  def __init__(self, wtype, wid):
    self.type = wtype
    self.id = wid
    self.properties = dict()
    self.slots = list()
    if wtype not in _layouts:
      _logger.warning("window")
    self._slot_d = dict(_layouts[wtype])
    self._slot_d.update(_self_layout)

  def slot(self, name, n = 0):
    start, limit = self._slot_d[name]
    if n >= limit:
      raise ValueError("limit exceeded")
    if start < 0:
      start += len(self.slots)
    return start + n

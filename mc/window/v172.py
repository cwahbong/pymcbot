
class Window:

  def __init__(self):
    self.slots = list()

    # TODO set alias by _layout


class Inventory(Window):
  _layout = (
      ("crafting_output", 1),
      ("crafting_input", 4),
      ("armor", 4),
      ("main_inventory", 27),
      ("held", 9),
  )

  def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)


class Crafting(Window):
  _layout = (
      ("crafting_output", 1),
      ("crafting_input", 9),
      ("main_inventory", 27),
      ("held", 9),
  )

  def __init__(self, *args, **kwargs):
   super().__init__(*args, **kwargs)


_id_table = {
    -1: Inventory,
    # 0: Chest,
    1: Crafting,
}

def new_by_type_id(type_id):
  return _id_table[type_id]()

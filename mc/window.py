SELF = -1
CHEST = 0
WORKBENCH = 1
FURNACE = 2
DISPENSER = 3
ENCHANTMENT_TABLE = 4

__self = [
    ("main_inventory", 27),
    ("held_items", 9)
]

layout = {
    SELF: [
        ("crafting_output", 1),
        ("crafting_input", 4),
        ("armor", 4),
    ] + __self,
    CHEST: [
        ("chest", -1), 
    ] + __self,
    WORKBENCH: [
        ("crafting_output", 1),
        ("crafting_input", 9),
    ] + __self,
    FURNACE: [
        ("above flame", 1),
        ("fuel", 1),
        ("output", 1),
    ] + __self,
    DISPENSER: [
        ("content", 9),
    ] + __self,
    ENCHANTMENT_TABLE: [
        ("enchantment_slot", 1),
    ] + __self,
}

def slot_id(window_type, where, where_id, other_size=0):
  idx = 0
  for attr, num in layout[window_type]:
    if attr==where:
      return idx + where_id
    else:
      num = other_size if num<0 else num
      idx += num
  else:
    raise ValueErrorException


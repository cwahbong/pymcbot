""" We define the name and type id of mobs here.
"""

__name = {}
__type_id = {}

def name(type_id):
  return __name[type_id]

def type_id(name):
  return __type_id[name]

def register(type_id, name):
  __name[type_id] = name
  __type_id[name] = type_id

def list_register(tuple_list):
  for t in tuple_list:
    register(*t)

list_register([
    (50, "creeper"),
    (51, "skeleton"),
    (52, "spider"),
    (53, "giant_zombie"),
    (54, "zombie"),
    (55, "slime"),
    (56, "ghast"),
    (57, "zombie_pigman"),
    (58, "enderman"),
    (59, "cave_spider"),
    (60, "silverfish"),
    (61, "blaze"),
    (62, "magma_cube"),
    (63, "ender_dragon"),
    (90, "pig"),
    (91, "sheep"),
    (92, "cow"),
    (93, "chicken"),
    (94, "squid"),
    (95, "wolf"),
    (96, "mooshroom"),
    (97, "snowman"),
    (98, "ocelot"),
    (99, "iron_folem"),
    (120, "villager"),
])


import sys
from mc import util

__id_manager = util.IdManager(sys.modules[__name__])

__id_manager.list_register([
    (01, "boat"),
    (10, "minecart"),
    (11, "minecart_storage"),
    (12, "minecart_powered"),
    (50, "activated_tnt"),
    (51, "ender_crystal"),
    (60, "arrow"),
    (61, "snowball"),
    (62, "egg"),
    (70, "falling_objects"),
    (72, "eye_of_ender"),
    (74, "falling_dragon_egg"),
    (90, "fishing_float"),
])


from mc.fields import *


_fields = {
    "c2s": {},
    "s2c": {},
}

_kwset = {
    "c2s": {},
    "s2c": {},
}

_name = {}

_id = {}


class Packet(object):
  
  def __init__(self, direction, name, **field_info):
    self.id = _id[name]
    kwset = _kwset[direction][self.id]
    for field_name, field_content in field_info.items():
      if field_name in kwset:
        setattr(self, field_name, field_content)
      else:
        raise ValueError("``{}'' is not a valid field name.".format(field_name))


def pack(packet):
  result = UnsignedByte.pack(packet.id)
  for field_type, field_name in _fields[direction][packet.id]:
    field_content = getattr(packet, field_name, None)
    result += field_type.pack(field_content)
  return result


def unpack(rawstring, direction, offset=0):
    id, offset = UnsignedByte.unpack(rawstring, offset)
    field_info = {}
    for field_type, field_name in _fields[direction][id]:
      field_content, offset = field_type.unpack(rawstring, offset)
      field_info[field_name] = field_content
    return Packet(direction, _name[id], **field_info), offset


def register(id, direction, name, fields):
  if direction=="both":
    register(id, "c2s", name, fields)
    register(id, "s2c", name, fields)
  else:
    if direction not in ("c2s", "s2c"):
      raise ValueError("Not a valid direction: {}".format(direction))
    _fields[direction][id] = fields
    _kwset[direction][id] = set(map(lambda p: p[1], fields))
    _name[id] = name
    _id[name] = id

__entity = [(Int, "eid")]
__entity_relative_move = [
    (Byte,          "dx"),
    (Byte,          "dy"),
    (Byte,          "dz"),
]
__entity_look = [
    (Byte,          "yaw"),
    (Byte,          "pitch"),
]
__window = [(Byte, "window_id")]

register(0x00, "both", "keep_alive", [(Int, "keepalive_id")])
register(0x01,  "c2s", "login_request", [
    (Int,           "version"),
    (String,        "username"),
    (String,        ""),
    (Int,           ""),
    (Int,           ""),
    (Byte,          ""),
    (UnsignedByte,  ""),
    (UnsignedByte,  ""),
])
register(0x01,  "s2c", "login_request",  __entity + [
    (String,        ""),
    (String,        "level_type"),
    (Int,           "server_mode"),
    (Int,           "dimension"),
    (Byte,          "difficulty"),
    (UnsignedByte,  ""),
    (UnsignedByte,  ""),
])
register(0x02, "c2s",  "handshake", [(String, "username_host")])
register(0x02, "s2c",  "handshake", [(String, "connection_hash")])
register(0x03, "both", "chat_message", [(String, "message")])
register(0x04, "both", "time_update", [(Long, "time")])
register(0x05, "s2c",  "entity_equipment", __entity + [
    (Short,         "slot"),
    (Short,         "item_id"),
    (Short,         "damage"),
])
register(0x06, "s2c",  "spawn_position", [
    (Int,           "x"),
    (Int,           "y"),
    (Int,           "z"),
])
register(0x07, "c2s",  "use_entity", [
    (Int,           "user"),
    (Int,           "target"),
    (Bool,          "mouse_button"),
])
register(0x08, "s2c",  "update_health", [
    (Short,         "health"),
    (Short,         "food"),
    (Float,         "food_saturation"),
])
register(0x09, "both", "respawn", [
    (Int,           "dimension"),
    (Byte,          "difficulty"),
    (Byte,          "creative_mode"),
    (Short,         "world_height"),
    (String,        "level_type"),
])
__player = [(Bool, "on_ground")]
register(0x0A, "c2s",  "player", __player)
register(0x0B, "c2s",  "player_position", [
    (Double,        "x"),
    (Double,        "y"),
    (Double,        "stance"),
    (Double,        "z"),
] + __player)
register(0x0C, "c2s",  "player_look", [
    (Float,         "yaw"),
    (Float,         "pitch"),
] + __player)
register(0x0D, "c2s",  "player_position_look", [
    (Double,        "x"),
    (Double,        "y"),
    (Double,        "stance"),
    (Double,        "z"),
    (Float,         "yaw"),
    (Float,         "pitch"),
] + __player)
register(0x0D, "s2c",  "player_position_look", [
    (Double,        "x"),
    (Double,        "stance"),
    (Double,        "y"),
    (Double,        "z"),
    (Float,         "yaw"),
    (Float,         "pitch"),
] + __player)
register(0x0E, "c2s",  "player_digging", [
    (Byte,          "status"),
    (Int,           "x"),
    (Byte,          "y"),
    (Int,           "z"),
    (Byte,          "face"),
])
register(0x0F, "c2s",  "player_block_placement", [
    (Int,           "x"),
    (Byte,          "y"),
    (Int,           "z"),
    (Byte,          "direction"),
    (Slot,          "held_item"),
])
register(0x10, "c2s",  "held_item_change", [(Short, "slot_id")])
register(0x11, "s2c",  "use_bed", __entity + [
    (Byte,          ""), # unknown
    (Int,           "x"),
    (Byte,          "y"),
    (Int,           "z"),
])
register(0x12, "both", "animation", __entity + [
    (Byte,          "animation"),
])
register(0x13, "c2s",  "entity_action", __entity + [
    (Byte,          "action_id"),
])
register(0x14, "s2c",  "spawn_named_entity", __entity + [
    (String,        "player_name"),
    (Int,           "x"),
    (Int,           "y"),
    (Int,           "z"),
    (Byte,          "yaw"),
    (Byte,          "pitch"),
    (Short,         "current_item"),
])
register(0x15, "s2c",  "spawn_dropped_item", __entity + [
    (Short,         "item"),
    (Byte,          "count"),
    (Short,         "damage_data"),
    (Int,           "x"),
    (Int,           "y"),
    (Int,           "z"),
    (Byte,          "rotation"),
    (Byte,          "pitch"),
    (Byte,          "roll"),
])
register(0x16, "s2c",  "collect_item", [
    (Int,           "collected_eid"),
    (Int,           "collector_eid"),
])
register(0x17, "s2c",  "spawn_object_vehicle", __entity + [
    (Byte,          "type"),
    (Int,           "x"),
    (Int,           "y"),
    (Int,           "z"),
    (Object,        "additional_data"), # TODO
])
"""(Int,         "fireball_thrower_eid"),
(("h", "?fireball_thrower_eid"), "sx"),
(("h", "?fireball_thrower_eid"), "sy"),
(("h", "?fireball_thrower_eid"), "sz"),"""
register(0x18, "s2c",  "spawn_mob", __entity + [
    (Byte,          "type"),
    (Int,           "x"),
    (Int,           "y"),
    (Int,           "z"),
    (Byte,          "yaw"),
    (Byte,          "pitch"),
    (Byte,          "head_yaw"),
    (MetaData,      "metadata"),
])
register(0x19, "s2c",  "spawn_painting", __entity + [
    (String,        "title"),
    (Int,           "x"),
    (Int,           "y"),
    (Int,           "z"),
    (Int,           "direction"),
])
register(0x1A, "s2c",  "spawn_experience_orb",  __entity + [
    (Int,           "x"),
    (Int,           "y"),
    (Int,           "z"),
    (Short,         "count"),
])
register(0x1C, "s2c",  "entity_velocity", __entity + [
    (Short,         "vx"),
    (Short,         "vy"),
    (Short,         "vz"),
])
register(0x1D, "s2c",  "destroy_entity", __entity)
register(0x1E, "s2c",  "entity",  __entity)
register(0x1F, "s2c",  "entity_relative_move", __entity + __entity_relative_move)
register(0x20, "s2c",  "entity_look", __entity + __entity_look)
register(0x21, "s2c",  "entity_relative_move_look", __entity + __entity_relative_move + __entity_look)
register(0x22, "s2c",  "entity_teleport", __entity + [
    (Int, "x"),
    (Int, "y"),
    (Int, "z"),
] + __entity_look)
register(0x23, "s2c",  "entity_head_look", __entity + [(Byte, "head_yaw")])
register(0x26, "s2c",  "entity_status", __entity + [(Byte, "entity_statys")])
register(0x27, "s2c",  "attach_entity", __entity + [(Int, "vehical_id")])
register(0x28, "s2c",  "entity_metadata", __entity + [(MetaData, "metadata")])
register(0x29, "s2c",  "entity_effect", __entity + [
    (Byte,          "effect_id"),
    (Byte,          "amplifier"),
    (Short,         "duration"),
])
register(0x2A, "s2c",  "remove_entity_effect", __entity + [(Byte, "effect_id")])
register(0x2B, "s2c",  "set_experience", [
    (Float,         "experience_bar"),
    (Short,         "level"),
    (Short,         "total_experience"),
])
register(0x32, "s2c",  "map_column_allocation", [
    (Int,           "x"),
    (Int,           "z"),
    (Bool,          "mode"),
])
register(0x33, "s2c",  "chunk_data", [
    (Int,           "x"),
    (Int,           "z"),
    (Bool,          "ground_up_continues"),
    (UnsignedShort, "primary_bit_map"),
    (UnsignedShort, "add_bit_map"),
    (Int,           "compressed_size"),
    (Int,           ""),
    (Array(UnsignedByte, "compressed_size"),
                    "compressed_data"),
])
register(0x34, "s2c",  "multi_block_change", [
    (Int,           "cx"),
    (Int,           "cz"),
    (Short,         "record_count"),
    (Int,           "data_size"),
    (Array(Byte, "data_size"),
                    "data"),
])
register(0x35, "s2c",  "block_change", [
    (Int,           "x"),
    (Byte,          "y"),
    (Int,           "z"),
    (Byte,          "block_type"),
    (Byte,          "block_metadata"),
])
register(0x36, "s2c",  "block_action", [
    (Int,           "x"),
    (Short,         "y"),
    (Int,           "z"),
    (Byte,          "byte1"),
    (Byte,          "byte2"),
])
register(0x3C, "s2c",  "explosion", [
    (Double,        "x"),
    (Double,        "y"),
    (Double,        "z"),
    (Float,         "radius"),
    (Int,           "record_count"),
    (Array(Record, "record_count"),
                    "records"),
])
register(0x3D, "s2c",  "sound_partical_effect", __entity + [
    (Int,           "x"),
    (Byte,          "y"),
    (Int,           "z"),
    (Int,           "data"),
])
register(0x46, "s2c",  "change_game_state", [
    (Byte,          "reason"),
    (Byte,          "game_mode"),
])
register(0x47, "s2c",  "thunderbolt", __entity + [
    (Byte,          ""),
    (Int,           "x"),
    (Int,           "y"),
    (Int,           "z"),
])
register(0x64, "s2c",  "open_window", __window + [
    (Byte,          "inventory_type"),
    (String,        "window_title"),
    (Byte,          "number_of_slots"),
])
register(0x65, "both", "close_window", __window)
register(0x66, "c2s",  "click_window", __window + [
    (Short,         "slot"),
    (Byte,          "right_click"),
    (Short,         "action_number"),
    (Bool,          "shift"),
    (Slot,          "clicked_item"),
])
register(0x67, "s2c",  "set_slot", __window + [
    (Short,         "slot"),
    (Slot,          "slot_data"),
])
register(0x68, "s2c",  "set_window_items", __window + [
    (Short,         "count"),
    (Array(Slot, "count"),
                    "slot_data"),
])
register(0x69, "s2c",  "update_window_property", __window + [
    (Short,         "property"),
    (Short,         "value"),
])
register(0x6A, "both", "confirm_transaction", __window + [
    (Short,         "action_number"),
    (Bool,          "accepted"),
])
register(0x6B, "both", "creative_inventory_action", [
    (Short,         "slot"),
    (Slot,          "clicked_item"),
])
register(0x6C, "c2s",  "enchant_item", __window + [
    (Byte,          "enchantment"),
])
register(0x82, "both", "update_sign", [
    (Int,           "x"),
    (Short,         "y"),
    (Int,           "z"),
    (String,        "text1"),
    (String,        "text2"),
    (String,        "text3"),
    (String,        "text4"),
])
register(0x83, "s2c",  "item_data", [
    (Short,         "item_type"),
    (Short,         "item_id"),
    (UnsignedByte,  "text_length"),
    (Array(Byte, "text_length"),
                    "text"),
])
register(0x84, "s2c",  "update_title_entity", [
    (Int,           "x"),
    (Short,         "y"),
    (Int,           "z"),
    (Byte,          "action"),
    (Int,           "custom1"),
    (Int,           "custom2"),
    (Int,           "custom3"),
])
register(0xC8, "s2c",  "increment_statistic", [
    (Int,           "statistic_id"),
    (Byte,          "amount"),
])
register(0xC9, "s2c",  "player_list_item", [
    (String,        "player_name"),
    (Bool,          "online"),
    (Short,         "ping"),
])
register(0xCA, "both", "player_abilities", [
    (Bool,          "invulnerabile"),
    (Bool,          "flying"),
    (Bool,          "flyable"),
    (Bool,          "instant_destroy"),
])
register(0xFA, "both", "plugin_message", [
    (String,        "channel"),
    (Short,         "length"),
    (Array(Byte, "length"),
                    "data")
])
register(0xFE, "c2s",  "server_list_ping", [])
register(0xFF, "both", "disconnect", [(String, "reason")])



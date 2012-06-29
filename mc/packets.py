import struct

 
def pack(packet):
  result = struct.pack("!B", packet.id)
  for d in packet.get_datatable():
    attr = getattr(packet, d[1], None)
    if d[0] in ("ba", "Ba", "Ta"): # array
      raise NotImplementedError
    if d[0]=="S": # utf 16 be string
      attr = "" if attr is None else attr
      utf16_attr = attr.encode("utf_16_be")
      result += struct.pack("!h", len(attr))
      result += struct.pack("!{}s".format(len(utf16_attr)), utf16_attr)
    elif d[0]=="T": # slot
      raise NotImplementedError
    elif d[0]=='M': # metadata
      raise NotImplementedError
    elif d[0] in "bB?hHiIlLfd":
      attr = 0 if attr is None else attr
      result += struct.pack("!{}".format(d[0]), attr)
    else:
      raise ValueError("Invalid data type '{}'".format(d[0]))
  return result
  
def unpack(rawstring, direction):
  # 1. find all class in this module, match id.
  # 2. unpack data with specific data table.
  pass


class packet(object):
  id = -1

  def __init__(self, direction, **kwargs):
    if direction not in ("c2s", "s2c"):
      raise ValueError("Direction invalid.")
    self.direction = direction
    for (_, attrname) in filter(lambda d: d[1], self.get_datatable()):
      setattr(self, attrname, kwargs[attrname])

  def get_datatable(self):
    return getattr(self.__class__, "data_{}".format(self.direction))
  

class keep_alive(packet):
  id = 0x00
  data_c2s = data_s2c = (("i", "keepalive_id"), )


class login_request(packet):
  id = 0x01
  data_c2s = (
      ("i", "version"),
      ("S", "username"),
      ("S", ""),
      ("i", ""),
      ("i", ""),
      ("b", ""),
      ("B", ""),
      ("B", ""),
  )
  data_s2c = (
      ("i", "eid"),
      ("S", ""),
      ("S", "level_type"),
      ("i", "server_mode"),
      ("i", "dimension"),
      ("b", "difficulty"),
      ("B", ""),
      ("B", "max_players"),
  )


class handshake(packet):
  id = 0x02
  data_c2s = (("S", "username_host"), )
  data_s2c = (("S", "connection_hash"), )


class chat_message(packet):
  id = 0x03
  data_c2s = data_s2c = (("S", "message"), )


class time_update(packet):
  id = 0x04
  data_c2s = data_s2c = (("q", "time"), )


class entity_equipment(packet):
  id = 0x05
  data_s2c = (
      ("i", "eid"),
      ("h", "slot"),
      ("h", "item_id"),
      ("h", "damage"),
  )


class spawn_position(packet):
  id = 0x06
  data_s2c = (
      ("i", "x"),
      ("i", "y"),
      ("i", "z"),
  )


class use_entity(packet):
  id = 0x07
  data_c2s = (
      ("i", "user"),
      ("i", "target"),
      ("?", "mouse_button"),
  )


class update_health(packet):
  id = 0x08
  data_s2c = (
      ("h", "health"),
      ("h", "food"),
      ("f", "food_saturation"),
  )


class respawn(packet):
  id = 0x09
  data_c2s = data_s2c = (
      ("i", "dimension"),
      ("b", "difficulty"),
      ("b", "creative_mode"),
      ("h", "world_height"),
      ("S", "level_type"),
  )


class player(packet):
  id = 0x0A
  data_c2s = (("?", "on_ground"), )


class player_position(player):
  id = 0x0B
  data_c2s = (
      ("d", "x"),
      ("d", "y"),
      ("d", "stance"),
      ("d", "z"),
  ) + player.data_c2s


class player_look(player):
  id = 0x0C
  data_c2s = (
      ("f", "yaw"),
      ("f", "pitch"),
  ) + player.data_c2s


class player_position_look(player):
  id = 0x0D
  data_c2s = (
      ("d", "x"),
      ("d", "y"),
      ("d", "stance"),
      ("d", "z"),
      ("f", "yaw"),
      ("f", "pitch"),
  ) + player.data_c2s
  data_s2c = (
      ("d", "x"),
      ("d", "stance"),
      ("d", "y"),
      ("d", "z"),
      ("f", "yaw"),
      ("f", "pitch"),
  ) + player.data_c2s


class player_digging(packet):
  id = 0x0E
  data_c2s = (
      ("b", "status"),
      ("i", "x"),
      ("b", "y"),
      ("i", "z"),
      ("b", "face"),
  )


class player_block_placement(packet):
  id = 0x0F
  data_c2s = (
      ("i", "x"),
      ("b", "y"),
      ("i", "z"),
      ("b", "direction"),
      ("T", "held_item"),
  )


class held_item_change(packet):
  id = 0x10
  data_c2s = (("h", "slot_id"), )


class use_bed(packet):
  id = 0x11
  data_s2c = (
      ("i", "eid"),
      ("b", ""), # unknown
      ("i", "x"),
      ("b", "y"),
      ("i", "z"),
  )


class animation(packet):
  id = 0x12
  data_c2s = data_s2c = (
      ("i", "eid"),
      ("b", "animation"),
  )


class entity_action(packet):
  id = 0x13
  data_c2s = (
      ("i", "eid"),
      ("b", "action_id"),
  )


class spawn_named_entity(packet):
  id = 0x14
  data_s2c = (
      ("i", "eid"),
      ("S", "player_name"),
      ("i", "x"),
      ("i", "y"),
      ("i", "z"),
      ("b", "yaw"),
      ("b", "pitch"),
      ("h", "current_item"),
  )


class spawn_dropped_item(packet):
  id = 0x15
  data_s2c = (
      ("i", "eid"),
      ("h", "item"),
      ("b", "count"),
      ("h", "damage_data"),
      ("i", "x"),
      ("i", "y"),
      ("i", "z"),
      ("b", "rotation"),
      ("b", "pitch"),
      ("b", "roll"),
  )


class collect_item(packet):
  id = 0x16
  data_s2c = (
      ("i", "collected_eid"),
      ("i", "collector_eid"),
  )


class spawn_object_vehicle(packet):
  id = 0x17
  data_s2c = (
      ("i", "eid"),
      ("b", "type"),
      ("i", "x"),
      ("i", "y"),
      ("i", "z"),
      ("i", "fireball_thrower_eid"),
      ("h", "sx"),
      ("h", "sy"),
      ("h", "sz"),
  )


class spawn_mob(packet):
  id = 0x18
  data_s2c = (
      ("i", "eid"),
      ("b", "bype"),
      ("i", "x"),
      ("i", "y"),
      ("i", "z"),
      ("b", "yaw"),
      ("b", "pitch"),
      ("b", "head_yaw"),
      ("M", "metadata"),
  )


class spawn_painting(packet):
  id = 0x19
  data_s2c = (
      ("i", "eid"),
      ("S", "title"),
      ("i", "x"),
      ("i", "y"),
      ("i", "z"),
      ("i", "direction"),
  )


class spawn_experience_orb(packet):
  id = 0x1A
  data_s2c = (
      ("i", "eid"),
      ("i", "x"),
      ("i", "y"),
      ("i", "z"),
      ("h", "count"),
  )


class entity_velocity(packet):
  id = 0x1C
  data_s2c = (
      ("i", "eid"),
      ("h", "vx"),
      ("h", "vy"),
      ("h", "vz"),
  )


class destroy_entity(packet):
  id = 0x1D
  data_s2c = (("i", "eid"), )


class entity(packet):
  id = 0x1E
  data_s2c = (("i", "eid"), )


class entity_relative_move(entity):
  id = 0x1F
  data_s2c = entity.data_s2c + (
      ("b", "dx"),
      ("b", "dy"),
      ("b", "dz"),
  )


class entity_look(entity):
  id = 0x20
  data_s2c = entity.data_s2c + (
      ("b", "yaw"),
      ("b", "pitch"),
  )


class entity_relative_move_look(entity):
  id = 0x21
  data_s2c = entity.data_s2c + entity_relative_move.data_s2c[1:] + entity_look.data_s2c[1:]


class entity_teleport(entity):
  id = 0x22
  data_s2c = entity.data_s2c + (
      ("i", "x"),
      ("i", "y"),
      ("i", "z"),
      ("b", "yaw"),
      ("b", "pitch"),
  )


class entity_head_look(entity):
  id = 0x23
  data_s2c = entity.data_s2c + (("b", "head_yaw"), )


class entity_statys(entity):
  id = 0x26
  data_s2c = entity.data_s2c + (("b", "entity_status"), )


class attach_entity(entity):
  id = 0x27
  data_s2c = entity.data_s2c + (("i", "vehical_id"), )


class entity_metadata(entity):
  id = 0x28
  data_s2c = entity.data_s2c + (("M", "metadata"), )


class entity_effect(entity):
  id = 0x29
  data_s2c = entity.data_s2c + (
      ("b", "effect_id"),
      ("b", "amplifier"),
      ("h", "duration"),
  )


class remove_entity_effect(entity):
  id = 0x2A
  data_s2c = entity.data_s2c + (("b", "effect_id"), )


class set_experience(packet):
  id = 0x2B
  data_s2c = (
      ("f", "experience_bar"),
      ("h", "level"),
      ("h", "total_experience"),
  )


class map_column_allocation(packet):
  id = 0x32
  data_s2c = (
      ("i", "x"),
      ("i", "z"),
      ("?", "mode"),
  )


class map_chunks(packet):
  id = 0x33
  data_s2c = (
      ("i", "x"),
      ("i", "z"),
      ("?", "ground_up_continuous"),
      ("H", "primary_bit_map"),
      ("H", "add_bit_map"),
      ("i", "compressed_size"),
      ("i", ""),
      ("Ba", "compressed_data"),
  )


class multi_block_change(packet):
  id = 0x34
  data_s2c = (
      ("i", "cx"),
      ("i", "cz"),
      ("h", "record_count"),
      ("i", "data_size"),
      ("ba", "data"),
  )


class block_change(packet):
  id = 0x35
  data_s2c = (
      ("i", "x"),
      ("b", "y"),
      ("i", "z"),
      ("b", "block_type"),
      ("b", "block_metadata"),
  )


class block_action(packet):
  id = 0x36
  data_s2c = (
      ("i", "x"),
      ("h", "y"),
      ("i", "z"),
      ("b", "byte1"),
      ("b", "byte2"),
  )


class explosion(packet):
  id = 0x3C
  data_s2c = (
      ("d", "x"),
      ("d", "y"),
      ("d", "z"),
      ("f", "radius"),
      ("i", "record_count"),
      ("ba", "records"),
  )


class sound_partical_effect(packet):
  id = 0x3D
  data_s2c = (
      ("i", "eid"),
      ("i", "x"),
      ("b", "y"),
      ("i", "z"),
      ("i", "data"),
  )


class change_game_state(packet):
  id = 0x46
  data_s2c = (
      ("b", "reason"),
      ("b", "game_mode"),
  )


class thunderbolt(packet):
  id = 0x47
  data_s2c = (
      ("i", "eid"),
      ("b", ""),
      ("i", "x"),
      ("i", "y"),
      ("i", "z"),
  )


class open_window(packet):
  id = 0x64
  data_s2c = (
      ("b", "window_id"),
      ("b", "inventory_type"),
      ("S", "window_title"),
      ("b", "number_of_slots"),
  )


class close_window(packet):
  id = 0x65
  data_c2s = data_s2c = (("b", "window_id"), )


class click_window(packet):
  id = 0x66
  data_c2s = (
      ("b", "window_id"),
      ("h", "slot"),
      ("b", "right_click"),
      ("h", "action_number"),
      ("?", "shift"),
      ("T", "clicked_item"),
  )


class set_slot(packet):
  id = 0x67
  data_s2c = (
      ("b", "window_id"),
      ("h", "slot"),
      ("T", "slot_data"),
  )


class set_window_items(packet):
  id = 0x68
  data_s2c = (
      ("b", "window_id"),
      ("h", "count"),
      ("Ta", "slot_data"),
  )


class update_window_property(packet):
  id = 0x69
  data_s2c = (
      ("b", "window_id"),
      ("h", "property"),
      ("h", "value"),
  )


class confirm_transaction(packet):
  id = 0x6A
  data_c2s = data_s2c = (
      ("b", "window_id"),
      ("h", "action_number"),
      ("?", "accepted"),
  )


class creative_inventory_action(packet):
  id = 0x6B
  data_c2s = data_s2c = (
      ("h", "slot"),
      ("T", "clicked_item"),
  )


class enchant_item(packet):
  id = 0x6C
  data_c2s = (
      ("b", "window_id"),
      ("b", "enchantment"),
  )


class update_sign(packet):
  id = 0x82
  data_c2s = data_s2c = (
      ("i", "x"),
      ("h", "y"),
      ("i", "z"),
      ("S", "text1"),
      ("S", "text2"),
      ("S", "text3"),
      ("S", "text4"),
  )


class item_data(packet):
  id = 0x83
  data_s2c = (
      ("h", "item_type"),
      ("h", "item_id"),
      ("B", "text_length"),
      ("ba", "text"),
  )


class update_title_entity(packet):
  id = 0x84
  data_s2c = (
      ("i", "x"),
      ("h", "y"),
      ("i", "z"),
      ("b", "action"),
      ("i", "custom1"),
      ("i", "custom2"),
      ("i", "custom3"),
  )


class increment_statistic(packet):
  id = 0xC8
  data_s2c = (
      ("i", "statistic_id"),
      ("b", "amount"),
  )


class player_list_item(packet):
  id = 0xC9
  data_s2c = (
      ("S", "player_name"),
      ("?", "online"),
      ("h", "ping"),
  )


class player_abilities(packet):
  id = 0xCA
  data_c2s = data_s2c = (
      ("?", "invulnerabile"),
      ("?", "flying"),
      ("?", "flyable"),
      ("?", "instant_destroy"),
  )


class plugin_message(packet):
  id = 0xFA
  data_c2s = data_s2c = (
      ("S", "channel"),
      ("h", "length"),
      ("ba", "data") # byte array
  )


class server_list_ping(packet):
  id = 0xFE
  data_c2s = ()


class disconnect(packet):
  id = 0xFF
  data_c2s = data_s2c = (("S", "reason"), )



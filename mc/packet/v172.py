from mc.fields import *

import collections
import functools
import logging
import sys

_logger = logging.getLogger(__name__)

CLIENT_TO_SERVER = 0
SERVER_TO_CLIENT = 1

_pre = {
    CLIENT_TO_SERVER: "cs_",
    SERVER_TO_CLIENT: "sc_",
}

START_STATE   = 0
STATUS_STATE  = 1
LOGIN_STATE   = 2
PLAY_STATE    = 3

_fields = collections.defaultdict(dict)
_kwset = collections.defaultdict(dict)

_name = collections.defaultdict(dict)
_pid = collections.defaultdict(dict)


class RawPacket:

  def __init__(self, pid, raw):
    self._pid = pid
    self._name = "unknown"
    self.raw = raw


class Packet:

  def __init__(self, packet_direction, packet_state, packet_name, **field_info):
    self._pid = _pid[packet_direction, packet_state][packet_name]
    self._name = packet_name
    kwset = _kwset[packet_direction, packet_state][self._pid]
    for fname, fcontent in field_info.items():
      if fname in kwset:
        setattr(self, fname, fcontent)
      else:
        raise ValueError("``{}'' is not a valid field name.".format(fname))


def pack(packet, direction, state):
  p = VarInt.pack(packet._pid)
  for ftype, fname in _fields[direction, state][packet._pid]:
    fcontent = getattr(packet, fname, None) if fname else None
    p += ftype.pack(fcontent)
  result = VarInt.pack(len(p)) + p
  return result

def unpack(raw, direction, state, offset = 0):
  plen, noffset = VarInt.unpack(raw, offset)
  size = plen + noffset
  if len(raw) < size:
    raise struct.error("Raw data length not enough for packet.")
  pid, noffset = VarInt.unpack(raw, noffset)
  if pid not in _fields[direction, state]:
    _logger.warning("Packet id {} not supported and skipped.".format(pid))
    return RawPacket(pid, raw[noffset:size]), size
  finfo = dict()
  for ftype, fname in _fields[direction, state][pid]:
    fcontent, noffset = ftype.unpack(raw, noffset, finfo)
    if fname:
      finfo[fname] = fcontent
  if noffset != size:
    import binascii
    _logger.warning("noffset != size, possibly parse incorrectly. {},"
       "{}".format(noffset, size))
    _logger.warning(binascii.hexlify(raw[offset:size]))
  _logger.debug(finfo)
  return Packet(
      direction,
      state,
      _name[direction, state][pid],
      **finfo
  ), size

def register(direction, state, *type_infos):
  for type_info in type_infos:
    pid, name, fields = type_info
    _fields[direction, state][pid] = fields
    _kwset[direction, state][pid] = set(map(lambda p: p[1], fields))
    _name[direction, state][pid] = name
    _pid[direction, state][name] = pid
    setattr(sys.modules[__name__], _pre[direction] + name, functools.partial(
        Packet,
        direction,
        state,
        name
    ))


register(CLIENT_TO_SERVER, START_STATE,
    (0x00, "handshake", [
        (VarInt, "version"),
        (String, "address"),
        (UnsignedShort, "port"),
        (VarInt, "state"),
    ]),
)

register(CLIENT_TO_SERVER, STATUS_STATE,
    (0x00, "status_request", []),
    (0x01, "ping", [
        (Long, "time"),
    ]),
)

register(SERVER_TO_CLIENT, STATUS_STATE,
    (0x00, "status_response", [
        (String, "json_response"),
    ]),
    (0x01, "ping", [
        (Long, "time"),
    ]),
)

register(CLIENT_TO_SERVER, LOGIN_STATE,
    (0x00, "login_start", [
        (String, "name"),
    ]),
    (0x01, "encryption_response", [
        (Short, "public_key_length"),
        (Array(Byte, "public_key_length"),
                "public_key"),
        (Short, "token_length"),
        (Array(Byte, "token_length"),
                "verify_token"),
    ]),
)

register(SERVER_TO_CLIENT, LOGIN_STATE,
    (0x00, "disconnect", [
        (String, "json"),
    ]),
    (0x01, "encryption_request", [
        (String, "server_id"),
        (Short, "public_key_length"),
        (Array(Byte, "public_key_length"),
                "public_key"),
        (Short, "token_length"),
        (Array(Byte, "token_length"),
                "verity_token"),
    ]),
    (0x02, "login_success", [
        (String, "uuid"),
        (String, "username"),
    ]),
)

register(SERVER_TO_CLIENT, PLAY_STATE,
    (0x00, "keep_alive", [
        (Int, "keep_live_id"),
    ]),
    (0x01, "join_game", [
        (Int, "entity_id"),
        (UnsignedByte, "gamemode"),
        (Byte, "dimension"),
        (UnsignedByte, "difficulty"),
        (UnsignedByte, "max_players"),
        (String, "level_type"),
    ]),
    (0x02, "chat_message", [
        (String, "json_data"),
    ]),
    (0x03, "time_update", [
        (Long, "age_of_the_world"),
        (Long, "time_of_day"),
    ]),
    (0x04, "entity_equipment", [
        (Int, "entity_id"),
        (Short, "slot"),
        (Slot, "item"),
    ]),
    (0x05, "spawn_position", [
        (Int, "x"),
        (Int, "y"),
        (Int, "z"),
    ]),
    (0x06, "update_health", [
        (Float, "health"),
        (Short, "food"),
        (Float, "food_saturation"),
    ]),
    (0x07, "respawn", [
        (Int, "dimension"),
        (UnsignedByte, "difficulty"),
        (UnsignedByte, "gamemode"),
        (String, "level_type"),
    ]),
    (0x08, "player_position_and_look", [
        (Double, "x"),
        (Double, "y"),
        (Double, "z"),
        (Float, "yaw"),
        (Float, "pitch"),
        (Bool, "on_ground"),
    ]),
    (0x09, "held_item_change", [
        (Byte, "slot"),
    ]),
    (0x0A, "use_bed", [
        (Int, "entity_id"),
        (Int, "x"),
        (UnsignedByte, "y"),
        (Int, "z"),
    ]),
    (0x0B, "animation", [
        (VarInt, "entity_id"),
        (UnsignedByte, "animation"),
    ]),
    (0x0C, "spawn_player", [
        (VarInt, "entity_id"),
        (String, "player_uuid"),
        (String, "player_name"),
        (Int, "x"),
        (Int, "y"),
        (Int, "z"),
        (Byte, "yaw"),
        (Byte, "pitch"),
        (Short, "current_item"),
        (MetaData, "metadata"),
    ]),
    (0x0D, "collect_item", [
        (Int, "collected_entity_id"),
        (Int, "collector_entity_id"),
    ]),
    (0x0E, "spawn_object", [
        (VarInt, "entity_id"),
        (Byte, "type"),
        (Int, "x"),
        (Int, "y"),
        (Int, "z"),
        (Byte, "pitch"),
        (Byte, "yaw"),
        (Object, "data"),
    ]),
    (0x0F, "spawn_mob", [
        (VarInt, "entity_id"),
        (UnsignedByte, "type"),
        (Int, "x"),
        (Int, "y"),
        (Int, "z"),
        (Byte, "pitch"),
        (Byte, "head_pitch"),
        (Byte, "yaw"),
        (Short, "velocity_x"),
        (Short, "velocity_y"),
        (Short, "velocity_z"),
        (MetaData, "metadata"),
    ]),
    (0x10, "spawn_painting", [
        (VarInt, "entity_id"),
        (String, "title"),
        (Int, "x"),
        (Int, "y"),
        (Int, "z"),
        (Int, "direction"),
    ]),
    (0x11, "spawn_experience_orb", [
        (VarInt, "entity_id"),
        (Int, "x"),
        (Int, "y"),
        (Int, "z"),
        (Short, "count"),
    ]),
    (0x12, "entity_velocity", [
        (Int, "entity_id"),
        (Short, "velocity_x"),
        (Short, "velocity_y"),
        (Short, "velocity_z"),
    ]),
    (0x13, "destroy_entities", [
        (Byte, "count"),
        (Array(Int, "count"),
            "entity_ids"),
    ]),
    (0x14, "entity", [
        (Int, "entity_id"),
    ]),
    (0x15, "entity_relative_move", [
        (Int, "entity_id"),
        (Byte, "dx"),
        (Byte, "dy"),
        (Byte, "dz"),
    ]),
    (0x16, "entity_look", [
        (Int, "entity_id"),
        (Byte, "yaw"),
        (Byte, "pitch"),
    ]),
    (0x17, "entity_look_and_relative_move", [
        (Int, "entity_id"),
        (Byte, "dx"),
        (Byte, "dy"),
        (Byte, "dz"),
        (Byte, "yaw"),
        (Byte, "pitch"),
    ]),
    (0x18, "entity_teleport", [
        (Int, "entity_id"),
        (Int, "x"),
        (Int, "y"),
        (Int, "z"),
        (Byte, "yaw"),
        (Byte, "pitch"),
    ]),
    (0x19, "entity_head_look", [
        (Int, "entity_id"),
        (Byte, "head_yaw"),
    ]),
    (0x1A, "entity_statys", [
        (Int, "entity_id"),
        (Byte, "entity_statys"),
    ]),
    (0x1B, "attach_entity", [
        (Int, "entity_id"),
        (Int, "vehicle_id"),
        (Bool, "leash"),
    ]),
    (0x1C, "entity_metadata", [
        (Int, "entity_id"),
        (MetaData, "metadata"),
    ]),
    (0x1D, "entity_effect", [
        (Int, "entity_id"),
        (Byte, "effect_id"),
        (Byte, "amplified"),
        (Short, "duration"),
    ]),
    (0x1E, "remove_entity_effect", [
        (Int, "entity_id"),
        (Byte, "effect_id"),
    ]),
    (0x1F, "set_experience", [
        (Float, "experience_bar"),
        (Short, "level"),
        (Short, "total_experience"),
    ]),
    # (0x20, "entity_properties"), [
    #     (Int, "entity_id"),
    #     (Int, "count"),
        # TODO(Array(Property, "count"),
    #         "properties"),
    # ]),
    (0x21, "chunk_data", [
        (Int, "chunk_x"),
        (Int, "chunk_z"),
        (Bool, "ground_up_continuous"),
        (UnsignedShort, "add_bit_map"),
        (Int, "compressed_size"),
        (Array(Byte, "compressed_size"),
            "compressed_data"),
    ]),
    (0x22, "multi_block_change", [
        (Int, "chunk_x"),
        (Int, "chunk_z"),
        (Short, "record_count"),
        (Int, "data_size"),
        (Array(Byte, "data_size"),
            "records"),
    ]),
    (0x23, "block_change", [
        (Int, "x"),
        (UnsignedByte, "y"),
        (Int, "z"),
        (VarInt, "block_id"),
        (UnsignedByte, "block_metadata"),
    ]),
    (0x24, "block_action", [
        (Int, "x"),
        (Short, "y"),
        (Int, "z"),
        (UnsignedByte, "byte_1"),
        (UnsignedByte, "byte_2"),
        (VarInt, "block_type"),
    ]),
    (0x25, "block_break_animation", [
        (VarInt, "entity_id"),
        (Int, "x"),
        (Int, "y"),
        (Int, "z"),
        (Byte, "destroy_stage"),
    ]),
    (0x26, "map_chunk_bulk", [
        (Short, "chunk_column_count"),
        (Int, "data_length"),
        (Bool, "sky_light_sent"),
        (Array(Byte, "data_length"),
            "data"),
        (
            Array(
                Multi(
                    (Int, "chunk_x"),
                    (Int, "chunk_z"),
                    (UnsignedShort, "primary_bitmap"),
                    (UnsignedShort, "add_bitmap"),
                ),
                "chunk_column_count"
            ),
            "meta",
        ),
    ]),
    # (0x27, "explosion", [
    #     (Float, "x"),
    #     (Float, "y"),
    #     (Float, "z"),
    #     (Float, "radius"),
    #     (Int, "record_count"),
    #     TODO ( records,
    #     (Float, "player_motion_x"),
    #     (Float, "player_motion_y"),
    #     (Float, "player_motion_z"),
    # ]),
    (0x28, "effect", [
        (Int, "effect_id"),
        (Int, "x"),
        (Byte, "y"),
        (Int, "z"),
        (Int, "data"),
        (Bool, "disable_relative_volumn"),
    ]),
    (0x29, "sound_effect", [
        (String, "sound_name"),
        (Int, "effect_position_x"),
        (Int, "efect_position_y"),
        (Int, "effect_position_z"),
        (Float, "volumn"),
        (UnsignedByte, "pitch"),
    ]),
    (0x2A, "particle", [
        (String, "particle_name"),
        (Float, "x"),
        (Float, "y"),
        (Float, "z"),
        (Float, "offset_x"),
        (Float, "offset_y"),
        (Float, "offset_z"),
        (Float, "particle_data"),
        (Int, "number_of_particles"),
    ]),
    (0x2B, "change_game_state", [
        (UnsignedByte, "reason"),
        (Float, "value"),
    ]),
    (0x2C, "spawn_global_entity", [
        (VarInt, "entity_id"),
        (Byte, "type"),
        (Int, "x"),
        (Int, "y"),
        (Int, "z"),
    ]),
    (0x2D, "open_window",[
        (UnsignedByte, "window_id"),
        (UnsignedByte, "inventory_type"),
        (String, "window_title"),
        (UnsignedByte, "number_of_slots"),
        (Bool, "use_provided_window_title"),
        (Int, "entity_id"), # TODO only set when window type is 11
    ]),
    (0x2E, "close_window", [
        (UnsignedByte, "window_id"),
    ]),
    (0x2F, "set_slot", [
        (Byte, "window_id"),
        (Short, "slot"),
        (Slot, "slot_data"),
    ]),
    (0x30, "window_items", [
        (UnsignedByte, "window_id"),
        (Short, "count"),
        (Array(Slot, "count"),
            "slot_data"),
    ]),
    (0x31, "window_property", [
        (UnsignedByte, "window_id"),
        (Short, "property"),
        (Short, "value"),
    ]),
    (0x32, "confirm_transaction", [
        (UnsignedByte, "window_id"),
        (Short, "action_number"),
        (Bool, "accepted"),
    ]),
    (0x33, "update_sign", [
        (Int, "x"),
        (Int, "y"),
        (Int, "z"),
        (String, "line_1"),
        (String, "line_2"),
        (String, "line_3"),
        (String, "line_4"),
    ]),
    (0x34, "maps", [
        (VarInt,"item_damage"),
        (Short, "data_length"),
        (Array(Byte, "data_length"),
            "data"),
    ]),
    (0x35, "update_block_entity", [
        (Int, "x"),
        (Short, "y"),
        (Int, "z"),
        (UnsignedByte, "action"),
        (Short, "nbt_data_length"),
        (Array(Byte, "nbt_data_length"),
            "nbt_data"),
    ]),
    (0x36, "sign_editor_open", [
        (Int, "x"),
        (Int, "y"),
        (Int, "z"),
    ]),
    (0x37, "statistics", [
        (VarInt, "count"),
        (
            Array(
                Multi(
                    (String, "statistic_name"),
                    (VarInt, "entry_value"),
                ),
                "count",
            ),
           "entries"
        ),
    ]),
    (0x38, "player_list_item", [
        (String, "player_name"),
        (Bool, "online"),
        (Short, "ping"),
    ]),
    (0x39, "player_abilities", [
        (Byte, "flags"),
        (Float, "flying_speed"),
        (Float, "walking_speed"),
    ]),
    (0x3A, "tab_complete", [
        (VarInt, "count"),
        (String, "match"),
    ]),
    (0x3B, "scoreboard_objective", [
        (String, "objective_name"),
        (String, "objective_value"),
        (Byte, "create_remove"),
    ]),
    (0x3C, "update_score", [
        (String, "item_name"),
        (Byte, "update_remove"),
        (String, "score_name"),
        (Int, "value"),
    ]),
    (0x3D, "display_scoreboad", [
        (Byte, "position"),
        (String, "score_name"),
    ]),
    (0x3E, "teams", [
        (String, "team_name"),
        (Byte, "mode"),
        (String, "team_display_name"),
        (String, "team_prefix"),
        (String, "team_suffix"),
        (Byte, "friendly_fire"),
        (Short, "player_count"),
        (Array(String, "player_count"),
            "players"),
    ]),
    (0x3F, "plugin_message", [
        (String, "channel"),
        (Short, "data_length"),
        (Array(Byte, "data_length"),
            "data"),
    ]),
    (0x40, "disconnect", [
        (String, "reason"),
    ]),
)

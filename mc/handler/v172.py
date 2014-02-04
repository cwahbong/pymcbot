import logging

from mc.handler.base import Handler
from mc.window import v172 as windows

import mc.net

_logger = logging.getLogger(__name__)

class Connection(Handler):
  def __init__(self, client, connector):
    super().__init__(client, connector)

  def keep_alive(self, packet):
    self._connector.send_later("keep_alive",
        keep_alive_id = packet.keep_alive_id,
    )
    _logger.debug("Response a keep_alive packet with id {}.".format(
        packet.keep_alive_id
    ))

  def disconnect(self, packet):
    _logger.info("Disconnected by server, reason: {}.".format(
        packet.reason
    ))


class WorldStatus(Handler):
  def __init__(self, client, connector):
    super().__init__(client, connector)

  def join_game(self, packet):
    pass

  def time_update(self, packet):
    pass

  def respawn(self, packet):
    pass

  def change_game_state(self, packet):
    pass


class PlayerStatus(Handler):
  def __init__(self, client, connector):
    super().__init__(client, connector)

  def join_game(self, packet):
    self._client.player_entity_id = packet.entity_id

  def update_health(self, packet):
    self._client.health = packet.health
    self._client.food = packet.food
    self._client.food_saturation = packet.food_saturation

  def player_position_and_look(self, packet):
    self._client._positioner.message(mc.net.POSITION_LOOK_SERVER, packet)

  def held_item_change(self, packet):
    self._client.held_item_slot = packet.slot

  def use_bed(self, packet):
    if packet.entity_id == self._client.player_entity_id:
      self._client.on_bed = True

  def set_experience(self, packet):
    self._client.experience_bar = packet.experience_bar
    self._client.level = packet.level
    self._client.total_experience = packet.total_experience

  def player_abilities(self, packet):
    self._client.god_mode = packet.flags & 0x8
    self._client.can_fly = packet.flags & 0x4
    self._client.flying = packet.flags & 0x2
    self._client.creative_mode = packet.flags & 0x1
    self._client.flying_speed = packet.flying_speed
    self._client.walking_speed = packet.walking_speed


class Block(Handler):

  def __init__(self, client, connector):
    super().__init__(client, connector)

  def chunk_data(self, packet):
    pass

  def multi_block_change(self, packet):
    pass

  def block_change(self, packet):
    pass

  def block_action(self, packet):
    pass

  def block_break_animation(self, packet):
    pass

  def map_chunk_bulk(self, packet):
    pass

  def explosion(self, packet):
    pass


class Window(Handler):

  def __init__(self, client, connector):
    super().__init__(client, connector)
    self._client.windows = {
        0: windows.new_by_type_id(-1)
    }
    self._client.window_stack = [0]

  def open_window(self, packet):
    self._client.windows[packet.window_id] = windows.new_by_type_id(packet.inventory_type)
    self._client.current_window_id.append(packet.window_id)

  def close_window(self, packet):
    del self._client.windows[packet.window_id]

  def set_slot(self, packet):
    if packet.window_id == -1:
      _logger.warning("Negative window id.")
      return
    if packet.window_id not in self._client.windows:
      _logger.error("Window not initialized, id = {}".format(
          packet.window_id
      ))
      return
    self._client.windows[packet.window_id].slots[packet.slot] = packet.slot_data

  def window_items(self, packet):
    self._client.windows[packet.window_id].slots = list(packet.slot_data)

  def window_property(self, packet):
    # TODO
    pass

  def confirm_transaction(self, packet):
    # TODO
    pass


class Entity(Handler):

  def __init__(self, client, connector):
    super().__init__(client, connector)

  def entity_equipment(self, packet):
    pass

  def spawn_player(self, packet):
    pass

  def collect_item(self, packet):
    pass

  def spawn_object(self, packet):
    pass

  def spawn_mob(self, packet):
    pass

  def spawn_painting(self, packet):
    pass

  def spawn_experience_orb(self, packet):
    pass

  def entity_velocity(self, packet):
    pass

  def destroy_entities(self, packet):
    pass

  def entity(self, packet):
    pass

  def entity_relative_move(self, packet):
    pass

  def entity_look(self, packet):
    pass

  def entity_look_and_relative_move(self, packet):
    pass

  def entity_teleport(self, packet):
    pass

  def entity_head_look(self, packet):
    pass

  def entity_status(self, packet):
    pass

  def attach_entity(self, packet):
    pass

  def entity_metadata(self, packet):
    pass

  def entity_effect(self, packet):
    pass

  def remove_entity_effect(self, packet):
    pass

  def entity_properties(self, packet):
    pass

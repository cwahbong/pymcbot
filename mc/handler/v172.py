import logging
import zlib

from mc.handler.base import Handler
from mc.window import v172 as window

import mc.map
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
    self._client.wmap = mc.map.World()

  def _update_by_chunk(self, data, offset, X, Z, primary, add,
      ground_up, skylight):
    def column_extract(extractor):
      x, z = X * 16, Z * 16
      for Y in range(16):
        if primary & (1 << Y):
          y = Y * 16
          extractor(x, y, z)
    def byte(updater):
      def extractor(x, y, z):
        nonlocal offset
        for yy in range(y, y + 16):
          for zz in range(z, z + 16):
            for xx in range(x, x + 16):
              updater(xx, yy, zz, data[offset])
              offset += 1
      return extractor
    def half_byte(updater):
      def extractor(x, y, z):
        nonlocal offset
        for yy in range(y, y + 16):
          for zz in range(z, z + 16):
            for xx in range(x, x + 16, 2):
              m_even, m_odd = data[offset] >> 4, data[offset] & 0xF
              updater(xx, yy, zz, m_even, m_odd)
              offset += 1
      return extractor
    def block_type(xx, yy, zz, m):
      self._client.wmap[xx][zz][yy].type = m
    def block_metadata(xx, yy, zz, m_even, m_odd):
      self._client.wmap[xx][zz][yy].metadata = m_even
      self._client.wmap[xx + 1][zz][yy].metadata = m_odd
    def block_light(xx, yy, zz, m_even, m_odd):
      self._client.wmap[xx][zz][yy].light = m_even
      self._client.wmap[xx + 1][zz][yy].light = m_odd
    def block_sky_light(xx, yy, zz, m_even, m_odd):
      self._client.wmap[xx][zz][yy].sky_light = m_even
      self._client.wmap[xx + 1][zz][yy].sky_light = m_odd

    column_extract(byte(block_type))
    column_extract(half_byte(block_metadata))
    column_extract(half_byte(block_light))
    column_extract(half_byte(block_sky_light))
    # ADD_ARRAY (secondary bitmask)
    if add > 0:
      _logger.warning("Add bitmask is not zero but not implemented.")
      # TODO
    x, z = X * 16, Z * 16
    # BIOME (byte per XZ, 16 * 16 = 256 total)
    for zz in range(z, z + 16):
      for xx in range(x, x + 16):
        self._client.wmap[xx][zz].biome = data[offset]
        offset += 1
    return offset


  def chunk_data(self, packet):
    if packet.ground_up_continuous and packet.primary_bit_map == 0:
      # TODO unload chunk
      _logger.warning("Unload chunk (not implemented)")
    else:
      self._update_by_chunk(data, 0, packet.x, packet.z,
          packet.primary_bit_map, packet.add_bit_map,
          ground_up = packet.ground_up_continuous,
          skylight = True)

  def multi_block_change(self, packet):
    _logger.warning("multi_block_change handler not implemented.")

  def block_change(self, packet):
    x, y, z = packet.x, packet.y, packet.z
    block = self._client.wmap[x][z][y]
    block.type = packet.block_id
    block.metadata = packet.block_metadata

  def block_action(self, packet):
    pass

  def block_break_animation(self, packet):
    pass

  def map_chunk_bulk(self, packet):
    data = zlib.decompress(bytes(packet.data))
    p = 0
    for m in packet.meta:
      p = self._update_by_chunk(data, p,
          m.chunk_x, m.chunk_z,
          m.primary_bitmap,
          m.add_bitmap,
          ground_up = True,
          skylight = packet.sky_light_sent,
      )
    if p != len(data):
      _logger.warning(
          "Final offset not equal to the length of decompressed data."
      )

  def explosion(self, packet):
    pass


class Window(Handler):

  def __init__(self, client, connector):
    super().__init__(client, connector)
    self._client.windows = window.Windows()

    inventory = window.Window(window.SELF, 0)
    self._client.windows.add(inventory)

  def open_window(self, packet):
    w = window.Window(packet.inventory_type, packet.window_id)
    self._client.windows.add(w)

  def close_window(self, packet):
    self._client.windows.pop(packet.window_id)

  def set_slot(self, packet):
    if packet.window_id < 0:
      _logger.warning("Negative window id. {}".format(
          packet.window_id
      ))
      return
    if packet.window_id not in self._client.windows:
      _logger.error("Window not initialized, id = {}".format(
          packet.window_id
      ))
      return
    self._client.windows.by_id[packet.window_id].slots[packet.slot] = packet.slot_data

  def window_items(self, packet):
    self._client.windows.by_id[packet.window_id].slots = list(packet.slot_data)

  def window_property(self, packet):
    self._client.windows.properties[packet.property] = packet.value

  def confirm_transaction(self, packet):
    if packet.accepted:
      # TODO
      # self._client.windows.accepted(packet.action_number)
      pass
    else:
      _logger.info("Transaction refused, action number {}.".format(
          packet.action_number
      ))


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

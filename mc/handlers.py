import zlib

from mc import window

class Handler(object):

  def __init__(self, client):
    self._client = client


class Connection(Handler):

  def on__keep_alive(self, packet):
    self._client._send(packet)
    print "keep alive"

  def on__disconnect(self, packet):
    print "Disconnect, reason:", packet.reason


class PositionLook(Handler):

  def on__spawn_position(self, packet):
    self._client.next_position_look(position={
        "x": packet.x,
        "y": packet.y,
        "z": packet.z,
        "stance": 0.1,
    }, look={
        "yaw": 0.0,
        "pitch": 0.0,
    }, on_ground=True)
    print "Spawn at ({}, {}, {})".format(packet.x, packet.y, packet.z)

  def on__player_position_look(self, packet):
    self._client._send(packet)
    self._client._update_position_look(
        packet.x, packet.y, packet.z, packet.stance,
        packet.yaw, packet.pitch, packet.on_ground
    )


class Blocks(Handler):

  def __on_blocks(self, packet):
    pass

  def on__map_column_allocation(self, packet):
    self.__on_blocks(packet)
    print "x:", packet.x, "z:", packet.z
    # IGNORE IN FUTURE VERSION

  def on__chunk_data(self, packet):

    def for_xz_in_chunk(decompressed, offset, chunk_x, chunk_z, func):
      for x in range(chunk_x*16, (chunk_x+1)*16):
        for z in range(chunk_z*16, (chunk_z+1)*16):
          offset = func(decompressed, offset, x, z)
      return offset

    def array_byte(decompressed, offset, chunk_x, chunk_y, chunk_z, attrname):
      def fill_for_y(decompressed, offset, x, z):
        for y in range(chunk_y*16, (chunk_y+1)*16):
          setattr(self._client.map[x][z][y], attrname, ord(decompressed[offset]))
          offset += 1
        return offset
      return for_xz_in_chunk(decompressed, offset, chunk_x, chunk_z, fill_for_y)

    def array_half_byte(decompressed, offset, chunk_x, chunk_y, chunk_z, attrname):
      def fill_for_y(decompressed, offset, x, z):
        for y in range(chunk_y*16, (chunk_y+1)*16, 2):
          y_1 = y
          y_2 = y + 1
          byte = ord(decompressed[offset])
          setattr(self._client.map[x][z][y_1], attrname, byte & 0x0F)
          setattr(self._client.map[x][z][y_2], attrname, byte >> 4)
          offset += 1
        return offset
      return for_xz_in_chunk(decompressed, offset, chunk_x, chunk_z, fill_for_y)

    offset = 0
    self.__on_blocks(packet)
    decompressed = zlib.decompress("".join(map(chr, packet.compressed_data)))
    print "len compress", len(packet.compressed_data)
    print "chunk_data", len(decompressed)
    for chunk_y in range(16):
      if packet.primary_bit_map & (1<<chunk_y):
        # Block type array (1 byte per block, 4096 bytes per section)
        offset = array_byte(decompressed, offset, packet.x, chunk_y, packet.z, "type")
        # Block metadata array (half byte per block, 2048 bytes per section)
        offset = array_half_byte(decompressed, offset, packet.x, chunk_y, packet.z, "metadata")
        # Block light array (half byte per block, 2048 bytes per section)
        offset = array_half_byte(decompressed, offset, packet.x, chunk_y, packet.z, "light")
        # Sky light array (half byte per block, 2048 bytes per section)
        offset = array_half_byte(decompressed, offset, packet.x, chunk_y, packet.z, "sky_light")
        if packet.add_bit_map & (1<<chunk_y):
          # Add array (half byte per block, 2048 bytes per section, uses second bitmask)
          raise NotImplementedError
      # Biome array (1 byte per XZ coordinate, 256 bytes total, only sent if 'ground up continuous' is true)
    if packet.ground_up_continuous:
      def fill_biome(decompressed, offset, x, z):
        self._client.map[x][z].biome = ord(decompressed[offset])
        offset += 1
        return offset
      offset = for_xz_in_chunk(decompressed, offset, packet.x, packet.z, fill_biome)
    if offset != len(decompressed):
      print offset, len(decompressed)
      raise ValueError

  def on__multi_block_change(self, packet):
    self.__on_blocks(packet)

  def on__block_change(self, packet):
    self.__on_blocks(packet)

  def on__block_action(self, packet):
    self.__on_blocks(packet)

  def on__explosion(self, packet):
    self.__on_blocks(packet)


class Slot(Handler):

  def on__set_slot(self, packet):
    if packet.window_id==-1 and packet.slot==-1:
      self._client._mouse_hold = {"id": -1}
    elif packet.window_id==self._client.window_id:
      idx = 0
      for pair in window.layout[self._client.window_type]:
        attr = pair[0]
        num = self._client.other_size if pair[1]<0 else pair[1]
        if idx<=packet.slot<idx+num:
          getattr(self._client, attr)[packet.slot-idx] = packet.slot_data
        idx += num

  def on__set_window_items(self, packet):
    idx = 0
    for pair in window.layout[self._client.window_type]:
      attr = pair[0]
      num = pair[1] if pair[1]!=-1 else packet.count-36
      setattr(self._client, attr, packet.slot_data[idx:idx+num])
      idx += num


class Window(Handler):

  def on__open_window(self, packet):
    self._client.window_id = packet.window_id
    self._client.window_type = SELF if packet.window_id==0 else packet.inventory_type
    self._client.other_size = packet.number_of_slots

  def on__close_window(self, packet):
    self._client.close()


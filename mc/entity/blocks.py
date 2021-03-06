import sys
from mc import util

__id_manager = util.IdManager(sys.modules[__name__])

_info = [
    (0x00, "air"),
    (0x01, "stone"),
    (0x02, "grass"),
    (0x03, "dirt"),
    (0x04, "cobblestone"),
    (0x05, "wooden_planks"),
    (0x06, "saplings"),
    (0x07, "bedrock"),
    (0x08, "water"),
    (0x09, "stationary_water"),
    (0x0A, "lava"),
    (0x0B, "stationary_lava"),
    (0x0C, "sand"),
    (0x0D, "gravel"),
    (0x0E, "gold_ore"),
    (0x0F, "iron_ore"),
    (0x10, "coal_ore"),
    (0x11, "wood"),
    (0x12, "leaves"),
    (0x13, "sponge"),
    (0x14, "glass"),
    (0x15, "lapis_lazuli_ore"),
    (0x16, "lapis_lazuli_block"),
    (0x17, "dispenser"),
    (0x18, "sandstone"),
    (0x19, "noteblock"),
    (0x1A, "bed"),
    (0x1B, "powered_rail"),
    (0x1C, "detector_rail"),
    (0x1D, "sticky_piston"),
    (0x1E, "cobweb"),
    (0x1F, "tall_grass"),
    (0x20, "dead_bush"),
    (0x21, "piston"),
    (0x22, "piston_extension"),
    (0x23, "wool"),
    (0x24, "block_moved_by_piston"),
    (0x25, "dandelion"),
    (0x26, "rose"),
    (0x27, "brown_mushroom"),
    (0x28, "red_mushroon"),
    (0x29, "block_of_gold"),
    (0x2A, "block_of_iron"),
    (0x2B, "double_slabs"),
    (0x2C, "slabs"),
    (0x2D, "bricks"),
    (0x2E, "tnt"),
    (0x2F, "bookshelf"),
    (0x30, "moss_stone"),
    (0x31, "obsidian"),
    (0x32, "torch"),
    (0x33, "fire"),
    (0x34, "moster_spawner"),
    (0x35, "oak_wood_stairs"),
    (0x36, "chest"),
    (0x37, "redstone_wire"),
    (0x38, "diamond_ore"),
    (0x39, "block_of_diamond"),
    (0x3A, "crafting_table"),
    (0x3B, "wheat_seeds"),
    (0x3C, "farmland"),
    (0x3D, "furnace"),
    (0x3E, "burning_furnace"),
    (0x3F, "sign_post"),
    (0x40, "wooden_door"),
    (0x41, "ladders"),
    (0x42, "rails"),
    (0x43, "cobblestone_stairs"),
    (0x44, "wall_sign"),
    (0x45, "lever"),
    (0x46, "stone_pressure_plate"),
    (0x47, "iron_door"),
    (0x48, "wooden_pressure_plate"),
    (0x49, "redstone_ore"),
    (0x4A, "glowing_redstone_ore"),
    (0x4B, "redstone_torch_off"),
    (0x4C, "redstone_torch_on"),
    (0x4D, "stone_button"),
    (0x4E, "snow"),
    (0x4F, "ice"),
    (0x50, "snow_block"),
    (0x51, "cactus"),
    (0x52, "clay_block"),
    (0x53, "sugar_cane"),
    (0x54, "jukebox"),
    (0x55, "fence"),
    (0x56, "pumpkin"),
    (0x57, "netherrack"),
    (0x58, "soul_sand"),
    (0x59, "glowstone_block"),
    (0x5A, "portal"),
    (0x5B, "jack_o_lantern"),
    (0x5C, "cake_block"),
    (0x5D, "redstone_repeater_off"),
    (0x5E, "redstone_repeater_on"),
    (0x5F, "locked_chest"),
    (0x60, "trapdoor"),
    (0x61, "monster_egg"),
    (0x62, "stone_bricks"),
    (0x63, "huge_brown_mushroom"),
    (0x64, "huge_red_mushroom"),
    (0x65, "iron_bars"),
    (0x66, "glass_pane"),
    (0x67, "melon"),
    (0x68, "pumpkin_stem"),
    (0x69, "melon_stem"),
    (0x6A, "vines"),
    (0x6B, "fence_gate"),
    (0x6C, "brick_stairs"),
    (0x6D, "stone_brick_stairs"),
    (0x6E, "mycellum"),
    (0x6F, "lily_pad"),
    (0x70, "nether_brick"),
    (0x71, "nether_brick_fence"),
    (0x72, "nether_brick_stairs"),
    (0x73, "nether_wart"),
    (0x74, "enchantment_table"),
    (0x75, "brewing_stand"),
    (0x76, "cauldron"),
    (0x77, "end_portal"),
    (0x78, "ent_portal_frame"),
    (0x79, "end_stone"),
    (0x7A, "dragon_egg"),
    (0x7B, "redstone_lamp_off"),
    (0x7C, "redstone_lamp_on"),
    (0x7D, "wooden_double_slab"),
    (0x7E, "wooden_slab"),
    (0x7F, "cocoa_plant"),
    (0x80, "sandstone_stairs"),
    (0x81, "emerald_ore"),
    (0x82, "ender_chest"),
    (0x83, "tripwire_hook"),
    (0x84, "tripwire"),
    (0x85, "block_of_emerald"),
    (0x86, "sprice_wood_stairs"),
    (0x87, "birch_wood_stairs"),
    (0x88, "jungle_wood_stairs"),
]

__id_manager.list_register(_info)


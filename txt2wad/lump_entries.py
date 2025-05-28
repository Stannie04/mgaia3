import struct


class LumpBuilder:
    def __init__(self):
        self.entries = []

    def add_entry(self, entry):
        self.entries.append(entry)

    def pack_lump(self):
        lump = b""
        for entry in self.entries:
            lump += entry.pack_data()
        return lump


################
# Lump entries #
################

class Empty:
    def __init__(self):
        pass

    def pack_data(self):
        return b""


class Thing:
    def __init__(self, x, y, angle, thing_type, flags):
        """Build a Thing object.

        Each entry is 10 bytes long:
        - x: int16_t x position, 2 bytes
        - y: int16_t y position, 2 bytes
        - angle: int16_t angle, 2 bytes
        - type: int16_t DoomED thing type, 2 bytes
        - flags: int16_t flags, 2 bytes

        Flags:
        - Bit 0 (dec 1): On skill levels 1 & 2
        - Bit 1 (dec 2): On skill levels 3
        - Bit 2 (dec 4): On skill levels 4 & 5
        - Bit 3 (dec 8): Waiting in ambush
        - Bit 4 (dec 16): Not in single player
        """

        self.x = x
        self.y = y
        self.angle = angle
        self.type = thing_type
        self.flags = flags

    def pack_data(self):
        return struct.pack("<hhhhh", self.x, self.y, self.angle, self.type, self.flags)


class Vertex:
    def __init__(self, x, y):
        """Build a Vertex object.

        Each entry is 4 bytes long:
        - x: int16_t x position, 2 bytes
        - y: int16_t y position, 2 bytes
        """

        self.x = x
        self.y = y

    def pack_data(self):
        return struct.pack("<hh", self.x, self.y)


class Linedef:
    def __init__(self, v1, v2, flags, special, tag, sidedef1, sidedef2):
        """Build a Linedef object.

        Each entry is 14 bytes long:
        - v1: int16_t starting vertex (x,y), 2 bytes
        - v2: int16_t ending vertex (x,y), 2 bytes
        - flags: int16_t flags, 2 bytes
        - special: int16_t type, 2 bytes
        - tag: int16_t tag, 2 bytes
        - sidedef1: int16_t front sidedef, 2 bytes
        - sidedef2: int16_t back sidedef, 2 bytes

        Flags:
        - Bit 0 (dec 1): Blocks players and monsters
        - Bit 1 (dec 2): Blocks projectiles
        - Bit 2 (dec 4): Two-sided
        - Bit 3 (dec 8): Upper texture unpegged
        - Bit 4 (dec 16): Lower texture unpegged
        - Bit 5 (dec 32): Secret, monsters cannot open if door
        - Bit 6 (dec 64): Blocks sound
        - Bit 7 (dec 128): Never shows on automap
        - Bit 8 (dec 256): Always shows on automap

        Types: https://doomwiki.org/wiki/Linedef_type
        """

        self.v1 = v1
        self.v2 = v2
        self.flags = flags
        self.special = special
        self.tag = tag
        self.sidedef1 = sidedef1
        self.sidedef2 = sidedef2

    def pack_data(self):
        return struct.pack("<hhhhhhH", self.v1, self.v2, self.flags, self.special, self.tag, self.sidedef1, self.sidedef2)


class Sidedef:
    def __init__(self, x_offset, y_offset, upper_texture, lower_texture, middle_texture, sector):
        """Build a Sidedef object.

        Each entry is 30 bytes long:
        - x_offset: int16_t x offset, 2 bytes
        - y_offset: int16_t y offset, 2 bytes
        - upper_texture: char[8] upper texture name, 8 bytes
        - lower_texture: char[8] lower texture name, 8 bytes
        - middle_texture: char[8] middle texture name, 8 bytes
        - sector: int16_t sector number, 2 bytes
        """

        self.x_offset = x_offset
        self.y_offset = y_offset
        self.upper_texture = upper_texture
        self.lower_texture = lower_texture
        self.middle_texture = middle_texture
        self.sector = sector

    def pack_data(self):
        # Pack the texture names as 8-byte strings
        # upper_texture_bytes = self.upper_texture.encode('ascii').ljust(8, b'\x00')
        # lower_texture_bytes = self.lower_texture.encode('ascii').ljust(8, b'\x00')
        # middle_texture_bytes = self.middle_texture.encode('ascii').ljust(8, b'\x00')

        return struct.pack("<hh8s8s8sh", self.x_offset, self.y_offset, self.upper_texture, self.lower_texture, self.middle_texture, self.sector)


class Sector:
    def __init__(self, floor_height, ceiling_height, floor_texture, ceiling_texture, light_level, special_type, tag):
        """Build a Sector object.

        Each entry is 26 bytes long:
        - floor_height: int16_t floor height, 2 bytes
        - ceiling_height: int16_t ceiling height, 2 bytes
        - floor_texture: int8_t[8] floor texture name, 8 bytes
        - ceiling_texture: int8_t[8] ceiling texture name, 8 bytes
        - light_level: int16_t light level, 2 bytes
        - special_type: int16_t special type, 2 bytes
        - tag: int16_t tag, 2 bytes
        """

        self.floor_height = floor_height
        self.ceiling_height = ceiling_height
        self.floor_texture = floor_texture
        self.ceiling_texture = ceiling_texture
        self.light_level = light_level
        self.special_type = special_type
        self.tag = tag

    def pack_data(self):
        # Pack the texture names as 8-byte strings
        # floor_texture_bytes = self.floor_texture.encode('ascii').ljust(8, b'\x00')
        # ceiling_texture_bytes = self.ceiling_texture.encode('ascii').ljust(8, b'\x00')

        return struct.pack("<hh8s8shhh", self.floor_height, self.ceiling_height, self.floor_texture, self.ceiling_texture, self.light_level, self.special_type, self.tag)
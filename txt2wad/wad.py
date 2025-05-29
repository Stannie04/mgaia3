import struct
import random
import re

try:
    from .lump_entries import *
except ImportError:
    from lump_entries import *


class WAD:
    def __init__(self, filename, scale, texture_palettes):
        self.spawn_placed = False # Ignore subsequent spawn points (that exist due to multiplayer)
        self.lumps = {
            "MAP01": LumpBuilder(),
            "THINGS": LumpBuilder(),
            "LINEDEFS": LumpBuilder(),
            "SIDEDEFS": LumpBuilder(),
            "VERTEXES": LumpBuilder(),
            "SECTORS": LumpBuilder(),
            "SEGS": LumpBuilder(),
            "SSECTORS": LumpBuilder(),
            "NODES": LumpBuilder(),
            "REJECT": LumpBuilder(),
            "BLOCKMAP": LumpBuilder(),
        }

        self.filename = filename
        self.scale = scale

        self.wad_data = b""

        self.id2char = {
            0: '-', 1: 'X', 2: '.', 3: ',',
            4: 'E', 5: 'W', 6: 'A', 7: 'H',
            8: 'B', 9: 'K', 10: '<', 11: 'T',
            12: ':', 13: 'L', 14: 't', 15: '+',
            16: '>'
        }

        # Reverse mapping from character to number
        self.char2id = {v: k for k, v in self.id2char.items()}

        self.thing_types = {
            4: 3004,  # enemy (e.g. ZombieMan)
            5: 2001,  # weapon (Shotgun)
            6: 2007,  # ammo (Clip)
            7: 2011,  # health (Stimpack)
            8: 2035,  # environmental (ExplosiveBarrel)
            9: 13,  # card/skull (e.g. RedCard)
            10: 1,  # player start (Player start)
            11: 14,  # teleport destination
            12: 2012  # fallback object (Medikit)
        }

        self.walls = {1, 16}
        self.edges = set()

        self.grid = []
        self.vertices_set = {}

        self.read_ascii_map()
        self.extract_geometry()
        self.build_vertices_and_linedefs()
        self.extract_things()

        self.textures = self.pick_palette(texture_palettes)

    @staticmethod
    def pick_palette(texture_dict):
        map_name, all_textures = random.choice(list(texture_dict.items()))

        # Get all button textures
        regex_button = re.compile("SW(1|2).*")
        all_buttons = list(filter(regex_button.match, all_textures["Textures"]))

        # Get all exit sign textures
        exit_style = re.compile("EXIT.*")
        all_exit_style = list(filter(exit_style.match, all_textures["Textures"]))

        # Valid wall textures
        wall_no_buttons = set(all_textures["Textures"]) - set(all_buttons) - set(all_exit_style)

        wall_textures_up = random.choice(list(wall_no_buttons))
        wall_text_low = wall_mid = wall_textures_up

        floor_textures = random.choice(all_textures["Flats"])
        roof_textures = random.choice(all_textures["Flats"])

        regex = re.compile("SW1.*")
        switches = list(filter(regex.match, all_textures["Textures"]))

        exit_tex = random.choice(switches)
        return {"wall_up": wall_textures_up, "wall_mid": wall_mid, "wall_low": wall_text_low,
                "floor": floor_textures, "roof": roof_textures, "exit":exit_tex}


    def build_wad(self, output_filename):
        # Add missing lump data
        for lump_name in ["MAP01", "SEGS",  "SSECTORS", "NODES",  "REJECT", "BLOCKMAP"]:
            self.lumps[lump_name].add_entry(Empty())

        self.build_sidedefs()
        self.build_sector()

        identification = b"PWAD"
        lump_names = list(self.lumps.keys())
        lump_data = [l.pack_lump() for l in self.lumps.values()]
        n_lumps = len(lump_data)

        # The header is 12 bytes; following that are the lumps.
        data = b""
        header_size = 12
        lump_directory = []
        current_offset = header_size  # file offset where lumps begin
        for name, lump in zip(lump_names, lump_data):
            lump_size = len(lump)
            lump_directory.append((current_offset, lump_size, name))
            data += lump
            current_offset += lump_size

        # Now build the directory. Each directory entry is 16 bytes:
        # filepos (4), size (4), name (8 bytes, padded with null bytes).
        directory_data = b""
        for (filepos, size, name) in lump_directory:
            name_bytes = name.encode("ascii")
            if len(name_bytes) < 8:
                name_bytes = name_bytes.ljust(8, b'\0')
            else:
                name_bytes = name_bytes[:8]
            directory_data += struct.pack("<II8s", filepos, size, name_bytes)

        # The directory offset is current_offset.
        info_table_offset = current_offset
        wad_data = struct.pack("<4sII", identification, n_lumps, info_table_offset) + data + directory_data

        # Write the WAD data to a file.
        with open(output_filename, "wb") as f:
            f.write(wad_data)

        print(f"WAD file '{output_filename}' created successfully.")

    def build_sector(self):
        """Put the entire map in a single sector."""
        floor_height = 0
        ceiling_height = 128  # arbitrary
        # floor_tex = b"FLOOR1\0"  # 8 bytes, padded with zeros if necessary
        floor_tex = self.textures["floor"].encode("utf-8")
        if len(floor_tex) < 8:
            floor_tex = floor_tex.ljust(8, b'\0')
        # ceiling_tex = b"CEIL1\0\0"
        ceiling_tex = self.textures["roof"].encode("utf-8")

        if len(ceiling_tex) < 8:
            ceiling_tex = ceiling_tex.ljust(8, b'\0')
        light = 200
        special = 0
        tag = 0
        self.lumps["SECTORS"].add_entry(Sector(floor_height, ceiling_height, floor_tex, ceiling_tex, light, special, tag))

    def build_sidedefs(self):
        # First build sidedef 0 for the exit
        ex = self.textures["exit"].encode("utf-8")
        self.lumps["SIDEDEFS"].add_entry(Sidedef(0, 0, self.textures["wall_up"].encode("utf-8"), self.textures["wall_up"].encode("utf-8"),ex, 0))

        n_sidedefs = len(self.lumps["LINEDEFS"].entries)

        up, low, mid = self.textures["wall_up"].encode("utf-8"), self.textures["wall_low"].encode("utf-8"), self.textures["wall_mid"].encode("utf-8")
        for i in range(n_sidedefs):
            self.lumps["SIDEDEFS"].add_entry(Sidedef(0, 0, up, low, mid, 0))

    ##########################
    # Text parsing functions #
    ##########################

    def read_ascii_map(self):
        """Read the ASCII map file and convert it into a 2D grid of integers."""
        with open(self.filename, 'r') as f:
            for line in f:
                line = line.rstrip('\n')
                # Convert each character to a numeric ID (if unknown, use 0)
                row = [self.char2id.get(ch, 0) for ch in line]
                if row:  # skip empty lines
                    self.grid.append(row)


    def extract_things(self):
        """
        From the grid, extract thing (object) placements.
        Return a list of tuples: (x, y, type)
        We place a thing at the center of a cell if its value is in thing_types.
        """
        height = len(self.grid)
        width = len(self.grid[0]) if height > 0 else 0
        for y in range(height):
            for x in range(width):
                cell = self.grid[y][x]
                if cell in self.thing_types:
                    # If the cell is a spawn point (10), we only place it once.
                    if cell == 10:
                        if self.spawn_placed:
                            self.grid[y][x] = 2  # Change to floor tile
                            continue
                        else:
                            self.spawn_placed = True

                    # Place the thing at the center of the cell.
                    thing_x = int((x + 0.5) * self.scale)
                    thing_y = int((y + 0.5) * self.scale)
                    thing_type = self.thing_types[cell]

                    # Flag 7 (0111): Thing exists on all skill levels
                    self.lumps["THINGS"].add_entry((Thing(x=thing_x, y=thing_y, angle=0, thing_type=thing_type, flags=7)))


    def add_edge(self, v1, v2, exit):
        # Order the two endpoints (as tuples) so that duplicate edges aren’t added.
        edge = (v1, v2, exit)
        if edge not in self.edges:
            self.edges.add(edge)


    def extract_geometry(self):
        """
        From the grid, extract a set of edges that represent wall cell boundaries.
        We assume that any cell whose value is in WALL_SET is a wall cell.
        For each wall cell, we add an edge along any border adjacent to a non‐wall cell.

        Coordinates: cell at (x, y) has its top‐left corner at (x, y);
        each cell is 1 unit square.
        """
        height = len(self.grid)
        width = len(self.grid[0]) if height > 0 else 0

        for y in range(height):
            for x in range(width):
                cell = self.grid[y][x]
                exit = True if cell == 16 else False
                if cell in self.walls:
                    # Check top edge: if above cell is missing or not a wall.
                    if y == 0 or self.grid[y - 1][x] not in self.walls:
                        self.add_edge((x, y), (x + 1, y), exit)
                    # Check bottom edge
                    if y == height - 1 or self.grid[y + 1][x] not in self.walls:
                        self.add_edge( (x + 1, y + 1), (x, y + 1), exit)
                    # Check left edge
                    if x == 0 or self.grid[y][x - 1] not in self.walls:
                        self.add_edge( (x, y + 1), (x, y), exit) #
                    # Check right edge
                    if x == width - 1 or self.grid[y][x + 1] not in self.walls:
                        self.add_edge( (x + 1, y), (x + 1, y + 1), exit)


    def get_vertex_index(self, vertex):
        # Scale the point
        scaled = (int(vertex[0] * self.scale), int(vertex[1] * self.scale))
        if scaled not in self.vertices_set:
            self.vertices_set[scaled] = len(self.lumps["VERTEXES"].entries)
            self.lumps["VERTEXES"].add_entry(Vertex(scaled[0], scaled[1]))
        return self.vertices_set[scaled]


    def build_vertices_and_linedefs(self):
        """
        Build a list of unique vertices (with coordinates scaled) and
        construct linedefs (edge list) referring to vertex indices.

        A vertex is a tuple (x, y) (scaled by SCALE).
        A linedef is a tuple (start, end) of vertex indices.
        """

        # assign an index to a vertex; vertices are defined by (x, y) coordinates.

        for i, (v1, v2, exit) in enumerate(self.edges):
            i1 = self.get_vertex_index(v1)
            i2 = self.get_vertex_index(v2)

            # Flag 7 (0111): Two-sided, blocks players and monsters
            special = 11 if exit else 0
            sidedef = 0 if exit else (i+1)
            self.lumps["LINEDEFS"].add_entry(Linedef(v1=i1, v2=i2, flags=1, special=special, tag=0, sidedef1=sidedef, sidedef2=0xFFFF))
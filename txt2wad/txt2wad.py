#!/usr/bin/env python
"""
txt2wad.py

A best‐effort reverse converter that reads a .txt file (an ASCII “rasterized” level produced
by WADRasterizer) and produces a minimal Doom‐style .WAD file.

WARNING: Because the original WADRasterizer “rasterizes” the level,
a lot of geometric and semantic data is lost. This converter
simply reconstructs a basic grid geometry (using cell boundaries
of wall cells) and places objects where the ASCII map indicates.

Usage:
    python txt2wad.py input_map.txt output.wad
"""

import sys, struct, os

# Mapping from numeric IDs (used when producing the ASCII map) to characters.
# (These are the same as id2char in WADRasterizer.)
id2char = {
    0: '-', 1: 'X', 2: '.', 3: ',',
    4: 'E', 5: 'W', 6: 'A', 7: 'H',
    8: 'B', 9: 'K', 10: '<', 11: 'T',
    12: ':', 13: 'L', 14: 't', 15: '+',
    16: '>'
}
# Reverse mapping from character to number
char2id = {v: k for k, v in id2char.items()}

# Define which cell values we treat as “wall” and which as objects.
WALL_SET = {1, 3, 13, 14, 15, 16}
# Define a mapping from cell value to a Doom “thing” type.
# (The numbers here are arbitrary Doom type numbers chosen for demonstration.)
thing_type_map = {
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

# Scale factor: we assume each cell is 1 “map unit” and we scale up to get reasonable Doom dimensions.
SCALE = 64


def read_ascii_map(filename):
    """Read the ASCII map file and convert it into a 2D grid of integers."""
    grid = []
    with open(filename, 'r') as f:
        for line in f:
            line = line.rstrip('\n')
            # Convert each character to a numeric ID (if unknown, use 0)
            row = [char2id.get(ch, 0) for ch in line]
            if row:  # skip empty lines
                grid.append(row)
    return grid


def extract_geometry(grid):
    """
    From the grid, extract a set of edges that represent wall cell boundaries.
    We assume that any cell whose value is in WALL_SET is a wall cell.
    For each wall cell, we add an edge along any border adjacent to a non‐wall cell.

    Coordinates: cell at (x, y) has its top‐left corner at (x, y);
    each cell is 1 unit square.
    """
    edges = set()
    height = len(grid)
    width = len(grid[0]) if height > 0 else 0

    def add_edge(v1, v2):
        # Order the two endpoints (as tuples) so that duplicate edges aren’t added.
        edge = tuple(sorted((v1, v2)))
        edges.add(edge)

    for y in range(height):
        for x in range(width):
            cell = grid[y][x]
            if cell in WALL_SET:
                # Check top edge: if above cell is missing or not a wall.
                if y == 0 or grid[y - 1][x] not in WALL_SET:
                    add_edge((x, y), (x + 1, y))
                # Check bottom edge
                if y == height - 1 or grid[y + 1][x] not in WALL_SET:
                    add_edge((x, y + 1), (x + 1, y + 1))
                # Check left edge
                if x == 0 or grid[y][x - 1] not in WALL_SET:
                    add_edge((x, y), (x, y + 1))
                # Check right edge
                if x == width - 1 or grid[y][x + 1] not in WALL_SET:
                    add_edge((x + 1, y), (x + 1, y + 1))
    return edges


def extract_things(grid):
    """
    From the grid, extract thing (object) placements.
    Return a list of tuples: (x, y, type)
    We place a thing at the center of a cell if its value is in thing_type_map.
    """
    things = []
    height = len(grid)
    width = len(grid[0]) if height > 0 else 0
    for y in range(height):
        for x in range(width):
            cell = grid[y][x]
            if cell in thing_type_map:
                # Place the thing at the center of the cell.
                thing_x = int((x + 0.5) * SCALE)
                thing_y = int((y + 0.5) * SCALE)
                thing_type = thing_type_map[cell]
                things.append((thing_x, thing_y, thing_type))
                print(f"Thing placed at ({thing_x}, {thing_y}) of type {thing_type}")
    return things


def build_vertices_and_linedefs(edges):
    """
    Build a list of unique vertices (with coordinates scaled) and
    construct linedefs (edge list) referring to vertex indices.

    A vertex is a tuple (x, y) (scaled by SCALE).
    A linedef is a tuple (start, end) of vertex indices.
    """
    vertices = {}
    vertex_list = []
    linedefs = []

    # assign an index to a vertex; vertices are defined by (x, y) coordinates.
    def get_vertex_index(pt):
        # Scale the point
        scaled = (int(pt[0] * SCALE), int(pt[1] * SCALE))
        if scaled not in vertices:
            vertices[scaled] = len(vertex_list)
            vertex_list.append(scaled)
        return vertices[scaled]

    for (v1, v2) in edges:
        i1 = get_vertex_index(v1)
        i2 = get_vertex_index(v2)
        linedefs.append((i1, i2))
        linedefs.append((i2, i1))  # add reverse edge for two-sided lines
    return vertex_list, linedefs


# --- WAD lump builders ---

def build_things_lump(things):
    """
    Build the THINGS lump.
    For Doom, each thing is 10 bytes:
        short x, short y, short angle, short type, short flags
    We'll set angle and flags to zero.
    """
    lump = b""
    for (x, y, thing_type) in things:
        # Using little-endian shorts (2 bytes each)
        lump += struct.pack("<hhhhh", x, y, 0, thing_type, 7)
    return lump


def build_vertexes_lump(vertex_list):
    """
    Build the VERTEXES lump. Each vertex is 4 bytes: short x, short y.
    """
    lump = b""
    for (x, y) in vertex_list:
        lump += struct.pack("<hh", x, y)
    return lump


def build_linedefs_lump(linedefs):
    """
    Build the LINEDEFS lump.
    Each linedef is 14 bytes:
       short start vertex, short end vertex, short flags,
       short line type, short sector tag, short right sidedef, short left sidedef
    For one-sided walls, we set left sidedef to 0xFFFF.
    We'll use flags=0, line type=0, sector tag=0.
    The right sidedef index is set to the index of the corresponding sidedef.
    In our case, we will create one sidedef per linedef, so the right sidedef index equals
    the linedef’s index.
    """
    lump = b""
    for i, (v1, v2) in enumerate(linedefs):
        flags = 0
        line_type = 0
        sector_tag = 0
        right_sidedef = i  # we assume each linedef gets its own sidedef entry (see build_sidedefs_lump)
        left_sidedef = 0xFFFF  # one-sided
        lump += struct.pack("<hhhhhhH", v1, v2, flags, line_type, sector_tag, right_sidedef, left_sidedef)
        # However, note that Doom linedefs are exactly 14 bytes; here we pack 2+2+2+2+2+2+2 = 14 bytes.
    return lump


def build_sidedefs_lump(num_sidedefs):
    """
    Build the SIDEDEFS lump.
    Each sidedef is 30 bytes:
       short x offset, short y offset,
       8-byte upper texture, 8-byte lower texture, 8-byte middle texture,
       short sector number.
    We fill with dummy values (offsets 0, textures "NULL____", sector 0).
    """
    lump = b""
    up = b"NULL____"  # exactly 8 bytes
    mid = b"BRICK01_"  # exactly 8 bytes
    low = b"NULL____"  # exactly 8 bytes
    for _ in range(num_sidedefs):
        xoffs = 0
        yoffs = 0
        # sector number is 0 (the single sector we create later)
        sector = 0
        lump += struct.pack("<hh8s8s8sh", xoffs, yoffs, up, mid, low, sector)
    return lump


def build_sectors_lump():
    """
    Build the SECTORS lump.
    Each sector is 26 bytes:
       short floor height, short ceiling height,
       8-byte floor texture, 8-byte ceiling texture,
       short light level, short special type, short tag.
    We create a single sector covering the entire level.
    """
    floor_height = 0
    ceiling_height = 128  # arbitrary
    floor_tex = b"FLOOR1\0"  # 8 bytes, padded with zeros if necessary
    if len(floor_tex) < 8:
        floor_tex = floor_tex.ljust(8, b'\0')
    ceiling_tex = b"CEIL1\0\0"
    if len(ceiling_tex) < 8:
        ceiling_tex = ceiling_tex.ljust(8, b'\0')
    light = 160
    special = 0
    tag = 0
    lump = struct.pack("<hh8s8shhh", floor_height, ceiling_height, floor_tex, ceiling_tex, light, special, tag)
    return lump


def build_empty_lump():
    """Return an empty lump (used for SEGS, SSECTORS, NODES, REJECT, BLOCKMAP etc.)."""
    return b""


# --- WAD file builder ---

def build_wad(lumps, level_name="MAP01"):
    """
    Build a WAD file containing a single level.
    The level lumps are stored in order:
      Level marker (the level name)
      THINGS
      LINEDEFS
      SIDEDEFS
      VERTEXES
      SECTORS
      (optionally empty lumps for SEGS, SSECTORS, NODES, REJECT, BLOCKMAP)
    """
    level_lump_names = [
        level_name,  # level marker (name lump)
        "THINGS",
        "LINEDEFS",
        "SIDEDEFS",
        "VERTEXES",
        "SECTORS",
        "SEGS",  # empty
        "SSECTORS",  # empty
        "NODES",  # empty
        "REJECT",  # empty
        "BLOCKMAP"  # empty
    ]

    # Build the binary data for each lump.
    # 'lumps' is a dictionary with keys: things, linedefs, sidedefs, vertexes, sectors
    lump_data = []
    # The level marker lump is empty.
    lump_data.append(b"")
    lump_data.append(lumps["things"])
    lump_data.append(lumps["linedefs"])
    lump_data.append(lumps["sidedefs"])
    lump_data.append(lumps["vertexes"])
    lump_data.append(lumps["sectors"])
    # Append empty lumps for the rest.
    lump_data.append(build_empty_lump())
    lump_data.append(build_empty_lump())
    lump_data.append(build_empty_lump())
    lump_data.append(build_empty_lump())
    lump_data.append(build_empty_lump())

    # Now, build the full file data.
    # First, we need to write the header.
    # WAD header: 12 bytes: identification (4 bytes, "PWAD"), numlumps (4 bytes), info table offset (4 bytes)
    identification = b"PWAD"
    numlumps = len(lump_data)

    # The header is 12 bytes; following that are the lumps.
    data = b""
    header_size = 12
    lump_directory = []
    current_offset = header_size  # file offset where lumps begin
    for name, lump in zip(level_lump_names, lump_data):
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
    full_data = struct.pack("<4sII", identification, numlumps, info_table_offset) + data + directory_data
    return full_data


def main():
    if len(sys.argv) < 3:
        print("Usage: python txt2wad.py input_map.txt output.wad")
        sys.exit(1)

    input_txt = sys.argv[1]
    output_wad = sys.argv[2]

    # Read and parse the ASCII map
    grid = read_ascii_map(input_txt)
    if not grid:
        print("Input map is empty or could not be read.")
        sys.exit(1)

    # Extract wall geometry and object placements
    edges = extract_geometry(grid)
    things = extract_things(grid)

    # Build vertices and linedefs from edges
    vertex_list, linedefs = build_vertices_and_linedefs(edges)

    # Build lump data for each level component
    lumps = {}
    lumps["things"] = build_things_lump(things)
    lumps["vertexes"] = build_vertexes_lump(vertex_list)
    lumps["linedefs"] = build_linedefs_lump(linedefs)
    # Create one sidedef per linedef.
    lumps["sidedefs"] = build_sidedefs_lump(len(linedefs))
    lumps["sectors"] = build_sectors_lump()

    # Build the full WAD file binary data
    wad_data = build_wad(lumps)

    # Write output
    with open(output_wad, "wb") as f:
        f.write(wad_data)
    print("WAD file written to", output_wad)


if __name__ == "__main__":
    main()
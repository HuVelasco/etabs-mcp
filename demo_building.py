"""
SURPRISE: Parametric 3D Building Generator for ETABS
Creates a complete steel frame structure using etabs_run_script
"""

from server import etabs_run_script, connect_to_etabs
import json

print('=' * 60)
print('   SURPRISE: PARAMETRIC 3D BUILDING GENERATOR')
print('=' * 60)
print()

# The complete building generation script
building_script = '''
import math

# ═══════════════════════════════════════════════════════════════
#              PARAMETRIC BUILDING GENERATOR
#     Creates a complete 3D steel frame structure in ETABS
# ═══════════════════════════════════════════════════════════════

# BUILDING PARAMETERS (easily adjustable!)
NUM_STORIES = 4
STORY_HEIGHT = 4000.0   # mm (4 meters)
NUM_BAYS_X = 3
NUM_BAYS_Y = 2
BAY_WIDTH_X = 8000.0    # mm (8 meters)
BAY_WIDTH_Y = 6000.0    # mm (6 meters)

# SECTION PROPERTIES
BEAM_SECTION = "W21X50"
COLUMN_SECTION = "W14X90"
BRACE_SECTION = "HSS8X8X1/2"

# Track created elements
created_points = []
created_columns = []
created_beams = []
created_braces = []

print("=" * 60)
print("  PARAMETRIC BUILDING GENERATOR")
print("=" * 60)
print(f"  Stories: {NUM_STORIES} x {STORY_HEIGHT}mm = {NUM_STORIES * STORY_HEIGHT}mm total")
print(f"  Grid: {NUM_BAYS_X} x {NUM_BAYS_Y} bays")
print(f"  Footprint: {NUM_BAYS_X * BAY_WIDTH_X}mm x {NUM_BAYS_Y * BAY_WIDTH_Y}mm")
print("=" * 60)

# Define sections
try:
    # W21X50 beam (imperial dimensions in mm)
    sap_model.PropFrame.SetISection(BEAM_SECTION, "A992Fy50",
        528.32, 166.37, 13.59, 9.65, 166.37, 13.59, -1)
    print(f"Defined beam section: {BEAM_SECTION}")
except: pass

try:
    # W14X90 column
    sap_model.PropFrame.SetISection(COLUMN_SECTION, "A992Fy50",
        355.6, 368.3, 18.03, 11.18, 368.3, 18.03, -1)
    print(f"Defined column section: {COLUMN_SECTION}")
except: pass

try:
    # HSS brace
    sap_model.PropFrame.SetTube(BRACE_SECTION, "A500GrB",
        203.2, 203.2, 12.7, 12.7, -1)
    print(f"Defined brace section: {BRACE_SECTION}")
except: pass

# ═══════════════════════════════════════════════════════════════
#                    CREATE GRID POINTS
# ═══════════════════════════════════════════════════════════════
print("\\nCreating grid points...")
grid_points = {}  # (ix, iy, story) -> point_name

for story in range(NUM_STORIES + 1):  # 0 = base, 1-4 = floors
    z = story * STORY_HEIGHT
    for ix in range(NUM_BAYS_X + 1):
        x = ix * BAY_WIDTH_X
        for iy in range(NUM_BAYS_Y + 1):
            y = iy * BAY_WIDTH_Y

            ret = sap_model.PointObj.AddCartesian(float(x), float(y), float(z), "", "", "Global", False, 0)
            pt_name = str(ret[1])
            grid_points[(ix, iy, story)] = pt_name
            created_points.append(pt_name)

print(f"  Created {len(created_points)} grid points")

# ═══════════════════════════════════════════════════════════════
#                      CREATE COLUMNS
# ═══════════════════════════════════════════════════════════════
print("\\nCreating columns...")

for story in range(NUM_STORIES):
    for ix in range(NUM_BAYS_X + 1):
        for iy in range(NUM_BAYS_Y + 1):
            pt_bottom = grid_points[(ix, iy, story)]
            pt_top = grid_points[(ix, iy, story + 1)]

            ret = sap_model.FrameObj.AddByPoint(pt_bottom, pt_top, COLUMN_SECTION, "", "Global")
            col_name = str(ret[1])
            created_columns.append(col_name)

print(f"  Created {len(created_columns)} columns")

# ═══════════════════════════════════════════════════════════════
#                       CREATE BEAMS
# ═══════════════════════════════════════════════════════════════
print("\\nCreating beams...")

for story in range(1, NUM_STORIES + 1):  # Beams at each floor level
    # X-direction beams
    for iy in range(NUM_BAYS_Y + 1):
        for ix in range(NUM_BAYS_X):
            pt1 = grid_points[(ix, iy, story)]
            pt2 = grid_points[(ix + 1, iy, story)]

            ret = sap_model.FrameObj.AddByPoint(pt1, pt2, BEAM_SECTION, "", "Global")
            beam_name = str(ret[1])
            created_beams.append(beam_name)

    # Y-direction beams
    for ix in range(NUM_BAYS_X + 1):
        for iy in range(NUM_BAYS_Y):
            pt1 = grid_points[(ix, iy, story)]
            pt2 = grid_points[(ix, iy + 1, story)]

            ret = sap_model.FrameObj.AddByPoint(pt1, pt2, BEAM_SECTION, "", "Global")
            beam_name = str(ret[1])
            created_beams.append(beam_name)

print(f"  Created {len(created_beams)} beams")

# ═══════════════════════════════════════════════════════════════
#                   CREATE BRACES (X-pattern)
# ═══════════════════════════════════════════════════════════════
print("\\nCreating braces (perimeter X-bracing)...")

# Add X-braces on perimeter bays only (for lateral stability)
for story in range(NUM_STORIES):
    z_bot = story * STORY_HEIGHT
    z_top = (story + 1) * STORY_HEIGHT

    # Front face (iy = 0) - first and last bay
    for ix in [0, NUM_BAYS_X - 1]:
        x1 = ix * BAY_WIDTH_X
        x2 = (ix + 1) * BAY_WIDTH_X
        y = 0.0

        # Diagonal 1
        ret = sap_model.FrameObj.AddByCoord(x1, y, z_bot, x2, y, z_top, BRACE_SECTION, "", "Global")
        created_braces.append(str(ret[1]))
        # Diagonal 2
        ret = sap_model.FrameObj.AddByCoord(x2, y, z_bot, x1, y, z_top, BRACE_SECTION, "", "Global")
        created_braces.append(str(ret[1]))

    # Back face (iy = NUM_BAYS_Y) - first and last bay
    for ix in [0, NUM_BAYS_X - 1]:
        x1 = ix * BAY_WIDTH_X
        x2 = (ix + 1) * BAY_WIDTH_X
        y = NUM_BAYS_Y * BAY_WIDTH_Y

        ret = sap_model.FrameObj.AddByCoord(x1, y, z_bot, x2, y, z_top, BRACE_SECTION, "", "Global")
        created_braces.append(str(ret[1]))
        ret = sap_model.FrameObj.AddByCoord(x2, y, z_bot, x1, y, z_top, BRACE_SECTION, "", "Global")
        created_braces.append(str(ret[1]))

    # Left face (ix = 0) - first and last bay
    for iy in [0, NUM_BAYS_Y - 1]:
        y1 = iy * BAY_WIDTH_Y
        y2 = (iy + 1) * BAY_WIDTH_Y
        x = 0.0

        ret = sap_model.FrameObj.AddByCoord(x, y1, z_bot, x, y2, z_top, BRACE_SECTION, "", "Global")
        created_braces.append(str(ret[1]))
        ret = sap_model.FrameObj.AddByCoord(x, y2, z_bot, x, y1, z_top, BRACE_SECTION, "", "Global")
        created_braces.append(str(ret[1]))

    # Right face (ix = NUM_BAYS_X) - first and last bay
    for iy in [0, NUM_BAYS_Y - 1]:
        y1 = iy * BAY_WIDTH_Y
        y2 = (iy + 1) * BAY_WIDTH_Y
        x = NUM_BAYS_X * BAY_WIDTH_X

        ret = sap_model.FrameObj.AddByCoord(x, y1, z_bot, x, y2, z_top, BRACE_SECTION, "", "Global")
        created_braces.append(str(ret[1]))
        ret = sap_model.FrameObj.AddByCoord(x, y2, z_bot, x, y1, z_top, BRACE_SECTION, "", "Global")
        created_braces.append(str(ret[1]))

print(f"  Created {len(created_braces)} braces")

# ═══════════════════════════════════════════════════════════════
#                        FINAL SUMMARY
# ═══════════════════════════════════════════════════════════════
total_points = sap_model.PointObj.Count()
total_frames = sap_model.FrameObj.Count()

print("\\n" + "=" * 60)
print("  BUILDING COMPLETE!")
print("=" * 60)
print(f"  Total Points: {total_points}")
print(f"  Total Frames: {total_frames}")
print(f"    - Columns: {len(created_columns)}")
print(f"    - Beams: {len(created_beams)}")
print(f"    - Braces: {len(created_braces)}")
print("=" * 60)

result = {
    "success": True,
    "building": {
        "stories": NUM_STORIES,
        "height_mm": NUM_STORIES * STORY_HEIGHT,
        "height_m": NUM_STORIES * STORY_HEIGHT / 1000,
        "bays_x": NUM_BAYS_X,
        "bays_y": NUM_BAYS_Y,
        "footprint_mm": [NUM_BAYS_X * BAY_WIDTH_X, NUM_BAYS_Y * BAY_WIDTH_Y],
        "footprint_m": [NUM_BAYS_X * BAY_WIDTH_X / 1000, NUM_BAYS_Y * BAY_WIDTH_Y / 1000]
    },
    "elements": {
        "points": len(created_points),
        "columns": len(created_columns),
        "beams": len(created_beams),
        "braces": len(created_braces),
        "total_frames": len(created_columns) + len(created_beams) + len(created_braces)
    },
    "sections": {
        "beams": BEAM_SECTION,
        "columns": COLUMN_SECTION,
        "braces": BRACE_SECTION
    }
}
'''

# Execute the building script
result = etabs_run_script(building_script)
data = json.loads(result)

# Display results
print()
if data.get('stdout'):
    print(data['stdout'])

print()
print('=' * 60)
print('  JSON RESULT')
print('=' * 60)
print(json.dumps(data.get('result', {}), indent=2))

if data.get('success'):
    building = data['result']['building']
    elements = data['result']['elements']
    print()
    print('=' * 60)
    print('  VISUALIZATION TIP')
    print('=' * 60)
    print('  In ETABS: View > Set 3D View > Isometric')
    print('  Or use: View > Refresh View')
    print()
    print(f"  You now have a {building['stories']}-story building")
    print(f"  with {elements['total_frames']} structural members!")
    print('=' * 60)

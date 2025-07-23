# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Running the Application

To run the main application:
```bash
source venv/bin/activate
python main.py
```

The application uses Python 3.12.3 with pyxel 2.4.3 for game development.

## Project Architecture

This is a Python-based isometric grid game built with the pyxel library. Currently in development phase with basic functionality implemented.

### Core Components

- **main.py**: Basic isometric tile renderer (current implementation)
  - Simple `App` class with pyxel initialization and main game loop
  - Basic camera controls (arrow keys for scrolling only)
  - Fixed 3x3 grid with hardcoded height values (1-3 range)
  - Isometric diamond tile rendering with 3D appearance (top, left, right faces)
  - No rotation, zoom, or mouse interaction yet

- **main_backup.py**: Full-featured version with advanced capabilities
  - Complete 3D rotation system with 15-degree increments (24 directions)
  - Dynamic Z-sorting and proper depth rendering
  - Mouse-based tile selection with hover/click effects
  - Camera controls including zoom (0.3x-3.0x) and rotation
  - Integration with FieldGrid for dynamic tile management
  - Compass direction labels with rotation-aware positioning

- **FieldGrid.py**: Grid data structure and tile management (used by main_backup.py)
  - `Tile` dataclass: Stores tile properties (height, ground_type, level, position, center coordinates)
  - `FieldGrid` class: Manages 2D array of tiles with random generation
  - Ground types: "fire", "water", "earth", "wind"
  - Height range: 1-15 with periodic updates via `update_heights()`

- **my_resource.pyxres**: Pyxel resource file containing game assets (images, sounds, maps)

### Current Status (main.py)

**Implemented Features:**
- **Basic Isometric Rendering**: Diamond-shaped tiles with 3D appearance
- **Simple Camera System**: Arrow key scrolling only
- **Fixed Grid**: 3x3 hardcoded height map
- **3D Tile Appearance**: Left/right side faces with proper shading

**Missing Features (available in main_backup.py):**
- 3D rotation system
- Mouse interaction and tile selection
- Zoom functionality
- Dynamic grid management
- Z-sorting for proper depth rendering
- Compass direction system

### Key Constants

```python
WIN_WIDTH = 256          # Window width
WIN_HEIGHT = 256         # Window height  
GRID_SIZE = 3           # Current: 3x3 grid (main_backup.py uses 10x10)
CELL_SIZE = 30          # Diamond tile width (30px horizontal, 15px vertical)
HEIGHT_UNIT = 5         # Vertical pixels per height level
```

### Coordinate System (Current)

Basic 2D isometric projection:
```python
iso_x = (grid_x - grid_y) * (CELL_SIZE // 2) + center_x + offset_x
iso_y = (grid_x + grid_y) * (CELL_SIZE // 4) + center_y + offset_y - height * HEIGHT_UNIT
```

### Controls (Current)

- **Arrow keys**: Camera movement (scroll)
- **Q key**: Quit application

### Advanced Features (main_backup.py)

The backup version contains the full feature set described in the original documentation:
- **3D Rotation System**: 15-degree incremental rotation (24 directions)
- **Dynamic Z-Sorting**: Proper depth rendering for all rotation angles
- **Mouse-based Tile Selection**: Hover highlighting and click selection
- **Advanced Camera**: Scroll, zoom (Z/X keys), rotation (Q/W keys), reset (A key)
- **Real-time Updates**: Configurable height animation system

### Development Environment

- **Virtual Environment**: `venv/` with Python 3.12.3
- **Dependencies**: pyxel 2.4.3 for game development
- **Language**: Mixed Japanese/English (comments and README in Japanese)
- **Version Control**: Git-based with incremental feature commits
- **Architecture**: Currently refactoring from main_backup.py to main.py

### File Structure

```
GridMadness/
├── main.py                    # Current: Basic isometric renderer (3x3 grid)
├── main_backup.py            # Full-featured version with rotation system
├── FieldGrid.py              # Grid data structures and tile management
├── my_resource.pyxres         # Pyxel game assets
├── README.md                 # Project documentation (Japanese)
├── CLAUDE.md                 # Development guidance (this file)
└── venv/                     # Python virtual environment
```

### Development Status

**Current Phase**: Rebuilding main.py from scratch based on main_backup.py reference
- Starting with basic 3x3 isometric grid
- Implementing fundamental rendering before adding advanced features
- main_backup.py serves as reference for full feature implementation

### Extension Points

The system is designed for easy extension:
- **Grid size**: Adjust `GRID_SIZE` constant (currently 3, can expand to 10x10)
- **Tile rendering**: Extend `draw_diamond_tile()` method
- **Camera system**: Add zoom and rotation from main_backup.py
- **Mouse interaction**: Implement tile selection and hover effects
- **Dynamic tiles**: Integrate FieldGrid.py for random generation
- **Visual effects**: Add new rendering methods based on main_backup.py patterns
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

This is a Python-based isometric grid game built with the pyxel library. The project consists of:

### Core Components

- **main.py**: Main application entry point containing the `App` class
  - Handles pyxel initialization and main game loop (update/draw)
  - Manages camera controls (arrow keys for scrolling, Z/X for zoom, Q/W for rotation, A for reset)
  - Handles mouse interactions for tile selection and hover effects
  - Renders the isometric grid with proper depth sorting and 3D rotation

- **FieldGrid.py**: Grid data structure and tile management
  - `Tile` dataclass: Stores tile properties (height, ground_type, level, position, center coordinates)
  - `FieldGrid` class: Manages 2D array of tiles with random generation
  - Ground types: "fire", "water", "earth", "wind"
  - Height range: 1-15 with periodic updates via `update_heights()`

- **my_resource.pyxres**: Pyxel resource file containing game assets (images, sounds, maps)

### Key Features

- **3D Rotation System**: 15-degree incremental rotation (24 directions)
- **Dynamic Z-Sorting**: Proper depth rendering for all rotation angles
- **Isometric 3D Projection**: 10x10 grid with height-based 3D appearance
- **Interactive Camera System**: Scroll, zoom, and rotation controls
- **Mouse-based Tile Selection**: Hover highlighting and click selection
- **Collision Detection**: Center rectangle method for tile selection
- **Real-time Updates**: Configurable height animation system

### Coordinate System

The application uses a multi-stage coordinate transformation:
1. **Grid Coordinates**: Base (x, y) positions in the 10x10 grid
2. **Rotation Transform**: 3D rotation matrix applied around grid center
3. **Isometric Projection**: Converted to isometric screen coordinates
4. **Camera Transform**: Zoom and offset applied for viewport control
5. **Z-Sorting**: Dynamic depth calculation for proper rendering order

Key transformation functions:
- `get_rotated_coordinates(x, y)`: Applies rotation matrix
- `get_tile_depth(x, y)`: Calculates rendering depth for Z-sorting

### Controls

- **Arrow keys**: Camera movement (scroll)
- **Z/X keys**: Zoom in/out (0.3x to 3.0x)
- **Q/W keys**: Rotate view (15-degree steps, 24 directions)
- **A key**: Reset camera position and rotation
- **Mouse**: Hover and click to select tiles
- **Escape**: Quit application

### Rotation System

The rotation system supports:
- **24 discrete directions** (15-degree increments)
- **Configurable step size** (easily adjustable from 15° to 30°, 10°, etc.)
- **Smooth visual transitions** between rotation states
- **Proper Z-sorting** for all rotation angles
- **Performance optimized** with pre-calculated depth values

### Development Environment

- **Virtual Environment**: `venv/` with Python 3.12.3
- **Dependencies**: pyxel 2.4.3 for game development
- **Language**: Mixed Japanese/English (comments and README in Japanese)
- **Version Control**: Git-based with incremental feature commits
- **Architecture**: Modular design with clear separation of concerns

### File Structure

```
GridMadness/
├── main.py                    # Main application with rotation system
├── FieldGrid.py              # Grid data structures and tile management
├── my_resource.pyxres         # Pyxel game assets
├── main_before_rotation.py    # Backup before rotation system
├── main_baclup.py            # Earlier development backup
├── README.md                 # Project documentation (Japanese)
├── CLAUDE.md                 # Development guidance (this file)
└── venv/                     # Python virtual environment
```

### Extension Points

The system is designed for easy extension:
- **Rotation angles**: Modify `self.rotation_step` (15°, 10°, 5°, etc.)
- **Grid size**: Adjust `GRID_SIZE` constant
- **Tile properties**: Extend `Tile` dataclass in FieldGrid.py
- **Visual effects**: Add new rendering methods in main.py
- **Input handling**: Extend key/mouse processing in update() method
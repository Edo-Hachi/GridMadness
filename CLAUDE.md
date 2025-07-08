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
  - Manages camera controls (arrow keys for scrolling, Z/X for zoom, A for reset)
  - Handles mouse interactions for tile selection and hover effects
  - Renders the isometric grid with proper depth sorting

- **FieldGrid.py**: Grid data structure and tile management
  - `Tile` dataclass: Stores tile properties (height, ground_type, level, position, center coordinates)
  - `FieldGrid` class: Manages 2D array of tiles with random generation
  - Ground types: "fire", "water", "earth", "wind"
  - Height range: 1-15 with periodic updates via `update_heights()`

- **my_resource.pyxres**: Pyxel resource file containing game assets (images, sounds, maps)

### Key Features

- Isometric 3D projection of a 10x10 grid
- Interactive camera system with scroll and zoom
- Mouse-based tile selection with hover highlighting
- Tile collision detection using center rectangle method
- Real-time height updates (configurable via frame counter)

### Coordinate System

The application uses isometric transformation:
- Grid coordinates (x, y) are converted to isometric screen coordinates
- Height affects Y-offset for 3D appearance
- Zoom and camera offset are applied for viewport control

### Controls

- Arrow keys: Camera movement
- Z/X keys: Zoom in/out
- A key: Reset camera position
- Mouse: Hover and click to select tiles
- Escape: Quit application

### Development Environment

- Uses virtual environment in `venv/`
- Project written in Japanese (comments and README)
- No test framework or build system detected
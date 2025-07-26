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
├── main.py                    # Main: Full-featured isometric renderer with all systems
├── isometric_renderer.py      # Unified coordinate calculation with caching
├── mouse_hit_detector.py      # Precision diamond-shaped hit detection
├── viewport_manager.py        # Viewport management with LRU cache (currently bypassed)
├── FieldGrid.py              # Grid data structures and tile management
├── my_resource.pyxres         # Pyxel game assets
├── map_data.json             # Saved/loaded map data
├── GridMadness_20250726/     # Archive: Modularized reference implementation
├── README.md                 # Project documentation (Japanese)
├── CLAUDE.md                 # Development guidance (this file)
└── venv/                     # Python virtual environment
```

### Development Status

**Current Phase**: 完全実装完了 (Full Implementation Completed)
- ✅ 256x256 MapGrid with 16x16 viewport system
- ✅ 3D rotation system (Q/E keys, 15-degree steps)
- ✅ Zoom functionality (Z/X keys, 0.3x-3.0x range)
- ✅ Z-sorting for proper depth rendering
- ✅ Mouse interaction with hover/click selection
- ✅ Camera reset functionality (C key)
- ✅ Mouse wheel zoom support
- ✅ JSON save/load system (F1/F2 keys)
- ✅ Manual random map generation (F3 key)

**Final Implementation Features:**
- **WASD**: Viewport navigation through 256x256 map
- **Q/E**: 3D rotation (24 directions, 15° increments)
- **Z/X**: Zoom in/out (0.3x-3.0x range)
- **Mouse**: Hover (green) and click selection (blue) with wheel zoom
- **C**: Reset all camera settings to initial state
- **Arrow keys**: Fine camera adjustment/offset
- **F1**: Save map data to JSON file
- **F2**: Load map data from JSON file
- **F3**: Generate new random map manually
- **ESCAPE**: Quit application

**Map System:**
- 256x256 full map with Tile dataclass (floor_id, height, attribute, color)
- 16x16 viewport display with smooth navigation
- Empty flat map initialization (grass terrain, height=1)
- Manual random generation instead of automatic on startup

### Known Issues

**Mouse Collision Detection**:
- ✅ **RESOLVED**: マウスクリック当たり判定のずれ問題を解決
- MouseHitDetectorによる精密な三角形ベースのひし形当たり判定を実装
- 回転・ズーム時でも正確な判定が可能

**ViewportManager Cache Issue** (2025-07-26):
- ✅ **RESOLVED**: ViewportManagerのキャッシュシステム問題を完全修正
- **原因**: `clear_cache()`後に`self.current_tiles`が更新されていなかった
- **根本問題**: `set_viewport_position()`が位置変更時のみ`_update_current_tiles()`を実行
- **影響**: JSONロード、ランダムマップ生成、リセット機能の即座反映不良

**Technical Solution**:
- **修正1**: `clear_cache()`メソッドに`self._update_current_tiles()`を追加
- **修正2**: `set_viewport_position()`に`force_update`オプションを追加
- **修正3**: ViewportManager使用を復活、パフォーマンス最適化も復活
- **結果**: 
  ```
  MapGrid直接アクセス:     height=2, color=8  ✅
  ViewportManager経由:     height=2, color=8  ✅ (完全一致)
  キャッシュ統計:          tile_cache_size=100, viewport_cache_size=1  ✅
  ```

**Performance Benefits Restored**:
- LRUキャッシュによるタイル取得の高速化が復活
- ビューポート移動時のスムーズなレスポンス
- メモリ効率的なタイル管理

### Development Log

**2025-07-26: モジュール化リファクタリング完了**
- GridMadness_20250726からIsometricRenderer・MouseHitDetector・ViewportManagerを統合
- IsometricRendererによる座標計算の統一とキャッシュ機能実装
- MouseHitDetectorによる精密なひし形当たり判定（三角形分割法）
- 高さシステム変更：HEIGHT_UNIT=3ピクセル、1-5段階の高さ範囲
- 側面ポリゴンの高さ反映修正（ズーム対応）
- カメラ操作の改善：矢印キー上下左右リバース
- ViewportManagerキャッシュ問題の完全修正（パフォーマンス最適化復活）

**2025-07-23: 完全システム実装完了**
- main.py を main_backup.py を参考に完全作り直し
- 11段階の実装プランを段階的に実行
- 全機能実装完了：256x256マップ、3D回転、ズーム、マウス操作、保存機能
- キーバインド調整完了：競合回避（E回転、Cリセット、F1/F2/F3機能キー）
- 初期化時ランダム生成を無効化、手動生成（F3）に変更

**実装アプローチ:**
- バイブコーディング手法：動作するmain_backup.pyを参考実装として活用
- 段階的開発：各ステップで動作確認とユーザーフィードバック反映
- 明確な要件定義：refact_plan.txtベースの具体的仕様

**技術的成果:**
- Tile dataclass設計（floor_id, height, attribute, color）
- MapGrid class with viewport system
- 3D coordinate transformation with rotation matrix
- Z-sorting algorithm for proper depth rendering
- JSON serialization for map persistence
- Mouse collision detection with center rectangle method

### Extension Points

The system is now ready for advanced extensions:
- **Terrain editing**: Interactive map modification tools
- **More precise collision**: Improve diamond-shaped hit detection from current center rectangle method
- **Visual effects**: Add particle effects or animations  
- **Multi-layer support**: Height-based layer system
- **AI features**: Pathfinding, procedural generation algorithms
- **Network support**: Multiplayer functionality
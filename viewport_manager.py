"""
ビューポート管理の最適化とモジュール化
"""
from typing import List, Tuple, Optional, Dict, Any
from dataclasses import dataclass
import json


@dataclass
class ViewportState:
    """ビューポート状態を管理するデータクラス"""
    x: int = 120  # マップ内のX位置
    y: int = 120  # マップ内のY位置
    size: int = 16  # ビューポートサイズ（16x16）
    
    def __post_init__(self):
        """初期化後の検証"""
        self.x = max(0, min(self.x, 256 - self.size))
        self.y = max(0, min(self.y, 256 - self.size))


class ViewportManager:
    """ビューポート管理の最適化クラス"""
    
    def __init__(self, map_grid, viewport_size: int = 16, cache_size: int = 100):
        """
        初期化
        
        Args:
            map_grid: マップグリッドオブジェクト
            viewport_size: ビューポートサイズ
            cache_size: キャッシュサイズ（LRU）
        """
        self.map_grid = map_grid
        self.viewport_size = viewport_size
        self.cache_size = cache_size
        
        # ビューポート状態
        self.viewport_state = ViewportState(size=viewport_size)
        
        # タイルキャッシュ（LRU方式）
        self.tile_cache: Dict[Tuple[int, int], Any] = {}
        self.cache_access_order: List[Tuple[int, int]] = []
        
        # ビューポートキャッシュ
        self.viewport_cache: Dict[Tuple[int, int, int], List[List[Any]]] = {}
        self.viewport_access_order: List[Tuple[int, int, int]] = []
        
        # 統計情報
        self.cache_hits = 0
        self.cache_misses = 0
        self.viewport_cache_hits = 0
        self.viewport_cache_misses = 0
        
        # 現在のビューポートタイル
        self.current_tiles = None
        self._update_current_tiles()
    
    def _update_lru_cache(self, cache_dict: Dict, access_order: List, key: Any, value: Any, max_size: int):
        """LRUキャッシュの更新"""
        if key in cache_dict:
            # 既存キーの場合、アクセス順序を更新
            access_order.remove(key)
        elif len(cache_dict) >= max_size:
            # キャッシュが満杯の場合、最古のエントリを削除
            oldest_key = access_order.pop(0)
            del cache_dict[oldest_key]
        
        cache_dict[key] = value
        access_order.append(key)
    
    def get_tile_cached(self, x: int, y: int) -> Any:
        """
        キャッシュ付きタイル取得
        
        Args:
            x, y: マップ座標
            
        Returns:
            タイルオブジェクト
        """
        cache_key = (x, y)
        
        if cache_key in self.tile_cache:
            self.cache_hits += 1
            # アクセス順序を更新
            self.cache_access_order.remove(cache_key)
            self.cache_access_order.append(cache_key)
            return self.tile_cache[cache_key]
        
        self.cache_misses += 1
        tile = self.map_grid.get_tile(x, y)
        
        if tile is not None:
            self._update_lru_cache(
                self.tile_cache, self.cache_access_order, 
                cache_key, tile, self.cache_size
            )
        
        return tile
    
    def get_viewport_tiles_cached(self, start_x: int, start_y: int, size: int) -> List[List[Any]]:
        """
        キャッシュ付きビューポートタイル取得
        
        Args:
            start_x, start_y: 開始座標
            size: ビューポートサイズ
            
        Returns:
            ビューポートタイル配列
        """
        cache_key = (start_x, start_y, size)
        
        if cache_key in self.viewport_cache:
            self.viewport_cache_hits += 1
            # アクセス順序を更新
            self.viewport_access_order.remove(cache_key)
            self.viewport_access_order.append(cache_key)
            return self.viewport_cache[cache_key]
        
        self.viewport_cache_misses += 1
        
        # ビューポートタイルを生成
        viewport = []
        for y in range(size):
            row = []
            for x in range(size):
                map_x = start_x + x
                map_y = start_y + y
                tile = self.get_tile_cached(map_x, map_y)
                
                if tile is None:
                    # 範囲外の場合はダミータイルを作成
                    from main import Tile  # 循環インポートを避けるため
                    import pyxel
                    tile = Tile(
                        floor_id=f"{map_x:03d}_{map_y:03d}",
                        height=1,
                        attribute=0,
                        color=pyxel.COLOR_BLACK
                    )
                row.append(tile)
            viewport.append(row)
        
        # ビューポートキャッシュに保存
        self._update_lru_cache(
            self.viewport_cache, self.viewport_access_order,
            cache_key, viewport, 20  # ビューポートキャッシュは小さめ
        )
        
        return viewport
    
    def _update_current_tiles(self):
        """現在のビューポートタイルを更新"""
        self.current_tiles = self.get_viewport_tiles_cached(
            self.viewport_state.x, self.viewport_state.y, self.viewport_state.size
        )
    
    def move_viewport(self, dx: int, dy: int) -> bool:
        """
        ビューポートを移動
        
        Args:
            dx, dy: 移動量
            
        Returns:
            移動が実行されたかどうか
        """
        new_x = self.viewport_state.x + dx
        new_y = self.viewport_state.y + dy
        
        # 範囲チェック
        new_x = max(0, min(new_x, 256 - self.viewport_state.size))
        new_y = max(0, min(new_y, 256 - self.viewport_state.size))
        
        if new_x != self.viewport_state.x or new_y != self.viewport_state.y:
            self.viewport_state.x = new_x
            self.viewport_state.y = new_y
            self._update_current_tiles()
            return True
        
        return False
    
    def set_viewport_position(self, x: int, y: int) -> bool:
        """
        ビューポート位置を直接設定
        
        Args:
            x, y: 新しい位置
            
        Returns:
            位置が変更されたかどうか
        """
        # 範囲チェック
        x = max(0, min(x, 256 - self.viewport_state.size))
        y = max(0, min(y, 256 - self.viewport_state.size))
        
        if x != self.viewport_state.x or y != self.viewport_state.y:
            self.viewport_state.x = x
            self.viewport_state.y = y
            self._update_current_tiles()
            return True
        
        return False
    
    def get_current_tiles(self) -> List[List[Any]]:
        """現在のビューポートタイルを取得"""
        return self.current_tiles
    
    def get_viewport_position(self) -> Tuple[int, int]:
        """現在のビューポート位置を取得"""
        return self.viewport_state.x, self.viewport_state.y
    
    def get_viewport_bounds(self) -> Tuple[int, int, int, int]:
        """ビューポートの境界を取得 (min_x, min_y, max_x, max_y)"""
        return (
            self.viewport_state.x,
            self.viewport_state.y,
            self.viewport_state.x + self.viewport_state.size - 1,
            self.viewport_state.y + self.viewport_state.size - 1
        )
    
    def is_position_in_viewport(self, map_x: int, map_y: int) -> bool:
        """指定された座標がビューポート内にあるかチェック"""
        min_x, min_y, max_x, max_y = self.get_viewport_bounds()
        return min_x <= map_x <= max_x and min_y <= map_y <= max_y
    
    def map_to_viewport_coords(self, map_x: int, map_y: int) -> Optional[Tuple[int, int]]:
        """
        マップ座標をビューポート座標に変換
        
        Args:
            map_x, map_y: マップ座標
            
        Returns:
            ビューポート座標 (None if outside viewport)
        """
        if not self.is_position_in_viewport(map_x, map_y):
            return None
        
        viewport_x = map_x - self.viewport_state.x
        viewport_y = map_y - self.viewport_state.y
        return viewport_x, viewport_y
    
    def viewport_to_map_coords(self, viewport_x: int, viewport_y: int) -> Tuple[int, int]:
        """
        ビューポート座標をマップ座標に変換
        
        Args:
            viewport_x, viewport_y: ビューポート座標
            
        Returns:
            マップ座標
        """
        map_x = self.viewport_state.x + viewport_x
        map_y = self.viewport_state.y + viewport_y
        return map_x, map_y
    
    def clear_cache(self):
        """全キャッシュをクリア"""
        self.tile_cache.clear()
        self.cache_access_order.clear()
        self.viewport_cache.clear()
        self.viewport_access_order.clear()
        self.cache_hits = 0
        self.cache_misses = 0
        self.viewport_cache_hits = 0
        self.viewport_cache_misses = 0
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """キャッシュ統計を取得"""
        total_requests = self.cache_hits + self.cache_misses
        viewport_total = self.viewport_cache_hits + self.viewport_cache_misses
        
        return {
            'tile_cache_size': len(self.tile_cache),
            'tile_cache_hits': self.cache_hits,
            'tile_cache_misses': self.cache_misses,
            'tile_cache_ratio': self.cache_hits / total_requests * 100 if total_requests > 0 else 0,
            'viewport_cache_size': len(self.viewport_cache),
            'viewport_cache_hits': self.viewport_cache_hits,
            'viewport_cache_misses': self.viewport_cache_misses,
            'viewport_cache_ratio': self.viewport_cache_hits / viewport_total * 100 if viewport_total > 0 else 0,
            'viewport_position': (self.viewport_state.x, self.viewport_state.y),
            'viewport_size': self.viewport_state.size
        }
    
    def preload_surrounding_area(self, radius: int = 1):
        """
        現在のビューポート周辺エリアを事前読み込み
        
        Args:
            radius: 事前読み込み半径（ビューポートサイズ単位）
        """
        current_x, current_y = self.get_viewport_position()
        size = self.viewport_state.size
        
        for dy in range(-radius, radius + 1):
            for dx in range(-radius, radius + 1):
                preload_x = current_x + dx * size
                preload_y = current_y + dy * size
                
                # 範囲内の場合のみ事前読み込み
                if (0 <= preload_x <= 256 - size and 
                    0 <= preload_y <= 256 - size):
                    self.get_viewport_tiles_cached(preload_x, preload_y, size)
    
    def reset_to_center(self):
        """ビューポートを中央にリセット"""
        center_x = (256 - self.viewport_state.size) // 2
        center_y = (256 - self.viewport_state.size) // 2
        self.set_viewport_position(center_x, center_y)

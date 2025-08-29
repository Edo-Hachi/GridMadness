"""
アイソメトリック座標計算を統一管理するモジュール
"""
import math
from typing import Tuple, Optional, Dict, Any
from dataclasses import dataclass


@dataclass
class CameraState:
    """カメラの状態を管理するデータクラス"""
    rotation: float = 0.0  # 回転角度（度）
    zoom: float = 1.0      # ズーム倍率
    offset_x: float = 0.0  # X軸オフセット
    offset_y: float = 0.0  # Y軸オフセット
    center_x: float = 128.0  # 画面中心X
    center_y: float = 96.0   # 画面中心Y


class IsometricRenderer:
    """アイソメトリック座標計算を統一管理するクラス"""
    
    def __init__(self, cell_size: int = 16, height_unit: int = 5):
        """
        初期化
        
        Args:
            cell_size: タイルのサイズ（ピクセル）
            height_unit: 高さ1段あたりのピクセル数
        """
        self.cell_size = cell_size
        self.height_unit = height_unit
        self._coord_cache = {}  # 座標キャッシュ
        self._cache_hits = 0
        self._cache_misses = 0
        
    def clear_cache(self):
        """座標キャッシュをクリア"""
        self._coord_cache.clear()
        self._cache_hits = 0
        self._cache_misses = 0
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """キャッシュ統計を取得"""
        total_requests = self._cache_hits + self._cache_misses
        cache_ratio = self._cache_hits / total_requests * 100 if total_requests > 0 else 0
        
        return {
            'cache_hits': self._cache_hits,
            'cache_misses': self._cache_misses,
            'cache_ratio': cache_ratio,
            'total_requests': total_requests
        }
    
    def _rotate_coordinates(self, grid_x: float, grid_y: float, rotation: float, center: Tuple[float, float] = (0, 0)) -> Tuple[float, float]:
        """
        グリッド座標を回転させる
        
        Args:
            grid_x, grid_y: グリッド座標
            rotation: 回転角度（度）
            center: 回転中心（デフォルトは原点）
            
        Returns:
            回転後の座標
        """
        if rotation == 0:
            return grid_x, grid_y
            
        angle_rad = math.radians(rotation)
        cos_a = math.cos(angle_rad)
        sin_a = math.sin(angle_rad)
        
        # 回転中心からの相対座標
        rel_x = grid_x - center[0]
        rel_y = grid_y - center[1]
        
        # 回転変換
        rotated_x = rel_x * cos_a - rel_y * sin_a + center[0]
        rotated_y = rel_x * sin_a + rel_y * cos_a + center[1]
        
        return rotated_x, rotated_y
    
    def grid_to_iso(self, grid_x: float, grid_y: float, height: float = 0, 
                   camera_state: Optional[CameraState] = None) -> Tuple[float, float]:
        """
        グリッド座標をアイソメトリック座標に変換
        
        Args:
            grid_x, grid_y: グリッド座標
            height: タイルの高さ
            camera_state: カメラ状態（None の場合はデフォルト値使用）
            
        Returns:
            アイソメトリック座標 (x, y)
        """
        if camera_state is None:
            camera_state = CameraState()
        
        # キャッシュキーを生成
        cache_key = (grid_x, grid_y, height, camera_state.rotation, 
                    camera_state.zoom, camera_state.offset_x, camera_state.offset_y,
                    camera_state.center_x, camera_state.center_y)
        
        # キャッシュから取得を試行
        if cache_key in self._coord_cache:
            self._cache_hits += 1
            return self._coord_cache[cache_key]
        
        self._cache_misses += 1
        
        # 回転計算（ビューポート中心を基準）
        viewport_center = (8.0, 8.0)  # 16x16ビューポートの中心
        rotated_x, rotated_y = self._rotate_coordinates(
            grid_x, grid_y, camera_state.rotation, viewport_center
        )
        
        # アイソメトリック変換
        iso_x = (rotated_x - rotated_y) * (self.cell_size // 2)
        iso_y = (rotated_x + rotated_y) * (self.cell_size // 4) - height * self.height_unit
        
        # ズーム変換（アイソメトリック座標にズームを適用してからオフセットと中心を適用）
        zoomed_x = iso_x * camera_state.zoom
        zoomed_y = iso_y * camera_state.zoom
        
        # オフセットと画面中心を適用
        final_x = camera_state.center_x + zoomed_x + camera_state.offset_x
        final_y = camera_state.center_y + zoomed_y + camera_state.offset_y
        
        result = (final_x, final_y)
        self._coord_cache[cache_key] = result
        return result
    
    def calculate_diamond_vertices(self, center_x: float, center_y: float, 
                                 scaled_cell_size: int, height: float = 0, zoom: float = 1.0) -> dict:
        """
        ダイアモンド形状の頂点座標を計算
        
        Args:
            center_x, center_y: 中心座標
            scaled_cell_size: ズーム適用済みのセルサイズ
            height: タイルの高さ
            zoom: ズーム倍率
            
        Returns:
            頂点座標の辞書 {'top', 'left', 'right', 'bottom', 'bottom_left', 'bottom_right', 'bottom_bottom'}
        """
        scaled_height = int(height * self.height_unit * zoom)
        
        # 上面の4頂点
        top = (center_x + scaled_cell_size // 2, center_y)
        left = (center_x, center_y + scaled_cell_size // 4)
        right = (center_x + scaled_cell_size, center_y + scaled_cell_size // 4)
        bottom = (center_x + scaled_cell_size // 2, center_y + scaled_cell_size // 2)
        
        # 側面の下側頂点（高さ分だけ下に移動）
        bottom_left = (left[0], left[1] + scaled_height)
        bottom_right = (right[0], right[1] + scaled_height)
        bottom_bottom = (bottom[0], bottom[1] + scaled_height)
        
        return {
            'top': top,
            'left': left,
            'right': right,
            'bottom': bottom,
            'bottom_left': bottom_left,
            'bottom_right': bottom_right,
            'bottom_bottom': bottom_bottom
        }
    
    def get_tile_depth(self, grid_x: float, grid_y: float, height: float, 
                      camera_state: Optional[CameraState] = None) -> float:
        """
        Z-ソート用の深度値を計算
        
        Args:
            grid_x, grid_y: グリッド座標
            height: タイルの高さ
            camera_state: カメラ状態
            
        Returns:
            深度値（小さいほど奥）
        """
        if camera_state is None:
            camera_state = CameraState()
        
        # 回転後の座標を取得
        viewport_center = (8.0, 8.0)
        rotated_x, rotated_y = self._rotate_coordinates(
            grid_x, grid_y, camera_state.rotation, viewport_center
        )
        
        # アイソメトリック投影での正しい深度計算
        # 従来の実装では回転後のY座標のみを使用していたが、これは180度回転時に
        # Z-ソートが逆転して表示が崩れる問題があった。
        # アイソメトリック座標系では、奥行き（深度）は回転後のX座標とY座標の
        # 合計値で正確に表現される。これにより全回転角度で一貫した描画順序を実現。
        # 修正前: depth = rotated_y - height * 0.1 (Y座標のみ、180度で破綻)
        # 修正後: iso_depth = rotated_x + rotated_y - height * 0.1 (X+Y座標、全角度対応)
        iso_depth = rotated_x + rotated_y - height * 0.1
        return iso_depth
    
    def is_point_in_diamond(self, point_x: float, point_y: float, 
                           diamond_center_x: float, diamond_center_y: float,
                           diamond_width: float, diamond_height: float) -> bool:
        """
        点がダイアモンド形状内にあるかを判定（簡易版）
        
        Args:
            point_x, point_y: 判定する点の座標
            diamond_center_x, diamond_center_y: ダイアモンドの中心座標
            diamond_width, diamond_height: ダイアモンドの幅と高さ
            
        Returns:
            点がダイアモンド内にある場合True
        """
        # 中央の矩形を使った簡易判定
        half_width = diamond_width // 4
        half_height = diamond_height // 4
        
        return (diamond_center_x - half_width <= point_x <= diamond_center_x + half_width and
                diamond_center_y - half_height <= point_y <= diamond_center_y + half_height)

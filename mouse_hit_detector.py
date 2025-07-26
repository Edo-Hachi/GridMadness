"""
マウスヒット検出の最適化モジュール（フェーズ4）
"""
import math
import logging
import os
from typing import Optional, Tuple, List, Dict, Any
from dataclasses import dataclass


@dataclass
class HitResult:
    """ヒット検出結果"""
    grid_x: int
    grid_y: int
    map_x: int
    map_y: int
    depth: float
    distance_from_center: float


class MouseHitDetector:
    """マウスヒット検出の最適化クラス"""
    
    def __init__(self, isometric_renderer, viewport_manager, cell_size: int = 16, height_unit: int = 5, debug_mode: bool = False):
        """
        初期化
        
        Args:
            isometric_renderer: IsometricRendererインスタンス
            viewport_manager: ViewportManagerインスタンス
            cell_size: セルサイズ
            height_unit: 高さ単位
            debug_mode: デバッグモード
        """
        self.isometric_renderer = isometric_renderer
        self.viewport_manager = viewport_manager
        self.cell_size = cell_size
        self.height_unit = height_unit
        self.debug_mode = debug_mode
        
        # デバッグログの設定
        if self.debug_mode:
            # 既存のログファイルを削除（確実な上書きのため）
            log_file = 'debug.log'
            if os.path.exists(log_file):
                os.remove(log_file)
            
            # ログ設定をクリア
            for handler in logging.root.handlers[:]:
                logging.root.removeHandler(handler)
            
            logging.basicConfig(
                filename=log_file,
                level=logging.DEBUG,
                format='%(asctime)s - %(message)s',
                filemode='w'  # 毎回ファイルを上書き
            )
            self.logger = logging.getLogger('MouseHitDetector')
            self.logger.info("=== 新しいデバッグセッション開始 ===")
        
        # 統計情報
        self.hit_tests = 0
        self.successful_hits = 0
        self.cache_hits = 0
        self.cache_misses = 0
        
        # 結果キャッシュ（マウス座標→結果）
        self.result_cache: Dict[Tuple[int, int], Optional[HitResult]] = {}
        self.cache_max_size = 50
    
    def get_tile_at_mouse(self, mouse_x: int, mouse_y: int, camera_state, current_tiles, 
                         win_width: int = 256, win_height: int = 192) -> Optional[Tuple[int, int]]:
        """
        マウス座標からタイルを検出（最適化版）
        
        Args:
            mouse_x, mouse_y: マウス座標
            camera_state: カメラ状態
            current_tiles: 現在のビューポートタイル
            win_width, win_height: ウィンドウサイズ
            
        Returns:
            ヒットしたタイルの座標 (grid_x, grid_y) または None
        """
        self.hit_tests += 1
        
        # キャッシュチェック
        cache_key = (mouse_x, mouse_y)
        if cache_key in self.result_cache:
            self.cache_hits += 1
            result = self.result_cache[cache_key]
            return (result.grid_x, result.grid_y) if result else None
        
        self.cache_misses += 1
        
        # 逆座標変換でおおよそのグリッド座標を計算
        candidates = self._get_candidate_tiles(mouse_x, mouse_y, camera_state, win_width, win_height)
        
        # 候補タイルに対して精密な当たり判定
        best_hit = None
        
        viewport_state = self.viewport_manager.viewport_state
        
        # 候補タイルを深度と高さでソート（手前から奥、高い床から低い床）
        candidate_tiles = []
        for viewport_x, viewport_y in candidates:
            # ビューポート座標をマップ座標に変換
            map_x = viewport_x + viewport_state.x
            map_y = viewport_y + viewport_state.y
            
            # 実際の256x256マップからタイルを取得
            tile = self.viewport_manager.get_tile_cached(map_x, map_y)
            
            if tile is None:
                continue
                
            # 深度計算
            depth = self.isometric_renderer.get_tile_depth(viewport_x, viewport_y, tile.height, camera_state)
            
            candidate_tiles.append((viewport_x, viewport_y, tile, map_x, map_y, depth))
        
        # ソート: 1. 深度（手前から奥）, 2. 高さ（高い床から低い床）
        candidate_tiles.sort(key=lambda x: (x[5], -x[2].height))  # depth昇順, height降順
        
        for viewport_x, viewport_y, tile, map_x, map_y, depth in candidate_tiles:
            # 精密ひし形判定（ビューポート座標使用）
            hit_result = self._is_point_in_diamond(mouse_x, mouse_y, viewport_x, viewport_y, tile, camera_state, win_width, win_height)
            if hit_result:
                
                # マウス位置からタイル中心までの距離
                center_x, center_y = self._get_tile_screen_center(viewport_x, viewport_y, tile, camera_state, win_width, win_height)
                distance = math.sqrt((mouse_x - center_x) ** 2 + (mouse_y - center_y) ** 2)
                
                # デバッグログ出力
                if self.debug_mode:
                    dx = mouse_x - center_x
                    dy = mouse_y - center_y
                    self.logger.debug(f"HIT DETECTED - Mouse({mouse_x}, {mouse_y}) -> Tile({viewport_x}, {viewport_y})")
                    self.logger.debug(f"  Tile height: {tile.height}")
                    self.logger.debug(f"  Tile depth: {depth:.1f}")
                    self.logger.debug(f"  Tile center: ({center_x:.1f}, {center_y:.1f})")
                    self.logger.debug(f"  Mouse relative to center: dx={dx:.1f}, dy={dy:.1f}")
                    self.logger.debug(f"  Distance from center: {distance:.1f}")
                    self.logger.debug(f"  Map coordinates: ({map_x}, {map_y})")
                    self.logger.debug(f"  Selected (Z-sort + height-sort priority)")
                
                # 最初にヒットしたタイルを選択（既にソート済みなので最優先）
                best_hit = HitResult(
                    grid_x=viewport_x,
                    grid_y=viewport_y,
                    map_x=map_x,
                    map_y=map_y,
                    depth=depth,
                    distance_from_center=distance
                )
                break  # 最優先タイルが見つかったので終了
        
        # 結果をキャッシュ
        self._cache_result(cache_key, best_hit)
        
        if best_hit:
            self.successful_hits += 1
            return (best_hit.grid_x, best_hit.grid_y)
        
        return None
    
    def _get_candidate_tiles(self, mouse_x: int, mouse_y: int, camera_state, win_width: int, win_height: int) -> List[Tuple[int, int]]:
        """
        逆座標変換でマウス位置周辺の候補タイルを取得
        
        Args:
            mouse_x, mouse_y: マウス座標
            camera_state: カメラ状態
            win_width, win_height: ウィンドウサイズ
            
        Returns:
            候補タイル座標のリスト
        """
        center_x = win_width // 2
        center_y = win_height // 2
        
        # ズームとオフセットを逆算
        unzoomed_x = center_x + (mouse_x - center_x) / camera_state.zoom
        unzoomed_y = center_y + (mouse_y - center_y) / camera_state.zoom
        
        # オフセットを除去
        iso_x = unzoomed_x - center_x - camera_state.offset_x
        iso_y = unzoomed_y - center_y - camera_state.offset_y
        
        # アイソメトリック座標からグリッド座標への逆変換
        # iso_x = (grid_x - grid_y) * (cell_size / 2)
        # iso_y = (grid_x + grid_y) * (cell_size / 4)
        # これを解くと:
        # grid_x = (iso_x / (cell_size / 2) + iso_y / (cell_size / 4)) / 2
        # grid_y = (iso_y / (cell_size / 4) - iso_x / (cell_size / 2)) / 2
        
        half_cell = self.cell_size / 2
        quarter_cell = self.cell_size / 4
        
        grid_x_float = (iso_x / half_cell + iso_y / quarter_cell) / 2
        grid_y_float = (iso_y / quarter_cell - iso_x / half_cell) / 2
        
        # 回転を考慮した逆変換
        if camera_state.rotation != 0:
            angle_rad = -math.radians(camera_state.rotation)  # 逆回転
            cos_angle = math.cos(angle_rad)
            sin_angle = math.sin(angle_rad)
            
            # 回転中心（ビューポート中心）
            viewport_size = self.viewport_manager.viewport_state.size
            center = viewport_size // 2
            
            # 回転中心からの相対座標
            rel_x = grid_x_float - center
            rel_y = grid_y_float - center
            
            # 逆回転
            unrotated_x = rel_x * cos_angle - rel_y * sin_angle
            unrotated_y = rel_x * sin_angle + rel_y * cos_angle
            
            grid_x_float = unrotated_x + center
            grid_y_float = unrotated_y + center
        
        # 候補タイルを周辺も含めて取得（精度向上のため）
        base_x = int(grid_x_float)
        base_y = int(grid_y_float)
        
        candidates = []
        for dy in range(-2, 3):  # 5x5の範囲をチェック
            for dx in range(-2, 3):
                candidate_x = base_x + dx
                candidate_y = base_y + dy
                # ビューポート範囲内チェック
                if 0 <= candidate_x < self.viewport_manager.viewport_state.size and 0 <= candidate_y < self.viewport_manager.viewport_state.size:
                    candidates.append((candidate_x, candidate_y))
        
        return candidates
    
    def _is_point_in_diamond(self, mouse_x: int, mouse_y: int, grid_x: int, grid_y: int, 
                           tile, camera_state, win_width: int, win_height: int) -> bool:
        """
        精密なひし形内判定を実行
        
        Args:
            mouse_x, mouse_y: マウス座標
            grid_x, grid_y: グリッド座標
            tile: タイルオブジェクト
            camera_state: カメラ状態
            win_width, win_height: ウィンドウサイズ
            
        Returns:
            ひし形内にあるかどうか
        """
        # 実際のタイル高さで判定（描画とヒット判定の一致）
        screen_coords = self.isometric_renderer.grid_to_iso(
            grid_x, grid_y, tile.height, camera_state
        )
        
        if screen_coords is None:
            return False
        
        iso_x, iso_y = screen_coords
        
        # ズーム適用されたセルサイズ
        scaled_cell_size = int(self.cell_size * camera_state.zoom)
        
        # ひし形の4頂点を計算（IsometricRenderer.calculate_diamond_vertices()と完全一致）
        # 描画とヒット判定の一貫性を保つため、同じ計算式を使用
        top = (iso_x + scaled_cell_size // 2, iso_y)
        left = (iso_x, iso_y + scaled_cell_size // 4)
        right = (iso_x + scaled_cell_size, iso_y + scaled_cell_size // 4)
        bottom = (iso_x + scaled_cell_size // 2, iso_y + scaled_cell_size // 2)
        
        # デバッグログ出力
        if self.debug_mode:
            self.logger.debug(f"Diamond test for tile ({grid_x}, {grid_y}):")
            self.logger.debug(f"  Tile height: {tile.height}")
            self.logger.debug(f"  Screen coords (height={tile.height}): ({iso_x}, {iso_y})")
            self.logger.debug(f"  Scaled cell size: {scaled_cell_size}")
            self.logger.debug(f"  Diamond dimensions: width={scaled_cell_size}, height={scaled_cell_size // 2}")
            self.logger.debug(f"  Diamond vertices: top{top}, left{left}, right{right}, bottom{bottom}")
            self.logger.debug(f"  Mouse position: ({mouse_x}, {mouse_y})")
        
        # ひし形内判定（4つの三角形に分割して判定）
        in_diamond = (self._point_in_triangle(mouse_x, mouse_y, top, left, bottom) or
                      self._point_in_triangle(mouse_x, mouse_y, top, right, bottom) or
                      self._point_in_triangle(mouse_x, mouse_y, left, bottom, right) or
                      self._point_in_triangle(mouse_x, mouse_y, top, left, right))
        
        if self.debug_mode:
            self.logger.debug(f"  Diamond hit test: {in_diamond}")
        
        return in_diamond
    
    def _point_in_triangle(self, px: float, py: float, p1: Tuple[float, float], 
                          p2: Tuple[float, float], p3: Tuple[float, float]) -> bool:
        """
        点が三角形内にあるかどうかを判定
        
        Args:
            px, py: 判定する点の座標
            p1, p2, p3: 三角形の頂点
            
        Returns:
            三角形内にあるかどうか
        """
        x1, y1 = p1
        x2, y2 = p2
        x3, y3 = p3
        
        # 重心座標を使用した判定
        denom = (y2 - y3) * (x1 - x3) + (x3 - x2) * (y1 - y3)
        if abs(denom) < 1e-10:  # 三角形が退化している場合
            return False
        
        a = ((y2 - y3) * (px - x3) + (x3 - x2) * (py - y3)) / denom
        b = ((y3 - y1) * (px - x3) + (x1 - x3) * (py - y3)) / denom
        c = 1 - a - b
        
        return 0 <= a <= 1 and 0 <= b <= 1 and 0 <= c <= 1
    
    def _get_tile_screen_center(self, grid_x: int, grid_y: int, tile, camera_state, 
                               win_width: int, win_height: int) -> Tuple[float, float]:
        """
        タイルのスクリーン座標中心を取得
        
        Args:
            grid_x, grid_y: グリッド座標
            tile: タイルオブジェクト
            camera_state: カメラ状態
            win_width, win_height: ウィンドウサイズ
            
        Returns:
            スクリーン座標の中心
        """
        screen_coords = self.isometric_renderer.grid_to_iso(
            grid_x, grid_y, tile.height, camera_state
        )
        
        if screen_coords is None:
            return (0, 0)
        
        iso_x, iso_y = screen_coords
        scaled_cell_size = int(self.cell_size * camera_state.zoom)
        
        # ひし形の中心
        center_x = iso_x + scaled_cell_size // 2
        center_y = iso_y + scaled_cell_size // 4
        
        return (center_x, center_y)
    
    def _cache_result(self, cache_key: Tuple[int, int], result: Optional[HitResult]):
        """結果をキャッシュに保存"""
        if len(self.result_cache) >= self.cache_max_size:
            # 最古のエントリを削除（簡易LRU）
            oldest_key = next(iter(self.result_cache))
            del self.result_cache[oldest_key]
        
        self.result_cache[cache_key] = result
    
    def clear_cache(self):
        """キャッシュをクリア"""
        self.result_cache.clear()
        self.hit_tests = 0
        self.successful_hits = 0
        self.cache_hits = 0
        self.cache_misses = 0
    
    def get_hit_stats(self) -> Dict[str, Any]:
        """ヒット検出統計を取得"""
        total_cache_requests = self.cache_hits + self.cache_misses
        cache_ratio = self.cache_hits / total_cache_requests * 100 if total_cache_requests > 0 else 0
        hit_ratio = self.successful_hits / self.hit_tests * 100 if self.hit_tests > 0 else 0
        
        return {
            'hit_tests': self.hit_tests,
            'successful_hits': self.successful_hits,
            'hit_ratio': hit_ratio,
            'cache_hits': self.cache_hits,
            'cache_misses': self.cache_misses,
            'cache_ratio': cache_ratio,
            'cache_size': len(self.result_cache)
        }

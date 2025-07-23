import pyxel
import math
import random
from dataclasses import dataclass

# タイルデータ構造
@dataclass
class Tile:
    """マップタイルの情報を格納するデータクラス"""
    floor_id: str      # マップタイルのID（xxx_yyy形式）
    height: int        # 地形高さ
    attribute: int     # 地形属性
    color: int         # 地形色（Pyxelカラーコード）

class MapGrid:
    """256x256のマップタイル配列を管理するクラス"""
    
    def __init__(self, map_size=256):
        self.map_size = map_size
        self.tiles = []
        self.generate_random_map()
    
    def generate_random_map(self):
        """ランダムなマップデータを生成する"""
        print(f"256x256マップを生成中...")
        
        # 地形属性の定義
        terrain_types = [
            {"attribute": 1, "color": 11, "name": "草地"},      # 明緑
            {"attribute": 2, "color": 3, "name": "森"},         # 暗緑
            {"attribute": 3, "color": 12, "name": "砂漠"},      # 黄色
            {"attribute": 4, "color": 1, "name": "海"},         # 青
            {"attribute": 5, "color": 8, "name": "山"},         # 赤
        ]
        
        for y in range(self.map_size):
            row = []
            for x in range(self.map_size):
                # floor_idを座標ベースで生成（xxx_yyy形式）
                floor_id = f"{x:03d}_{y:03d}"
                
                # ランダムな高さ（1-15の範囲）
                height = random.randint(1, 15)
                
                # ランダムな地形タイプを選択
                terrain = random.choice(terrain_types)
                attribute = terrain["attribute"]
                color = terrain["color"]
                
                tile = Tile(
                    floor_id=floor_id,
                    height=height,
                    attribute=attribute,
                    color=color
                )
                row.append(tile)
            self.tiles.append(row)
        
        print(f"256x256マップ生成完了！")
    
    def get_tile(self, x, y):
        """指定座標のタイルを取得（範囲外チェック付き）"""
        if 0 <= x < self.map_size and 0 <= y < self.map_size:
            return self.tiles[y][x]
        return None
    
    def get_viewport_tiles(self, start_x, start_y, viewport_size=16):
        """指定座標から16x16のビューポート範囲のタイルを取得"""
        viewport = []
        for y in range(viewport_size):
            row = []
            for x in range(viewport_size):
                map_x = start_x + x
                map_y = start_y + y
                tile = self.get_tile(map_x, map_y)
                if tile is None:
                    # 範囲外の場合はダミータイルを作成
                    tile = Tile(
                        floor_id=f"{map_x:03d}_{map_y:03d}",
                        height=1,
                        attribute=0,
                        color=0  # 黒
                    )
                row.append(tile)
            viewport.append(row)
        return viewport

# 定数設定
WIN_WIDTH = 256
WIN_HEIGHT = 256
VIEWPORT_SIZE = 16  # 16x16ビューポート
CELL_SIZE = 16  # タイルサイズを小さく（16x16表示のため）
HEIGHT_UNIT = 2  # 高さ単位を小さく（密集表示のため）

# 色定数
COLOR_OUTLINE = 7
COLOR_TOP = 11
COLOR_LEFT = 6   # 左側面（ライトグレー）
COLOR_RIGHT = 5  # 右側面（ダークグレー）

class App:
    def __init__(self):
        # カメラパラメータ
        self.iso_x_offset = 0
        self.iso_y_offset = 0
        self.zoom = 1.0
        
        # ビューポート位置（256x256マップ内の表示開始位置）
        self.viewport_x = 120  # マップ中央付近から開始
        self.viewport_y = 120  # マップ中央付近から開始
        self.viewport_size = VIEWPORT_SIZE  # 16x16を表示
        
        # 回転システム
        self.rotation_step = 15  # 15度刻み
        self.rotation_index = 0  # 現在の回転ステップ番号
        self.max_rotations = 360 // self.rotation_step  # 24方向
        
        # 256x256のマップグリッドを生成
        print("MapGridを初期化中...")
        self.map_grid = MapGrid(256)
        
        # 現在のビューポートタイルを取得
        self.update_viewport_tiles()
        
        pyxel.init(WIN_WIDTH, WIN_HEIGHT, title="Grid Maddness")
        pyxel.run(self.update, self.draw)
    
    def update_viewport_tiles(self):
        """現在のビューポート位置から16x16タイルを取得"""
        self.current_tiles = self.map_grid.get_viewport_tiles(
            self.viewport_x, self.viewport_y, self.viewport_size
        )
    
    @property
    def current_angle(self):
        """現在の回転角度(度)を返す"""
        return self.rotation_index * self.rotation_step
    
    def get_rotated_coordinates(self, grid_x, grid_y):
        """現在の回転角度を用いてグリッド座標を回転させる"""
        angle_rad = math.radians(self.current_angle)
        
        # グリッド中心からの相対座標
        center = self.viewport_size // 2
        rel_x = grid_x - center
        rel_y = grid_y - center
        
        # 回転変換
        rotated_x = rel_x * math.cos(angle_rad) - rel_y * math.sin(angle_rad)
        rotated_y = rel_x * math.sin(angle_rad) + rel_y * math.cos(angle_rad)
        
        return rotated_x, rotated_y

    def update(self):
        if pyxel.btnp(pyxel.KEY_ESCAPE):
            pyxel.quit()
        
        # WASD移動でビューポートを移動（256x256マップ内）
        viewport_moved = False
        
        if pyxel.btnp(pyxel.KEY_W):  # 上移動
            if self.viewport_y > 0:
                self.viewport_y -= 1
                viewport_moved = True
        if pyxel.btnp(pyxel.KEY_S):  # 下移動
            if self.viewport_y < 256 - self.viewport_size:
                self.viewport_y += 1
                viewport_moved = True
        if pyxel.btnp(pyxel.KEY_A):  # 左移動
            if self.viewport_x > 0:
                self.viewport_x -= 1
                viewport_moved = True
        if pyxel.btnp(pyxel.KEY_D):  # 右移動
            if self.viewport_x < 256 - self.viewport_size:
                self.viewport_x += 1
                viewport_moved = True
        
        # ビューポートが移動した場合、表示タイルを更新
        if viewport_moved:
            self.update_viewport_tiles()
        
        # 回転処理（Q/Eキー）
        if pyxel.btnp(pyxel.KEY_Q):  # 反時計回り
            self.rotation_index = (self.rotation_index - 1) % self.max_rotations
        if pyxel.btnp(pyxel.KEY_E):  # 時計回り（Wの代わりにE）
            self.rotation_index = (self.rotation_index + 1) % self.max_rotations
        
        # ズーム機能（Z/Xキー）
        if pyxel.btn(pyxel.KEY_Z):
            self.zoom += 0.05  # 少しずつズーム
            if self.zoom > 3.0:  # 最大3倍まで
                self.zoom = 3.0
        if pyxel.btn(pyxel.KEY_X):
            self.zoom -= 0.05  # 少しずつズームアウト
            if self.zoom < 0.3:  # 最小0.3倍まで
                self.zoom = 0.3
        
        # 矢印キーでカメラ移動（表示位置の微調整）
        if pyxel.btn(pyxel.KEY_LEFT):
            self.iso_x_offset -= 2
        if pyxel.btn(pyxel.KEY_RIGHT):
            self.iso_x_offset += 2
        if pyxel.btn(pyxel.KEY_UP):
            self.iso_y_offset -= 2
        if pyxel.btn(pyxel.KEY_DOWN):
            self.iso_y_offset += 2

    def rect_poly(self, p0, p1, p2, p3, color):
        """4頂点の平行四辺形を2つの三角形で塗りつぶす"""
        pyxel.tri(p0[0], p0[1], p1[0], p1[1], p2[0], p2[1], color)
        pyxel.tri(p0[0], p0[1], p2[0], p2[1], p3[0], p3[1], color)

    def rect_polyb(self, p0, p1, p2, p3, color):
        """4頂点の平行四辺形に枠線を描画"""
        pyxel.line(p0[0], p0[1], p1[0], p1[1], color)
        pyxel.line(p1[0], p1[1], p2[0], p2[1], color)
        pyxel.line(p2[0], p2[1], p3[0], p3[1], color)
        pyxel.line(p3[0], p3[1], p0[0], p0[1], color)

    def draw_diamond_tile(self, grid_x, grid_y):
        """指定されたグリッド位置にダイアモンド型タイルを高さ付きで描画"""
        center_x = WIN_WIDTH // 2
        center_y = WIN_HEIGHT // 2
        
        # 現在のビューポートタイルから高さを取得
        tile = self.current_tiles[grid_y][grid_x]
        height = tile.height
        
        # 回転座標を取得
        rotated_x, rotated_y = self.get_rotated_coordinates(grid_x, grid_y)
        
        # 回転後のアイソメトリック座標計算
        base_iso_x = (rotated_x - rotated_y) * (CELL_SIZE // 2) + center_x + self.iso_x_offset
        base_iso_y = (rotated_x + rotated_y) * (CELL_SIZE // 4) + center_y + self.iso_y_offset - height * HEIGHT_UNIT
        
        # ズーム適用（ウィンドウ中心を基準）
        iso_x = center_x + (base_iso_x - center_x) * self.zoom
        iso_y = center_y + (base_iso_y - center_y) * self.zoom
        
        # 地面レベル座標もズーム適用（回転座標使用）
        base_ground_y = (rotated_x + rotated_y) * (CELL_SIZE // 4) + center_y + self.iso_y_offset
        ground_y = center_y + (base_ground_y - center_y) * self.zoom
        
        # ズーム適用されたセルサイズと高さ単位
        scaled_cell_size = int(CELL_SIZE * self.zoom)
        scaled_height_unit = int(HEIGHT_UNIT * self.zoom)
        
        # ダイアモンド（ひし形）上面の4頂点を計算
        FT = (iso_x + scaled_cell_size // 2, iso_y)                           # 上
        FL = (iso_x, iso_y + scaled_cell_size // 4)                          # 左
        FR = (iso_x + scaled_cell_size, iso_y + scaled_cell_size // 4)       # 右
        FB = (iso_x + scaled_cell_size // 2, iso_y + scaled_cell_size // 2)  # 下
        
        # 壁面（側面）の下側座標を地面レベル基準で計算
        BL = (FL[0], ground_y + scaled_cell_size // 4)   # 左側面の下
        BR = (FR[0], ground_y + scaled_cell_size // 4)   # 右側面の下
        BB = (FB[0], ground_y + scaled_cell_size // 2)   # 下側面の下
        
        # 左側面を描画（ライトグレー）
        # FL(左上) -> FB(下上) -> BB(下下) -> BL(左下) の順で平行四辺形
        self.rect_poly(FL, FB, BB, BL, COLOR_LEFT)
        
        # 右側面を描画（ダークグレー）
        # FB(下上) -> FR(右上) -> BR(右下) -> BB(下下) の順で平行四辺形
        self.rect_poly(FB, FR, BR, BB, COLOR_RIGHT)
        
        # 上面（ひし形）を描画（タイルの色を使用）
        self.rect_poly(FL, FT, FR, FB, tile.color)
        
        # 上面の枠線を描画
        self.rect_polyb(FT, FL, FB, FR, COLOR_OUTLINE)

    def draw(self):
        pyxel.cls(0)
        
        # 16x16ビューポートのダイアモンドタイルを描画
        for y in range(self.viewport_size):
            for x in range(self.viewport_size):
                self.draw_diamond_tile(x, y)
        
        # ビューポート情報とタイル色表示を追加
        tile_center = self.current_tiles[8][8]  # 中央タイル
        pyxel.rect(220, 5, 30, 30, tile_center.color)  # タイル色サンプル
        
        # 操作説明
        pyxel.text(5, 5, "WASD: Move viewport", 7)
        pyxel.text(5, 13, "Arrow: Move camera", 7)
        pyxel.text(5, 21, "Q/E: Rotate view", 7)
        pyxel.text(5, 29, "Z/X: Zoom in/out", 7)
        pyxel.text(5, 37, "ESC: Quit", 7)
        
        # ステータス表示
        pyxel.text(5, 215, f"Rotation:{self.current_angle}deg", 7)
        pyxel.text(5, 225, f"Zoom:{self.zoom:.1f}x", 7)
        pyxel.text(5, 235, f"Pos:({self.viewport_x},{self.viewport_y})", 7)
        pyxel.text(5, 245, f"Tile:{tile_center.floor_id}", 7)

App()
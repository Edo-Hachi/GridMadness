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

    def update(self):
        if pyxel.btnp(pyxel.KEY_Q):
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
        
        # 地面レベル（基準面）の座標計算
        # 横方向の間隔: CELL_SIZE//2 (15px間隔でタイルを配置)
        # 縦方向の間隔: CELL_SIZE//4 (7.5px間隔でタイルを配置)
        iso_x = (grid_x - grid_y) * (CELL_SIZE // 2) + center_x + self.iso_x_offset
        base_iso_y = (grid_x + grid_y) * (CELL_SIZE // 4) + center_y + self.iso_y_offset
        
        # 上面の座標計算（地面レベルから高さ分だけ上に）
        iso_y = base_iso_y - height * HEIGHT_UNIT
        
        # ダイアモンド（ひし形）上面の4頂点を計算
        # CELL_SIZE=30の場合の座標オフセット:
        # 上: 中心から右に15px, 下: 中心から右に15px・下に15px
        # 左: 中心から下に7.5px, 右: 中心から右に30px・下に7.5px
        FT = (iso_x + CELL_SIZE // 2, iso_y)                    # 上: +15px, +0px
        FL = (iso_x, iso_y + CELL_SIZE // 4)                    # 左: +0px, +7.5px
        FR = (iso_x + CELL_SIZE, iso_y + CELL_SIZE // 4)        # 右: +30px, +7.5px
        FB = (iso_x + CELL_SIZE // 2, iso_y + CELL_SIZE // 2)   # 下: +15px, +15px
        
        # 壁面（側面）の下側座標を地面レベル基準で計算
        # 全タイルの底面が同じ地面レベルに揃うように統一
        BL = (FL[0], base_iso_y + CELL_SIZE // 4)   # 左側面の下（地面レベル基準）
        BR = (FR[0], base_iso_y + CELL_SIZE // 4)   # 右側面の下（地面レベル基準）
        BB = (FB[0], base_iso_y + CELL_SIZE // 2)   # 下側面の下（地面レベル基準）
        
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
        pyxel.text(5, 21, "Q: Quit", 7)
        pyxel.text(5, 235, f"Pos:({self.viewport_x},{self.viewport_y})", 7)
        pyxel.text(5, 245, f"Tile:{tile_center.floor_id}", 7)

App()
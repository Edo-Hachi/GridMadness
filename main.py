import pyxel
import math
import random
import json
from dataclasses import dataclass, asdict

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
        # 初期化時のランダム生成をコメントアウト（F2で読み込み、または手動生成）
        # self.generate_random_map()
        self.create_empty_map()
    
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
    
    def create_empty_map(self):
        """空のマップ（全て基本地形）を生成する"""
        print(f"空の{self.map_size}x{self.map_size}マップを初期化中...")
        
        for y in range(self.map_size):
            row = []
            for x in range(self.map_size):
                # floor_idを座標ベースで生成（xxx_yyy形式）
                floor_id = f"{x:03d}_{y:03d}"
                
                # 基本設定（平坦な草地）
                height = 1          # 最低高さ
                attribute = 1       # 草地属性
                color = 11          # 明緑色
                
                tile = Tile(
                    floor_id=floor_id,
                    height=height,
                    attribute=attribute,
                    color=color
                )
                row.append(tile)
            self.tiles.append(row)
        
        print(f"空のマップ初期化完了！")
    
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
    
    def save_to_json(self, filename="map_data.json"):
        """マップデータをJSONファイルに保存"""
        print(f"マップデータを{filename}に保存中...")
        
        # タイルデータを辞書形式に変換
        map_data = {
            "map_size": self.map_size,
            "tiles": []
        }
        
        for y in range(self.map_size):
            row = []
            for x in range(self.map_size):
                tile = self.tiles[y][x]
                tile_dict = asdict(tile)
                row.append(tile_dict)
            map_data["tiles"].append(row)
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(map_data, f, ensure_ascii=False, indent=2)
            print(f"保存完了: {filename}")
            return True
        except Exception as e:
            print(f"保存エラー: {e}")
            return False
    
    def load_from_json(self, filename="map_data.json"):
        """JSONファイルからマップデータを読み込み"""
        print(f"{filename}からマップデータを読み込み中...")
        
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                map_data = json.load(f)
            
            # マップサイズの確認
            if map_data["map_size"] != self.map_size:
                print(f"警告: ファイルのマップサイズ({map_data['map_size']})が異なります")
                return False
            
            # タイルデータを復元
            new_tiles = []
            for y in range(self.map_size):
                row = []
                for x in range(self.map_size):
                    tile_dict = map_data["tiles"][y][x]
                    tile = Tile(
                        floor_id=tile_dict["floor_id"],
                        height=tile_dict["height"],
                        attribute=tile_dict["attribute"],
                        color=tile_dict["color"]
                    )
                    row.append(tile)
                new_tiles.append(row)
            
            # 既存のタイルデータを置き換え
            self.tiles = new_tiles
            print(f"読み込み完了: {filename}")
            return True
            
        except FileNotFoundError:
            print(f"ファイルが見つかりません: {filename}")
            return False
        except Exception as e:
            print(f"読み込みエラー: {e}")
            return False

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
        
        # 初期値の保存（Aキーでリセットするため）
        self.initial_viewport_x = self.viewport_x
        self.initial_viewport_y = self.viewport_y
        self.initial_iso_x_offset = self.iso_x_offset
        self.initial_iso_y_offset = self.iso_y_offset
        self.initial_zoom = self.zoom
        self.initial_rotation_index = self.rotation_index
        
        # マウス座標や選択状態
        self.mouse_x = 0
        self.mouse_y = 0
        self.hovered_tile = None  # マウスオーバー中のタイル
        self.selected_tile = None  # 選択されたタイル
        
        # JSON操作のフィードバック
        self.last_save_load_message = ""
        self.message_timer = 0
        
        # 256x256のマップグリッドを生成
        print("MapGridを初期化中...")
        self.map_grid = MapGrid(256)
        
        # 現在のビューポートタイルを取得
        self.update_viewport_tiles()
        
        pyxel.init(WIN_WIDTH, WIN_HEIGHT, title="Grid Maddness")
        pyxel.mouse(True)  # マウスカーソルを表示
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
    
    def get_tile_depth(self, grid_x, grid_y):
        """Z-ソート用にタイルの描画順を決めるための深度値を計算する"""
        rotated_x, rotated_y = self.get_rotated_coordinates(grid_x, grid_y)
        tile = self.current_tiles[grid_y][grid_x]
        
        # 深度 = 回転後のY座標 + 高さ（後ろにあるものほど先に描画）
        depth = rotated_y - tile.height * 0.1
        return depth
    
    def is_point_in_center_rect(self, point_x, point_y, diamond_center_x, diamond_center_y, diamond_width, diamond_height):
        """中央の矩形を用いたシンプルな当たり判定を行う"""
        # 矩形のサイズ（ひし形の幅・高さの50%を中央に）
        rect_width = diamond_width * 0.5
        rect_height = diamond_height * 0.5
        left = diamond_center_x - rect_width / 2
        right = diamond_center_x + rect_width / 2
        top = diamond_center_y - rect_height / 2
        bottom = diamond_center_y + rect_height / 2
        return left <= point_x <= right and top <= point_y <= bottom
    
    def get_tile_at_mouse(self):
        """マウスカーソル下にあるタイルを返す"""
        center_x = WIN_WIDTH // 2
        center_y = WIN_HEIGHT // 2

        # 全タイルを走査してマウス座標との当たりを検出
        for y in range(self.viewport_size):
            for x in range(self.viewport_size):
                tile = self.current_tiles[y][x]
                height = tile.height
                
                # 回転座標を取得
                rotated_x, rotated_y = self.get_rotated_coordinates(x, y)
                
                # draw_diamond_tileと同じ座標計算を使用
                base_iso_x = (rotated_x - rotated_y) * (CELL_SIZE // 2) + center_x + self.iso_x_offset
                base_iso_y = (rotated_x + rotated_y) * (CELL_SIZE // 4) + center_y + self.iso_y_offset - height * HEIGHT_UNIT
                
                # ズーム適用（ウィンドウ中心を基準）
                iso_x = center_x + (base_iso_x - center_x) * self.zoom
                iso_y = center_y + (base_iso_y - center_y) * self.zoom
                
                # ズーム適用されたセルサイズ
                scaled_cell_size = int(CELL_SIZE * self.zoom)
                
                # ダイアモンド（ひし形）上面の4頂点を計算（draw_diamond_tileと同じ）
                FT = (iso_x + scaled_cell_size // 2, iso_y)                           # 上
                FL = (iso_x, iso_y + scaled_cell_size // 4)                          # 左
                FR = (iso_x + scaled_cell_size, iso_y + scaled_cell_size // 4)       # 右
                FB = (iso_x + scaled_cell_size // 2, iso_y + scaled_cell_size // 2)  # 下
                
                # ひし形の中心座標を正確に計算
                diamond_center_x = (FL[0] + FR[0]) / 2  # 左右の中点
                diamond_center_y = (FT[1] + FB[1]) / 2  # 上下の中点
                
                # ひし形のサイズ
                diamond_width = scaled_cell_size
                diamond_height = scaled_cell_size // 2
                
                # 中心矩形で当たり判定
                if self.is_point_in_center_rect(self.mouse_x, self.mouse_y, 
                                               diamond_center_x, diamond_center_y, 
                                               diamond_width, diamond_height):
                    return (x, y)
        
        return None

    def update(self):
        if pyxel.btnp(pyxel.KEY_ESCAPE):
            pyxel.quit()
        
        # 現在のマウス座標を取得
        self.mouse_x = pyxel.mouse_x
        self.mouse_y = pyxel.mouse_y
        
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
        
        # マウスホイールズーム
        wheel_y = pyxel.mouse_wheel
        if wheel_y > 0:  # ホイール前方向（上）= ズームイン
            self.zoom += 0.1
            if self.zoom > 3.0:
                self.zoom = 3.0
        elif wheel_y < 0:  # ホイール後方向（下）= ズームアウト
            self.zoom -= 0.1
            if self.zoom < 0.3:
                self.zoom = 0.3
        
        # リセット処理（Cキー）
        if pyxel.btnp(pyxel.KEY_C):
            # ビューポートを中央に戻す
            self.viewport_x = self.initial_viewport_x
            self.viewport_y = self.initial_viewport_y
            # カメラオフセットをリセット
            self.iso_x_offset = self.initial_iso_x_offset
            self.iso_y_offset = self.initial_iso_y_offset
            # ズームをリセット
            self.zoom = self.initial_zoom
            # 回転をリセット
            self.rotation_index = self.initial_rotation_index
            # ビューポートタイルを更新
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
        
        # マウスクリックでタイル選択
        if pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT):
            if self.hovered_tile:
                self.selected_tile = self.hovered_tile
        
        # JSON保存/読み込み機能
        if pyxel.btnp(pyxel.KEY_F1):  # F1キーで保存
            if self.map_grid.save_to_json():
                self.last_save_load_message = "Map Saved!"
                self.message_timer = 120  # 2秒間表示（60FPS想定）
        
        if pyxel.btnp(pyxel.KEY_F2):  # F2キーで読み込み
            if self.map_grid.load_from_json():
                # 読み込み成功時、ビューポートを更新
                self.update_viewport_tiles()
                self.last_save_load_message = "Map Loaded!"
                self.message_timer = 120  # 2秒間表示
            else:
                self.last_save_load_message = "Load Failed!"
                self.message_timer = 120
        
        if pyxel.btnp(pyxel.KEY_F3):  # F3キーでランダムマップ生成
            self.map_grid.generate_random_map()
            self.update_viewport_tiles()
            self.last_save_load_message = "Random Map Generated!"
            self.message_timer = 120
        
        # メッセージタイマーを更新
        if self.message_timer > 0:
            self.message_timer -= 1

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
        
        # 色の決定（ホバー/選択状態を考慮）
        top_color = tile.color
        
        # マウスオーバーまたは選択状態の場合は色を変更
        is_hovered = self.hovered_tile == (grid_x, grid_y)
        is_selected = self.selected_tile == (grid_x, grid_y)
        
        if is_selected:
            top_color = 9  # 青色（選択状態）
        elif is_hovered:
            top_color = 10  # 緑色（ホバー状態）
        
        # 上面（ひし形）を描画
        self.rect_poly(FL, FT, FR, FB, top_color)
        
        # 上面の枠線を描画
        self.rect_polyb(FT, FL, FB, FR, COLOR_OUTLINE)

    def draw(self):
        pyxel.cls(0)
        
        # マウスオーバー中のタイルを更新
        self.hovered_tile = self.get_tile_at_mouse()
        
        # Z-ソート: 深度順にタイルを並べる
        # 各タイルの描画深度を求め配列に格納
        tiles_with_depth = []
        for y in range(self.viewport_size):
            for x in range(self.viewport_size):
                depth = self.get_tile_depth(x, y)
                tiles_with_depth.append((depth, x, y))
        
        # 深度順にソート（小さい値から大きい値へ = 奥から手前へ）
        tiles_with_depth.sort(key=lambda item: item[0])
        
        # ソート済みの順序で描画（奥から手前の順にタイルを描画）
        for depth, x, y in tiles_with_depth:
            self.draw_diamond_tile(x, y)
        
        # ビューポート情報とタイル色表示を追加
        tile_center = self.current_tiles[8][8]  # 中央タイル
        pyxel.rect(220, 5, 30, 30, tile_center.color)  # タイル色サンプル
        
        # 操作説明
        pyxel.text(5, 5, "WASD: Move viewport", 7)
        pyxel.text(5, 13, "Arrow: Move camera", 7)
        pyxel.text(5, 21, "Q/E: Rotate view", 7)
        pyxel.text(5, 29, "Z/X/Wheel: Zoom", 7)
        pyxel.text(5, 37, "Mouse: Hover/Click", 7)
        pyxel.text(5, 45, "F1: Save / F2: Load", 7)
        pyxel.text(5, 53, "F3: Random Map", 7)
        pyxel.text(5, 61, "C: Reset view", 7)
        pyxel.text(5, 69, "ESC: Quit", 7)
        
        # ステータス表示
        pyxel.text(5, 195, f"Rotation:{self.current_angle}deg", 7)
        pyxel.text(5, 205, f"Zoom:{self.zoom:.1f}x", 7)
        pyxel.text(5, 215, f"Pos:({self.viewport_x},{self.viewport_y})", 7)
        pyxel.text(5, 225, f"Tile:{tile_center.floor_id}", 7)
        
        # ホバー/選択タイル情報を表示
        if self.hovered_tile:
            x, y = self.hovered_tile
            tile = self.current_tiles[y][x]
            pyxel.text(5, 235, f"Hover:({x},{y}) H:{tile.height}", 7)
        
        if self.selected_tile:
            x, y = self.selected_tile
            tile = self.current_tiles[y][x]
            pyxel.text(5, 245, f"Select:({x},{y}) {tile.floor_id}", 9)
        
        # リセット可能であることを示すヒント
        if self.viewport_x != self.initial_viewport_x or \
           self.viewport_y != self.initial_viewport_y or \
           self.iso_x_offset != self.initial_iso_x_offset or \
           self.iso_y_offset != self.initial_iso_y_offset or \
           self.zoom != self.initial_zoom or \
           self.rotation_index != self.initial_rotation_index:
            # 選択タイルがない場合のみリセットヒントを表示
            if not self.selected_tile:
                pyxel.text(5, 245, "Press C to reset!", 8)  # オレンジ色で目立つように
        
        # JSON操作のフィードバックメッセージ表示
        if self.message_timer > 0:
            # 画面中央にメッセージを表示
            message_x = WIN_WIDTH // 2 - len(self.last_save_load_message) * 2
            message_y = WIN_HEIGHT // 2 - 10
            pyxel.rect(message_x - 4, message_y - 2, len(self.last_save_load_message) * 4 + 8, 12, 0)  # 背景
            pyxel.rectb(message_x - 4, message_y - 2, len(self.last_save_load_message) * 4 + 8, 12, 7)  # 枠
            pyxel.text(message_x, message_y, self.last_save_load_message, 10)  # 緑色で表示

App()
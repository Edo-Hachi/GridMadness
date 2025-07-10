"""Pyxel を用いたアイソメトリックグリッド描画アプリケーション."""

import pyxel
import random
import math
from FieldGrid import FieldGrid

# 色定数
COLOR_OUTLINE = 7
COLOR_TOP = 11
COLOR_LEFT = 12
COLOR_RIGHT = 5
COLOR_HEIGHT_LINE = 8
COLOR_HOVER = 10  # マウスオーバー時の色（緑）
COLOR_SELECTED = 9  # 選択時の色（青）

WIN_WIDTH = 256
WIN_HEIGHT = 256
GRID_SIZE = 10  # グリッドの数（10x10）
CELL_SIZE = WIN_WIDTH // GRID_SIZE  # 各セルのピクセルサイズ
HEIGHT_UNIT = 1  # 1段あたりの高さ（ピクセル）

class App:
    """ゲーム全体を管理するアプリケーションクラス."""

    def __init__(self):
        """pyxel 初期化とゲーム状態のセットアップ."""
        # フレームカウンタ（タイルの高さ更新に利用）
        self.frame_count = 0
        
        # -------------------------
        # カメラパラメータ
        # -------------------------
        # 等角投影座標に加算するスクロール用オフセット
        self.iso_x_offset = -6
        self.iso_y_offset = 16
        
        # ズーム倍率（1.0 が等倍）
        self.zoom = 1.0
        
        # -------------------------
        # 回転システム
        # -------------------------
        # 1ステップあたりの回転角度
        self.rotation_step = 15
        # 現在の回転ステップ番号
        self.rotation_index = 0
        # 0〜self.max_rotations-1 までの値を取る
        self.max_rotations = 360 // self.rotation_step
        
        # -------------------------
        # 初期値の保存（Aキーでリセットするため）
        # -------------------------
        self.initial_iso_x_offset = self.iso_x_offset
        self.initial_iso_y_offset = self.iso_y_offset
        self.initial_zoom = self.zoom
        self.initial_rotation_index = self.rotation_index

        # マウス座標や選択状態
        self.mouse_x = 0
        self.mouse_y = 0
        self.hovered_tile = None  # マウスオーバー中のタイル
        self.selected_tile = None  # 選択されたタイル


        # -------------------------
        # グリッド生成
        # -------------------------
        # FieldGrid がランダムにタイルを生成する
        self.fieldgrid = FieldGrid(GRID_SIZE, CELL_SIZE, CELL_SIZE, self.iso_x_offset, self.iso_y_offset)

        # Pyxel 初期化およびゲームループ開始
        pyxel.init(WIN_WIDTH, WIN_HEIGHT, title="Grid Madness")
        pyxel.load("my_resource.pyxres")
        pyxel.mouse(True)  # マウスカーソルを表示
        pyxel.run(self.update, self.draw)
    

    def update(self):
        """ユーザー入力の処理とゲーム状態の更新を行う."""

        # 現在のマウス座標を取得
        self.mouse_x = pyxel.mouse_x
        self.mouse_y = pyxel.mouse_y
        
        # Esc Key Down
        if pyxel.btn(pyxel.KEY_ESCAPE):
            pyxel.quit()
            
        # スクロール処理
        if pyxel.btn(pyxel.KEY_LEFT):
            self.iso_x_offset -= 2
        if pyxel.btn(pyxel.KEY_RIGHT):
            self.iso_x_offset += 2
        if pyxel.btn(pyxel.KEY_UP):
            self.iso_y_offset -= 2
        if pyxel.btn(pyxel.KEY_DOWN):
            self.iso_y_offset += 2
            
        # ズーム処理
        if pyxel.btn(pyxel.KEY_Z):
            self.zoom += 0.1
            if self.zoom > 3.0:  # 最大3倍まで
                self.zoom = 3.0
        if pyxel.btn(pyxel.KEY_X):
            self.zoom -= 0.1
            if self.zoom < 0.3:  # 最小0.3倍まで
                self.zoom = 0.3
                
        # 回転処理
        if pyxel.btnp(pyxel.KEY_Q):  # btnp = 押した瞬間のみ
            self.rotation_index = (self.rotation_index - 1) % self.max_rotations
        if pyxel.btnp(pyxel.KEY_W):
            self.rotation_index = (self.rotation_index + 1) % self.max_rotations
                
        # リセット処理
        if pyxel.btn(pyxel.KEY_A):
            self.iso_x_offset = self.initial_iso_x_offset
            self.iso_y_offset = self.initial_iso_y_offset
            self.zoom = self.initial_zoom
            self.rotation_index = self.initial_rotation_index
            
        # マウスクリックでタイル選択
        if pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT):
            if self.hovered_tile:
                self.selected_tile = self.hovered_tile
        
        self.frame_count += 1
        if self.frame_count % 10 == 0:  # 10フレームごとに更新
            self.fieldgrid.update_heights()
    
    @property
    def current_angle(self):
        """現在の回転角度(度)を返す."""
        return self.rotation_index * self.rotation_step
    
    def get_rotated_coordinates(self, grid_x, grid_y):
        """現在の回転角度を用いてグリッド座標を回転させる."""
        angle_rad = math.radians(self.current_angle)
        
        # グリッド中心からの相対座標
        center = GRID_SIZE // 2
        rel_x = grid_x - center
        rel_y = grid_y - center
        
        # 回転変換
        rotated_x = rel_x * math.cos(angle_rad) - rel_y * math.sin(angle_rad)
        rotated_y = rel_x * math.sin(angle_rad) + rel_y * math.cos(angle_rad)
        
        return rotated_x, rotated_y
    
    def get_tile_depth(self, grid_x, grid_y):
        """Zソート用にタイルの描画順を決めるための深度値を計算する."""
        rotated_x, rotated_y = self.get_rotated_coordinates(grid_x, grid_y)
        tile = self.fieldgrid[grid_y][grid_x]
        
        # 深度 = 回転後のY座標 + 高さ（後ろにあるものほど先に描画）
        depth = rotated_y - tile.height * 0.1
        return depth
    

    def is_point_in_center_rect(self, point_x, point_y, diamond_center_x, diamond_center_y, diamond_width, diamond_height):
        """中央の矩形を用いたシンプルな当たり判定を行う."""
        # 矩形のサイズ（ひし形の幅・高さの50%を中央に）
        rect_width = diamond_width * 0.5
        rect_height = diamond_height * 0.5
        left = diamond_center_x - rect_width / 2
        right = diamond_center_x + rect_width / 2
        top = diamond_center_y - rect_height / 2
        bottom = diamond_center_y + rect_height / 2
        return left <= point_x <= right and top <= point_y <= bottom

    def get_tile_at_mouse(self):
        """マウスカーソル下にあるタイルを返す."""
        center_x = WIN_WIDTH // 2
        center_y = WIN_HEIGHT // 2

        # 全タイルを走査してマウス座標との当たりを検出
        for y in range(GRID_SIZE):
            for x in range(GRID_SIZE):
                tile = self.fieldgrid[y][x]
                h = tile.height
                
                # 回転座標を取得
                rotated_x, rotated_y = self.get_rotated_coordinates(x, y)
                
                # 回転後のアイソメトリック座標
                base_iso_x = (rotated_x - rotated_y) * (CELL_SIZE // 2) + center_x + self.iso_x_offset
                base_iso_y = (rotated_x + rotated_y) * (CELL_SIZE // 4) + self.iso_y_offset - h * HEIGHT_UNIT
                
                # ズーム適用（ウィンドウ中心を基準）
                iso_x = center_x + (base_iso_x - center_x) * self.zoom
                iso_y = center_y + (base_iso_y - center_y) * self.zoom
                
                # ひし形の中心座標（ズーム適用後）
                diamond_center_x = iso_x + int(CELL_SIZE * self.zoom) // 2
                diamond_center_y = iso_y + int(CELL_SIZE * self.zoom) // 4
                
                # ひし形のサイズ
                diamond_width = int(CELL_SIZE * self.zoom)
                diamond_height = int(CELL_SIZE * self.zoom) // 2
                
                # 中心矩形で当たり判定
                if self.is_point_in_center_rect(self.mouse_x, self.mouse_y, 
                                               diamond_center_x, diamond_center_y, 
                                               diamond_width, diamond_height):
                    return (x, y)
        
        return None

    def draw_compass_labels(self):
        """グリッドの角に方角文字を表示（固定方角・オフセット付き）"""
        center_x = WIN_WIDTH // 2
        center_y = WIN_HEIGHT // 2
        
        # 4つの角の座標と、その位置に表示する固定の方角（EとWを入れ替え）
        compass_positions = [
            (0, 0, "N"),    # 北西の角に北（N）
            (0, 9, "W"),    # 北東の角に西（W）← 元はE
            (9, 0, "E"),    # 南西の角に東（E）← 元はW
            (9, 9, "S")     # 南東の角に南（S）
        ]
        
        for grid_x, grid_y, direction in compass_positions:
            # 回転座標を取得
            rotated_x, rotated_y = self.get_rotated_coordinates(grid_x, grid_y)
            
            # 回転後のアイソメトリック座標計算
            base_iso_x = (rotated_x - rotated_y) * (CELL_SIZE // 2) + center_x + self.iso_x_offset
            base_iso_y = (rotated_x + rotated_y) * (CELL_SIZE // 4) + self.iso_y_offset
            
            # ズーム適用
            iso_x = center_x + (base_iso_x - center_x) * self.zoom
            iso_y = center_y + (base_iso_y - center_y) * self.zoom
            
            # ひし形の各頂点を計算（タイル描画と同じ計算）
            scaled_cell_size = int(CELL_SIZE * self.zoom)
            
            # ひし形の中心座標を計算
            tile_center_x = iso_x + scaled_cell_size // 2
            tile_center_y = iso_y + scaled_cell_size // 4
            
            # 全ての方角文字をひし形の中心に表示（微調整のベース）
            text_x = tile_center_x
            text_y = tile_center_y
            
            # 固定オフセット表（4つの基本方向）
            up_offset = (5, -30)      # 上方向
            right_offset = (20, 5)    # 右方向  
            down_offset = (-5, 30)    # 下方向
            left_offset = (-20, -5)   # 左方向
            
            # 回転に応じてN/E/S/Wに方向を割り当て
            if 0 <= self.rotation_index <= 6:
                # 0-6: 基準（N=上, E=右, S=下, W=左）
                n_offset = up_offset
                e_offset = right_offset
                s_offset = down_offset
                w_offset = left_offset
                
            elif 7 <= self.rotation_index <= 12:
                # 7-12: 90度回転（N=右, E=下, S=左, W=上）
                n_offset = right_offset
                e_offset = down_offset
                s_offset = left_offset
                w_offset = up_offset
                
            elif 13 <= self.rotation_index <= 18:
                # 13-18: 180度回転（N=下, E=左, S=上, W=右）
                n_offset = down_offset
                e_offset = left_offset
                s_offset = up_offset
                w_offset = right_offset
                
            elif 19 <= self.rotation_index <= 23:
                # 19-23: 270度回転（N=左, E=上, S=右, W=下）
                n_offset = left_offset
                e_offset = up_offset
                s_offset = right_offset
                w_offset = down_offset
            
            # オフセットを適用
            n_text_x = tile_center_x + n_offset[0]
            n_text_y = tile_center_y + n_offset[1]
            e_text_x = tile_center_x + e_offset[0]
            e_text_y = tile_center_y + e_offset[1]
            s_text_x = tile_center_x + s_offset[0]
            s_text_y = tile_center_y + s_offset[1]
            w_text_x = tile_center_x + w_offset[0]
            w_text_y = tile_center_y + w_offset[1]

            # 各方角に応じた位置を適用
            if direction == "N":
                text_x = n_text_x
                text_y = n_text_y
            elif direction == "E":
                text_x = e_text_x
                text_y = e_text_y
            elif direction == "S":
                text_x = s_text_x
                text_y = s_text_y
            elif direction == "W":
                text_x = w_text_x
                text_y = w_text_y
            
            # デバッグ表示：N(0度)とW(90度)の座標比較（画面下）
            if direction == "N" and self.rotation_index == 0:
                debug_text = f"N0deg:({int(text_x)},{int(text_y)})"
                pyxel.text(0, 200, debug_text, 7)
            elif direction == "W" and self.rotation_index == 6:  # 90度は6インデックス
                debug_text = f"W90deg:({int(text_x)},{int(text_y)})"
                pyxel.text(0, 208, debug_text, 7)
            
            # 現在の回転インデックスも表示
            if direction == "N" and grid_x == 0 and grid_y == 0:  # 1回だけ表示
                pyxel.text(0, 216, f"RotIdx:{self.rotation_index}", 7)
                # タイル中心座標も表示
                pyxel.text(0, 224, f"Center:({int(tile_center_x)},{int(tile_center_y)})", 7)
                # 回転座標も表示
                rot_x, rot_y = self.get_rotated_coordinates(grid_x, grid_y)
                pyxel.text(0, 232, f"Rot:({rot_x:.1f},{rot_y:.1f})", 7)
            
            # 固定の方角文字と座標を描画（赤色）
            text_with_coords = f"{direction}({grid_x},{grid_y})"
            pyxel.text(int(text_x), int(text_y), text_with_coords, 8)

    def rect_poly(self, p0, p1, p2, p3, color):
        """4頂点の平行四辺形を 2 つの三角形で塗りつぶす."""
        pyxel.tri(p0[0], p0[1], p1[0], p1[1], p2[0], p2[1], color)
        pyxel.tri(p0[0], p0[1], p2[0], p2[1], p3[0], p3[1], color)

    def rect_polyb(self, p0, p1, p2, p3, color):
        """4頂点の平行四辺形に枠線を描画する."""
        pyxel.line(p0[0], p0[1], p1[0], p1[1], color)
        pyxel.line(p1[0], p1[1], p2[0], p2[1], color)
        pyxel.line(p2[0], p2[1], p3[0], p3[1], color)
        pyxel.line(p3[0], p3[1], p0[0], p0[1], color)

    def draw(self):
        """現在のゲーム状態を画面に描画する."""
        pyxel.cls(0)
        
        # マウスオーバー中のタイルを更新
        self.hovered_tile = self.get_tile_at_mouse()
        
        # ウィンドウ中心を基準にズーム計算
        center_x = WIN_WIDTH // 2
        center_y = WIN_HEIGHT // 2
        
        # Zソート: 深度順にタイルを並べる
        # 各タイルの描画深度を求め配列に格納
        tiles_with_depth = []
        for y in range(GRID_SIZE):
            for x in range(GRID_SIZE):
                depth = self.get_tile_depth(x, y)
                tiles_with_depth.append((depth, x, y))
        
        # 深度順にソート（小さい値から大きい値へ = 奥から手前へ）
        tiles_with_depth.sort(key=lambda item: item[0])
        
        # ソート済みの順序で描画
        # 奥から手前の順にタイルを描画
        for depth, x, y in tiles_with_depth:
            tile = self.fieldgrid[y][x]
            h = tile.height
            
            # 描画位置算出のためにグリッド座標を回転
            rotated_x, rotated_y = self.get_rotated_coordinates(x, y)
            
            # 回転後のアイソメトリック座標を求める
            base_iso_x = (rotated_x - rotated_y) * (CELL_SIZE // 2) + center_x + self.iso_x_offset
            base_iso_y = (rotated_x + rotated_y) * (CELL_SIZE // 4) + self.iso_y_offset - h * HEIGHT_UNIT
            
            # ウィンドウ中心を基準にズームを適用
            iso_x = center_x + (base_iso_x - center_x) * self.zoom
            iso_y = center_y + (base_iso_y - center_y) * self.zoom

            # タイル上面の4頂点（ズーム適用済み）
            scaled_cell_size = int(CELL_SIZE * self.zoom)
            FT = (iso_x + scaled_cell_size // 2, iso_y)                # 上
            FL = (iso_x, iso_y + scaled_cell_size // 4)                # 左
            FR = (iso_x + scaled_cell_size, iso_y + scaled_cell_size // 4)    # 右
            FB = (iso_x + scaled_cell_size // 2, iso_y + scaled_cell_size // 2)  # 下
            
            # 壁面の下側の座標（高さ分だけY方向にオフセット）
            scaled_height_unit = int(HEIGHT_UNIT * self.zoom)
            BL = (FL[0], FL[1] + h * scaled_height_unit)   # 左側壁面の下
            BTB = (FB[0], FB[1] + h * scaled_height_unit)  # 下側壁面の下
            BR = (FR[0], FR[1] + h * scaled_height_unit)   # 右側壁面の下

            # 色の決定
            top_color = COLOR_TOP
            left_color = COLOR_LEFT
            right_color = COLOR_RIGHT
            
            # マウスオーバーまたは選択状態の場合は上面の色のみ変更
            is_hovered = self.hovered_tile == (x, y)
            is_selected = self.selected_tile == (x, y)
            
            if is_selected:
                top_color = COLOR_SELECTED
            elif is_hovered:
                top_color = COLOR_HOVER

            # 左側面をrect_polyで描画
            self.rect_poly(FL, FB, BTB, BL, left_color)

            # 右側面をrect_polyで描画
            self.rect_poly(FB, FR, BR, BTB, right_color)                           

            #上を描画
            self.rect_poly(FL , FT, FR, FB, top_color)

            #Topのアウトラインを描画
            self.rect_polyb(FT, FL, FB, FR, COLOR_OUTLINE)

        # 方角表示を描画
        self.draw_compass_labels()
        
        # デバッグ情報表示
        pyxel.text(0, 0, f"Rotation: {self.current_angle}deg", 7)
        pyxel.text(0, 8, f"Index: {self.rotation_index}/{self.max_rotations-1}", 7)
        
        if self.hovered_tile:
            x, y = self.hovered_tile
            tile = self.fieldgrid[y][x]
            pyxel.text(0, 16, f"Hover: ({x}, {y})", 7)
            pyxel.text(0, 24, f"Height: {tile.height}", 7)
            pyxel.text(0, 32, f"Type: {tile.ground_type}", 7)
        
        if self.selected_tile:
            x, y = self.selected_tile
            pyxel.text(0, 40, f"Selected: ({x}, {y})", 9)

if __name__ == '__main__':
    App()

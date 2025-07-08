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
    def __init__(self):
        # 10x10の配列を作成し、各セルにランダムで1～3の高さを設定
        self.frame_count = 0
        
        # カメラ位置（スクロール用）
        self.iso_x_offset = -6  # X方向のオフセット
        self.iso_y_offset = 16   # Y方向のオフセット
        
        # ズーム機能
        self.zoom = 1.0  # ズーム倍率
        
        # 回転システム
        self.rotation_step = 15  # 回転ステップ角度（設定可能）
        self.rotation_index = 0  # 現在の回転インデックス
        self.max_rotations = 360 // self.rotation_step  # 24方向
        
        # 初期位置を記憶（リセット用）
        self.initial_iso_x_offset = self.iso_x_offset
        self.initial_iso_y_offset = self.iso_y_offset
        self.initial_zoom = self.zoom
        self.initial_rotation_index = self.rotation_index

        # マウス関連
        self.mouse_x = 0
        self.mouse_y = 0
        self.hovered_tile = None  # マウスオーバー中のタイル
        self.selected_tile = None  # 選択されたタイル


        # 高さや属性を持つグリッドを生成
        self.fieldgrid = FieldGrid(GRID_SIZE, CELL_SIZE, CELL_SIZE, self.iso_x_offset, self.iso_y_offset)        

        pyxel.init(WIN_WIDTH, WIN_HEIGHT, title="Grid Madness")
        pyxel.load("my_resource.pyxres")
        pyxel.mouse(True)  # マウスカーソルを表示
        pyxel.run(self.update, self.draw)
    

    def update(self):
        # マウス座標を取得
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
        """現在の回転角度を取得"""
        return self.rotation_index * self.rotation_step
    
    def get_rotated_coordinates(self, grid_x, grid_y):
        """グリッド座標を回転座標に変換"""
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
        """タイルの描画深度を計算（Zソート用）"""
        rotated_x, rotated_y = self.get_rotated_coordinates(grid_x, grid_y)
        tile = self.fieldgrid[grid_y][grid_x]
        
        # 深度 = 回転後のY座標 + 高さ（後ろにあるものほど先に描画）
        depth = rotated_y - tile.height * 0.1
        return depth
    

    def is_point_in_center_rect(self, point_x, point_y, diamond_center_x, diamond_center_y, diamond_width, diamond_height):
        """ひし形の中心にある矩形での当たり判定"""
        # 矩形のサイズ（ひし形の幅・高さの50%を中央に）
        rect_width = diamond_width * 0.5
        rect_height = diamond_height * 0.5
        left = diamond_center_x - rect_width / 2
        right = diamond_center_x + rect_width / 2
        top = diamond_center_y - rect_height / 2
        bottom = diamond_center_y + rect_height / 2
        return left <= point_x <= right and top <= point_y <= bottom

    def get_tile_at_mouse(self):
        """マウス位置のタイルを取得（回転対応コリジョン）"""
        center_x = WIN_WIDTH // 2
        center_y = WIN_HEIGHT // 2
        
        for y in range(GRID_SIZE):
            for x in range(GRID_SIZE):
                tile = self.fieldgrid[y][x]
                h = tile.height
                
                # 回転座標を取得
                rotated_x, rotated_y = self.get_rotated_coordinates(x, y)
                
                # 回転後のアイソメトリック座標計算
                base_iso_x = (rotated_x - rotated_y) * (CELL_SIZE // 2) + center_x + self.iso_x_offset
                base_iso_y = (rotated_x + rotated_y) * (CELL_SIZE // 4) + self.iso_y_offset - h * HEIGHT_UNIT
                
                # ズーム適用（ウィンドウ中心を基準）
                iso_x = center_x + (base_iso_x - center_x) * self.zoom
                iso_y = center_y + (base_iso_y - center_y) * self.zoom
                
                # ひし形の中心座標
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

    #4頂点（左, 上, 右, 下）で囲まれた平行四辺形を2つの三角形で塗りつぶす
    def rect_poly(self, p0, p1, p2, p3, color):
        pyxel.tri(p0[0], p0[1], p1[0], p1[1], p2[0], p2[1], color)
        pyxel.tri(p0[0], p0[1], p2[0], p2[1], p3[0], p3[1], color)

    #4頂点（左, 上, 右, 下）で囲まれた平行四辺形の枠線を描画
    def rect_polyb(self, p0, p1, p2, p3, color):
        pyxel.line(p0[0], p0[1], p1[0], p1[1], color)
        pyxel.line(p1[0], p1[1], p2[0], p2[1], color)
        pyxel.line(p2[0], p2[1], p3[0], p3[1], color)
        pyxel.line(p3[0], p3[1], p0[0], p0[1], color)

    def draw(self):
        pyxel.cls(0)
        
        # マウスオーバー中のタイルを更新
        self.hovered_tile = self.get_tile_at_mouse()
        
        # ウィンドウ中心を基準にズーム計算
        center_x = WIN_WIDTH // 2
        center_y = WIN_HEIGHT // 2
        
        # Zソート: 深度順にタイルを並べる
        tiles_with_depth = []
        for y in range(GRID_SIZE):
            for x in range(GRID_SIZE):
                depth = self.get_tile_depth(x, y)
                tiles_with_depth.append((depth, x, y))
        
        # 深度順にソート（小さい値から大きい値へ = 奥から手前へ）
        tiles_with_depth.sort(key=lambda item: item[0])
        
        # ソート済みの順序で描画
        for depth, x, y in tiles_with_depth:
            tile = self.fieldgrid[y][x]
            h = tile.height
            
            # 回転座標を取得
            rotated_x, rotated_y = self.get_rotated_coordinates(x, y)
            
            # 回転後のアイソメトリック座標計算
            base_iso_x = (rotated_x - rotated_y) * (CELL_SIZE // 2) + center_x + self.iso_x_offset
            base_iso_y = (rotated_x + rotated_y) * (CELL_SIZE // 4) + self.iso_y_offset - h * HEIGHT_UNIT
            
            # ズーム適用（ウィンドウ中心を基準）
            iso_x = center_x + (base_iso_x - center_x) * self.zoom
            iso_y = center_y + (base_iso_y - center_y) * self.zoom

            # 床ひし形の各頂点座標を直接代入（ズーム適用済み）
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

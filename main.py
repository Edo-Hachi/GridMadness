import pyxel
import random
from FieldGrid import FieldGrid

# 色定数
COLOR_OUTLINE = 7
COLOR_TOP = 11
COLOR_LEFT = 12
COLOR_RIGHT = 5
COLOR_HEIGHT_LINE = 8

WIN_WIDTH = 128
WIN_HEIGHT = 128
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
        
        # 初期位置を記憶（リセット用）
        self.initial_iso_x_offset = self.iso_x_offset
        self.initial_iso_y_offset = self.iso_y_offset
        self.initial_zoom = self.zoom

        # 高さや属性を持つグリッドを生成
        self.fieldgrid = FieldGrid(GRID_SIZE, CELL_SIZE, CELL_SIZE, self.iso_x_offset, self.iso_y_offset)        

        pyxel.init(WIN_WIDTH, WIN_HEIGHT, title="Grid Madness")
        pyxel.load("my_resource.pyxres")
        pyxel.run(self.update, self.draw)

    def update(self):
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
                
        # リセット処理
        if pyxel.btn(pyxel.KEY_A):
            self.iso_x_offset = self.initial_iso_x_offset
            self.iso_y_offset = self.initial_iso_y_offset
            self.zoom = self.initial_zoom
            
        self.frame_count += 1
        if self.frame_count % 10 == 0:  # 10フレームごとに更新
            self.fieldgrid.update_heights()
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
        
        # ウィンドウ中心を基準にズーム計算
        center_x = WIN_WIDTH // 2
        center_y = WIN_HEIGHT // 2
        
        for y in range(GRID_SIZE):
            for x in range(GRID_SIZE):
                #h = self.grid[y][x]  # 高さ情報
                tile = self.fieldgrid[y][x]
                h = tile.height
                
                # 基本座標計算
                base_iso_x = (x - y) * (CELL_SIZE // 2) + center_x + self.iso_x_offset
                base_iso_y = (x + y) * (CELL_SIZE // 4) + self.iso_y_offset - h * HEIGHT_UNIT
                
                # ズーム適用（ウィンドウ中心を基準）
                iso_x = center_x + (base_iso_x - center_x) * self.zoom
                iso_y = center_y + (base_iso_y - center_y) * self.zoom
                
                #iso_y = (x + y) * (CELL_SIZE // 4) + ISO_Y_OFFSET - HEIGHT_UNIT  # 高さ分だけ上にずらす
                # points = [
                #     (iso_x, iso_y + CELL_SIZE // 4),  # 左
                #     (iso_x + CELL_SIZE // 2, iso_y),  # 上
                #     (iso_x + CELL_SIZE, iso_y + CELL_SIZE // 4),  # 右
                #     (iso_x + CELL_SIZE // 2, iso_y + CELL_SIZE // 2)  # 下
                # ]

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

                # 左側面をrect_polyで描画
                self.rect_poly(FL, FB, BTB, BL, COLOR_LEFT)

                # 右側面をrect_polyで描画
                self.rect_poly(FB, FR, BR, BTB, COLOR_RIGHT)                           

                #上を描画
                self.rect_poly(FL , FT, FR, FB, COLOR_TOP)

                #Topのアウトラインを描画
                self.rect_polyb(FT, FL, FB, FR, COLOR_OUTLINE)


if __name__ == '__main__':
    App()

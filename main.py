import pyxel
import random

# 色定数
COLOR_OUTLINE = 7
COLOR_TOP = 11
COLOR_LEFT = 12
#COLOR_FLOOR_LEFT = 12
COLOR_RIGHT = 5
#COLOR_FLOOR_RIGHT = 5
COLOR_HEIGHT_LINE = 8

WIN_WIDTH = 128
WIN_HEIGHT = 128
GRID_SIZE = 10  # グリッドの数（10x10）
CELL_SIZE = WIN_WIDTH // GRID_SIZE  # 各セルのピクセルサイズ
HEIGHT_UNIT = 4  # 1段あたりの高さ（ピクセル）

ISO_X_OFFSET = -6  # X方向のオフセット
ISO_Y_OFFSET = 16   # Y方向のオフセット

class App:
    def __init__(self):
        # 10x10の配列を作成し、各セルにランダムで1～3の高さを設定
        self.frame_count = 0

        self.grid = [[random.randint(1, 4) for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]
        pyxel.init(WIN_WIDTH, WIN_HEIGHT, title="Grid Madness")
        pyxel.load("my_resource.pyxres")
        pyxel.run(self.update, self.draw)

    def update(self):
        # Esc Key Down
        if pyxel.btn(pyxel.KEY_ESCAPE):
            pyxel.quit()
        self.frame_count += 1
        if self.frame_count % 5 == 0:  # 10フレームごとに更新
            for y in range(GRID_SIZE):
                for x in range(GRID_SIZE):
                    self.grid[y][x] += 1
                    if self.grid[y][x] > 4:
                        self.grid[y][x] = 0

    def rect_poly(self, p0, p1, p2, p3, col):
        """
        4頂点（左, 上, 右, 下）で囲まれた平行四辺形を2つの三角形で塗りつぶす
        """
        pyxel.tri(p0[0], p0[1], p1[0], p1[1], p2[0], p2[1], col)
        pyxel.tri(p0[0], p0[1], p2[0], p2[1], p3[0], p3[1], col)

    def rect_polyb(self, p0, p1, p2, p3, col):
        """
        4頂点（左, 上, 右, 下）で囲まれた平行四辺形の枠線を描画
        """
        pyxel.line(p0[0], p0[1], p1[0], p1[1], col)
        pyxel.line(p1[0], p1[1], p2[0], p2[1], col)
        pyxel.line(p2[0], p2[1], p3[0], p3[1], col)
        pyxel.line(p3[0], p3[1], p0[0], p0[1], col)

    def draw(self):
        pyxel.cls(0)
        for y in range(GRID_SIZE):
            for x in range(GRID_SIZE):
                h = self.grid[y][x]  # 高さ情報
                iso_x = (x - y) * (CELL_SIZE // 2) + WIN_WIDTH // 2 + ISO_X_OFFSET
                iso_y = (x + y) * (CELL_SIZE // 4) + ISO_Y_OFFSET - h * HEIGHT_UNIT  # 高さ分だけ上にずらす
                points = [
                    (iso_x, iso_y + CELL_SIZE // 4),  # 左
                    (iso_x + CELL_SIZE // 2, iso_y),  # 上
                    (iso_x + CELL_SIZE, iso_y + CELL_SIZE // 4),  # 右
                    (iso_x + CELL_SIZE // 2, iso_y + CELL_SIZE // 2)  # 下
                ]

                # 床ひし形の各頂点座標を直接代入
                FT = (iso_x + CELL_SIZE // 2, iso_y)                # 上
                FL = (iso_x, iso_y + CELL_SIZE // 4)                # 左
                FR = (iso_x + CELL_SIZE, iso_y + CELL_SIZE // 4)    # 右
                FB = (iso_x + CELL_SIZE // 2, iso_y + CELL_SIZE // 2)  # 下
                # 壁面の下側の座標（高さ分だけY方向にオフセット）
                BL = (FL[0], FL[1] + h * HEIGHT_UNIT)   # 左側壁面の下
                BTB = (FB[0], FB[1] + h * HEIGHT_UNIT)  # 下側壁面の下
                BR = (FR[0], FR[1] + h * HEIGHT_UNIT)   # 右側壁面の下

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

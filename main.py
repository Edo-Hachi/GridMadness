import pyxel
import math

# 定数設定
WIN_WIDTH = 256
WIN_HEIGHT = 256
GRID_SIZE = 3  # 3x3グリッドから開始
CELL_SIZE = 30  # ひし形の横幅（左右の最大幅）をピクセル単位で指定
               # ひし形の縦幅は自動的にCELL_SIZE/2になる
               # CELL_SIZE=30の場合: 横幅30px、縦幅15px
HEIGHT_UNIT = 5  # 1段あたりの高さ（ピクセル）- 5px per level

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
        
        # 高さデータ（3x3グリッド用の簡単な高さマップ）
        # 各タイルの高さを1-3の範囲で設定
        self.tile_heights = [
            [1, 2, 1],  # 上段: 低-高-低
            [2, 3, 2],  # 中段: 高-最高-高
            [1, 2, 1]   # 下段: 低-高-低
        ]
        
        pyxel.init(WIN_WIDTH, WIN_HEIGHT, title="Grid Maddness")
        pyxel.run(self.update, self.draw)

    def update(self):
        if pyxel.btnp(pyxel.KEY_Q):
            pyxel.quit()
        
        # 簡単なカメラ移動
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
        
        # タイルの高さを取得
        height = self.tile_heights[grid_y][grid_x]
        
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
        
        # 上面（ひし形）を描画
        self.rect_poly(FL, FT, FR, FB, COLOR_TOP)
        
        # 上面の枠線を描画
        self.rect_polyb(FT, FL, FB, FR, COLOR_OUTLINE)

    def draw(self):
        pyxel.cls(0)
        
        # 3x3グリッドのダイアモンドタイルを描画
        for y in range(GRID_SIZE):
            for x in range(GRID_SIZE):
                self.draw_diamond_tile(x, y)
        
        # 操作説明
        pyxel.text(5, 5, "Arrow keys: Move camera", 7)
        pyxel.text(5, 13, "Q: Quit", 7)

App()
import pyxel
import random

WIN_WIDTH = 128
WIN_HEIGHT = 128
GRID_SIZE = 10  # グリッドの数（10x10）
CELL_SIZE = WIN_WIDTH // GRID_SIZE  # 各セルのピクセルサイズ
HEIGHT_UNIT = 4  # 1段あたりの高さ（ピクセル）

class App:
    def __init__(self):
        # 10x10の配列を作成し、各セルにランダムで0～3の高さを設定
        self.grid = [[random.randint(1, 3) for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]
        pyxel.init(WIN_WIDTH, WIN_HEIGHT, title="Grid Madness")
        pyxel.load("my_resource.pyxres")
        pyxel.run(self.update, self.draw)

    def update(self):
        # Esc Key Down
        if pyxel.btn(pyxel.KEY_ESCAPE):
            pyxel.quit()

    def draw(self):
        pyxel.cls(0)
        for y in range(GRID_SIZE):
            for x in range(GRID_SIZE):
                h = self.grid[y][x]  # 高さ情報
                iso_x = (x - y) * (CELL_SIZE // 2) + WIN_WIDTH // 2
                iso_y = (x + y) * (CELL_SIZE // 4) + 8 - h * HEIGHT_UNIT  # 高さ分だけ上にずらす
                points = [
                    (iso_x, iso_y + CELL_SIZE // 4),  # 左
                    (iso_x + CELL_SIZE // 2, iso_y),  # 上
                    (iso_x + CELL_SIZE, iso_y + CELL_SIZE // 4),  # 右
                    (iso_x + CELL_SIZE // 2, iso_y + CELL_SIZE // 2)  # 下
                ]
                # 2つの三角形で塗りつぶし
                pyxel.tri(points[0][0], points[0][1], points[1][0], points[1][1], points[2][0], points[2][1], h)
                pyxel.tri(points[0][0], points[0][1], points[2][0], points[2][1], points[3][0], points[3][1], h)
                # 枠線（4辺を個別にlineで描画）
                pyxel.line(points[0][0], points[0][1], points[1][0], points[1][1], 7)
                pyxel.line(points[1][0], points[1][1], points[2][0], points[2][1], 7)
                pyxel.line(points[2][0], points[2][1], points[3][0], points[3][1], 7)
                pyxel.line(points[3][0], points[3][1], points[0][0], points[0][1], 7)
                # ひし形の下の頂点に色番号8で点を描画
                px, py = points[3]
                #pyxel.pset(px, py, 8)
                # その点から高さ分だけ下方向に線を引く
                line_length = h * HEIGHT_UNIT
                pyxel.line(px, py, px, py + line_length, 8)
                # 左右と中央の頂点から高さ分だけ下方向に線を引く
                points_bottom = []
                for idx in [0, 2, 3]:
 #                   px, py = points[idx]
  #                  line_length = h * HEIGHT_UNIT
#                    points_bottom.append((px, py + line_length))
                # 左の高さ線の先端と中央の高さ線の先端をLINEで結ぶ
                #pyxel.line(points_bottom[0][0], points_bottom[0][1], points_bottom[2][0], points_bottom[2][1], 8)
                # 右の高さ線の先端と中央の高さ線の先端をLINEで結ぶ
                #pyxel.line(points_bottom[1][0], points_bottom[1][1], points_bottom[2][0], points_bottom[2][1], 8)
                # 左の高さ線の開始点、終端、中央の高さ線の終端で三角形を描画
                start_left = points[0]
                end_left = points_bottom[0]
                end_center = points_bottom[2]
                pyxel.tri(
                    start_left[0], start_left[1],
                    end_left[0], end_left[1],
                    end_center[0], end_center[1],
                    12  # 左側面も色12で統一
                )
                # 右の高さ線の開始点、終端、中央の高さ線の終端で三角形を描画
                start_right = points[2]
                end_right = points_bottom[1]
                end_center = points_bottom[2]
                pyxel.tri(
                    start_right[0], start_right[1],
                    end_right[0], end_right[1],
                    end_center[0], end_center[1],
                    5  # 右側面を色5で統一
                )
                # 床の左側の三角形を塗りつぶし（左の点、下の点、中央線の終端）
                pyxel.tri(
                    points[0][0], points[0][1],      # 左の点
                    points[3][0], points[3][1],      # 下（中央）の点
                    points_bottom[2][0], points_bottom[2][1],  # 中央線の終端
                    12  # 色12で塗りつぶし
                )
                # 床の右側の三角形を塗りつぶし（右の点、下の点、中央線の終端）
                pyxel.tri(
                    points[2][0], points[2][1],      # 右の点
                    points[3][0], points[3][1],      # 下（中央）の点
                    points_bottom[2][0], points_bottom[2][1],  # 中央線の終端
                    5  # 右側も色5で統一
                )
                # 最後にもう一度ひし形を描画して床を強調
                pyxel.line(points[0][0], points[0][1], points[1][0], points[1][1], 7)
                pyxel.line(points[1][0], points[1][1], points[2][0], points[2][1], 7)
                pyxel.line(points[2][0], points[2][1], points[3][0], points[3][1], 7)
                pyxel.line(points[3][0], points[3][1], points[0][0], points[0][1], 7)

        # 次に高さ線だけ描画
        # for y in range(GRID_SIZE):
        #     for x in range(GRID_SIZE):
        #         h = self.grid[y][x]
        #         iso_x = (x - y) * (CELL_SIZE // 2) + WIN_WIDTH // 2
        #         iso_y = (x + y) * (CELL_SIZE // 4) + 8 - h * 4
        #         points = [
        #             (iso_x, iso_y + CELL_SIZE // 4),
        #             (iso_x + CELL_SIZE // 2, iso_y),
        #             (iso_x + CELL_SIZE, iso_y + CELL_SIZE // 4),
        #             (iso_x + CELL_SIZE // 2, iso_y + CELL_SIZE // 2)
        #         ]
        #         line_length = h * (CELL_SIZE // 2)
        #         px, py = points[3]

if __name__ == '__main__':
    App()

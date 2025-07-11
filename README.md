# プロジェクト概要: GridMadness

このプロジェクトは、Pythonのゲーム開発ライブラリである `pyxel` を使用して、アイソメトリックな視点で表示されるグリッドベースのアプリケーションです。ユーザーはグリッド上をスクロールしたり、ズームしたり、特定のタイルを選択したりできます。

## 主要なファイルと役割:

1.  **`main.py`**:
    *   アプリケーションのエントリーポイントであり、`pyxel` の初期化、メインループ（`update` と `draw` 関数）を管理します。
    *   グリッドの描画ロジック、カメラのスクロール（矢印キー）、ズーム（Z/Xキー）、表示のリセット（Aキー）などのユーザーインタラクションを処理します。
    *   マウスの動きを検知し、マウスオーバーしているタイルや選択されたタイルをハイライト表示します。
    *   `FieldGrid.py` で定義された `FieldGrid` クラスのインスタンスを生成し、グリッドデータを扱います。
    *   `my_resource.pyxres` からリソースをロードします。

2.  **`FieldGrid.py`**:
    *   グリッド内の個々のタイルとその属性を管理するためのデータ構造とロジックを提供します。
    *   **`Tile` クラス**: 各タイルの高さ、地面の種類（"fire", "water", "earth", "wind"）、レベル、グリッド内の位置（行、列）、中心座標を保持するデータクラスです。
    *   **`FieldGrid` クラス**:
        *   指定されたサイズ（例: 10x10）でタイルの2次元配列を生成します。
        *   各タイルの初期高さ、地面の種類、レベルはランダムに設定されます。
        *   `update_heights` メソッドを持ち、タイルの高さを更新するロジックが含まれています（現在の実装では、高さを0増やし、15を超えたら0にリセットする）。

3.  **`my_resource.pyxres`**:
    *   `pyxel` アプリケーションで使用される画像、サウンド、マップなどのリソースが格納されているファイルです。`main.py` でロードされます。

## アプリケーションの動作概要:

*   起動すると、ランダムな高さと属性を持つ10x10のグリッドがアイソメトリックな視点で表示されます。
*   ユーザーはキーボードで視点を移動したり、ズームを変更したりできます。
*   マウスを動かすと、その下のタイルがハイライトされ、クリックするとタイルが選択されます。
*   タイルの高さは、`FieldGrid.py` の `update_heights` メソッドによって定期的に更新される可能性があります（現在の実装では、高さは実質的に変化しませんが、将来的な拡張の余地があります）。

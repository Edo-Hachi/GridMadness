from dataclasses import dataclass
import random

GROUND_TYPES = ["fire", "water", "earth", "wind"]

@dataclass
class Tile:
    height: int
    ground_type: str
    level: int
    row: int
    column: int
    center_x: float
    center_y: float


class FieldGrid:
    def __init__(self, size: int, tile_width: int, tile_height: int, base_x: int, base_y: int):
        self.size = size
        self.tile_width = tile_width
        self.tile_height = tile_height
        self.base_x = base_x
        self.base_y = base_y
        self.tiles = [
            [
                self._create_tile(row, column)
                for column in range(size)
            ]
            for row in range(size)
        ]

    def _create_tile(self, row: int, column: int) -> Tile:
        center_x = self.base_x + (column - row) * (self.tile_width // 2)
        center_y = self.base_y + (column + row) * (self.tile_height // 2)
        return Tile(
            height=random.randint(1, 15),
            ground_type=random.choice(GROUND_TYPES),
            level=random.randint(1, 3),
            row=row,
            column=column,
            center_x=center_x,
            center_y=center_y,
        )

    def __getitem__(self, index):
        return self.tiles[index]

    def update_heights(self):
        for row in self.tiles:
            for tile in row:
                tile.height += 0
                if tile.height > 15:
                    tile.height = 0

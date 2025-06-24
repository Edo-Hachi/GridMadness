from dataclasses import dataclass
import random

GROUND_TYPES = ["fire", "water", "earth", "wind"]

@dataclass
class Tile:
    height: int
    ground_type: str
    level: int


class FieldGrid:
    def __init__(self, size: int):
        self.size = size
        self.tiles = [[self._random_tile() for _ in range(size)] for _ in range(size)]

    def _random_tile(self) -> Tile:
        return Tile(
            height=random.randint(1, 15),
            ground_type=random.choice(GROUND_TYPES),
            level=random.randint(1, 3),
        )

    def __getitem__(self, index):
        return self.tiles[index]

    def update_heights(self):
        for row in self.tiles:
            for tile in row:
                tile.height += 2
                if tile.height > 15:
                    tile.height = 0

from blocks import Block, Ladder, Rope, Gold, Decoration, Entrance, Exit, AnimatedDecoration, Spawner
from background import Background
from enemy import Enemy


class Field:
    def __init__(self, w=None, h=None, file_name=None):
        if w is not None and h is not None and (w < 3 or h < 3):
            raise ValueError('Слишком маленькое поле')

        if w is None or h is None:
            w, h = 3, 3
        self.w, self.h = w, h
        self.player_x, self.player_y = 1, 1
        self.exit_x, self.exit_y = 1, 1
        self.gold_count = 0
        self.background_field = [[None] * w for _ in range(h)]
        self.foreground_field = [[None] * w for _ in range(h)]
        self.field = [[Block()
                       if 0 in (x, y) or x == w - 1 or y == h - 1 else
                       None for x in range(w)] for y in range(h)]
        self.background = None
        self.enemies = []

        if file_name is not None:
            with open(file_name) as f:
                exec(f.read(), globals(), locals())

        for enemy in self.enemies:
            enemy.field = self.field

    def __getitem__(self, key):
        return self.field[key]

    def get_player_pos(self):
        return self.player_x, self.player_y

    def get_enemies(self):
        return self.enemies

    def get_background(self):
        return self.background

    def get_gold_count(self):
        return self.gold_count

    def get_exit(self):
        return self.field[self.exit_y][self.exit_x]

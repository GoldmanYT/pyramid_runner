import pygame as pg
from blocks import Block, Ladder, Rope, Gold, Decoration, Entrance, Exit, AnimatedDecoration, Spawner, FakeBlock, Null
from background import Background
from enemy import Enemy1, Enemy2


class Field:
    def __init__(self, w=None, h=None, filename=None):
        if w is not None and h is not None and (w < 3 or h < 3):
            raise ValueError('Слишком маленькое поле')

        if w is None or h is None:
            w, h = 3, 3
        self.w, self.h = w, h
        self.player_x, self.player_y = 1, 1
        self.exit = None
        self.exit_pos = None
        self.gold_count = 0
        self.winning_ladders_field = [[None] * w for _ in range(h)]
        self.background_field = [[None] * w for _ in range(h)]
        self.foreground_field = [[None] * w for _ in range(h)]
        self.field = [[Block()
                       if 0 in (x, y) or x == w - 1 or y == h - 1 else
                       None for x in range(w)] for y in range(h)]
        self.background = None
        self.enemies = []
        self.spawners = []

        if filename is not None:
            self.decode(filename)

    def decode(self, filename):
        items = [Block, Ladder, Rope, Gold, Decoration, Entrance, Exit, AnimatedDecoration, Spawner, FakeBlock, Enemy1,
                 Enemy2, Background, Null]
        images = {}
        with open('data/images.txt') as f:
            for s in f.readlines():
                item, *ims = s.split()
                images[item] = [pg.image.load(img_name).convert_alpha() for img_name in ims]

        with open(filename + '.txt') as f:
            self.w, self.h = map(int, f.readline().split())
            s = f.readline().strip()
            if s:
                self.background = Background(image=images.get('Background')[0], crop_index=int(s))

        self.field = [[None] * self.w for _ in range(self.h)]
        self.background_field = [[None] * self.w for _ in range(self.h)]
        self.foreground_field = [[None] * self.w for _ in range(self.h)]

        with open(filename + '.xxx', 'rb') as f:
            i = 0
            x, y = 0, 0
            field_type = 0
            field_types = {
                0: self.field,
                1: self.background_field,
                2: self.foreground_field
            }
            a = list(map(int, f.read()))
            while i < len(a):
                index = [j.id for j in items].index(a[i])
                item = items[index]
                if item == Block:
                    field_types.get(field_type)[y][x] = Block(crop_index=a[i + 1], diggable=a[i + 2])
                    i += 3
                elif item in (Enemy1, Enemy2):
                    enemy = item(x=x, y=y)
                    self.enemies.append(enemy)
                    i += 1
                elif item == Null:
                    i += 1
                else:
                    field = field_types.get(field_type)
                    field[y][x] = item(crop_index=a[i + 1])
                    if item == Gold:
                        self.gold_count += 1
                    if item == Entrance:
                        self.player_x, self.player_y = x, y
                    if item == Exit:
                        self.exit = self.field[y][x]
                        self.exit_pos = x, y
                    if item == Spawner:
                        field[y][x].set_pos(x, y)
                        self.spawners.append(field[y][x])
                    i += 2
                x += 1
                if x == self.w:
                    x = 0
                    y += 1
                if y == self.h:
                    x = 0
                    y = 0
                    field_type += 1
        for row in self.field:
            for pos in row:
                if pos is not None:
                    if isinstance(pos, Block) and pos.diggable:
                        pos.image = images.get(pos.__class__.__name__)[1]
                    else:
                        pos.image = images.get(pos.__class__.__name__)[0]
        for row in self.background_field:
            for pos in row:
                if pos is not None:
                    pos.image = images.get(pos.__class__.__name__)[0]
        for row in self.foreground_field:
            for pos in row:
                if pos is not None:
                    pos.image = images.get(pos.__class__.__name__)[0]
        for enemy in self.enemies:
            enemy.image = images.get(enemy.__class__.__name__)[0]
            enemy.field = self.field
            enemy.entities = self.enemies

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
        return self.exit

    def get_exit_pos(self):
        return self.exit_pos

    def get_spawners(self):
        return self.spawners

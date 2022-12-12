import pygame as pg
from blocks import Block, Ladder, Rope, Gold, Decoration, Entrance, Exit, AnimatedDecoration, Spawner, FakeBlock
from background import Background
from enemy import Enemy
from consts import A, BG_H
from copy import deepcopy


class Field:
    def __init__(self, w=None, h=None, file_name=None):
        if w is not None and h is not None and (w < 3 or h < 3):
            raise ValueError('Слишком маленькое поле')

        if w is None or h is None:
            w, h = 3, 3
        self.w, self.h = w, h
        self.player_x, self.player_y = 1, 1
        self.exit = None
        self.gold_count = 0
        self.winning_ladders_field = [[None] * w for _ in range(h)]
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

        for y, row in enumerate(self.field):
            for x, pos in enumerate(row):
                if isinstance(pos, Gold):
                    self.gold_count += 1
                elif isinstance(pos, Exit):
                    self.exit = pos
                elif isinstance(pos, Entrance):
                    self.player_x, self.player_y = x, y

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

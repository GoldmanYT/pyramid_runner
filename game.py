import pygame as pg

from blocks import Ladder, Rope
from player import Player
from field import Field
from consts import FPS, GLOBAL_OFFSET_X, GLOBAL_OFFSET_Y, BACKGROUND_OFFSET_X, BACKGROUND_OFFSET_Y
from camera import Camera


class Game:
    def __init__(self, w, h):
        self.w, self.h = w, h
        pg.init()

        self.screen = pg.display.set_mode((w, h))
        self.a = 50
        self.field = None
        self.background_field = None
        self.foreground_field = None
        self.player = None
        self.enemies = None
        self.background = None
        self.camera = None
        self.gold_count = None
        self.exit = None
        self.load_level('levels/level1_28.txt')

        clock = pg.time.Clock()
        run = True

        while run:
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    run = False

            self.tick()
            self.draw()
            pg.display.flip()

            clock.tick(FPS)

    def load_level(self, file_name):
        self.field = Field(file_name=file_name)
        self.background_field = self.field.background_field
        self.foreground_field = self.field.foreground_field
        x, y = self.field.get_player_pos()
        self.player = Player(x, y, field=self.field, texture='data/player.png')
        self.enemies = self.field.get_enemies()
        self.background = self.field.get_background()
        self.camera = Camera(self.a * self.field.w, self.a * self.field.h, self.w, self.h)
        self.gold_count = self.field.get_gold_count()
        self.exit = self.field.get_exit()
        if self.background is not None:
            self.background.level_w = self.a * self.field.w - self.w
            self.background.level_h = self.a * self.field.h - self.h
            self.background.w = self.w
            self.background.h = self.h

    def tick(self):
        keys = pg.key.get_pressed()

        if not (self.gold_count - self.player.collected_gold) and not self.exit.opened:
            self.exit.open()
        if keys[pg.K_z]:
            self.player.dig('left')
        elif keys[pg.K_x]:
            self.player.dig('right')

        directions = []
        if keys[pg.K_UP] and not keys[pg.K_DOWN]:
            directions.append('up')
        if keys[pg.K_DOWN] and not keys[pg.K_UP]:
            directions.append('down')
        if keys[pg.K_LEFT] and not keys[pg.K_RIGHT]:
            directions.append('left')
        if keys[pg.K_RIGHT] and not keys[pg.K_LEFT]:
            directions.append('right')
        self.player.update(directions if directions else None)

        for enemy in self.enemies:
            enemy.update()

    def draw(self):
        self.screen.fill((0, 0, 0))
        camera_x, camera_y = self.camera.pos(
            self.player.x * self.a + self.player.step_x * self.a // self.player.n_steps + self.a // 2,
            (self.field.h - self.player.y - 1) * self.a -
            self.player.step_y * self.a // self.player.n_steps + self.a // 2)

        if self.background is not None:
            self.background.draw(self.screen, 0, 0, camera_x, camera_y)

        for y in range(self.field.h):
            for x in range(self.field.w):
                pos = self.background_field[y][x]
                if pos is not None:
                    pos.draw(
                        self.screen,
                        x * self.a + GLOBAL_OFFSET_X + BACKGROUND_OFFSET_X + camera_x,
                        (self.field.h - y - 1) * self.a + GLOBAL_OFFSET_Y + BACKGROUND_OFFSET_Y + camera_y
                    )
        for y in range(self.field.h):
            for x in range(self.field.w):
                pos = self.field[y][x]
                if pos is not None:
                    if isinstance(pos, Ladder):
                        pos.draw(
                            self.screen,
                            x * self.a + GLOBAL_OFFSET_X + camera_x,
                            (self.field.h - y - 1) * self.a + GLOBAL_OFFSET_Y + camera_y,
                            self.field[y + 1][x], self.field[y - 1][x]
                        )
                    elif isinstance(pos, Rope):
                        pos.draw(
                            self.screen,
                            x * self.a + GLOBAL_OFFSET_X + camera_x,
                            (self.field.h - y - 1) * self.a + GLOBAL_OFFSET_Y + camera_y,
                            self.field[y][x - 1], self.field[y][x + 1]
                        )
                    else:
                        pos.draw(
                            self.screen,
                            x * self.a + GLOBAL_OFFSET_X + camera_x,
                            (self.field.h - y - 1) * self.a + GLOBAL_OFFSET_Y + camera_y
                        )

        x, step_x, y, step_y = self.player.x, self.player.step_x, self.player.y, self.player.step_y
        self.player.draw(
            self.screen,
            x * self.a + step_x * self.a // self.player.n_steps + GLOBAL_OFFSET_X + camera_x,
            (self.field.h - y - 1) * self.a - step_y * self.a // self.player.n_steps + GLOBAL_OFFSET_Y + camera_y
        )
        for enemy in self.enemies:
            x, step_x, y, step_y = enemy.x, enemy.step_x, enemy.y, enemy.step_y
            enemy.draw(
                self.screen,
                x * self.a + step_x * self.a // self.player.n_steps + GLOBAL_OFFSET_X + camera_x,
                (self.field.h - y - 1) * self.a - step_y * self.a // self.player.n_steps + GLOBAL_OFFSET_Y + camera_y
            )

        for y in range(self.field.h):
            for x in range(self.field.w):
                pos = self.foreground_field[y][x]
                if pos is not None:
                    pos.draw(
                        self.screen,
                        x * self.a + GLOBAL_OFFSET_X + camera_x,
                        (self.field.h - y - 1) * self.a + GLOBAL_OFFSET_Y + camera_y
                    )

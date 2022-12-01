import pygame as pg

from blocks import Ladder, Rope
from player import Player
from field import Field
from enemy import Enemy
from consts import FPS, GLOBAL_OFFSET_X, GLOBAL_OFFSET_Y, BACKGROUND_OFFSET_X, BACKGROUND_OFFSET_Y


class Game:
    def __init__(self, w, h):
        self.w, self.h = w, h
        pg.init()

        self.screen = pg.display.set_mode((w, h))
        run = True
        self.field = Field(file_name='levels/level1_28.txt')
        self.background_field = self.field.background_field
        self.foreground_field = self.field.foreground_field
        x, y = self.field.get_player_pos()
        self.player = Player(x, y, field=self.field, texture='data/player.png')
        self.a = 50

        clock = pg.time.Clock()

        while run:
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    run = False

            self.tick()
            self.draw()
            pg.display.flip()

            clock.tick(FPS)

    def tick(self):
        keys = pg.key.get_pressed()
        inside = self.player.inside()
        under = self.player.under()

        if keys[pg.K_z]:
            self.player.dig('left')
        elif keys[pg.K_x]:
            self.player.dig('right')
        if isinstance(inside, Ladder):
            if keys[pg.K_UP] and not keys[pg.K_DOWN]:
                self.player.update('up')
            elif keys[pg.K_DOWN] and not keys[pg.K_UP]:
                self.player.update('down')
            elif keys[pg.K_LEFT] and not keys[pg.K_RIGHT]:
                self.player.update('left')
            elif keys[pg.K_RIGHT] and not keys[pg.K_LEFT]:
                self.player.update('right')
            else:
                self.player.update()
        else:
            if keys[pg.K_LEFT] and not keys[pg.K_RIGHT]:
                self.player.update('left')
            elif keys[pg.K_RIGHT] and not keys[pg.K_LEFT]:
                self.player.update('right')
            elif keys[pg.K_UP] and not keys[pg.K_DOWN]:
                self.player.update('up')
            elif keys[pg.K_DOWN] and not keys[pg.K_UP]:
                self.player.update('down')
            else:
                self.player.update()

    def draw(self):
        self.screen.fill((0, 0, 0))

        for y in range(self.field.h):
            for x in range(self.field.w):
                pos = self.background_field[y][x]
                if pos is not None:
                    pos.draw(
                        self.screen,
                        x * self.a + GLOBAL_OFFSET_X + BACKGROUND_OFFSET_X,
                        (self.field.h - y - 1) * self.a + GLOBAL_OFFSET_Y + BACKGROUND_OFFSET_Y
                    )
        for y in range(self.field.h):
            for x in range(self.field.w):
                pos = self.field[y][x]
                if pos is not None:
                    if isinstance(pos, Ladder):
                        pos.draw(
                            self.screen,
                            x * self.a + GLOBAL_OFFSET_X,
                            (self.field.h - y - 1) * self.a + GLOBAL_OFFSET_Y,
                            self.field[y + 1][x], self.field[y - 1][x]
                        )
                    elif isinstance(pos, Rope):
                        pos.draw(
                            self.screen,
                            x * self.a + GLOBAL_OFFSET_X,
                            (self.field.h - y - 1) * self.a + GLOBAL_OFFSET_Y,
                            self.field[y][x - 1], self.field[y][x + 1]
                        )
                    else:
                        pos.draw(
                            self.screen,
                            x * self.a + GLOBAL_OFFSET_X,
                            (self.field.h - y - 1) * self.a + GLOBAL_OFFSET_Y
                        )
        x, step_x, y, step_y = self.player.x, self.player.step_x, self.player.y, self.player.step_y
        self.player.draw(
            self.screen,
            x * self.a + step_x * self.a // self.player.n_steps + GLOBAL_OFFSET_X,
            (self.field.h - y - 1) * self.a - step_y * self.a // self.player.n_steps + GLOBAL_OFFSET_Y
        )
        for y in range(self.field.h):
            for x in range(self.field.w):
                pos = self.foreground_field[y][x]
                if pos is not None:
                    pos.draw(
                        self.screen,
                        x * self.a + GLOBAL_OFFSET_X,
                        (self.field.h - y - 1) * self.a + GLOBAL_OFFSET_Y
                    )

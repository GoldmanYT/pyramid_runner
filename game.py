import pygame as pg

from blocks import Block, Ladder, Rope, Gold
from player import Player
from field import Field
from enemy import Enemy

FPS = 167


class Game:
    def __init__(self, w, h):
        self.w, self.h = w, h
        pg.init()

        self.screen = pg.display.set_mode((w, h))
        run = True
        self.field = Field(file_name='levels/level0.txt')
        self.player = Player(2, 2, field=self.field, texture='data/player.png')
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
        if isinstance(inside, Ladder) or isinstance(under, Ladder):
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
                if self.field[y][x] is not None and self.field[y][x].texture is not None:
                    self.field[y][x].draw(self.screen, x * self.a, (self.field.h - y - 1) * self.a)
        x, step_x, y, step_y = self.player.x, self.player.step_x, self.player.y, self.player.step_y
        self.player.draw(
            self.screen,
            x * self.a + step_x * self.a // self.player.n_steps,
            (self.field.h - y - 1) * self.a - step_y * self.a // self.player.n_steps
        )

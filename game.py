import pygame as pg

from blocks import Block, Ladder
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
        self.field = Field(7, 7)
        self.field[1][1] = Ladder()
        self.field[2][1] = Ladder()
        self.field[3][3] = Ladder()
        self.field[2][2] = Block(1)
        self.field[2][3] = Block(1)
        self.field[2][4] = Block(1)
        self.player = Player(2, 1, field=self.field)
        self.a = 64

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

        if keys[pg.K_z]:
            self.player.dig('left')
        elif keys[pg.K_x]:
            self.player.dig('right')
        if keys[pg.K_LEFT] and not keys[pg.K_RIGHT]:
            self.player.update('left')
        elif keys[pg.K_RIGHT] and not keys[pg.K_LEFT]:
            self.player.update('right')
        elif keys[pg.K_UP] and not keys[pg.K_DOWN]:
            self.player.update('down')  # поменять местами
        elif keys[pg.K_DOWN] and not keys[pg.K_UP]:
            self.player.update('up')  # поменять местами
        else:
            self.player.update()

    def draw(self):
        self.screen.fill((0, 0, 0))

        for y in range(self.field.h):
            for x in range(self.field.w):
                if isinstance(self.field[y][x], Block):
                    if self.field[y][x].diggable:
                        if self.field[y][x].has_collision:
                            pg.draw.rect(self.screen, 'green', (x * self.a, y * self.a, self.a, self.a), 1)
                        else:
                            pg.draw.rect(self.screen, 'yellow', (x * self.a, y * self.a, self.a, self.a), 1)
                    else:
                        pg.draw.rect(self.screen, 'white', (x * self.a, y * self.a, self.a, self.a), 1)
                elif isinstance(self.field[y][x], Ladder):
                    pg.draw.line(self.screen, 'white', (x * self.a + self.a // 8, y * self.a), (x * self.a + self.a // 8, (y + 1) * self.a))
                    pg.draw.line(self.screen, 'white', (x * self.a + 7 * self.a // 8, y * self.a), (x * self.a + 7 * self.a // 8, (y + 1) * self.a))
                    pg.draw.line(self.screen, 'white', (x * self.a + self.a // 8, y * self.a + self.a // 4), (x * self.a + 7 * self.a // 8, y * self.a + self.a // 4))
                    pg.draw.line(self.screen, 'white', (x * self.a + self.a // 8, y * self.a + 2 * self.a // 4), (x * self.a + 7 * self.a // 8, y * self.a + 2 * self.a // 4))
                    pg.draw.line(self.screen, 'white', (x * self.a + self.a // 8, y * self.a + 3 * self.a // 4), (x * self.a + 7 * self.a // 8, y * self.a + 3 * self.a // 4))

        x, step_x, y, step_y = self.player.x, self.player.step_x, self.player.y, self.player.step_y
        pg.draw.ellipse(self.screen, 'red', (x * self.a + step_x * self.a // self.player.n_steps, y * self.a + step_y * self.a // self.player.n_steps, self.a, self.a), 1)

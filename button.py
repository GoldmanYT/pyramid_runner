import pygame as pg
from consts import MENU_BTN_SIZE


pg.init()


def dist(x1, y1, x2, y2):
    return ((x1 - x2) ** 2 + (y2 - y1) ** 2) ** 0.5


class Button:
    def __init__(self, im, bg_im, pos, start_opacity=125, velocity=5):
        self.im = im
        self.w, self.h = self.im.get_size()
        self.bg_im = bg_im
        self.opacity = start_opacity
        self.start_opacity = start_opacity
        self.x, self.y = pos
        self.r = MENU_BTN_SIZE // 2
        self.v = velocity

    def update(self, x, y, clicked):
        cursor_hovered = self.x <= x <= self.x + self.w and self.y <= y <= self.y + self.h
        if cursor_hovered and self.opacity < 255:
            self.opacity += self.v
        elif not cursor_hovered and self.opacity > self.start_opacity:
            self.opacity -= self.v
        if clicked and cursor_hovered:
            return True
        return False

    def draw(self, surface):
        button = pg.Surface((self.w, self.h), pg.SRCALPHA)
        button.blit(self.bg_im, (0, 0))
        button.set_alpha(min(self.opacity, 255))
        surface.blit(button, (self.x, self.y))
        surface.blit(self.im, (self.x, self.y))


class RoundButton(Button):
    def update(self, x, y, clicked):
        cursor_hovered = dist(self.x + self.r, self.y + self.r, x, y) <= self.r
        if cursor_hovered and self.opacity < 255:
            self.opacity += self.v
        elif not cursor_hovered and self.opacity > 128:
            self.opacity -= self.v
        if clicked and cursor_hovered:
            return True
        return False

import pygame as pg


W = 1024
H = 768


class Background:
    def __init__(self, texture=None, crop_index=0, level_w=None, level_h=None, w=None, h=None):
        self.texture = texture
        self.crop_index = crop_index
        self.level_w, self.level_h = level_w, level_h
        self.w, self.h = w, h
        if self.texture is not None:
            self.image = pg.image.load(self.texture).convert()

    def draw(self, surface, x, y, cam_x=None, cam_y=None):
        if self.texture is not None:
            if None in (cam_x, cam_y, self.level_w, self.level_h, self.w, self.h):
                surface.blit(self.image, (x, y), (0, self.crop_index * H, W, H))
            else:
                surface.blit(self.image, (x, y),
                             (-cam_x * (W - self.w) // self.level_w,
                              -cam_y * (H - self.h) // self.level_h + self.crop_index * H, W, H))

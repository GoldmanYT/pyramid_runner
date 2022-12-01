import pygame as pg


H = 768


class Background:
    def __init__(self, texture=None, crop_index=0):
        self.texture = texture
        self.crop_index = crop_index
        if self.texture is not None:
            self.image = pg.image.load(self.texture).convert()

    def draw(self, surface, x, y):
        if self.texture is not None:
            surface.blit(self.image, (x, y), (0, self.crop_index * H, 1024, H))

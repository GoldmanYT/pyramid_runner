from consts import BG_W, BG_H


class Background:
    def __init__(self, image=None, crop_index=0, level_w=None, level_h=None, w=None, h=None):
        self.image = image
        self.crop_index = crop_index
        self.level_w, self.level_h = level_w, level_h
        self.w, self.h = w, h

    def draw(self, surface, x, y, cam_x=None, cam_y=None):
        if self.image is not None:
            if None in (cam_x, cam_y, self.level_w, self.level_h, self.w, self.h) or self.level_w * self.level_h <= 0:
                surface.blit(self.image, (x, y), (0, self.crop_index * BG_H, BG_W, BG_H))
            else:
                surface.blit(self.image, (x, y),
                             (-cam_x * (BG_W - self.w) // self.level_w,
                              -cam_y * (BG_H - self.h) // self.level_h + self.crop_index * BG_H, BG_W, BG_H))

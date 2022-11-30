import pygame as pg


A = 64


class TexturedBlock:
    def __init__(self, texture=None, crop_index=0):
        self.texture = texture
        if texture is not None:
            self.image = pg.image.load(texture).convert_alpha()
            self.crop_index = crop_index

    def draw(self, surface, x, y):
        if self.texture is not None:
            surface.blit(self.image, (x, y), (0, self.crop_index * A, A, A))


class Block(TexturedBlock):
    def __init__(self, texture=None, crop_index=0, diggable=False, has_collision=True, recovery_time=1084):
        super().__init__(texture, crop_index)
        if not diggable and not has_collision:
            raise ValueError('Неразрушаемый блок должен иметь коллизию')

        self.diggable, self.has_collision = diggable, has_collision
        self.recovery_time = recovery_time
        self.time = 0

    def dig(self):
        self.has_collision = False

    def tick(self):
        if self.has_collision:
            return

        self.time += 1
        if self.time >= self.recovery_time:
            self.time = 0
            self.has_collision = True


class Ladder(TexturedBlock):
    pass


class Rope(TexturedBlock):
    pass


class Gold(TexturedBlock):
    def __init__(self, texture=None, crop_index=0):
        super().__init__(texture, crop_index)
        self.frames = 19
        self.frame = 0
        self.anim_index = 0
        self.anim_frames = 8
        self.anim_direction = 1

    def draw(self, surface, x, y):
        if self.texture is not None:
            surface.blit(self.image, (x, y), (self.anim_index * A, self.crop_index * A, A, A))
            self.frame += 1
            if self.frame == self.frames:
                self.frame = 0
                self.anim_index += self.anim_direction
                if self.anim_index in (0, self.anim_frames):
                    self.anim_direction *= -1
                    self.anim_index += 2 * self.anim_direction


class Decoration(TexturedBlock):
    pass

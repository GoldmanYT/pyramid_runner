import pygame as pg
from consts import A


class TexturedBlock:
    def __init__(self, image=None, crop_index=0):
        self.image = image
        self.crop_index = crop_index

    def draw(self, surface, x, y):
        if self.image is not None:
            surface.blit(self.image, (x, y), (0, self.crop_index * A, A, A))


class Block(TexturedBlock):
    id = 0
    has_collision = True
    recovery_time = 1084

    def __init__(self, image=None, crop_index=0, diggable=False):
        super().__init__(image, crop_index)

        self.diggable = diggable
        self.time = 0

    def draw(self, surface, x, y):
        if self.has_collision:
            super().draw(surface, x, y)

    def dig(self):
        self.has_collision = False

    def restore(self):
        self.has_collision = True
        self.time = 0

    def tick(self):
        if self.has_collision:
            return

        self.time += 1
        if self.time >= self.recovery_time:
            self.time = 0
            self.has_collision = True

    def __repr__(self):
        return '█'


class Ladder(TexturedBlock):
    id = 1

    def draw(self, surface, x, y, above=None, under=None):
        k = {
            (1, 1): 0,
            (0, 1): 1,
            (1, 0): 2,
            (0, 0): 3
        }
        if self.image is not None:
            surface.blit(self.image, (x, y),
                         (k.get((isinstance(above, Ladder), isinstance(under, Ladder))) * A, self.crop_index * A, A, A))

    def __repr__(self):
        return 'Н'


class Rope(TexturedBlock):
    id = 2

    def draw(self, surface, x, y, left=None, right=None):
        k = {
            (1, 1): 0,
            (0, 1): 1,
            (1, 0): 2,
            (0, 0): 3
        }
        if self.image is not None:
            surface.blit(self.image, (x, y),
                         (k.get((isinstance(left, Rope), isinstance(right, Rope))) * A, self.crop_index * A, A, A))

    def __repr__(self):
        return '-'


class Gold(TexturedBlock):
    id = 3

    def __init__(self, image=None, crop_index=0):
        super().__init__(image, crop_index)
        self.frames = 19
        self.frame = 0
        self.anim_index = 0
        self.anim_frames = 8
        self.anim_direction = 1

    def draw(self, surface, x, y):
        if self.image is not None:
            surface.blit(self.image, (x, y), (self.anim_index * A, self.crop_index * A, A, A))
            self.update()

    def update(self):
        self.frame += 1
        if self.frame == self.frames:
            self.frame = 0
            self.anim_index += self.anim_direction
            if self.anim_index in (0, self.anim_frames):
                self.anim_direction *= -1
                self.anim_index += 2 * self.anim_direction


class Decoration(TexturedBlock):
    id = 4


class AnimatedDecoration(TexturedBlock):
    id = 5

    def __init__(self, image=None, crop_index=0, n_frames=18, n_anims=2):
        super().__init__(image, crop_index)
        self.frame = 0
        self.n_frames = n_frames
        self.anim = 0
        self.n_anims = n_anims

    def draw(self, surface, x, y):
        if self.image is not None:
            surface.blit(self.image, (x, y), (self.anim * A, self.crop_index * A, A, A))
            self.update()

    def update(self):
        self.frame += 1
        if self.frame == self.n_frames:
            self.frame = 1
            self.anim = (self.anim + 1) % self.n_anims


class Entrance(TexturedBlock):
    id = 6

    def __init__(self, image=None, crop_index=0):
        super().__init__(image, crop_index)
        self.door_pos = 0

    def draw(self, surface, x, y):
        if self.image is not None:
            surface.blit(self.image, (x, y),
                         (0, 0, A, A))
            surface.blit(self.image, (x, y + self.door_pos),
                         (0, 64, A, A - self.door_pos))


class Exit(TexturedBlock):
    id = 7

    def __init__(self, image=None, crop_index=0):
        super().__init__(image, crop_index)
        self.opened = False
        self.door_pos = 0

    def draw(self, surface, x, y):
        if self.image is not None:
            surface.blit(self.image, (x, y),
                         (self.opened * A, 0, A, A))
            surface.blit(self.image, (x, y + self.door_pos),
                         (self.opened * A, 64, A, A - self.door_pos))

    def open(self):
        self.opened = True


class Spawner(TexturedBlock):
    id = 8

    def __init__(self, image=None, crop_index=0):
        super().__init__(image, crop_index)
        self.spawn_time = 501
        self.spawning = 0
        self.x, self.y = None, None
        self.enemy = None

    def update(self):
        if not self.spawning:
            return
        self.spawning -= 1
        if not self.spawning:
            self.enemy.x, self.enemy.y = self.x, self.y
            self.enemy.alive = True
            return self.enemy

    def draw(self, surface, x, y):
        if self.image is not None:
            dy = self.spawning * A // self.spawn_time
            if self.spawning:
                surface.blit(self.image, (x, y), (A, self.crop_index * A, A, dy))
                surface.blit(self.image, (x, y + dy), (2 * A, self.crop_index * A + dy, A, A - dy))
            else:
                surface.blit(self.image, (x, y), (0, self.crop_index * A, A, A))

    def spawn(self, enemy):
        self.spawning = self.spawn_time
        self.enemy = enemy

    def set_pos(self, x, y):
        self.x, self.y = x, y


class FakeBlock(TexturedBlock):
    id = 9

    def __init__(self, image=None, crop_index=0):
        super().__init__(image, crop_index)
        self.player_inside = False

    def update(self, player=None):
        if player is not None and player.inside() is self:
            self.player_inside = True
        else:
            self.player_inside = False

    def draw(self, surface, x, y):
        if self.image is not None:
            surface.blit(self.image, (x, y), (self.player_inside * A, self.crop_index * A, A, A))


class Null:
    id = 14

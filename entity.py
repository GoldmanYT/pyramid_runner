import pygame as pg
from blocks import Block, Ladder, Rope
from consts import A, N_ANIMS


class Entity:
    def __init__(self, x, y, speed=5500, n_steps=203500, field=None, image=None, entities=None):
        if speed > n_steps:
            raise ValueError('Скорость не может быть больше количества шагов')
        self.image = image
        self.x, self.y = x, y
        self.ver_speed = speed
        self.hor_speed = speed
        self.center_speed = 27 * speed // 22
        self.step_x, self.step_y, self.n_steps = 0, 0, n_steps
        self.field = field
        self.stop_time = 0
        if entities is None:
            self.entities = []
        else:
            self.entities = entities

        self.alive = True
        self.moved = False
        self.sprite_direction = 'l'
        self.direction = None
        self.last_direction = 'left'
        self.anim = 'standing_l'
        self.anims = {
            'standing_l': 0,
            'standing_r': 1,
            'going_l': 2,
            'going_r': 3,
            'roping_l': 4,
            'roping_r': 5,
            'laddering_l': 6,
            'laddering_r': 7,
            'falling_l': 8,
            'falling_r': 9,
            'digging_l': 10,
            'digging_r': 11
        }
        self.frame = 0
        self.n_anim = 0
        self.n_frames = {
            'standing': 41,
            'going': 6,
            'roping': 5,
            'laddering': 4,
            'falling': 5,
            'digging': 10
        }

    def pos(self):
        return (self.x + (self.step_x + self.n_steps // 2) // self.n_steps,
                self.y + (self.step_y + self.n_steps // 2) // self.n_steps)

    def under(self):
        if self.field is not None:
            x = self.x + (self.step_x + self.n_steps // 2) // self.n_steps
            y = self.y + bool(self.step_y) - 1
            return self.field[y][x]
        return Block()

    def inside(self):
        if self.field is not None:
            x, y = self.pos()
            return self.field[y][x]
        return None

    def is_standing(self):
        under = self.under()
        inside = self.inside()
        x = self.pos()[0]
        y = self.y + bool(self.step_y) - 1
        for entity in self.entities:
            if entity.pos() == (x, y) and self is not entity and not self.step_y:
                return True
        if isinstance(under, Block) and under.has_collision or \
                isinstance(under, Ladder) or isinstance(inside, Ladder) or \
                isinstance(inside, Rope) and not self.step_y:
            return True
        return False

    def check_state(self):
        if self.last_direction in ('left', 'right'):
            self.sprite_direction = self.last_direction[0]
        if not self.is_standing():
            return f'falling_{self.sprite_direction}'
        inside = self.inside()
        under = self.under()
        if isinstance(inside, Rope) and not self.step_y:
            return f'roping_{self.sprite_direction}'
        if (isinstance(inside, Ladder) or isinstance(under, Ladder)) and self.last_direction in ('up', 'down'):
            return f'laddering_{self.sprite_direction}'
        if self.stop_time:
            return f'digging_{self.sprite_direction}'
        if self.direction in ('left', 'right') and self.moved:
            return f'going_{self.sprite_direction}'
        return f'standing_{self.sprite_direction}'

    def draw(self, surface, x, y):
        if self.image is not None:
            anim = self.check_state()
            if anim != self.anim:
                self.anim = anim
                self.frame = 0
                self.n_anim = 0
            crop_index = self.anims.get(anim)
            anim, direction = anim.split('_')
            n_frames = self.n_frames.get(anim)
            surface.blit(self.image, (x, y), (self.n_anim * A, crop_index * A, A, A))
            if self.moved or anim == 'standing' or self.stop_time and anim != 'roping':
                self.frame += 1
            if self.frame == n_frames:
                self.frame = 0
                self.n_anim = (self.n_anim + 1) % N_ANIMS
        self.moved = False
        return anim

    def update(self, directions=None):
        x, y = self.pos()
        pos = self.field[y][x]
        if isinstance(pos, Block) and pos.has_collision:
            self.alive = False
        if not self.is_standing():
            self.move('down', ver_speed=min(self.ver_speed, (self.step_y - 1) % self.n_steps + 1))
            self.direction = 'down'
            self.last_direction = 'down'
        elif directions is not None:
            inside = self.inside()
            under = self.under()
            if not (isinstance(inside, Ladder) or isinstance(under, Ladder) and self.step_y) \
                    and 'up' in directions:
                self.direction = None
                self.moved = False
                directions.remove('up')
            direction = None
            if isinstance(inside, Ladder) or isinstance(under, Ladder) and self.step_y:
                if 'up' in directions:
                    direction = 'up'
                elif 'down' in directions:
                    direction = 'down'
            if direction is not None:
                self.move(direction, ver_speed=min(self.ver_speed, (self.step_y - 1) % self.n_steps + 1))
            if not self.moved:
                if 'left' in directions:
                    direction = 'left'
                elif 'right' in directions:
                    direction = 'right'
                if direction is not None:
                    self.move(direction, ver_speed=min(self.ver_speed, (self.step_y - 1) % self.n_steps + 1))
            if not self.moved:
                if 'up' in directions:
                    direction = 'up'
                elif 'down' in directions:
                    direction = 'down'
                if direction is not None:
                    self.move(direction, ver_speed=min(self.ver_speed, (self.step_y - 1) % self.n_steps + 1))
            if not self.stop_time:
                self.direction = direction
                self.last_direction = direction
        else:
            self.direction = None
            self.moved = False

    def move_to_center(self):
        if self.step_x < self.n_steps - self.step_x:
            step_x = self.step_x
        else:
            step_x = self.step_x - self.n_steps
        if self.step_y < self.n_steps - self.step_y:
            step_y = self.step_y
        else:
            step_y = self.step_y - self.n_steps

        hor_speed = min(abs(step_x), self.center_speed)
        ver_speed = min(abs(step_y), self.center_speed)

        directions = ['right', 'left']
        direction = directions[step_x > 0]
        self.move(direction, hor_speed, 0)

        directions = ['up', 'down']
        direction = directions[step_y > 0]
        self.move(direction, 0, ver_speed)

    def move(self, direction, hor_speed=None, ver_speed=None):
        if hor_speed is None:
            hor_speed = self.hor_speed
        if ver_speed is None:
            ver_speed = self.ver_speed
        directions = ['left', 'right', 'up', 'down']
        if direction not in directions:
            raise ValueError('Нет такого направления')

        k = {'left': -1, 'right': 1, 'up': 1, 'down': -1}
        dx, dy = 0, 0
        x0, y0, step_x0, step_y0 = self.x, self.y, self.step_x, self.step_y
        if direction in ('left', 'right'):
            self.step_x += hor_speed * k.get(direction)
            self.x += self.step_x // self.n_steps
            self.step_x %= self.n_steps
            dy = ((self.step_y + self.n_steps // 2) // self.n_steps * 2 - 1) * \
                min(ver_speed, self.n_steps - self.step_y, self.step_y)
            self.step_y += dy
            self.y += self.step_y // self.n_steps
            self.step_y %= self.n_steps
        elif direction in ('up', 'down'):
            self.step_y += ver_speed * k.get(direction)
            self.y += self.step_y // self.n_steps
            self.step_y %= self.n_steps
            dx = ((self.step_x + self.n_steps // 2) // self.n_steps * 2 - 1) * \
                min(hor_speed, self.n_steps - self.step_x, self.step_x)
            self.step_x += dx
            self.x += self.step_x // self.n_steps
            self.step_x %= self.n_steps

        if self.field is not None:
            px = {'left': 0, 'right': 1, 'up': (self.step_x + self.n_steps // 2) // self.n_steps,
                  'down': (self.step_x + self.n_steps // 2) // self.n_steps}
            py = {'left': (self.step_y + self.n_steps // 2) // self.n_steps,
                  'right': (self.step_y + self.n_steps // 2) // self.n_steps, 'up': 1, 'down': 0}
            pos = self.field[self.y + py.get(direction)][self.x + px.get(direction)]
            if isinstance(pos, Block) and pos.has_collision:
                if direction in ('left', 'right'):
                    self.step_x = 0
                    if direction == 'left':
                        self.x += 1
                    self.step_y -= dy
                    self.y += self.step_y // self.n_steps
                    self.step_y %= self.n_steps
                elif direction in ('up', 'down'):
                    self.step_y = 0
                    if direction == 'down':
                        self.y += 1
                    self.step_x -= dx
                    self.x += self.step_x // self.n_steps
                    self.step_x %= self.n_steps

        x1, y1, step_x1, step_y1 = self.x, self.y, self.step_x, self.step_y
        if (x0, y0, step_x0, step_y0) == (x1, y1, step_x1, step_y1):
            self.moved = False
        else:
            self.moved = True

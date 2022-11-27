from blocks import Block, Ladder


class Entity:
    def __init__(self, x, y, speed=5500, n_steps=203500, field=None):
        if speed > n_steps:
            raise ValueError('Скорость не может быть больше количества шагов')
        self.x, self.y = x, y
        self.ver_speed = speed
        self.hor_speed = 23 * speed // 22
        self.center_speed = 27 * speed // 22
        self.block_dig_speed = 5 * speed // 2
        self.step_x, self.step_y, self.n_steps = 0, 0, n_steps
        self.field = field

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
        if isinstance(under, Block) and under.has_collision or \
           isinstance(under, Ladder) or isinstance(inside, Ladder):
            return True

        return False

    def update(self, direction=None):
        if not self.is_standing():
            self.move('down')
        elif direction is not None:
            if not (isinstance(self.inside(), Ladder) or isinstance(self.under(), Ladder)) \
                    and direction == 'up':
                return
            self.move(direction)

    def move_to(self, x, y):
        step_x = self.x * self.n_steps + self.step_x
        step_y = self.y * self.n_steps + self.step_y

    def move(self, direction):
        directions = ['left', 'right', 'up', 'down', 'fall']
        if direction not in directions:
            raise ValueError('Нет такого направления')

        k = {'left': -1, 'right': 1, 'up': 1, 'down': -1}
        dx, dy = 0, 0
        if direction in ('left', 'right'):
            self.step_x += self.hor_speed * k.get(direction)
            self.x += self.step_x // self.n_steps
            self.step_x %= self.n_steps
            dy = ((self.step_y + self.n_steps // 2) // self.n_steps * 2 - 1) * \
                min(self.ver_speed, self.n_steps - self.step_y, self.step_y)
            self.step_y += dy
            self.y += self.step_y // self.n_steps
            self.step_y %= self.n_steps
        elif direction in ('up', 'down'):
            self.step_y += self.ver_speed * k.get(direction)
            self.y += self.step_y // self.n_steps
            self.step_y %= self.n_steps
            dx = ((self.step_x + self.n_steps // 2) // self.n_steps * 2 - 1) * \
                min(self.hor_speed, self.n_steps - self.step_x, self.step_x)
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

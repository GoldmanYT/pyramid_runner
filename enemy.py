from blocks import Block, Ladder, Rope
from entity import Entity


class Enemy(Entity):
    def __init__(self, x=0, y=0, speed=2618, n_steps=203500, field=None, image=None, entities=None):
        super().__init__(x, y, speed, n_steps, field, image, entities)
        self.speed = speed
        self.n_frames = {
            'standing': 41,
            'going': 13,
            'roping': 11,
            'laddering': 8,
            'falling': 11,
            'digging': 21
        }
        self.w, self.h = 0, 0
        self.freeze_time = 268
        self.block = None

    def check_state(self):
        if self.last_direction in ('left', 'right'):
            self.sprite_direction = self.last_direction[0]
        if not self.is_standing():
            return f'falling_{self.sprite_direction}'
        inside = self.inside()
        under = self.under()
        if isinstance(inside, Rope) and not self.step_y:
            return f'roping_{self.sprite_direction}'
        if (isinstance(inside, Ladder) or isinstance(under, Ladder) or
            isinstance(inside, Block) and not self.stop_time) and \
                self.last_direction in ('up', 'down'):
            return f'laddering_{self.sprite_direction}'
        if self.direction in ('left', 'right') and self.moved:
            return f'going_{self.sprite_direction}'
        return f'standing_{self.sprite_direction}'

    def set_field(self, field):
        self.field = field
        self.w, self.h = self.field.w, self.field.h

    def update(self, directions=None, player=None):
        pos = self.move_to_player(player)
        k = {
            (0, 1): 'down',
            (0, -1): 'up',
            (1, 0): 'left',
            (-1, 0): 'right'
        }
        directions = [k.get(pos)]
        super().update(directions)

    def get_directions(self, x, y):
        under = self.field[y - 1][x] if 0 <= y - 1 < self.h else Block()
        pos = self.field[y][x]
        if isinstance(under, Ladder) or isinstance(pos, Ladder):
            return [(0, -1), (0, 1), (-1, 0), (1, 0)]
        if isinstance(under, Block) or isinstance(pos, Rope):
            return [(-1, 0), (1, 0), (0, -1)]
        return [(0, -1)]

    def is_free(self, x, y):
        return not isinstance(self.field[y][x], Block)

    def move_to_player(self, player):
        if self.w == 0 == self.h:
            raise ValueError('Нет поля')
        x, y = self.pos()
        target = player.pos()
        distance = [[float('inf')] * self.w for _ in range(self.h)]
        distance[y][x] = 0
        prev = [[None] * self.w for _ in range(self.h)]
        queue = [(x, y)]
        while queue:
            x, y = queue.pop(0)
            for dx, dy in self.get_directions(x, y):
                next_x, next_y = x + dx, y + dy
                if self.w > next_x >= 0 <= next_y < self.h and self.is_free(next_x, next_y) and \
                        distance[next_y][next_x] == float('inf'):
                    distance[next_y][next_x] = distance[y][x] + 1
                    prev[next_y][next_x] = (x, y)
                    queue.append((next_x, next_y))
        x, y = target
        start = self.pos()
        if distance[y][x] == float('inf') or (x, y) == start:
            return None
        while prev[y][x] != start:
            x, y = prev[y][x]
        start_x, start_y = start
        return start_x - x, start_y - y


class Enemy1(Enemy):
    id = 11


class Enemy2(Enemy):
    id = 12

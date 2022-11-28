from entity import Entity
from blocks import Block, Ladder, Gold, Decoration


class Player(Entity):
    def __init__(self, x, y, speed=5500, n_steps=203500, field=None):
        super().__init__(x, y, speed=speed, n_steps=n_steps, field=field)
        self.dug_blocks = []
        self.freeze_frames = 67
        self.stop_time = 0

    def dig(self, direction):
        directions = ['left', 'right']
        if direction not in directions:
            raise ValueError('Нет такого направления')

        if not self.is_standing():
            return

        k = {'left': -1, 'right': 1}
        x, y = self.pos()
        pos = self.field[y - 1][x + k.get(direction)]
        above_pos = self.field[y][x + k.get(direction)]

        if isinstance(pos, Block) and pos.diggable and pos.has_collision and above_pos is None:
            pos.dig()
            self.dug_blocks.append(pos)
            self.stop_time = self.freeze_frames

    def update(self, direction=None):
        if not self.stop_time:
            super().update(direction)
        else:
            self.move_to_center()
            self.stop_time -= 1
        inside = self.inside()
        if isinstance(inside, Gold):
            x, y = self.pos()
            self.field[y][x] = None

        recovered_blocks = []
        for i, block in enumerate(self.dug_blocks):
            block.tick()
            if block.has_collision:
                recovered_blocks.append(i)

        for i in recovered_blocks[::-1]:
            self.dug_blocks.pop(i)

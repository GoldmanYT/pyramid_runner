from entity import Entity
from blocks import Block, Ladder, Gold, Decoration


class Player(Entity):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.dug_blocks = []

    def dig(self, direction):
        directions = ['left', 'right']
        if direction not in directions:
            raise ValueError('Нет такого направления')

        under = self.under()
        if not (isinstance(under, Block) and under.has_collision or
                isinstance(under, Ladder)):
            return

        k = {'left': -1, 'right': 1}
        x, y = self.pos()
        pos = self.field[y - 1][x + k.get(direction)]
        above_pos = self.field[y][x + k.get(direction)]

        if isinstance(pos, Block) and pos.diggable and pos.has_collision and \
           (above_pos is None or isinstance(above_pos, Decoration)):
            pos.dig()
            self.dug_blocks.append(pos)

    def update(self, direction=None):
        super().update(direction)
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

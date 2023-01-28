from entity import Entity
from blocks import Block, Gold, Entrance, Exit, Spawner, Decoration, AnimatedDecoration


class Player(Entity):
    id = 10

    def __init__(self, x, y, speed=5500, n_steps=203500, field=None, image=None, entities=None):
        super().__init__(x, y, speed, n_steps, field, image, entities)
        self.dug_blocks = []
        self.freeze_frames = 67
        self.collected_gold = 0
        self.above_digging_pos = None
        self.digging_block = None

    def dig(self, direction):
        directions = ['left', 'right']
        if direction not in directions:
            raise ValueError('Нет такого направления')

        if not self.is_standing():
            return False

        k = {'left': -1, 'right': 1}
        x, y = self.pos()
        pos = self.field[y - 1][x + k.get(direction)]
        above_pos = self.field[y][x + k.get(direction)]
        for entity in self.entities:
            if entity.pos() == (x + k.get(direction), y):
                return False

        if isinstance(pos, Block) and pos.diggable and pos.has_collision and \
                (above_pos is None or isinstance(above_pos, Block) and not above_pos.has_collision or
                 isinstance(above_pos, Entrance) or isinstance(above_pos, Exit) or
                 isinstance(above_pos, Spawner) or isinstance(above_pos, Decoration) or
                 isinstance(above_pos, AnimatedDecoration)):
            pos.dig()
            self.above_digging_pos = x + k.get(direction), y
            self.digging_block = pos
            self.dug_blocks.append(pos)
            self.stop_time = self.freeze_frames
            self.last_direction = direction
            return True
        return False

    def update(self, directions=None):
        restored = False
        if not self.stop_time:
            self.above_digging_pos = None
            self.digging_block = None
            super().update(directions)
        else:
            self.move_to_center()
            self.stop_time -= 1
            for entity in self.entities:
                if entity.pos() == self.above_digging_pos:
                    restored = self.digging_block.restore()

        for entity in self.entities:
            if entity.pos() == self.pos():
                self.alive = False

        gold_collected = False
        inside = self.inside()
        if isinstance(inside, Gold):
            x, y = self.pos()
            self.field[y][x] = None
            self.collected_gold += 1
            gold_collected = True

        recovered_blocks = []
        for i, block in enumerate(self.dug_blocks):
            block.tick()
            if block.has_collision:
                recovered_blocks.append(i)

        for i in recovered_blocks[::-1]:
            self.dug_blocks.pop(i)

        return gold_collected, restored

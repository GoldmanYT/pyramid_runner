class TexturedBlock:
    def __init__(self, texture=None):
        self.texture = texture


class Block(TexturedBlock):
    def __init__(self, texture=None, diggable=False, has_collision=True, recovery_time=210):
        super().__init__(texture)
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
    pass


class Decoration(TexturedBlock):
    pass

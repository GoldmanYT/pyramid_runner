class Block:
    def __init__(self, diggable=False, has_collision=True, recovery_time=210):
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

from entity import Entity


class Enemy(Entity):
    def __init__(self, x=0, y=0, speed=2618, n_steps=203500, field=None, image=None):
        super().__init__(x, y, speed, n_steps, field, image)
        self.speed = speed
        self.n_frames = {
            'standing': 41,
            'going': 6,
            'roping': 5,
            'laddering': 4,
            'falling': 5,
            'digging': 10
        }

    def update(self, directions=None):
        super().update(directions)

from blocks import Block, Ladder


class Field:
    def __init__(self, w, h, file=None):
        if w < 3 or h < 3:
            raise ValueError('Слишком маленькое поле')

        if file is not None:
            pass
        self.w, self.h = w, h
        self.field = [[Block()
                       if 0 in (x, y) or x == w - 1 or y == h - 1 else
                       None for x in range(w)] for y in range(h)]

    def __getitem__(self, key):
        return self.field[key]

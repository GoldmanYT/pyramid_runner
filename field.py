from blocks import Block, Ladder, Rope, Gold, Decoration


class Field:
    def __init__(self, w=None, h=None, file_name=None):
        if w is not None and h is not None and (w < 3 or h < 3):
            raise ValueError('Слишком маленькое поле')

        if w is None or h is None:
            w, h = 3, 3
        self.w, self.h = w, h
        self.field = [[Block()
                       if 0 in (x, y) or x == w - 1 or y == h - 1 else
                       None for x in range(w)] for y in range(h)]
        if file_name is not None:
            with open(file_name) as f:
                exec(f.read(), globals(), locals())
        print(self.field)

    def __getitem__(self, key):
        return self.field[key]

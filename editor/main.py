import pygame as pg
from blocks import Block, Ladder, Rope, Gold, Decoration
from inspect import getfullargspec


def draw(item, x, y, t=True):
    global a, cam_x, cam_y
    if item is not None and item.texture is not None:
        sprite = pg.image.load(item.texture)
        screen.blit(sprite, sprite.get_rect(x=x * a - (cam_x + 2 if t else 0), y=y * a - (cam_y + 14 if t else 0)))
    elif isinstance(item, Block):
        if item.diggable:
            pass
        else:
            pass
    elif isinstance(item, Ladder):
        pass
    elif isinstance(item, Rope):
        pass
    elif isinstance(item, Gold):
        pass
    elif isinstance(item, Decoration):
        pass


def on_field(x, y):
    return w - 2 >= x >= 1 <= y <= h - 2


def place(item, x, y):
    field[y][x] = item


def delete(x, y):
    field[y][x] = None


# w = int(input('w: '))
# h = int(input('h: '))
w, h = 8, 8
a = 50

pg.init()

screen = pg.display.set_mode((800, 600))
run = True
items = [Block(texture='data/block.png'),
         Block(texture='data/block_diggable.png', diggable=True),
         Ladder(texture='data/ladder.png'),
         Rope(texture='data/rope.png'),
         Gold(texture='data/gold.png')]
field = [[items[0] if 0 in (x, y) or x == w - 1 or y == h - 1 else None for x in range(w)] for y in range(h)]
selected_item = 0
cam_x, cam_y = 0, 0
delete_mode = False
place_mode = False
move_mode = False

while run:
    screen.fill((0, 0, 0))
    for event in pg.event.get():
        if event.type == pg.QUIT:
            run = False
        elif event.type == pg.MOUSEBUTTONDOWN:
            mouse_x, mouse_y = event.pos
            x, y = (mouse_x + cam_x) // a, h - (mouse_y + cam_y) // a - 1
            if event.button == 1:
                place_mode = True
                if on_field(x, y):
                    place(items[selected_item], x, y)
            elif event.button == 2:
                move_mode = True
            elif event.button == 3:
                delete_mode = True
                if on_field(x, y):
                    delete(x, y)
            elif event.button == 4:
                selected_item += 1
                selected_item %= len(items)
            elif event.button == 5:
                selected_item -= 1
                selected_item %= len(items)
        elif event.type == pg.MOUSEBUTTONUP:
            if event.button == 1:
                place_mode = False
            elif event.button == 2:
                move_mode = False
            elif event.button == 3:
                delete_mode = False
        elif event.type == pg.MOUSEMOTION:
            mouse_x, mouse_y = event.pos
            x, y = (mouse_x + cam_x) // a, h - (mouse_y + cam_y) // a - 1
            if on_field(x, y):
                if delete_mode:
                    delete(x, y)
                elif place_mode:
                    place(items[selected_item], x, y)
            if move_mode:
                x, y = event.rel
                cam_x -= x
                cam_y -= y

    for y in range(h - 1, -1, -1):
        for x in range(w):
            draw(field[h - y - 1][x], x, y)
    screen.fill((0, 0, 0), (0, 0, 64, 64))
    draw(items[selected_item], 0, 0, False)
    pg.display.flip()
pg.quit()

file_name = input('Введите имя файла: ')
if file_name:
    with open('C:/Users/DEXP/PycharmProjects/pyramid_runner/' + file_name, 'w') as f:
        f.write(f'self.w, self.h = {w}, {h}' + '\n')
        for x in range(w):
            for y in range(h):
                pos = field[y][x]
                args_spec = getfullargspec(pos.__init__)
                args = args_spec.args[1:]
                defaults = args_spec.defaults
                if pos is not None:
                    f.write(f'self.field[{y}][{x}] = {pos.__class__.__name__}(' +
                            ', '.join(f'''{arg}={"'" if type(eval(f"field[y][x].{arg}")) == str else ""}'''
                                      f'''{eval(f"field[y][x].{arg}")}'''
                                      f'''{"'" if type(eval(f"field[y][x].{arg}")) == str else ""}'''
                                      for i, arg in enumerate(args)
                                      if defaults[i] != eval(f"field[y][x].{arg}")) +
                            ')\n')

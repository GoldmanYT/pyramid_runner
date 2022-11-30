import pygame as pg
from blocks import Block, Ladder, Rope, Gold, Decoration
from inspect import getfullargspec


def draw(item, x, y, t=True):
    global a, cam_x, cam_y
    if item is not None and item.texture is not None:
        item.draw(screen, x * a - (cam_x + 2 if t else 0), y * a - (cam_y + 14 if t else 0))


def on_field(x, y):
    return w - 1 >= x >= 0 <= y <= h - 1


def place(item, selected_index, x, y):
    field[y][x] = item[selected_index]


def delete(x, y):
    field[y][x] = None


w, h = map(int, input('w h: ').split())
a = 50
FPS = 167

pg.init()

screen = pg.display.set_mode((800, 600))
clock = pg.time.Clock()
run = True
items = [Block(texture='data/block.png'),
         Block(texture='data/block_diggable.png', diggable=True),
         Ladder(texture='data/ladder.png'),
         Rope(texture='data/rope.png'),
         Gold(texture='data/gold.png'),
         Decoration(texture='data/decoration.png')]

for i in range(len(items)):
    item = items[i]
    temp = []
    for j in range(item.image.get_size()[1] // 64):
        args_spec = getfullargspec(item.__init__)
        args = args_spec.args[1:]
        defaults = args_spec.defaults

        copy = eval(f'{item.__class__.__name__}(' +
                    ', '.join(f'''{arg}={"'" if type(m:=eval(f"items[{i}].{arg}")) == str else ""}'''
                              f'''{m}{"'" if type(m) == str else ""}'''
                              for k, arg in enumerate(args)
                              if defaults[k] != eval(f"items[{i}].{arg}")) + ')')
        copy.crop_index = j
        temp.append(copy)
    items[i] = temp

field = [[items[0][0] if 0 in (x, y) or x == w - 1 or y == h - 1 else None for x in range(w)] for y in range(h)]
background = [[None] * w for _ in range(h)]
foreground = [[None] * w for _ in range(h)]
edit_mode = 0
offset_x, offset_y = 10, -10
selected_item = 0
selected_index = 0
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
            keys = pg.key.get_pressed()
            if event.button == 1:
                place_mode = True
                if on_field(x, y):
                    place(items[selected_item], selected_index, x, y)
            elif event.button == 2:
                move_mode = True
            elif event.button == 3:
                delete_mode = True
                if on_field(x, y):
                    delete(x, y)
            elif event.button == 4:
                if keys[pg.K_LSHIFT]:
                    selected_index += 1
                    selected_index %= len(items[selected_item])
                else:
                    selected_index = 0
                    selected_item += 1
                    selected_item %= len(items)
            elif event.button == 5:
                if keys[pg.K_LSHIFT]:
                    selected_index -= 1
                    selected_index %= len(items[selected_item])
                else:
                    selected_index = 0
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
                    place(items[selected_item], selected_index, x, y)
            if move_mode:
                x, y = event.rel
                cam_x -= x
                cam_y -= y
        elif event.type == pg.KEYDOWN:
            if event.key == pg.K_SPACE:
                edit_mode = (edit_mode + 1) % 3

    for y in range(h - 1, -1, -1):
        for x in range(w):
            draw(field[h - y - 1][x], x, y)
    screen.fill((0, 0, 0), (0, 0, 64, 64))
    draw(items[selected_item][selected_index], 0, 0, False)
    clock.tick(FPS)
    pg.display.flip()
pg.quit()

file_name = input('Введите имя файла: ')
if file_name:
    with open('levels/' + file_name, 'w') as f:
        f.write(f'self.w, self.h = {w}, {h}' + '\n')
        f.write('self.field = [[Block() '
                f'if 0 in (x, y) or x == {w} - 1 or y == {h} - 1 else '
                f'None for x in range({w})] for y in range({h})]\n')
        for y in range(h):
            for x in range(w):
                pos = field[y][x]
                args_spec = getfullargspec(pos.__init__)
                args = args_spec.args[1:]
                defaults = args_spec.defaults
                if pos is not None:
                    f.write(f'self.field[{y}][{x}] = {pos.__class__.__name__}(' +
                            ', '.join(f'''{arg}={"'" if type(m:=eval(f"field[y][x].{arg}")) == str else ""}'''
                                      f'''{m}{"'" if type(m) == str else ""}'''
                                      for i, arg in enumerate(args)
                                      if defaults[i] != eval(f"field[y][x].{arg}")) + ')\n')

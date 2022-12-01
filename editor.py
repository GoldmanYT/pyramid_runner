import pygame as pg
from blocks import Block, Ladder, Rope, Gold, Decoration, Entrance, Exit
from inspect import getfullargspec
from backgound import Background


def draw(item, x, y, t=True, offset=False):
    global a, cam_x, cam_y, offset_x, offset_y, field
    if item is not None and item.texture is not None:
        if isinstance(item, Ladder) or isinstance(item, Rope):
            item.draw(screen,
                      x * a - (cam_x + 2 if t else 0) + (offset_x if offset else 0),
                      y * a - (cam_y + 14 if t else 0) + (offset_y if offset else 0), None, None)
        else:
            item.draw(screen,
                      x * a - (cam_x + 2 if t else 0) + (offset_x if offset else 0),
                      y * a - (cam_y + 14 if t else 0) + (offset_y if offset else 0))


def on_field(x, y):
    return w - 1 >= x >= 0 <= y <= h - 1


def place(container, item, selected_index, x, y):
    container[y][x] = item[selected_index]


def delete(container, x, y):
    container[y][x] = None


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
         Decoration(texture='data/decoration.png'),
         Entrance(texture='data/entrance.png'),
         Exit(texture='data/exit.png')]

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
background_field = [[None] * w for _ in range(h)]
foreground_field = [[None] * w for _ in range(h)]
background = None
n_backgrounds = 7
backgrounds = [Background(texture='data/background.png', crop_index=i) for i in range(n_backgrounds)]
edit_mode = 0
offset_x, offset_y = 10, -10
selected_item = 0
selected_index = 0
cam_x, cam_y = 0, 0
delete_mode = False
place_mode = False
move_mode = False
inventory_opened = False

while run:
    screen.fill((0, 0, 0))
    if background is not None:
        backgrounds[background].draw(screen, 0, 0)
    keys = pg.key.get_pressed()
    if keys[pg.K_f]:
        background_field = [[items[selected_item][selected_index]] * w for _ in range(h)]
    for event in pg.event.get():
        if event.type == pg.QUIT:
            run = False
        elif event.type == pg.MOUSEBUTTONDOWN:
            mouse_x, mouse_y = event.pos
            if edit_mode == 2:
                x, y = (mouse_x + cam_x - offset_x) // a, h - (mouse_y + cam_y - offset_y) // a - 1
            else:
                x, y = (mouse_x + cam_x) // a, h - (mouse_y + cam_y) // a - 1
            if event.button == 1:
                place_mode = True
                if on_field(x, y):
                    if edit_mode == 0:
                        place(field, items[selected_item], selected_index, x, y)
                    elif edit_mode == 1:
                        place(foreground_field, items[selected_item], selected_index, x, y)
                    elif edit_mode == 2:
                        place(background_field, items[selected_item], selected_index, x, y)
            elif event.button == 2:
                move_mode = True
            elif event.button == 3:
                delete_mode = True
                if on_field(x, y):
                    if edit_mode == 0:
                        delete(field, x, y)
                    elif edit_mode == 1:
                        delete(foreground_field, x, y)
                    elif edit_mode == 2:
                        delete(background_field, x, y)
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
            if edit_mode == 2:
                x, y = (mouse_x + cam_x - offset_x) // a, h - (mouse_y + cam_y - offset_y) // a - 1
            else:
                x, y = (mouse_x + cam_x) // a, h - (mouse_y + cam_y) // a - 1
            if on_field(x, y):
                if delete_mode:
                    if edit_mode == 0:
                        delete(field, x, y)
                    elif edit_mode == 1:
                        delete(foreground_field, x, y)
                    elif edit_mode == 2:
                        delete(background_field, x, y)
                elif place_mode:
                    if edit_mode == 0:
                        place(field, items[selected_item], selected_index, x, y)
                    elif edit_mode == 1:
                        place(foreground_field, items[selected_item], selected_index, x, y)
                    elif edit_mode == 2:
                        place(background_field, items[selected_item], selected_index, x, y)
            if move_mode:
                x, y = event.rel
                cam_x -= x
                cam_y -= y
        elif event.type == pg.KEYDOWN:
            if event.key == pg.K_SPACE:
                edit_mode = (edit_mode + 1) % 3
            elif event.key == pg.K_b:
                if background is None:
                    background = 0
                else:
                    if keys[pg.K_LSHIFT]:
                        background = (background + 1) % n_backgrounds
                    else:
                        background = None
            elif event.key == pg.K_e:
                inventory_opened = not inventory_opened
    for y in range(h - 1, -1, -1):
        for x in range(w):
            draw(background_field[h - y - 1][x], x, y, offset=True)
    if edit_mode in (0, 1):
        for y in range(h - 1, -1, -1):
            for x in range(w):
                draw(field[h - y - 1][x], x, y)
    if edit_mode == 1:
        for y in range(h - 1, -1, -1):
            for x in range(w):
                draw(foreground_field[h - y - 1][x], x, y)
    screen.fill((0, 0, 0), (0, 0, 64, 64))
    draw(items[selected_item][selected_index], 0, 0, False)
    clock.tick(FPS)
    pg.display.flip()
pg.quit()

file_name = input('Введите имя файла: ')
if file_name:
    with open('levels/' + file_name, 'w') as f:
        f.write(f'self.w, self.h = {w}, {h}' + '\n')
        f.write(f'self.field = [[None] * {w} for y in range({h})]\n')
        f.write(f'self.background_field = [[None] * {w} for y in range({h})]\n')
        f.write(f'self.foreground_field = [[None] * {w} for y in range({h})]\n')
        for y in range(h):
            for x in range(w):
                pos = field[y][x]
                if pos is not None:
                    args_spec = getfullargspec(pos.__init__)
                    args = args_spec.args[1:]
                    defaults = args_spec.defaults
                    f.write(f'self.field[{y}][{x}] = {pos.__class__.__name__}(' +
                            ', '.join(f'''{arg}={"'" if type(m:=eval(f"field[y][x].{arg}")) == str else ""}'''
                                      f'''{m}{"'" if type(m) == str else ""}'''
                                      for i, arg in enumerate(args)
                                      if defaults[i] != eval(f"field[y][x].{arg}")) + ')\n')
                    if isinstance(pos, Entrance):
                        f.write(f'self.player_x, self.player_y = {x}, {y}\n')
                pos = background_field[y][x]
                if pos is not None:
                    args_spec = getfullargspec(pos.__init__)
                    args = args_spec.args[1:]
                    defaults = args_spec.defaults
                    f.write(f'self.background_field[{y}][{x}] = {pos.__class__.__name__}(' +
                            ', '.join(f'''{arg}={"'" if type(m:=eval(f"background_field[y][x].{arg}")) == str else ""}'''
                                      f'''{m}{"'" if type(m) == str else ""}'''
                                      for i, arg in enumerate(args)
                                      if defaults[i] != eval(f"background_field[y][x].{arg}")) + ')\n')
                pos = foreground_field[y][x]
                if pos is not None:
                    args_spec = getfullargspec(pos.__init__)
                    args = args_spec.args[1:]
                    defaults = args_spec.defaults
                    f.write(f'self.foreground_field[{y}][{x}] = {pos.__class__.__name__}(' +
                            ', '.join(f'''{arg}={"'" if type(m:=eval(f"foreground_field[y][x].{arg}")) == str else ""}'''
                                      f'''{m}{"'" if type(m) == str else ""}'''
                                      for i, arg in enumerate(args)
                                      if defaults[i] != eval(f"foreground_field[y][x].{arg}")) + ')\n')

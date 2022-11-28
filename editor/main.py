import pygame as pg
from blocks import Block, Ladder, Rope, Gold, Decoration


def draw(item, x, y, t=True):
    global a
    if item is not None and item.texture is not None:
        sprite = pg.image.load(item.texture)
        screen.blit(sprite, sprite.get_rect(x=x * a - (2 if t else 0), y=y * a - (14 if t else 0)))
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
    return 0 <= x <= w - 1 and 0 <= y <= h - 1


def place(item, x, y):
    field[y][x] = item


def delete(x, y):
    field[y][x] = None


# w = int(input('w: '))
# h = int(input('h: '))
w, h = 20, 20
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

while run:
    screen.fill((0, 0, 0))
    for event in pg.event.get():
        if event.type == pg.QUIT:
            run = False
        elif event.type == pg.MOUSEBUTTONDOWN:
            if event.button == 1:
                place_mode = True
                mouse_x, mouse_y = event.pos
                x, y = mouse_x // a, mouse_y // a
                if on_field(x, y):
                    place(items[selected_item], x, y)
            elif event.button == 3:
                delete_mode = True
                mouse_x, mouse_y = event.pos
                x, y = mouse_x // a, mouse_y // a
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
            elif event.button == 3:
                delete_mode = False
        elif event.type == pg.MOUSEMOTION:
            mouse_x, mouse_y = event.pos
            x, y = mouse_x // a, mouse_y // a
            if on_field(x, y):
                if delete_mode:
                    delete(x, y)
                elif place_mode:
                    place(items[selected_item], x, y)
        elif event.type == pg.KEYDOWN:
            if event.key == pg.K_w:
                cam_y -= 1
            elif event.key == pg.K_s:
                cam_y += 1
            elif event.key == pg.K_a:
                cam_x -= 1
            elif event.key == pg.K_d:
                cam_x += 1

    for y in range(h - 1, -1, -1):
        for x in range(w):
            draw(field[y][x], x - cam_x, y - cam_y)
    screen.fill((0, 0, 0), (0, 0, 64, 64))
    draw(items[selected_item], 0, 0, False)
    pg.display.flip()

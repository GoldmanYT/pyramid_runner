import pygame as pg
from blocks import Block, Ladder, Rope, Gold, Decoration, AnimatedDecoration, Entrance, Exit, Spawner, FakeBlock, Null
from background import Background
from enemy import Enemy1, Enemy2
from copy import deepcopy
from consts import A, BG_H


def draw(item, x, y, t=True, offset=False):
    global a, cam_x, cam_y, offset_x, offset_y, field
    if item is not None and not isinstance(item, Null) and item.image is not None:
        item.draw(screen,
                  x * a - (cam_x + 2 if t else 0) + (offset_x if offset else 0),
                  y * a - (cam_y + 14 if t else 0) + (offset_y if offset else 0))


def on_field(x, y):
    return w - 1 >= x >= 0 <= y <= h - 1


def place(container, item, selected_index, x, y):
    if edit_mode == 0 or edit_mode != 0 and isinstance(item[selected_index], (Decoration, AnimatedDecoration)):
        container[y][x] = item[selected_index]


def delete(container, x, y):
    container[y][x] = Null()


a = 50

pg.init()

screen = pg.display.set_mode((800, 600))
clock = pg.time.Clock()
run = True

items = []
linear_items = []
texture_names = ['data/block.png', 'data/block_diggable.png', 'data/ladder.png', 'data/rope.png', 'data/gold.png',
                 'data/decoration.png', 'data/entrance.png', 'data/exit.png', 'data/spawner.png',
                 'data/fake_block.png']
blocks = [Block(), Block(diggable=True), Ladder(), Rope(), Gold(), Decoration(), Entrance(), Exit(), Spawner(),
          FakeBlock()]
blocks[-1].player_inside = True

for texture_name, block in zip(texture_names, blocks, strict=True):
    temp = []
    image = pg.image.load(texture_name).convert_alpha()
    for i in range(image.get_size()[1] // A):
        copy = deepcopy(block)
        copy.image = image
        copy.crop_index = i
        temp.append(copy)
    items.append(temp)
    linear_items.extend(temp)

enemies_texture_names = ['data/enemy1.png', 'data/enemy2.png']
enemies = []
for texture_name, enemy_type in zip(enemies_texture_names, [Enemy1, Enemy2]):
    enemy = enemy_type()
    image = pg.image.load(texture_name).convert_alpha()
    copy = deepcopy(enemy)
    copy.image = image
    enemies.append(copy)
items.append(enemies)
linear_items.extend(enemies)

anim_decs = [AnimatedDecoration(crop_index=0, n_frames=53, n_anims=2),
             AnimatedDecoration(crop_index=1, n_frames=10, n_anims=8),
             AnimatedDecoration(crop_index=2, n_frames=37, n_anims=4)]
anim_decs_name = 'data/decoration_animated.png'
image = pg.image.load(anim_decs_name)
for i, anim_dec in enumerate(anim_decs):
    anim_decs[i].image = image
items.append(anim_decs)
linear_items.extend(anim_decs)

backgrounds = []
background_texture_name = 'data/background.png'
image = pg.image.load(background_texture_name).convert()
for i in range(image.get_size()[1] // BG_H):
    backgrounds.append(Background(image=image, crop_index=i))

font = pg.font.Font(None, 18)
edit_mode = 0
offset_x, offset_y = 10, -10
selected_item = 0
selected_index = 0
cam_x, cam_y = 0, 0
delete_mode = False
place_mode = False
move_mode = False
inventory_opened = False

background = None

s = input('Открыть? ')
if s == 'open':
    file_name = input('Введите имя файла: ')
    with open('levels/' + file_name) as f:
        exec(f.read().replace('self.', ''))
    if background is not None:
        background = background.crop_index
else:
    w, h = map(int, input('w h: ').split())

    field = [[items[0][0] if 0 in (x, y) or x == w - 1 or y == h - 1 else Null() for x in range(w)] for y in range(h)]
    background_field = [[Null() for _ in range(w)] for _ in range(h)]
    foreground_field = [[Null() for _ in range(w)] for _ in range(h)]

FPS = 167

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
                        background = (background + 1) % len(backgrounds)
                    else:
                        background = None
            elif event.key == pg.K_e:
                inventory_opened = not inventory_opened
    for y in range(h - 1, -1, -1):
        for x in range(w):
            draw(background_field[h - y - 1][x], x, y, offset=True)
    for y in range(h - 1, -1, -1):
        for x in range(w):
            draw(field[h - y - 1][x], x, y)
    for y in range(h - 1, -1, -1):
        for x in range(w):
            draw(foreground_field[h - y - 1][x], x, y)
    text = {
        0: 'Основной слой',
        1: 'Верхний слой',
        2: 'Нижний слой'
    }
    text = font.render(text.get(edit_mode), True, 'white')
    screen.fill((0, 0, 0), (0, 0, 64, 64))
    draw(items[selected_item][selected_index], 0, 0, False)
    screen.blit(text, (0, 0))
    clock.tick(FPS)
    pg.display.flip()
pg.quit()

gold_count = 0
file_name = input('Введите имя файла: ')
if file_name:
    with open('levels/' + file_name + '.txt', 'w') as f:
        f.write(f'{w} {h}\n')
        if background is not None:
            f.write(f'{background}')

    file_bytes = []
    for row in field:
        for pos in row:
            if isinstance(pos, Block):
                file_bytes.extend([pos.id, pos.crop_index, int(pos.diggable)])
            elif isinstance(pos, (Enemy1, Enemy2, Null)):
                file_bytes.append(pos.id)
            elif pos is None:
                file_bytes.append(Null.id)
            else:
                file_bytes.extend([pos.id, pos.crop_index])
    for row in background_field:
        for pos in row:
            if isinstance(pos, Block):
                file_bytes.extend([pos.id, pos.crop_index, int(pos.diggable)])
            elif isinstance(pos, (Enemy1, Enemy2, Null)):
                file_bytes.append(pos.id)
            elif pos is None:
                file_bytes.append(Null.id)
            else:
                file_bytes.extend([pos.id, pos.crop_index])
    for row in foreground_field:
        for pos in row:
            if isinstance(pos, Block):
                file_bytes.extend([pos.id, pos.crop_index, int(pos.diggable)])
            elif isinstance(pos, (Enemy1, Enemy2, Null)):
                file_bytes.append(pos.id)
            elif pos is None:
                file_bytes.append(Null.id)
            else:
                file_bytes.extend([pos.id, pos.crop_index])
    with open('levels/' + file_name + '.xxx', 'wb') as f:
        f.write(bytes(file_bytes))

from sqlite3 import connect

import pygame as pg

from blocks import Ladder, Rope, FakeBlock, Exit
from button import Button, dist
from player import Player
from field import Field
from consts import FPS, GLOBAL_OFFSET_X, GLOBAL_OFFSET_Y, BG_OFFSET_X, BG_OFFSET_Y, MENU_BTN_SIZE, START_BTN_POS, \
    RECORDS_BTN_POS, EXIT_BTN_POS, W, H, RECORDS_OK_BTN_POS, LEVELS_PLAY_BTN_POS, LEVELS_EXIT_BTN_POS, N_LEVELS, \
    LEVELS_W, LEVELS_POS, FRAME_W, LEVELS_MARGIN, START_N_FRAMES, GAME_OVER_FRAMES, RECORDS_COLOR, RECORDS_NUM_POS, \
    RECORDS_HOR_MARGIN, RECORDS_VER_MARGIN, RECORDS_SCORE_POS
from camera import Camera


class Game:
    def __init__(self, w, h):
        self.w, self.h = w, h
        pg.init()

        self.connection = connect('data/database.sqlite')
        cur = self.connection.cursor()
        self.level_paths = dict(cur.execute('''SELECT id, path FROM levels'''))

        # self.screen = pg.display.set_mode((w, h), pg.FULLSCREEN)
        self.screen = pg.display.set_mode((w, h))
        self.game_runs = False
        self.a = 50
        self.door_pos = None
        self.field = None
        self.background_field = None
        self.foreground_field = None
        self.player = None
        self.enemies = None
        self.spawners = None
        self.n_current_spawner = None
        self.background = None
        self.camera = None
        self.gold_count = None
        self.exit = None
        self.exit_pos = None
        self.win = False

        self.menu_opened = True
        self.bg = None
        self.start_btn = None
        self.exit_btn = None
        self.records_btn = None
        self.menu_buttons = []
        self.load_menu()

        self.records_opened = False
        self.records_bg = None
        self.records_ok_btn = None
        self.records = None
        self.load_records()

        self.levels_opened = False
        self.levels_bg = None
        self.levels_btn_play = None
        self.levels_btn_exit = None
        self.levels_frame = None
        self.levels = None
        self.selected_level = 0
        self.load_levels()

        self.paused = False
        self.start_opened = False
        self.start_bg = None
        self.start_frame = 0
        self.load_start()

        self.end_opened = False
        self.end_bg = None
        self.end_ok_btn = None
        self.load_end()

        self.game_over_opened = False
        self.game_over_frame = 0
        self.game_over_screen = None
        self.load_game_over()

        self.tr = None
        self.transition_runs = False
        self.alpha = 0
        self.alpha_direction = 1

        self.font = None
        self.load_font()

        clock = pg.time.Clock()
        run = True

        while run:
            clicked = False
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    run = False
                elif event.type == pg.MOUSEBUTTONDOWN:
                    clicked = True
                elif event.type == pg.KEYDOWN:
                    if event.key == pg.K_ESCAPE:
                        self.paused = not self.paused

            if self.menu_opened:
                self.draw_menu(clicked)
            elif self.records_opened:
                self.draw_records(clicked)
            elif self.levels_opened:
                self.draw_levels(clicked)
            elif self.start_opened:
                self.draw_start()
            elif self.end_opened:
                self.draw_end(clicked)
            elif self.game_over_opened:
                self.draw_game_over()
            elif self.game_runs:
                if not self.paused:
                    self.tick()
                self.draw()
            if self.transition_runs:
                self.transition()
            pg.display.flip()

            clock.tick(FPS)

    def load_font(self):
        self.font = pg.font.Font('data/font.ttf', 28)

    def load_game_over(self):
        self.game_over_screen = pg.image.load('data/game_over.png').convert_alpha()

    def draw_game_over(self):
        self.screen.blit(self.game_over_screen, (0, 0))
        self.game_over_frame += 1
        if self.game_over_frame == GAME_OVER_FRAMES:
            self.tr = 1
            self.transition_runs = True
            self.game_over_frame = 0

    def load_end(self):
        self.end_bg = pg.image.load('data/level_end.png').convert_alpha()
        btn_im = pg.image.load('data/ok.png').convert_alpha()
        w, h = btn_im.get_size()
        btn_bg = btn_im.subsurface((w // 2, 0, w // 2, h))
        btn_im = btn_im.subsurface((0, 0, w // 2, h))
        self.end_ok_btn = Button(btn_im, btn_bg, RECORDS_OK_BTN_POS)

    def draw_end(self, clicked):
        self.screen.blit(self.end_bg, (0, 0))
        x, y = pg.mouse.get_pos()
        self.end_ok_btn.draw(self.screen)
        pressed = self.end_ok_btn.update(x, y, clicked)
        if pressed and self.tr is None:
            self.tr = 2
            self.transition_runs = True

    def load_start(self):
        self.start_bg = pg.image.load('data/level_start.png').convert_alpha()

    def draw_start(self):
        self.screen.blit(self.start_bg, (0, 0))
        self.start_frame += 1
        if self.start_frame == START_N_FRAMES:
            self.start_frame = 0
            self.tr = 3
            self.transition_runs = True

    def load_levels(self):
        self.levels_bg = pg.image.load('data/levels_bg.png').convert_alpha()
        self.levels_frame = pg.image.load('data/level_frame.png').convert_alpha()
        levels_buttons = pg.image.load('data/levels_buttons.png')
        w, h = levels_buttons.get_size()
        btn1_im = levels_buttons.subsurface((0, 0, w // 2, h // 2))
        btn1_bg = levels_buttons.subsurface((w // 2, 0, w // 2, h // 2))
        btn2_im = levels_buttons.subsurface((0, h // 2, w // 2, h // 2))
        btn2_bg = levels_buttons.subsurface((w // 2, h // 2, w // 2, h // 2))
        self.levels_btn_play = Button(btn1_im, btn1_bg, LEVELS_PLAY_BTN_POS)
        self.levels_btn_exit = Button(btn2_im, btn2_bg, LEVELS_EXIT_BTN_POS)
        levels_im = pg.image.load('data/levels.png').convert_alpha()
        w, h = levels_im.get_size()
        self.levels = []
        for i in range(N_LEVELS):
            x, y = LEVELS_POS
            btn = Button(levels_im.subsurface(i * LEVELS_W, 0, LEVELS_W, h),
                         pg.Surface((LEVELS_W, h)), (x + i * LEVELS_MARGIN, y))
            self.levels.append(btn)

    def draw_levels(self, clicked):
        self.screen.blit(self.levels_bg, (0, 0))
        x, y = pg.mouse.get_pos()
        self.levels_btn_play.draw(self.screen)
        pressed = self.levels_btn_play.update(x, y, clicked)
        if pressed and self.tr is None:
            self.tr = 4
            self.transition_runs = True
        self.levels_btn_exit.draw(self.screen)
        pressed = self.levels_btn_exit.update(x, y, clicked)
        if pressed and self.tr is None:
            self.tr = 1
            self.transition_runs = True
        for i, level in enumerate(self.levels):
            level.draw(self.screen)
            pressed = level.update(x, y, clicked)
            if pressed:
                self.selected_level = i
        x, y = LEVELS_POS
        self.screen.blit(self.levels_frame, (x + self.selected_level * LEVELS_MARGIN - FRAME_W, y - FRAME_W))

    def load_records(self):
        self.records_bg = pg.image.load('data/records.png').convert_alpha()
        btn_im = pg.image.load('data/ok.png').convert_alpha()
        w, h = btn_im.get_size()
        btn_bg = btn_im.subsurface((w // 2, 0, w // 2, h))
        btn_im = btn_im.subsurface((0, 0, w // 2, h))
        self.records_ok_btn = Button(btn_im, btn_bg, RECORDS_OK_BTN_POS)

    def load_records_score(self):
        cur = self.connection.cursor()
        result = cur.execute('''SELECT name, score FROM records''').fetchall()
        result.sort(key=lambda x: -x[1])
        self.records = result[:5]
        if len(self.records) < 5:
            self.records.extend([('Нет имени', 0)] * (5 - len(self.records)))
        for i, x in enumerate(self.records):
            self.records[i] = list(self.records[i])
            self.records[i][1] = str(x[1])

    def draw_records(self, clicked):
        self.screen.blit(self.records_bg, (0, 0))
        x, y = pg.mouse.get_pos()
        self.records_ok_btn.draw(self.screen)
        pressed = self.records_ok_btn.update(x, y, clicked)
        if pressed and self.tr is None:
            self.tr = 1
            self.transition_runs = True
        for i in range(5):
            text = self.font.render(f'{i + 1}.', True, RECORDS_COLOR)
            w, h = text.get_size()
            x, y = RECORDS_NUM_POS
            self.screen.blit(text, (x - w, y - h + i * RECORDS_VER_MARGIN))
            text = self.font.render(self.records[i][0], True, RECORDS_COLOR)
            w, h = text.get_size()
            self.screen.blit(text, (x + RECORDS_HOR_MARGIN, y - h + i * RECORDS_VER_MARGIN))
            text = self.font.render(self.records[i][1], True, RECORDS_COLOR)
            x, y = RECORDS_SCORE_POS
            w, h = text.get_size()
            self.screen.blit(text, (x - w, y - h + i * RECORDS_VER_MARGIN))

    def load_menu(self):
        self.bg = pg.image.load('data/menu_bg.png').convert_alpha()
        btn_im = pg.image.load('data/menu_buttons.png').convert_alpha()
        btn_bg = btn_im.subsurface((0, 0, MENU_BTN_SIZE, MENU_BTN_SIZE))
        btn1_im = btn_im.subsurface((0, MENU_BTN_SIZE, MENU_BTN_SIZE, MENU_BTN_SIZE))
        btn2_im = btn_im.subsurface((MENU_BTN_SIZE, 0, MENU_BTN_SIZE, MENU_BTN_SIZE))
        btn3_im = btn_im.subsurface((MENU_BTN_SIZE, MENU_BTN_SIZE, MENU_BTN_SIZE, MENU_BTN_SIZE))
        self.start_btn = Button(btn1_im, btn_bg, START_BTN_POS)
        self.exit_btn = Button(btn2_im, btn_bg, EXIT_BTN_POS)
        self.records_btn = Button(btn3_im, btn_bg, RECORDS_BTN_POS)
        self.menu_buttons = [self.start_btn, self.exit_btn, self.records_btn]

    def draw_menu(self, clicked):
        self.screen.fill((0, 0, 0))
        self.screen.blit(self.bg, (0, 0))
        pressed_button = None
        x, y = pg.mouse.get_pos()
        for button in self.menu_buttons:
            button.draw(self.screen)
            pressed = button.update(x, y, clicked)
            if pressed:
                pressed_button = button
        if pressed_button == self.exit_btn:
            pg.quit()
            exit()
        if pressed_button == self.records_btn and self.tr is None:
            self.tr = 0
            self.transition_runs = True
        if pressed_button == self.start_btn and self.tr is None:
            self.tr = 2
            self.transition_runs = True

    def transition(self):
        if self.alpha == 0:
            if self.alpha_direction == 1:
                self.menu_opened, self.start_opened, self.end_opened, self.levels_opened, \
                self.records_opened, self.game_over_opened, self.game_runs = [False] * 7
            else:
                self.tr = None
                self.transition_runs = False
                self.alpha_direction = 1
                return
        black_screen = pg.Surface((W, H))
        self.alpha += 5 * self.alpha_direction
        black_screen.set_alpha(self.alpha)
        if self.alpha == 255:
            self.alpha_direction = -1
            if self.tr == 0:
                self.load_records_score()
                self.records_opened = True
            elif self.tr == 1:
                self.menu_opened = True
            elif self.tr == 2:
                self.levels_opened = True
            elif self.tr == 3:
                self.start_opened = True
            elif self.tr == 4:
                self.game_runs = True
                self.load_level(self.level_paths.get(self.selected_level + 1))
            elif self.tr == 5:
                self.end_opened = True
            elif self.tr == 6:
                self.game_over_opened = True
        self.screen.blit(black_screen, (0, 0))

    def load_level(self, file_name):
        self.field = Field(filename=file_name)
        self.background_field = self.field.background_field
        self.foreground_field = self.field.foreground_field
        x, y = self.field.get_player_pos()
        self.player = Player(x, y, field=self.field, image=pg.image.load('data/player.png').convert_alpha())
        self.enemies = self.field.get_enemies()
        self.player.entities = self.enemies
        for enemy in self.enemies:
            enemy.entities = self.enemies
            enemy.set_field(self.field)
        self.background = self.field.get_background()
        self.camera = Camera(self.a * self.field.w, self.a * self.field.h, self.w, self.h)
        self.gold_count = self.field.get_gold_count()
        self.exit = self.field.get_exit()
        self.exit.v = 1
        self.win = False
        self.player.alive = True
        self.exit_pos = self.field.get_exit_pos()
        self.spawners = self.field.get_spawners()
        if self.spawners:
            self.n_current_spawner = 0
        if self.background is not None:
            self.background.level_w = self.a * self.field.w - self.w
            self.background.level_h = self.a * self.field.h - self.h
            self.background.w = self.w
            self.background.h = self.h

    def tick(self):
        keys = pg.key.get_pressed()

        if not (self.gold_count - self.player.collected_gold) and self.exit is not None and not self.exit.opened:
            self.exit.open()
        if self.player.pos() == self.exit_pos and self.exit.opened:
            self.exit.v = 0.1
            self.player.x, self.player.y = self.exit_pos
            self.player.step_x, self.player.step_y = 0, 0
            self.win = True
            if self.exit.door_pos <= 0:
                self.tr = 5
                self.transition_runs = True

        if self.win:
            self.exit.door_close()
            return

        if keys[pg.K_z]:
            self.player.dig('left')
        elif keys[pg.K_x]:
            self.player.dig('right')

        directions = []
        if keys[pg.K_UP] and not keys[pg.K_DOWN]:
            directions.append('up')
        if keys[pg.K_DOWN] and not keys[pg.K_UP]:
            directions.append('down')
        if keys[pg.K_LEFT] and not keys[pg.K_RIGHT]:
            directions.append('left')
        if keys[pg.K_RIGHT] and not keys[pg.K_LEFT]:
            directions.append('right')
        self.player.update(directions if directions else None)
        x, y = self.player.pos()
        if self.exit_pos is not None and self.exit.opened:
            x1, y1 = self.exit_pos
            r = dist(x, y, x1, y1)
            if r <= 2:
                self.exit.door_open()
            else:
                self.exit.door_close()

        deleted = []
        for enemy in self.enemies:
            if not enemy.alive:
                deleted.append(enemy)
                continue
            enemy.update(player=self.player)
        for enemy in deleted:
            self.enemies.remove(enemy)
            if self.spawners:
                spawner = self.spawners[self.n_current_spawner]
                self.n_current_spawner = (self.n_current_spawner + 1) % len(self.spawners)
                spawner.spawn(enemy)

        for row in self.field:
            for block in row:
                if isinstance(block, FakeBlock):
                    block.update(self.player)

        for spawner in self.spawners:
            enemy = spawner.update()
            if enemy is not None:
                self.enemies.append(enemy)

    def draw(self):
        self.screen.fill((0, 0, 0))
        camera_x, camera_y = self.camera.pos(
            self.player.x * self.a + self.player.step_x * self.a // self.player.n_steps + self.a // 2,
            (self.field.h - self.player.y - 1) * self.a -
            self.player.step_y * self.a // self.player.n_steps + self.a // 2)

        if self.background is not None:
            self.background.draw(self.screen, 0, 0, camera_x, camera_y)

        for y in range(self.field.h):
            for x in range(self.field.w):
                pos = self.background_field[y][x]
                if pos is not None:
                    pos.draw(
                        self.screen,
                        x * self.a + GLOBAL_OFFSET_X + BG_OFFSET_X + camera_x,
                        (self.field.h - y - 1) * self.a + GLOBAL_OFFSET_Y + BG_OFFSET_Y + camera_y
                    )

        for y in range(self.field.h):
            for x in range(self.field.w):
                pos = self.field[y][x]
                if pos is not None:
                    if isinstance(pos, Ladder):
                        pos.draw(
                            self.screen,
                            x * self.a + GLOBAL_OFFSET_X + camera_x,
                            (self.field.h - y - 1) * self.a + GLOBAL_OFFSET_Y + camera_y,
                            self.field[y + 1][x], self.field[y - 1][x]
                        )
                    elif isinstance(pos, Rope):
                        pos.draw(
                            self.screen,
                            x * self.a + GLOBAL_OFFSET_X + camera_x,
                            (self.field.h - y - 1) * self.a + GLOBAL_OFFSET_Y + camera_y,
                            self.field[y][x - 1], self.field[y][x + 1]
                        )
                    else:
                        if isinstance(self.player.inside(), FakeBlock) and isinstance(pos, FakeBlock) and \
                                pos.player_inside:
                            self.draw_player(camera_x, camera_y)
                        if isinstance(pos, Exit) and self.win:
                            self.door_pos = (x * self.a + GLOBAL_OFFSET_X + camera_x,
                                             (self.field.h - y - 1) * self.a + GLOBAL_OFFSET_Y + camera_y)
                        pos.draw(
                            self.screen,
                            x * self.a + GLOBAL_OFFSET_X + camera_x,
                            (self.field.h - y - 1) * self.a + GLOBAL_OFFSET_Y + camera_y
                        )
        if not isinstance(self.player.inside(), FakeBlock):
            self.draw_player(camera_x, camera_y)
        for enemy in self.enemies:
            x, step_x, y, step_y = enemy.x, enemy.step_x, enemy.y, enemy.step_y
            enemy.draw(
                self.screen,
                x * self.a + step_x * self.a // self.player.n_steps + GLOBAL_OFFSET_X + camera_x,
                (self.field.h - y - 1) * self.a - step_y * self.a // self.player.n_steps + GLOBAL_OFFSET_Y + camera_y
            )

        for y in range(self.field.h):
            for x in range(self.field.w):
                pos = self.foreground_field[y][x]
                if pos is not None:
                    pos.draw(
                        self.screen,
                        x * self.a + GLOBAL_OFFSET_X + camera_x,
                        (self.field.h - y - 1) * self.a + GLOBAL_OFFSET_Y + camera_y
                    )

    def draw_player(self, camera_x, camera_y):
        x, step_x, y, step_y = self.player.x, self.player.step_x, self.player.y, self.player.step_y
        if not self.player.alive:
            self.tr = 6
            self.transition_runs = True
            return
        self.player.draw(
            self.screen, x * self.a + step_x * self.a // self.player.n_steps + GLOBAL_OFFSET_X + camera_x +
            self.win * BG_OFFSET_X,
            (self.field.h - y - 1) * self.a - step_y * self.a // self.player.n_steps + GLOBAL_OFFSET_Y + camera_y +
            self.win * BG_OFFSET_Y
        )
        if self.win:
            self.exit.draw_door(self.screen, *self.door_pos)

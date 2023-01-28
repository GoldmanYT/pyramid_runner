from random import choice
from sqlite3 import connect

import pygame as pg

from blocks import Ladder, Rope, FakeBlock, Exit, Gold
from button import Button, dist
from enemy import Enemy1
from player import Player
from field import Field
from consts import FPS, GLOBAL_OFFSET_X, GLOBAL_OFFSET_Y, BG_OFFSET_X, BG_OFFSET_Y, MENU_BTN_SIZE, START_BTN_POS, \
    RECORDS_BTN_POS, EXIT_BTN_POS, W, H, RECORDS_OK_BTN_POS, LEVELS_PLAY_BTN_POS, LEVELS_EXIT_BTN_POS, N_LEVELS, \
    LEVELS_W, LEVELS_POS, FRAME_W, LEVELS_MARGIN, START_N_FRAMES, GAME_OVER_FRAMES, RECORDS_COLOR, RECORDS_NUM_POS, \
    RECORDS_HOR_MARGIN, RECORDS_VER_MARGIN, RECORDS_SCORE_POS, END_TEXT_COLOR, END_TEXT1_POS, END_TEXT2_POS, \
    END_TEXT3_POS, END_TEXT4_POS, END_TEXT5_POS, END_LINE_POS, END_GOLD_POS, END_ENEMY_POS, RECORDS_TYPING_COLOR, \
    RECORDS_YOUR_SCORE_POS, RECORDS_TYPING_FRAMES, START_LEVEL_POS, START_LIVES_POS, START_SCORE_POS, START_TEXT_COLOR
from camera import Camera


class Game:
    def __init__(self, w, h):
        self.w, self.h = w, h
        pg.mixer.pre_init()
        pg.init()

        self.connection = connect('data/database.sqlite')
        cur = self.connection.cursor()
        self.level_paths = dict(cur.execute('''SELECT id, path FROM levels'''))

        # self.screen = pg.display.set_mode((w, h), pg.FULLSCREEN)
        self.screen = pg.display.set_mode((w, h))
        pg.display.set_icon(pg.image.load('data/game.ico'))
        pg.display.set_caption('Тайны пирамид')
        self.game_runs = False
        self.a = 50
        self.door_pos = None
        self.field = None
        self.background_field = None
        self.foreground_field = None
        self.player = None
        self.prev_state = None
        self.enemies = None
        self.spawners = None
        self.n_current_spawner = None
        self.background = None
        self.camera = None
        self.gold_count = None
        self.exit = None
        self.exit_pos = None
        self.win = False
        self.enemies_killed = 0
        self.score = 0
        self.lives = 5
        self.previous_score = 0

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
        self.records_typing_frame = 0
        self.records_typing_index = None
        self.name = ''
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
        self.load_pause()

        self.start_opened = False
        self.start_bg = None
        self.start_frame = 0
        self.load_start()

        self.end_opened = False
        self.end_bg = None
        self.end_ok_btn = None
        self.end_gold = None
        self.end_enemy = None
        self.line = None
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

        self.load_sounds()
        self.load_main_menu_music()

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
                    if event.key == pg.K_ESCAPE and self.game_runs:
                        self.paused = not self.paused
                    if self.records_typing_index is not None:
                        if event.key == pg.K_BACKSPACE:
                            self.name = self.name[:-1]
                            self.typing.play()
                        elif len(self.name) < 16:
                            self.name += event.unicode
                            self.typing.play()

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

    def load_sounds(self):
        self.block_dig = pg.mixer.Sound('data/block_dig.ogg')
        self.block_restore = pg.mixer.Sound('data/block_restore.wav')
        self.click = pg.mixer.Sound('data/click.wav')
        self.door_close = pg.mixer.Sound('data/door_closed.wav')
        self.door_open = pg.mixer.Sound('data/door_opened.wav')
        self.enemy_died = pg.mixer.Sound('data/enemy_died.wav')
        self.exit_door_opened = pg.mixer.Sound('data/exit_door_opened.wav')
        self.falling = pg.mixer.Sound('data/falling.ogg')
        self.gold1 = pg.mixer.Sound('data/gold1.ogg')
        self.gold2 = pg.mixer.Sound('data/gold2.ogg')
        self.laddering = pg.mixer.Sound('data/laddering.wav')
        self.level_completed = pg.mixer.Sound('data/level_completed.ogg')
        self.level_select = pg.mixer.Sound('data/level_select.wav')
        self.pause_click = pg.mixer.Sound('data/pause_click.ogg')
        self.player_died = pg.mixer.Sound('data/player_died.wav')
        self.roping = pg.mixer.Sound('data/roping.wav')
        self.steps = pg.mixer.Sound('data/steps.wav')
        self.typing = pg.mixer.Sound('data/typing.wav')

    def load_level_music(self, level):
        d = {
            0: 'data/music1.ogg',
            1: 'data/music2.ogg',
            2: 'data/music3.mp3'
        }
        pg.mixer.music.load(d.get(level, d[0]))
        pg.mixer.music.play(-1)

    def load_main_menu_music(self):
        pg.mixer.music.load('data/main_menu_music.mp3')
        pg.mixer.music.play(-1)

    def load_levels_music(self):
        pg.mixer.music.load('data/levels_music.ogg')
        pg.mixer.music.play(-1)

    def load_game_over_music(self):
        pg.mixer.music.load('data/game_over_music.mp3')
        pg.mixer.music.play()

    def load_end_music(self):
        pg.mixer.music.load('data/end_music.ogg')
        pg.mixer.music.play(-1)

    def load_records_music(self):
        pg.mixer.music.load('data/records_music.ogg')
        pg.mixer.music.play(-1)

    def load_start_music(self):
        pg.mixer.music.load('data/start_music.ogg')
        pg.mixer.music.play()

    def load_pause(self):
        pass

    def save_score(self, score=None):
        self.load_records_score()
        if score is not None:
            if not self.name:
                self.name = 'Нет имени'
            self.records_typing_index = None
            cur = self.connection.cursor()
            cur.execute(f'''INSERT INTO records(name, score) VALUES ("{self.name}", {score})''')
            self.connection.commit()
            return
        for i, (name, score) in enumerate(self.records):
            score = int(score)
            if score < self.score or score == 0 != self.score:
                self.records_typing_index = i
                self.records.insert(self.records_typing_index, ('', f'{self.score}'))
                break

    def load_font(self):
        self.font = pg.font.Font('data/font.ttf', 28)

    def load_game_over(self):
        self.game_over_screen = pg.image.load('data/game_over.png').convert_alpha()

    def draw_game_over(self):
        self.screen.blit(self.game_over_screen, (0, 0))
        self.game_over_frame += 1
        if self.game_over_frame == GAME_OVER_FRAMES:
            self.save_score()
            if self.records_typing_index is None:
                self.tr = 1
            else:
                self.tr = 0
            self.transition_runs = True
            self.game_over_frame = 0

    def compute_score(self):
        self.previous_score = self.score
        gold_score = self.player.collected_gold * 100
        enemy_score = self.enemies_killed * 100
        new_score = gold_score + enemy_score
        self.score += new_score

    def load_end(self):
        self.end_bg = pg.image.load('data/level_end.png').convert_alpha()
        btn_im = pg.image.load('data/ok.png').convert_alpha()
        w, h = btn_im.get_size()
        btn_bg = btn_im.subsurface((w // 2, 0, w // 2, h))
        btn_im = btn_im.subsurface((0, 0, w // 2, h))
        self.end_ok_btn = Button(btn_im, btn_bg, RECORDS_OK_BTN_POS)
        self.line = pg.image.load('data/line.png').convert_alpha()
        enemy_im = pg.image.load('data/enemy1.png').convert_alpha()
        self.end_enemy = Enemy1(image=enemy_im)
        gold_im = pg.image.load('data/gold.png').convert_alpha()
        self.end_gold = Gold(gold_im)

    def draw_end(self, clicked):
        self.screen.blit(self.end_bg, (0, 0))
        x, y = pg.mouse.get_pos()
        self.end_ok_btn.draw(self.screen)
        pressed = self.end_ok_btn.update(x, y, clicked)
        gold_score = self.player.collected_gold * 100
        enemy_score = self.enemies_killed * 100
        new_score = gold_score + enemy_score
        s1 = f'УРОВЕНЬ  {self.selected_level + 1}'
        s2 = f'{self.player.collected_gold}  x  100  =  {gold_score}'
        s3 = f'{self.enemies_killed}  x  100  =  {enemy_score}'
        s4 = f'ИТОГО:  {new_score}'
        s5 = f'ВАШИ ОЧКИ:  {self.previous_score}  +  {new_score}  =  {self.previous_score + new_score}'
        text1 = self.font.render(s1, True, END_TEXT_COLOR)
        text2 = self.font.render(s2, True, END_TEXT_COLOR)
        text3 = self.font.render(s3, True, END_TEXT_COLOR)
        text4 = self.font.render(s4, True, END_TEXT_COLOR)
        text5 = self.font.render(s5, True, END_TEXT_COLOR)
        self.screen.blit(self.line, END_LINE_POS)
        self.end_gold.draw(self.screen, *END_GOLD_POS)
        self.end_enemy.draw(self.screen, *END_ENEMY_POS)
        for text, coord in zip((text1, text2, text3, text4, text5),
                               (END_TEXT1_POS, END_TEXT2_POS, END_TEXT3_POS, END_TEXT4_POS, END_TEXT5_POS)):
            w, h = text.get_size()
            x, y = coord
            if text in (text2, text3):
                self.screen.blit(text, (x, y - h))
            else:
                self.screen.blit(text, (x - w // 2, y - h))
        if pressed and self.tr is None:
            self.tr = 2
            self.transition_runs = True
            self.click.play()

    def load_start(self):
        self.start_bg = pg.image.load('data/level_start.png').convert_alpha()

    def draw_start(self):
        self.screen.blit(self.start_bg, (0, 0))
        self.start_frame += 1
        d = {
            START_LEVEL_POS: f'Уровень  {self.selected_level + 1}',
            START_LIVES_POS: f'Жизни    {self.lives}',
            START_SCORE_POS: f'Очки     {self.score}',
        }
        for x, y in (START_LEVEL_POS, START_LIVES_POS, START_SCORE_POS):
            text = self.font.render(d.get((x, y)), True, START_TEXT_COLOR)
            w, h = text.get_size()
            self.screen.blit(text, (x - w // 2, y - h))
        if self.start_frame == START_N_FRAMES:
            self.start_frame = 0
            self.tr = 4
            self.load_level(self.level_paths.get(self.selected_level + 1))
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
            self.tr = 3
            self.transition_runs = True
            self.click.play()
        self.levels_btn_exit.draw(self.screen)
        pressed = self.levels_btn_exit.update(x, y, clicked)
        if pressed and self.tr is None:
            self.save_score()
            if self.records_typing_index is None:
                self.tr = 1
            else:
                self.tr = 0
            self.transition_runs = True
            self.click.play()
        for i, level in enumerate(self.levels):
            level.draw(self.screen)
            pressed = level.update(x, y, clicked)
            if pressed:
                self.selected_level = i
                self.level_select.play()
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
            if self.records_typing_index is not None:
                self.save_score(self.score)
            self.tr = 1
            self.transition_runs = True
            self.click.play()
        for i in range(5):
            if self.records_typing_index == i:
                text = self.font.render(f'{i + 1}.', True, RECORDS_TYPING_COLOR)
            else:
                text = self.font.render(f'{i + 1}.', True, RECORDS_COLOR)
            w, h = text.get_size()
            x, y = RECORDS_NUM_POS
            self.screen.blit(text, (x - w, y - h + i * RECORDS_VER_MARGIN))
            if self.records_typing_index == i:
                s = ('_' if self.records_typing_frame // RECORDS_TYPING_FRAMES % 2 else '')
                text = self.font.render(self.name + s, True, RECORDS_TYPING_COLOR)
            else:
                text = self.font.render(self.records[i][0], True, RECORDS_COLOR)
            w, h = text.get_size()
            self.screen.blit(text, (x + RECORDS_HOR_MARGIN, y - h + i * RECORDS_VER_MARGIN))
            if self.records_typing_index == i:
                text = self.font.render(f'{self.score}', True, RECORDS_TYPING_COLOR)
            else:
                text = self.font.render(self.records[i][1], True, RECORDS_COLOR)
            x, y = RECORDS_SCORE_POS
            w, h = text.get_size()
            self.screen.blit(text, (x - w, y - h + i * RECORDS_VER_MARGIN))
            if self.records_typing_index == i:
                text = self.font.render(f'ВАШИ  ОЧКИ:  {self.score}', True, RECORDS_TYPING_COLOR)
                x, y = RECORDS_YOUR_SCORE_POS
                w, h = text.get_size()
                self.screen.blit(text, (x - w // 2, y - h))
                self.records_typing_frame += 1
                self.records_typing_frame %= 2 * RECORDS_TYPING_FRAMES

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
                self.click.play()
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
                self.open_records()
            elif self.tr == 1:
                self.open_menu()
            elif self.tr == 2:
                self.open_levels()
            elif self.tr == 3:
                self.open_start()
            elif self.tr == 4:
                self.open_game()
            elif self.tr == 5:
                self.open_end()
            elif self.tr == 6:
                self.open_game_over()
        self.screen.blit(black_screen, (0, 0))

    def open_records(self):
        self.save_score()
        self.records_opened = True
        self.load_records_music()

    def open_menu(self):
        self.menu_opened = True
        self.score = 0
        self.lives = 5
        self.load_main_menu_music()

    def open_levels(self):
        self.levels_opened = True
        self.load_levels_music()

    def open_start(self):
        self.start_opened = True
        self.load_start_music()

    def open_game(self):
        self.game_runs = True
        self.load_level(self.level_paths.get(self.selected_level + 1))
        self.load_level_music(self.selected_level)

    def open_end(self):
        self.compute_score()
        self.end_opened = True
        self.load_end_music()

    def open_game_over(self):
        self.game_over_opened = True
        self.load_game_over_music()

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
        self.win = False
        self.enemies_killed = 0
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

    def stop_moving_sounds(self):
        self.falling.stop()
        self.steps.stop()
        self.laddering.stop()
        self.roping.stop()

    def tick(self):
        keys = pg.key.get_pressed()

        if not (self.gold_count - self.player.collected_gold) and self.exit is not None and not self.exit.opened:
            self.exit.open()
            self.exit_door_opened.play()
        if self.player.pos() == self.exit_pos and self.exit.opened:
            self.exit.v = 0.2
            self.player.x, self.player.y = self.exit_pos
            self.player.step_x, self.player.step_y = 0, 0
            if not self.win:
                self.level_completed.play()
            self.win = True
            if self.exit.door_pos <= 0:
                self.tr = 5
                self.transition_runs = True

        if self.win:
            self.exit.door_close()
            self.stop_moving_sounds()
            return

        if keys[pg.K_z]:
            if self.player.dig('left'):
                self.block_dig.play()
        elif keys[pg.K_x]:
            if self.player.dig('right'):
                self.block_dig.play()

        directions = []
        if keys[pg.K_UP] and not keys[pg.K_DOWN]:
            directions.append('up')
        if keys[pg.K_DOWN] and not keys[pg.K_UP]:
            directions.append('down')
        if keys[pg.K_LEFT] and not keys[pg.K_RIGHT]:
            directions.append('left')
        if keys[pg.K_RIGHT] and not keys[pg.K_LEFT]:
            directions.append('right')
        gold_collected, restored = self.player.update(directions if directions else None)
        if gold_collected:
            choice((self.gold1, self.gold2)).play()
        if restored:
            self.block_restore.play()

        state = self.player.check_state().split('_')[0]
        state_sounds = {
            'falling': self.falling,
            'roping': self.roping,
            'laddering': self.laddering,
            'going': self.steps
        }
        if self.player.moved:
            if self.prev_state != state:
                if state_sounds.get(self.prev_state) is not None:
                    state_sounds.get(self.prev_state).stop()
                if state_sounds.get(state) is not None:
                    state_sounds.get(state).play(-1)
        elif state_sounds.get(self.prev_state) is not None:
            state_sounds.get(self.prev_state).stop()
        self.prev_state = state

        x, y = self.player.pos()
        if self.exit_pos is not None and self.exit.opened:
            x1, y1 = self.exit_pos
            r = dist(x, y, x1, y1)
            if r <= 2:
                if self.exit.door_open():
                    self.door_open.play()
            else:
                if self.exit.door_close():
                    self.door_close.play()

        deleted = []
        for enemy in self.enemies:
            if not enemy.alive:
                deleted.append(enemy)
                continue
            enemy.update(player=self.player)
        for enemy in deleted:
            self.enemies.remove(enemy)
            self.enemies_killed += 1
            self.enemy_died.play()
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
            self.lives -= 1
            self.player_died.play()
            self.stop_moving_sounds()
            if not self.lives:
                self.save_score()
                self.tr = 6
            else:
                self.tr = 3
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

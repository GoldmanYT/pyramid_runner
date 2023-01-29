from random import choice
from sqlite3 import connect

import pygame as pg

from blocks import Ladder, Rope, FakeBlock, Gold
from button import Button, dist
from enemy import Enemy1
from player import Player
from field import Field
from consts import FPS, GLOBAL_OFFSET_X, GLOBAL_OFFSET_Y, BG_OFFSET_X, BG_OFFSET_Y, MENU_BTN_SIZE, START_BTN_POS, \
    RECORDS_BTN_POS, EXIT_BTN_POS, W, H, RECORDS_OK_BTN_POS, LEVELS_PLAY_BTN_POS, LEVELS_EXIT_BTN_POS, N_LEVELS, \
    LEVELS_W, LEVELS_POS, FRAME_W, LEVELS_MARGIN, START_N_FRAMES, GAME_OVER_FRAMES, RECORDS_COLOR, RECORDS_NUM_POS, \
    RECORDS_HOR_MARGIN, RECORDS_VER_MARGIN, RECORDS_SCORE_POS, END_TEXT_COLOR, END_TEXT1_POS, END_TEXT2_POS, \
    END_TEXT3_POS, END_TEXT4_POS, END_TEXT5_POS, END_LINE_POS, END_GOLD_POS, END_ENEMY_POS, RECORDS_TYPING_COLOR, \
    RECORDS_YOUR_SCORE_POS, RECORDS_TYPING_FRAMES, START_LEVEL_POS, START_LIVES_POS, START_SCORE_POS, \
    START_TEXT_COLOR, DIED_N_FRAMES, PAUSE_BTN_CONTINUE_POS, PAUSE_BTN_H, PAUSE_BTN_RESTART_POS, \
    PAUSE_BTN_EXIT_POS, PAUSE_N_FRAMES, PAUSE_BG_COLOR, PAUSE_BG_ALPHA, BLACK, PAUSE_STRIPE_H, \
    EXIT_DOOR_OPENED_N_FRAMES, EXIT_DOOR_OPENED_POS, WHITE, GOLD_COUNT_POS, GOLD_COUNT_TEXT_DY
from camera import Camera


def load_level_music(level):
    d = {
        0: 'data/music1.ogg',
        1: 'data/music2.ogg',
        2: 'data/music3.mp3'
    }
    pg.mixer.music.load(d.get(level, d[0]))
    pg.mixer.music.play(-1)


def load_main_menu_music():
    pg.mixer.music.load('data/main_menu_music.mp3')
    pg.mixer.music.play(-1)


def load_levels_music():
    pg.mixer.music.load('data/levels_music.ogg')
    pg.mixer.music.play(-1)


def load_game_over_music():
    pg.mixer.music.load('data/game_over_music.mp3')
    pg.mixer.music.play()


def load_end_music():
    pg.mixer.music.load('data/end_music.ogg')
    pg.mixer.music.play(-1)


def load_records_music():
    pg.mixer.music.load('data/records_music.ogg')
    pg.mixer.music.play(-1)


def load_start_music():
    pg.mixer.music.load('data/start_music.ogg')
    pg.mixer.music.play()


class Game:
    def __init__(self, w, h):
        self.w, self.h = w, h
        pg.mixer.pre_init()
        pg.init()

        self.connection = connect('data/database.sqlite')
        cur = self.connection.cursor()
        self.level_paths = dict(cur.execute('''SELECT id, path FROM levels'''))

        self.full_screen = True
        self.screen = pg.display.set_mode((w, h), pg.FULLSCREEN)
        pg.display.set_icon(pg.image.load('data/game.ico'))
        pg.display.set_caption('Тайны пирамид')
        self.game_runs = False
        self.a = 50
        self.entrance_door_pos = None
        self.exit_door_pos = None
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
        self.entrance = None
        self.entrance_pos = None
        self.exit = None
        self.exit_pos = None
        self.win = False
        self.can_move = False
        self.died_frames = 0
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
        self.pause_continue_btn = None
        self.pause_restart_btn = None
        self.pause_exit_btn = None
        self.pause_frame = 0
        self.pause_anim_direction = 1
        self.load_pause()

        self.exit_door_opened_frame = 0
        self.exit_opened = None
        self.load_exit_door_opened()

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

        self.gold_count_im = None
        self.load_gold_count()

        self.block_dig = None
        self.block_restore = None
        self.click = None
        self.door_close = None
        self.door_open = None
        self.enemy_died = None
        self.exit_door_opened = None
        self.falling = None
        self.gold1 = None
        self.gold2 = None
        self.laddering = None
        self.level_completed = None
        self.level_select = None
        self.pause_click = None
        self.player_died = None
        self.roping = None
        self.steps = None
        self.typing = None
        self.load_sounds()
        load_main_menu_music()

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
                    if event.key == pg.K_ESCAPE and self.game_runs and self.pause_frame in (0, PAUSE_N_FRAMES):
                        if self.paused:
                            self.pause_anim_direction = -1
                        else:
                            self.paused = True
                            self.stop_moving_sounds()
                            self.prev_state = None
                    if event.key == pg.K_F11:
                        self.full_screen = not self.full_screen
                        if self.full_screen:
                            self.screen = pg.display.set_mode((w, h), pg.FULLSCREEN)
                        else:
                            self.screen = pg.display.set_mode((w, h))
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
                if self.paused:
                    self.draw_pause(clicked)
            if self.transition_runs:
                self.transition()
            pg.display.flip()

            clock.tick(FPS)

    def load_gold_count(self):
        self.gold_count_im = pg.image.load('data/gold_count.png').convert_alpha()

    def load_exit_door_opened(self):
        self.exit_opened = pg.image.load('data/exit_door_opened.png').convert_alpha()

    def draw_exit_door_opened(self):
        if self.exit_door_opened_frame < EXIT_DOOR_OPENED_N_FRAMES:
            self.exit_door_opened_frame += 1
            self.screen.blit(self.exit_opened, EXIT_DOOR_OPENED_POS)

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

    def load_pause(self):
        im = pg.image.load('data/pause.png').convert_alpha()
        bg = pg.image.load('data/pause_bg.png').convert_alpha()
        w, h = im.get_size()
        cropped_im = im.subsurface(0, 0, w, PAUSE_BTN_H)
        self.pause_continue_btn = Button(cropped_im, bg, PAUSE_BTN_CONTINUE_POS, 0, 17)
        cropped_im = im.subsurface(0, PAUSE_BTN_H, w, PAUSE_BTN_H)
        self.pause_restart_btn = Button(cropped_im, bg, PAUSE_BTN_RESTART_POS, 0, 17)
        cropped_im = im.subsurface(0, 2 * PAUSE_BTN_H, w, PAUSE_BTN_H)
        self.pause_exit_btn = Button(cropped_im, bg, PAUSE_BTN_EXIT_POS, 0, 17)

    def draw_pause(self, clicked):
        x, y = pg.mouse.get_pos()
        buttons = pg.Surface((W, H), pg.SRCALPHA)
        self.pause_continue_btn.draw(buttons)
        self.pause_restart_btn.draw(buttons)
        self.pause_exit_btn.draw(buttons)
        buttons.set_alpha(255 * self.pause_frame // PAUSE_N_FRAMES)
        bg = pg.Surface((W, H))
        bg.fill(PAUSE_BG_COLOR)
        bg.set_alpha(PAUSE_BG_ALPHA * self.pause_frame // PAUSE_N_FRAMES)
        self.screen.blit(bg, (0, 0))
        self.screen.blit(buttons, (0, 0))
        pg.draw.rect(self.screen, BLACK, (0, 0, W, PAUSE_STRIPE_H * self.pause_frame // PAUSE_N_FRAMES))
        pg.draw.rect(self.screen, BLACK,
                     (0, H - PAUSE_STRIPE_H * self.pause_frame // PAUSE_N_FRAMES, W,
                      PAUSE_STRIPE_H * self.pause_frame // PAUSE_N_FRAMES))
        if self.pause_frame < PAUSE_N_FRAMES and self.pause_anim_direction > 0:
            self.pause_frame += self.pause_anim_direction
        elif self.pause_frame > 0 and self.pause_anim_direction < 0:
            self.pause_frame += self.pause_anim_direction
        elif self.pause_frame == 0 and self.pause_anim_direction < 0:
            self.paused = False
            self.pause_anim_direction = 1
        if self.pause_continue_btn.update(x, y, clicked):
            self.pause_anim_direction = -1
            self.click.play()
        if self.pause_restart_btn.update(x, y, clicked):
            self.paused = False
            self.pause_anim_direction = 1
            self.pause_frame = 0
            self.tr = 3
            self.transition_runs = True
            self.click.play()
        if self.pause_exit_btn.update(x, y, clicked):
            self.paused = False
            self.pause_anim_direction = 1
            self.pause_frame = 0
            self.tr = 2
            self.transition_runs = True
            self.click.play()

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
        result.sort(key=lambda value: -value[1])
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
        load_records_music()

    def open_menu(self):
        self.menu_opened = True
        self.score = 0
        self.lives = 5
        load_main_menu_music()

    def open_levels(self):
        self.levels_opened = True
        load_levels_music()

    def open_start(self):
        self.start_opened = True
        load_start_music()

    def open_game(self):
        self.game_runs = True
        self.load_level(self.level_paths.get(self.selected_level + 1))
        load_level_music(self.selected_level)

    def open_end(self):
        self.compute_score()
        self.end_opened = True
        load_end_music()

    def open_game_over(self):
        self.game_over_opened = True
        load_game_over_music()

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
        self.entrance = self.field.get_entrance()
        self.entrance_pos = self.field.get_entrance_pos()
        self.exit = self.field.get_exit()
        self.exit_pos = self.field.get_exit_pos()
        self.spawners = self.field.get_spawners()
        self.win = False
        self.enemies_killed = 0
        self.died_frames = 0
        self.start_frame = 0
        self.exit_door_opened_frame = 0
        self.can_move = False
        self.player.alive = True
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
            self.exit.v = 0.15
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

        if not self.can_move:
            if self.entrance.door_open():
                self.door_open.play()
            if self.entrance.door_opened():
                self.can_move = True
            return
        else:
            if self.entrance.door_close():
                self.door_close.play()

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
                sound = state_sounds.get(self.prev_state)
                if sound is not None:
                    sound.stop()
                sound = state_sounds.get(state)
                if sound is not None:
                    sound.play(-1)
                self.prev_state = state
        elif state_sounds.get(self.prev_state) is not None:
            state_sounds.get(self.prev_state).stop()
            self.prev_state = None

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
                        pos.draw(
                            self.screen,
                            x * self.a + GLOBAL_OFFSET_X + camera_x,
                            (self.field.h - y - 1) * self.a + GLOBAL_OFFSET_Y + camera_y
                        )
        x, y = self.entrance_pos
        self.entrance_door_pos = (x * self.a + GLOBAL_OFFSET_X + camera_x,
                                  (self.field.h - y - 1) * self.a + GLOBAL_OFFSET_Y + camera_y)
        x, y = self.exit_pos
        self.exit_door_pos = (x * self.a + GLOBAL_OFFSET_X + camera_x,
                              (self.field.h - y - 1) * self.a + GLOBAL_OFFSET_Y + camera_y)
        if not isinstance(self.player.inside(), FakeBlock):
            self.draw_player(camera_x, camera_y)
        for enemy in self.enemies:
            x, step_x, y, step_y = enemy.x, enemy.step_x, enemy.y, enemy.step_y
            enemy.draw(
                self.screen,
                x * self.a + step_x * self.a // self.player.n_steps + GLOBAL_OFFSET_X + camera_x,
                (self.field.h - y - 1) * self.a - step_y * self.a // self.player.n_steps + GLOBAL_OFFSET_Y + camera_y,
                not self.paused and self.player.alive and not self.win
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

        if self.exit.opened:
            self.draw_exit_door_opened()

        self.draw_gold_count()

    def draw_gold_count(self):
        w, h = self.gold_count_im.get_size()
        gold_count = pg.Surface((w, h), pg.SRCALPHA)
        gold_count.blit(self.gold_count_im, (0, 0))
        text = self.font.render(f'{self.gold_count - self.player.collected_gold}', True, WHITE)
        text_w, text_h = text.get_size()
        gold_count.blit(text, ((w - text_w) // 2, (h - text_h) // 2 + GOLD_COUNT_TEXT_DY))
        self.screen.blit(gold_count, GOLD_COUNT_POS)

    def draw_player(self, camera_x, camera_y):
        x, step_x, y, step_y = self.player.x, self.player.step_x, self.player.y, self.player.step_y
        if not self.player.alive:
            if self.died_frames == 0:
                self.player_died.play()
            self.stop_moving_sounds()
            if self.died_frames < DIED_N_FRAMES:
                self.died_frames += 1
                return
            self.lives -= 1
            if not self.lives:
                self.save_score()
                self.tr = 6
            else:
                self.tr = 3
            self.transition_runs = True
            return
        self.player.draw(
            self.screen, x * self.a + step_x * self.a // self.player.n_steps + GLOBAL_OFFSET_X + camera_x +
            (self.win or not self.can_move) * BG_OFFSET_X,
            (self.field.h - y - 1) * self.a - step_y * self.a // self.player.n_steps + GLOBAL_OFFSET_Y + camera_y +
            (self.win or not self.can_move) * BG_OFFSET_Y,
            not self.paused and self.player.alive and not self.win
        )
        if self.win:
            self.exit.draw_door(self.screen, *self.exit_door_pos)
        if not self.can_move:
            self.entrance.draw_door(self.screen, *self.entrance_door_pos)

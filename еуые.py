import pygame
from button import Button

pygame.init()

size = [600, 600]
screen = pygame.display.set_mode(size)
sur = pygame.Surface((600, 600))
im = pygame.image.load(r'data/test1.png').convert_alpha()
bg_im = pygame.image.load(r'data/test2.png').convert_alpha()
button = Button(im, bg_im)
while True:
    screen.fill((0, 0, 0))
    button.draw(screen, 0, 0)
    pygame.display.flip()

pygame.quit()

import pygame, sys
clock = pygame.time.Clock()
from pygame.locals import *

pygame.init()
pygame.display.set_caption('Frost Soul')
WINDOW_SIZE = (400,400)
screen = pygame.display.set_mode(WINDOW_SIZE, 0, 32) #inicia a janela
player_image = pygame.image.load('hero2.png')
moving_right = False
moving_left = False
player_location = [50,200]
player_y_momentum = 0
player_rect = pygame.rect(player_location[0], player_location[1], player_image.get_width(), player_image.get_height())
while True:
    screen.fill((146,244,255)) ## cor da tela
    screen.blit(player_image, player_location)

    if player_location[1]> WINDOW_SIZE[1]-player_image.get_height():
        player_y_momentum = -player_y_momentum
    else:
        player_y_momentum += 0.2
    player_location[1] += player_y_momentum

    if moving_right == True:
        player_location[0] += 4
    if moving_left == True:
        player_location[0] -= 4

    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit()

        if event.type == KEYDOWN:
            if event.key == K_RIGHT:
                moving_right = True
            if event.key == K_LEFT:
                moving_left = True

        if event.type == KEYUP:
            if event.key == K_RIGHT:
                moving_right = False
            if event.key == K_LEFT:
                moving_left = False
    pygame.display.update()
    clock.tick(60)
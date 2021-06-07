import pygame, sys
import data.engine as e
import threading
clock = pygame.time.Clock()
from pygame.locals import *
pygame.mixer.pre_init(44100, -16, 2, 512)
pygame.init()  # initiates pygame
pygame.mixer.set_num_channels(64)
pygame.display.set_caption('Frost Soul')
WINDOW_SIZE = (900, 600)
screen = pygame.display.set_mode(WINDOW_SIZE, 0, 32)  # initiate the window
display = pygame.Surface((600, 300))  # used as the surface for rendering, which is scaled

moving_right = False
moving_left = False
vertical_momentum = 0
air_timer = 0

true_scroll = [0, 0]

def load_map(path):
    f = open(path + '.txt', 'r')
    data = f.read()
    f.close()
    data = data.split('\n')
    game_map = []
    for row in data:
        game_map.append(list(row))
    return game_map

e.load_animations('data/images/entities/')

snow_sound_timer = 0

game_map = load_map('map')

grass_img = pygame.image.load('data/images/chao_neve.png')
dirt_img = pygame.image.load('data/images/chao_terra.png')
crystal_img = pygame.image.load('data/images/Crystal.png')

correr_neve = pygame.mixer.Sound('data/audios/running_snow.wav')
jump_sound = pygame.mixer.Sound('data/audios/hop.wav')
blizard_sound = pygame.mixer.Sound('data/audios/blizzard.wav')
blizard_sound.play(-1)
pygame.mixer.music.load('data/audios/I_Stand_Alone.wav')
pygame.mixer.music.set_volume(0.4)
pygame.mixer.music.play(-1)
music = True

player = e.entity(100, 100, 39, 45, 'player')

enemies_map_location_x= [200, 300]
enemies = []
for i in range(2):
    enemies.append([0, e.entity(enemies_map_location_x[i]-1, 200, 45, 50, 'esqueleto')]) #gera a localização do inimgo
esqueleto1 = [0, e.entity(200, 200, 45, 50, 'esqueleto')]
    # e coloca a física de colisão

background_objects = [[0.25, [120, 10, 70, 400]], [0.25, [280, 30, 40, 400]], [0.5, [30, 40, 40, 400]],
                      [0.5, [130, 90, 100, 400]], [0.5, [300, 80, 120, 400]]]


while True:  # game loop
    display.fill((194, 226, 255))  # coloca cor de fundo de azul quase branco

    if snow_sound_timer > 0:
        snow_sound_timer -= 1

    true_scroll[0] += (player.x - true_scroll[0] - 169) / 20 #posição da camera x
    true_scroll[1] += (player.y - true_scroll[1] - 112) / 20 #posição da camera y
    scroll = true_scroll.copy()
    scroll[0] = int(scroll[0])
    scroll[1] = int(scroll[1])

    pygame.draw.rect(display, (0, 131, 255), pygame.Rect(0, 120, 300, 80)) #primeiro é a cor do bloco do fundo
    for background_object in background_objects:
        obj_rect = pygame.Rect(background_object[1][0] - scroll[0] * background_object[0],
                               background_object[1][1] - scroll[1] * background_object[0], background_object[1][2],
                               background_object[1][3])
        if background_object[0] == 1:
            pygame.draw.rect(display, (95, 161, 254), obj_rect)
        else:
            pygame.draw.rect(display, (95, 161, 254), obj_rect)

    tile_rects = []
    y = 0
    for layer in game_map:
        x = 0
        for tile in layer:
            if tile == '1':
                display.blit(dirt_img, (x * 32 - scroll[0], y * 32 - scroll[1]))
            if tile == '2':
                display.blit(grass_img, (x * 32 - scroll[0], y * 32 - scroll[1]))
            if tile == '3':
                display.blit(crystal_img, (x * 32 - scroll[0], y * 35 - scroll[1]))
            if tile != '0':
                tile_rects.append(pygame.Rect(x * 32, y * 32, 32, 32))
            x += 1
        y += 1

    player_movement = [0, 0]
    if moving_right == True:
        player_movement[0] += 4
    if moving_left == True:
        player_movement[0] -= 4
    player_movement[1] += vertical_momentum
    vertical_momentum += 0.2
    if vertical_momentum > 3:
        vertical_momentum = 3

    if player_movement[0] == 0:
        player.set_action('parado')
    if player_movement[0] > 0:
        player.set_action('correr')
        player.set_flip(False)
    if player_movement[0] < 0:
        player.set_action('correr')
        player.set_flip(True)
    if vertical_momentum == 3:
        player.set_action('cair')
    elif air_timer > 7:
        player.set_action('pular')

    collision_types = player.move(player_movement, tile_rects)

    if collision_types['bottom'] == True:
        air_timer = 0
        vertical_momentum = 0
        if player_movement[0] !=0:
            if snow_sound_timer ==0:
                snow_sound_timer = 30
                correr_neve.play()
        if player_movement[0] ==0 or air_timer!=0:
            correr_neve.fadeout(0)
    else:
        air_timer += 1

    player.change_frame(1)
    player.display(display, scroll)

    for enemy in enemies:
        enemy[0] +=0.2
        if enemy[0] > 3:
            enemy[0] = 3
        enemy_movement = [0, enemy[0]]
        if player.x > enemy[1].x + 5:
            enemy_movement[0] = 1
            enemy[1].set_action('correr')
            enemy[1].set_flip(False)
        if player.x < enemy[1].x - 5:
            enemy_movement[0] = -1
            enemy[1].set_action('correr')
            enemy[1].set_flip(True)
        if enemy_movement[0] == 0:
            enemy[1].set_action('parado')
        collision_types = enemy[1].move(enemy_movement, tile_rects)
        if collision_types['bottom'] == True:
            enemy[0] = 0
        enemy[1].display(display, scroll)
        if player.obj.rect.colliderect(enemy[1].obj.rect):
            player_movement[0] += 4
            #vertical_momentum = -4
        enemy[1].change_frame(1)

    for event in pygame.event.get():  # event loop
        if event.type == QUIT:
            pygame.quit()
            sys.exit()
        if event.type == KEYDOWN:
            if event.key == K_m:
                if music == True:
                    pygame.mixer.music.fadeout(10)
                    music = False
                else:
                    pygame.mixer.music.play(-1)
                    music = True
            if event.key == K_d:
                moving_right = True
            if event.key == K_a:
                moving_left = True
            if event.key == K_w:
                correr_neve.fadeout(0)
                if air_timer < 8:
                    jump_sound.play()
                    vertical_momentum = -7
        if event.type == KEYUP:
            if event.key == K_d:
                moving_right = False
            if event.key == K_a:
                moving_left = False

    screen.blit(pygame.transform.scale(display, WINDOW_SIZE), (0, 0))
    pygame.display.update()
    clock.tick(60)

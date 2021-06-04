import pygame, sys
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

global animation_frames
animation_frames = {}

def load_animation(path, frame_durations):
    global animation_frames
    animation_name = path.split('/')[-1]
    animation_frame_data = []
    n = 0
    for frame in frame_durations:
        animation_frame_id = animation_name + '_' + str(n)
        img_location = path + '/' + animation_frame_id + '.png'
        animation_image = pygame.image.load(img_location).convert()
        animation_image.set_colorkey((0,0,0)) #o fundo do personagem está preto, isso tira a cor preta de fundo
        animation_frames[animation_frame_id] = animation_image.copy()
        for i in range(frame):
            animation_frame_data.append(animation_frame_id)
        n += 1
    return animation_frame_data

def change_action(action_var, frame, new_value):
    if action_var != new_value:
        action_var = new_value
        frame = 0
    return action_var, frame

animation_database = {}
animation_database['correr'] = load_animation('player_animations/correr', [7,7,7])
animation_database['parado'] = load_animation('player_animations/parado', [7,7,7])
animation_database['pular'] = load_animation('player_animations/pular', [7])
animation_database['cair'] = load_animation('player_animations/cair', [7])

player_action = 'parado'
player_frame = 0
player_flip = False

snow_sound_timer = 0

game_map = load_map('map')

grass_img = pygame.image.load('chao_neve.png')
dirt_img = pygame.image.load('chao_terra.png')
crystal_img = pygame.image.load('Crystal.png')

correr_neve = pygame.mixer.Sound('running_snow.wav')
jump_sound = pygame.mixer.Sound('hop.wav')
blizard_sound = pygame.mixer.Sound('blizzard.wav')
blizard_sound.play(-1)
pygame.mixer.music.load('I_Stand_Alone.wav')
pygame.mixer.music.set_volume(0.4)
pygame.mixer.music.play(-1)
music = True

player_rect = pygame.Rect(100, 100, 39, 45)

background_objects = [[0.25, [120, 10, 70, 400]], [0.25, [280, 30, 40, 400]], [0.5, [30, 40, 40, 400]],
                      [0.5, [130, 90, 100, 400]], [0.5, [300, 80, 120, 400]]]


def collision_test(rect, tiles):
    hit_list = []
    for tile in tiles:
        if rect.colliderect(tile):
            hit_list.append(tile)
    return hit_list


def move(rect, movement, tiles):
    collision_types = {'top': False, 'bottom': False, 'right': False, 'left': False}
    rect.x += movement[0]
    hit_list = collision_test(rect, tiles)
    for tile in hit_list:
        if movement[0] > 0:
            rect.right = tile.left
            collision_types['right'] = True
        elif movement[0] < 0:
            rect.left = tile.right
            collision_types['left'] = True
    rect.y += movement[1]
    hit_list = collision_test(rect, tiles)
    for tile in hit_list:
        if movement[1] > 0:
            rect.bottom = tile.top
            collision_types['bottom'] = True
        elif movement[1] < 0:
            rect.top = tile.bottom
            collision_types['top'] = True
    return rect, collision_types


while True:  # game loop
    display.fill((194, 226, 255))  # coloca cor de fundo de azul quase branco

    if snow_sound_timer > 0:
        snow_sound_timer -= 1

    true_scroll[0] += (player_rect.x - true_scroll[0] - 169) / 20 #posição da camera x
    true_scroll[1] += (player_rect.y - true_scroll[1] - 112) / 20 #posição da camera y
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

    if player_movement[0] > 0:
        player_action, player_frame = change_action(player_action, player_frame, 'correr')
        player_flip = False
    if player_movement[0] == 0:
        player_action, player_frame = change_action(player_action, player_frame, 'parado')
    if player_movement[0] < 0:
        player_action, player_frame = change_action(player_action, player_frame, 'correr')
        player_flip = True
    if vertical_momentum == 3:
        player_action, player_frame = change_action(player_action, player_frame, 'cair')
    elif air_timer > 7:
        player_action, player_frame = change_action(player_action, player_frame, 'pular')

    player_rect, collisions = move(player_rect, player_movement, tile_rects)

    if collisions['bottom'] == True:
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

    player_frame += 1
    if player_frame >= len(animation_database[player_action]):
        player_frame = 0
    player_img_id = animation_database[player_action][player_frame]
    player_img = animation_frames[player_img_id]
    display.blit(pygame.transform.flip(player_img,player_flip, False,),(player_rect.x - scroll[0], player_rect.y - scroll[1]))

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
                if air_timer < 7:
                    jump_sound.play()
                    vertical_momentum = -6
        if event.type == KEYUP:
            if event.key == K_d:
                moving_right = False
            if event.key == K_a:
                moving_left = False

    screen.blit(pygame.transform.scale(display, WINDOW_SIZE), (0, 0))
    pygame.display.update()
    clock.tick(60)

#!/usr/bin/python3

import pygame
from pygame.locals import *
from pygame.compat import geterror
import os
import random
from pygame.math import Vector2 as Vec

os.environ['SDL_VIDEO_CENTERED'] = '0'

# settings for the game
TITLE = 'Bunny'
WIDTH = 480
HEIGHT = 600
FPS = 60

# define colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
GRAY = (128, 128, 128)
AQUA = (0, 255, 255)
PURPLE = (128, 0, 128)

# Directories
main_dir = os.path.split(os.path.abspath(__file__))[0]
data_dir = os.path.join(main_dir, 'data')


# functions to create our resources
def load_image(name, colorkey=None):
    fullname = os.path.join(data_dir, name)
    try:
        image = pygame.image.load(fullname)
    except pygame.error:
        print('Cannot load image:', fullname)
        raise SystemExit(str(geterror()))
    image = image.convert()
    if colorkey is not None:
        if colorkey is -1:
            colorkey = image.get_at((0, 0))
        image.set_colorkey(colorkey, RLEACCEL)
    return image, image.get_rect()


def load_sound(name):
    class NoneSound:
        def play(self): pass

    if not pygame.mixer or not pygame.mixer.get_init():
        return NoneSound()
    fullname = os.path.join(data_dir, name)
    try:
        sound = pygame.mixer.Sound(fullname)
    except pygame.error:
        print('Cannot load sound: %s' % fullname)
        raise SystemExit(str(geterror()))
    return sound


def load_music(name):
    class NoneSound:
        def play(self): pass

    if not pygame.mixer or not pygame.mixer.get_init():
        return NoneSound()
    fullname = os.path.join(data_dir, name)
    try:
        sound = pygame.mixer.music.load(fullname)
    except pygame.error:
        print('Cannot load music: %s' % fullname)
        raise SystemExit(str(geterror()))
    return sound


sprite_mine = pygame.sprite.Sprite

# platform list
PLATFORM_LIST = [
    (0, HEIGHT-30, WIDTH, 30),
    (WIDTH//2-50, HEIGHT//2-100, 100, 30),
    (30, HEIGHT-200, 100, 30),
    (WIDTH-100, HEIGHT-250, 100, 30),
]

# platform


class Platform(sprite_mine):
    def __init__(self, x, y, w, h):
        sprite_mine.__init__(self)
        self.image = pygame.Surface((w, h))
        self.image.fill(GREEN)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

    def update(self):
        if self.rect.top >= HEIGHT:
            self.kill()


# Player settings
PLAYER_STARTING_POSITION = Vec(WIDTH//2, HEIGHT//2)
PLAYER_ACCELERATION = 3
PLAYER_FRICTION = -1
PLAYER_GRAVITY = 1
PLAYER_VERTICAL_JUMP = -20

# the player


class Player(sprite_mine):
    def __init__(self, game):
        sprite_mine.__init__(self)
        self.game = game

        # game variables
        self.image_orig = game.bunny_standing[0]
        self.image = self.image_orig.copy()
        self.rect = self.image.get_rect()
        self.rect.center = PLAYER_STARTING_POSITION
        # self.rect.topleft = self.pos

        # animation variables
        self.last_update = 0
        self.frame = 0
        self.frame_limit_standing = 250
        self.frame_limit_walking = 90
        self.current_frame = 0

        # movement variables
        self.vel = Vec(0, 0)
        self.acc = Vec(0, 0)
        self.pos = PLAYER_STARTING_POSITION

    def jump(self):
        if not self.game.jumping:
            self.vel.y = PLAYER_VERTICAL_JUMP

    def animate(self):
        if abs(self.vel.x) > 0:
            now = pygame.time.get_ticks()
            if now - self.last_update > self.frame_limit_walking:
                self.last_update = now
                self.current_frame = (self.current_frame +
                                      1) % len(self.game.bunny_standing)
                midbottom = self.rect.midbottom
                if self.vel.x > 0:
                    self.image = self.game.bunny_walking_left[self.current_frame]
                else:
                    self.image = self.game.bunny_walking_right[self.current_frame]
                self.rect = self.image.get_rect()
                self.rect.midbottom = midbottom
        else:
            now = pygame.time.get_ticks()
            if now - self.last_update > self.frame_limit_standing:
                self.last_update = now
                self.current_frame = (self.current_frame +
                                      1) % len(self.game.bunny_standing)
                midbottom = self.rect.midbottom
                self.image = self.game.bunny_standing[self.current_frame]
                self.rect = self.image.get_rect()
                self.rect.midbottom = midbottom

    def movement(self):
        # key is pressed
        if self.keystate[K_LEFT]:
            self.acc.x = -PLAYER_ACCELERATION
        elif self.keystate[K_RIGHT]:
            self.acc.x = PLAYER_ACCELERATION
        # wap the character around the screen
        if self.rect.left > WIDTH:
            self.pos.x = - self.rect.width//2
        elif self.rect.right < 0:
            self.pos.x = WIDTH + self.rect.width//2
        if self.rect.top > HEIGHT:
            self.kill()
        if self.vel.y < PLAYER_VERTICAL_JUMP:
            self.vel.y = PLAYER_VERTICAL_JUMP
        elif self.vel.y > -PLAYER_VERTICAL_JUMP:
            self.vel.y = -PLAYER_VERTICAL_JUMP

        self.acc.x += self.vel.x * PLAYER_FRICTION
        self.vel += self.acc
        self.pos += self.vel + 0.5 * self.acc
        self.rect.midbottom = self.pos

    def update(self):
        self.keystate = pygame.key.get_pressed()
        self.acc = Vec(0, PLAYER_GRAVITY)
        self.movement()
        self.animate()


class Game:
    # A bunch of stuff that happen when the game starts
    def __init__(self):
        pygame.init()
        pygame.mixer.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption(TITLE)
        self.clock = pygame.time.Clock()
        self.running = True
        self._graphics()
        self.jumping = False

    def _graphics(self):
        # background
        background, rect = load_image('bg_layer1.png', BLACK)
        self.background = pygame.transform.scale(background, (WIDTH, HEIGHT))
        self.background_rect = self.background.get_rect()
        # bunny standing
        bunny_image1, rect = load_image('bunny1_stand.png', BLACK)
        bunny_image1 = pygame.transform.scale(bunny_image1, (60, 100))
        bunny_image2, rect = load_image('bunny1_ready.png', BLACK)
        bunny_image2 = pygame.transform.scale(bunny_image2, (60, 100))
        # bunny walking left
        bunny_image3, rect = load_image('bunny1_walk1.png', BLACK)
        bunny_image3 = pygame.transform.scale(bunny_image3, (60, 100))
        bunny_image4, rect = load_image('bunny1_walk2.png', BLACK)
        bunny_image4 = pygame.transform.scale(bunny_image4, (60, 100))
        # bunny walking right
        bunny_image5 = pygame.transform.flip(bunny_image3, True, False)
        bunny_image6 = pygame.transform.flip(bunny_image4, True, False)
        # different lists of states of the bunny
        self.bunny_standing = [bunny_image1, bunny_image2]
        self.bunny_walking_left = [bunny_image3, bunny_image4]
        self.bunny_walking_right = [bunny_image5, bunny_image6]
        # Platform
        self.platform_image, rect = load_image('ground_grass.png', BLACK)

    # Start a new Game
    def new(self):
        self.all_sprites = pygame.sprite.Group()
        self.platform = pygame.sprite.Group()
        self.player = Player(self)
        self.all_sprites.add(self.player)
        self.platlist()

    # load platform list
    def platlist(self):
        for plat in PLATFORM_LIST:
            p = Platform(*plat)
            self.all_sprites.add(p)
            self.platform.add(p)

    # The game loop
    def run(self):
        self.playing = True
        while self.playing:
            self.clock.tick(FPS)
            self.events()
            self.update()
            self.draw()

    # Game loop update

    def update(self):
        self.all_sprites.update()
        # check the collision when the player is moving downward
        if self.player.vel.y > 0:
            hits = pygame.sprite.spritecollide(
                self.player, self.platform, False)
            if hits:
                self.player.pos.y = hits[0].rect.top
                self.player.vel.y = 0
                self.jumping = False
        # scroll the screen
        if self.player.rect.top <= HEIGHT/4:
            self.player.pos.y += abs(self.player.vel.y)
            for plat in self.platform:
                plat.rect.y += max(abs(self.player.vel.y), 10)
        # if player dies game ends
        if self.player.rect.top > HEIGHT:
            for sprite in self.all_sprites:
                sprite.rect.y -= max(self.player.vel.y, 10)
            self.running = False
        # spawn new platforms
        while len(self.platform) < 5:
            width = random.randrange(100, 150)
            p = Platform(random.randrange(0, WIDTH-width),
                         random.randrange(-65, -30), width, 30)
            self.platform.add(p)
            self.all_sprites.add(p)

    # Game loop events
    def events(self):
        for event in pygame.event.get():
            # check for closing window
            if event.type == pygame.QUIT or event.type == KEYUP and event.key == K_ESCAPE:
                if self.playing:
                    self.playing = False
                self.running = False
            # user input for jumping
            if event.type == KEYDOWN and event.key == K_SPACE:
                self.player.jump()
                self.jumping = True

    # Game loop draw
    def draw(self):
        # Draw / Render
        self.screen.fill(BLACK)
        # blit the background
        self.screen.blit(self.background, self.background_rect)
        # update all the sprites
        self.all_sprites.draw(self.screen)
        # draw the fps
        pygame.display.set_caption(
            TITLE + " | {:.2f}|".format(self.clock.get_fps()))
        # *after*  drawing everything , flip the display last
        pygame.display.flip()

    # Game start screen
    def show_start_screen(self): pass

    # Game over screen
    def show_game_over_screen(self): pass


g = Game()
g.show_start_screen()
while g.running:
    g.new()
    g.run()
    g.show_game_over_screen()

pygame.quit()
quit()

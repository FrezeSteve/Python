#!/usr/bin/python3

import pygame
from pygame.locals import *
from pygame.compat import geterror
import os
import random
from pygame.math import Vector2 as Vec

os.environ['SDL_VIDEO_CENTERED'] = '0'

WIDTH = 800
HEIGHT = 480
FPS = 90
TITLE = 'Test'

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

# player settings
player_speed = 250
player_friction = -1
Gravity = -10


class Platform(sprite_mine):
    def __init__(self, x, y, w, h):
        sprite_mine.__init__(self)
        self.image = pygame.Surface((w, h))
        self.image.fill(GREEN)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y


class Player(sprite_mine):
    def __init__(self, game):
        self.game = game
        sprite_mine.__init__(self)
        self.image = pygame.Surface((50, 40))
        self.image.fill(YELLOW)
        self.rect = self.image.get_rect()
        self.rect.midbottom = Vec(0, 0)
        self.pos = Vec(30, HEIGHT-55)

    def jump(self):
        pass

    def update(self):
        self.rect.midbottom = self.pos
        if self.rect.left > WIDTH:
            self.pos.x = -self.rect.width//2
        pass


class Game:
    # A bunch of stuff that happen when the game starts
    def __init__(self):
        pygame.init()
        pygame.mixer.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption(TITLE)
        self.clock = pygame.time.Clock()
        self.running = True

    # Start a new Game
    def new(self):
        self.all_sprites = pygame.sprite.Group()
        self.platform_group = pygame.sprite.Group()
        self.player = Player(self)
        self.all_sprites.add(self.player)
        p1 = Platform(0, HEIGHT-50, WIDTH, 50)
        self.all_sprites.add(p1)
        self.platform_group.add(p1)

    # The game loop

    def run(self):
        self.playing = True
        while self.playing:
            self.dt = self.clock.tick(FPS)/1000
            self.events()
            self.update()
            self.draw()

    # Game loop update

    def update(self):
        self.all_sprites.update()
        # collision detection for the platform and the player
        hits = pygame.sprite.spritecollide(
            self.player, self.platform_group, False)
        if hits:
            self.player.pos.y = hits[0].rect.top

    # Game loop events

    def events(self):
        for event in pygame.event.get():
            # check for closing window
            if event.type == pygame.QUIT:
                if self.playing:
                    self.playing = False
                self.running = False
            if event.type == KEYDOWN:
                if event.key == K_SPACE:
                    self.player.jump()

    # Game loop draw
    def draw(self):
        # Draw / Render
        self.screen.fill(BLACK)
        self.all_sprites.draw(self.screen)
        # *after*  drawing everything , flip the display last
        pygame.display.flip()
        pygame.display.set_caption(
            TITLE + " | {:.2f}|".format(self.clock.get_fps()))

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

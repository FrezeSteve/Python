# Bunny GAME
import pygame
import random
import os

from pygame.locals import *
from pygame.compat import geterror

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

# Player Character settings
Bunny_Speed = 150
Bunny_Friction = -1
Bunny_Jump = -1000
Gravity = 10


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


class Platform(sprite_mine):
    def __init__(self, game, x, y):
        sprite_mine.__init__(self)
        self.game = game
        self.image_orig = game.platform_image
        self.rect = self.image_orig.get_rect()
        self.rect.width = self.rect.width//2
        self.rect.height = self.rect.height//2
        self.image = pygame.transform.scale(
            self.image_orig, (self.rect.width, self.rect.height))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y


class Player(sprite_mine):
    def __init__(self, game):
        sprite_mine.__init__(self)
        self.game = game
        # self.image = pygame.Surface((30, 40))
        self.image_orig = game.bunny_standing[0]
        self.image = self.image_orig.copy()
        self.rect = self.image.get_rect()
        self.rect.center = Vec(WIDTH//2, 0)
        self.vel, self.acc = Vec(0, 0), Vec(0, 0)
        self.pos = Vec(WIDTH//2, HEIGHT//2)
        # self.rect.topleft = self.pos
        self.last_update = 0
        self.frame = 0
        self.frame_limit_standing = 250
        self.frame_limit_walking = 100
        self.current_frame = 0
        self.walking = False
        self.in_Air = True

    def animate(self):
        if self.walking:
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

    def jump(self):
        if not self.in_Air:
            self.vel.y = int(Bunny_Jump * self.game.dt)
            self.in_Air = True

    def update(self):

        self.animate()
        # the velocity is always equals to 0 if the player isnt pressing the keys
        self.acc = Vec(0, Gravity * self.game.dt)
        # self.acc = Vec(0, 0)
        # the character is always standing if the player isnt pressing the keys
        self.walking = False
        # receive the keys the player is pressing
        keys = pygame.key.get_pressed()
        # check the different keys being pressed
        if keys[K_LEFT]:
            self.acc.x = -Bunny_Speed * self.game.dt
            self.walking = True
        elif keys[K_RIGHT]:
            self.acc.x = Bunny_Speed * self.game.dt
            self.walking = True
        # make sure the player is always in on screen
        if self.rect.left > WIDTH+10:
            self.pos.x = -self.rect.width
        elif self.rect.right < -10:
            self.pos.x = WIDTH
        # the movement formulae
        self.acc.x += self.vel.x * Bunny_Friction
        self.vel += self.acc
        self.pos += self.vel + 0.5 * self.acc

        self.rect.midbottom = self.pos


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

    def _graphics(self):
        # background
        background, rect = load_image('bg_layer1.png', BLACK)
        self.background = pygame.transform.scale(background, (WIDTH, HEIGHT))
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
        self.platform_group = pygame.sprite.Group()
        self.player = Player(self)
        self.all_sprites.add(self.player)
        p1 = Platform(self, WIDTH//2, HEIGHT-50)
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
        # update the sprites
        self.all_sprites.update()
        # collision detection for the platform and the player
        hits = pygame.sprite.spritecollide(
            self.player, self.platform_group, False)
        if hits:
            self.player.pos.y = hits[0].rect.top
            self.player.vel.y = 0
            self.player.acc.y = 0
            self.player.in_Air = False

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
        rect = self.background.get_rect()
        self.screen.blit(self.background, rect)
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

# Import Statements
import pygame as pg
from os.path  import join
from random  import randint, uniform

pg.init()
title = "Space Shooter"
window_width, window_height= 1920, 1200
running = True
clock = pg.time.Clock()
pg.mouse.set_visible(False)
display_surface = pg.display.set_mode((window_width, window_height))
pg.display.set_caption(title)
score = 0

class Player(pg.sprite.Sprite):
    def __init__(self, group):
        super().__init__(group)
        self.image = pg.image.load(join("images","s_ship.png")).convert_alpha()
        self.image = pg.transform.scale(self.image, (125,125))
        self.rect = self.image.get_frect(center = (window_width * 0.5, window_height * 0.85))
        self.dir = pg.math.Vector2()
        self.speed = 600
        
        self.mask = pg.mask.from_surface(self.image)
        
        self.can_shoot = True
        self.shoot_cooldown = 150
        self.last_shot_time = 0
        
    def laser_timer(self):
        interval = pg.time.get_ticks() - self.last_shot_time
        if interval >= self.shoot_cooldown:
            self.can_shoot = True

        
    def update(self, dt):
        KEY_PRESS = pg.key.get_pressed()
        KEY_JPRESS = pg.key.get_just_pressed()
        KEY_JREL = pg.key.get_just_released()
        
        self.rect.center = pg.mouse.get_pos()
        """ 
        if KEY_PRESS[pg.K_z] and self.rect.top > 0:
            self.dir.y = -1
        if KEY_PRESS[pg.K_s] and self.rect.bottom < window_height:
            self.dir.y = 1
        if KEY_PRESS[pg.K_q] and self.rect.left > 0:
            self.dir.x = -1
        if KEY_PRESS[pg.K_d] and self.rect.right < window_width:
            self.dir.x = 1
             
        if self.dir:
            self.dir = self.dir.normalize()
            """
        self.rect.center += self.dir * self.speed * dt
        self.dir.y = 0
        self.dir.x = 0
         
        if pg.mouse.get_pressed()[0]:
            if self.can_shoot:
                Laser(laser_surf, self.rect.midtop, (all_sprites, laser_sprites))
                self.can_shoot = False
                self.last_shot_time = pg.time.get_ticks()
                laser_sound.play()
            self.laser_timer()

class Star(pg.sprite.Sprite):

    def __init__(self, star_surf, group):
        super().__init__(group)
        self.image = star_surf
        star_size = randint(7, 40)
        self.image = pg.transform.scale(self.image, (star_size, star_size)) 
        self.image.set_alpha(randint(50,255))
        self.rect =  self.image.get_frect(center = (randint(0, window_width), randint(0, window_height)))
        self.speed = randint(500, 1100)
        
    def update(self, dt):
        self.rect.y += self.speed * dt
        if  self.rect.top > window_height:
            self.rect.x = randint(0, window_width)
            self.rect.bottom = 0
        
class Laser(pg.sprite.Sprite):
    def __init__(self, surf, pos, group):
        super().__init__(group)
        self.image = surf
        self.rect = self.image.get_frect(midbottom = pos)
        self.speed = 1200
        
    def update( self, dt):
        self.rect.y -= self.speed * dt
        if self.rect.bottom < 0:
            self.kill()

class Meteor(pg.sprite.Sprite):
    def __init__(self, meteor_surf, group):
        super().__init__(group)
        self.og_image = meteor_surf
        self.image = self.og_image
        self.start_angle = randint(-359,359)
        self.rotation_angle = randint(-180,180)
        new_width = randint(70, 110)
        aspect_ratio = self.image.get_width() / self.image.get_height()
        new_height = int(new_width / aspect_ratio)
        self.image = pg.transform.scale(self.image, (new_width, new_height))
        self.rect = self.image.get_frect(midbottom = (randint(50, window_width - 50), 0))
        self.speed = randint(180,400)
        self.alive_time = 6500
        self.birth_time = pg.time.get_ticks()
        self.dir = pg.math.Vector2(uniform(-0.5,0.5),1)
        
        if self.dir:
            self.dir = self.dir.normalize()
        
    def update(self, dt):
        self.image = pg.transform.rotozoom(self.og_image, self.start_angle,1)
        self.start_angle += self.rotation_angle * dt
        self.rect = self.image.get_frect(center = self.rect.center)
        self.rect.center += self.dir * self.speed * dt
        if pg.time.get_ticks() - self.birth_time >= self.alive_time:
            self.kill()
        if self.rect.left <= 0:
            self.dir.x *= -1
        elif self.rect.right >= window_width:
            self.dir.x *= -1

class AnimatedExplosion(pg.sprite.Sprite):
    def __init__(self, pos, group):
        super().__init__(group)
        self.sheets = [pg.image.load(join("images","explosion",f"{i}.png")).convert_alpha() for i in range(0,21)]
        self.index = 0
        self.image = self.sheets[self.index]
        self.rect = self.image.get_frect(center = (pos))
        self.counter = 0
        
    def update(self,dt):
        explosion_speed = 45 * dt
        self.counter += 1
        if self.counter >= explosion_speed and self.index < len(self.sheets) - 1:
            self.counter = 0
            self.index += 1
            self.image = self.sheets[self.index]
        if self.index >= len(self.sheets) - 1:
            self.kill()

def collisions():
    global score
    if pg.sprite.spritecollide(p1, meteor_sprites, True, pg.sprite.collide_mask):
        damage_sound.play()
    collided_lasers = pg.sprite.groupcollide(laser_sprites, meteor_sprites, True, True, pg.sprite.collide_mask)
    if collided_lasers:
        score += len(collided_lasers)
        explosion_sound.play()
        for laser in collided_lasers:
            AnimatedExplosion(laser.rect.midtop, all_sprites)
    return score

def display_score():
    text_surf = font.render(str(collisions()), True, "#9c055a")
    text_rect = text_surf.get_frect(center = (window_width / 2, window_height - 60))
    display_surface.blit(text_surf, text_rect)
    pg.draw.rect(display_surface, "#9c055a", text_rect.inflate(30,15).move(0,-5), 5, 10)
    
star_surf = pg.image.load(join("images","star.png")).convert_alpha()
meteor_surf = pg.image.load(join("images","meteor.png")).convert_alpha()
laser_surf = pg.image.load(join("images", "laser.png")).convert_alpha()

font = pg.font.Font(join("images", "Oxanium-Bold.ttf"), 40)

laser_sound = pg.mixer.Sound(join("audio","laser2.wav"))
laser_sound.set_volume(0.06)

explosion_sound = pg.mixer.Sound(join("audio","explosion.wav"))
explosion_sound.set_volume(0.08)

damage_sound = pg.mixer.Sound(join("audio","damage.ogg"))
damage_sound.set_volume(0.2)
game_music = pg.mixer.Sound(join("audio","game_music.wav"))
game_music.set_volume(0.03)
game_music.play(-1)

all_sprites = pg.sprite.Group()
meteor_sprites = pg.sprite.Group()
laser_sprites = pg.sprite.Group()

for _ in range(35):
    star = Star(star_surf,all_sprites)
    
paused = False
p1 = Player(all_sprites)

meteor_event = pg.event.custom_type()
pg.time.set_timer(meteor_event, 500)

while running:
    dt = clock.tick(165) * 0.001
    
    # event loop
    for event in pg.event.get():
        if event.type == pg.QUIT:
            running = False
        elif event.type == pg.WINDOWMOVED:
            paused = True
        elif event.type == pg.ACTIVEEVENT:
            if event.gain and paused:
                paused = False
        if event.type == meteor_event:
            Meteor(meteor_surf, (all_sprites, meteor_sprites))

    # update and drawing
    if not paused:
        all_sprites.update(dt)
        collisions()
        display_surface.fill("black")
        display_score()
        all_sprites.draw(display_surface)
        
        pg.display.update()

pg.quit()
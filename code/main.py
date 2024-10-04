from settings import *
import pygame
from player import *
from sprites import *
from random import randint , choice
from pytmx.util_pygame import load_pygame
from groups import *


class Game():
    def __init__(self):
        pygame.init()
        self.display_surface = pygame.display.set_mode((WINDOW_WIDTH , WINDOW_HEIGHT))
        pygame.display.set_caption("Survivor")
        self.clock = pygame.time.Clock()
        self.running = True

        #groups
        self.all_sprites = AllSprites()
        self.collision_sprites = pygame.sprite.Group()
        self.bullet_sprites = pygame.sprite.Group()
        self.enemy_sprites = pygame.sprite.Group()

        # shoot timer
        self.can_shoot = True
        self.shoot_time = 0
        self.gun_cooldown =  200    

        # damage player time
        self.can_damage = True
        self.damage_time = 0
        self.damage_cooldown =  500  

        # enemy
        self.enemy_event = pygame.event.custom_type()
        pygame.time.set_timer(self.enemy_event, 800)
        self.spawn_positions = []

        # audio
        self.shoot_sound = pygame.mixer.Sound('audio/shoot.wav')
        self.impact_sound = pygame.mixer.Sound('audio/impact.ogg')
        self.music = pygame.mixer.Sound('audio/music.wav')
        self.music.set_volume(0.3)
        self.music.play(loops = -1)

        self.load_images()
        self.setup()

    def load_images(self):
        self.bullet_surface = pygame.image.load(join("images", "gun" , "bullet.png")).convert_alpha()

        folders = list(walk('images/enemies'))[0][1]
        self.enemy_frames ={}
        for folder in folders:
            for folder_path, _, file_names in walk(f'images/enemies/{folder}'):
                self.enemy_frames[folder] = []
                for file_name in sorted(file_names, key= lambda name: int(name.split('.')[0])):
                    full_path = f"{folder_path}/{file_name}"
                    surf = pygame.image.load(full_path).convert_alpha()
                    self.enemy_frames[folder].append(surf)

       
    def input(self):
        if pygame.mouse.get_pressed()[0] and self.can_shoot:
            pos = self.gun.rect.center +self.gun.player_direction * 50
            Bullet(self.bullet_surface, pos , self.gun.player_direction ,(self.all_sprites, self.bullet_sprites))
            self.can_shoot = False
            self.shoot_time = pygame.time.get_ticks()
    
    def gun_timer(self):
        if not self.can_shoot:
            current_time = pygame.time.get_ticks()
            if current_time  - self.shoot_time >= self.gun_cooldown:
                self.can_shoot = True

    def damage_timer(self):
        if not self.can_damage:
            current_time = pygame.time.get_ticks()
            if current_time  - self.damage_time >= self.damage_cooldown:
                self.can_damage = True

    def bullet_collision(self):
        for bullet in self.bullet_sprites:
            collosion = pygame.sprite.spritecollide(bullet, self.enemy_sprites ,False, pygame.sprite.collide_mask)
            if collosion:
                    self.impact_sound.play()
                    for sprite in collosion:
                        sprite.destroy()
                    bullet.kill()

    def player_collision(self):
        self.damage_timer()
        if pygame.sprite.spritecollide(self.player , self.enemy_sprites, False,  pygame.sprite.collide_mask) and self.can_damage:
            self.player.health -= 7
            if self.player.health <= 0: self.running = False 
            self.can_damage = False
            self.damage_time = pygame.time.get_ticks()



    def setup(self):
        map = load_pygame(join("data", "maps" ,"world.tmx"))
        for x,y , image in map.get_layer_by_name('Ground').tiles():
            Ground((x * TILE_SIZE, y * TILE_SIZE), image, self.all_sprites)

        for obj in map.get_layer_by_name('Objects'):
            CollisionSprites((obj.x, obj.y) , obj.image, (self.all_sprites, self.collision_sprites))

        for obj in map.get_layer_by_name('Collisions'):
            CollisionSprites((obj.x, obj.y) , pygame.Surface((obj.width , obj.height), pygame.SRCALPHA) , (self.all_sprites ,self.collision_sprites))
        for obj in map.get_layer_by_name('Entities'):
            if obj.name == 'Player':
                 self.player = Player((obj.x,obj.y),self.all_sprites , self.collision_sprites)
                 self.gun = Gun(self.player , self.all_sprites)
            else: self.spawn_positions.append((obj.x, obj.y))

    def show_health(self):
        health_image = pygame.Surface((self.player.health * 2, 25))
        health_image.fill((255, 0, 0))  
        health_rect = health_image.get_rect(topleft=(100, 20))
        self.display_surface.blit(health_image, health_rect)
        pygame.draw.rect(self.display_surface, "black", pygame.Rect(100, 20, 200, 25), 2)

        font = pygame.font.Font(None, 30)
        text_surface = font.render("Health", True, (0, 0, 0))  
        text_rect = text_surface.get_rect(midleft=(20, 33))  
        self.display_surface.blit(text_surface, text_rect)

    

    def run(self):
        while self.running:
            dt = self.clock.tick() / 1000

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                if event.type == self.enemy_event:
                   Enemy(choice(self.spawn_positions), choice(list(self.enemy_frames.values())), (self.all_sprites, self.enemy_sprites) ,  self.player , self.collision_sprites)

            self.gun_timer()
            self.input()
            self.bullet_collision()
            self.player_collision()
            self.all_sprites.update(dt)

            
            self.display_surface.fill('black')
            self.all_sprites.draw(self.player.rect.center)
            
            self.show_health()


            pygame.display.update()
        pygame.quit()
        

game = Game()
if __name__ == '__main__':
    game.run()

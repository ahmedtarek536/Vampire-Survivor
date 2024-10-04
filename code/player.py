import pygame
from settings import *


class Player(pygame.sprite.Sprite):
    def __init__(self, pos ,groups , collision_sprites):
        super().__init__(groups)
        self.health = 100
        self.state , self.frame_index = 'down' , 0
        self.load_images()
        self.image = pygame.image.load(join('images','player','down','0.png')).convert_alpha()
        self.rect = self.image.get_rect(center = pos)
        self.hitbox_rect = self.rect.inflate(-60,-60)
        self.direction = pygame.math.Vector2(0,0)
        self.speed = 400 
        self.collision_sprites = collision_sprites
        
    def load_images(self):
        self.frames = {'left':[], 'right':[], 'down':[] ,'up':[]}
        for state in self.frames.keys():
          for folder_path , sub_folder , file_names in list(walk(join("images" , "player" , state))):
            if file_names:
                for file_name in sorted(file_names , key= lambda name: int(name.split('.')[0])):
                    full_path = join(folder_path , file_name)
                    surf = pygame.image.load(full_path).convert_alpha()
                    self.frames[state].append(surf)
            

    def input(self):
        keys = pygame.key.get_pressed()
        self.speed = 700 if keys[pygame.K_SPACE] else 400
        self.direction.x = int(keys[pygame.K_RIGHT] or keys[pygame.K_d]) - int(keys[pygame.K_LEFT] or keys[pygame.K_a])
        self.direction.y = int(keys[pygame.K_DOWN] or keys[pygame.K_s]) - int(keys[pygame.K_UP] or keys[pygame.K_w])
        self.direction = self.direction.normalize() if self.direction else self.direction

    def move(self,  dt):
        self.hitbox_rect.x += self.direction.x * self.speed * dt
        self.collision('horizontal')
        self.hitbox_rect.y += self.direction.y * self.speed * dt
        self.collision('vertical')
        self.rect.center =  self.hitbox_rect.center 

    def collision(self, direction):
        for sprite in self.collision_sprites:
            if sprite.rect.colliderect(self.hitbox_rect):
                if direction == "horizontal":
                    if self.direction.x > 0: self.hitbox_rect.right = sprite.rect.left
                    if self.direction.x < 0: self.hitbox_rect.left = sprite.rect.right
                else:
                    if self.direction.y > 0: self.hitbox_rect.bottom = sprite.rect.top
                    if self.direction.y < 0: self.hitbox_rect.top = sprite.rect.bottom
                        
    def animate(self, dt):
        if self.direction.x != 0:
            self.state = 'right' if self.direction.x > 0 else 'left'
        if self.direction.y !=0:
            self.state = 'down' if self.direction.y >0 else 'up'
        self.frame_index += 5 * dt if self.direction else 0
        self.image = self.frames[self.state][int(self.frame_index) % len(self.frames[self.state])]
    
    def update(self, dt):
        self.input()
        self.move(dt)
        self.animate(dt)

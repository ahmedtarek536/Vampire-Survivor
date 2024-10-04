from typing import Any
from settings import * 
from math import atan2, degrees




class Ground(pygame.sprite.Sprite):
    def __init__(self, pos, surf, groups):
        super().__init__(groups)
        self.image =  surf
        self.rect = self.image.get_rect(topleft = pos)
        self.ground = True
    

class CollisionSprites(pygame.sprite.Sprite):
    def __init__(self, pos, surf, groups ):
        super().__init__(groups)
        self.image =  surf
        self.rect = self.image.get_rect(topleft = pos)


        
   
      
    


class Gun(pygame.sprite.Sprite):
    def __init__(self, player, groups ):
        self.player = player
        self.distance = 100
        self.player_direction = pygame.Vector2(0,0)
        super().__init__(groups)
        self.gun_surf = pygame.transform.scale(pygame.image.load(join("images" , "gun" , "gun.png")).convert_alpha() , (100,60))
        self.image = self.gun_surf
        self.rect = self.image.get_rect(center = self.player.rect.center + self.distance * self.player_direction)
    
    def get_direction(self):
        mouse_pos = (pygame.Vector2(pygame.mouse.get_pos()))
        player_pos = pygame.Vector2(WINDOW_WIDTH /2 , WINDOW_HEIGHT/2)
        self.player_direction = (mouse_pos - player_pos).normalize()
    def rotate_gun(self):
        angle = degrees(atan2(self.player_direction.x , self.player_direction.y)) - 90
        if self.player_direction.x > 0:
            self.image = pygame.transform.rotozoom(self.gun_surf , angle , 1)
        else:
            self.image = pygame.transform.rotozoom(self.gun_surf , abs(angle) , 1)
            self.image = pygame.transform.flip(self.image, False, True)

    def update(self, dt):
        self.get_direction()
        self.rotate_gun()
        self.rect.center = self.player.rect.center + self.player_direction * self.distance



class Bullet(pygame.sprite.Sprite):
    def __init__(self, surf, pos, direction, groups):
        super().__init__(groups)
        self.image = surf
        self.rect = self.image.get_rect(center = pos)
        self.spawn_time = pygame.time.get_ticks()
        self.life_time = 1000

        self.direction = direction
        self.speed = 1200

    def update(self, dt):
        self.rect.center += self.direction * self.speed * dt

        if pygame.time.get_ticks() - self.spawn_time >= self.life_time:
            self.kill()



class Enemy(pygame.sprite.Sprite):
    def __init__(self, pos, frames, groups, player, collision_sprites):
        super().__init__(groups)
        self.player = player

        self.farmes , self.frames_index = frames, 0
        self.image = self.farmes[self.frames_index]
        self.animation_speed = 6

        self.rect = self.image.get_rect(center = pos)
        self.hitbox_rect = self.rect.inflate(-20 , -40)
        self.collision_sprites = collision_sprites
        self.direction = pygame.Vector2()
        self.speed = 200

        self.death_time = 0
        self.death_duration = 100
    def animate(self, dt):
        self.frames_index += self.animation_speed * dt
        self.image = self.farmes[int(self.frames_index % len(self.farmes))]

    def move(self, dt):
        player_pos = pygame.Vector2(self.player.rect.center)
        enemy_pos =pygame.Vector2(self.rect.center)
        pos = (player_pos -enemy_pos)
        self.direction = pos.normalize() if pos else pos

        self.hitbox_rect.x += self.direction.x * self.speed * dt
        self.collisions('horizontal')
        self.hitbox_rect.y += self.direction.y * self.speed * dt
        self.collisions('vertical')
        self.rect.center = self.hitbox_rect.center
    
    def collisions(self, direction):
         for sprite in self.collision_sprites:
            if sprite.rect.colliderect(self.hitbox_rect):
                if direction == "horizontal":
                    if self.direction.x > 0: self.hitbox_rect.right = sprite.rect.left
                    if self.direction.x < 0: self.hitbox_rect.left = sprite.rect.right
                else:
                    if self.direction.y > 0: self.hitbox_rect.bottom = sprite.rect.top
                    if self.direction.y < 0: self.hitbox_rect.top = sprite.rect.bottom
    def destroy(self):
        self.death_time = pygame.time.get_ticks()
        surf = pygame.mask.from_surface(self.farmes[0]).to_surface()
        surf.set_colorkey('black')
        self.image = surf
    def death_timer(self):
        if pygame.time.get_ticks() - self.death_time >= self.death_duration:
            self.kill()
    def update(self, dt):
        if self.death_time == 0:
          self.move(dt)
          self.animate(dt)
        else: self.death_timer()

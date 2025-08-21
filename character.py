from constants import *
import pygame
class Character:
    def __init__(self, x, y):
        self.playerright = pygame.image.load("assets/yoshi_right.png")
        self.playerright = pygame.transform.scale(self.playerright, (int(2224/20), int(2632/20)))
        self.playerleft = pygame.image.load("assets/yoshi_left.png")
        self.playerleft = pygame.transform.scale(self.playerleft, (int(2224/20), int(2632/20)))
        
        self.x = x
        self.y = y
        # Use the actual sprite size for collisions
        self.width = self.playerright.get_width()
        self.height = self.playerright.get_height()
        self.speed = CHARACTER_SPEED
        self.velocity_x = 0
        self.velocity_y = 0
        self.on_ground = True
        self.on_platform = False
        self.jump_power = -15
        self.gravity = 0.5
        self.direction = 'right'
        self.prev_y = y
        self.accelerate = 0.15
        self.decelerate = 0.18


    def update(self):
        # Remember previous vertical position for swept collisions
        self.prev_y = self.y

        # Handle horizontal movement
        self.x += self.velocity_x
        
        # Handle vertical movement (gravity and jumping)
        if not self.on_ground:
            self.velocity_y += self.gravity

        self.y += self.velocity_y

        # Ground collision
        ground_y = SCREEN_HEIGHT - GROUND_HEIGHT - self.height
        if self.y >= ground_y:
            self.y = ground_y
            self.velocity_y = 0
            self.on_ground = True
            self.on_platform = False

        # Keep character on screen horizontally
        if self.x < 0:
            self.x = 0
        elif self.x > SCREEN_WIDTH - self.width:
            self.x = SCREEN_WIDTH - self.width

    def jump(self):
        if self.on_ground:
            self.velocity_y = self.jump_power
            self.on_ground = False
            self.on_platform = False

    def move_left(self):
        self.velocity_x -=  self.accelerate
        if self.velocity_x < -self.speed:
            self.velocity_x = -self.speed
        self.direction = 'left'
    def move_right(self):
        self.velocity_x +=  self.accelerate
        if self.velocity_x > self.speed:
            self.velocity_x = self.speed
        self.direction = 'right'
    def stop_horizontal_movement(self):
        if self.direction == 'right':
            self.velocity_x -= self.decelerate 
            if self.velocity_x < 0:
                self.velocity_x = 0
        else :
            self.velocity_x += self.decelerate
            if self.velocity_x > 0:
                self.velocity_x = 0

    def draw(self, screen):
        if self.direction == 'right':
            screen.blit(self.playerright, (self.x, self.y))
            
        if self.direction == 'left':
            screen.blit(self.playerleft, (self.x, self.y))

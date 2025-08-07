from constants import *
import pygame
class Character:
    def __init__(self, x, y):
        self.player_image = pygame.image.load("assets/yoshi.png")
        self.player_image = pygame.transform.scale(self.player_image, (2224/20, 2632/20))
        self.x = x
        self.y = y
        self.width = CHARACTER_WIDTH
        self.height = CHARACTER_HEIGHT
        self.speed = CHARACTER_SPEED
        self.velocity_x = 0
        self.velocity_y = 0
        self.on_ground = True
        self.jump_power = -15
        self.gravity = 0.5

    def update(self):
        # Handle horizontal movement
        self.x += self.velocity_x
        print(self.x , self.y)
        
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

        # Keep character on screen horizontally
        if self.x < 0:
            self.x = 0
        elif self.x > SCREEN_WIDTH - self.width:
            self.x = SCREEN_WIDTH - self.width

    def jump(self):
        if self.on_ground:
            self.velocity_y = self.jump_power
            self.on_ground = False

    def move_left(self):
        self.velocity_x = -self.speed

    def move_right(self):
        self.velocity_x = self.speed

    def stop_horizontal_movement(self):
        self.velocity_x = 0

    def draw(self, screen):
        screen.blit(self.player_image, (self.x, self.y - 80))

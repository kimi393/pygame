import pygame
import sys

# Initialize Pygame
pygame.init()

# Constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
GROUND_HEIGHT = 100

# Load assets
try:
    sun_image = pygame.image.load("assets/sun.png")
    # Scale the sun image to a reasonable size (you can adjust this)
    sun_image = pygame.transform.scale(sun_image, (80, 80))
except pygame.error:
    print("Could not load sun.png - using yellow circle instead")
    sun_image = None

# Colors
WHITE = (255, 255, 255)
BLUE = (0, 100, 255)
GREEN = (34, 139, 34)
YELLOW = (255, 255, 0)

# Character properties
CHARACTER_WIDTH = 40
CHARACTER_HEIGHT = 40
CHARACTER_SPEED = 5


class Character:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = CHARACTER_WIDTH
        self.height = CHARACTER_HEIGHT
        self.speed = CHARACTER_SPEED
        self.velocity_x = 0
        self.velocity_y = 0
        self.on_ground = True
        self.jump_power = -15
        self.gravity = 0.8

    def update(self):
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
        pygame.draw.rect(
            screen, BLUE, (self.x, self.y, self.width, self.height))


def draw_sun(screen):
    """Draw the sun in the top left corner"""
    sun_x = 20  # 20 pixels from left edge
    sun_y = 20  # 20 pixels from top edge

    if sun_image is not None:
        # Draw the loaded sun image
        screen.blit(sun_image, (sun_x, sun_y))
    else:
        # Fallback: draw a yellow circle if image couldn't be loaded
        pygame.draw.circle(screen, YELLOW, (sun_x + 40, sun_y + 40), 40)


def main():
    # Create the screen
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Blue Character Running Game")
    clock = pygame.time.Clock()

    # Create character
    character = Character(100, SCREEN_HEIGHT -
                          GROUND_HEIGHT - CHARACTER_HEIGHT)

    # Game loop
    running = True
    while running:
        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    character.jump()

        # Handle continuous key presses
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            character.move_left()
        elif keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            character.move_right()
        else:
            character.stop_horizontal_movement()

        # Update game objects
        character.update()

        # Clear screen with white background
        screen.fill(WHITE)

        # Draw green ground plane
        pygame.draw.rect(screen, GREEN, (0, SCREEN_HEIGHT -
                         GROUND_HEIGHT, SCREEN_WIDTH, GROUND_HEIGHT))

        # Draw sun in top left corner
        draw_sun(screen)

        # Draw character
        character.draw(screen)

        # Update display
        pygame.display.flip()

        clock.tick(60)  # 60 FPS

    # Quit
    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()

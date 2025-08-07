import pygame
import sys

from constants import *
from character import Character

# Initialize Pygame
pygame.init()

# Load assets
try:
    sun_image = pygame.image.load("assets/sun.png")
    # Scale the sun image to a reasonable size (you can adjust this)
    sun_image = pygame.transform.scale(sun_image, (342/4,262/4))
except:
    print("Could not load sun.png - using yellow circle instead")
    sun_image = None



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

def draw_clouds(screen, cloud_color, cloud_x, cloud_y):
    pygame.draw.circle(screen, cloud_color, (cloud_x, cloud_y), 40)  # Main center circle
    pygame.draw.circle(screen, cloud_color, (cloud_x - 30, cloud_y + 10), 30) # Left bottom
    pygame.draw.circle(screen, cloud_color, (cloud_x + 30, cloud_y + 10), 30) # Right bottom
    pygame.draw.circle(screen, cloud_color, (cloud_x - 15, cloud_y - 20), 35) # Left top
    pygame.draw.circle(screen, cloud_color, (cloud_x + 15, cloud_y - 20), 35) # Right top


def draw(screen, character):
    # Clear screen with white background
    screen.fill(SKYBLUE)

    # Draw green ground plane
    pygame.draw.rect(screen, GREEN, (0, SCREEN_HEIGHT -
                    GROUND_HEIGHT, SCREEN_WIDTH, GROUND_HEIGHT))

    pygame.draw.rect(screen, GREEN, (600,400,100,50))

    # Draw sun in top left corner
    draw_sun(screen)

    # Draw character
    character.draw(screen)

    draw_clouds(screen,(155, 232, 232),300,150)
    draw_clouds(screen,(155, 232, 232),500,185)
    # Update display
    pygame.display.flip()

    

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
        draw(screen, character)
        
        clock.tick(60)  # 60 FPS

    # Quit
    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()

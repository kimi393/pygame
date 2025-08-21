import pygame
import sys

from constants import *
from character import Character

pygame.mixer.init()
pygame.mixer.music.load("assets/yoshi!.mp3")  # Put your music file in the same folder
pygame.mixer.music.play(-1)  

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


def draw(screen, character, platforms, timer):
    # Clear screen with white background
    screen.fill(SKYBLUE)

    # Draw green ground plane
    pygame.draw.rect(screen, GREEN, (0, SCREEN_HEIGHT -
                    GROUND_HEIGHT, SCREEN_WIDTH, GROUND_HEIGHT))

    # Draw all platforms
    for plat in platforms:
        pygame.draw.rect(screen, GREEN, plat)

    # Draw sun in top left corner
    draw_sun(screen)

    draw_clouds(screen,(155, 232, 232),300,150)
    draw_clouds(screen,(155, 232, 232),500,185)
    # Draw character
    character.draw(screen)
    font = pygame.font.SysFont("Arial", 40)
    text = font.render(f"time: {timer:.1f}",True, WHITE)
    screen.blit(text, (350,0))
    # Update display
    pygame.display.flip()

    

def main():
    # Create the screen
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("yoshi Running Game")
    clock = pygame.time.Clock()
    timer = TIME
    # Create character
    character = Character(100, SCREEN_HEIGHT -
                          GROUND_HEIGHT - CHARACTER_HEIGHT)
    # Align start so sprite feet sit on ground
    character.y = SCREEN_HEIGHT - GROUND_HEIGHT - character.height

    # Define platforms
    platforms = [
        pygame.Rect(500, 400, 80, 50),
        pygame.Rect(200, 320, 120, 40),
    ]

    # Game loop
    running = True
    while running:
        last_key = None
        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    character.jump()
        timer -= (1 / 60)
        
        if timer <= 0:
            pygame.quit()
            sys.exit()
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

        # Platform collision logic (swept test to avoid tunneling) for multiple platforms
        char_left = character.x
        char_right = character.x + character.width

        prev_bottom = character.prev_y + character.height
        curr_bottom = character.y + character.height
        falling = character.velocity_y > 0

        # Try to land on any platform when crossing its top while falling
        if falling:
            for plat in platforms:
                plat_left = plat.left
                plat_right = plat.right
                horizontal_overlap = (char_right > plat_left) and (char_left < plat_right)
                if horizontal_overlap and prev_bottom <= plat.top and curr_bottom >= plat.top:
                    character.y = plat.top - character.height
                    character.velocity_y = 0
                    character.on_ground = True
                    character.on_platform = True
                    break

        # If currently on a platform but no longer overlapping any, start falling
        if character.on_platform:
            overlapping_any = False
            for plat in platforms:
                if (char_right > plat.left) and (char_left < plat.right):
                    # also ensure we are at the platform height
                    if abs((character.y + character.height) - plat.top) < 1e-3:
                        overlapping_any = True
                        break
            if not overlapping_any:
                character.on_ground = False
                character.on_platform = False

        draw(screen, character, platforms, timer)
        
        clock.tick(60)  # 60 FPS

    # Quit
    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()

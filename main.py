import pygame
import os
import sys
import random

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

# Load coin asset
try:
    coin_image_raw = pygame.image.load("assets/coin.png")
    COIN_SIZE = 32
    coin_image = pygame.transform.scale(coin_image_raw, (COIN_SIZE, COIN_SIZE))
except:
    print("Could not load coin.png - using yellow circle for coins")
    coin_image = None
    COIN_SIZE = 20

# Coin placement tuning
GROUND_COIN_LIMIT = 3  # maximum coins allowed on the ground at once
COIN_PAD = 6          # minimum pixel padding between coin edges


def _fits_without_overlap(rect, others, avoid_rects=None, pad: int = COIN_PAD):
    # Inflate candidate by padding to keep some visual spacing
    candidate = rect.inflate(pad * 2, pad * 2)
    for o in others:
        if candidate.colliderect(o):
            return False
    if avoid_rects:
        for a in avoid_rects:
            if candidate.colliderect(a):
                return False
    return True


def spawn_coin(platforms, existing_coins, avoid_rects=None, yoshi_platform=None, strict_avoid_platform=False, max_attempts: int = 120):
    """Return a new non-overlapping coin Rect, avoiding Yoshi and biased off crowded floor.

    avoid_rects: list of rects to avoid (e.g., Yoshi inflated rect)
    yoshi_platform: platform Rect Yoshi stands on; prefer other platforms
    strict_avoid_platform: if True, never use Yoshi's platform when alternatives exist
    """
    ground_y = SCREEN_HEIGHT - GROUND_HEIGHT - COIN_SIZE
    total = len(existing_coins)
    ground_count = sum(1 for c in existing_coins if c.y == ground_y)
    desired_ground_ratio = 0.3
    prefer_platform = bool(platforms) and (total > 0 and (ground_count / total) > desired_ground_ratio)

    for _ in range(max_attempts):
        choose_platform = bool(platforms) and (prefer_platform or random.random() < 0.85)

        if choose_platform:
            candidate_platforms = platforms
            if yoshi_platform is not None and len(platforms) > 1:
                # Prefer a platform different from the one Yoshi is standing on
                others = [p for p in platforms if p is not yoshi_platform]
                if others:
                    candidate_platforms = others
            if strict_avoid_platform and yoshi_platform is not None and len(candidate_platforms) > 1:
                candidate_platforms = [p for p in candidate_platforms if p is not yoshi_platform] or candidate_platforms
            plat = random.choice(candidate_platforms)
            start_x = plat.x + 10
            end_x = plat.right - COIN_SIZE - 10
            if start_x <= end_x:
                x = random.randint(start_x, end_x)
                y = plat.y - COIN_SIZE
                candidate = pygame.Rect(x, y, COIN_SIZE, COIN_SIZE)
                if _fits_without_overlap(candidate, existing_coins, avoid_rects):
                    return candidate
            # if not placed, continue to next attempt (try another platform or ground next loop)
            continue

        # Ground attempt (respect limit)
        ground_count = sum(1 for c in existing_coins if c.y == ground_y)
        if ground_count < GROUND_COIN_LIMIT or not platforms:
            x = random.randint(10, max(10, SCREEN_WIDTH - COIN_SIZE - 10))
            candidate = pygame.Rect(x, ground_y, COIN_SIZE, COIN_SIZE)
            if _fits_without_overlap(candidate, existing_coins, avoid_rects):
                return candidate
    # Fallback deterministic scan: try platforms then ground
    # Prefer not Yoshi's current platform if possible
    ordered_platforms = list(platforms)
    if yoshi_platform in ordered_platforms and len(ordered_platforms) > 1:
        ordered_platforms = [p for p in ordered_platforms if p is not yoshi_platform] + [yoshi_platform]
    if strict_avoid_platform and yoshi_platform is not None and len(ordered_platforms) > 1:
        ordered_platforms = [p for p in ordered_platforms if p is not yoshi_platform] + [yoshi_platform]

    # First pass: respect avoid rects
    for plat in ordered_platforms:
        start_x = plat.x + 10
        end_x = plat.right - COIN_SIZE - 10
        for x in range(start_x, end_x + 1, max(10, COIN_SIZE)):
            candidate = pygame.Rect(x, plat.y - COIN_SIZE, COIN_SIZE, COIN_SIZE)
            if _fits_without_overlap(candidate, existing_coins, avoid_rects):
                return candidate
    # Only scan ground if under the limit or there are no platforms
    ground_count = sum(1 for c in existing_coins if c.y == ground_y)
    if ground_count < GROUND_COIN_LIMIT or not platforms:
        for x in range(10, SCREEN_WIDTH - COIN_SIZE - 10 + 1, COIN_SIZE + COIN_PAD):
            candidate = pygame.Rect(x, ground_y, COIN_SIZE, COIN_SIZE)
            if _fits_without_overlap(candidate, existing_coins, avoid_rects):
                return candidate

    # Second pass: ignore avoid rects to guarantee a spot (still tries to avoid Yoshi platform)
    for plat in ordered_platforms:
        start_x = plat.x + 10
        end_x = plat.right - COIN_SIZE - 10
        for x in range(start_x, end_x + 1, max(10, COIN_SIZE)):
            candidate = pygame.Rect(x, plat.y - COIN_SIZE, COIN_SIZE, COIN_SIZE)
            if _fits_without_overlap(candidate, existing_coins, None):
                return candidate
    if ground_count < GROUND_COIN_LIMIT or not platforms:
        for x in range(10, SCREEN_WIDTH - COIN_SIZE - 10 + 1, COIN_SIZE + COIN_PAD):
            candidate = pygame.Rect(x, ground_y, COIN_SIZE, COIN_SIZE)
            if _fits_without_overlap(candidate, existing_coins, None):
                return candidate
    return None


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


def draw(screen, character, platforms, timer, coins, score, game_state=None):
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

    # Draw coins
    for coin in coins:
        if coin_image is not None:
            screen.blit(coin_image, (coin.x, coin.y))
        else:
            pygame.draw.circle(screen, YELLOW, (coin.x + COIN_SIZE//2, coin.y + COIN_SIZE//2), COIN_SIZE//2)
    # Draw character
    character.draw(screen)
    font = pygame.font.SysFont("Arial", 40)
    text = font.render(f"time: {timer:.1f}",True, WHITE)
    screen.blit(text, (350,0))
    score_text = font.render(f"coins: {score}", True, WHITE)
    screen.blit(score_text, (10, 70))
    # End-state overlay
    if game_state in ("win", "lose"):
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(140)
        overlay.fill((0, 0, 0))
        screen.blit(overlay, (0, 0))

        big_font = pygame.font.SysFont("Arial", 64, bold=True)
        small_font = pygame.font.SysFont("Arial", 28)
        title = "You Win!" if game_state == "win" else "Time's Up!"
        t_surface = big_font.render(title, True, WHITE)
        screen.blit(t_surface, (SCREEN_WIDTH//2 - t_surface.get_width()//2, SCREEN_HEIGHT//2 - 100))

        info_lines = [
            f"Coins: {score}  Time left: {max(0.0, timer):.1f}s",
            "Press R to restart, or ESC to quit",
        ]
        for i, line in enumerate(info_lines):
            s = small_font.render(line, True, (230, 230, 230))
            screen.blit(s, (SCREEN_WIDTH//2 - s.get_width()//2, SCREEN_HEIGHT//2 - 10 + i*36))

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

    def generate_initial_coins():
        coins_local = []
        # Ground coins: keep just a few to avoid clutter
        ground_y = SCREEN_HEIGHT - GROUND_HEIGHT - COIN_SIZE
        for x in (100, SCREEN_WIDTH // 2 - COIN_SIZE // 2, SCREEN_WIDTH - 150):
            c = pygame.Rect(max(10, min(x, SCREEN_WIDTH - COIN_SIZE - 10)), ground_y, COIN_SIZE, COIN_SIZE)
            if _fits_without_overlap(c, coins_local):
                coins_local.append(c)

        # Multiple coins on platforms (rows across each platform)
        for plat in platforms:
            cy = plat.y - COIN_SIZE
            start_x = plat.x + 10
            end_x = plat.right - COIN_SIZE - 10
            for cx in range(start_x, end_x + 1, 40):
                c = pygame.Rect(cx, cy, COIN_SIZE, COIN_SIZE)
                if _fits_without_overlap(c, coins_local):
                    coins_local.append(c)

        # Floating arcs of coins for jumps
        arc1_origin = (300, 350)
        for i in range(6):
            ax = arc1_origin[0] + i * 30
            ay = arc1_origin[1] - (i - 2) * (i - 2) * 6 - COIN_SIZE
            c = pygame.Rect(ax, ay, COIN_SIZE, COIN_SIZE)
            if _fits_without_overlap(c, coins_local):
                coins_local.append(c)

        arc2_origin = (550, 300)
        for i in range(6):
            ax = arc2_origin[0] + i * 28
            ay = arc2_origin[1] - (i - 2) * (i - 2) * 5 - COIN_SIZE
            c = pygame.Rect(ax, ay, COIN_SIZE, COIN_SIZE)
            if _fits_without_overlap(c, coins_local):
                coins_local.append(c)
        return coins_local

    coins = generate_initial_coins()
    score = 0
    target_coin_count = len(coins)
    pending_respawns = []
    game_state = "playing"
    pending_respawns = []  # schedule coin respawns to reduce farming

    # Prepare ding sound for coin pickups (tries mp3/ogg/wav, then fallback synth)
    ding_sound = None
    for filename in ("assets/ding.mp3", "assets/ding.ogg", "assets/ding.wav"):
        try:
            if os.path.exists(filename):
                ding_sound = pygame.mixer.Sound(filename)
                break
        except Exception:
            ding_sound = None

    if ding_sound is None:
        # Fallback: synthesize a short beep tone
        try:
            import math
            import array
            mix_init = pygame.mixer.get_init()
            if mix_init is not None:
                sample_rate, snd_size, channels = mix_init
            else:
                sample_rate, snd_size, channels = 44100, -16, 2

            tone_hz = 880
            duration = 0.09  # seconds
            n_samples = int(sample_rate * duration)
            amplitude = 2**15 - 1 if snd_size in (-16, 16) else 127

            samples = array.array('h') if snd_size in (-16, 16) else array.array('b')
            for i in range(n_samples):
                s = int(amplitude * 0.25 * math.sin(2 * math.pi * tone_hz * (i / sample_rate)))
                if channels == 1:
                    samples.append(s)
                else:
                    samples.append(s)
                    samples.append(s)
            try:
                ding_sound = pygame.mixer.Sound(buffer=samples)
            except Exception:
                ding_sound = None
        except Exception:
            ding_sound = None

    # Game loop
    running = True
    while running:
        last_key = None
        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit(); sys.exit()
                if game_state == "playing":
                    if event.key == pygame.K_SPACE:
                        character.jump()
                elif event.key == pygame.K_r:
                    # Reset state
                    timer = TIME
                    character = Character(100, SCREEN_HEIGHT - GROUND_HEIGHT - CHARACTER_HEIGHT)
                    character.y = SCREEN_HEIGHT - GROUND_HEIGHT - character.height
                    coins = generate_initial_coins()
                    score = 0
                    target_coin_count = len(coins)
                    pending_respawns = []
                    game_state = "playing"

        if game_state == "playing":
            timer -= (1 / 60)
            # Handle continuous key presses
            keys = pygame.key.get_pressed()
            if keys[pygame.K_LEFT] or keys[pygame.K_a]:
                character.move_left()
            elif keys[pygame.K_RIGHT] or keys[pygame.K_d]:
                character.move_right()
            else:
                character.stop_horizontal_movement()

        # Update game objects
        if game_state == "playing":
            character.update()

        # Platform collision logic (swept test to avoid tunneling) for multiple platforms
        char_left = character.x
        char_right = character.x + character.width

        prev_bottom = character.prev_y + character.height
        curr_bottom = character.y + character.height
        falling = character.velocity_y > 0

        # Try to land on any platform when crossing its top while falling
        if game_state == "playing" and falling:
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
        if game_state == "playing" and character.on_platform:
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

        if game_state == "playing":
            # Coin collection: check collision with character (infinite respawn, no overlap, avoid Yoshi)
            char_rect = pygame.Rect(int(character.x), int(character.y), int(character.width), int(character.height))
            survivors = []
            collected = 0
            for coin in coins:
                if char_rect.colliderect(coin):
                    score += 1
                    collected += 1
                    if ding_sound is not None:
                        ding_sound.play()
                else:
                    survivors.append(coin)
            # Queue respawn and determine current platform
            now_ms = pygame.time.get_ticks()
            for i in range(collected):
                pending_respawns.append(now_ms + 400 + i * 120)

            # Determine current platform Yoshi stands on (if any)
            current_platform = None
            if character.on_platform:
                for plat in platforms:
                    if (char_rect.right > plat.left) and (char_rect.left < plat.right):
                        if abs((character.y + character.height) - plat.top) < 1e-3:
                            current_platform = plat
                            break
            avoid = [char_rect.inflate(250, 150)]
            # Spawn any pending coins whose delay has elapsed
            ready_times = [t for t in pending_respawns if t <= now_ms]
            pending_respawns = [t for t in pending_respawns if t > now_ms]
            for _ in ready_times:
                new_coin = spawn_coin(platforms, survivors, avoid_rects=avoid, yoshi_platform=current_platform, strict_avoid_platform=True)
                if new_coin is None:
                    new_coin = spawn_coin(platforms, survivors, avoid_rects=None, yoshi_platform=current_platform, strict_avoid_platform=True)
                if new_coin is None:
                    new_coin = spawn_coin(platforms, survivors, avoid_rects=None, yoshi_platform=None, strict_avoid_platform=False)
                if new_coin is not None:
                    survivors.append(new_coin)
            coins = survivors

            # Check win/lose conditions
            if score >= WIN_COINS:
                game_state = "win"
            elif timer <= 0:
                game_state = "lose"

        draw(screen, character, platforms, timer, coins, score, game_state)
        
        clock.tick(60)  # 60 FPS

    # Quit
    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()

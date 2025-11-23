"""
Space Invaders Demo for 16x16 NeoPixel Matrix
Raspberry Pi Pico 2W - MicroPython

Auto-play demo with optional button controls:
- GPIO 2: Move Left
- GPIO 3: Move Right
- GPIO 4: Fire
"""

import machine
import neopixel
import time
import random

# ============================================
# CONFIGURATION
# ============================================
WIDTH = 16
HEIGHT = 16
NUM_LEDS = WIDTH * HEIGHT
PIN = 0
BRIGHTNESS = 0.3

# Optional button pins (leave unconnected for auto-play)
BTN_LEFT = 2
BTN_RIGHT = 3
BTN_FIRE = 4

# Initialize NeoPixel
pin = machine.Pin(PIN, machine.Pin.OUT)
np = neopixel.NeoPixel(pin, NUM_LEDS)

# Button setup (with pull-up, active low)
try:
    btn_left = machine.Pin(BTN_LEFT, machine.Pin.IN, machine.Pin.PULL_UP)
    btn_right = machine.Pin(BTN_RIGHT, machine.Pin.IN, machine.Pin.PULL_UP)
    btn_fire = machine.Pin(BTN_FIRE, machine.Pin.IN, machine.Pin.PULL_UP)
    BUTTONS_ENABLED = True
except:
    BUTTONS_ENABLED = False

# ============================================
# COLORS
# ============================================
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)
CYAN = (0, 255, 255)
MAGENTA = (255, 0, 255)
ORANGE = (255, 150, 0)

# Alien colors by row
ALIEN_COLORS = [MAGENTA, CYAN, GREEN, YELLOW, ORANGE]

# ============================================
# COORDINATE MAPPING
# ============================================
def xy_to_index(x, y):
    """Convert x,y to LED index (serpentine layout)"""
    if x < 0 or x >= WIDTH or y < 0 or y >= HEIGHT:
        return -1
    if y % 2 == 0:
        return y * WIDTH + x
    else:
        return y * WIDTH + (WIDTH - 1 - x)

def scale_color(color):
    """Apply brightness scaling"""
    return tuple(int(c * BRIGHTNESS) for c in color)

def set_pixel(x, y, color):
    """Set pixel at x,y with bounds checking"""
    idx = xy_to_index(x, y)
    if idx >= 0:
        np[idx] = scale_color(color)

def clear():
    """Clear the display"""
    np.fill((0, 0, 0))

def show():
    """Update the display"""
    np.write()

# ============================================
# GAME SPRITES (relative coordinates)
# ============================================

# Player ship (3 pixels wide)
PLAYER_SPRITE = [(0, 0), (-1, 0), (1, 0), (0, -1)]

# Alien types (different shapes)
ALIEN_SPRITE_1 = [(-1, 0), (0, 0), (1, 0), (-1, -1), (1, -1)]  # Squid
ALIEN_SPRITE_2 = [(-1, 0), (0, 0), (1, 0), (0, -1)]  # Crab
ALIEN_SPRITE_3 = [(0, 0), (-1, -1), (1, -1)]  # Small

# ============================================
# GAME STATE
# ============================================
class Game:
    def __init__(self):
        self.reset()

    def reset(self):
        # Player
        self.player_x = WIDTH // 2
        self.player_y = HEIGHT - 1
        self.player_alive = True

        # Bullets
        self.player_bullets = []  # [(x, y), ...]
        self.alien_bullets = []

        # Aliens: list of (x, y, alive, sprite_type)
        self.aliens = []
        self.alien_direction = 1  # 1 = right, -1 = left
        self.alien_drop = False

        # Score and level
        self.score = 0
        self.level = 1
        self.game_over = False
        self.victory = False

        # Timing
        self.last_alien_move = 0
        self.last_alien_shot = 0
        self.alien_speed = 400  # ms between moves

        # Auto-play
        self.auto_target_x = self.player_x
        self.auto_fire_cooldown = 0

        # Spawn aliens
        self.spawn_aliens()

    def spawn_aliens(self):
        """Create alien formation"""
        self.aliens = []
        rows = min(3 + self.level // 2, 5)  # More rows at higher levels
        cols = min(6 + self.level, 11)  # More columns

        start_x = (WIDTH - cols * 2) // 2 + 1
        start_y = 1

        for row in range(rows):
            sprite_type = row % 3
            for col in range(cols):
                x = start_x + col * 2
                y = start_y + row * 2
                if x < WIDTH - 1:
                    self.aliens.append({
                        'x': x,
                        'y': y,
                        'alive': True,
                        'type': sprite_type
                    })

        # Adjust speed based on level
        self.alien_speed = max(150, 400 - self.level * 30)

# ============================================
# GAME LOGIC
# ============================================
game = Game()

def draw_player():
    """Draw the player ship"""
    if not game.player_alive:
        return

    for dx, dy in PLAYER_SPRITE:
        set_pixel(game.player_x + dx, game.player_y + dy, GREEN)

def draw_aliens():
    """Draw all living aliens"""
    for alien in game.aliens:
        if not alien['alive']:
            continue

        x, y = alien['x'], alien['y']
        color = ALIEN_COLORS[alien['type'] % len(ALIEN_COLORS)]

        # Choose sprite based on type
        if alien['type'] == 0:
            sprite = ALIEN_SPRITE_1
        elif alien['type'] == 1:
            sprite = ALIEN_SPRITE_2
        else:
            sprite = ALIEN_SPRITE_3

        for dx, dy in sprite:
            set_pixel(x + dx, y + dy, color)

def draw_bullets():
    """Draw all bullets"""
    for bx, by in game.player_bullets:
        set_pixel(bx, by, YELLOW)

    for bx, by in game.alien_bullets:
        set_pixel(bx, by, RED)

def move_player(direction):
    """Move player left (-1) or right (1)"""
    new_x = game.player_x + direction
    if 1 <= new_x <= WIDTH - 2:
        game.player_x = new_x

def fire_player():
    """Player fires a bullet"""
    if len(game.player_bullets) < 3:  # Max 3 bullets on screen
        game.player_bullets.append([game.player_x, game.player_y - 2])

def move_bullets():
    """Update bullet positions"""
    # Player bullets move up
    new_bullets = []
    for bullet in game.player_bullets:
        bullet[1] -= 1
        if bullet[1] >= 0:
            new_bullets.append(bullet)
    game.player_bullets = new_bullets

    # Alien bullets move down
    new_bullets = []
    for bullet in game.alien_bullets:
        bullet[1] += 1
        if bullet[1] < HEIGHT:
            new_bullets.append(bullet)
    game.alien_bullets = new_bullets

def move_aliens():
    """Move alien formation"""
    current_time = time.ticks_ms()

    if time.ticks_diff(current_time, game.last_alien_move) < game.alien_speed:
        return

    game.last_alien_move = current_time

    # Check if any alien hit the edge
    hit_edge = False
    for alien in game.aliens:
        if not alien['alive']:
            continue
        if alien['x'] <= 1 and game.alien_direction == -1:
            hit_edge = True
            break
        if alien['x'] >= WIDTH - 2 and game.alien_direction == 1:
            hit_edge = True
            break

    if hit_edge:
        # Drop down and reverse direction
        game.alien_direction *= -1
        for alien in game.aliens:
            if alien['alive']:
                alien['y'] += 1
                # Check if aliens reached bottom
                if alien['y'] >= HEIGHT - 2:
                    game.game_over = True
                    return
    else:
        # Move horizontally
        for alien in game.aliens:
            if alien['alive']:
                alien['x'] += game.alien_direction

def alien_shoot():
    """Random alien fires"""
    current_time = time.ticks_ms()

    shoot_interval = max(500, 1500 - game.level * 100)
    if time.ticks_diff(current_time, game.last_alien_shot) < shoot_interval:
        return

    game.last_alien_shot = current_time

    # Get alive aliens
    alive = [a for a in game.aliens if a['alive']]
    if not alive:
        return

    # Bottom aliens more likely to shoot
    bottom_aliens = {}
    for a in alive:
        col = a['x']
        if col not in bottom_aliens or a['y'] > bottom_aliens[col]['y']:
            bottom_aliens[col] = a

    if bottom_aliens:
        shooter = random.choice(list(bottom_aliens.values()))
        if len(game.alien_bullets) < 5:
            game.alien_bullets.append([shooter['x'], shooter['y'] + 1])

def check_collisions():
    """Check bullet collisions"""
    # Player bullets hit aliens
    for bullet in game.player_bullets[:]:
        bx, by = bullet
        for alien in game.aliens:
            if not alien['alive']:
                continue
            # Simple hit detection
            if abs(bx - alien['x']) <= 1 and abs(by - alien['y']) <= 1:
                alien['alive'] = False
                if bullet in game.player_bullets:
                    game.player_bullets.remove(bullet)
                game.score += 10 * (alien['type'] + 1)

                # Speed up remaining aliens
                alive_count = sum(1 for a in game.aliens if a['alive'])
                if alive_count > 0:
                    speed_factor = alive_count / len(game.aliens)
                    game.alien_speed = int(max(80, 400 * speed_factor))
                break

    # Alien bullets hit player
    for bullet in game.alien_bullets[:]:
        bx, by = bullet
        if abs(bx - game.player_x) <= 1 and abs(by - game.player_y) <= 1:
            game.player_alive = False
            game.game_over = True
            return

    # Check victory
    if all(not a['alive'] for a in game.aliens):
        game.victory = True

def auto_play():
    """AI player for demo mode"""
    # Find nearest alien above player
    target_x = game.player_x
    min_dist = 999

    alive_aliens = [a for a in game.aliens if a['alive']]
    for alien in alive_aliens:
        dist = abs(alien['x'] - game.player_x)
        if dist < min_dist:
            min_dist = dist
            target_x = alien['x']

    # Dodge incoming bullets
    for bx, by in game.alien_bullets:
        if by > HEIGHT - 4 and abs(bx - game.player_x) < 2:
            # Bullet incoming, dodge!
            if bx <= game.player_x:
                target_x = game.player_x + 2
            else:
                target_x = game.player_x - 2
            break

    # Move toward target
    if game.player_x < target_x:
        move_player(1)
    elif game.player_x > target_x:
        move_player(-1)

    # Fire when aligned with alien
    game.auto_fire_cooldown -= 1
    if game.auto_fire_cooldown <= 0:
        for alien in alive_aliens:
            if abs(alien['x'] - game.player_x) <= 1:
                fire_player()
                game.auto_fire_cooldown = 3
                break

def check_buttons():
    """Check button inputs"""
    if not BUTTONS_ENABLED:
        return False

    button_pressed = False
    if btn_left.value() == 0:
        move_player(-1)
        button_pressed = True
    if btn_right.value() == 0:
        move_player(1)
        button_pressed = True
    if btn_fire.value() == 0:
        fire_player()
        button_pressed = True

    return button_pressed

def draw_score():
    """Draw simple score indicator (top-right corner dots)"""
    # Show level as dots in corner
    for i in range(min(game.level, 3)):
        set_pixel(WIDTH - 1 - i, 0, WHITE)

def show_game_over():
    """Display game over animation"""
    # Red flash
    for _ in range(3):
        for y in range(HEIGHT):
            for x in range(WIDTH):
                set_pixel(x, y, RED)
        show()
        time.sleep(0.1)
        clear()
        show()
        time.sleep(0.1)

    # Show X pattern
    clear()
    for i in range(16):
        set_pixel(i, i, RED)
        set_pixel(15 - i, i, RED)
    show()
    time.sleep(2)

def show_victory():
    """Display victory animation"""
    # Rainbow celebration
    for offset in range(50):
        for y in range(HEIGHT):
            for x in range(WIDTH):
                hue = ((x + y + offset) * 8) % 256
                color = wheel(hue)
                set_pixel(x, y, color)
        show()
        time.sleep(0.05)

def wheel(pos):
    """Rainbow color wheel"""
    pos = pos % 256
    if pos < 85:
        return (255 - pos * 3, pos * 3, 0)
    elif pos < 170:
        pos -= 85
        return (0, 255 - pos * 3, pos * 3)
    else:
        pos -= 170
        return (pos * 3, 0, 255 - pos * 3)

def show_title():
    """Show title screen"""
    clear()

    # Draw simple alien face
    alien_x, alien_y = 7, 5
    for dx, dy in [(-3, 0), (-2, 0), (-1, 0), (0, 0), (1, 0), (2, 0), (3, 0),
                   (-2, -1), (2, -1), (-3, -2), (-1, -2), (1, -2), (3, -2),
                   (-2, 1), (-1, 1), (1, 1), (2, 1)]:
        set_pixel(alien_x + dx, alien_y + dy, GREEN)

    # Animate
    show()
    time.sleep(2)

    # Countdown
    for i in range(3, 0, -1):
        clear()
        # Simple number display
        cx, cy = 7, 7
        if i == 3:
            points = [(0,-2), (1,-2), (2,-2), (2,-1), (1,0), (2,1), (0,2), (1,2), (2,2)]
        elif i == 2:
            points = [(0,-2), (1,-2), (2,-2), (2,-1), (0,0), (1,0), (2,0), (0,1), (0,2), (1,2), (2,2)]
        else:
            points = [(1,-2), (1,-1), (1,0), (1,1), (1,2)]

        for dx, dy in points:
            set_pixel(cx + dx, cy + dy, YELLOW)
        show()
        time.sleep(0.7)

# ============================================
# MAIN GAME LOOP
# ============================================
def run_game():
    """Main game loop"""
    print("Space Invaders Demo Starting...")
    print("Connect buttons to GPIO 2,3,4 for manual control")
    print("Press Ctrl+C to stop")

    try:
        while True:
            # Title screen
            show_title()

            # Reset game
            game.reset()

            # Game loop
            while not game.game_over and not game.victory:
                # Clear screen
                clear()

                # Check inputs or auto-play
                if not check_buttons():
                    auto_play()

                # Update game state
                move_bullets()
                move_aliens()
                alien_shoot()
                check_collisions()

                # Draw everything
                draw_aliens()
                draw_bullets()
                draw_player()
                draw_score()

                # Update display
                show()

                # Frame delay
                time.sleep(0.05)

            # End game
            if game.victory:
                show_victory()
                game.level += 1
                game.victory = False
                game.game_over = False
                game.spawn_aliens()
                game.player_bullets = []
                game.alien_bullets = []
            else:
                show_game_over()
                game.level = 1

    except KeyboardInterrupt:
        print("\nGame stopped!")
        clear()
        show()
        print(f"Final Score: {game.score}")

if __name__ == "__main__":
    run_game()

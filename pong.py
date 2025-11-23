"""
Pong Demo for 16x16 NeoPixel Matrix
Raspberry Pi Pico 2W - MicroPython

Auto-play demo with optional button controls:
- GPIO 2: Player 1 Up
- GPIO 3: Player 1 Down
- GPIO 4: Player 2 Up
- GPIO 5: Player 2 Down
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

# Optional button pins
BTN_P1_UP = 2
BTN_P1_DOWN = 3
BTN_P2_UP = 4
BTN_P2_DOWN = 5

# Initialize NeoPixel
pin = machine.Pin(PIN, machine.Pin.OUT)
np = neopixel.NeoPixel(pin, NUM_LEDS)

# Button setup
try:
    btn_p1_up = machine.Pin(BTN_P1_UP, machine.Pin.IN, machine.Pin.PULL_UP)
    btn_p1_down = machine.Pin(BTN_P1_DOWN, machine.Pin.IN, machine.Pin.PULL_UP)
    btn_p2_up = machine.Pin(BTN_P2_UP, machine.Pin.IN, machine.Pin.PULL_UP)
    btn_p2_down = machine.Pin(BTN_P2_DOWN, machine.Pin.IN, machine.Pin.PULL_UP)
    BUTTONS_ENABLED = True
except:
    BUTTONS_ENABLED = False

# ============================================
# COLORS
# ============================================
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
BLUE = (0, 100, 255)
GREEN = (0, 255, 0)
YELLOW = (255, 255, 0)
CYAN = (0, 255, 255)
ORANGE = (255, 150, 0)

# ============================================
# DISPLAY FUNCTIONS
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
    idx = xy_to_index(int(x), int(y))
    if idx >= 0:
        np[idx] = scale_color(color)

def clear():
    """Clear the display"""
    np.fill((0, 0, 0))

def show():
    """Update the display"""
    np.write()

# ============================================
# GAME STATE
# ============================================
class PongGame:
    def __init__(self):
        self.reset()

    def reset(self):
        # Paddle settings
        self.paddle_height = 4
        self.paddle_speed = 1

        # Paddle positions (y coordinate of top of paddle)
        self.p1_y = (HEIGHT - self.paddle_height) // 2
        self.p2_y = (HEIGHT - self.paddle_height) // 2

        # Paddle x positions
        self.p1_x = 0
        self.p2_x = WIDTH - 1

        # Ball
        self.ball_x = WIDTH // 2
        self.ball_y = HEIGHT // 2
        self.ball_vx = random.choice([-1, 1]) * 0.8
        self.ball_vy = random.uniform(-0.5, 0.5)

        # Scores
        self.p1_score = 0
        self.p2_score = 0
        self.winning_score = 5

        # Game state
        self.game_over = False
        self.winner = None
        self.paused = False
        self.rally_count = 0

        # AI settings
        self.ai_reaction_delay = 2  # Frames before AI reacts
        self.ai_error = 0.3  # Chance of AI making mistake

    def reset_ball(self, direction=None):
        """Reset ball to center after score"""
        self.ball_x = WIDTH // 2
        self.ball_y = HEIGHT // 2

        if direction is None:
            direction = random.choice([-1, 1])

        self.ball_vx = direction * 0.8
        self.ball_vy = random.uniform(-0.4, 0.4)
        self.rally_count = 0

# ============================================
# GAME INSTANCE
# ============================================
game = PongGame()

# ============================================
# DRAWING FUNCTIONS
# ============================================
def draw_paddle(x, y, height, color):
    """Draw a vertical paddle"""
    for i in range(height):
        set_pixel(x, y + i, color)

def draw_ball(x, y, color):
    """Draw the ball"""
    set_pixel(int(x), int(y), color)

def draw_center_line():
    """Draw dashed center line"""
    for y in range(0, HEIGHT, 2):
        set_pixel(WIDTH // 2, y, (50, 50, 50))

def draw_score(score, x_start, color):
    """Draw score as vertical bar"""
    for i in range(min(score, HEIGHT)):
        set_pixel(x_start, HEIGHT - 1 - i, color)

def draw_game():
    """Draw all game elements"""
    clear()

    # Center line
    draw_center_line()

    # Paddles
    draw_paddle(game.p1_x, game.p1_y, game.paddle_height, BLUE)
    draw_paddle(game.p2_x, game.p2_y, game.paddle_height, RED)

    # Ball with trail effect
    trail_color = (100, 100, 50)
    if game.ball_vx > 0:
        set_pixel(int(game.ball_x) - 1, int(game.ball_y), trail_color)
    else:
        set_pixel(int(game.ball_x) + 1, int(game.ball_y), trail_color)

    draw_ball(game.ball_x, game.ball_y, WHITE)

    # Scores (small dots at top)
    for i in range(game.p1_score):
        set_pixel(2 + i, 0, BLUE)
    for i in range(game.p2_score):
        set_pixel(WIDTH - 3 - i, 0, RED)

    show()

# ============================================
# GAME LOGIC
# ============================================
def move_paddle(paddle, direction):
    """Move paddle up (-1) or down (1)"""
    if paddle == 1:
        new_y = game.p1_y + direction
        if 0 <= new_y <= HEIGHT - game.paddle_height:
            game.p1_y = new_y
    else:
        new_y = game.p2_y + direction
        if 0 <= new_y <= HEIGHT - game.paddle_height:
            game.p2_y = new_y

def update_ball():
    """Update ball position and handle collisions"""
    # Store old position
    old_x = game.ball_x
    old_y = game.ball_y

    # Update position
    game.ball_x += game.ball_vx
    game.ball_y += game.ball_vy

    # Top/bottom wall collision
    if game.ball_y <= 0:
        game.ball_y = 0
        game.ball_vy = abs(game.ball_vy)
    elif game.ball_y >= HEIGHT - 1:
        game.ball_y = HEIGHT - 1
        game.ball_vy = -abs(game.ball_vy)

    # Paddle 1 collision (left)
    if game.ball_x <= game.p1_x + 1 and game.ball_vx < 0:
        if game.p1_y <= game.ball_y <= game.p1_y + game.paddle_height - 1:
            game.ball_x = game.p1_x + 1
            game.ball_vx = abs(game.ball_vx)

            # Add angle based on where ball hit paddle
            hit_pos = (game.ball_y - game.p1_y) / game.paddle_height
            game.ball_vy = (hit_pos - 0.5) * 1.5

            # Speed up slightly
            game.ball_vx = min(game.ball_vx * 1.05, 2.0)
            game.rally_count += 1

    # Paddle 2 collision (right)
    if game.ball_x >= game.p2_x - 1 and game.ball_vx > 0:
        if game.p2_y <= game.ball_y <= game.p2_y + game.paddle_height - 1:
            game.ball_x = game.p2_x - 1
            game.ball_vx = -abs(game.ball_vx)

            # Add angle based on where ball hit paddle
            hit_pos = (game.ball_y - game.p2_y) / game.paddle_height
            game.ball_vy = (hit_pos - 0.5) * 1.5

            # Speed up slightly
            game.ball_vx = max(game.ball_vx * 1.05, -2.0)
            game.rally_count += 1

    # Scoring
    if game.ball_x <= 0:
        # Player 2 scores
        game.p2_score += 1
        show_score_effect(2)
        if game.p2_score >= game.winning_score:
            game.game_over = True
            game.winner = 2
        else:
            game.reset_ball(direction=1)

    elif game.ball_x >= WIDTH - 1:
        # Player 1 scores
        game.p1_score += 1
        show_score_effect(1)
        if game.p1_score >= game.winning_score:
            game.game_over = True
            game.winner = 1
        else:
            game.reset_ball(direction=-1)

def ai_control():
    """AI controls both paddles for demo mode"""
    # Predict ball position
    predict_y = game.ball_y + game.ball_vy * 3

    # Player 1 AI (left paddle)
    if game.ball_vx < 0:  # Ball coming toward P1
        target_y = predict_y - game.paddle_height // 2
        # Add some randomness/error
        if random.random() < game.ai_error:
            target_y += random.randint(-2, 2)
    else:
        # Return to center when ball going away
        target_y = (HEIGHT - game.paddle_height) // 2

    if game.p1_y < target_y:
        move_paddle(1, 1)
    elif game.p1_y > target_y:
        move_paddle(1, -1)

    # Player 2 AI (right paddle)
    if game.ball_vx > 0:  # Ball coming toward P2
        target_y = predict_y - game.paddle_height // 2
        if random.random() < game.ai_error:
            target_y += random.randint(-2, 2)
    else:
        target_y = (HEIGHT - game.paddle_height) // 2

    if game.p2_y < target_y:
        move_paddle(2, 1)
    elif game.p2_y > target_y:
        move_paddle(2, -1)

def check_buttons():
    """Check button inputs, return True if any pressed"""
    if not BUTTONS_ENABLED:
        return False

    pressed = False

    if btn_p1_up.value() == 0:
        move_paddle(1, -1)
        pressed = True
    if btn_p1_down.value() == 0:
        move_paddle(1, 1)
        pressed = True
    if btn_p2_up.value() == 0:
        move_paddle(2, -1)
        pressed = True
    if btn_p2_down.value() == 0:
        move_paddle(2, 1)
        pressed = True

    return pressed

# ============================================
# EFFECTS
# ============================================
def show_score_effect(player):
    """Flash effect when someone scores"""
    color = BLUE if player == 1 else RED

    for _ in range(2):
        # Flash the scoring side
        for y in range(HEIGHT):
            if player == 1:
                for x in range(WIDTH // 2):
                    set_pixel(x, y, color)
            else:
                for x in range(WIDTH // 2, WIDTH):
                    set_pixel(x, y, color)
        show()
        time.sleep(0.1)
        clear()
        show()
        time.sleep(0.1)

def show_winner(player):
    """Display winner animation"""
    color = BLUE if player == 1 else RED
    other_color = RED if player == 1 else BLUE

    # Fill screen with winner's color
    for i in range(HEIGHT):
        for y in range(i + 1):
            for x in range(WIDTH):
                set_pixel(x, y, color)
        show()
        time.sleep(0.05)

    time.sleep(0.5)

    # Flash
    for _ in range(5):
        for y in range(HEIGHT):
            for x in range(WIDTH):
                set_pixel(x, y, color)
        show()
        time.sleep(0.1)
        clear()
        show()
        time.sleep(0.1)

    time.sleep(1)

def show_title():
    """Show title screen"""
    clear()

    # Draw "PONG" using pixels
    # P
    for y in range(2, 7):
        set_pixel(2, y, WHITE)
    set_pixel(3, 2, WHITE)
    set_pixel(4, 2, WHITE)
    set_pixel(4, 3, WHITE)
    set_pixel(3, 4, WHITE)

    # O
    for y in range(2, 7):
        set_pixel(6, y, WHITE)
        set_pixel(9, y, WHITE)
    set_pixel(7, 2, WHITE)
    set_pixel(8, 2, WHITE)
    set_pixel(7, 6, WHITE)
    set_pixel(8, 6, WHITE)

    # N
    for y in range(2, 7):
        set_pixel(11, y, WHITE)
        set_pixel(14, y, WHITE)
    set_pixel(12, 3, WHITE)
    set_pixel(13, 4, WHITE)

    # Ball animation
    ball_y = 10
    for x in range(16):
        set_pixel(x, ball_y, YELLOW)
        show()
        time.sleep(0.05)
        set_pixel(x, ball_y, BLACK)

    # Draw paddles
    draw_paddle(1, 9, 4, BLUE)
    draw_paddle(14, 9, 4, RED)

    show()
    time.sleep(2)

def show_countdown():
    """3-2-1 countdown"""
    for num in [3, 2, 1]:
        clear()

        # Simple number in center
        cx, cy = 7, 7

        if num == 3:
            points = [(0,-2), (1,-2), (2,-2), (2,-1), (1,0), (2,1), (0,2), (1,2), (2,2), (2,0)]
        elif num == 2:
            points = [(0,-2), (1,-2), (2,-2), (2,-1), (1,0), (0,0), (2,0), (0,1), (0,2), (1,2), (2,2)]
        else:
            points = [(1,-2), (0,-1), (1,-1), (1,0), (1,1), (1,2), (0,2), (2,2)]

        for dx, dy in points:
            set_pixel(cx + dx, cy + dy, GREEN)

        show()
        time.sleep(0.6)

    # GO!
    clear()
    for y in range(HEIGHT):
        for x in range(WIDTH):
            set_pixel(x, y, GREEN)
    show()
    time.sleep(0.2)
    clear()
    show()

# ============================================
# MAIN GAME LOOP
# ============================================
def run_game():
    """Main game loop"""
    print("Pong Demo Starting...")
    print("Auto-play mode (connect buttons to GPIO 2-5 for manual control)")
    print("Press Ctrl+C to stop")

    try:
        while True:
            # Title screen
            show_title()

            # Countdown
            show_countdown()

            # Reset game
            game.reset()

            # Game loop
            frame = 0
            while not game.game_over:
                # Input handling
                buttons_used = check_buttons()

                # AI control if no buttons or demo mode
                if not buttons_used:
                    if frame % 2 == 0:  # Slow down AI slightly
                        ai_control()

                # Update ball
                update_ball()

                # Draw
                draw_game()

                # Frame timing
                time.sleep(0.05)
                frame += 1

            # Show winner
            show_winner(game.winner)

            print(f"Game Over! Player {game.winner} wins!")
            print(f"Score: P1 {game.p1_score} - P2 {game.p2_score}")

    except KeyboardInterrupt:
        print("\nGame stopped!")
        clear()
        show()

if __name__ == "__main__":
    run_game()

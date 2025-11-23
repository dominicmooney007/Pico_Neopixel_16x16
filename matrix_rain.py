"""
Matrix Rain Effect for 16x16 NeoPixel Matrix
Raspberry Pi Pico 2W - MicroPython

The iconic falling green code from The Matrix.
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
BRIGHTNESS = 0.4

# Effect settings
DROP_SPEED = 0.07        # Seconds between updates (lower = faster)
SPAWN_RATE = 0.4         # Chance of new drop per column per frame
TRAIL_LENGTH = 6         # Length of fading trail
HEAD_BRIGHTNESS = 1.0    # Brightness of drop head (white-ish)
VARIATION = True         # Random speed variation per drop

# Initialize NeoPixel
pin = machine.Pin(PIN, machine.Pin.OUT)
np = neopixel.NeoPixel(pin, NUM_LEDS)

# ============================================
# COLORS
# ============================================
# Matrix green shades (head to tail gradient)
def get_trail_color(position, trail_len):
    """Get color for trail position (0 = head, higher = older)"""
    if position == 0:
        # Head is bright white-green
        return (180, 255, 180)
    else:
        # Fade from bright green to dark green
        fade = 1.0 - (position / trail_len)
        intensity = int(255 * fade * fade)  # Quadratic fade
        return (0, intensity, 0)

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
    """Set pixel at x,y"""
    idx = xy_to_index(int(x), int(y))
    if idx >= 0:
        np[idx] = scale_color(color)

def clear():
    """Clear display"""
    np.fill((0, 0, 0))

def show():
    """Update display"""
    np.write()

# ============================================
# DROP CLASS
# ============================================
class Drop:
    def __init__(self, x):
        self.x = x
        self.y = random.randint(-TRAIL_LENGTH, -1)  # Start above screen
        self.speed = 1.0
        if VARIATION:
            self.speed = random.uniform(0.7, 1.3)
        self.trail_length = TRAIL_LENGTH
        self.accumulator = 0.0  # For sub-pixel movement

    def update(self, dt):
        """Update drop position"""
        self.accumulator += self.speed
        if self.accumulator >= 1.0:
            self.y += 1
            self.accumulator = 0.0

    def is_offscreen(self):
        """Check if entire drop (including trail) is off screen"""
        return self.y - self.trail_length > HEIGHT

    def draw(self):
        """Draw the drop and its trail"""
        for i in range(self.trail_length):
            py = int(self.y) - i
            if 0 <= py < HEIGHT:
                color = get_trail_color(i, self.trail_length)
                set_pixel(self.x, py, color)

# ============================================
# RAIN SYSTEM
# ============================================
class MatrixRain:
    def __init__(self):
        self.drops = []
        self.column_cooldown = [0] * WIDTH  # Prevent too many drops per column

    def update(self):
        """Update all drops and spawn new ones"""
        # Update existing drops
        new_drops = []
        for drop in self.drops:
            drop.update(DROP_SPEED)
            if not drop.is_offscreen():
                new_drops.append(drop)
        self.drops = new_drops

        # Decrease cooldowns
        for i in range(WIDTH):
            if self.column_cooldown[i] > 0:
                self.column_cooldown[i] -= 1

        # Spawn new drops
        for x in range(WIDTH):
            if self.column_cooldown[x] == 0:
                if random.random() < SPAWN_RATE * 0.1:  # Adjusted rate
                    self.drops.append(Drop(x))
                    self.column_cooldown[x] = random.randint(3, 8)

    def draw(self):
        """Draw all drops"""
        clear()
        for drop in self.drops:
            drop.draw()
        show()

# ============================================
# GLITCH EFFECT (occasional)
# ============================================
def glitch_effect(rain):
    """Random glitch flash"""
    if random.random() < 0.005:  # Rare occurrence
        # Flash a random row
        row = random.randint(0, HEIGHT - 1)
        for x in range(WIDTH):
            set_pixel(x, row, (0, random.randint(100, 255), 0))
        show()
        time.sleep(0.02)

# ============================================
# CHARACTER OVERLAY (optional)
# ============================================
# Simulated "characters" that briefly appear
def spawn_character(x, y):
    """Draw a brief character glyph"""
    patterns = [
        [(0, 0)],  # Single dot
        [(0, 0), (0, 1)],  # Vertical line
        [(0, 0), (1, 0)],  # Horizontal line
        [(0, 0), (1, 0), (0, 1)],  # L shape
    ]
    pattern = random.choice(patterns)
    for dx, dy in pattern:
        if 0 <= x + dx < WIDTH and 0 <= y + dy < HEIGHT:
            set_pixel(x + dx, y + dy, (200, 255, 200))

# ============================================
# MAIN LOOP
# ============================================
def run_matrix():
    """Main matrix rain loop"""
    print("Matrix Rain Starting...")
    print("Press Ctrl+C to stop")

    rain = MatrixRain()

    # Initial drops to fill screen faster
    for _ in range(WIDTH // 2):
        x = random.randint(0, WIDTH - 1)
        drop = Drop(x)
        drop.y = random.randint(0, HEIGHT)
        rain.drops.append(drop)

    try:
        while True:
            rain.update()
            rain.draw()

            # Occasional glitch
            glitch_effect(rain)

            time.sleep(DROP_SPEED)

    except KeyboardInterrupt:
        print("\nMatrix rain stopped!")
        clear()
        show()

# ============================================
# VARIATIONS
# ============================================
def run_rainbow_matrix():
    """Matrix rain with rainbow colors instead of green"""
    print("Rainbow Matrix Starting...")

    class RainbowDrop(Drop):
        def __init__(self, x):
            super().__init__(x)
            self.hue = random.randint(0, 255)

        def draw(self):
            for i in range(self.trail_length):
                py = int(self.y) - i
                if 0 <= py < HEIGHT:
                    fade = 1.0 - (i / self.trail_length)
                    color = wheel((self.hue + i * 10) % 256)
                    color = tuple(int(c * fade * fade) for c in color)
                    set_pixel(self.x, py, color)

    def wheel(pos):
        pos = pos % 256
        if pos < 85:
            return (255 - pos * 3, pos * 3, 0)
        elif pos < 170:
            pos -= 85
            return (0, 255 - pos * 3, pos * 3)
        else:
            pos -= 170
            return (pos * 3, 0, 255 - pos * 3)

    drops = []
    cooldowns = [0] * WIDTH

    try:
        while True:
            # Update drops
            new_drops = []
            for drop in drops:
                drop.update(DROP_SPEED)
                if not drop.is_offscreen():
                    new_drops.append(drop)
            drops = new_drops

            # Cooldowns and spawning
            for i in range(WIDTH):
                if cooldowns[i] > 0:
                    cooldowns[i] -= 1
                elif random.random() < 0.03:
                    drops.append(RainbowDrop(i))
                    cooldowns[i] = random.randint(3, 8)

            # Draw
            clear()
            for drop in drops:
                drop.draw()
            show()

            time.sleep(DROP_SPEED)

    except KeyboardInterrupt:
        print("\nRainbow matrix stopped!")
        clear()
        show()

def run_blue_matrix():
    """Matrix rain in blue (like system code)"""
    print("Blue Matrix Starting...")

    global get_trail_color

    def blue_trail_color(position, trail_len):
        if position == 0:
            return (200, 220, 255)  # White-blue head
        else:
            fade = 1.0 - (position / trail_len)
            intensity = int(255 * fade * fade)
            return (0, int(intensity * 0.4), intensity)

    # Temporarily override
    original = get_trail_color

    try:
        get_trail_color = blue_trail_color
        run_matrix()
    finally:
        get_trail_color = original

# ============================================
# ENTRY POINT
# ============================================
if __name__ == "__main__":
    # Choose your style:
    run_matrix()          # Classic green
    # run_rainbow_matrix()  # Rainbow variant
    # run_blue_matrix()     # Blue variant

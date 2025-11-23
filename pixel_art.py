"""
Pixel Art Display for 16x16 NeoPixel Matrix
Raspberry Pi Pico 2W - MicroPython

Displays a collection of 16x16 pixel art with transition effects.
Optional button on GPIO 2 to manually cycle sprites.
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

# Display settings
DISPLAY_TIME = 5       # Seconds per sprite
AUTO_CYCLE = True      # Auto-cycle through sprites
RANDOM_ORDER = False   # Random or sequential
TRANSITION = "fade"    # fade, wipe_right, wipe_down, dissolve, none

# Optional button
BTN_NEXT = 2

# Initialize NeoPixel
pin = machine.Pin(PIN, machine.Pin.OUT)
np = neopixel.NeoPixel(pin, NUM_LEDS)

# Button setup
try:
    btn_next = machine.Pin(BTN_NEXT, machine.Pin.IN, machine.Pin.PULL_UP)
    BUTTON_ENABLED = True
except:
    BUTTON_ENABLED = False

# ============================================
# COLOR PALETTE (indexed colors save memory)
# ============================================
PALETTE = {
    '.': (0, 0, 0),        # Black/transparent
    'W': (255, 255, 255),  # White
    'R': (255, 0, 0),      # Red
    'G': (0, 255, 0),      # Green
    'B': (0, 0, 255),      # Blue
    'Y': (255, 255, 0),    # Yellow
    'O': (255, 150, 0),    # Orange
    'P': (255, 100, 200),  # Pink
    'C': (0, 255, 255),    # Cyan
    'M': (255, 0, 255),    # Magenta
    'L': (150, 100, 50),   # Brown/tan
    'D': (100, 100, 100),  # Dark gray
    'S': (200, 150, 100),  # Skin tone
    'N': (50, 50, 80),     # Navy
    'T': (0, 150, 0),      # Dark green
    'K': (30, 30, 30),     # Near black
    'F': (255, 200, 150),  # Flesh/peach
    'A': (150, 200, 255),  # Light blue
}

# ============================================
# SPRITE DATA (16x16 pixel art as strings)
# ============================================
SPRITES = {
    "heart": [
        "................",
        "................",
        "..RRR....RRR....",
        ".RRRRR..RRRRR...",
        "RRRRRRRRRRRRRRR.",
        "RRWRRRRRRRRRRRR.",
        "RRRRRRRRRRRRRRR.",
        "RRRRRRRRRRRRRRR.",
        ".RRRRRRRRRRRRR..",
        "..RRRRRRRRRRR...",
        "...RRRRRRRRR....",
        "....RRRRRRR.....",
        ".....RRRRR......",
        "......RRR.......",
        ".......R........",
        "................",
    ],

    "star": [
        "................",
        ".......YY.......",
        ".......YY.......",
        "......YYYY......",
        "......YYYY......",
        ".YYYYYYYYYYYY...",
        "..YYYYYYYYYY....",
        "...YYYYYYYY.....",
        "....YYYYYY......",
        "...YYWYYYYY.....",
        "...YYY.YYYY.....",
        "..YYY...YYY.....",
        "..YY.....YY.....",
        ".YY.......YY....",
        ".Y.........Y....",
        "................",
    ],

    "pacman": [
        "................",
        "......YYYY......",
        "....YYYYYYYY....",
        "...YYYYYYYYYY...",
        "..YYYYYYYYYYYY..",
        "..YYYYYYYYYYYY..",
        ".YYYYYYYYYY.....",
        ".YYYYYYY........",
        ".YYYYYYYYYY.....",
        "..YYYYYYYYYYYY..",
        "..YYYYYYYYYYYY..",
        "...YYYYYYYYYY...",
        "....YYYYYYYY....",
        "......YYYY......",
        "................",
        "................",
    ],

    "ghost": [
        "................",
        ".....RRRRRR.....",
        "....RRRRRRRR....",
        "...RRRRRRRRRR...",
        "..RRRRRRRRRRRR..",
        "..RRWWRRRRWWRR..",
        "..RWBWRRRRWBWR..",
        "..RWBWRRRRWBWR..",
        "..RRWWRRRRWWRR..",
        "..RRRRRRRRRRRR..",
        "..RRRRRRRRRRRR..",
        "..RRRRRRRRRRRR..",
        "..RRRRRRRRRRRR..",
        "..RR.RRR.RRR.R..",
        "..R..RRR..RR....",
        "................",
    ],

    "mushroom": [
        "................",
        "......RRRR......",
        "....RRRRRRRR....",
        "...RRWWRRWWRR...",
        "..RRRWWRRWWRRR..",
        "..RRRRRRRRRRRR..",
        ".RRRRRRRRRRRRRR.",
        ".RRRRRRRRRRRRRR.",
        "..WWWWWWWWWWWW..",
        "....WWWWWWWW....",
        "....WWWWWWWW....",
        "....WWWWWWWW....",
        "....WWKKKKWW....",
        "....WWKKKKWW....",
        ".....WWWWWW.....",
        "................",
    ],

    "invader": [
        "................",
        "................",
        "....G......G....",
        ".....G....G.....",
        "....GGGGGGGG....",
        "...GG.GGGG.GG...",
        "..GGGGGGGGGGGG..",
        "..G.GGGGGGGG.G..",
        "..G.GG....GG.G..",
        "....GGG..GGG....",
        "................",
        "................",
        "................",
        "................",
        "................",
        "................",
    ],

    "skull": [
        "................",
        ".....WWWWWW.....",
        "....WWWWWWWW....",
        "...WWWWWWWWWW...",
        "..WWWWWWWWWWWW..",
        "..WWWWWWWWWWWW..",
        "..WW.WWWWWW.WW..",
        "..WK.WWWWWW.KW..",
        "..WK.WWWWWW.KW..",
        "..WWWWWKKWWWWW..",
        "..WWWWWWWWWWWW..",
        "...WWWWWWWWWW...",
        "...W.W.WW.W.W...",
        "...W.W.WW.W.W...",
        "....W...W.W.....",
        "................",
    ],

    "smiley": [
        "................",
        ".....YYYYYY.....",
        "...YYYYYYYYYY...",
        "..YYYYYYYYYYYY..",
        ".YYYYYYYYYYYYYV.",
        ".YYYKKYYYYKKYYY.",
        ".YYYKKYYYYKKYYY.",
        ".YYYYYYYYYYYYYV.",
        ".YYYYYYYYYYYYYV.",
        ".YYKYYYYYYYYKYY.",
        ".YYYKYYYYYYKYVY.",
        "..YYYYKKKKYYVY..",
        "..YYYYYYYYYYYY..",
        "...YYYYYYYYYY...",
        ".....YYYYYY.....",
        "................",
    ],

    "mario": [
        "................",
        ".....RRRRRR.....",
        "....RRRRRRRRR...",
        "....LLLSSLS.....",
        "...LSLSSSLSSS...",
        "...LSLLLSSSSS...",
        "....SSSSSSSS....",
        "....RRRBRRRR....",
        "...RRRRBRRRRR...",
        "..RRRRBBBBRRRR..",
        "..SSRBBWBBRSS...",
        "..SSSBBBBBBSSS..",
        "..SSBBBBBBBBSS..",
        "....BBB..BBB....",
        "...LLL....LLL...",
        "..LLLL....LLLL..",
    ],

    "creeper": [
        "................",
        "..GGGGGGGGGGGG..",
        "..GGGGGGGGGGGG..",
        "..GGGGGGGGGGGG..",
        "..GKKGGGGGGKKG..",
        "..GKKGGGGGGKKG..",
        "..GKKGGGGGGKKG..",
        "..GGGGGGGGGGGG..",
        "..GGGGKKKGGGGG..",
        "..GGGKKKKGGGGGG.",
        "..GGGKGGKGGGGG..",
        "..GGGKGGKGGGGG..",
        "..GGGKGGKGGGGG..",
        "..GGGGGGGGGGGG..",
        "..GGGGGGGGGGGG..",
        "................",
    ],

    "sun": [
        ".......YY.......",
        "..Y....YY....Y..",
        "...Y...YY...Y...",
        "....Y.YYYY.Y....",
        ".....YYYYYY.....",
        "...YYYYYYYYYY...",
        "YYYYYYWWYYYYYY..",
        "YYYYYWWWWYYYYY..",
        "YYYYYWWWWYYYYY..",
        "YYYYYYWWYYYYYY..",
        "...YYYYYYYYYY...",
        ".....YYYYYY.....",
        "....Y.YYYY.Y....",
        "...Y...YY...Y...",
        "..Y....YY....Y..",
        ".......YY.......",
    ],

    "moon": [
        "................",
        ".......AAAA.....",
        "......AAAAAA....",
        ".....AAAAAAAA...",
        "....AAAAAAAAAA..",
        "....AAAA.AAAAA..",
        "...AAAA...AAAA..",
        "...AAAA....AAA..",
        "...AAAA....AAA..",
        "...AAAA...AAAA..",
        "....AAAA.AAAAA..",
        "....AAAAAAAAAA..",
        ".....AAAAAAAA...",
        "......AAAAAA....",
        ".......AAAA.....",
        "................",
    ],

    "cherry": [
        "................",
        "...........T....",
        "..........TT....",
        ".........TT.....",
        "........TT.T....",
        ".......TT..TT...",
        ".....TTT....TT..",
        "....TT.......T..",
        "....RRRR...RRR..",
        "...RRRRRR.RRRRR.",
        "..RWRRRRRRRWRRR.",
        "..RRRRRR.RRRRRR.",
        "..RRRRRR.RRRRRR.",
        "...RRRR...RRRR..",
        "....RR.....RR...",
        "................",
    ],

    "diamond": [
        "................",
        "................",
        "......CCCC......",
        ".....CCCCCC.....",
        "....CCWCCCCC....",
        "...CCWWCCCCCC...",
        "..CCCWCCCCCCCCC.",
        ".CCCCCCCCCCCCCC.",
        "..CCCCCCCCCCCCC.",
        "...CCCCCCCCCCC..",
        "....CCCCCCCCC...",
        ".....CCCCCCC....",
        "......CCCCC.....",
        ".......CCC......",
        "........C.......",
        "................",
    ],

    "flower": [
        "................",
        "................",
        ".....RRR........",
        "....RRRRR.......",
        "...RRRWRRRRR....",
        "...RRWWWRRRR....",
        "...RRRWRRRRR....",
        "....RRRRRRR.....",
        ".....RRRTT......",
        "......TTT.......",
        ".....TTTTT......",
        "......TTT.......",
        "......TTT.......",
        ".....TTTTT......",
        ".....TT.TT......",
        "................",
    ],
}

# ============================================
# ANIMATED SPRITES (multiple frames)
# ============================================
ANIMATIONS = {
    "blink_heart": {
        "frames": ["heart", "heart_small"],
        "speed": 500,  # ms per frame
    },
}

# Additional frame for animation
SPRITES["heart_small"] = [
    "................",
    "................",
    "................",
    "...RR....RR.....",
    "..RRRR..RRRR....",
    "..RRRRRRRRRRR...",
    "..RWRRRRRRRRRR..",
    "..RRRRRRRRRRR...",
    "...RRRRRRRRR....",
    "....RRRRRRR.....",
    ".....RRRRR......",
    "......RRR.......",
    ".......R........",
    "................",
    "................",
    "................",
]

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

def scale_color(color, brightness=BRIGHTNESS):
    """Apply brightness scaling"""
    return tuple(int(c * brightness) for c in color)

def set_pixel(x, y, color):
    """Set pixel at x,y"""
    idx = xy_to_index(x, y)
    if idx >= 0:
        np[idx] = scale_color(color)

def clear():
    """Clear display"""
    np.fill((0, 0, 0))

def show():
    """Update display"""
    np.write()

# ============================================
# SPRITE RENDERING
# ============================================
def parse_sprite(sprite_data):
    """Convert sprite string data to pixel array"""
    pixels = []
    for y, row in enumerate(sprite_data):
        for x, char in enumerate(row):
            if char in PALETTE and char != '.':
                color = PALETTE[char]
                pixels.append((x, y, color))
    return pixels

def draw_sprite(sprite_name, offset_x=0, offset_y=0, alpha=1.0):
    """Draw a sprite with optional offset and alpha"""
    if sprite_name not in SPRITES:
        return

    sprite_data = SPRITES[sprite_name]
    for y, row in enumerate(sprite_data):
        for x, char in enumerate(row):
            if char in PALETTE:
                color = PALETTE[char]
                if char != '.':  # Don't draw transparent pixels
                    # Apply alpha
                    color = tuple(int(c * alpha) for c in color)
                    set_pixel(x + offset_x, y + offset_y, color)

def get_sprite_pixels(sprite_name):
    """Get all non-transparent pixels from a sprite"""
    if sprite_name not in SPRITES:
        return []

    pixels = []
    sprite_data = SPRITES[sprite_name]
    for y, row in enumerate(sprite_data):
        for x, char in enumerate(row):
            if char in PALETTE and char != '.':
                pixels.append((x, y, PALETTE[char]))
    return pixels

# ============================================
# TRANSITION EFFECTS
# ============================================
def transition_none(from_sprite, to_sprite):
    """Instant transition"""
    clear()
    draw_sprite(to_sprite)
    show()

def transition_fade(from_sprite, to_sprite, steps=10):
    """Fade out then fade in"""
    # Fade out
    for i in range(steps, -1, -1):
        clear()
        draw_sprite(from_sprite, alpha=i / steps)
        show()
        time.sleep(0.03)

    # Fade in
    for i in range(steps + 1):
        clear()
        draw_sprite(to_sprite, alpha=i / steps)
        show()
        time.sleep(0.03)

def transition_wipe_right(from_sprite, to_sprite):
    """Wipe from left to right"""
    for x in range(WIDTH + 1):
        clear()
        # Draw old sprite (clipped)
        for py in range(HEIGHT):
            for px in range(x, WIDTH):
                char = SPRITES[from_sprite][py][px] if from_sprite in SPRITES else '.'
                if char in PALETTE and char != '.':
                    set_pixel(px, py, PALETTE[char])
        # Draw new sprite (clipped)
        for py in range(HEIGHT):
            for px in range(x):
                char = SPRITES[to_sprite][py][px] if to_sprite in SPRITES else '.'
                if char in PALETTE and char != '.':
                    set_pixel(px, py, PALETTE[char])
        show()
        time.sleep(0.03)

def transition_wipe_down(from_sprite, to_sprite):
    """Wipe from top to bottom"""
    for y in range(HEIGHT + 1):
        clear()
        # Draw old sprite (bottom part)
        for py in range(y, HEIGHT):
            for px in range(WIDTH):
                char = SPRITES[from_sprite][py][px] if from_sprite in SPRITES else '.'
                if char in PALETTE and char != '.':
                    set_pixel(px, py, PALETTE[char])
        # Draw new sprite (top part)
        for py in range(y):
            for px in range(WIDTH):
                char = SPRITES[to_sprite][py][px] if to_sprite in SPRITES else '.'
                if char in PALETTE and char != '.':
                    set_pixel(px, py, PALETTE[char])
        show()
        time.sleep(0.03)

def transition_dissolve(from_sprite, to_sprite, steps=20):
    """Random pixel dissolve"""
    # Get all pixel positions
    positions = [(x, y) for y in range(HEIGHT) for x in range(WIDTH)]
    random.shuffle(positions)

    pixels_per_step = len(positions) // steps

    # Start with from_sprite
    clear()
    draw_sprite(from_sprite)
    show()

    # Gradually replace with to_sprite
    for step in range(steps):
        start_idx = step * pixels_per_step
        end_idx = start_idx + pixels_per_step

        for x, y in positions[start_idx:end_idx]:
            char = SPRITES[to_sprite][y][x] if to_sprite in SPRITES else '.'
            if char in PALETTE:
                color = PALETTE[char]
                set_pixel(x, y, color)
        show()
        time.sleep(0.05)

def do_transition(from_sprite, to_sprite, effect=TRANSITION):
    """Perform transition between sprites"""
    if effect == "fade":
        transition_fade(from_sprite, to_sprite)
    elif effect == "wipe_right":
        transition_wipe_right(from_sprite, to_sprite)
    elif effect == "wipe_down":
        transition_wipe_down(from_sprite, to_sprite)
    elif effect == "dissolve":
        transition_dissolve(from_sprite, to_sprite)
    else:
        transition_none(from_sprite, to_sprite)

# ============================================
# MAIN DISPLAY LOOP
# ============================================
def run_display():
    """Main display loop"""
    print("Pixel Art Display Starting...")
    print(f"Mode: {'Auto-cycle' if AUTO_CYCLE else 'Manual'}")
    print(f"Transition: {TRANSITION}")
    print("Press Ctrl+C to stop")

    sprite_names = list(SPRITES.keys())
    # Remove animation frames from main rotation
    sprite_names = [s for s in sprite_names if not s.endswith("_small")]

    current_idx = 0
    current_sprite = sprite_names[current_idx]

    # Initial display
    clear()
    draw_sprite(current_sprite)
    show()

    last_change = time.time()
    last_button = time.ticks_ms()

    try:
        while True:
            current_time = time.time()

            # Check for button press
            next_pressed = False
            if BUTTON_ENABLED:
                if btn_next.value() == 0:
                    if time.ticks_diff(time.ticks_ms(), last_button) > 300:
                        next_pressed = True
                        last_button = time.ticks_ms()

            # Check if time to change sprite
            should_change = False
            if AUTO_CYCLE and (current_time - last_change) >= DISPLAY_TIME:
                should_change = True
            if next_pressed:
                should_change = True

            if should_change:
                # Select next sprite
                if RANDOM_ORDER:
                    new_idx = random.randint(0, len(sprite_names) - 1)
                    while new_idx == current_idx and len(sprite_names) > 1:
                        new_idx = random.randint(0, len(sprite_names) - 1)
                    current_idx = new_idx
                else:
                    current_idx = (current_idx + 1) % len(sprite_names)

                next_sprite = sprite_names[current_idx]

                print(f"Showing: {next_sprite}")

                # Transition
                do_transition(current_sprite, next_sprite)

                current_sprite = next_sprite
                last_change = time.time()

            time.sleep(0.05)

    except KeyboardInterrupt:
        print("\nDisplay stopped!")
        clear()
        show()

# ============================================
# DEMO MODE - cycle through all effects
# ============================================
def run_demo():
    """Demo mode showing all sprites with different transitions"""
    print("Pixel Art Demo Mode")
    print("Showing all sprites with various transitions...")

    sprite_names = [s for s in SPRITES.keys() if not s.endswith("_small")]
    transitions = ["fade", "wipe_right", "wipe_down", "dissolve"]

    current_sprite = sprite_names[0]
    clear()
    draw_sprite(current_sprite)
    show()
    time.sleep(2)

    try:
        idx = 1
        while True:
            next_sprite = sprite_names[idx % len(sprite_names)]
            transition = transitions[idx % len(transitions)]

            print(f"{current_sprite} -> {next_sprite} ({transition})")

            do_transition(current_sprite, next_sprite, transition)

            current_sprite = next_sprite
            idx += 1

            time.sleep(3)

    except KeyboardInterrupt:
        print("\nDemo stopped!")
        clear()
        show()

if __name__ == "__main__":
    # Run demo mode or display mode
    run_demo()
    # run_display()  # Uncomment for normal display mode

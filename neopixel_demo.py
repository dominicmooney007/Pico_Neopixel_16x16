"""
NeoPixel 16x16 Matrix Demo for Raspberry Pi Pico 2W
Demonstrates various effects and drawing capabilities
"""

import machine
import neopixel
import time
import math

# ============================================
# CONFIGURATION
# ============================================
WIDTH = 16
HEIGHT = 16
NUM_LEDS = WIDTH * HEIGHT
PIN = 0  # GPIO pin connected to DIN
BRIGHTNESS = 0.3  # 0.0 to 1.0 (keep low to reduce power draw)

# Initialize NeoPixel
pin = machine.Pin(PIN, machine.Pin.OUT)
np = neopixel.NeoPixel(pin, NUM_LEDS)

# ============================================
# COORDINATE MAPPING (Serpentine Layout)
# ============================================
def xy_to_index(x, y):
    """Convert x,y coordinates to LED index for serpentine/zigzag layout"""
    if x < 0 or x >= WIDTH or y < 0 or y >= HEIGHT:
        return -1
    if y % 2 == 0:
        # Even rows: left to right
        return y * WIDTH + x
    else:
        # Odd rows: right to left
        return y * WIDTH + (WIDTH - 1 - x)

# ============================================
# COLOR UTILITIES
# ============================================
def scale_color(color, brightness=BRIGHTNESS):
    """Scale color by brightness factor"""
    return tuple(int(c * brightness) for c in color)

def hsv_to_rgb(h, s, v):
    """Convert HSV (0-1 range) to RGB (0-255 range)"""
    if s == 0.0:
        return (int(v * 255), int(v * 255), int(v * 255))

    i = int(h * 6.0)
    f = (h * 6.0) - i
    p = v * (1.0 - s)
    q = v * (1.0 - s * f)
    t = v * (1.0 - s * (1.0 - f))
    i = i % 6

    if i == 0: r, g, b = v, t, p
    elif i == 1: r, g, b = q, v, p
    elif i == 2: r, g, b = p, v, t
    elif i == 3: r, g, b = p, q, v
    elif i == 4: r, g, b = t, p, v
    else: r, g, b = v, p, q

    return (int(r * 255), int(g * 255), int(b * 255))

def wheel(pos):
    """Generate rainbow colors (0-255 input)"""
    pos = pos % 256
    if pos < 85:
        return (255 - pos * 3, pos * 3, 0)
    elif pos < 170:
        pos -= 85
        return (0, 255 - pos * 3, pos * 3)
    else:
        pos -= 170
        return (pos * 3, 0, 255 - pos * 3)

# ============================================
# BASIC DRAWING FUNCTIONS
# ============================================
def clear():
    """Turn off all LEDs"""
    np.fill((0, 0, 0))
    np.write()

def fill(color):
    """Fill entire matrix with a color"""
    np.fill(scale_color(color))
    np.write()

def set_pixel(x, y, color):
    """Set a single pixel at x,y coordinates"""
    idx = xy_to_index(x, y)
    if idx >= 0:
        np[idx] = scale_color(color)

def draw_line(x0, y0, x1, y1, color):
    """Draw a line using Bresenham's algorithm"""
    dx = abs(x1 - x0)
    dy = -abs(y1 - y0)
    sx = 1 if x0 < x1 else -1
    sy = 1 if y0 < y1 else -1
    err = dx + dy

    while True:
        set_pixel(x0, y0, color)
        if x0 == x1 and y0 == y1:
            break
        e2 = 2 * err
        if e2 >= dy:
            err += dy
            x0 += sx
        if e2 <= dx:
            err += dx
            y0 += sy

def draw_rect(x, y, w, h, color):
    """Draw rectangle outline"""
    draw_line(x, y, x + w - 1, y, color)
    draw_line(x + w - 1, y, x + w - 1, y + h - 1, color)
    draw_line(x + w - 1, y + h - 1, x, y + h - 1, color)
    draw_line(x, y + h - 1, x, y, color)

def fill_rect(x, y, w, h, color):
    """Draw filled rectangle"""
    for py in range(y, y + h):
        for px in range(x, x + w):
            set_pixel(px, py, color)

def draw_circle(cx, cy, r, color):
    """Draw circle outline using midpoint algorithm"""
    x = r
    y = 0
    err = 0

    while x >= y:
        set_pixel(cx + x, cy + y, color)
        set_pixel(cx + y, cy + x, color)
        set_pixel(cx - y, cy + x, color)
        set_pixel(cx - x, cy + y, color)
        set_pixel(cx - x, cy - y, color)
        set_pixel(cx - y, cy - x, color)
        set_pixel(cx + y, cy - x, color)
        set_pixel(cx + x, cy - y, color)

        y += 1
        err += 1 + 2 * y
        if 2 * (err - x) + 1 > 0:
            x -= 1
            err += 1 - 2 * x

def fill_circle(cx, cy, r, color):
    """Draw filled circle"""
    for y in range(-r, r + 1):
        for x in range(-r, r + 1):
            if x * x + y * y <= r * r:
                set_pixel(cx + x, cy + y, color)

# ============================================
# ANIMATION EFFECTS
# ============================================
def effect_color_wipe(color, delay=0.02):
    """Fill matrix one pixel at a time"""
    for y in range(HEIGHT):
        for x in range(WIDTH):
            set_pixel(x, y, color)
            np.write()
            time.sleep(delay)

def effect_rainbow_wave(duration=5, speed=0.05):
    """Diagonal rainbow wave across the matrix"""
    start = time.time()
    offset = 0
    while time.time() - start < duration:
        for y in range(HEIGHT):
            for x in range(WIDTH):
                color = wheel((x + y + offset) * 8)
                set_pixel(x, y, color)
        np.write()
        offset += 1
        time.sleep(speed)

def effect_plasma(duration=5, speed=0.05):
    """Plasma-like color effect"""
    start = time.time()
    t = 0
    while time.time() - start < duration:
        for y in range(HEIGHT):
            for x in range(WIDTH):
                # Create plasma pattern using sine waves
                v1 = math.sin(x / 4.0 + t)
                v2 = math.sin((y / 4.0 + t) / 2.0)
                v3 = math.sin((x + y) / 8.0 + t)
                v = (v1 + v2 + v3 + 3) / 6.0  # Normalize to 0-1
                color = hsv_to_rgb(v, 1.0, 1.0)
                set_pixel(x, y, color)
        np.write()
        t += 0.3
        time.sleep(speed)

def effect_bouncing_ball(duration=5):
    """Bouncing ball animation"""
    x, y = 7.0, 7.0
    vx, vy = 0.5, 0.3
    start = time.time()

    while time.time() - start < duration:
        clear()

        # Draw ball
        fill_circle(int(x), int(y), 2, (255, 100, 0))
        np.write()

        # Update position
        x += vx
        y += vy

        # Bounce off walls
        if x <= 2 or x >= WIDTH - 3:
            vx = -vx
        if y <= 2 or y >= HEIGHT - 3:
            vy = -vy

        time.sleep(0.05)

def effect_expanding_rings(duration=5, delay=0.1):
    """Expanding rings from center"""
    start = time.time()
    while time.time() - start < duration:
        for r in range(12):
            clear()
            color = wheel(r * 20)
            draw_circle(7, 7, r, color)
            if r > 0:
                draw_circle(7, 7, r - 1, (color[0]//2, color[1]//2, color[2]//2))
            np.write()
            time.sleep(delay)

def effect_sparkle(duration=3, density=10):
    """Random sparkle effect"""
    import random
    start = time.time()
    while time.time() - start < duration:
        clear()
        for _ in range(density):
            x = random.randint(0, WIDTH - 1)
            y = random.randint(0, HEIGHT - 1)
            color = (random.randint(100, 255), random.randint(100, 255), random.randint(100, 255))
            set_pixel(x, y, color)
        np.write()
        time.sleep(0.05)

def effect_matrix_rain(duration=5):
    """Matrix-style falling rain effect"""
    import random
    drops = []
    start = time.time()

    while time.time() - start < duration:
        clear()

        # Spawn new drops
        if random.random() < 0.3:
            drops.append([random.randint(0, WIDTH - 1), 0, random.randint(3, 8)])

        # Update and draw drops
        new_drops = []
        for drop in drops:
            x, y, length = drop
            # Draw trail
            for i in range(length):
                if y - i >= 0 and y - i < HEIGHT:
                    intensity = int(255 * (1 - i / length))
                    set_pixel(x, y - i, (0, intensity, 0))

            drop[1] += 1
            if drop[1] - length < HEIGHT:
                new_drops.append(drop)

        drops = new_drops
        np.write()
        time.sleep(0.07)

def effect_checkerboard(duration=3):
    """Animated checkerboard pattern"""
    start = time.time()
    offset = 0
    while time.time() - start < duration:
        for y in range(HEIGHT):
            for x in range(WIDTH):
                if (x + y + offset) % 2 == 0:
                    set_pixel(x, y, (255, 0, 100))
                else:
                    set_pixel(x, y, (0, 100, 255))
        np.write()
        offset += 1
        time.sleep(0.3)

def effect_spiral(color=(0, 255, 100), delay=0.03):
    """Spiral fill from center"""
    cx, cy = WIDTH // 2, HEIGHT // 2
    visited = [[False] * HEIGHT for _ in range(WIDTH)]
    directions = [(1, 0), (0, 1), (-1, 0), (0, -1)]

    x, y = cx, cy
    dir_idx = 0

    clear()
    for _ in range(NUM_LEDS):
        if 0 <= x < WIDTH and 0 <= y < HEIGHT and not visited[x][y]:
            set_pixel(x, y, color)
            visited[x][y] = True
            np.write()
            time.sleep(delay)

        # Try to turn right
        next_dir = (dir_idx + 1) % 4
        nx = x + directions[next_dir][0]
        ny = y + directions[next_dir][1]

        if 0 <= nx < WIDTH and 0 <= ny < HEIGHT and not visited[nx][ny]:
            dir_idx = next_dir
            x, y = nx, ny
        else:
            # Continue straight
            x += directions[dir_idx][0]
            y += directions[dir_idx][1]

def demo_shapes():
    """Demonstrate drawing shapes"""
    clear()

    # Draw various shapes
    draw_rect(1, 1, 6, 6, (255, 0, 0))       # Red rectangle
    fill_rect(9, 1, 5, 5, (0, 255, 0))       # Green filled rect
    draw_circle(4, 11, 3, (0, 0, 255))       # Blue circle
    fill_circle(12, 11, 3, (255, 255, 0))    # Yellow filled circle
    draw_line(0, 0, 15, 15, (255, 0, 255))   # Magenta diagonal

    np.write()
    time.sleep(3)

# ============================================
# MAIN DEMO LOOP
# ============================================
def run_demo():
    """Run all demo effects in a loop"""
    print("NeoPixel 16x16 Demo Starting...")
    print("Press Ctrl+C to stop")

    try:
        while True:
            print("-> Shapes demo")
            demo_shapes()

            print("-> Color wipe (red)")
            effect_color_wipe((255, 0, 0), delay=0.01)
            time.sleep(0.5)

            print("-> Rainbow wave")
            effect_rainbow_wave(duration=5)

            print("-> Plasma effect")
            effect_plasma(duration=5)

            print("-> Bouncing ball")
            effect_bouncing_ball(duration=5)

            print("-> Expanding rings")
            effect_expanding_rings(duration=4)

            print("-> Sparkle")
            effect_sparkle(duration=3)

            print("-> Matrix rain")
            effect_matrix_rain(duration=5)

            print("-> Checkerboard")
            effect_checkerboard(duration=3)

            print("-> Spiral")
            effect_spiral()
            time.sleep(1)

            print("-> Cycle complete, restarting...")

    except KeyboardInterrupt:
        print("\nStopping demo...")
        clear()
        print("Done!")

# Run the demo when executed
if __name__ == "__main__":
    run_demo()

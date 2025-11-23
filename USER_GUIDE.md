# Pico 2W NeoPixel 16x16 Matrix - User Guide

A complete guide to setting up your Raspberry Pi Pico 2W with MicroPython and controlling a 16x16 WS2812B NeoPixel matrix.

---

## Table of Contents

1. [Hardware Requirements](#hardware-requirements)
2. [Pico 2W Setup](#pico-2w-setup)
3. [Wiring the NeoPixel Matrix](#wiring-the-neopixel-matrix)
4. [Development Environment](#development-environment)
5. [Understanding the NeoPixel Library](#understanding-the-neopixel-library)
6. [Code Architecture](#code-architecture)
7. [Running the Examples](#running-the-examples)
8. [Troubleshooting](#troubleshooting)

---

## Hardware Requirements

| Component | Description | Notes |
|-----------|-------------|-------|
| Raspberry Pi Pico 2W | RP2350 microcontroller with WiFi | Also works with Pico/Pico W |
| 16x16 NeoPixel Matrix | WS2812B LED panel (256 LEDs) | Typically comes as flexible or rigid PCB |
| 5V Power Supply | 4A-10A recommended | **DO NOT power from Pico!** |
| Jumper Wires | 3 wires minimum | Data, Ground, (optional 5V for level shifting) |
| 1000µF Capacitor | Across power supply | Protects LEDs from voltage spikes |
| 300-500Ω Resistor | On data line (optional) | Protects first LED |

### Power Calculation

Each WS2812B LED can draw up to 60mA at full white brightness:
- 256 LEDs × 60mA = **15.36A maximum**
- At 30% brightness: ~4.6A
- Realistic usage: 2-5A

**Always use an external 5V power supply!**

---

## Pico 2W Setup

### Step 1: Download MicroPython UF2

1. Go to the official MicroPython download page:
   **https://micropython.org/download/RPI_PICO2_W/**

2. Download the latest `.uf2` file for **Pico 2W** (RP2350)
   - Look for: `RPI_PICO2_W-xxxxxxxx-vX.X.X.uf2`

   > **Note:** For original Pico W, use: https://micropython.org/download/RPI_PICO_W/

### Step 2: Flash MicroPython to Pico

1. **Enter BOOTSEL mode:**
   - Hold down the **BOOTSEL** button on the Pico
   - While holding, connect USB cable to your computer
   - Release the button after connecting

2. **Pico appears as a USB drive:**
   - Windows: Shows as `RPI-RP2` drive
   - The drive contains `INDEX.HTM` and `INFO_UF2.TXT`

3. **Copy the UF2 file:**
   - Drag and drop the `.uf2` file onto the `RPI-RP2` drive
   - Pico will automatically reboot
   - The drive will disappear (this is normal!)

4. **Verify installation:**
   - Pico is now running MicroPython
   - Ready for code upload

### Step 3: Verify MicroPython (Optional)

Connect via serial terminal (PuTTY, screen, or Thonny):
- Baud rate: 115200
- You should see the MicroPython REPL prompt: `>>>`

```python
>>> import sys
>>> sys.implementation
(name='micropython', version=(1, 23, 0), ...)
```

---

## Wiring the NeoPixel Matrix

### Basic Wiring Diagram

```
┌─────────────────┐          ┌─────────────────┐
│   Pico 2W       │          │  NeoPixel 16x16 │
│                 │          │                 │
│  GPIO 0 ────────┼──────────┼─► DIN           │
│                 │          │                 │
│  GND ───────────┼────┬─────┼─► GND           │
│                 │    │     │                 │
└─────────────────┘    │     │   5V ◄──────────┼──── 5V Power Supply (+)
                       │     │                 │
                       └─────┼─────────────────┼──── 5V Power Supply (-)
                             └─────────────────┘
```

### Connections Summary

| Pico 2W Pin | NeoPixel Pin | Power Supply |
|-------------|--------------|--------------|
| GPIO 0      | DIN (Data In)| - |
| GND         | GND          | GND (common ground!) |
| -           | 5V           | 5V+ |

### Important Wiring Notes

1. **Common Ground:** All grounds (Pico, NeoPixel, Power Supply) must be connected together

2. **Data Pin:** GPIO 0 is used in our examples, but any GPIO works. The Pico outputs 3.3V logic which usually works with 5V WS2812B LEDs

3. **Optional Level Shifter:** For reliable operation, use a level shifter (3.3V → 5V) on the data line

4. **Power Injection:** For large matrices, inject 5V power at multiple points to prevent voltage drop

---

## Development Environment

### Option 1: VSCode + MicroPico (Recommended)

1. **Install VSCode:**
   - Download from: https://code.visualstudio.com/

2. **Install Extensions:**
   - Open Extensions panel (Ctrl+Shift+X)
   - Search and install: `MicroPico` (by paulober)
   - Also recommended: `Python`, `Pylance`

3. **Configure Project:**
   - Open your project folder
   - Run command: `MicroPico: Configure Project`
   - This creates `.micropico` marker file

4. **Connect to Pico:**
   - Command Palette (Ctrl+Shift+P)
   - `MicroPico: Connect`

5. **Useful Commands:**
   | Command | Description |
   |---------|-------------|
   | `MicroPico: Upload current file to Pico` | Deploy single file |
   | `MicroPico: Upload project to Pico` | Deploy all files |
   | `MicroPico: Run current file on Pico` | Run without saving |
   | `MicroPico: Delete all files from Pico` | Clean device |

### Option 2: Thonny IDE

1. Download Thonny: https://thonny.org/
2. Select interpreter: `MicroPython (Raspberry Pi Pico)`
3. Use "Save as" to save files directly to Pico

---

## Understanding the NeoPixel Library

### The Built-in `neopixel` Module

MicroPython includes a `neopixel` module for WS2812B control. No external libraries needed!

### Basic Usage

```python
import machine
import neopixel

# Initialize
pin = machine.Pin(0, machine.Pin.OUT)  # GPIO 0
np = neopixel.NeoPixel(pin, 256)       # 256 LEDs (16x16)

# Set a pixel (index, RGB tuple)
np[0] = (255, 0, 0)    # First LED = Red
np[1] = (0, 255, 0)    # Second LED = Green
np[255] = (0, 0, 255)  # Last LED = Blue

# IMPORTANT: Changes aren't visible until you call write()!
np.write()

# Fill all LEDs with one color
np.fill((255, 255, 255))  # All white
np.write()

# Turn off all LEDs
np.fill((0, 0, 0))
np.write()
```

### NeoPixel Class Reference

```python
# Constructor
neopixel.NeoPixel(pin, n, bpp=3, timing=1)
```

| Parameter | Description |
|-----------|-------------|
| `pin` | `machine.Pin` object for data line |
| `n` | Number of LEDs |
| `bpp` | Bytes per pixel: 3 for RGB, 4 for RGBW |
| `timing` | 0 for 400KHz, 1 for 800KHz (most LEDs use 800KHz) |

### Methods

| Method | Description |
|--------|-------------|
| `np[i] = (r, g, b)` | Set pixel `i` to RGB color (0-255 each) |
| `np[i]` | Get current color of pixel `i` |
| `np.fill((r, g, b))` | Set all pixels to same color |
| `np.write()` | Send data to LEDs (makes changes visible) |
| `len(np)` | Returns number of LEDs |

### Color Format

Colors are tuples of 3 integers (0-255):
```python
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)       # Off
YELLOW = (255, 255, 0)
CYAN = (0, 255, 255)
MAGENTA = (255, 0, 255)
ORANGE = (255, 165, 0)
```

---

## Code Architecture

### The Serpentine/Zigzag Layout Problem

Most 16x16 NeoPixel matrices are wired in a **serpentine pattern**, not a simple grid:

```
LED Index Layout (Serpentine):

Row 0:  →  0   1   2   3   4   5  ... 15
Row 1:  ← 31  30  29  28  27  26  ... 16
Row 2:  → 32  33  34  35  36  37  ... 47
Row 3:  ← 63  62  61  60  59  58  ... 48
...
```

This means pixel index 16 is NOT at position (0, 1) - it's at (15, 1)!

### The Coordinate Mapping Function

Every file in this project uses this critical function:

```python
def xy_to_index(x, y):
    """Convert (x, y) coordinates to LED index"""
    # Bounds checking
    if x < 0 or x >= WIDTH or y < 0 or y >= HEIGHT:
        return -1

    if y % 2 == 0:
        # Even rows (0, 2, 4...): left to right
        return y * WIDTH + x
    else:
        # Odd rows (1, 3, 5...): right to left (reversed!)
        return y * WIDTH + (WIDTH - 1 - x)
```

### Using the Mapping

```python
# Set pixel at column 5, row 3 to red
index = xy_to_index(5, 3)
if index >= 0:  # Valid coordinate
    np[index] = (255, 0, 0)
np.write()
```

### Wrapper Function Pattern

Most examples use a wrapper for convenience:

```python
def set_pixel(x, y, color):
    """Set pixel at x,y with bounds checking"""
    idx = xy_to_index(x, y)
    if idx >= 0:
        np[idx] = scale_color(color)

def scale_color(color, brightness=0.3):
    """Reduce brightness to save power"""
    return tuple(int(c * brightness) for c in color)
```

### Common Code Structure

All example files follow this pattern:

```python
import machine
import neopixel
import time

# 1. Configuration
WIDTH = 16
HEIGHT = 16
NUM_LEDS = 256
PIN = 0
BRIGHTNESS = 0.3

# 2. Initialize hardware
pin = machine.Pin(PIN, machine.Pin.OUT)
np = neopixel.NeoPixel(pin, NUM_LEDS)

# 3. Utility functions
def xy_to_index(x, y): ...
def set_pixel(x, y, color): ...
def clear(): ...
def show(): ...

# 4. Effect/game logic
def my_effect(): ...

# 5. Main loop
def run():
    try:
        while True:
            # Update logic
            # Draw to buffer
            # np.write() to display
            time.sleep(0.05)
    except KeyboardInterrupt:
        clear()
        show()

if __name__ == "__main__":
    run()
```

---

## Running the Examples

### Available Example Files

| File | Description |
|------|-------------|
| `blink.py` | Simple LED blink test |
| `neopixel_demo.py` | Multiple effects showcase |
| `space_invaders.py` | Space Invaders game |
| `pong.py` | Pong game |
| `pixel_art.py` | Pixel art slideshow |
| `matrix_rain.py` | Matrix digital rain |

### How to Run

**Method 1: Run directly (testing)**
1. Open file in VSCode
2. `MicroPico: Run current file on Pico`
3. Code runs but isn't saved to device

**Method 2: Upload and run**
1. `MicroPico: Upload current file to Pico`
2. File is saved to Pico's filesystem
3. Run via REPL: `import filename`

**Method 3: Auto-run on boot**
1. Rename your main file to `main.py`
2. Upload to Pico
3. Pico will run `main.py` automatically on power-up

### Stopping a Running Program

- Press **Ctrl+C** in the terminal/REPL
- Or disconnect/reconnect USB

---

## Troubleshooting

### LEDs Don't Light Up

| Issue | Solution |
|-------|----------|
| No power | Check 5V power supply connections |
| Wrong pin | Verify GPIO number matches code |
| No `np.write()` | Must call write() to update LEDs |
| Loose connection | Check all wiring connections |

### Wrong Colors

| Issue | Solution |
|-------|----------|
| Colors swapped (e.g., red shows as green) | Your LEDs use GRB order, not RGB. Some matrices are wired differently. |
| Dim colors | Check brightness setting, ensure adequate power |

**To fix color order:**
```python
# If your matrix uses GRB instead of RGB:
def set_pixel_grb(x, y, rgb_color):
    r, g, b = rgb_color
    grb_color = (g, r, b)  # Swap red and green
    idx = xy_to_index(x, y)
    if idx >= 0:
        np[idx] = grb_color
```

### Pixels in Wrong Position

| Issue | Solution |
|-------|----------|
| Pattern looks mirrored | Your matrix might start from a different corner |
| Pattern looks scrambled | Check if your matrix uses serpentine wiring |

**To adjust orientation:**
```python
# If your matrix starts from bottom-right instead of top-left:
def xy_to_index_adjusted(x, y):
    x = WIDTH - 1 - x   # Mirror horizontally
    y = HEIGHT - 1 - y  # Mirror vertically
    return xy_to_index(x, y)
```

### Flickering or Glitching

| Issue | Solution |
|-------|----------|
| Random flickering | Add capacitor across power supply |
| First LED glitching | Add 300-500Ω resistor on data line |
| Corruption at end | Power supply can't deliver enough current |

### Memory Errors

MicroPython has limited RAM (~264KB). If you get `MemoryError`:

1. Use `const()` for constants:
   ```python
   WIDTH = const(16)  # Saves memory
   ```

2. Avoid large lists, use generators
3. Delete unused variables: `del large_list`
4. Run garbage collection: `import gc; gc.collect()`

---

## Quick Reference

### Coordinate System

```
        x →
      0 1 2 3 4 5 6 7 8 9 ...15
    ┌─────────────────────────
  0 │ ■ □ □ □ □ □ □ □ □ □    (0,0) = top-left
y 1 │ □ □ □ □ □ □ □ □ □ □
↓ 2 │ □ □ □ □ □ □ □ □ □ □
  3 │ □ □ □ □ □ □ □ □ □ □
  . │
 15 │ □ □ □ □ □ □ □ □ □ ■    (15,15) = bottom-right
```

### Essential Code Snippet

```python
import machine, neopixel, time

np = neopixel.NeoPixel(machine.Pin(0, machine.Pin.OUT), 256)

def xy(x, y):
    if y % 2 == 0: return y * 16 + x
    return y * 16 + (15 - x)

# Draw red pixel at (5, 3)
np[xy(5, 3)] = (255, 0, 0)
np.write()
```

---

## Resources

- [MicroPython NeoPixel Docs](https://docs.micropython.org/en/latest/library/neopixel.html)
- [Raspberry Pi Pico Documentation](https://www.raspberrypi.com/documentation/microcontrollers/)
- [MicroPython Downloads](https://micropython.org/download/)
- [WS2812B Datasheet](https://cdn-shop.adafruit.com/datasheets/WS2812B.pdf)

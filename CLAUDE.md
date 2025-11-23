# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

MicroPython project for Raspberry Pi Pico 2W controlling a 16x16 WS2812B NeoPixel LED matrix (256 LEDs total).

## Development Environment

- **IDE**: VSCode with MicroPico extension (`paulober.pico-w-go`)
- **Language**: MicroPython (not standard Python)
- **Target Hardware**: Raspberry Pi Pico 2W (RP2350)

### MicroPico Commands (VSCode Command Palette)

- `MicroPico: Upload current file to Pico` - Deploy single file
- `MicroPico: Upload project to Pico` - Deploy all project files
- `MicroPico: Run current file on Pico` - Execute without saving to device
- `MicroPico: Connect` / `Disconnect` - Serial connection management

## Hardware Configuration

- **GPIO 0**: NeoPixel data line (DIN)
- **Matrix Layout**: 16x16 serpentine/zigzag pattern
- **LED Count**: 256 (WIDTH * HEIGHT)
- **Power**: External 5V supply required (not Pico VBUS)

## Code Architecture

### Coordinate System

The NeoPixel matrix uses serpentine wiring. Use `xy_to_index(x, y)` to convert 2D coordinates to linear LED index:
- Even rows (0, 2, 4...): left-to-right
- Odd rows (1, 3, 5...): right-to-left

### Key Modules

- `neopixel` - Built-in MicroPython module for WS2812B control
- `machine` - Hardware access (Pin, PWM, etc.)

## MicroPython Constraints

- No threading (use `time.sleep()` for timing)
- Limited memory (~264KB RAM)
- Use `const()` for constants to save memory
- Avoid large lists/dicts; prefer generators where possible

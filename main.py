
# -*- coding: utf-8 -*-
"""
Alarm_Project1_v6_3_1_web.py  (rename to: main.py for pygbag)
- PyGBag-ready: async main loop + await asyncio.sleep(0) each frame.
- No sys.exit()/pygame.quit() after asyncio.run(main()).
- Snapshot saving disabled on web (emscripten) to avoid blocking I/O.
- Fonts: single-sentinel ensure_fonts() (no chained 'and' warnings).
- Machine defaults RUNNING; realistic visuals; timed cleaning, etc.

Author: M365 Copilot for Cameron Paton
"""
pip install pygbag pygame
import sys
import asyncio
import pygame
import random
import math
import time
import csv
import json
from datetime import datetime
from typing import Tuple

# ==============================
# Canvas & timing
# ==============================
SCALE = 4
BASE_W, BASE_H = 288, 192
WIDTH, HEIGHT = BASE_W * SCALE, BASE_H * SCALE
FPS = 60
random.seed(7)

# ==============================
# Scenes
# ==============================
SCENE_YARD = 0
SCENE_ELECTRICAL = 1
SCENE_VEHICLE = 2
SCENE_MACHINE = 3

# ==============================
# Behavior tuning
# ==============================
VEH_RADIUS_DEFAULT = 5.0
OP_RADIUS = 6.0
AVOID_DIST_VEH = 26.0
AVOID_DIST_OP  = 28.0
AVOID_TURN_GAIN_VEH = 0.7
AVOID_TURN_GAIN_OP  = 0.9
CORNER_SLOW_RADIUS = 42.0
LOOKAHEAD_GAIN = 0.25

# Machine scene tuning
MACHINE_PROX_DIST = 22.0
CLEANING_TIME_SEC = 5.0
RUN_TIME_TO_DIRTY = 40.0
DIRT_MAX_DENSITY   = 220

# ==============================
# Palette (UI theme)
# ==============================
SAND_BASE = (208, 174, 125)
SAND_DOT_A = (187, 153, 107)
SAND_DOT_B = (222, 188, 139)
SAND_DOT_C = (198, 164, 117)
SAND_BORDER_LIGHT = (231, 195, 144)
SAND_BORDER_DARK  = (179, 141, 92)
EDGE_GREY = (103, 98, 89)
WALL_DARK = (40, 40, 40)
MORTAR = (62, 62, 62)
PIPE = (170, 170, 170)
PIPE_SHAD = (130, 130, 130)
NODE = (137, 137, 137)
PLANK = (214, 120, 53)
PLANK_DK = (168, 86, 35)
PLANK_EDGE = (105, 62, 31)
CONCRETE = (170, 168, 160)
CONC_SHAD = (101, 97, 92)
CONC_DOT = (146, 144, 137)
BLACK = (22, 22, 22)
WHITE = (240, 240, 240)
CHEV_BLACK = (0, 0, 0)
CHEV_YEL   = (240, 205, 60)
GREY_FLOOR  = (196, 196, 196)
GREY_FLOOR2 = (184, 184, 184)
HELMET  = (249, 199, 25)
VEST    = (247, 140, 29)
TRIM    = (45, 45, 45)
SLEEVE  = (78, 88, 102)
TROUSERS= (109, 78, 50)
BOOTS   = (35, 35, 35)
SHADOW  = (0, 0, 0, 70)
TRIP_YEL = (255, 220, 70)
TRIP_BLK = (0, 0, 0)
STATION_BODY   = (170, 168, 160)
STATION_EDGE   = (110, 108, 100)
STATION_SCREEN = (60, 140, 80)
STATION_LEGEND = (250, 250, 250)
STATION_LED_ON = (40, 200, 60)
STATION_LED_OFF= (200, 160, 40)
CAB_BODY   = (160, 160, 165)
CAB_EDGE   = (90, 90, 95)
CAB_HANDLE = (70, 70, 75)
CAB_VENT   = (120, 120, 130)
HAZ_TRI_Y  = (245, 210, 60)
HAZ_TRI_B  = (40, 40, 40)
CAB_LED_ON  = (40, 200, 60)
CAB_LED_OFF = (220, 60, 40)
ISO_BODY   = (150, 150, 155)
ISO_EDGE   = (85, 85, 90)
ISO_LEVER  = (80, 80, 85)
ISO_LED_ON  = (40, 200, 60)
ISO_LED_OFF = (220, 60, 40)
TARMAC     = (90, 90, 95)
TARMAC_DOT = (80, 80, 85)
LINE_MARK  = (230, 230, 230)
BARRIER       = (180, 40, 40)
BARRIER_EDGE  = (230, 230, 230)
RED_WARNING    = (255, 60, 60)
AMBER_WARNING  = (255, 210, 90)
PURPLE_LOADING = (190, 110, 255)
BLUE_STATIONARY= (90, 180, 255)
BANNER_BG      = (20, 20, 20, 180)
BORDER_RED     = (255, 80, 80)
BORDER_AMBER   = (255, 220, 90)
BORDER_PURPLE  = (210, 140, 255)
BORDER_BLUE    = (120, 200, 255)
TEXT_COLOR     = (250, 250, 250)
CAM_BODY   = (120, 120, 125)
CAM_EDGE   = (70, 70, 75)
CAM_LENS   = (50, 80, 140)
CAM_LED_OK = (40, 200, 60)
CAM_LED_WARN= (220, 60, 40)
HUD_BG     = (0, 0, 0, 140)
HUD_FG     = (220, 220, 230)
HUD_DOT    = (255, 240, 120)
HUD_VEH    = (120, 220, 255)
HUD_WARN   = (255, 120, 120)

# Machine room visuals
MROOM_FLOOR = (180, 180, 182)
MROOM_FLOOR_DOT = (168, 168, 170)
MACHINE_BODY = (150, 150, 155)
MACHINE_EDGE = (85, 85, 90)
MACHINE_LED_RUN = (220, 60, 40)
MACHINE_LED_STOP = (40, 200, 60)
BEACON_ON  = (255, 180, 80)
BEACON_OFF = (120, 120, 120)
BELT_COLOR = (90, 90, 95)
ROLLER     = (120, 120, 120)
FAN_BLADE  = (200, 200, 200)
TANK_BODY = (120, 130, 180)
TANK_EDGE = (70, 75, 110)
TANK_DIRT = (120, 85, 45)
TANK_CLEAN = (90, 190, 255)
FILL_BG   = (40, 60, 90)

# ==============================
# Fonts + typed getter (single sentinel)
# ==============================
FONT_MAIN = None
FONT_SMALL = None
FONT_TINY = None

def ensure_fonts():
    """
    Initialize fonts once (single sentinel).
    Using FONT_MAIN avoids chained 'and' checks that some linters dislike.
    """
    global FONT_MAIN, FONT_SMALL, FONT_TINY
    if FONT_MAIN is not None:
        return
    if not pygame.font.get_init():
        pygame.font.init()
    try:
        # On web, system fonts may not be available — fallback handled
        FONT_MAIN  = pygame.font.SysFont("consolas", 26, bold=True)
        FONT_SMALL = pygame.font.SysFont("consolas", 18)
        FONT_TINY  = pygame.font.SysFont("consolas", 14)
    except Exception:
        FONT_MAIN  = pygame.font.Font(None, 28)
        FONT_SMALL = pygame.font.Font(None, 18)
        FONT_TINY  = pygame.font.Font(None, 14)

def fonts() -> Tuple[pygame.font.Font, pygame.font.Font, pygame.font.Font]:
    ensure_fonts()
    return FONT_MAIN, FONT_SMALL, FONT_TINY

# ==============================
# Pixel helpers
# ==============================
def pset(surf, x, y, col): surf.fill(col, (x, y, 1, 1))
def rectfill(surf, x, y, w, h, col): surf.fill(col, (x, y, w, h))
def hline(surf, x1, x2, y, col):
    if x2 < x1: x1, x2 = x2, x1
    surf.fill(col, (x1, y, x2 - x1 + 1, 1))
def vline(surf, x, y1, y2, col):
    if y2 < y1: y1, y2 = y2, y1
    surf.fill(col, (x, y1, 1, y2 - y1 + 1))

# ==============================
# Yard drawing
# ==============================
def draw_sand(base, stop_x):
    rectfill(base, 0, 0, stop_x, BASE_H, SAND_BASE)
    for y in range(BASE_H):
        for x in range(stop_x):
            r = (x * 97 + y * 53 + (x ^ y)) % 41
            if r == 0: pset(base, x, y, SAND_DOT_A)
            elif r == 7: pset(base, x, y, SAND_DOT_B)
            elif r == 15: pset(base, x, y, SAND_DOT_C)
    vline(base, stop_x - 8, 0, BASE_H - 1, SAND_BORDER_LIGHT)
    vline(base, stop_x - 7, 0, BASE_H - 1, SAND_BORDER_DARK)

def draw_brick_wall(base, x0):
    rectfill(base, x0, 0, BASE_W - x0, BASE_H, W ALL_DARK)
    bw, bh = 14, 8
    for y in range(0, BASE_H, bh):
        hline(base, x0, BASE_W - 1, y, MORTAR)
        off = (y // bh) % 2 * (bw // 2)
        for x in range(x0 + off, BASE_W, bw):
            vline(base, x, y, min(y + bh, BASE_H - 1), MORTAR)

def draw_scaffold(base, x0, cw=44, ch=44, margin=8):
    for x in range(x0 + margin, BASE_W - margin + 1, cw):
        vline(base, x, 0, BASE_H - 1, PIPE); vline(base, x+1, 0, BASE_H - 1, PIPE_SHAD)
    for y in range(margin, BASE_H - margin + 1, ch):
        hline(base, x0 + margin, BASE_W - margin, y, PIPE); hline(base, x0 + margin, BASE_W - margin, y+1, PIPE_SHAD)
    for y in range(margin, BASE_H - margin + 1, ch):
        for x in range(x0 + margin, BASE_W - margin + 1, cw):
            rectfill(base, x-2, y-2, 5, 5, NODE)
    for y in range(margin, BASE_H - margin - ch + 1, ch):
        for x in range(x0 + margin, BASE_W - margin - cw + 1, cw):
            for d in range(0, cw):
                pset(base, x + d, y + d, PIPE)
                pset(base, x + d, y + (ch - 1) - d, PIPE_SHAD)

def draw_planks(base, x0):
    y_mid = BASE_H // 2 + 2
    rectfill(base, x0 + 8, y_mid - 10, BASE_W - (x0 + 16), 20, PLANK)
    vline(base, BASE_W - (BASE_W - (x0 + 8)) // 2, y_mid - 10, y_mid + 9, PLANK_EDGE)
    for yy in range(y_mid - 7, y_mid + 8, 4):
        hline(base, x0 + 12, BASE_W - 12, yy, PLANK_DK)
    hline(base, x0 + 8, BASE_W - 9, y_mid - 10, PLANK_EDGE)
    hline(base, x0 + 8, BASE_W - 9, y_mid + 10, PLANK_EDGE)

def draw_platform(base, x0):
    y_mid = BASE_H // 2 + 2
    plat_w, plat_h = 30, 24
    plat_x = x0 - plat_w + 2
    plat_y = y_mid - plat_h // 2
    rectfill(base, plat_x, plat_y, plat_w, plat_h, CONCRETE)
    for _ in range(60):
        rx = plat_x + 2 + random.randint(0, plat_w - 4)
        ry = plat_y + 2 + random.randint(0, plat_h - 4)
        pset(base, rx, ry, CONC_DOT)
    rectfill(base, plat_x - 1, plat_y + plat_h - 2, plat_w + 2, 2, CONC_SHAD)
    rectfill(base, plat_x - 2, plat_y + 2, 2, plat_h - 4, CONC_SHAD)

def draw_edge_and_chevrons(base, x0, band_w=12, period=8):
    vline(base, x0 - 1, 0, BASE_H - 1, EDGE_GREY)
    bx0 = x0 - 1 - band_w
    for y in range(BASE_H):
        for x in range(bx0, x0 - 1):
            pset(base, x, y, CHEV_BLACK if (x + y) % period < period // 2 else CHEV_YEL)

def draw_trip_line(base, line_x):
    for y in range(0, BASE_H, 4):
        rectfill(base, line_x, y, 1, 2, TRIP_YEL)
        rectfill(base, line_x, y + 2, 1, 2, TRIP_BLK)

def draw_permit_station(base, cx, cy, has_permit):
    x, y = cx - 10, cy - 8
    rectfill(base, x, y, 20, 16, STATION_BODY)
    for dx in (0, 19): vline(base, x + dx, y, y + 15, STATION_EDGE)
    for dy in (0, 15): hline(base, x, x + 19, y + dy, STATION_EDGE)
    rectfill(base, x + 3, y + 3, 10, 6, STATION_SCREEN)
    hline(base, x + 2, x + 17, y + 12, STATION_LEGEND)
    rectfill(base, x + 16, y + 2, 2, 2, STATION_LED_ON if has_permit else STATION_LED_OFF)

def draw_worker(base, cx, cy):
    x, y = cx - 7, cy - 14
    sh = pygame.Surface((12, 4), pygame.SRCALPHA); sh.fill((0, 0, 0, 70)); base.blit(sh, (x + 6, y + 14))
    rectfill(base, x + 2, y + 14, 4, 2, (35, 35, 35)); rectfill(base, x + 8, y + 14, 4, 2, (35, 35, 35))
    rectfill(base, x + 3, y + 10, 3, 4, (109, 78, 50)); rectfill(base, x + 9, y + 10, 3, 4, (109, 78, 50))
    rectfill(base, x + 2, y + 5, 10, 6, (247, 140, 29)); hline(base, x + 2, x + 11, y + 7, (45, 45, 45)); vline(base, x + 7, y + 5, y + 10, (45, 45, 45))
    rectfill(base, x + 1, y + 6, 2, 5, (78, 88, 102)); rectfill(base, x + 11, y + 6, 2, 5, (78, 88, 102))
    rectfill(base, x + 2, y + 2, 10, 3, (249, 199, 25))

# ==============================
# Physical cameras (fixtures)
# ==============================
def draw_camera_fixture_yard(base):
    x = BASE_W - 26; y = 12
    rectfill(base, x, y, 14, 8, (120, 120, 125))
    pygame.draw.rect(base, (70, 70, 75), (x, y, 14, 8), 1)
    rectfill(base, x+2, y+2, 6, 4, (50, 80, 140))
    rectfill(base, x+10, y+2, 2, 2, (40, 200, 60))

def draw_camera_fixture_elec(base):
    x = 110; y = 8
    rectfill(base, x, y, 16, 8, (120, 120, 125))
    pygame.draw.rect(base, (70, 70, 75), (x, y, 16, 8), 1)
    rectfill(base, x+3, y+3, 5, 3, (50, 80, 140))
    rectfill(base, x+12, y+2, 2, 2, (40, 200, 60))

def draw_camera_fixture_vehicle(base):
    x = BASE_W//2 - 6; y = 6
    rectfill(base, x, y, 12, 10, (120, 120, 125))
    pygame.draw.rect(base, (70, 70, 75), (x, y, 12, 10), 1)
    rectfill(base, x+4, y+4, 4, 3, (50, 80, 140))
    rectfill(base, x+2, y+2, 2, 2, (40, 200, 60))

def draw_camera_fixture_machine(base):
    x = BASE_W//2 - 6; y = 6
    rectfill(base, x, y, 12, 10, (120, 120, 125))
    pygame.draw.rect(base, (70, 70, 75), (x, y, 12, 10), 1)
    rectfill(base, x+5, y+4, 3, 3, (50, 80, 140))
    rectfill(base, x+2, y+2, 2, 2, (40, 200, 60))

# ==============================
# Electrical drawing (omitted here to save space — unchanged)
# ==============================
# ... (keep your existing electrical, vehicle, machine drawing & logic blocks)

# (For brevity: include the rest of your previously shared functions unchanged:
# draw_elec_floor, draw_elec_cabinet, draw_trip_rect, draw_isolation_station,
# draw_tarmac, draw_barrier, draw_vehicle_sprite,
# draw_machine_floor, draw_live_machine, draw_tank,
# UI kit (upscale, draw_spotlight, draw_panel, draw_severity_icon, etc),
# Camera HUD, utilities (clamp, dist2, point_in_rect, circle_rect_collision),
# vehicle controller (make_vehicle, vehicle_update),
# scene composition (render_yard_base/render_electrical_base/render_vehicle_base/render_machine_base),
# side panel & legend, config/logging functions.)
#
# Paste those blocks back exactly as in your latest local file.
#
# Below, we only show the parts that change for PyGBag: the main() and the save guard.)

# ==============================
# Main (async for PyGBag)
# ==============================
async def main():
    pygame.init()
    pygame.display.set_caption("Safety Training v6.3.1 – Web (PyGBag)")
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    clock = pygame.time.Clock()
    ensure_fonts()

    # --- your existing config / load_config(), session logging, state init ---
    # (Use the same state initializations from your v6_3_1 desktop version)
    # Default machine_running=True, etc.

    # Example: tiny subset (replace with your full state init)
    scene = SCENE_YARD
    has_permit = False
    isolated = False
    show_debug = False
    show_vignette = True
    show_hud = True
    show_legend = False
    paused = False

    machine_running = True
    tank_dirty = False
    cleaning_timer = 0.0
    run_time_since_clean = 0.0
    fill_level = 0.75
    belt_phase = 0
    fan_phase = 0
    beacon_on = False

    # Geometry and vehicles as in your v6_3_1
    # ...
    px, py = 70, 150
    BLINK_MS = 500
    save_requested = False
    running_loops = True

    while running_loops:
        dt = clock.get_time() / 1000.0

        # --- events ---
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                # On web, just stop the loop; no pygame.quit/sys.exit after asyncio.run
                running_loops = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running_loops = False
                elif event.key == pygame.K_p:
                    paused = not paused
                elif event.key == pygame.K_s:
                    # Disable file saving in browser to avoid I/O issues
                    if sys.platform == "emscripten":
                        # Optionally draw a banner/message in your HUD instead
                        save_requested = False
                    else:
                        save_requested = True
                # ... keep your other key handlers unchanged (D/V/H/F1, scenes, machine controls)

        if paused:
            # draw pause UI
            # draw_pause_menu(screen)  # keep your function call
            pygame.display.flip()
            # Yield to browser each frame
            await asyncio.sleep(0)
            clock.tick(FPS)
            continue

        # --- movement & scene logic ---
        keys = pygame.key.get_pressed()
        spd = 1 + (1 if (keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]) else 0)
        if keys[pygame.K_LEFT]:  px -= spd
        if keys[pygame.K_RIGHT]: px += spd
        if keys[pygame.K_UP]:    py -= spd
        if keys[pygame.K_DOWN]:  py += spd

        # ... keep your nested-if scene gates and all per scene logic exactly as in v6_3_1 ...

        # --- rendering ---
        # base = render_...()
        # screen.blit(upscale(base), (0,0))
        # overlays/banners, side panel, legend, HUD, camera LEDs, vignette
        # ...

        # If desktop, allow snapshot
        if save_requested and sys.platform != "emscripten":
            pygame.image.save(screen, "safety_training_snapshot_web.png")
            save_requested = False

        pygame.display.flip()

        # *** Critical for PyGBag: yield to browser every frame ***
        await asyncio.sleep(0)  # required by PyGBag
        clock.tick(FPS)

    # (No pygame.quit() here; returning is fine in PyGBag)


# Required: this must be the final executable statement in the file for PyGBag
# and do not add code after it (no sys.exit/pygame.quit after asyncio.run)
if __name__ == "__main__":
    asyncio.run(main())

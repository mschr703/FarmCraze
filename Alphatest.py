import pygame
import sys
import os
import time

WINDOW_WIDTH: int = 800
WINDOW_HEIGHT: int = 500

BLACK: tuple = (0, 0, 0)
RED: tuple = (255, 0, 0)
BLUE: tuple = (0, 0, 255)
WHITE: tuple = (255, 255, 255)
DARK_GRAY = (50, 50, 50)
HOVER_COLOR = (100, 100, 100)

VELOCITY: int = 10  # geschwindigkeit der spieler

pygame.init()
state = "menu"

clock = pygame.time.Clock()
fps: int = 60

font = pygame.font.SysFont("arial", 36)

WIDTH, HEIGHT = 1920, 1080
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("FarmCraze")

icon = pygame.image.load("./media/main-menu/logo/icon.png")
pygame.display.set_icon(icon)

# Hintergrund-Frames laden
bg_frames = []
bg_folder = "./media/main-menu/background/frames"
for filename in sorted(os.listdir(bg_folder)):
    if filename.endswith(".png"):
        img = pygame.image.load(os.path.join(bg_folder, filename))
        img = pygame.transform.scale(img, (WIDTH, HEIGHT))
        bg_frames.append(img)

bg_frame_index = 0
bg_frame_timer = 0
bg_frame_speed = 100

# Logo
logo = pygame.image.load("./media/main-menu/logo/logo-transparent.png")
if hasattr(pygame.transform, 'scale_by'):
    logo = pygame.transform.scale_by(logo, 0.4)
else:
    logo_rect_temp = logo.get_rect()
    new_size = (int(logo_rect_temp.width * 0.4), int(logo_rect_temp.height * 0.4))
    logo = pygame.transform.scale(logo, new_size)
logo_rect = logo.get_rect(center=(WIDTH // 2, 150))

# --------------------- Buttons ----------------------------------
button_size = (290, 100)

btn_spielen = pygame.image.load("./media/main-menu/buttons/button-spielen.png").convert_alpha()
btn_spielen = pygame.transform.scale(btn_spielen, button_size)

btn_einstellungen = pygame.image.load("./media/main-menu/buttons/button-einstellungen.png").convert_alpha()
btn_einstellungen = pygame.transform.scale(btn_einstellungen, button_size)

btn_verlassen = pygame.image.load("./media/main-menu/buttons/button-verlassen.png").convert_alpha()
btn_verlassen = pygame.transform.scale(btn_verlassen, button_size)

def make_hover(surface):
    hover_img = surface.copy()
    hover_img.fill((50, 50, 50, 0), special_flags=pygame.BLEND_RGB_ADD)
    return hover_img

btn_spielen_hover = make_hover(btn_spielen)
btn_einstellungen_hover = make_hover(btn_einstellungen)
btn_verlassen_hover = make_hover(btn_verlassen)

button_spacing = 110
start_y = 395

sp_rect = btn_spielen.get_rect(center=(WIDTH // 2, start_y))
einst_rect = btn_einstellungen.get_rect(center=(WIDTH // 2, start_y + button_spacing))
quit_rect = btn_verlassen.get_rect(center=(WIDTH // 2, start_y + 2 * button_spacing))

# Ping-Pong-Animation
sp_base_y = sp_rect.centery
sp_offset = 0.0
sp_dir = 1

einst_base_y = einst_rect.centery
einst_offset = 0.0
einst_dir = 1

quit_base_y = quit_rect.centery
quit_offset = 0.0
quit_dir = 1

button_speed = 0.01
button_amplitude = 2

# --------------------- Schaf ----------------------------------
sheep_paths = [
    "./media/main-menu/background/schaf/sheep-idle.png",
    "./media/main-menu/background/schaf/sheep-walk.png"
]
sheep_frames = []
sheep_scale = 0.2
for path in sheep_paths:
    img = pygame.image.load(path).convert_alpha()
    w, h = img.get_size()
    new_w, new_h = int(w * sheep_scale), int(h * sheep_scale)
    scaled_img = pygame.transform.scale(img, (new_w, new_h))
    sheep_frames.append(scaled_img)

sheep_x = -128
sheep_y = HEIGHT - 280
sheep_speed = 2
sheep_frame_index = 0
sheep_animation_timer = 0
sheep_frame_delay = 800

# --------------------- Hund ----------------------------------
dog_paths = [
    "./media/main-menu/background/hund/dog-idling.png",
    "./media/main-menu/background/hund/dog-walking.png"
]
dog_frames = []
dog_scale = 0.2
for path in dog_paths:
    img = pygame.image.load(path).convert_alpha()
    w, h = img.get_size()
    new_w, new_h = int(w * dog_scale), int(h * dog_scale)
    scaled_img = pygame.transform.scale(img, (new_w, new_h))
    dog_frames.append(scaled_img)

dog_frame_index = 0
dog_animation_timer = 0
dog_frame_delay = 800
dog_x_offset = -350
dog_y_offset = 0

# --------------------- Wolken ---------------------------------
wolke = pygame.image.load("./media/main-menu/background/wolke.png").convert_alpha()
if hasattr(pygame.transform, 'scale_by'):
    wolke = pygame.transform.scale_by(wolke, 0.3)
else:
    w, h = wolke.get_size()
    wolke = pygame.transform.scale(wolke, (int(w * 0.4), int(h * 0.4)))

clouds = []
for i in range(3):
    c = {
        "x": -200 - i * 300,
        "y_base": 100 + i * 60,
        "y_offset": 0,
        "direction": 1,
        "speed_x": 0.3,
        "speed_y": 0.1
    }
    clouds.append(c)

# --------------------- Musik & Sound --------------------------
pygame.mixer.init()
music_started = False

pygame.mixer.music.load("./media/main-menu/sound/music/main-menu-music.wav")
pygame.mixer.music.set_volume(0.3)
vogel_sound = pygame.mixer.Sound("./media/main-menu/sound/music/vogelgezwitscher.wav")
vogel_sound.set_volume(0.4)

button_click_sound = pygame.mixer.Sound("./media/main-menu/sound/button-sounds/button-click.wav")
button_click_sound.set_volume(0.5)

# --------------------- Settings-UI (Kleiner + X-Button) -------
settings_ui = pygame.image.load("./media/main-menu/ui/settings-ui.png").convert_alpha()
# Skalieren auf 600×400 (Beispiel)
settings_ui = pygame.transform.scale(settings_ui, (600, 700))
settings_ui_rect = settings_ui.get_rect(center=(WIDTH // 2, HEIGHT // 2))

# "X" oben rechts
# Wir rendern ein kleines "X" an der Ecke
font_small = pygame.font.SysFont("arial", 30)
close_text = font_small.render("X", True, WHITE)
# Platzieren wir 35 px vom rechten Rand / 10 px von oben
close_rect = close_text.get_rect()
close_rect.x = settings_ui_rect.right - 40
close_rect.y = settings_ui_rect.top + 10

running = True

while running:
    dt = clock.tick(fps)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        # State: MENU
        if state == "menu":
            if event.type == pygame.MOUSEBUTTONDOWN:
                if sp_rect.collidepoint(event.pos):
                    button_click_sound.play()
                    print("Spiel starten")
                    pygame.mixer.music.stop()
                    vogel_sound.stop()
                    state = "game"
                    music_started = False

                elif einst_rect.collidepoint(event.pos):
                    button_click_sound.play()
                    print("Einstellungen öffnen")
                    state = "settings"

                elif quit_rect.collidepoint(event.pos):
                    button_click_sound.play()
                    time.sleep(2.5)
                    pygame.quit()
                    sys.exit()

        # State: SETTINGS
        elif state == "settings":
            if event.type == pygame.MOUSEBUTTONDOWN:
                if close_rect.collidepoint(event.pos):
                    # Klick aufs X
                    button_click_sound.play()
                    state = "menu"

        # State: GAME
        elif state == "game":
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                state = "menu"

    # ------------------- LOGIK: MENU -------------------
    if state == "menu":
        # Hintergrund
        bg_frame_timer += dt
        if bg_frame_timer >= bg_frame_speed:
            bg_frame_index = (bg_frame_index + 1) % len(bg_frames)
            bg_frame_timer = 0

        if not music_started:
            pygame.mixer.music.play(-1)
            vogel_sound.play(-1)
            music_started = True

        for c in clouds:
            c["x"] += c["speed_x"]
            c["y_offset"] += c["speed_y"] * c["direction"]
            if abs(c["y_offset"]) > 10:
                c["direction"] *= -1
            if c["x"] > WIDTH + 100:
                c["x"] = -300

        # Schaf
        sheep_x += sheep_speed
        if sheep_x > WIDTH:
            sheep_x = -128
        sheep_animation_timer += dt
        if sheep_animation_timer >= sheep_frame_delay:
            sheep_frame_index = (sheep_frame_index + 1) % len(sheep_frames)
            sheep_animation_timer = 0

        # Hund
        dog_x = sheep_x + dog_x_offset
        dog_y = sheep_y + dog_y_offset
        dog_animation_timer += dt
        if dog_animation_timer >= dog_frame_delay:
            dog_frame_index = (dog_frame_index + 1) % len(dog_frames)
            dog_animation_timer = 0

        # Buttons Ping-Pong
        sp_offset += dt * button_speed * sp_dir
        if sp_offset > button_amplitude:
            sp_offset = button_amplitude
            sp_dir = -1
        elif sp_offset < -button_amplitude:
            sp_offset = -button_amplitude
            sp_dir = 1
        sp_rect.centery = sp_base_y + int(sp_offset)

        einst_offset += dt * button_speed * einst_dir
        if einst_offset > button_amplitude:
            einst_offset = button_amplitude
            einst_dir = -1
        elif einst_offset < -button_amplitude:
            einst_offset = -button_amplitude
            einst_dir = 1
        einst_rect.centery = einst_base_y + int(einst_offset)

        quit_offset += dt * button_speed * quit_dir
        if quit_offset > button_amplitude:
            quit_offset = button_amplitude
            quit_dir = -1
        elif quit_offset < -button_amplitude:
            quit_offset = -button_amplitude
            quit_dir = 1
        quit_rect.centery = quit_base_y + int(quit_offset)

        # RENDER MENU
        screen.blit(bg_frames[bg_frame_index], (0, 0))

        for c in clouds:
            wolke_y = c["y_base"] + c["y_offset"]
            screen.blit(wolke, (c["x"], wolke_y))

        current_dog = dog_frames[dog_frame_index]
        screen.blit(current_dog, (dog_x, dog_y))

        current_sheep = sheep_frames[sheep_frame_index]
        screen.blit(current_sheep, (sheep_x, sheep_y))

        screen.blit(logo, logo_rect)

        mouse_pos = pygame.mouse.get_pos()
        if sp_rect.collidepoint(mouse_pos):
            screen.blit(btn_spielen_hover, sp_rect)
        else:
            screen.blit(btn_spielen, sp_rect)

        if einst_rect.collidepoint(mouse_pos):
            screen.blit(btn_einstellungen_hover, einst_rect)
        else:
            screen.blit(btn_einstellungen, einst_rect)

        if quit_rect.collidepoint(mouse_pos):
            screen.blit(btn_verlassen_hover, quit_rect)
        else:
            screen.blit(btn_verlassen, quit_rect)

    # ------------------- SETTINGS ----------------------
    elif state == "settings":
        # Einfachen Hintergrund
        screen.blit(bg_frames[bg_frame_index], (0, 0))
        # Das UI-Fenster
        screen.blit(settings_ui, settings_ui_rect)
        # Das X
        screen.blit(close_text, close_rect)

    # ------------------- GAME -------------------------
    elif state == "game":
        screen.fill((0, 120, 60))
        game_text = font.render("Das Spiel läuft...", True, WHITE)
        screen.blit(game_text, (WIDTH // 2 - 200, HEIGHT // 2))

    pygame.display.flip()

pygame.quit()

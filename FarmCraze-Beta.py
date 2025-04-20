import pygame
import sys
import os
import time
import random
import math
import webbrowser


#! Note 1:
# Das Spiel ist weitaus nicht in dem erwarteten Zustand, ich werde auch nach Abgabe hieran arbeiten.
# Schwierigkeit: Timer der Tiere wird schneller, Tiere lösen sich ab (Mehr % bei erhöhter schwierigkeit) -> Bsp: Line 820
# Dictionary genutzt bei Timer (728) "sheep list"

#! Note 2:
# Am besten lesbar mit der VS code extension: Colorful Comments

# -----------                           -----------
#* Zum verändern: (STRG+F & Dazugehörige Value suchen)
# -----------                           -----------
#* Hauptmenü
# [PPA] - Ping-Pong Animationsgeschwindigkeit
# -----            
#* Powerups & Snacks:
# [PKTbearb] - Pull range von dem Magnet Powerup
# [SCBbearb] - Score Bonus durch den Score Powerup
# [SBPUbearb] - Speed Bonus durch Speed Powerup
# [SNPIbearb] - Snack Spawn Intervall
# [FPETbearb] - Timer (wie lange der Freeze Powerup anhält)
# [SNCKprob] - probability das der snack toxic wird je nach schwierigkeit
# [PUTIbearb] - Despawn Zeit der Powerups
# ----- 
#* Events
# [UFOWSKbearb] - Ufo Event Spawn Wahrscheinlichkeit
# ----- 
#* Tiere:
# [SAT1bearb] - Timer der Schafe bearbeiten
# [VABCTbearb] - Schaf bricht Verfolgung ab (chance)
# [SFVSnormal] & [SFVSevent] - Verfolgungs-Speed der Schafe normal und in einem Event wie zb UFO
# ----- 
#* Spiel:
# [TABbearb] - Ab wann der Tag wieder beginnt (in der Nacht)
# [DLVRYbearb] - Delivery Zone der Schafe um den Stall herum
# ----- 

#^ -----------------------
#^ Grundlegende Settings
#^ -----------------------
WINDOW_WIDTH: int = 800
WINDOW_HEIGHT: int = 500

BLACK: tuple = (0, 0, 0)
RED: tuple = (255, 0, 0)
BLUE: tuple = (0, 0, 255)
WHITE: tuple = (255, 255, 255)
DARK_GRAY = (50, 50, 50)
HOVER_COLOR = (100, 100, 100)

VELOCITY: int = 10  # geschwindigkeit des spielers

pygame.init()
state = "menu"  #! mögliche States bisher: "menu", "choose_difficulty", "settings", "game"

clock = pygame.time.Clock()
fps: int = 60

#^ ==============================
#^ Highscore‑Datei einlesen
#^ ==============================

#! Das ist eine kleine lösung um den Score & die Coins zu speichern (auch nachdem man das game geschlossen hat) per txt datei

HIGH_SCORE_FILE = "highscore.txt"
COINS_FILE      = "coins.txt"

# Highscore laden
if os.path.exists(HIGH_SCORE_FILE):
    try:
        with open(HIGH_SCORE_FILE, "r") as f:
            highscore = int(f.read().strip())
    except:
        highscore = 0
else:
    highscore = 0

# Coins laden
if os.path.exists(COINS_FILE):
    try:
        with open(COINS_FILE, "r") as f:
            coins = int(f.read().strip())
    except:
        coins = 0
else:
    coins = 0
    highscore = 0

#^ -----------------------
#^ Pixelart-ähnliche Font (ByteBounce)
#^ -----------------------
try:
    pixel_font = pygame.font.Font("./media/fonts/ByteBounce.ttf", 48)
except:
    pixel_font = pygame.font.SysFont("couriernew", 48, bold=True)
    print("WARNUNG: ByteBounce.ttf nicht gefunden, nutze CourierNew stattdessen.")

# Kleiner Font fürs "X" im Settings
font_small = pygame.font.SysFont("arial", 30)

WIDTH, HEIGHT = 1920, 1080
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("FarmCraze")

# Icon
icon = pygame.image.load("./media/main-menu/logo/icon.png")
pygame.display.set_icon(icon)

#^ -----------------------
#^ Hintergrund-Animation
#^ -----------------------
# Das ist dafür da, um die pygame Gif sperre zu umgehen. Per Ordner alle frames von gif als bild = einzelnd laden
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

#^ -----------------------
#^ Logo
#^ -----------------------

logo = pygame.image.load("./media/main-menu/logo/logo-transparent.png")
if hasattr(pygame.transform, 'scale_by'):
    logo = pygame.transform.scale_by(logo, 0.4)
else:
    logo_rect_temp = logo.get_rect()
    new_size = (int(logo_rect_temp.width * 0.4), int(logo_rect_temp.height * 0.4))
    logo = pygame.transform.scale(logo, new_size)
logo_rect = logo.get_rect(center=(WIDTH // 2, 150))

#^ -----------------------
#^  ==== HUD Images ====
#^ -----------------------

# Münz-Icon für die Geldanzeige
coin_img = pygame.image.load("./media/game/hud/coin.png").convert_alpha()
coin_img = pygame.transform.scale(coin_img, (32, 32))

# Herz-Icon für Lebensanzeige
heart_img = pygame.image.load("./media/game/hud/heart.png").convert_alpha()
heart_img = pygame.transform.scale(heart_img, (32, 32))  # je nach Stil ggf. anpassen

#^ ------------------------------------------------------------
#^ Hauptmenü Buttons (Spielen, Einstellungen, Verlassen)
#^ ------------------------------------------------------------

button_size = (290, 100)

btn_spielen = pygame.image.load("./media/main-menu/buttons/button-spielen.png").convert_alpha()
btn_spielen = pygame.transform.scale(btn_spielen, button_size)

btn_einstellungen = pygame.image.load("./media/main-menu/buttons/button-anleitung.png").convert_alpha()
btn_einstellungen = pygame.transform.scale(btn_einstellungen, button_size)

btn_verlassen = pygame.image.load("./media/main-menu/buttons/button-verlassen.png").convert_alpha()
btn_verlassen = pygame.transform.scale(btn_verlassen, button_size)

# Buttons für die Socials

btn_github = pygame.image.load("./media/main-menu/buttons/button-github.png").convert_alpha()
btn_github = pygame.transform.scale(btn_github, (70, 70))

btn_trello = pygame.image.load("./media/main-menu/buttons/button-trello.png").convert_alpha()
btn_trello = pygame.transform.scale(btn_trello, (70, 70))



#& Hover Funktion für die buttons
def make_hover(surface):
    hover_img = surface.copy() #& Surface kopieren / fillen mit weiss = hover effekt für die buttons
    hover_img.fill((50, 50, 50, 0), special_flags=pygame.BLEND_RGB_ADD)
    return hover_img

#& Letzter step für den hover effekt
btn_spielen_hover = make_hover(btn_spielen)
btn_einstellungen_hover = make_hover(btn_einstellungen)
btn_verlassen_hover = make_hover(btn_verlassen)
btn_github_hover = make_hover(btn_github)
btn_trello_hover = make_hover(btn_trello)

#& button tweaks
button_spacing = 110 # abstand zwischen den buttons
start_y = 395 # start y

# rects für spielbuttons
sp_rect = btn_spielen.get_rect(center=(WIDTH // 2, start_y))
einst_rect = btn_einstellungen.get_rect(center=(WIDTH // 2, start_y + button_spacing))
quit_rect = btn_verlassen.get_rect(center=(WIDTH // 2, start_y + 2 * button_spacing))
# rects für social buttons
github_rect = btn_github.get_rect(topleft=(20, 110))
trello_rect = btn_trello.get_rect(topleft=(github_rect.right + 20, 110))


#* Ping-Pong-Animation (Hauptmenü) [PPA]
sp_base_y = sp_rect.centery #& Centery = Center von dem rect // sp base is die start referenz für die animation
sp_offset = 0.0 #& Wie sehr sie bisher gemoved haben
sp_dir = 1 #& dir = directions / Richtung wohin sie moven

einst_base_y = einst_rect.centery
einst_offset = 0.0
einst_dir = 1

quit_base_y = quit_rect.centery
quit_offset = 0.0
quit_dir = 1

button_speed = 0.01 #& Schnelligkeit bewegung der buttons
button_amplitude = 2 #& Amount wie sehr es hoch und runter moved

#^ ------------------------------------------------------------
#^ Schwierigkeits-Buttons (Leicht, Mittel, Schwer)
#^ ------------------------------------------------------------
diff_button_size = (300, 130) #& Button größe für 

btn_leicht = pygame.image.load("./media/main-menu/buttons/button-leicht.png").convert_alpha()
btn_leicht = pygame.transform.scale(btn_leicht, diff_button_size)

btn_mittel = pygame.image.load("./media/main-menu/buttons/button-mittel.png").convert_alpha()
btn_mittel = pygame.transform.scale(btn_mittel, diff_button_size)

btn_schwer = pygame.image.load("./media/main-menu/buttons/button-schwer.png").convert_alpha()
btn_schwer = pygame.transform.scale(btn_schwer, diff_button_size)

btn_leicht_hover = make_hover(btn_leicht)
btn_mittel_hover = make_hover(btn_mittel)
btn_schwer_hover = make_hover(btn_schwer)

diff_spacing = 150
diff_start_y = 395

leicht_rect = btn_leicht.get_rect(center=(WIDTH // 2, diff_start_y))
mittel_rect = btn_mittel.get_rect(center=(WIDTH // 2, diff_start_y + diff_spacing))
schwer_rect = btn_schwer.get_rect(center=(WIDTH // 2, diff_start_y + 2 * diff_spacing))

selected_difficulty = None

#^ ------------------------------------------------------------
#^ Kleine "Verbrauchs"-Items
#^ ------------------------------------------------------------

#^ SNACKS 

snack_images = {
    "healthy": pygame.transform.scale(
        pygame.image.load("./media/game/images/snacks/Snack-healthy.png").convert_alpha(),
        (64, 64)
    ),
    "toxic": pygame.transform.scale(
        pygame.image.load("./media/game/images/snacks/Snack-toxic.png").convert_alpha(),
        (64, 64)
    ),
}

snack = None
snack_spawn_timer = 0.0
snack_spawn_interval = 30.0 #* [SNPIbearb]

#* [SNCKprob] Wahrscheinlichkeit für toxische Snacks je nach Schwierigkeit
snack_toxic_chances = {
    "Leicht": 0.20,   # 20 %
    "Mittel": 0.35,   # 35 %
    "Schwer": 0.55    # 55 %
}



#^ ------------------------------------------------------------
#^ Schaf (Deko im Menü)
#^ ------------------------------------------------------------

menusheep_paths = [ # 2 states
    "./media/main-menu/background/schaf/sheep-idle.png",
    "./media/main-menu/background/schaf/sheep-walk.png"
]

menusheep_frames = []
sheep_scale = 0.2
for path in menusheep_paths:
    img = pygame.image.load(path).convert_alpha()
    w, h = img.get_size()
    new_w, new_h = int(w * sheep_scale), int(h * sheep_scale)
    scaled_img = pygame.transform.scale(img, (new_w, new_h))
    menusheep_frames.append(scaled_img)

menusheep_x = -128
menusheep_y = HEIGHT - 280
menusheep_speed = 2
menusheep_frame_index = 0
menusheep_animation_timer = 0
menusheep_frame_delay = 800

#^ ------------------------------------------------------------
#^ Hund (Deko im Menü)
#^ ------------------------------------------------------------
dog_paths = [
    "./media/main-menu/background/hund/dog-idling.png",
    "./media/main-menu/background/hund/dog-walking.png" #& 2 States für den Hunden laden
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

#^ ------------------------------------------------------------
#^ Wolken
#^ ------------------------------------------------------------
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

#^ ------------------------------------------------------------
#^ Musik & Sounds
#^ ------------------------------------------------------------

pygame.mixer.init()
music_started = False

pygame.mixer.music.load("./media/main-menu/sound/music/main-menu-music.wav") # selbstgemachte main menu musik (erstellungsvideo in word dokument)
pygame.mixer.music.set_volume(0.3)
vogel_sound = pygame.mixer.Sound("./media/main-menu/sound/music/vogelgezwitscher.wav")
vogel_sound.set_volume(0.4) # lautstärke

button_click_sound = pygame.mixer.Sound("./media/main-menu/sound/button-sounds/button-click.wav")
button_click_sound.set_volume(0.5)

cancel_sound = pygame.mixer.Sound("./media/game/sounds/effects/sonstiges/cancel.wav")
cancel_sound.set_volume(0.6)

pickup_sound = pygame.mixer.Sound("./media/game/sounds/effects/sonstiges/pickup.wav")
pickup_sound.set_volume(0.4)

deliver_sound = pygame.mixer.Sound("./media/game/sounds/effects/sonstiges/deliver.wav")
deliver_sound.set_volume(0.5)

clock_tick_sound = pygame.mixer.Sound("./media/game/sounds/effects/sonstiges/clock.wav")
loose_sound = pygame.mixer.Sound("./media/game/sounds/effects/sonstiges/loose.wav")

powerup_sound = pygame.mixer.Sound("./media/game/sounds/effects/sonstiges/powerup.wav")
powerup_sound.set_volume(0.5)

#^ ------------------------------------------------------------
#^ Geräusche für den Hund
#^ ------------------------------------------------------------

dog_eat_sound = pygame.mixer.Sound("./media/game/sounds/effects/animals/dog-eating.wav") # essen zb snacks
dog_eat_sound.set_volume(0.5)

dog_walk_sound = pygame.mixer.Sound("./media/game/sounds/effects/animals/dog-walking.wav") # beim laufen
dog_walk_sound.set_volume(0.4)

dog_bark_sound = pygame.mixer.Sound("./media/game/sounds/effects/animals/dog-barking.wav") # zufällig bellen
dog_bark_sound.set_volume(0.6)


#^ ------------------------------------------------------------
#^ MAPS + Musik für Game-State
#^ ------------------------------------------------------------
map_paths = [
    "./media/game/maps/map1/map1-day.png",
    "./media/game/maps/map2/map2-day.png",
    "./media/game/maps/map3/map3-day.png"
]
map_surface = None
day_music = "./media/game/sounds/music/song1-day.wav"
night_music = "./media/game/sounds/music/song1-night.wav"

#^ ------------------------------------------------------------
#^ Spieler (Wolf) mit 4 Einzelbildern (oben, links, unten, rechts)
#^ ------------------------------------------------------------
player_scale = 0.1
def load_and_scale(path, scale):
    img_ = pygame.image.load(path).convert_alpha()
    w_, h_ = img_.get_size()
    return pygame.transform.scale(img_, (int(w_*scale), int(h_*scale)))

player_sprites = {
    "up":    load_and_scale("./media/game/sprites/player/oben.png",   player_scale),
    "left":  load_and_scale("./media/game/sprites/player/links.png",  player_scale),
    "down":  load_and_scale("./media/game/sprites/player/unten.png",  player_scale),
    "right": load_and_scale("./media/game/sprites/player/rechts.png", player_scale),
}

player_x = 400
player_y = 300
player_speed = 4
player_direction = "down"
tick = 0
is_walking = False

#^ -------------------------
#^ Schaf mit 4 einzelbildern
#^ -------------------------

sheep_scale = 0.1  # gleiche Größe wie der Spieler
def load_sheep_sprite(name):
    return load_and_scale(f"./media/game/sprites/sheep/{name}.png", sheep_scale)

sheep_sprites = {
    "up": load_sheep_sprite("oben"),
    "down": load_sheep_sprite("unten"),
    "left": load_sheep_sprite("links"),
    "right": load_sheep_sprite("rechts"),
}

#^ Schaf Timer 

def get_default_timer(difficulty):
    if difficulty == "Leicht": #* [SAT1bearb] Timer der Schafe bearbeiten
        return 36.0
    elif difficulty == "Mittel":
        return 29.0
    else:
        return 24.0


#^ ─────────────────────────────────────────────────────────────────────
#^ Wolf (Gegner in der Nacht)
#^ ─────────────────────────────────────────────────────────────────────
#^ zwei Sprite‑Varianten für die Gegner (links/rechts)

enemy_scale = 0.1
enemy_sprites = {
    "left": load_and_scale("./media/game/sprites/enemy/wolf-left.png", enemy_scale),
    "right": load_and_scale("./media/game/sprites/enemy/wolf-right.png", enemy_scale),
    # für up und down genau die gleichen
    "up":    load_and_scale("./media/game/sprites/enemy/wolf-left.png", enemy_scale),
    "down":  load_and_scale("./media/game/sprites/enemy/wolf-right.png", enemy_scale),
}

# Liste der aktiven enemys
enemies = []  # wird befüllt, sobald Nacht beginnt
enemy_speed = 2
enemy_change_dir_interval = 2.0  # Sekunden, bis sie zufällig die Richtung ändern


# sonstige variablen für später
sheep_currently_following = None # checken ob schaf schon verfolgt für später
cancel_message_timer = 0.0 # der -1 text
cancel_message_alpha = 0
current_day = 1
score = 0
score_popups = []
sheep_list = []

game_over = False

#^ --------------------------
#^ Random-Event Variablen (UFO-Event, Vulkan-Event, Sturm-Event)
#^ --------------------------

#? Ufo Event Variablen
event_active = False
event_timer = 0.0
event_duration = 15.0
event_type = None

#? UFO Event UI
ufo_img = pygame.image.load("./media/game/images/events/ufo/ufo.png").convert_alpha()
ufo_img = pygame.transform.scale_by(ufo_img, 0.1)  # ggf. anpassen
ufo_text = pixel_font.render("UFO-Sichtung! Schafe rasten aus!", True, (100, 255, 100))

#? Sound beim Start des UFO-Events
ufo_sound = pygame.mixer.Sound("./media/game/images/events/ufo/ufo-landing.wav")
ufo_sound.set_volume(0.5)

#? Sound beim teleportieren der Tiere
teleport_sound = pygame.mixer.Sound("./media/game/images/events/ufo/teleport.wav")
teleport_sound.set_volume(0.5)




#^ --------------------------
#^  Die Uhr laden / über stalltiere
#^ --------------------------

clock_img = pygame.image.load("./media/game/images/clock.png").convert_alpha()
clock_img = pygame.transform.scale_by(clock_img, 0.045)

# Game over timer für den game over screen

game_over_timer = 0.0

#^ ------------------------------------------------------------
#^ Power‑Ups: Bilder & State
#^ ------------------------------------------------------------

powerup_images = {
    "speed": load_and_scale("./media/game/images/powerups/powerups-day/powerup-speed.png", 0.1),
    "magnet": load_and_scale("./media/game/images/powerups/powerups-day/powerup-magnet.png", 0.1),
    "score10": load_and_scale("./media/game/images/powerups/powerups-day/powerup-10.png", 0.1),
    "freeze": load_and_scale("./media/game/images/powerups/powerups-day/powerup-freeze.png", 0.1),
    "random": load_and_scale("./media/game/images/powerups/powerups-day/powerup-random.png", 0.1),
}

powerups = []                    # aktuell auf der Map liegende Power‑Ups
powerup_spawn_timer = 0.0        # zählt Sekunden bis zum nächsten Spawn
powerup_spawn_interval = 30.0    # mindestens 30 s Abstand
active_powerup = None            # aktuell wirkender Effekt
freeze_active = False            # Freeze aktiv check
powerup_effect_timer = 0.0       # Restdauer des aktiven Effekts
base_speed = player_speed        # merken, um Speed‑Buff zurückzusetzen
base_magnet_range = 50           # Standard‑Range fürs Aufsammeln
magnet_range = base_magnet_range # aktuelle Range

#^ ------------------------------------------------------------
#^ Zeit-Logik: Start 19:00 => (0:00) => ... => Zeit doppelt so schnell in Nacht
#^ ------------------------------------------------------------

game_minutes = 1200   # 19:00 = 19*60
time_accum = 0.0
day_night_fade_in = False
fade_alpha = 255
fade_duration = 1.0

# Bool, ob man schon im "Night-Modus" ist
night_mode = False
map_loaded = False
chosen_map_base = None
night_just_started = False

#^ ------------------------------------------------------------
#^ Glow effekt (Nachts unter Spieler und Tiere)
#^ ------------------------------------------------------------

def draw_glow(surface, x, y, tick, night_mode, sprite_width=50, sprite_height=50):
    if night_mode:
        radius = 35 + 5 * math.sin(tick / 10)
        glow_surface = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
        pygame.draw.circle(glow_surface, (255, 255, 100, 80), (radius, radius), int(radius))
        glow_x = x + sprite_width // 2 - radius
        glow_y = y + sprite_height // 2 - radius
        surface.blit(glow_surface, (glow_x, glow_y))

#^ ------------------------------------------------------------
#^ Stall
#^ ------------------------------------------------------------

stall_base = pygame.image.load("./media/game/images/stall.png").convert_alpha()
stall_scale = 0.3  # Ähnlich Wolf
w_stall, h_stall = stall_base.get_size()
stall_img = pygame.transform.scale(stall_base, (int(w_stall*stall_scale), int(h_stall*stall_scale)))
stall_rect = None
stall_placed = False

running = True #? Ab hier beginnt die Main game loop

#? ----------------------------------------------------------------------------------
#? Hauptloop
#? ----------------------------------------------------------------------------------

while running:
    dt = clock.tick(fps)
    dt_s = dt / 1000.0
    tick += 1
    #! Random Bellen des Hundes
    if random.random() < 0.002:  # Wahrscheinlichkeit pro Frame (~0.2%)
        dog_bark_sound.play()
    #! — Power‑Up‑Spawn —
    powerup_spawn_timer += dt_s
    if powerup_spawn_timer >= powerup_spawn_interval:
        powerup_spawn_timer = 0.0
        pu_type = random.choice(list(powerup_images.keys()))
        pu_x = random.randint(100, WIDTH - 100)
        pu_y = random.randint(100, HEIGHT - 100)
        powerups.append({
            "type": pu_type,
            "x": pu_x,
            "y": pu_y, #? 7 Sekunden Zeit zum einsammeln vom Powerups
            "timer": 7.0  #* [PUTIbearb]
        })
    #! - Snack Spawn -
    snack_spawn_timer += dt_s
    if snack is None and snack_spawn_timer >= snack_spawn_interval:
        snack_spawn_timer = 0.0
        snack = {
            "x": random.randint(100, WIDTH - 100),
            "y": random.randint(100, HEIGHT - 100),
            "type": "healthy",
            "timer": 15.0,
            "transformed": False
        }


    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        #? Gamestate = Menü
        if state == "menu":
            if event.type == pygame.MOUSEBUTTONDOWN:
                if sp_rect.collidepoint(event.pos): #^ Klick auf Spielen ->
                    button_click_sound.play() #& button sound
                    print("Klick auf Spielen -> Difficulty-Auswahl")
                    state = "choose_difficulty" #& gamestate wird geändert

                elif einst_rect.collidepoint(event.pos): #^ Klick auf Anleitung ->
                    button_click_sound.play()
                    print("Anleitung wird im Browser geöffnet ...")
                    webbrowser.open("https://lipsum.com")


                elif github_rect.collidepoint(event.pos): #^ Klick auf Github ->
                    button_click_sound.play()
                    webbrowser.open("https://github.com/mschr703/FarmCraze") #& Github Seite öffnet sich

                elif trello_rect.collidepoint(event.pos): #^ Klick auf Trello ->
                    button_click_sound.play()
                    webbrowser.open("https://trello.com/b/8PAAm2gj/farmcraze")  #& Trello Seite öffnet sich


                elif quit_rect.collidepoint(event.pos): #^ Klick auf Verlassen ->
                    button_click_sound.play() #& Button click regristriert
                    time.sleep(1.0)
                    pygame.quit()
                    sys.exit()

        #? Gamestate = Schwierigkeit auswählen
        elif state == "choose_difficulty":
            if event.type == pygame.MOUSEBUTTONDOWN:
                if leicht_rect.collidepoint(event.pos):
                    button_click_sound.play()
                    selected_difficulty = "Leicht"
                    print("Difficulty = LEICHT")
                    lives = 5
                    state = "game"
                    #& Variablen vorbereiten
                    fade_alpha = 255 #& reinfaden ins spiel
                    night_mode = False #& kein nightmode da day
                    map_surface = None
                    stall_placed = False

                elif mittel_rect.collidepoint(event.pos):
                    button_click_sound.play()
                    selected_difficulty = "Mittel"
                    print("Difficulty = MITTEL")
                    lives = 3
                    state = "game"
                    fade_alpha = 255
                    night_mode = False
                    map_surface = None
                    stall_placed = False

                elif schwer_rect.collidepoint(event.pos):
                    button_click_sound.play()
                    selected_difficulty = "Schwer"
                    print("Difficulty = SCHWER")
                    lives = 2
                    state = "game"
                    fade_alpha = 255
                    night_mode = False
                    map_surface = None
                    stall_placed = False

        # GAME
        elif state == "game":
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                state = "menu"
                # ----------------------------
                # Reset aller Game‑Variablen
                # ----------------------------
                # Map + Nacht/Tag
                map_loaded = False
                map_surface = None
                chosen_map_base = None
                night_mode = False
                fade_in = False

                # Tages‑ und Zeit‑Zähler
                current_day = 1
                game_minutes = 1140    # 19:00
                time_accum = 0.0

                # Stall + Schafe
                stall_placed = False
                sheep_list.clear()
                sheep_currently_following = None

                # Enemies (Wölfe)
                enemies.clear()
                night_just_started = False

                # Score und Popups
                score = 0
                score_popups.clear()
                game_over = False

                # Leben zurücksetzen je nach gewählter Schwierigkeit
                if selected_difficulty == "Leicht":
                    lives = 5
                elif selected_difficulty == "Mittel":
                    lives = 3
                else:
                    lives = 2

                game_minutes = 1140
                time_accum = 0.0
                night_mode = False
                map_loaded = False
                map_surface = None
                stall_placed = False
                # Sound stoppen
                pygame.mixer.music.stop()
                # zurück ins Menü
                state = "menu"
                continue

    #? ---------------------------------------------------------------------------------
    #? STATES - LOGIK
    #? ---------------------------------------------------------------------------------
    
    if state == "menu":
        # Hintergrund
        bg_frame_timer += dt #& Einzelne frames laden aufgrund kein pygame gif support
        if bg_frame_timer >= bg_frame_speed:
            bg_frame_index = (bg_frame_index + 1) % len(bg_frames)
            bg_frame_timer = 0

        if not music_started: #& wenn die musik nicht gestartet wurde...
            pygame.mixer.music.play(-1) #& Main menu musik starten
            vogel_sound.play(-1) #& vogelgezwitscher starten
            music_started = True 

        # Wolken
        for c in clouds:
            c["x"] += c["speed_x"]
            c["y_offset"] += c["speed_y"] * c["direction"]
            if abs(c["y_offset"]) > 10:
                c["direction"] *= -1
            if c["x"] > WIDTH + 100:
                c["x"] = -300

        # Menü Schaf
        menusheep_x += menusheep_speed
        if menusheep_x > WIDTH:
            menusheep_x = -128
        menusheep_animation_timer += dt
        if menusheep_animation_timer >= menusheep_frame_delay:
            menusheep_frame_index = (menusheep_frame_index + 1) % len(menusheep_frames)
            menusheep_animation_timer = 0

        current_menusheep = menusheep_frames[menusheep_frame_index]
        screen.blit(current_menusheep, (menusheep_x, menusheep_y))

        # Hund
        dog_x = menusheep_x + dog_x_offset
        dog_y = menusheep_y + dog_y_offset
        dog_animation_timer += dt
        if dog_animation_timer >= dog_frame_delay:
            dog_frame_index = (dog_frame_index + 1) % len(dog_frames)
            dog_animation_timer = 0

        # Ping-Pong
        sp_offset += dt * button_speed * sp_dir #& Ping pong wie zuvor (vor hauptloop) wird eingesetzt
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

        # Render - MENU
        screen.blit(bg_frames[bg_frame_index], (0, 0))
        for c in clouds:
            wolke_y = c["y_base"] + c["y_offset"]
            screen.blit(wolke, (c["x"], wolke_y))

        current_dog = dog_frames[dog_frame_index]
        screen.blit(current_dog, (dog_x, dog_y))

        current_sheep = menusheep_frames[menusheep_frame_index]
        screen.blit(current_sheep, (menusheep_x, menusheep_y))

        screen.blit(logo, logo_rect)

        #! Die ganzen Buttons blitten
        mouse_pos = pygame.mouse.get_pos() # Maus position

        if sp_rect.collidepoint(mouse_pos): #! Spielen
            screen.blit(btn_spielen_hover, sp_rect)
        else:
            screen.blit(btn_spielen, sp_rect)

        if einst_rect.collidepoint(mouse_pos): #! Anleitung
            screen.blit(btn_einstellungen_hover, einst_rect)
        else:
            screen.blit(btn_einstellungen, einst_rect)

        if quit_rect.collidepoint(mouse_pos): #! Quit
            screen.blit(btn_verlassen_hover, quit_rect)
        else:
            screen.blit(btn_verlassen, quit_rect)

        #! Social buttons blit

        if github_rect.collidepoint(mouse_pos): #! Github
            screen.blit(btn_github_hover, github_rect)
        else:
            screen.blit(btn_github, github_rect)

        if trello_rect.collidepoint(mouse_pos): #! Trello
            screen.blit(btn_trello_hover, trello_rect)
        else:
            screen.blit(btn_trello, trello_rect)


        # Highscore
        hs_surf = pixel_font.render(f"Highscore: {highscore}", True, WHITE)
        hs_rect = hs_surf.get_rect(topright=(WIDTH - 40, 20))
        screen.blit(hs_surf, hs_rect)

        # Coins nebeneinander
        coins_surf = pixel_font.render(str(coins), True, WHITE)
        coins_rect = coins_surf.get_rect(topright=(WIDTH - 40, hs_rect.bottom + 20))

        coin_x = coins_rect.left - coin_img.get_width() - 10  # etwas Abstand zur Zahl
        coin_y = coins_rect.top + (coins_surf.get_height() - coin_img.get_height()) // 2

        screen.blit(coin_img, (coin_x, coin_y))
        screen.blit(coins_surf, coins_rect)


        # Version & Changelog oben links
        ver_surf = pixel_font.render("Version 1.01", True, WHITE)
        ver_rect = ver_surf.get_rect(topleft=(20, 20))
        screen.blit(ver_surf, ver_rect)

        upd_surf = pixel_font.render("Updates: bugfixes", True, WHITE)
        upd_rect = upd_surf.get_rect(topleft=(20, ver_rect.bottom + 5))
        screen.blit(upd_surf, upd_rect)


    elif state == "choose_difficulty":
        bg_frame_timer += dt
        if bg_frame_timer >= bg_frame_speed:
            bg_frame_index = (bg_frame_index + 1) % len(bg_frames)
            bg_frame_timer = 0

        screen.blit(bg_frames[bg_frame_index], (0, 0))

        mouse_pos = pygame.mouse.get_pos()
        if leicht_rect.collidepoint(mouse_pos):
            screen.blit(btn_leicht_hover, leicht_rect)
        else:
            screen.blit(btn_leicht, leicht_rect)

        if mittel_rect.collidepoint(mouse_pos):
            screen.blit(btn_mittel_hover, mittel_rect)
        else:
            screen.blit(btn_mittel, mittel_rect)

        if schwer_rect.collidepoint(mouse_pos):
            screen.blit(btn_schwer_hover, schwer_rect)
        else:
            screen.blit(btn_schwer, schwer_rect)

    elif state == "settings":
        bg_frame_timer += dt
        if bg_frame_timer >= bg_frame_speed:
            bg_frame_index = (bg_frame_index + 1) % len(bg_frames)
            bg_frame_timer = 0

        screen.blit(bg_frames[bg_frame_index], (0, 0))

    elif state == "game":
        #& wenn map nicht geladen ist... / map aus ordner extrahieren
        if not map_loaded:
            # Tag-Map => 'mapX-day.png'
            chosen_map_full = random.choice(map_paths)  #& zb "./media/game/maps/map1/map1-day.png"
            #& Basis (z.b map1) wird gesplittet (ausgeschnitten) damit wir später einfacher die nachtversion kriegen können
            #! splitted = "./media/game/maps/map1/map1-day.png".split("-day") => ["./media/game/maps/map1/map1", ".png"] 
            #& somit muss ich da nur night einsetzen, für jetzt aber day (tagbeginn)
            splitted = chosen_map_full.split("-day") 
            if len(splitted) == 2:
                chosen_map_base = splitted[0]  # "./media/game/maps/map1/map1"
            else:
                chosen_map_base = chosen_map_full.replace(".png", "")  # fallback

            loaded_map = pygame.image.load(chosen_map_full).convert()
            map_surface = pygame.transform.scale(loaded_map, (WIDTH, HEIGHT))

            pygame.mixer.music.stop()
            pygame.mixer.music.load(day_music)
            pygame.mixer.music.play(-1)

            map_loaded = True
            print(f"Tag-Map '{chosen_map_full}' geladen (Basis: {chosen_map_base}).")

            # Zeit / Fade
            game_minutes = 1140
            time_accum = 0.0
            night_mode = False
            fade_in = True
            fade_alpha = 255
            stall_placed = False

        # Stall platzieren, falls noch nicht
        if not stall_placed:
            sheep_list.clear()  #^ Vorherige Schafe entfernen um duplikation zu vermeiden
            sheep_currently_following = None
            #^ Stall‑Rect holen und positionieren
            stall_rect = stall_img.get_rect()
            margin = 300
            stall_rect.centerx = random.randint(margin, WIDTH - margin)
            stall_rect.centery = random.randint(margin, HEIGHT - margin)

            #^ harte Block‑Zone: exakt die Fläche des Stalls
            #^ (Damit der Spieler nicht in den Stall reinlaufen kann)
            block_zone = stall_rect.copy()

            #^ Delivery Zone: Hier können die Schafe abgegeben werden
            #^ Etwas größer, damit der Stall einen nicht blockiert
            delivery_zone = stall_rect.inflate(80, 80) #* [DLVRYbearb]


            # sheep list
            sheep_spawn_margin = 100  # Abstand zum Bildschirmrand

            for i in range(3):
                while True:
                    # 1) Zufällige Position wählen
                    x = random.randint(sheep_spawn_margin, WIDTH - sheep_spawn_margin)
                    y = random.randint(sheep_spawn_margin, HEIGHT - sheep_spawn_margin)
                    sheep_rect = pygame.Rect(
                        x, y,
                        sheep_sprites["up"].get_width(),
                        sheep_sprites["up"].get_height()
                    )

                    # 2) Nicht im Stall spawnen
                    if stall_rect and sheep_rect.colliderect(block_zone):
                        continue

                    # 3) Nicht zu nahe an anderen Schafen
                    too_close = False
                    for other in sheep_list:
                        dist = math.hypot(other["x"] - x, other["y"] - y)
                        if dist < 60:
                            too_close = True
                            break
                    if too_close:
                        continue
                    
                    timer_start = get_default_timer(selected_difficulty)

                    # 5) Schaf mit initialem Timer hinzufügen
                    sheep_list.append({
                        "x": x,
                        "y": y,
                        "direction": "up",
                        "following": False,
                        "timer": {
                            "remaining": 10.0 if event_active else get_default_timer(selected_difficulty),
                            "active": False,
                            "last_tick_sound": 4
                        },
                    })
                    break

            stall_placed = True


        # 3) Fade-In
        if fade_in:
            fade_alpha -= int(255 * (dt_s / fade_duration))
            if fade_alpha <= 0:
                fade_alpha = 0
                fade_in = False

        # Wolf Movement (Diagonal)
        keys = pygame.key.get_pressed()
        dx, dy = 0, 0
        direction_for_render = "down"

        if keys[pygame.K_w] or keys[pygame.K_UP]:
            dy = -player_speed
            direction_for_render = "up"
        if keys[pygame.K_s] or keys[pygame.K_DOWN]:
            dy = player_speed
            direction_for_render = "down"
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            dx = -player_speed
            direction_for_render = "left"
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            dx = player_speed
            direction_for_render = "right"

        moving_now = dx != 0 or dy != 0 #! Laufsounds
        if moving_now and not is_walking:
            dog_walk_sound.play(-1)  # 🐾 leiser Loop
            is_walking = True
        elif not moving_now and is_walking:
            dog_walk_sound.stop()
            is_walking = False


        # aktuelles Bild holen, um Größe zu prüfen
        current_img = player_sprites[direction_for_render]

        # neue Position vorschauen & prüfen ob sie mit Stall kollidiert
        future_rect = pygame.Rect(player_x + dx, player_y + dy, current_img.get_width(), current_img.get_height())

        if not (stall_rect and future_rect.colliderect(block_zone)):
            player_x += dx
            player_y += dy
        
        # Spieler innerhalb der Map-Grenzen halten
        player_x = max(0, min(player_x, WIDTH  - current_img.get_width()))
        player_y = max(0, min(player_y, HEIGHT - current_img.get_height()))



        # Schaf verfolgt den Spieler (und bricht manchmal ab)
        for sheep in sheep_list:
            dx_s = player_x - sheep["x"]
            dy_s = player_y - sheep["y"]
            distance = math.hypot(dx_s, dy_s)

            # ---------------- Timer Initialisieren ----------------
            if "timer" not in sheep or type(sheep["timer"]) != dict:
                sheep["timer"] = {
                    "remaining": 10.0 if event_active else get_default_timer(selected_difficulty),
                    "active": False,
                    "last_tick_sound": 4
    }


            # ---------------- Timer Runterzählen ----------------
            if not sheep["following"]:
                if not freeze_active: #! Nötig aufgrund des Freeze powerups
                    sheep["timer"]["remaining"] -= dt_s

                # Ticks in den letzten 3 Sekunden
                if sheep["timer"]["remaining"] <= 3 and not sheep["timer"]["active"]:
                    clock_tick_sound.play()
                    sheep["timer"]["active"] = True  #! verhindert mehrfaches Abspielen


                # Zeit abgelaufen
                if sheep["timer"]["remaining"] <= 0:
                    sheep_list.remove(sheep)
                    loose_sound.play()
                    score_popups.append({
                        "x": sheep["x"] + 20,
                        "y": sheep["y"],
                        "alpha": 255,
                        "timer": {
                            "remaining": timer_start,
                            "active": False,
                            "last_tick_sound": 4
                        },

                        "text": "-1",
                        "color": (255, 50, 50)
                    })
                    score -= 1
                    lives -= 1

                    if lives <= 0:
                        game_over = True

                        # highscore bearbeiten
                        if score > highscore:
                            highscore = score
                            with open(HIGH_SCORE_FILE, "w") as f:
                                f.write(str(highscore))

                    # Score-Abzug rot anzeigen
                    score_popups.append({
                        "x": sheep["x"],
                        "y": sheep["y"],
                        "alpha": 255,
                        "timer": {
                            "remaining": timer_start,
                            "active": False,
                            "last_tick_sound": 4
                        },
                        "text": "-1",
                        "color": RED
                    })

                    # Respawn neues Schaf
                    while True:
                        new_x = random.randint(100, WIDTH - 100)
                        new_y = random.randint(100, HEIGHT - 100)
                        new_rect = pygame.Rect(
                            new_x, new_y,
                            sheep_sprites["up"].get_width(),
                            sheep_sprites["up"].get_height()
                        )

                        if new_rect.colliderect(block_zone):
                            continue

                        too_close = False
                        for other in sheep_list:
                            dist = math.hypot(other["x"] - new_x, other["y"] - new_y)
                            if dist < 60:
                                too_close = True
                                break
                        if too_close:
                            continue

                        timer_start = get_default_timer(selected_difficulty)


                        sheep_list.append({
                            "x": new_x,
                            "y": new_y,
                            "direction": "up",
                            "following": False,
                            "timer": {
                                "remaining": 10.0 if event_active else get_default_timer(selected_difficulty),
                                "active": False,
                                "last_tick_sound": 4
                            },
                        })
                        break

            # ---------------- Bewegung bei Verfolgung ----------------
            if not sheep["following"] and distance < magnet_range and sheep_currently_following is None:
                sheep["following"] = True
                sheep_currently_following = sheep
                pickup_sound.play()

            if sheep["following"] and selected_difficulty in ["Mittel", "Schwer"]:
                cancel_chance = 0.0005 if selected_difficulty == "Mittel" else 0.003 #* Verfolgungs-Abbruch Chance bei den Tieren [VABCTbearb]
                if random.random() < cancel_chance:
                    sheep["following"] = False
                    if sheep_currently_following == sheep:
                        sheep_currently_following = None
                    cancel_sound.play()
                    cancel_message_timer = 3.0
                    cancel_message_alpha = 0

            if sheep == sheep_currently_following and sheep["following"] and distance > 35:
                step = 3 # Schaf Verfolgungs-Speed Normal #* [SFVSnormal]
                if sheep.get("speed_boost", False):
                    step = 8  # Schaf Verfolgungs-Speed Event #* [SFVSevent]
                if abs(dx_s) > abs(dy_s):
                    sheep["direction"] = "left" if dx_s < 0 else "right"
                else:
                    sheep["direction"] = "up" if dy_s < 0 else "down"

                norm = max(1, distance)
                sheep["x"] += step * dx_s / norm
                sheep["y"] += step * dy_s / norm

            
        # Prüfen, ob Schaf im Stall ist
        if sheep_currently_following:
            dist_to_stall = math.hypot(
                sheep_currently_following["x"] - stall_rect.centerx,
                sheep_currently_following["y"] - stall_rect.centery
            )
            
            sheep_img = sheep_sprites[sheep_currently_following["direction"]]
            sheep_rect = pygame.Rect(
                sheep_currently_following["x"],
                sheep_currently_following["y"],
                sheep_img.get_width(),
                sheep_img.get_height()
            )

            if delivery_zone.colliderect(sheep_rect):
                # 1. Schaf despawnen
                sheep_list.remove(sheep_currently_following)

                # 2. Score erhöhen & speichern als münze
                score += 1
                coins += 1
                with open(COINS_FILE, "w") as f:
                    f.write(str(coins))

                # 3. Sound abspielen
                deliver_sound.play()
                # Und danach diesen +1 text zeigen
                score_popups.append({
                    "x": stall_rect.centerx,
                    "y": stall_rect.top,
                    "alpha": 255,
                    "timer": {
                        "remaining": timer_start,
                        "active": False,
                        "last_tick_sound": 4
                    },
                    "text": "+1",
                    "color": (255, 255, 100)  # Gelb wie vorher
                })



                # 4. Neues Schaf spawnen
                while True:
                    new_x = random.randint(100, WIDTH - 100)
                    new_y = random.randint(100, HEIGHT - 100)
                    new_rect = pygame.Rect(new_x, new_y, sheep_sprites["up"].get_width(), sheep_sprites["up"].get_height())
                    if not new_rect.colliderect(block_zone):
                        too_close = False
                        for other in sheep_list:
                            dist = math.hypot(other["x"] - new_x, other["y"] - new_y)
                            if dist < 60:
                                too_close = True
                                break
                        if not too_close:
                            timer_start = get_default_timer(selected_difficulty)

                            sheep_list.append({
                                "x": new_x,
                                "y": new_y,
                                "direction": "up",
                                "following": False,
                                "timer": {
                                    "remaining": 10.0 if event_active else get_default_timer(selected_difficulty),
                                    "active": False,
                                    "last_tick_sound": 4
                                },

                            })

                            break

                # 5. Reset Verfolgung
                sheep_currently_following = None

        # Zeit Tag->Nacht, ab 22:00 => night
        if not night_mode:
            if game_minutes < 1320:
                time_accum += dt_s
                if time_accum >= 1.0:
                    game_minutes += 1
                    time_accum -= 1.0
                if game_minutes >= 1320: #^ Wenn 22 Uhr -> Nacht startet
                    game_minutes = 1320
                    night_mode = True
                    time_accum = 0.0
                    stall_placed = False #^ Damit der Stall wieder neu platziert wird
            #! UFO EVENT!
            if not night_mode and not event_active and 1140 <= game_minutes < 1320 and random.random() < 0.0002: #* Ufo event Wahrscheinlichkeit [UFOWSKbearb]
                event_active = True
                event_type = "ufo"
                event_timer = event_duration
                player_speed = base_speed * 2
                ufo_sound.play()

                def teleport_sheep():
                    for sheep in sheep_list:
                        sheep["x"] = random.randint(100, WIDTH - 100)
                        sheep["y"] = random.randint(100, HEIGHT - 100)
                        sheep["speed_boost"] = True
                        sheep["timer"]["remaining"] = 10.0
                        sheep["timer"]["active"] = False
                    teleport_sound.play()

                teleport_sheep()  # sofort
                pygame.time.set_timer(pygame.USEREVENT + 1, 1000)
                pygame.time.set_timer(pygame.USEREVENT + 2, 2000)
                pygame.time.set_timer(pygame.USEREVENT + 3, 3000)

            if event_active:
                event_timer -= dt_s

                # Während des Events zufällig teleportieren (selten)
                if random.random() < 0.003:
                    teleport_sheep()

                if event_timer <= 0:
                    event_active = False
                    event_type = None
                    player_speed = base_speed
                    for sheep in sheep_list:
                        sheep["speed_boost"] = False
                        if not sheep["following"]:  # nur wenn Schaf gerade NICHT folgt
                            sheep["timer"]["remaining"] = get_default_timer(selected_difficulty)

                    #^ Nacht startet Text
                    score_popups.append({
                        "x": WIDTH // 2,
                        "y": HEIGHT // 2 - 150,
                        "alpha": 255,
                        "timer": {
                            "remaining": 3.0,
                            "active": False,
                            "last_tick_sound": 4
                        },
                        "text": "Die Nacht beginnt!",
                        "color": (180, 180, 180)  # Hellgrau
                    })

                    #^ Wechsle Map zur Night-Version
                    night_map = chosen_map_base + "-night.png"
                    if os.path.exists(night_map):
                        loaded_map = pygame.image.load(night_map).convert()
                        map_surface = pygame.transform.scale(loaded_map, (WIDTH, HEIGHT))
                        print(f"Nacht-Map '{night_map}' geladen.")
                    else:
                        print(f"Night-Map '{night_map}' nicht gefunden, bleibe bei Day-Map ...")

                    #^ Musik umschalten auf Nacht
                    pygame.mixer.music.stop()
                    if os.path.exists(night_music):
                        pygame.mixer.music.load(night_music)
                        pygame.mixer.music.play(-1)
                    else:
                        print(f"Night-Music '{night_music}' nicht gefunden, bleibe bei Day-Music ...")

                    fade_in = True
                    fade_alpha = 255

                    #^ markiere: Nacht hat gerade begonnen
                    night_just_started = True

                    #^ code snippet für den wolf spawn
                    if night_just_started:
                        enemies.clear()
                        for _ in range(4):
                            ex = random.randint(100, WIDTH-100)
                            ey = random.randint(100, HEIGHT-100)
                            # jede Enemy bekommt eine zufällige Start‑Richtung
                            direction = random.choice(["up","down","left","right"])
                            enemies.append({
                                "x": ex,
                                "y": ey,
                                "dir": direction,
                                "timer": 0.0  # um das Wechsel‑Intervall zu tracken
                            })

        else:
            #^ Nacht => Zeit doppelt so schnell
            time_accum += dt_s * 2
            if time_accum >= 1.0:
                game_minutes += 1
                time_accum -= 1.0

            if game_minutes >= 1530: #* Tagbeginn (zurzeit 1:30am) [TABbearb] 
                game_minutes = 1140  # Tag beginnt wieder um 19:00
                time_accum = 0.0
                night_mode = False
                current_day += 1  # Tag hochzählen
                fade_in = True
                fade_alpha = 255

                # Musik zurück zu Tag
                pygame.mixer.music.stop()
                if os.path.exists(day_music):
                    pygame.mixer.music.load(day_music)
                    pygame.mixer.music.play(-1)

                # Map zurück zu Day
                day_map = chosen_map_base + "-day.png"
                if os.path.exists(day_map):
                    loaded_map = pygame.image.load(day_map).convert()
                    map_surface = pygame.transform.scale(loaded_map, (WIDTH, HEIGHT))
                    print(f"Neuer Tag {current_day} begonnen – Map: '{day_map}'")

                # Wölfe verschwinden
                night_just_started = False
                enemies.clear()


        hour = (game_minutes // 60) % 24
        minute = game_minutes % 60
        time_text_str = f"Tag {current_day}: {hour:02d}:{minute:02d}"

        #? -------------------
        #? RENDER GAME 
        #? -------------------
        
        # — Power‑Up‑Timer & Sammel‑Logik —
        player_rect = pygame.Rect(player_x, player_y,
            player_sprites[direction_for_render].get_width(),
            player_sprites[direction_for_render].get_height())

        for pu in powerups[:]:
            pu["timer"] -= dt_s
            if pu["timer"] <= 0:
                powerups.remove(pu)
                continue

            pu_img = powerup_images[pu["type"]]
            pu_rect = pygame.Rect(pu["x"], pu["y"], pu_img.get_width(), pu_img.get_height())

            if pu_rect.colliderect(player_rect):
                powerup_sound.play()
                # Effekt anwenden

                #& Speed Powerup
                if pu["type"] == "speed":
                    player_speed = base_speed * 2 #* Speed bonus durch Powerup [SBPUbearb]
                    active_powerup = "speed"
                    powerup_effect_timer = 10.0
                    #& Text Popup für Speed
                    score_popups.append({
                        "x": player_x + 30,
                        "y": player_y - 20,
                        "alpha": 255,
                        "timer": {
                            "remaining": 2.0,
                            "active": False,
                            "last_tick_sound": 4
                        },
                        "text": "Schnelligkeit aufgesammelt!",
                        "color": (100, 255, 100)
                    })

                #& Magnet Powerup
                elif pu["type"] == "magnet":
                    magnet_range = base_magnet_range * 5 #* Pull / Magnet - Pullkraft HIER Bearbeiten [PKTbearb]
                    active_powerup = "magnet"
                    powerup_effect_timer = 10.0
                    #& Text Popup Magnet
                    score_popups.append({
                        "x": player_x + 30,
                        "y": player_y - 20,
                        "alpha": 255,
                        "timer": {
                            "remaining": 2.0,
                            "active": False,
                            "last_tick_sound": 4
                        },
                        "text": "Magnet aufgesammelt!",
                        "color": (100, 200, 255)
                    })
                
                #& +10 Powerup
                elif pu["type"] == "score10":
                    score += 10 #* Score Bonus durch den powerup HIER bearbeiten [SCBbearb]
                    #& Text Popup +10
                    score_popups.append({
                        "x": player_x + 30,
                        "y": player_y - 20,
                        "alpha": 255,
                        "timer": {
                            "remaining": 2.0,
                            "active": False,
                            "last_tick_sound": 4
                        },
                        "text": "+10!",
                        "color": (255, 255, 100)
                    })

                #& Freeze Powerup
                elif pu["type"] == "freeze":
                    active_powerup = "freeze"
                    powerup_effect_timer = 10.0 #* Timer für den Freeze Effekt Powerup [FPETbearb]
                    freeze_active = True

                    # Popup-Text
                    score_popups.append({
                        "x": player_x + 30,
                        "y": player_y - 20,
                        "alpha": 255,
                        "timer": {
                            "remaining": 2.0,
                            "active": False,
                            "last_tick_sound": 4
                        },
                        "text": "Zeit eingefroren!",
                        "color": (150, 255, 255)
                    })
                
                #& Zufalls-Powerup
                elif pu["type"] == "random":
                    # Auswahl aus allen außer "random" selbst
                    random_choice = random.choice(["speed", "magnet", "score10", "freeze"])
                    # Füge das gewählte Powerup zur Liste hinzu
                    powerups.append({
                        "type": random_choice,
                        "x": player_x,
                        "y": player_y,
                        "timer": 0.0  # sofortiger Pickup
                    })

                    # Popup anzeigen
                    score_popups.append({
                        "x": player_x + 30,
                        "y": player_y - 20,
                        "alpha": 255,
                        "timer": {
                            "remaining": 2.0,
                            "active": False,
                            "last_tick_sound": 4
                        },
                        "text": "Zufalls-Powerup!",
                        "color": (255, 255, 255)
                    })

                #& Powerup entfernen nach Zeit ablauf
                powerups.remove(pu)

        screen.blit(map_surface, (0, 0))

        #? Zeit Text zeichnen
        time_surf = pixel_font.render(time_text_str, True, WHITE)
        time_rect = time_surf.get_rect(midtop=(WIDTH // 2, 10))
        screen.blit(time_surf, time_rect)

        #? Score links oben
        score_text = f"Score: {score}"
        score_surf = pixel_font.render(score_text, True, WHITE)
        score_rect = score_surf.get_rect(topleft=(40, 20))
        screen.blit(score_surf, score_rect)

        #? Herzen oben rechts (Leben)
        heart_spacing = 10
        heart_y = 20
        for i in range(lives):
            heart_x = WIDTH - (heart_img.get_width() + heart_spacing) * (lives - i) - 40
            screen.blit(heart_img, (heart_x, heart_y))

        #? Coins direkt unter den Herzen
        coin_y = heart_y + heart_img.get_height() + 10
        coin_x = WIDTH - coin_img.get_width() - 40
        screen.blit(coin_img, (coin_x, coin_y))

        coins_surf = pixel_font.render(str(coins), True, WHITE)
        coins_rect = coins_surf.get_rect(
            midright=(coin_x - 10, coin_y + coin_img.get_height() // 2)
        )
        screen.blit(coins_surf, coins_rect)



        #* Score Popups zeichnen
        for popup in score_popups[:]:
            popup["y"] -= 30 * dt_s
            popup["alpha"] -= 255 * dt_s
            popup["timer"]["remaining"] -= dt_s

            if popup["timer"]["remaining"] <= 0:
                score_popups.remove(popup)
                continue

            popup_text = pixel_font.render(popup["text"], True, popup.get("color", (255, 255, 100)))
            popup_text.set_alpha(max(0, int(popup["alpha"])))
            rect = popup_text.get_rect(center=(popup["x"], popup["y"]))
            screen.blit(popup_text, rect)

        #? Wolf zeichnen
        draw_glow(screen, player_x, player_y, tick, night_mode, current_img.get_width(), current_img.get_height()) #? glow für den Wolf (Nachts)
        current_img = player_sprites[direction_for_render]
        screen.blit(current_img, (player_x, player_y))

        #? Mehrere Schafe Zeichnen + Uhr falls keine Verfolgung
        for sheep in sheep_list:
            sheep_img = sheep_sprites[sheep["direction"]]
            draw_glow(screen, sheep["x"], sheep["y"], tick, night_mode, sheep_img.get_width(), sheep_img.get_height())
            screen.blit(sheep_img, (sheep["x"], sheep["y"]))
            # Uhr anzeigen über wartenden Schafen
            if not sheep["following"]:
                screen.blit(clock_img, (sheep["x"], sheep["y"] - 40))
                seconds_left = max(0, int(sheep["timer"]["remaining"] + 1))
                time_text = pixel_font.render(f"{seconds_left}s", True, WHITE)
                screen.blit(time_text, (sheep["x"] + 40, sheep["y"] - 40))

        #! ─────────────────────────────────────────────────────────────────────
        #! wolf (gegner) spawn/zeichnen
        #! ─────────────────────────────────────────────────────────────
        for e in enemies:
            #! Timer damit sie die Richtung korrekt wechseln
            e["timer"] += dt_s
            if e["timer"] >= enemy_change_dir_interval:
                e["dir"] = random.choice(["up","down","left","right"])
                e["timer"] = 0.0

            #! Bewegung der Wölfe (Up/Down/Left/Right)
            if e["dir"] == "up":
                e["y"] -= enemy_speed
            elif e["dir"] == "down":
                e["y"] += enemy_speed
            elif e["dir"] == "left":
                e["x"] -= enemy_speed
            else:
                e["x"] += enemy_speed

            #! Out of bounds prüfen
            max_x = WIDTH - enemy_sprites["left"].get_width()
            max_y = HEIGHT - enemy_sprites["left"].get_height()
            e["x"] = max(0, min(e["x"], max_x))
            e["y"] = max(0, min(e["y"], max_y))

            #! Zeichnen
            sprite = enemy_sprites[e["dir"]]
            screen.blit(sprite, (e["x"], e["y"]))

            #! Collision mit Spieler prüfen
            enemy_rect = pygame.Rect(e["x"], e["y"],
                                    sprite.get_width(), sprite.get_height())
            player_rect = pygame.Rect(player_x, player_y,
                                    player_sprites[direction_for_render].get_width(),
                                    player_sprites[direction_for_render].get_height())
            if enemy_rect.colliderect(player_rect): #! Wolf berührt ->
                lives -= 1 #! Leben abziehen
                cancel_sound.play() ##! Sound abspielen

                #! "Berührten" Wolf entfernen (verhindert leben abzug spam)
                enemies.remove(e)

                #! Pop-Up Text bei Biss
                score_popups.append({
                    "x": player_x,
                    "y": player_y - 30,
                    "alpha": 255,
                    "timer": {
                        "remaining": 2.0,
                        "active": False,
                        "last_tick_sound": 4
                    },
                    "text": "Du wurdest gebissen!",
                    "color": (255, 50, 50)  # Rot
                })

                #! Neuen wolf an anderer position spawnen
                new_e = {
                    "x": random.randint(100, WIDTH-100),
                    "y": random.randint(100, HEIGHT-100),
                    "dir": random.choice(["up","down","left","right"]),
                    "timer": 0.0
                }
                enemies.append(new_e)

                #! Game Over prüfen
                if lives <= 0:
                    game_over = True
                    pygame.mixer.music.stop()

                # direkt zur nächsten Schlaufe
                continue
        # ─────────────────────────────────────────────────────────────


        # — Power‑Ups zeichnen —
        for pu in powerups[:]:
            img = powerup_images[pu["type"]]
            screen.blit(img, (pu["x"], pu["y"]))
            sec = max(0, int(pu["timer"] + 1))
            timer_surf = pixel_font.render(f"{sec}s", True, WHITE)
            screen.blit(timer_surf, (pu["x"] + img.get_width() + 5, pu["y"]))

        # — Power‑Up‑Effekt‑Timer —
        if active_powerup:
            powerup_effect_timer -= dt_s
            if powerup_effect_timer <= 0:
                if active_powerup == "speed":
                    player_speed = base_speed
                elif active_powerup == "magnet":
                    magnet_range = base_magnet_range
                elif active_powerup == "freeze":
                    freeze_active = False
                active_powerup = None

        # — Snack zeichnen und verarbeiten —
        if snack:
            snack["timer"] -= dt_s

            # Spieler in der Nähe => Chance auf Transformation
            if not snack["transformed"]:
                dist_x = abs(player_x - snack["x"])
                dist_y = abs(player_y - snack["y"])
                distance = math.hypot(player_x - snack["x"], player_y - snack["y"])
                if distance < 175 and not snack["transformed"]:  # größere Range
                    chance = snack_toxic_chances.get(selected_difficulty, 0.25)
                    if random.random() < chance:
                        snack["type"] = "toxic"
                    snack["transformed"] = True


            # Snack-Rect & Kollisionsprüfung
            snack_img = snack_images[snack["type"]]
            snack_rect = pygame.Rect(snack["x"], snack["y"], snack_img.get_width(), snack_img.get_height())

            if snack_rect.colliderect(player_rect):
                if snack["type"] == "healthy":
                    coins += 2
                    score += 1
                    dog_eat_sound.play() # sound fürs essen
                    score_popups.append({ # popup text -> "+2 Münzen"
                        "x": player_x + 30,
                        "y": player_y - 20,
                        "alpha": 255,
                        "timer": {
                            "remaining": 2.0,
                            "active": False,
                            "last_tick_sound": 4
                        },
                        "text": "+2 Coins +1 Score!",
                        "color": (255, 255, 100)
                    })
                else:
                    lives -= 1
                    cancel_sound.play()
                    score_popups.append({
                        "x": player_x,
                        "y": player_y - 30,
                        "alpha": 255,
                        "timer": {
                            "remaining": 2.0,
                            "active": False,
                            "last_tick_sound": 4
                        },
                        "text": "Ihh, vergiftet!",
                        "color": (255, 0, 0)
                    })
                    if lives <= 0:
                        game_over = True
                        pygame.mixer.music.stop()

                snack = None
                snack_spawn_timer = 0.0

            elif snack["timer"] <= 0:
                snack = None
                snack_spawn_timer = 0.0

            else:
                screen.blit(snack_img, (snack["x"], snack["y"]))


        # — Delivery‑Zone leicht highlighten —
        highlight_surf = pygame.Surface(
            (delivery_zone.width, delivery_zone.height),
            pygame.SRCALPHA
        )
        pygame.draw.rect(
            highlight_surf,
            (100, 255, 100, 60),       # halbtransparentes Hellgrün
            highlight_surf.get_rect(),
            width=4,
            border_radius=8
        )
        screen.blit(highlight_surf, (delivery_zone.x, delivery_zone.y))

        # Stall
        if stall_placed and stall_rect:
            screen.blit(stall_img, stall_rect)

        # Fade
        if fade_in:
            fade_surf = pygame.Surface((WIDTH, HEIGHT))
            fade_surf.fill((0, 0, 0))
            fade_surf.set_alpha(fade_alpha)
            screen.blit(fade_surf, (0, 0))

        # Nachricht anzeigen, wenn Schaf abgebrochen hat
        if cancel_message_timer > 0:
            cancel_message_timer -= dt_s
            cancel_message_alpha = min(255, cancel_message_alpha + 10)  # Fade-In

            text_surf = pixel_font.render("Das Schaf hat aufgegeben!", True, WHITE)
            text_surf.set_alpha(cancel_message_alpha)
            text_rect = text_surf.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 100))
            screen.blit(text_surf, text_rect)

        #? ------
        #? Event Blits
        #? ------

        #? Ufo Event
        if event_active and event_type == "ufo":
            screen.blit(ufo_img, (500, 40))  # weiter links
            screen.blit(ufo_text, (WIDTH // 2 - ufo_text.get_width() // 2 + 60, 55))


        #! -----------------------------------------
        #! Game Over Screen
        #! -----------------------------------------

        if game_over: #! Game Over!

            #? Dunkles Overlay
            dark_overlay = pygame.Surface((WIDTH, HEIGHT))
            dark_overlay.fill((0, 0, 0))
            dark_overlay.set_alpha(255)   # <- komplett schwarz
            screen.blit(dark_overlay, (0, 0))

            #? Text: Du hast verloren
            game_over_text = pixel_font.render("Du hast verloren...", True, RED)
            text_rect = game_over_text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
            screen.blit(game_over_text, text_rect)

            #? Hinweis Text: ESC drücken
            restart_text = pixel_font.render("Drücke ESC um neuzustarten", True, WHITE)
            restart_rect = restart_text.get_rect(center=(WIDTH // 2, text_rect.bottom + 40))
            screen.blit(restart_text, restart_rect)

            #? Timer für automatischen zurücksprung
            game_over_timer += dt_s
            if game_over_timer >= 5.0:
                #? zurück ins Menü & Timer zurücksetzen
                game_over_timer = 0.0

                # ----------------------------
                #? Reset aller Game‑Variablen
                # ----------------------------

                #? Map + Nacht/Tag
                map_loaded = False
                map_surface = None
                chosen_map_base = None
                night_mode = False
                fade_in = False

                #? Tages‑ und Zeit‑Zähler
                current_day = 1
                game_minutes = 1140    # 19:00
                time_accum = 0.0

                #? Stall + Schafe
                stall_placed = False
                sheep_list.clear()
                sheep_currently_following = None

                #? Enemies (Wölfe)
                enemies.clear()
                night_just_started = False

                #? Score und Popups
                score = 0
                score_popups.clear()
                game_over = False

                #? Leben zurücksetzen je nach gewählter Schwierigkeit
                if selected_difficulty == "Leicht":
                    lives = 5
                elif selected_difficulty == "Mittel":
                    lives = 3
                else:
                    lives = 2

                game_minutes = 1140
                time_accum = 0.0
                night_mode = False
                map_loaded = False
                map_surface = None
                stall_placed = False
                #? Sound stoppen
                pygame.mixer.music.stop()
                state = "menu"



    pygame.display.flip()

pygame.quit()

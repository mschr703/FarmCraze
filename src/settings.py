# settings.py
# Zentrale Konfigurationsdatei für alle Spielkonstanten.

# --------------------
# FENSTER & ANZEIGE
# --------------------
# Dies ist die interne Auflösung des Spiels. Alle Positionen und Bewegungen
# basieren auf diesen Werten. Das Spiel wird dann auf die tatsächliche
# Bildschirmgröße des Spielers skaliert.
VIRTUAL_WIDTH = 1920
VIRTUAL_HEIGHT = 1080
FPS = 60
TITLE = "FarmCraze"

# --------------------
# FARBEN
# --------------------
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
DARK_GRAY = (50, 50, 50)
HOVER_COLOR = (100, 100, 100)
TIMER_COLOR = (255, 255, 100)
POPUP_PLUS_ONE_COLOR = (255, 255, 100)
POPUP_MINUS_ONE_COLOR = (255, 50, 50)

# --------------------
# DATEIPFADE
# --------------------
# Fonts
FONT_BYTEBOUNCE = "./media/fonts/ByteBounce.ttf"
# Hauptmenü
ICON_PATH = "./media/main-menu/logo/icon.png"
BG_FRAMES_PATH = "./media/main-menu/background/frames"
LOGO_PATH = "./media/main-menu/logo/logo-transparent.png"
MENU_SHEEP_IDLE_PATH = "./media/main-menu/background/schaf/sheep-idle.png"
MENU_SHEEP_WALK_PATH = "./media/main-menu/background/schaf/sheep-walk.png"
MENU_DOG_IDLE_PATH = "./media/main-menu/background/hund/dog-idling.png"
MENU_DOG_WALK_PATH = "./media/main-menu/background/hund/dog-walking.png"
MENU_CLOUD_PATH = "./media/main-menu/background/wolke.png"
# Sounds
MENU_MUSIC_PATH = "./media/main-menu/sound/music/main-menu-music.wav"
BIRD_SOUND_PATH = "./media/main-menu/sound/music/vogelgezwitscher.wav"
BUTTON_CLICK_SOUND_PATH = "./media/main-menu/sound/button-sounds/button-click.wav"
# Spiel-Sounds
CANCEL_SOUND_PATH = "./media/game/sounds/effects/sonstiges/cancel.wav"
PICKUP_SOUND_PATH = "./media/game/sounds/effects/sonstiges/pickup.wav"
DELIVER_SOUND_PATH = "./media/game/sounds/effects/sonstiges/deliver.wav"
CLOCK_TICK_SOUND_PATH = "./media/game/sounds/effects/sonstiges/clock.wav"
LOSE_SOUND_PATH = "./media/game/sounds/effects/sonstiges/loose.wav"
POWERUP_SOUND_PATH = "./media/game/sounds/effects/sonstiges/powerup.wav"
DOG_EAT_SOUND_PATH = "./media/game/sounds/effects/animals/dog-eating.wav"
DOG_WALK_SOUND_PATH = "./media/game/sounds/effects/animals/dog-walking.wav"
DOG_BARK_SOUND_PATH = "./media/game/sounds/effects/animals/dog-barking.wav"
DAY_MUSIC_PATH = "./media/game/sounds/music/song1-day.wav"
NIGHT_MUSIC_PATH = "./media/game/sounds/music/song1-night.wav"
# Spiel-Grafiken
STALL_PATH = "./media/game/images/stall.png"
COIN_HUD_PATH = "./media/game/hud/coin.png"
HEART_HUD_PATH = "./media/game/hud/heart.png"
CLOCK_HUD_PATH = "./media/game/images/clock.png"

# --------------------
# SPIELER-EINSTELLUNGEN
# --------------------
PLAYER_START_SPEED = 5
PLAYER_SCALE = 0.1
PLAYER_GLIDE_FRICTION = 0.92  # [GWSTEbearb] Stärke des Gleitens/Rutschen beim Sturm Event

# --------------------
# TIER-EINSTELLUNGEN
# --------------------
# Schafe
SHEEP_SCALE = 0.1
SHEEP_SPAWN_COUNT = 3
SHEEP_FOLLOW_SPEED_NORMAL = 3  # [SFVSnormal]
SHEEP_FOLLOW_SPEED_EVENT = 8   # [SFVSevent]
# Schaf-Timer je Schwierigkeit [SAT1bearb]
SHEEP_TIMER = {
    "Leicht": 36.0,
    "Mittel": 29.0,
    "Schwer": 24.0
}
# Abbruch-Chance der Verfolgung [VABCTbearb]
SHEEP_CANCEL_CHANCE = {
    "Leicht": 0.0,
    "Mittel": 0.0005,
    "Schwer": 0.003
}
# Gegner (Wölfe)
ENEMY_SCALE = 0.1
ENEMY_SPEED = 2
ENEMY_SPAWN_COUNT = 4
ENEMY_CHANGE_DIR_INTERVAL = 2.0  # Sekunden

# --------------------
# SPIELMECHANIKEN
# --------------------
# Leben je Schwierigkeit
LIVES_PER_DIFFICULTY = {
    "Leicht": 5,
    "Mittel": 3,
    "Schwer": 2
}
# Stall
STALL_SCALE = 0.3
STALL_MARGIN = 300  # Mindestabstand zum Rand
DELIVERY_ZONE_INFLATE = (80, 80)  # [DLVRYbearb] Lieferzone um den Stall

# Zeit
GAME_START_MINUTES = 1140  # 19:00 Uhr
NIGHT_START_MINUTES = 1320 # 22:00 Uhr
DAY_START_MINUTES = 1530   # 01:30 Uhr [TABbearb]

# --------------------
# ITEMS & POWER-UPS
# --------------------
# Power-ups
POWERUP_SPAWN_INTERVAL = 30.0
POWERUP_DESPAWN_TIME = 7.0  # [PUTIbearb]
POWERUP_EFFECT_DURATION = 10.0
POWERUP_SPEED_BONUS_MULTIPLIER = 2  # [SBPUbearb]
POWERUP_MAGNET_RANGE_MULTIPLIER = 5 # [PKTbearb]
POWERUP_SCORE_BONUS = 10            # [SCBbearb]
POWERUP_FREEZE_DURATION = 10.0      # [FPETbearb]
BASE_MAGNET_RANGE = 50

# Snacks
SNACK_SPAWN_INTERVAL = 30.0  # [SNPIbearb]
SNACK_DESPAWN_TIME = 15.0
SNACK_TRANSFORM_DISTANCE = 175
# Wahrscheinlichkeit für toxische Snacks [SNCKprob]
SNACK_TOXIC_CHANCES = {
    "Leicht": 0.20,
    "Mittel": 0.35,
    "Schwer": 0.55
}

# --------------------
# EVENTS
# --------------------
UFO_SPAWN_CHANCE = 0.0002 # [UFOWSKbearb]
STORM_SPAWN_CHANCE = 0.0002
EVENT_DURATION = 15.0
PRE_EVENT_DURATION = 3.0

# --------------------
# UI & MENÜ
# --------------------
# Hauptmenü-Buttons
MENU_BUTTON_SIZE = (290, 100)
MENU_BUTTON_SPACING = 110
MENU_BUTTON_START_Y = 395
# Social-Buttons
SOCIAL_BUTTON_SIZE = (70, 70)
# Schwierigkeits-Buttons
DIFF_BUTTON_SIZE = (300, 130)
DIFF_BUTTON_SPACING = 150
DIFF_BUTTON_START_Y = 395
# Ping-Pong-Animation [PPA]
BUTTON_ANIM_SPEED = 0.01
BUTTON_ANIM_AMPLITUDE = 2

# URLs
GITHUB_URL = "https://github.com/mschr703/FarmCraze"
TRELLO_URL = "https://trello.com/b/8PAAm2gj/farmcraze"
ANLEITUNG_URL = "https://lipsum.com" # Platzhalter
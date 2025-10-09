import pygame
import os
from . import settings

#* Diese Datei ist zuständig für die Assets im Spiel

class Assets: #! Eine Klasse für die Farmcraze Spiel assets
    def __init__(self):
        #? Fonts
        self.pixel_font_big = self._load_font(settings.FONT_BYTEBOUNCE, 48)
        self.pixel_font_small = self._load_font(settings.FONT_BYTEBOUNCE, 28)

        #? Sounds
        self.sounds = self._load_sounds()
        self._set_sound_volumes()

        #? Bilder
        self.images = self._load_images()

    def _load_font(self, path, size): #! Font-download mit fallback
        try:
            return pygame.font.Font(path, size)
        except pygame.error:
            print(f"WARNUNG: Schriftart '{path}' nicht gefunden. Nutze Fallback.")
            return pygame.font.SysFont("couriernew", size, bold=True)

    def _load_sounds(self): #! Lädt die sound dateien in ein dict
        return {
            "menu_music": settings.MENU_MUSIC_PATH,
            "day_music": settings.DAY_MUSIC_PATH,
            "night_music": settings.NIGHT_MUSIC_PATH,
            "vogel": self._load_sound(settings.BIRD_SOUND_PATH),
            "click": self._load_sound(settings.BUTTON_CLICK_SOUND_PATH),
            "cancel": self._load_sound(settings.CANCEL_SOUND_PATH),
            "pickup": self._load_sound(settings.PICKUP_SOUND_PATH),
            "deliver": self._load_sound(settings.DELIVER_SOUND_PATH),
            "clock_tick": self._load_sound(settings.CLOCK_TICK_SOUND_PATH),
            "loose": self._load_sound(settings.LOSE_SOUND_PATH),
            "powerup": self._load_sound(settings.POWERUP_SOUND_PATH),
            "dog_eat": self._load_sound(settings.DOG_EAT_SOUND_PATH),
            "dog_walk": self._load_sound(settings.DOG_WALK_SOUND_PATH),
            "dog_bark": self._load_sound(settings.DOG_BARK_SOUND_PATH),
            "ufo_start": self._load_sound("./media/game/images/events/ufo/ufo-landing.wav"),
            "teleport": self._load_sound("./media/game/images/events/ufo/teleport.wav"),
            "regen": self._load_sound("./media/game/images/events/regen/regen.wav"),
        }

    def _load_sound(self, path): #! Lädt eine einzelnde sound datei
        try:
            return pygame.mixer.Sound(path)
        except pygame.error:
            print(f"WARNUNG: Sound '{path}' konnte nicht geladen werden.")
            return None #? Gibt None zurück, um crashes zu vermeiden

    def _set_sound_volumes(self): #! Lautstärkeregler für sound dateien
        if self.sounds["vogel"]: self.sounds["vogel"].set_volume(0.4)
        if self.sounds["click"]: self.sounds["click"].set_volume(0.5)
        if self.sounds["cancel"]: self.sounds["cancel"].set_volume(0.6)
        if self.sounds["pickup"]: self.sounds["pickup"].set_volume(0.4)
        if self.sounds["deliver"]: self.sounds["deliver"].set_volume(0.5)
        if self.sounds["powerup"]: self.sounds["powerup"].set_volume(0.5)
        if self.sounds["dog_eat"]: self.sounds["dog_eat"].set_volume(0.5)
        if self.sounds["dog_walk"]: self.sounds["dog_walk"].set_volume(0.4)
        if self.sounds["dog_bark"]: self.sounds["dog_bark"].set_volume(0.6)
        if self.sounds["ufo_start"]: self.sounds["ufo_start"].set_volume(0.5)
        if self.sounds["teleport"]: self.sounds["teleport"].set_volume(0.5)
        if self.sounds["regen"]: self.sounds["regen"].set_volume(0.3)

    def _load_images(self): #! Lädt ein dict für die images
        images = {
            "icon": self._load_image(settings.ICON_PATH),
            "logo": self._load_image(settings.LOGO_PATH, scale_by=0.4),
            "bg_frames": self._load_animation_frames(settings.BG_FRAMES_PATH),
            "menu_sheep": self._load_image_list([settings.MENU_SHEEP_IDLE_PATH, settings.MENU_SHEEP_WALK_PATH], scale_by=0.2),
            "menu_dog": self._load_image_list([settings.MENU_DOG_IDLE_PATH, settings.MENU_DOG_WALK_PATH], scale_by=0.2),
            "cloud": self._load_image(settings.MENU_CLOUD_PATH, scale_by=0.3),
            "stall": self._load_image(settings.STALL_PATH, scale_by=settings.STALL_SCALE),
            "coin_hud": pygame.transform.scale(self._load_image(settings.COIN_HUD_PATH), (32, 32)),
            "heart_hud": pygame.transform.scale(self._load_image(settings.HEART_HUD_PATH), (32, 32)),
            "clock_hud": self._load_image(settings.CLOCK_HUD_PATH, scale_by=0.045),
            "ufo": self._load_image("./media/game/images/events/ufo/ufo.png", scale_by=0.1),
            "storm_cloud": self._load_image("./media/game/images/events/regen/regenwolke.png", scale_by=0.3),
        }

        #* Manuelles Laden der Spieler-Sprites, um die deutschen Dateinamen
        #* den englischen Logik-Namen zuzuordnen.
        images["player"] = {
            "up": self._load_image("./media/game/sprites/player/oben.png", scale_by=settings.PLAYER_SCALE),
            "down": self._load_image("./media/game/sprites/player/unten.png", scale_by=settings.PLAYER_SCALE),
            "left": self._load_image("./media/game/sprites/player/links.png", scale_by=settings.PLAYER_SCALE),
            "right": self._load_image("./media/game/sprites/player/rechts.png", scale_by=settings.PLAYER_SCALE)
        }
        
        #* gleicher grund wie oben ^ für die schaf sprites
        images["sheep"] = {
            "up": self._load_image("./media/game/sprites/sheep/oben.png", scale_by=settings.SHEEP_SCALE),
            "down": self._load_image("./media/game/sprites/sheep/unten.png", scale_by=settings.SHEEP_SCALE),
            "left": self._load_image("./media/game/sprites/sheep/links.png", scale_by=settings.SHEEP_SCALE),
            "right": self._load_image("./media/game/sprites/sheep/rechts.png", scale_by=settings.SHEEP_SCALE)
        }

        images["enemy"] = self._load_sprite_sheet("./media/game/sprites/enemy/", {"left": "wolf-left.png", "right": "wolf-right.png"}, settings.ENEMY_SCALE)
        
        #* Boost-Effekt Grafiken
        images["boost_effects"] = {
            "up": self._load_image("./media/game/sprites/effects/boost/up.png", scale_by=settings.PLAYER_SCALE * 1.5),
            "down": self._load_image("./media/game/sprites/effects/boost/down.png", scale_by=settings.PLAYER_SCALE * 1.5),
            "left": self._load_image("./media/game/sprites/effects/boost/left.png", scale_by=settings.PLAYER_SCALE * 1.5),
            "right": self._load_image("./media/game/sprites/effects/boost/right.png", scale_by=settings.PLAYER_SCALE * 1.5),
        }

        #* Power-ups und Snacks
        images["powerups"] = self._load_sprite_sheet("./media/game/images/powerups/powerups-day/", {
            "speed": "powerup-speed.png", "magnet": "powerup-magnet.png", "score10": "powerup-10.png",
            "freeze": "powerup-freeze.png", "random": "powerup-random.png"
        }, 0.1)
        images["snacks"] = {
            "healthy": pygame.transform.scale(self._load_image("./media/game/images/snacks/Snack-healthy.png"), (64, 64)),
            "toxic": pygame.transform.scale(self._load_image("./media/game/images/snacks/Snack-toxic.png"), (64, 64)),
        }
        return images

    def _load_image(self, path, scale_by=None): #! Lädt ein einzelnes bild
        try:
            img = pygame.image.load(path).convert_alpha()
            if scale_by:
                new_size = (int(img.get_width() * scale_by), int(img.get_height() * scale_by))
                img = pygame.transform.scale(img, new_size)
            return img
        except pygame.error as e:
            print(f"FEHLER: Bild '{path}' konnte nicht geladen werden. Fehler: {e}")
            #* Programm beenden, wenn kritische bilder vorhanden sind
            pygame.quit()
            raise SystemExit()


    def _load_image_list(self, paths, scale_by=None): #! Lädt eine liste von Bildern
        return [self._load_image(path, scale_by) for path in paths]

    def _load_animation_frames(self, folder_path): #! animations-frames
        frames = []
        if not os.path.exists(folder_path):
            print(f"WARNUNG: Animations-Ordner '{folder_path}' nicht gefunden.")
            return [pygame.Surface((settings.VIRTUAL_WIDTH, settings.VIRTUAL_HEIGHT))]

        for filename in sorted(os.listdir(folder_path)):
            if filename.endswith(".png"):
                img_path = os.path.join(folder_path, filename)
                img = self._load_image(img_path)
                img = pygame.transform.scale(img, (settings.VIRTUAL_WIDTH, settings.VIRTUAL_HEIGHT))
                frames.append(img)
        return frames

    def _load_sprite_sheet(self, folder, names, scale): #! Lädt entity sprites
        sprites = {}
        if isinstance(names, list): # Einfache Liste von Namen
            for name in names:
                path = os.path.join(folder, f"{name}.png")
                sprites[name] = self._load_image(path, scale_by=scale)
        elif isinstance(names, dict): # Dictionary von Name zu Dateiname
             for name, filename in names.items():
                path = os.path.join(folder, filename)
                sprites[name] = self._load_image(path, scale_by=scale)
        return sprites

    def load_map(self, map_base_path, is_night): #! Lädt maps (day/night)
        suffix = "-night.png" if is_night else "-day.png"
        map_path = map_base_path + suffix
        if os.path.exists(map_path):
            print(f"Lade Karte: '{map_path}'")
            loaded_map = pygame.image.load(map_path).convert()
            return pygame.transform.scale(loaded_map, (settings.VIRTUAL_WIDTH, settings.VIRTUAL_HEIGHT))
        else:
            print(f"WARNUNG: Karte '{map_path}' nicht gefunden. Nutze Fallback.") #! falls fehler mit map loading
            #! FALLBACK AUF NACHT KARTE
            if is_night:
                return self.load_map(map_base_path, False)
            return pygame.Surface((settings.VIRTUAL_WIDTH, settings.VIRTUAL_HEIGHT))
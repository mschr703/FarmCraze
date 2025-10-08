import pygame
import random
from . import settings

#* Diese Datei ist zuständig für die Events. (z.b ufo/sturm und weitere)
#? (rtspeed) -> Regentropfen speed

class EventManager: #! verwaltet die zufälligen event spawns
    def __init__(self, game_instance):
        self.game = game_instance
        self.assets = game_instance.assets
        
        self.is_active = False
        self.pre_event_active = False
        self.active_event_type = None
        
        self.event_timer = 0.0
        self.pre_event_timer = 0.0
        
        self.raindrops = []
        self.is_storm_overlay_active = False
        
        self.event_descriptions = {
            "ufo": [
                "- Die Aliens teleportieren deine Schafe!",
                "- Du erhältst einen Geschwindigkeits-Bonus.",
                "- Sammle sie schnell ein!"
            ],
            "storm": [
                "- Ein Sturm zieht auf!",
                "- Deine Steuerung wird rutschig.",
                "- Halte dich von den Wölfen fern!"
            ]
        }

    def update(self, dt): #! Aktualisiert die zufälligen events
        if self.is_active:
            self.event_timer -= dt
            if self.event_timer <= 0:
                self._end_event()
            else:
                self._run_active_event_logic()
        
        elif self.pre_event_active:
            self.pre_event_timer -= dt
            if self.pre_event_timer <= 0:
                self._start_event()
        
        #! Prüft ob ein neues Event gestartet werden soll
        elif not self.game.night_mode:
            self._check_for_new_event()
            
        if self.is_storm_overlay_active:
            self._update_raindrops()

    def _check_for_new_event(self): #! Prüft ob event gestartet werden soll
        if random.random() < settings.UFO_SPAWN_CHANCE:
            self._prepare_event("ufo")
        elif random.random() < settings.STORM_SPAWN_CHANCE:
            self._prepare_event("storm")

    def _prepare_event(self, event_type): #! Startet den event countdown
        self.pre_event_active = True
        self.active_event_type = event_type
        self.pre_event_timer = settings.PRE_EVENT_DURATION

    def _start_event(self): #! Aktiviert das event + effekte
        self.pre_event_active = False
        self.is_active = True
        self.event_timer = settings.EVENT_DURATION
        
        if self.active_event_type == "ufo":
            self._start_ufo_event()
        elif self.active_event_type == "storm":
            self._start_storm_event()

    def _end_event(self): #! Beendet das event + effekte
        if self.active_event_type == "ufo":
            self._end_ufo_event()
        elif self.active_event_type == "storm":
            self._end_storm_event()
            
        self.is_active = False
        self.active_event_type = None

    def _start_ufo_event(self): #! Startet das ufo event
        if self.assets.sounds["ufo_start"]:
            self.assets.sounds["ufo_start"].play()
        self.game.player.speed *= settings.POWERUP_SPEED_BONUS_MULTIPLIER
        
        for sheep in self.game.sheep_group:
            self._teleport_sheep(sheep)
            sheep.speed_boost = True

    def _teleport_sheep(self, sheep): #! Teleportiert schafe zufällig (ufo)
        sheep.rect.x = random.randint(100, settings.VIRTUAL_WIDTH - 100)
        sheep.rect.y = random.randint(100, settings.VIRTUAL_HEIGHT - 100)
        sheep.timer_remaining = 10.0
        if self.assets.sounds["teleport"]:
            self.assets.sounds["teleport"].play()

    def _end_ufo_event(self): #! Beendet das ufo event
        self.game.player.reset_speed()
        for sheep in self.game.sheep_group:
            sheep.speed_boost = False
            if not sheep.following:
                sheep.timer_remaining = settings.SHEEP_TIMER.get(self.game.difficulty, 30.0)

    def _start_storm_event(self): #! Startet das Sturm event
        pygame.mixer.music.fadeout(1000)
        if self.assets.sounds["regen"]:
            self.assets.sounds["regen"].play(-1)
        self.game.player.is_slippery = True
        self.is_storm_overlay_active = True
        if not self.raindrops:
            self._init_raindrops()

    def _end_storm_event(self): #! Beendet das sturm event
        if self.assets.sounds["regen"]:
            self.assets.sounds["regen"].stop()
        self.game.player.is_slippery = False
        self.is_storm_overlay_active = False
        self.game.play_music()

    def _run_active_event_logic(self): #! Logik für das aktive event
        if self.active_event_type == "ufo" and random.random() < 0.003:
            if self.game.sheep_group:
                self._teleport_sheep(random.choice(self.game.sheep_group.sprites()))
                
    def draw(self, surface): #! Handled die visuellen parts des events
        if self.pre_event_active:
            self._draw_pre_event_text(surface)
        elif self.is_active:
            self._draw_active_event_ui(surface)
            
        if self.is_storm_overlay_active:
            self._draw_storm_overlay(surface)

    def _draw_pre_event_text(self, surface): #! Zeichnet event text
        text = self.assets.pixel_font_big.render("Ein Event braut sich zusammen...", True, settings.DARK_GRAY)
        text = pygame.transform.rotate(text, random.uniform(-0.5, 0.5))
        rect = text.get_rect(center=(settings.VIRTUAL_WIDTH // 2, 150))
        surface.blit(text, rect)

    def _draw_active_event_ui(self, surface): #! Zeichnet titel + beschreibung des events
        if self.active_event_type == "ufo":
            title_text = "UFO Sichtung! Die Schafe rasten aus!"
            title_color = (100, 255, 100)
            surface.blit(self.assets.images["ufo"], (500, 40))
        elif self.active_event_type == "storm":
            title_text = "Es stürmt!"
            title_color = (100, 200, 255)
            
        title_surf = self.assets.pixel_font_big.render(title_text, True, title_color)
        title_surf = pygame.transform.rotate(title_surf, random.uniform(-0.7, 0.7))
        title_rect = title_surf.get_rect(center=(settings.VIRTUAL_WIDTH // 2, 150))
        surface.blit(title_surf, title_rect)

        # Beschreibung
        description_lines = self.event_descriptions.get(self.active_event_type, [])
        for i, line in enumerate(description_lines):
            desc_surf = self.assets.pixel_font_small.render(line, True, (180, 180, 180))
            desc_rect = desc_surf.get_rect(center=(settings.VIRTUAL_WIDTH // 2, 200 + i * 35))
            surface.blit(desc_surf, desc_rect)
            
    def _init_raindrops(self): #! Initialisiert die regentropfen (sturm event)
        self.raindrops = [{
            "x": random.randint(0, settings.VIRTUAL_WIDTH),
            "y": random.randint(0, settings.VIRTUAL_HEIGHT),
            "speed": random.uniform(2.0, 5.0)
        } for _ in range(100)]

    def _update_raindrops(self): #! bewegt die regentropfen
        for drop in self.raindrops:
            drop["y"] += drop["speed"] * 5 #? Geschwindigkeit anpassen (rtspeed)
            if drop["y"] > settings.VIRTUAL_HEIGHT:
                drop["y"] = 0
                drop["x"] = random.randint(0, settings.VIRTUAL_WIDTH)

    def _draw_storm_overlay(self, surface): #! Zeichnet regen + tropfen
        # Regen
        for drop in self.raindrops:
            pygame.draw.line(surface, (180, 180, 255), (drop["x"], drop["y"]), (drop["x"], drop["y"] + 5), 1)
        
        # Graues Overlay
        gray_overlay = pygame.Surface((settings.VIRTUAL_WIDTH, settings.VIRTUAL_HEIGHT), pygame.SRCALPHA)
        gray_overlay.fill((80, 80, 80, 120))
        surface.blit(gray_overlay, (0, 0))

        # Wolken
        storm_cloud_img = self.assets.images["storm_cloud"]
        surface.blit(storm_cloud_img, (80, 40))
        surface.blit(storm_cloud_img, (settings.VIRTUAL_WIDTH - storm_cloud_img.get_width() - 80, 40))
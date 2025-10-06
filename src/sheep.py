import pygame
import math
from . import settings # <-- Anpassung hier

class Sheep(pygame.sprite.Sprite):
    """
    Repräsentiert ein einzelnes Schaf im Spiel.
    Verwaltet seinen Zustand, Timer und seine Bewegung.
    """
    def __init__(self, x, y, assets, difficulty, is_ufo_active=False):
        super().__init__()
        self.assets = assets
        self.images = self.assets.images["sheep"]
        self.direction = "down"
        self.image = self.images[self.direction]
        self.rect = self.image.get_rect(topleft=(x, y))

        self.difficulty = difficulty
        self.following = False
        self.speed_boost = is_ufo_active

        # Timer-Setup
        self.timer_active = False
        if is_ufo_active:
            self.timer_remaining = 10.0
        else:
            self.timer_remaining = settings.SHEEP_TIMER.get(self.difficulty, 30.0)
        
        self.last_tick_sound_time = 4

    def update(self, dt, player_rect, freeze_active):
        """Aktualisiert den Zustand des Schafs."""
        if not self.following and not freeze_active:
            self.timer_remaining -= dt
            
            # Sound für die letzten 3 Sekunden abspielen
            if self.timer_remaining <= 3 and not self.timer_active:
                if self.assets.sounds["clock_tick"]:
                    self.assets.sounds["clock_tick"].play()
                self.timer_active = True

        # Wenn das Schaf dem Spieler folgt
        if self.following:
            self.move_towards(player_rect.center)
    
    def move_towards(self, target_pos):
        """Bewegt das Schaf in Richtung eines Ziels (Spieler)."""
        dx = target_pos[0] - self.rect.centerx
        dy = target_pos[1] - self.rect.centery
        distance = math.hypot(dx, dy)
        
        # Richtung für den Sprite festlegen
        if abs(dx) > abs(dy):
            self.direction = "right" if dx > 0 else "left"
        else:
            self.direction = "down" if dy > 0 else "up"
        self.image = self.images[self.direction]
        
        # Wenn nah genug, nicht mehr bewegen
        if distance < 35:
            return

        # Geschwindigkeit basierend auf Zustand (Normal vs. Event)
        speed = settings.SHEEP_FOLLOW_SPEED_EVENT if self.speed_boost else settings.SHEEP_FOLLOW_SPEED_NORMAL
        
        # Normalisierte Bewegung
        if distance > 0:
            self.rect.x += (dx / distance) * speed
            self.rect.y += (dy / distance) * speed

    def start_following(self):
        """Beginnt, dem Spieler zu folgen."""
        self.following = True
        self.timer_active = False # Stoppt den Tick-Sound, wenn es folgt
        if self.assets.sounds["pickup"]:
            self.assets.sounds["pickup"].play()

    def stop_following(self):
        """Stoppt die Verfolgung."""
        self.following = False
        if self.assets.sounds["cancel"]:
            self.assets.sounds["cancel"].play()

    def draw_timer(self, surface):
        """Zeichnet die Uhr und den Timer über dem Schaf, falls es nicht folgt."""
        if not self.following:
            clock_img = self.assets.images["clock_hud"]
            clock_pos = (self.rect.x, self.rect.y - 40)
            surface.blit(clock_img, clock_pos)

            seconds_left = max(0, int(self.timer_remaining + 1))
            timer_text = self.assets.pixel_font_big.render(f"{seconds_left}s", True, settings.WHITE)
            text_pos = (clock_pos[0] + 40, clock_pos[1])
            surface.blit(timer_text, text_pos)

    def draw(self, surface):
        """Zeichnet das Schaf."""
        surface.blit(self.image, self.rect)
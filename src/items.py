import pygame
import random
from . import settings

#* Diese Datei kümmert sich um die Logik für die Items

class Powerup(pygame.sprite.Sprite): #! powerup spawn
    def __init__(self, x, y, powerup_type, assets):
        super().__init__()
        self.type = powerup_type
        self.assets = assets
        self.image = self.assets.images["powerups"][self.type]
        self.rect = self.image.get_rect(topleft=(x, y))
        self.timer = settings.POWERUP_DESPAWN_TIME

    def update(self, dt): #! runterzählender despawn timer
        self.timer -= dt
        if self.timer <= 0:
            self.kill() #! ENTFERNT das sprite aus allen gruppen

    def draw_timer(self, surface): #! zeichnet den verbleibenden timer
        sec = max(0, int(self.timer + 1))
        timer_surf = self.assets.pixel_font_big.render(f"{sec}s", True, settings.WHITE)
        surface.blit(timer_surf, (self.rect.right + 5, self.rect.y))

class Snack(pygame.sprite.Sprite): #! Spawnt ein snack (gesund oder giftig)
    def __init__(self, x, y, assets, difficulty):
        super().__init__()
        self.assets = assets
        self.difficulty = difficulty
        self.type = "healthy" #! Startet immer als gesund
        self.image = self.assets.images["snacks"][self.type]
        self.rect = self.image.get_rect(topleft=(x, y))
        
        self.timer = settings.SNACK_DESPAWN_TIME
        self.transformed = False

    def update(self, dt, player_rect): #! TIMER zählt runter + transformation check (gift?)
        self.timer -= dt
        if self.timer <= 0:
            self.kill()
            return
        
        #! Prüft ob der Spieler nahe ist, um den Snack zu verwandeln
        if not self.transformed:
            distance = pygame.math.Vector2(self.rect.center).distance_to(player_rect.center)
            if distance < settings.SNACK_TRANSFORM_DISTANCE:
                chance = settings.SNACK_TOXIC_CHANCES.get(self.difficulty, 0.25)
                if random.random() < chance:
                    self.type = "toxic"
                    self.image = self.assets.images["snacks"][self.type]
                self.transformed = True
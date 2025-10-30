import pygame
import random
from . import settings

#* Diese Datei regelt die Gegner (z.b Wolf nachts)

class Enemy(pygame.sprite.Sprite):
    #! lädt den wolf gegner
    #! Eigenschaften: Bewegt sich zufällig, Spawnt nachts, erteilt Schaden bei Kontakt
    def __init__(self, x, y, assets):
        super().__init__()
        self.assets = assets
        
        #! KORREKTUR: Erstellt eine Kopie des Dictionaries, anstatt das
        #! globale Asset-Dictionary (self.assets.images["enemy"]) zu verändern.
        self.images = self.assets.images["enemy"].copy()
        
        #! fügt up und down sprites hinzu (basierend auf left/right)
        self.images["up"] = self.images["left"]
        self.images["down"] = self.images["right"]
        
        self.direction = random.choice(["up", "down", "left", "right"])
        self.image = self.images[self.direction]
        self.rect = self.image.get_rect(topleft=(x, y))

        self.speed = settings.ENEMY_SPEED
        self.change_dir_timer = 0.0

    def update(self, dt):
        """Aktualisiert die Bewegung und Richtung des Gegners."""
        #! Richtung nach einem Intervall zufällig ändern
        self.change_dir_timer += dt
        if self.change_dir_timer >= settings.ENEMY_CHANGE_DIR_INTERVAL:
            self.direction = random.choice(["up", "down", "left", "right"])
            self.image = self.images[self.direction]
            self.change_dir_timer = 0.0

        #! Bewegung basierend auf der aktuellen Richtung
        if self.direction == "up":
            self.rect.y -= self.speed
        elif self.direction == "down":
            self.rect.y += self.speed
        elif self.direction == "left":
            self.rect.x -= self.speed
        elif self.direction == "right":
            self.rect.x += self.speed
            
        #! Gegner innerhalb der Bildschirmgrenzen halten
        self.rect.left = max(0, self.rect.left)
        self.rect.right = min(settings.VIRTUAL_WIDTH, self.rect.right)
        self.rect.top = max(0, self.rect.top)
        self.rect.bottom = min(settings.VIRTUAL_HEIGHT, self.rect.bottom)
import pygame
from . import settings # <-- Anpassung hier

class Player(pygame.sprite.Sprite):
    """
    Repräsentiert den Spieler (Wolf/Hund).
    Verwaltet Bewegung, Darstellung und Kollisionen.
    """
    def __init__(self, assets):
        super().__init__()
        self.assets = assets
        self.images = self.assets.images["player"]
        self.direction = "down"
        self.image = self.images[self.direction]
        self.rect = self.image.get_rect(center=(settings.VIRTUAL_WIDTH // 2, settings.VIRTUAL_HEIGHT // 2))

        self.speed = settings.PLAYER_START_SPEED
        self.base_speed = settings.PLAYER_START_SPEED
        self.velocity = pygame.Vector2(0, 0)
        self.is_slippery = False
        
        self.walk_sound_playing = False

    def update(self, keys, block_zones):
        """Aktualisiert die Spielerposition basierend auf Input und Kollision."""
        desired_movement = self._get_desired_movement(keys)
        self._update_sound(desired_movement)
        
        # Bewegung basierend auf Steuerung (normal vs. rutschig)
        if self.is_slippery:
            # Langsamere Beschleunigung und Gleiten
            self.velocity += desired_movement * self.speed * 0.2
            self.velocity *= settings.PLAYER_GLIDE_FRICTION
        else:
            self.velocity = desired_movement * self.speed

        # Zukünftige Position berechnen und auf Kollision prüfen
        future_rect = self.rect.move(self.velocity)
        
        collided = False
        for zone in block_zones:
            if future_rect.colliderect(zone):
                collided = True
                break
        
        if not collided:
            self.rect.move_ip(self.velocity)

        # Spieler innerhalb der Bildschirmgrenzen halten
        self.rect.left = max(0, self.rect.left)
        self.rect.right = min(settings.VIRTUAL_WIDTH, self.rect.right)
        self.rect.top = max(0, self.rect.top)
        self.rect.bottom = min(settings.VIRTUAL_HEIGHT, self.rect.bottom)

    def _get_desired_movement(self, keys):
        """Ermittelt die gewünschte Bewegungsrichtung aus den Tasten."""
        desired = pygame.Vector2(0, 0)
        if keys[pygame.K_w] or keys[pygame.K_UP]:
            desired.y = -1
            self.direction = "up"
        if keys[pygame.K_s] or keys[pygame.K_DOWN]:
            desired.y = 1
            self.direction = "down"
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            desired.x = -1
            self.direction = "left"
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            desired.x = 1
            self.direction = "right"

        # Vektor normalisieren, um diagonale Bewegung nicht zu beschleunigen
        if desired.length() > 0:
            desired.normalize_ip()
            
        self.image = self.images[self.direction]
        return desired

    def _update_sound(self, desired_movement):
        """Startet oder stoppt den Lauf-Sound."""
        walk_sound = self.assets.sounds["dog_walk"]
        if not walk_sound: return

        if desired_movement.length() > 0:
            if not self.walk_sound_playing:
                walk_sound.play(-1)
                self.walk_sound_playing = True
        else:
            if self.walk_sound_playing:
                walk_sound.stop()
                self.walk_sound_playing = False
    
    def reset_speed(self):
        """Setzt die Geschwindigkeit auf den Standardwert zurück."""
        self.speed = self.base_speed

    def draw(self, surface):
        """Zeichnet den Spieler auf die angegebene Oberfläche."""
        surface.blit(self.image, self.rect)
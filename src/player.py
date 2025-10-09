import pygame
from . import settings

#* Diese Datei kümmert sich um die Spieler Logik.

class Player(pygame.sprite.Sprite): #! Spieler logik (collision/movement/dash)
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
        
        #* Dash / Boost Logik
        self.last_press_time = {}
        self.is_dashing = False
        self.dash_timer = 0.0
        self.dash_cooldown = 0.0
        self.dash_direction = pygame.Vector2(0, 0)
        
        #* Boost Effekt
        self.boost_effect_image = None
        self.boost_effect_rect = None
        self.boost_effect_timer = 0.0

    def handle_key_down(self, key): #! Verarbeitet Tastendrücke für den Double-Tap-Dash
        movement_keys = [pygame.K_w, pygame.K_UP, pygame.K_s, pygame.K_DOWN, pygame.K_a, pygame.K_LEFT, pygame.K_d, pygame.K_RIGHT]
        
        if key in movement_keys:
            current_time = pygame.time.get_ticks()
            #* Prüft, ob dieselbe Taste kurz zuvor gedrückt wurde
            if key in self.last_press_time and current_time - self.last_press_time[key] < settings.DOUBLE_TAP_INTERVAL * 1000:
                self._start_dash(key)
                self.last_press_time.pop(key) #* Zeitstempel entfernen, um erneutes Auslösen zu verhindern
            else:
                self.last_press_time[key] = current_time

    def _start_dash(self, direction_key): #! Löst den Dash aus
        if self.dash_cooldown > 0:
            return #* Dash ist im Cooldown, nichts tun

        self.is_dashing = True
        self.dash_timer = settings.PLAYER_DASH_DURATION
        self.dash_cooldown = settings.PLAYER_DASH_COOLDOWN
        
        #* Richtung und Effekt basierend auf der Taste festlegen
        if direction_key in [pygame.K_w, pygame.K_UP]:
            self.dash_direction = pygame.Vector2(0, -1)
            self.direction = "up"
            self.boost_effect_image = self.assets.images["boost_effects"]["up"]
            self.boost_effect_rect = self.boost_effect_image.get_rect(midtop=self.rect.midbottom)
        elif direction_key in [pygame.K_s, pygame.K_DOWN]:
            self.dash_direction = pygame.Vector2(0, 1)
            self.direction = "down"
            self.boost_effect_image = self.assets.images["boost_effects"]["down"]
            self.boost_effect_rect = self.boost_effect_image.get_rect(midbottom=self.rect.midtop)
        elif direction_key in [pygame.K_a, pygame.K_LEFT]:
            self.dash_direction = pygame.Vector2(-1, 0)
            self.direction = "left"
            self.boost_effect_image = self.assets.images["boost_effects"]["left"]
            self.boost_effect_rect = self.boost_effect_image.get_rect(midleft=self.rect.midright)
        elif direction_key in [pygame.K_d, pygame.K_RIGHT]:
            self.dash_direction = pygame.Vector2(1, 0)
            self.direction = "right"
            self.boost_effect_image = self.assets.images["boost_effects"]["right"]
            self.boost_effect_rect = self.boost_effect_image.get_rect(midright=self.rect.midleft)

        self.image = self.images[self.direction]
        self.boost_effect_timer = settings.PLAYER_DASH_DURATION + 0.1 #* Effekt etwas länger sichtbar

    def update(self, keys, block_zones, dt): #! aktualisiert die spielerpos nach input
        #* Timer aktualisieren
        if self.dash_cooldown > 0: self.dash_cooldown -= dt
        if self.boost_effect_timer > 0: self.boost_effect_timer -= dt
        
        if self.is_dashing:
            self.dash_timer -= dt
            if self.dash_timer <= 0:
                self.is_dashing = False
        
        #* Bewegungslogik
        if self.is_dashing:
            self.velocity = self.dash_direction * self.speed * settings.PLAYER_DASH_SPEED_MULTIPLIER
        else:
            desired_movement = self._get_desired_movement(keys)
            self._update_sound(desired_movement)
            
            if self.is_slippery:
                self.velocity += desired_movement * self.speed * 0.2
                self.velocity *= settings.PLAYER_GLIDE_FRICTION
            else:
                self.velocity = desired_movement * self.speed
        
        #* Zukünftige Position berechnen und auf Kollision prüfen
        future_rect = self.rect.move(self.velocity * dt * 60) #* Skalierung mit dt für Frame-unabhängigkeit
        
        collided = False
        for zone in block_zones:
            if future_rect.colliderect(zone):
                collided = True
                break
        
        if not collided:
            self.rect.move_ip(self.velocity * dt * 60)

        #* Spieler innerhalb der Bildschirmgrenzen halten
        self.rect.left = max(0, self.rect.left)
        self.rect.right = min(settings.VIRTUAL_WIDTH, self.rect.right)
        self.rect.top = max(0, self.rect.top)
        self.rect.bottom = min(settings.VIRTUAL_HEIGHT, self.rect.bottom)

    def _get_desired_movement(self, keys): #! Ermittelt die gewünschte Bewegungsrichtung aus den Tasten
        desired = pygame.Vector2(0, 0)
        if not self.is_dashing: #* Nur steuern, wenn nicht gedasht wird
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

            if desired.length() > 0:
                desired.normalize_ip()
                
            self.image = self.images[self.direction]
        return desired

    def _update_sound(self, desired_movement): #! Lauf sound start/stopp
        walk_sound = self.assets.sounds["dog_walk"]
        if not walk_sound: return

        if desired_movement.length() > 0 and not self.is_dashing:
            if not self.walk_sound_playing:
                walk_sound.play(-1)
                self.walk_sound_playing = True
        else:
            if self.walk_sound_playing:
                walk_sound.stop()
                self.walk_sound_playing = False
    
    def _draw_cooldown_bar(self, surface): #! Zeichnet die Cooldown-Anzeige für den Dash
        if self.dash_cooldown > 0:
            bar_width = self.rect.width
            bar_height = 10
            bar_x = self.rect.x
            bar_y = self.rect.bottom + 10

            #* Berechnet, wie voll die Leiste ist (sie "lädt auf")
            fill_ratio = 1.0 - (self.dash_cooldown / settings.PLAYER_DASH_COOLDOWN)
            
            #* Hintergrund der Leiste
            bg_rect = pygame.Rect(bar_x, bar_y, bar_width, bar_height)
            pygame.draw.rect(surface, settings.DARK_GRAY, bg_rect)
            
            #* Füllung der Leiste
            fill_width = bar_width * fill_ratio
            fill_rect = pygame.Rect(bar_x, bar_y, fill_width, bar_height)
            pygame.draw.rect(surface, settings.WHITE, fill_rect)
            
            #* Rand
            pygame.draw.rect(surface, settings.WHITE, bg_rect, 2)

    def reset_speed(self): #! Setzt die Geschwindigkeit zurück
        self.speed = self.base_speed

    def draw(self, surface): #! Zeichnet den Spieler und Zusatzelemente auf die Oberfläche
        #* Boost-Effekt zeichnen, falls aktiv
        if self.boost_effect_timer > 0 and self.boost_effect_image:
            surface.blit(self.boost_effect_image, self.boost_effect_rect)
        
        #* Spieler zeichnen
        surface.blit(self.image, self.rect)
        
        #* Cooldown-Anzeige zeichnen
        self._draw_cooldown_bar(surface)
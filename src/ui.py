import pygame
import webbrowser
import random
import math
from . import settings

#* Diese Datei ist für die UI Elemente verantwortlich

class Button: #! Klasse für die klickbaren menü buttons
    def __init__(self, pos, size, image_normal, image_hover, on_click, sound_player):
        self.rect = pygame.Rect(pos, size)
        self.rect.center = pos
        self.image_normal = pygame.transform.scale(image_normal, size)
        self.image_hover = pygame.transform.scale(image_hover, size)
        self.on_click = on_click
        self.sound_player = sound_player
        self.is_hovered = False

    def update_hover(self, virtual_mouse_pos): #! aktualisiert den hover zustand
        self.is_hovered = self.rect.collidepoint(virtual_mouse_pos)

    def handle_event(self, event): #! verarbeitet maus eingaben
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and self.is_hovered:
            self.sound_player()
            self.on_click()

    def draw(self, surface): #! zeichnet die buttons
        image_to_draw = self.image_hover if self.is_hovered else self.image_normal
        surface.blit(image_to_draw, self.rect)
        
    def update_animation(self, offset): #! aktualisiert den y wert fü die ping pong anim
        self.rect.centery += offset

class AnimatedObject: #! animiertes schaf + animierter hund für das main screen
    def __init__(self, frames, start_x, start_y, speed, frame_delay=800):
        self.frames = frames
        self.x = start_x
        self.y = start_y
        self.speed = speed
        self.frame_delay = frame_delay
        self.frame_index = 0
        self.animation_timer = 0
    
    def update(self, dt):
        self.x += self.speed
        if self.x > settings.VIRTUAL_WIDTH:
            self.x = -self.frames[0].get_width()
        
        self.animation_timer += dt * 1000 #! in Millisekunden
        if self.animation_timer >= self.frame_delay:
            self.frame_index = (self.frame_index + 1) % len(self.frames)
            self.animation_timer = 0
            
    def draw(self, surface, offset=(0,0)):
        surface.blit(self.frames[self.frame_index], (self.x + offset[0], self.y + offset[1]))

class PopupText(pygame.sprite.Sprite):
    """Ein Text, der auf dem Bildschirm erscheint und verblasst."""
    def __init__(self, x, y, text, font, color):
        super().__init__()
        self.image = font.render(text, True, color)
        self.rect = self.image.get_rect(center=(x, y))
        self.alpha = 255
        self.timer = 1.5 # Lebensdauer in Sekunden

    def update(self, dt):
        self.rect.y -= 30 * dt
        self.alpha -= 170 * dt
        if self.alpha <= 0:
            self.kill()
        else:
            self.image.set_alpha(int(self.alpha))

def draw_hud(surface, assets, lives, score, coins): #! heads up display (münzen, leben etc)
    #? Score
    score_text = f"Score: {score}"
    score_surf = assets.pixel_font_big.render(score_text, True, settings.WHITE)
    surface.blit(score_surf, (40, 20))

    #? Leben
    heart_img = assets.images["heart_hud"]
    for i in range(lives):
        heart_x = settings.VIRTUAL_WIDTH - (heart_img.get_width() + 10) * (i + 1)
        surface.blit(heart_img, (heart_x, 20))

    #? Münzen
    coin_img = assets.images["coin_hud"]
    coin_y = 20 + heart_img.get_height() + 10
    coin_x = settings.VIRTUAL_WIDTH - coin_img.get_width() - 40
    surface.blit(coin_img, (coin_x, coin_y))
    coins_surf = assets.pixel_font_big.render(str(coins), True, settings.WHITE)
    coins_rect = coins_surf.get_rect(midright=(coin_x - 10, coin_y + coin_img.get_height() // 2))
    surface.blit(coins_surf, coins_rect)

def draw_time(surface, assets, current_day, game_minutes): #! Zeichnet die ingame uhrzeit
    hour = int((game_minutes // 60) % 24)
    minute = int(game_minutes % 60)
    time_str = f"Tag {current_day}: {hour:02d}:{minute:02d}"
    time_surf = assets.pixel_font_big.render(time_str, True, settings.WHITE)
    time_rect = time_surf.get_rect(midtop=(settings.VIRTUAL_WIDTH // 2, 10))
    surface.blit(time_surf, time_rect)

def draw_glow(surface, rect, tick, is_night): #! zeichnet den glow effekt bei entities nachts
    if is_night:
        radius = 35 + 5 * math.sin(tick / 10)
        glow_surface = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
        pygame.draw.circle(glow_surface, (255, 255, 100, 80), (radius, radius), int(radius))
        glow_rect = glow_surface.get_rect(center=rect.center)
        surface.blit(glow_surface, glow_rect)

def open_url(url): #! öffnet eine url im browser
    try:
        webbrowser.open(url)
    except Exception as e:
        print(f"Fehler beim Öffnen der URL {url}: {e}") #! Fehler beim öffnen
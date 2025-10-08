import pygame
import sys
import os
import random
import math

from . import settings
from .assets import Assets
from .player import Player
from .sheep import Sheep
from .enemy import Enemy
from .items import Powerup, Snack
from .ui import Button, PopupText, AnimatedObject, draw_hud, draw_time, draw_glow, open_url # <-- Anpassung hier
from .events import EventManager

#* Diese Datei handlet die Hintergrund und Spiel Logik

class Game: #! Hauptklasse die das Spiel steuert
    def __init__(self):
        pygame.init()
        #! Bildschirm-Setup mit Skalierung
        self.real_screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        self.screen_width, self.screen_height = self.real_screen.get_size()
        self.virtual_screen = pygame.Surface((settings.VIRTUAL_WIDTH, settings.VIRTUAL_HEIGHT))
        
        #! speichert optionen zur skalierung mit der mausumrechnung
        self.scale_info = {"factor": 1.0, "offset_x": 0, "offset_y": 0}
        
        pygame.display.set_caption(settings.TITLE)
        self.clock = pygame.time.Clock()
        self.is_running = True
        self.state = "menu"
        self.tick = 0
        
        #! Assets laden
        self.assets = Assets()
        if self.assets.images.get("icon"):
            pygame.display.set_icon(self.assets.images["icon"])
            
        #! Spielvariablen
        self.difficulty = "Leicht"
        self.lives = 0
        self.score = 0
        self.coins = 0
        self.highscore = 0
        self._load_saved_data()

        #! Sprite-Gruppen
        self.all_sprites = pygame.sprite.Group()
        self.sheep_group = pygame.sprite.Group()
        self.enemy_group = pygame.sprite.Group()
        self.powerup_group = pygame.sprite.Group()
        self.snack_group = pygame.sprite.Group()
        self.popup_group = pygame.sprite.Group()

        #! Menü-Setup
        self._setup_menu()

        #! Spiel-Setup
        self.player = None
        self.stall_rect = None
        self.block_zone = None
        self.delivery_zone = None
        self.map_surface = None
        self.chosen_map_base = ""
        self.currently_followed_sheep = None
        
        #! Power-up-Zustände
        self.active_powerup = None
        self.powerup_effect_timer = 0.0
        self.magnet_range = settings.BASE_MAGNET_RANGE
        self.freeze_active = False
        
        self.event_manager = EventManager(self)
        
        self.music_started = False
        self.game_over = False

    def _load_saved_data(self): #! Lädt Spielstand aus den Txt dateien
        try:
            with open("highscore.txt", "r") as f:
                self.highscore = int(f.read().strip())
        except (FileNotFoundError, ValueError):
            self.highscore = 0
        try:
            with open("coins.txt", "r") as f:
                self.coins = int(f.read().strip())
        except (FileNotFoundError, ValueError):
            self.coins = 0
            
    def _save_data(self): #! Speichert den Spielstand in die txt dateien
        if self.score > self.highscore:
            self.highscore = self.score
            with open("highscore.txt", "w") as f:
                f.write(str(self.highscore))
        with open("coins.txt", "w") as f:
            f.write(str(self.coins))

    def run(self): #* Die Hauptspielschleife
        while self.is_running:
            dt = self.clock.tick(settings.FPS) / 1000.0
            
            #* je nach schwierigkeit die richtige methode abrufen
            if self.state == "menu":
                self._run_menu(dt)
            elif self.state == "choose_difficulty":
                self._run_difficulty_selection(dt)
            elif self.state == "game":
                self._run_game(dt)
            
            #! den bildschirm skalieren
            self._scale_and_draw_to_real_screen()
            self.tick += 1

    def _scale_and_draw_to_real_screen(self): #! SKALIERT den visuellen bildschirm auf den echten zurecht
        self.scale_info["factor"] = min(self.screen_width / settings.VIRTUAL_WIDTH, self.screen_height / settings.VIRTUAL_HEIGHT)
        scaled_width = int(settings.VIRTUAL_WIDTH * self.scale_info["factor"])
        scaled_height = int(settings.VIRTUAL_HEIGHT * self.scale_info["factor"])
        
        scaled_surface = pygame.transform.scale(self.virtual_screen, (scaled_width, scaled_height))
        
        self.scale_info["offset_x"] = (self.screen_width - scaled_width) / 2
        self.scale_info["offset_y"] = (self.screen_height - scaled_height) / 2
        
        self.real_screen.fill(settings.BLACK)
        self.real_screen.blit(scaled_surface, (self.scale_info["offset_x"], self.scale_info["offset_y"]))
        pygame.display.flip()

    #! NEUE HILFSFUNKTION - maus umrechnung
    def _get_virtual_mouse_pos(self):
        """Konvertiert die realen Mauskoordinaten in virtuelle Koordinaten."""
        mx, my = pygame.mouse.get_pos()
        factor = self.scale_info["factor"]
        offset_x = self.scale_info["offset_x"]
        offset_y = self.scale_info["offset_y"]
        
        if factor == 0: return 0, 0 # Division durch Null verhindern
            
        virtual_mx = int((mx - offset_x) / factor)
        virtual_my = int((my - offset_y) / factor)
        return virtual_mx, virtual_my
        
    #! ---------------------------------
    #! MENÜ-LOGIK
    #! ---------------------------------
    
    def _setup_menu(self): #! Initialisiert alle Hauptmenü Elemente
        self.menu_buttons = self._create_menu_buttons()
        self.difficulty_buttons = self._create_difficulty_buttons()
        self.bg_frame_index = 0
        self.bg_frame_timer = 0
        self.menu_sheep = AnimatedObject(self.assets.images["menu_sheep"], -128, settings.VIRTUAL_HEIGHT - 280, 2)
        self.menu_dog = AnimatedObject(self.assets.images["menu_dog"], -128, settings.VIRTUAL_HEIGHT - 280, 2)
        self.clouds = [{"x": -200 - i * 300, "y": 100 + i * 60, "speed": 0.3} for i in range(3)]
        
    def _create_menu_buttons(self):
        btn_y, spacing = settings.MENU_BUTTON_START_Y, settings.MENU_BUTTON_SPACING
        btn_imgs = {name: self._load_button_images(name) for name in ["spielen", "anleitung", "verlassen"]}
        return {
            "spielen": Button((settings.VIRTUAL_WIDTH // 2, btn_y), settings.MENU_BUTTON_SIZE, btn_imgs["spielen"][0], btn_imgs["spielen"][1], self._go_to_difficulty, self._play_click),
            "anleitung": Button((settings.VIRTUAL_WIDTH // 2, btn_y + spacing), settings.MENU_BUTTON_SIZE, btn_imgs["anleitung"][0], btn_imgs["anleitung"][1], lambda: open_url(settings.ANLEITUNG_URL), self._play_click),
            "verlassen": Button((settings.VIRTUAL_WIDTH // 2, btn_y + 2 * spacing), settings.MENU_BUTTON_SIZE, btn_imgs["verlassen"][0], btn_imgs["verlassen"][1], self._quit_game, self._play_click)
        }
        
    def _create_difficulty_buttons(self):
        btn_y, spacing = settings.DIFF_BUTTON_START_Y, settings.DIFF_BUTTON_SPACING
        btn_imgs = {name: self._load_button_images(name, True) for name in ["leicht", "mittel", "schwer"]}
        return {
            "leicht": Button((settings.VIRTUAL_WIDTH // 2, btn_y), settings.DIFF_BUTTON_SIZE, btn_imgs["leicht"][0], btn_imgs["leicht"][1], lambda: self._start_game("Leicht"), self._play_click),
            "mittel": Button((settings.VIRTUAL_WIDTH // 2, btn_y + spacing), settings.DIFF_BUTTON_SIZE, btn_imgs["mittel"][0], btn_imgs["mittel"][1], lambda: self._start_game("Mittel"), self._play_click),
            "schwer": Button((settings.VIRTUAL_WIDTH // 2, btn_y + 2 * spacing), settings.DIFF_BUTTON_SIZE, btn_imgs["schwer"][0], btn_imgs["schwer"][1], lambda: self._start_game("Schwer"), self._play_click)
        }

    def _load_button_images(self, name, is_diff=False):
        path_normal = f"./media/main-menu/buttons/button-{name}.png"
        normal_img = self.assets._load_image(path_normal)
        hover_img = normal_img.copy()
        hover_img.fill((50, 50, 50, 0), special_flags=pygame.BLEND_RGB_ADD)
        return normal_img, hover_img

    def _run_menu(self, dt):
        virtual_mouse_pos = self._get_virtual_mouse_pos()
        for button in self.menu_buttons.values():
            button.update_hover(virtual_mouse_pos)
            
        self._handle_events(self.menu_buttons)
        self._update_menu_animations(dt)
        self._draw_menu()

    def _run_difficulty_selection(self, dt):
        virtual_mouse_pos = self._get_virtual_mouse_pos()
        for button in self.difficulty_buttons.values():
            button.update_hover(virtual_mouse_pos)

        self._handle_events(self.difficulty_buttons)
        self._update_menu_animations(dt)
        self._draw_difficulty_selection()

    def _handle_events(self, buttons): #! Event verarbeitung
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.is_running = False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE and self.state == "choose_difficulty":
                self.state = "menu"
            for button in buttons.values():
                button.handle_event(event)

    def _update_menu_animations(self, dt):
        self.bg_frame_timer += dt * 1000
        if self.bg_frame_timer >= 100:
            self.bg_frame_index = (self.bg_frame_index + 1) % len(self.assets.images["bg_frames"])
            self.bg_frame_timer = 0
        if not self.music_started:
            self.play_music(is_menu=True)
            self.music_started = True
        self.menu_sheep.update(dt)
        self.menu_dog.update(dt)
        for cloud in self.clouds:
            cloud["x"] += cloud["speed"]
            if cloud["x"] > settings.VIRTUAL_WIDTH:
                cloud["x"] = -self.assets.images["cloud"].get_width()

    def _draw_menu(self):
        self._draw_common_menu_bg()
        for button in self.menu_buttons.values():
            button.draw(self.virtual_screen)
        hs_surf = self.assets.pixel_font_big.render(f"Highscore: {self.highscore}", True, settings.WHITE)
        self.virtual_screen.blit(hs_surf, hs_surf.get_rect(topright=(settings.VIRTUAL_WIDTH - 40, 20)))
        ver_surf = self.assets.pixel_font_big.render("Version 1.01", True, settings.WHITE)
        self.virtual_screen.blit(ver_surf, (20, 20))
        
    def _draw_difficulty_selection(self):
        self._draw_common_menu_bg()
        for button in self.difficulty_buttons.values():
            button.draw(self.virtual_screen)

    def _draw_common_menu_bg(self):
        self.virtual_screen.blit(self.assets.images["bg_frames"][self.bg_frame_index], (0, 0))
        for cloud in self.clouds:
            self.virtual_screen.blit(self.assets.images["cloud"], (cloud["x"], cloud["y"]))
        self.menu_sheep.draw(self.virtual_screen)
        self.menu_dog.draw(self.virtual_screen, offset=(-350, 0))
        logo_rect = self.assets.images["logo"].get_rect(center=(settings.VIRTUAL_WIDTH // 2, 150))
        self.virtual_screen.blit(self.assets.images["logo"], logo_rect)

    def _go_to_difficulty(self): self.state = "choose_difficulty"
    def _quit_game(self): self.is_running = False
    def _play_click(self):
        if self.assets.sounds["click"]: self.assets.sounds["click"].play()

    #! ---------------------------------
    #! SPIEL-LOGIK
    #! ---------------------------------

    def _start_game(self, difficulty):
        self.difficulty = difficulty
        self.lives = settings.LIVES_PER_DIFFICULTY.get(difficulty, 3)
        self.score = 0
        self.current_day = 1
        self.game_minutes = settings.GAME_START_MINUTES
        self.night_mode = False
        self.game_over = False
        
        self.player = Player(self.assets)
        self.all_sprites.add(self.player)
        self.powerup_spawn_timer = 0.0
        self.snack_spawn_timer = 0.0
        
        map_paths = ["./media/game/maps/map1/map1", "./media/game/maps/map2/map2", "./media/game/maps/map3/map3"]
        self.chosen_map_base = random.choice(map_paths)
        self.map_surface = self.assets.load_map(self.chosen_map_base, self.night_mode)
        self._place_stall_and_sheep()
        
        self.play_music()
        self.state = "game"

    def _reset_game(self):
        self._save_data()
        self.all_sprites.empty()
        self.sheep_group.empty()
        self.enemy_group.empty()
        self.powerup_group.empty()
        self.snack_group.empty()
        self.popup_group.empty()
        
        self.player = None
        self.stall_rect = None
        self.currently_followed_sheep = None
        
        self.music_started = False
        pygame.mixer.music.stop()
        if self.assets.sounds.get('dog_walk'): self.assets.sounds['dog_walk'].stop()
        if self.assets.sounds.get('regen'): self.assets.sounds['regen'].stop()

        self.state = "menu"

    def _run_game(self, dt):
        self._handle_game_events()
        if self.state != "game": return
        
        if not self.game_over:
            self._update_game_logic(dt)
        
        self._draw_game()

    def _handle_game_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT: self._quit_game()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE: self._reset_game()

    def _update_game_logic(self, dt):
        keys = pygame.key.get_pressed()
        
        self.player.update(keys, [self.block_zone])
        self.sheep_group.update(dt, self.player.rect, self.freeze_active)
        self.enemy_group.update(dt)
        self.powerup_group.update(dt)
        self.snack_group.update(dt, self.player.rect)
        self.popup_group.update(dt)
        self.event_manager.update(dt)
        
        self._update_time(dt)
        self._handle_sheep_logic(dt)
        self._handle_collisions()
        self._update_active_powerups(dt)
        
        self._spawn_powerups(dt)
        self._spawn_snacks(dt)

    def _draw_game(self):
        self.virtual_screen.blit(self.map_surface, (0, 0))
        
        highlight_surf = pygame.Surface(self.delivery_zone.size, pygame.SRCALPHA)
        pygame.draw.rect(highlight_surf, (100, 255, 100, 60), highlight_surf.get_rect(), width=4, border_radius=8)
        self.virtual_screen.blit(highlight_surf, self.delivery_zone.topleft)
        
        self.virtual_screen.blit(self.assets.images["stall"], self.stall_rect)
        
        for powerup in self.powerup_group:
            self.virtual_screen.blit(powerup.image, powerup.rect)
            powerup.draw_timer(self.virtual_screen)
        self.snack_group.draw(self.virtual_screen)
            
        for sheep in self.sheep_group:
            draw_glow(self.virtual_screen, sheep.rect, self.tick, self.night_mode)
            sheep.draw(self.virtual_screen)
            sheep.draw_timer(self.virtual_screen)
            
        self.enemy_group.draw(self.virtual_screen)
        draw_glow(self.virtual_screen, self.player.rect, self.tick, self.night_mode)
        self.player.draw(self.virtual_screen)
        self.popup_group.draw(self.virtual_screen)

        draw_hud(self.virtual_screen, self.assets, self.lives, self.score, self.coins)
        draw_time(self.virtual_screen, self.assets, self.current_day, self.game_minutes)
        self.event_manager.draw(self.virtual_screen)
        
        if self.game_over:
            overlay = pygame.Surface((settings.VIRTUAL_WIDTH, settings.VIRTUAL_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 180))
            self.virtual_screen.blit(overlay, (0, 0))
            go_text = self.assets.pixel_font_big.render("Du hast verloren...", True, settings.RED)
            esc_text = self.assets.pixel_font_small.render("Drücke ESC um ins Menü zurückzukehren", True, settings.WHITE)
            self.virtual_screen.blit(go_text, go_text.get_rect(center=(settings.VIRTUAL_WIDTH // 2, settings.VIRTUAL_HEIGHT // 2 - 20)))
            self.virtual_screen.blit(esc_text, esc_text.get_rect(center=(settings.VIRTUAL_WIDTH // 2, settings.VIRTUAL_HEIGHT // 2 + 40)))

    def _update_time(self, dt):
        time_multiplier = 2 if self.night_mode else 1 #! 1 sek im leben = 1 min im spiel
        self.game_minutes += dt * time_multiplier 
        
        was_day = not self.night_mode
        self.night_mode = settings.NIGHT_START_MINUTES <= self.game_minutes < settings.DAY_START_MINUTES
        is_day = not self.night_mode
        
        if self.night_mode and was_day: #! Übergang zu Nacht
            self.map_surface = self.assets.load_map(self.chosen_map_base, True)
            self.play_music()
            self._spawn_enemies()
        elif is_day and not was_day: #! Übergang zu Tag
            self.current_day += 1
            self.game_minutes = settings.GAME_START_MINUTES
            self.map_surface = self.assets.load_map(self.chosen_map_base, False)
            self.play_music()
            self.enemy_group.empty()

    def _handle_sheep_logic(self, dt):  #! Timer abgelaufen?
        for sheep in list(self.sheep_group):
            if sheep.timer_remaining <= 0:
                self.lives -= 1
                self.score -= 1
                self.popup_group.add(PopupText(sheep.rect.centerx, sheep.rect.centery, "-1 Leben", self.assets.pixel_font_small, settings.RED))
                if self.assets.sounds["loose"]: self.assets.sounds["loose"].play()
                sheep.kill()
                self._spawn_single_sheep()
                self._check_game_over()

        #! Neues Schaf verfolgen?
        if self.currently_followed_sheep is None:
            for sheep in self.sheep_group:
                if not sheep.following:
                    distance = pygame.math.Vector2(self.player.rect.center).distance_to(sheep.rect.center)
                    if distance < self.magnet_range:
                        sheep.start_following()
                        self.currently_followed_sheep = sheep
                        break
        
        #! Aktuelle Verfolgung
        if self.currently_followed_sheep:
            #! Abbruchchance
            if random.random() < settings.SHEEP_CANCEL_CHANCE.get(self.difficulty, 0):
                self.currently_followed_sheep.stop_following()
                self.currently_followed_sheep = None
            #! Abliefern
            elif self.delivery_zone.colliderect(self.currently_followed_sheep.rect):
                self.score += 1
                self.coins += 1
                self.popup_group.add(PopupText(self.stall_rect.centerx, self.stall_rect.top, "+1", self.assets.pixel_font_big, settings.POPUP_PLUS_ONE_COLOR))
                if self.assets.sounds["deliver"]: self.assets.sounds["deliver"].play()
                self.currently_followed_sheep.kill()
                self._spawn_single_sheep()
                self.currently_followed_sheep = None

    def _handle_collisions(self): #! Collision handling mit objekten
        #! Spieler mit Power-ups
        collided_powerups = pygame.sprite.spritecollide(self.player, self.powerup_group, True)
        for powerup in collided_powerups:
            if self.assets.sounds["powerup"]: self.assets.sounds["powerup"].play()
            self._apply_powerup_effect(powerup)

        #! Spieler mit Snacks
        collided_snacks = pygame.sprite.spritecollide(self.player, self.snack_group, True)
        for snack in collided_snacks:
            if snack.type == "healthy":
                self.coins += 2
                self.score += 1
                self.popup_group.add(PopupText(snack.rect.centerx, snack.rect.y, "+2 Coins", self.assets.pixel_font_small, settings.TIMER_COLOR))
                if self.assets.sounds["dog_eat"]: self.assets.sounds["dog_eat"].play()
            else: #! toxic snack = lebensabzug
                self.lives -= 1
                self.popup_group.add(PopupText(snack.rect.centerx, snack.rect.y, "Vergiftet!", self.assets.pixel_font_small, settings.RED))
                if self.assets.sounds["cancel"]: self.assets.sounds["cancel"].play()
                self._check_game_over()

        #! Spieler mit Gegnern = ebenfalls lebensabzug
        if self.night_mode:
            collided_enemies = pygame.sprite.spritecollide(self.player, self.enemy_group, True)
            if collided_enemies:
                self.lives -= 1
                self.popup_group.add(PopupText(self.player.rect.centerx, self.player.rect.y, "Gebissen!", self.assets.pixel_font_small, settings.RED))
                if self.assets.sounds["cancel"]: self.assets.sounds["cancel"].play()
                self._spawn_single_enemy()
                self._check_game_over()
    
    def _apply_powerup_effect(self, powerup):
        self.active_powerup = powerup.type
        self.powerup_effect_timer = settings.POWERUP_EFFECT_DURATION
        
        if powerup.type == "speed":
            self.player.speed = self.player.base_speed * settings.POWERUP_SPEED_BONUS_MULTIPLIER
        elif powerup.type == "magnet":
            self.magnet_range = settings.BASE_MAGNET_RANGE * settings.POWERUP_MAGNET_RANGE_MULTIPLIER
        elif powerup.type == "freeze":
            self.freeze_active = True
            self.powerup_effect_timer = settings.POWERUP_FREEZE_DURATION
        elif powerup.type == "score10":
            self.score += settings.POWERUP_SCORE_BONUS
            self.popup_group.add(PopupText(powerup.rect.centerx, powerup.rect.y, f"+{settings.POWERUP_SCORE_BONUS} Score", self.assets.pixel_font_small, settings.TIMER_COLOR))
            self.active_powerup = None #! Sofortiger Effekt
        elif powerup.type == "random":
             random_type = random.choice(["speed", "magnet", "score10", "freeze"])
             #! Erstelle ein "Dummy"-Powerup, um den Effekt auszulösen
             dummy_powerup = Powerup(0,0, random_type, self.assets)
             self._apply_powerup_effect(dummy_powerup)
    
    def _update_active_powerups(self, dt):
        if self.active_powerup:
            self.powerup_effect_timer -= dt
            if self.powerup_effect_timer <= 0:
                if self.active_powerup == "speed": self.player.reset_speed()
                if self.active_powerup == "magnet": self.magnet_range = settings.BASE_MAGNET_RANGE
                if self.active_powerup == "freeze": self.freeze_active = False
                self.active_powerup = None
                self.powerup_effect_timer = 0

    def _spawn_powerups(self, dt):
        self.powerup_spawn_timer += dt
        if self.powerup_spawn_timer >= settings.POWERUP_SPAWN_INTERVAL:
            self.powerup_spawn_timer = 0
            ptype = random.choice(list(self.assets.images["powerups"].keys()))
            x = random.randint(100, settings.VIRTUAL_WIDTH - 100)
            y = random.randint(100, settings.VIRTUAL_HEIGHT - 100)
            self.powerup_group.add(Powerup(x, y, ptype, self.assets))
            
    def _spawn_snacks(self, dt):
        self.snack_spawn_timer += dt
        if len(self.snack_group) == 0 and self.snack_spawn_timer >= settings.SNACK_SPAWN_INTERVAL:
            self.snack_spawn_timer = 0
            x = random.randint(100, settings.VIRTUAL_WIDTH - 100)
            y = random.randint(100, settings.VIRTUAL_HEIGHT - 100)
            self.snack_group.add(Snack(x, y, self.assets, self.difficulty))

    def _place_stall_and_sheep(self):
        stall_img = self.assets.images["stall"]
        margin = settings.STALL_MARGIN
        x = random.randint(margin, settings.VIRTUAL_WIDTH - margin - stall_img.get_width())
        y = random.randint(margin, settings.VIRTUAL_HEIGHT - margin - stall_img.get_height())
        self.stall_rect = stall_img.get_rect(topleft=(x, y))
        self.block_zone = self.stall_rect.copy()
        self.delivery_zone = self.stall_rect.inflate(*settings.DELIVERY_ZONE_INFLATE)
        self.sheep_group.empty()
        for _ in range(settings.SHEEP_SPAWN_COUNT):
            self._spawn_single_sheep()

    def _spawn_single_sheep(self, is_ufo=False):
        while True:
            x = random.randint(100, settings.VIRTUAL_WIDTH - 100)
            y = random.randint(100, settings.VIRTUAL_HEIGHT - 100)
            img = self.assets.images["sheep"]["down"]
            new_rect = img.get_rect(topleft=(x,y))
            if not self.block_zone.colliderect(new_rect):
                self.sheep_group.add(Sheep(x, y, self.assets, self.difficulty, is_ufo))
                break

    def _spawn_enemies(self):
        self.enemy_group.empty()
        for _ in range(settings.ENEMY_SPAWN_COUNT):
            self._spawn_single_enemy()
            
    def _spawn_single_enemy(self):
        while True:
            x = random.randint(100, settings.VIRTUAL_WIDTH - 100)
            y = random.randint(100, settings.VIRTUAL_HEIGHT - 100)
            img = self.assets.images["enemy"]["left"]
            new_rect = img.get_rect(topleft=(x,y))
            if not self.block_zone.colliderect(new_rect) and self.player.rect.distance_to(new_rect) > 200:
                self.enemy_group.add(Enemy(x, y, self.assets))
                break

    def _check_game_over(self):
        if self.lives <= 0:
            self.game_over = True
            pygame.mixer.music.stop()
            if self.player.walk_sound_playing: self.assets.sounds["dog_walk"].stop()
            self._save_data()

    def play_music(self, is_menu=False):
        pygame.mixer.music.stop()
        if self.assets.sounds.get("vogel"): self.assets.sounds["vogel"].stop()

        if is_menu:
            path = self.assets.sounds["menu_music"]
            pygame.mixer.music.set_volume(0.3)
            if self.assets.sounds["vogel"]: self.assets.sounds["vogel"].play(-1)
        else:
            path = self.assets.sounds["night_music"] if self.night_mode else self.assets.sounds["day_music"]
            pygame.mixer.music.set_volume(0.5)

        if os.path.exists(path):
            pygame.mixer.music.load(path)
            pygame.mixer.music.play(-1)
import pygame
from src.game import Game  # <-- Diese Zeile wird angepasst

if __name__ == '__main__':
    # Überprüfen, ob Pygame-Module geladen werden können
    if not pygame.font:
        print("Warnung: Font-Modul konnte nicht geladen werden.")
    if not pygame.mixer:
        print("Warnung: Mixer-Modul konnte nicht geladen werden.")

    # Das Haupt-Game-Objekt erstellen und die Hauptschleife starten
    game = Game()
    game.run()

    # Pygame ordnungsgemäß beenden
    pygame.quit()
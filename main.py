import pygame
from src.game import Game

if __name__ == '__main__':
    #? Pygame module überprüfen
    if not pygame.font:
        print("Warnung: Font-Modul konnte nicht geladen werden.")
    if not pygame.mixer:
        print("Warnung: Mixer-Modul konnte nicht geladen werden.")

    #? game objekt erstellen, main-loop starten
    game = Game()
    game.run()

    #! pygame beenden
    pygame.quit()
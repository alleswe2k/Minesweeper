import pygame
from camera import Camera

class Tile:
    def __init__(self, row, col, value, rect, images):
        
        self.row = row
        self.col = col
        self.value = value

        self.revealed = False
        self.flagged = False

        self.rect = rect
        self.images = images

    def draw(self, surface, camera: Camera):
        screen_rect = camera.apply(self.rect)

        if not self.revealed:
            if self.flagged:
                img = self.images["flag"]
            else:
                img = self.images["hidden"]
        else:
            if self.value == -1:
                img = self.images["bomb"]
            else:
                img = self.images[self.value]

        img = pygame.transform.scale(img, (screen_rect.w, screen_rect.h))
        surface.blit(img, screen_rect)

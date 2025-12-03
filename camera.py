import pygame

class Camera:
    def __init__(self):
        self.x = 0
        self.y = 0
        self.zoom = 1.0

    def apply(self, rect):
        # Convert world-space rect into screen-space
        return pygame.Rect(
            (rect.x - self.x) * self.zoom,
            (rect.y - self.y) * self.zoom,
            rect.width * self.zoom,
            rect.height * self.zoom
        )

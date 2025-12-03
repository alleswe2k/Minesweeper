import pygame

class Camera:
    def __init__(self, x=0, y=0, zoom=1.0):
        self.x = x
        self.y = y
        self.zoom = zoom

    def apply(self, rect):
        # Convert world-space rect into screen-space
        return pygame.Rect(
            (rect.x - self.x) * self.zoom,
            (rect.y - self.y) * self.zoom,
            rect.width * self.zoom,
            rect.height * self.zoom
        )

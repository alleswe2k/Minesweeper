import pygame
import numpy as np
from tile import Tile
from camera import Camera

NEIGHBOR_OFFSETS = [
    (-1, -1), (-1, 0), (-1, 1),
    (0, -1),           (0, 1),
    (1, -1),  (1, 0),  (1, 1)
]


class BombBoard:
    def __init__(self, height, width, bombs, tile_size, base_x, base_y, images):
        
        self.height = height
        self.width = width
        self.bombs = bombs
        self.tile_size = tile_size

        values = self._generate_values()

        self.game_over = False
        self.win = False

        self.tiles = []
        for r in range(height):
            row = []
            for c in range(width):
                rect = pygame.Rect(
                    base_x + c*tile_size,
                    base_y + r*tile_size,
                    tile_size,
                    tile_size
                )
                row.append(Tile(r, c, values[r][c], rect, images))
            self.tiles.append(row)

    def _generate_values(self):
        total = self.height * self.width
        arr = np.array([-1]*self.bombs + [0]*(total - self.bombs))
        np.random.shuffle(arr)
        board = arr.reshape((self.height, self.width))

        # Compute numbers
        for r in range(self.height):
            for c in range(self.width):
                if board[r][c] == -1:
                    continue

                count = 0
                for dr, dc in NEIGHBOR_OFFSETS:
                    nr = r + dr
                    nc = c + dc
                    if 0 <= nr < self.height and 0 <= nc < self.width:
                        if board[nr][nc] == -1:
                            count += 1

                board[r][c] = count 
            
        return board

    def draw(self, surface, camera: Camera):
        for row in self.tiles:
            for tile in row:
                tile.draw(surface, camera)

    def display_stats(self, surface, font, elapsed_time):

        timer_surf = font.render(f"Time: {elapsed_time}", True, "White")
        surface.blit(timer_surf, (10, 10))

        flags = 0
        for r in self.tiles:
            for c in r:
                if c.flagged:
                    flags += 1
        bombs_left = self.bombs - flags
        text = font.render(f"Bombs left: {bombs_left}", True, "white")
        surface.blit(text, (10, 50))

    def handle_click(self, pos, button):
        # Compute tile directly from mouse pos
        if self.game_over or self.win:
            return # Stop all clicks after game ends

        for row in self.tiles:
            for tile in row:
                if tile.rect.collidepoint(pos):
                    if button == 1:
                        self.reveal_tile(tile)
                        self.chord_tile(tile)
                        return 
                    elif button == 3:
                        if not tile.revealed:
                            tile.flagged = not tile.flagged
                    return

    def reveal_tile(self, tile: Tile):

        if tile.flagged or tile.revealed:
            return
        
        tile.revealed = True

        if tile.value == -1:
            self.game_over = True
            self._reveal_all_bombs()
            return
        
        if tile.value != 0:
            self._check_win()
            return
        
        self._reveal_neighbors(tile.row, tile.col)
        self._check_win()

    def _reveal_neighbors(self, r, c):
        stack = [(r, c)]

        while stack:
            rr, cc = stack.pop()
            current: Tile = self.tiles[rr][cc]

            # Reveal this tile if not revealed
            if not current.revealed and not current.flagged:
                current.revealed = True

            # If this tile is not zero, stop here
            if current.value != 0:
                continue

            # Flood to neighbors
            for dr, dc in NEIGHBOR_OFFSETS:
                nr = rr + dr
                nc = cc + dc
                if 0 <= nr < self.height and 0 <= nc < self.width:
                    neighbor = self.tiles[nr][nc]
                    if not neighbor.revealed and not neighbor.flagged:
                        stack.append((nr, nc))

    def chord_tile(self, tile: Tile):
        # Only possible on revealed number tiles
        if not tile.revealed or tile.value <= 0:
            return
        
        r, c = tile.row, tile.col

        # Count adjacent flags
        flag_count = 0
        neighbors = []

        for dr, dc in NEIGHBOR_OFFSETS:
            nr = r + dr
            nc = c + dc
            if 0 <= nr < self.height and 0 <= nc < self.width:
                nb = self.tiles[nr][nc]
                neighbors.append(nb)
                if nb.flagged:
                    flag_count += 1

        # Only chord if flags = tile number
        if flag_count != tile.value:
            return
        
        # Reveal all non-flagged neighbors
        for nb in neighbors:
            if not nb.flagged and not nb.revealed:
                self.reveal_tile(nb)

    
    def _reveal_all_bombs(self):
        for row in self.tiles:
            for tile in row:
                if tile.value == -1:
                    tile.revealed = True

    def _check_win(self):
        revealed_count = 0

        for row in self.tiles:
            for tile in row:
                if tile.revealed and tile.value != -1:
                    revealed_count += 1

        total_safe_tiles = self.height * self.width - self.bombs

        if revealed_count == total_safe_tiles:
            self.win = True



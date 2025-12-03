from board import BombBoard
from camera import Camera
import pygame
import os

# Pygame variables
pygame.init()
screen_size = (1280, 720)
screen = pygame.display.set_mode(screen_size)
clock = pygame.time.Clock()
running = True
game_state = "menu"

music = pygame.mixer.music.load("syfy_cave.mp3")
pygame.mixer.music.play(-1)

start_time = 0
elapsed_time = 0
current_time = 0

text_font = pygame.font.SysFont("Arial", 30)
font_big = pygame.font.SysFont("Arial", 48)

camera = Camera()

# Functions
def load_tiles_images(folder_path):
    images = {}

    for filename in os.listdir(folder_path):
        if not filename.endswith(".png"):
            continue

        # Removes tile_ and .png from the name
        name = filename[:-4]
        name = name[5:]

        key = int(name) if name.isdigit() else name

        # Load
        img = pygame.image.load(os.path.join(folder_path, filename)).convert_alpha()

        img = pygame.transform.scale(img, (img.get_width()*3, img.get_height()*3))


        if key in images:
            raise ValueError(f"Duplicate tile key detected: {key}")
        
        images[key] = img

    return images

def setup_board(width, height, bombs):
    base_x = int((screen_size[0] - (width * tile_size))/2)
    base_y = int((screen_size[1] - (height * tile_size))/2)
    board = BombBoard(width, height, bombs, tile_size, base_x, base_y, images)
    return board

images = load_tiles_images("sprites")
tile_size = images[0].get_width()

def handle_menu():
    global running, board, game_state, start_time

    screen.fill("black")

    title = font_big.render("MINESWEEPER", True, "white")
    screen.blit(title, (screen_size[0]//2 - title.get_width()//2, 100))

    easy_btn = pygame.Rect(screen_size[0]//2 - 100, 250, 200, 60)
    medium_btn = pygame.Rect(screen_size[0]//2 - 100, 330, 200, 60)
    hard_btn = pygame.Rect(screen_size[0]//2 - 100, 410, 200, 60)

    pygame.draw.rect(screen, (255, 255, 255), easy_btn)
    pygame.draw.rect(screen, (255, 255, 255), medium_btn)
    pygame.draw.rect(screen, (255, 255, 255), hard_btn)

    easy_t = text_font.render("Easy", True, "black")
    medium_t = text_font.render("Medium", True, "black")
    hard_t = text_font.render("Hard", True, "black")

    screen.blit(easy_t, (easy_btn.centerx - easy_t.get_width()//2,
                        easy_btn.centery - easy_t.get_height()//2))
    
    screen.blit(medium_t, (medium_btn.centerx - medium_t.get_width()//2,
                        medium_btn.centery - medium_t.get_height()//2))
    
    screen.blit(hard_t, (hard_btn.centerx - hard_t.get_width()//2,
                        hard_btn.centery - hard_t.get_height()//2))


    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.MOUSEBUTTONDOWN:
            x, y = event.pos

            if easy_btn.collidepoint(x, y):
                board = setup_board(8, 8, 10)
                start_time = pygame.time.get_ticks()
                game_state = "playing"

            if medium_btn.collidepoint(x, y):
                board = setup_board(16, 16, 40)
                start_time = pygame.time.get_ticks()
                game_state = "playing"

            if hard_btn.collidepoint(x, y):
                board = setup_board(30, 16, 99)
                start_time = pygame.time.get_ticks()
                game_state = "playing"

def screen_to_world(camera: Camera, pos):
    sx, sy = pos
    wx = sx / camera.zoom + camera.x
    wy = sy / camera.zoom + camera.y
    return wx, wy

dragging = False
last_pos = None

def handle_game():
    global game_state, running, board, elapsed_time, current_time
    global dragging, last_pos

    screen.fill("black")
    board.draw(screen, camera)
    board.display_stats(surface=screen, font=text_font, elapsed_time=elapsed_time)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.MOUSEBUTTONDOWN:
            world_pos = screen_to_world(camera, event.pos)
            board.handle_click(world_pos, event.button)

        if event.type == pygame.MOUSEWHEEL:
            old_zoom = camera.zoom
            camera.zoom *= 1.1 ** event.y
            camera.zoom = max(0.3, min(4.0, camera.zoom))

            mx, my = pygame.mouse.get_pos()
            camera.x = (camera.x + mx / old_zoom) - (mx / camera.zoom)
            camera.y = (camera.y + my / old_zoom) - (my / camera.zoom)

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 2:
            dragging = True
            last_pos = event.pos

        if event.type == pygame.MOUSEBUTTONUP and event.button == 2:
            dragging = False
        
        if event.type == pygame.MOUSEMOTION and dragging:
            mx, my = event.pos
            lx, ly = last_pos
            dx = (lx - mx) / camera.zoom
            dy = (ly - my) / camera.zoom
            camera.x += dx
            camera.y += dy
            last_pos = event.pos

    wx, wy = screen_to_world(camera, pygame.mouse.get_pos())
    for row in board.tiles:
        for tile in row:
            if tile.rect.collidepoint((wx, wy)):
                screen_rect = camera.apply(tile.rect)
                pygame.draw.rect(screen, "yellow", screen_rect, 2)

    if board.game_over or board.win:
        game_state = "game_end"
        current_time = elapsed_time

def handle_end():
    global running, game_state, start_time

    screen.fill("black")
    board.draw(screen, camera)
    board.display_stats(surface=screen, font=text_font, elapsed_time=current_time)

    end_t = None
    if board.game_over:
        board._reveal_all_bombs()
        end_t = font_big.render("Game Over!", True, "black")
    elif board.win:
        end_t = font_big.render("You Won!", True, "black")

    s = pygame.Surface((300, 400))
    s.set_alpha(128)
    s.fill((255, 255, 255))
    screen.blit(s, (screen_size[0]//2 - 150, screen_size[1]//2 - 200))
    screen.blit(end_t, (screen_size[0]//2 - end_t.get_width()//2
                        , screen_size[1]//2 - end_t.get_height()//2 - 100))
    
    menu_btn = pygame.Rect(screen_size[0]//2 - 100, screen_size[1]//2, 200, 60)
    quit_btn = pygame.Rect(screen_size[0]//2 - 100, screen_size[1]//2 + 70, 200, 60)

    menu_t = text_font.render("Menu", True, "black")
    quit_t = text_font.render("Quit", True, "black")

    pygame.draw.rect(screen, (255, 255, 255), menu_btn)
    pygame.draw.rect(screen, (0, 0, 0), menu_btn, 2)
    pygame.draw.rect(screen, (255, 255, 255), quit_btn)
    pygame.draw.rect(screen, (0, 0, 0), quit_btn, 2)

    screen.blit(menu_t, (menu_btn.centerx - menu_t.get_width()//2,
                         menu_btn.centery - menu_t.get_height()//2))
    
    screen.blit(quit_t, (quit_btn.centerx - quit_t.get_width()//2,
                         quit_btn.centery - quit_t.get_height()//2))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.MOUSEBUTTONDOWN:
            x, y = event.pos
            if menu_btn.collidepoint(x, y):
                game_state = "menu"
                start_time = 0
            if quit_btn.collidepoint(x, y):
                running = False


while running:

    if game_state == "menu":
        handle_menu()

    elif game_state == "playing":
        elapsed_time = (pygame.time.get_ticks() - start_time) // 1000
        handle_game()

    elif game_state == "game_end":
        handle_end()

    pygame.display.flip()
    clock.tick(60)
pygame.quit()

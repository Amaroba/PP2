import pygame

font = None

def get_font():
    global font
    if font is None:
        font = pygame.font.SysFont(None, 28)
    return font


def draw_text(screen, text, x, y):
    f = get_font()
    img = f.render(text, True, (255, 255, 255))
    screen.blit(img, (x, y))


def menu(screen):
    screen.fill((0, 0, 0))
    draw_text(screen, "R - Play", 100, 200)
    draw_text(screen, "L - Leaderboard", 100, 240)
    draw_text(screen, "Q - Quit", 100, 280)


def game_over(screen, score):
    screen.fill((0, 0, 0))
    draw_text(screen, f"Game Over: {score}", 100, 200)
    draw_text(screen, "R - Restart", 100, 240)
    draw_text(screen, "M - Menu", 100, 280)
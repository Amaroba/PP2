import pygame
import sys
from datetime import datetime
from tools import *

pygame.init()

WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
canvas = pygame.Surface((WIDTH, HEIGHT))
canvas.fill((255, 255, 255))

clock = pygame.time.Clock()

color = (0, 0, 0)
tool = PENCIL
brush_size = brush_sizes[1]

drawing = False
last_pos = None
start_pos = None

font = pygame.font.SysFont(None, 24)
text_input = ""
text_active = False
text_pos = (0, 0)


def flood_fill(surface, x, y, new_color):
    target_color = surface.get_at((x, y))
    if target_color == new_color:
        return

    stack = [(x, y)]
    while stack:
        px, py = stack.pop()

        if px < 0 or px >= WIDTH or py < 0 or py >= HEIGHT:
            continue

        if surface.get_at((px, py)) != target_color:
            continue

        surface.set_at((px, py), new_color)

        stack.append((px + 1, py))
        stack.append((px - 1, py))
        stack.append((px, py + 1))
        stack.append((px, py - 1))


while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        if event.type == pygame.KEYDOWN:

            if event.key == pygame.K_1:
                brush_size = brush_sizes[1]
            if event.key == pygame.K_2:
                brush_size = brush_sizes[2]
            if event.key == pygame.K_3:
                brush_size = brush_sizes[3]

            if event.key == pygame.K_p:
                tool = PENCIL
            if event.key == pygame.K_l:
                tool = LINE
            if event.key == pygame.K_f:
                tool = FILL
            if event.key == pygame.K_t:
                tool = TEXT

            if event.key == pygame.K_s and pygame.key.get_mods() & pygame.KMOD_CTRL:
                filename = datetime.now().strftime("%Y%m%d_%H%M%S.png")
                pygame.image.save(canvas, filename)
                print("Saved:", filename)

            if tool == TEXT and text_active:
                if event.key == pygame.K_RETURN:
                    text_surface = font.render(text_input, True, color)
                    canvas.blit(text_surface, text_pos)
                    text_input = ""
                    text_active = False

                elif event.key == pygame.K_ESCAPE:
                    text_input = ""
                    text_active = False

                else:
                    text_input += event.unicode

        if event.type == pygame.MOUSEBUTTONDOWN:
            drawing = True
            start_pos = event.pos

            if tool == FILL:
                flood_fill(canvas, event.pos[0], event.pos[1], color)

            elif tool == TEXT:
                text_active = True
                text_pos = event.pos
                text_input = ""

        if event.type == pygame.MOUSEBUTTONUP:
            drawing = False

            if tool == LINE:
                pygame.draw.line(canvas, color, start_pos, event.pos, brush_size)

        if event.type == pygame.MOUSEMOTION:
            if drawing and tool == PENCIL:
                if last_pos:
                    pygame.draw.line(canvas, color, last_pos, event.pos, brush_size)
                last_pos = event.pos

    screen.fill((200, 200, 200))
    screen.blit(canvas, (0, 0))

    if drawing and tool == LINE:
        pygame.draw.line(screen, color, start_pos, pygame.mouse.get_pos(), brush_size)

    if text_active:
        preview = font.render(text_input, True, color)
        screen.blit(preview, text_pos)

    tool_text = font.render(f"Tool: {tool} | Size: {brush_size}", True, (0, 0, 0))
    screen.blit(tool_text, (10, 10))

    pygame.display.flip()
    clock.tick(60)
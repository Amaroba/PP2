import pygame
from clock import MickeyClock

pygame.init()
screen = pygame.display.set_mode((600, 600))
clock = pygame.time.Clock()

mickey = MickeyClock(screen)

running = True
while running:
    screen.fill((255, 255, 255))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    mickey.draw()

    pygame.display.flip()
    clock.tick(1)  # update every second

pygame.quit()
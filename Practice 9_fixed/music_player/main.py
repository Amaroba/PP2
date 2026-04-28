import pygame
from player import MusicPlayer

pygame.init()
screen = pygame.display.set_mode((600, 400))
font = pygame.font.Font(None, 36)

player = MusicPlayer()

running = True
while running:
    screen.fill((30, 30, 30))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_p:
                player.play()
            elif event.key == pygame.K_s:
                player.stop()
            elif event.key == pygame.K_n:
                player.next()
            elif event.key == pygame.K_b:
                player.prev()

    text = font.render(f"Track: {player.current+1}", True, (255,255,255))
    screen.blit(text, (50, 50))

    pygame.display.flip()

pygame.quit()
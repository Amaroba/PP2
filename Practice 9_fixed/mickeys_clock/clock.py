import pygame
import datetime

class MickeyClock:
    def __init__(self, screen):
        self.screen = screen
        self.center = (300, 300)

        # Load image
        self.hand_img = pygame.image.load("images/mickey_hand.png")
        self.hand_img = pygame.transform.scale(self.hand_img, (100, 100))

    def draw(self):
        now = datetime.datetime.now()
        sec = now.second
        minute = now.minute

        # Angles
        sec_angle = -sec * 6
        min_angle = -minute * 6

        # Rotate
        sec_hand = pygame.transform.rotate(self.hand_img, sec_angle)
        min_hand = pygame.transform.rotate(self.hand_img, min_angle)

        # Get rect centered
        sec_rect = sec_hand.get_rect(center=self.center)
        min_rect = min_hand.get_rect(center=self.center)

        # Draw
        self.screen.blit(min_hand, min_rect)
        self.screen.blit(sec_hand, sec_rect)
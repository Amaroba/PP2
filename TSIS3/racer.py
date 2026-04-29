import pygame
import random

def load_car(path, size=(40, 40)):
    img = pygame.image.load(path)
    return pygame.transform.scale(img, size)

def load_img(path, size=(25, 25)):
    img = pygame.image.load(path)
    return pygame.transform.scale(img, size)



WIDTH, HEIGHT = 400, 600

class Player:
    def __init__(self):
        self.x = WIDTH // 2
        self.y = HEIGHT - 80

        self.speed = 5
        self.base_speed = 5

        self.image = load_car("assets/player.png")

        #защита
        self.shield = False

        #буст
        self.power = None
        self.timer = 0

        # HP система
        self.hp = 2
        self.max_hp = 2

    def move(self, keys):
        if keys[pygame.K_LEFT]:
            self.x -= self.speed
        if keys[pygame.K_RIGHT]:
            self.x += self.speed

    def update(self):
        if self.timer > 0:
            self.timer -= 1
        else:
            self.speed = self.base_speed
            self.power = None


class Enemy:
    def __init__(self):
        self.x = random.randint(50, WIDTH-50)
        self.y = -50
        self.speed = random.randint(3, 6)
        self.image = pygame.image.load("assets/enemy.png")
        self.image = pygame.transform.scale(self.image, (40, 40))

    def update(self):
        self.y += self.speed


class PowerUp:
    def __init__(self):
        self.x = random.randint(50, 350)
        self.y = -50

        self.type = random.choice(["nitro", "shield", "repair"])

        self.image = load_img("assets/powerup.png")

        self.speed = 4 

    def update(self):
        self.y += 4

    def update(self):
        self.y += self.speed
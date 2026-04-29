import pygame
import sys
import random

from racer import Player, Enemy, PowerUp
from persistence import *
from ui import *

pygame.init()
pygame.font.init()

WIDTH, HEIGHT = 400, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()

leaderboard = load_json("leaderboard.json", [])

font = pygame.font.SysFont(None, 30)


def get_name():
    name = ""
    active = True

    while active:
        screen.fill((0, 0, 0))
        text = font.render("Enter name: " + name, True, (255, 255, 255))
        screen.blit(text, (50, 300))
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    active = False
                elif event.key == pygame.K_BACKSPACE:
                    name = name[:-1]
                else:
                    name += event.unicode

    return name


def game():
    player = Player()
    enemies = []
    powerups = []

    score = 0
    username = get_name()

    while True:
        screen.fill((30, 30, 30))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        # ---------- INPUT ----------
        keys = pygame.key.get_pressed()
        player.move(keys)
        player.update()

        # ---------- SPAWN ----------
        if random.random() < 0.02:
            enemies.append(Enemy())

        if random.random() < 0.005:
            powerups.append(PowerUp())

        # ---------- PLAYER ----------
        screen.blit(player.image, (player.x, player.y))

        # ---------- ENEMIES ----------
        for e in enemies[:]:
            e.update()
            screen.blit(e.image, (e.x, e.y))

            if e.y > HEIGHT:
                enemies.remove(e)

            # collision enemy
            if abs(player.x - e.x) < 30 and abs(player.y - e.y) < 30:
                enemies.remove(e)

                if player.shield:
                    player.shield = False
                else:
                    player.hp -= 1

                    if player.hp <= 0:
                        return score, username

        # ---------- POWERUPS ----------
        for p in powerups[:]:
            p.update()
            screen.blit(p.image, (p.x, p.y))

            # debug (видно тип бустера)
            draw_text(screen, p.type, p.x, p.y - 15)

            if p.y > HEIGHT:
                powerups.remove(p)

            # collision with player
            if abs(player.x - p.x) < 20 and abs(player.y - p.y) < 20:

                # 🚀 NITRO
                if p.type == "nitro":
                    player.speed = 10
                    player.power = "nitro"
                    player.timer = 180

                # 🛡 SHIELD
                elif p.type == "shield":
                    player.shield = True

                # 🛠 REPAIR (лечит HP)
                elif p.type == "repair":
                    score += 50
                    player.hp = min(player.max_hp, player.hp + 1)

                powerups.remove(p)

        # ---------- NITRO TIMER ----------
        if player.timer > 0:
            player.timer -= 1
        else:
            player.speed = 5
            player.power = None

        # ---------- SCORE ----------
        score += 1

        # ---------- UI ----------
        draw_text(screen, f"Score: {score}", 10, 10)
        draw_text(screen, f"HP: {player.hp}", 10, 40)

        if player.shield:
            draw_text(screen, "Shield ON", 10, 70)

        if player.power:
            draw_text(screen, f"Power: {player.power}", 10, 100)

        pygame.display.flip()
        clock.tick(60)

def save_score(score, name):
    leaderboard.append({"name": name, "score": score})
    leaderboard.sort(key=lambda x: x["score"], reverse=True)
    save_json("leaderboard.json", leaderboard)


def show_leaderboard():
    while True:
        screen.fill((0, 0, 0))

        y = 100
        for i, s in enumerate(leaderboard[:10]):
            draw_text(screen, f"{i+1}. {s['name']} {s['score']}", 100, y)
            y += 30

        draw_text(screen, "Press B to back", 100, 400)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_b:
                    return

        pygame.display.flip()


def main():
    while True:
        menu(screen)
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:

                if event.key == pygame.K_r:
                    score, name = game()
                    save_score(score, name)

                if event.key == pygame.K_l:
                    show_leaderboard()

                if event.key == pygame.K_q:
                    pygame.quit()
                    sys.exit()

        clock.tick(60)


main()
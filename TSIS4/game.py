from __future__ import annotations

import json
import random
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Optional

import pygame

from config import (
    BACKGROUND_COLOR,
    BASE_MOVE_DELAY_MS,
    BORDER_COLOR,
    CELL_SIZE,
    FOOD_COLOR,
    FOOD_PER_LEVEL,
    GRID_COLOR,
    GRID_HEIGHT,
    GRID_WIDTH,
    MAX_OBSTACLES_PER_LEVEL,
    NORMAL_FOOD_TTL_MS,
    OBSTACLE_COLOR,
    POISON_COLOR,
    POISON_RESPAWN_MS,
    POWER_UP_EFFECT_MS,
    POWER_UP_TTL_MS,
    TEXT_COLOR,
    WINDOW_HEIGHT,
    WINDOW_WIDTH,
)
from db import DatabaseManager


class ScreenState(Enum):
    MENU = "menu"
    GAME = "game"
    GAME_OVER = "game_over"
    LEADERBOARD = "leaderboard"
    SETTINGS = "settings"


class PowerUpType(Enum):
    SPEED = "speed"
    SLOW = "slow"
    SHIELD = "shield"


@dataclass
class Food:
    pos: tuple[int, int]
    points: int
    spawned_at: int
    ttl_ms: int


@dataclass
class PowerUp:
    pos: tuple[int, int]
    kind: PowerUpType
    spawned_at: int


class SnakeGame:
    def __init__(self) -> None:
        pygame.init()
        pygame.display.set_caption("TSIS 4 Snake Game")
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("arial", 24)
        self.small_font = pygame.font.SysFont("arial", 18)

        self.db = DatabaseManager()
        self.db.connect()

        self.settings_path = Path("settings.json")
        self.settings = self.load_settings()

        self.state = ScreenState.MENU
        self.running = True
        self.username = ""
        self.menu_error = ""

        self.leaderboard_rows = []
        self.personal_best = 0
        self.final_score = 0
        self.final_level = 1

        self.available_colors = [
            (0, 220, 120),
            (80, 190, 255),
            (255, 170, 60),
            (255, 90, 150),
            (180, 120, 255),
        ]
        if tuple(self.settings["snake_color"]) not in self.available_colors:
            self.available_colors.append(tuple(self.settings["snake_color"]))

        self.reset_game()

    def default_settings(self) -> dict:
        return {
            "snake_color": [0, 220, 120],
            "grid_overlay": True,
            "sound": False,
        }

    def load_settings(self) -> dict:
        if not self.settings_path.exists():
            defaults = self.default_settings()
            self.settings_path.write_text(json.dumps(defaults, indent=2), encoding="utf-8")
            return defaults
        try:
            raw = json.loads(self.settings_path.read_text(encoding="utf-8"))
            defaults = self.default_settings()
            defaults.update(raw)
            return defaults
        except Exception:
            return self.default_settings()

    def save_settings(self) -> None:
        self.settings_path.write_text(json.dumps(self.settings, indent=2), encoding="utf-8")

    def reset_game(self) -> None:
        center = (GRID_WIDTH // 2, GRID_HEIGHT // 2)
        self.snake = [center, (center[0] - 1, center[1]), (center[0] - 2, center[1])]
        self.direction = (1, 0)
        self.next_direction = (1, 0)
        self.score = 0
        self.level = 1
        self.food_eaten = 0
        self.shield_active = False
        self.active_speed_modifier = 1.0
        self.active_power_effect_until = 0
        self.obstacles: set[tuple[int, int]] = set()

        now = pygame.time.get_ticks()
        self.normal_food = self.spawn_normal_food(now)
        self.poison_food = self.spawn_poison_food()
        self.last_poison_spawn = now
        self.field_power_up: Optional[PowerUp] = None
        self.last_power_spawn = now
        self.game_over_processed = False
        self.last_move_at = now

    def random_free_cell(self) -> tuple[int, int]:
        occupied = set(self.snake) | self.obstacles
        normal_food = getattr(self, "normal_food", None)
        poison_food = getattr(self, "poison_food", None)
        field_power_up = getattr(self, "field_power_up", None)

        if normal_food:
            occupied.add(normal_food.pos)
        if poison_food:
            occupied.add(poison_food)
        if field_power_up:
            occupied.add(field_power_up.pos)

        while True:
            cell = (random.randint(1, GRID_WIDTH - 2), random.randint(1, GRID_HEIGHT - 2))
            if cell not in occupied:
                return cell

    def spawn_normal_food(self, now: int) -> Food:
        points = random.choice([1, 2, 3])
        return Food(pos=self.random_free_cell(), points=points, spawned_at=now, ttl_ms=NORMAL_FOOD_TTL_MS)

    def spawn_poison_food(self) -> tuple[int, int]:
        return self.random_free_cell()

    def spawn_power_up(self, now: int) -> PowerUp:
        kind = random.choice(list(PowerUpType))
        return PowerUp(pos=self.random_free_cell(), kind=kind, spawned_at=now)

    def current_move_delay(self) -> int:
        level_factor = max(70, BASE_MOVE_DELAY_MS - (self.level - 1) * 12)
        return max(40, int(level_factor * self.active_speed_modifier))

    def neighbors(self, cell: tuple[int, int]) -> list[tuple[int, int]]:
        x, y = cell
        return [(x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)]

    def create_level_obstacles(self) -> None:
        if self.level < 3:
            self.obstacles = set()
            return

        target_count = min(MAX_OBSTACLES_PER_LEVEL, 8 + self.level * 4)
        head = self.snake[0]
        safe_ring = set(self.neighbors(head)) | {head}

        new_obstacles: set[tuple[int, int]] = set()
        attempts = 0
        while len(new_obstacles) < target_count and attempts < target_count * 25:
            attempts += 1
            cell = (random.randint(1, GRID_WIDTH - 2), random.randint(1, GRID_HEIGHT - 2))
            if cell in safe_ring or cell in self.snake or cell in new_obstacles:
                continue
            new_obstacles.add(cell)

        open_neighbors = 0
        for n in self.neighbors(head):
            if n[0] <= 0 or n[0] >= GRID_WIDTH - 1 or n[1] <= 0 or n[1] >= GRID_HEIGHT - 1:
                continue
            if n in new_obstacles:
                continue
            open_neighbors += 1
        if open_neighbors == 0:
            for n in self.neighbors(head):
                if n in new_obstacles:
                    new_obstacles.remove(n)
                    break

        self.obstacles = new_obstacles

    def activate_power(self, power: PowerUp, now: int) -> None:
        if power.kind == PowerUpType.SPEED:
            self.active_speed_modifier = 0.65
            self.active_power_effect_until = now + POWER_UP_EFFECT_MS
        elif power.kind == PowerUpType.SLOW:
            self.active_speed_modifier = 1.5
            self.active_power_effect_until = now + POWER_UP_EFFECT_MS
        elif power.kind == PowerUpType.SHIELD:
            self.shield_active = True

    def update_power_timers(self, now: int) -> None:
        if self.active_power_effect_until and now >= self.active_power_effect_until:
            self.active_speed_modifier = 1.0
            self.active_power_effect_until = 0

        if self.field_power_up and now - self.field_power_up.spawned_at >= POWER_UP_TTL_MS:
            self.field_power_up = None

        if self.field_power_up is None and now - self.last_power_spawn >= 3000:
            self.field_power_up = self.spawn_power_up(now)
            self.last_power_spawn = now

    def handle_collision(self, new_head: tuple[int, int]) -> bool:
        hit_border = (
            new_head[0] <= 0
            or new_head[0] >= GRID_WIDTH - 1
            or new_head[1] <= 0
            or new_head[1] >= GRID_HEIGHT - 1
        )
        hit_self = new_head in self.snake
        hit_obstacle = new_head in self.obstacles
        if hit_border or hit_self or hit_obstacle:
            if self.shield_active and (hit_border or hit_self):
                self.shield_active = False
                return False
            return True
        return False

    def process_game_over(self) -> None:
        if self.game_over_processed:
            return
        self.game_over_processed = True
        self.final_score = self.score
        self.final_level = self.level
        if self.username and self.db.available:
            self.db.save_game_session(self.username, self.final_score, self.final_level)
            self.personal_best = max(self.personal_best, self.db.get_personal_best(self.username))

    def advance_level_if_needed(self) -> None:
        expected_level = 1 + self.food_eaten // FOOD_PER_LEVEL
        if expected_level > self.level:
            self.level = expected_level
            self.create_level_obstacles()
            now = pygame.time.get_ticks()
            self.normal_food = self.spawn_normal_food(now)
            self.poison_food = self.spawn_poison_food()
            self.field_power_up = None

    def update_game(self) -> None:
        now = pygame.time.get_ticks()
        if now - self.last_move_at < self.current_move_delay():
            return
        self.last_move_at = now

        self.update_power_timers(now)

        if now - self.normal_food.spawned_at >= self.normal_food.ttl_ms:
            self.normal_food = self.spawn_normal_food(now)

        if self.poison_food is None and now - self.last_poison_spawn >= POISON_RESPAWN_MS:
            self.poison_food = self.spawn_poison_food()
            self.last_poison_spawn = now

        self.direction = self.next_direction
        new_head = (self.snake[0][0] + self.direction[0], self.snake[0][1] + self.direction[1])
        if self.handle_collision(new_head):
            self.process_game_over()
            self.state = ScreenState.GAME_OVER
            return

        self.snake.insert(0, new_head)

        ate_normal = new_head == self.normal_food.pos
        ate_poison = self.poison_food is not None and new_head == self.poison_food
        ate_power = self.field_power_up and new_head == self.field_power_up.pos

        if ate_normal:
            self.score += self.normal_food.points
            self.food_eaten += 1
            self.normal_food = self.spawn_normal_food(now)
            self.advance_level_if_needed()
        else:
            self.snake.pop()

        if ate_poison:
            self.poison_food = None
            self.last_poison_spawn = now
            for _ in range(2):
                if self.snake:
                    self.snake.pop()
            if len(self.snake) <= 1:
                self.process_game_over()
                self.state = ScreenState.GAME_OVER
                return

        if ate_power:
            self.activate_power(self.field_power_up, now)
            self.field_power_up = None
            self.last_power_spawn = now

    def draw_text_center(self, text: str, y: int, color=TEXT_COLOR, font=None) -> None:
        used_font = font or self.font
        surface = used_font.render(text, True, color)
        rect = surface.get_rect(center=(WINDOW_WIDTH // 2, y))
        self.screen.blit(surface, rect)

    def draw_button(self, rect: pygame.Rect, label: str) -> None:
        pygame.draw.rect(self.screen, (55, 65, 95), rect, border_radius=8)
        pygame.draw.rect(self.screen, (140, 155, 220), rect, 2, border_radius=8)
        text_surf = self.small_font.render(label, True, TEXT_COLOR)
        self.screen.blit(text_surf, text_surf.get_rect(center=rect.center))

    def menu_buttons(self) -> dict[str, pygame.Rect]:
        base_x = WINDOW_WIDTH // 2 - 120
        base_y = 280
        w, h = 240, 44
        gap = 12
        return {
            "play": pygame.Rect(base_x, base_y + (h + gap) * 0, w, h),
            "leaderboard": pygame.Rect(base_x, base_y + (h + gap) * 1, w, h),
            "settings": pygame.Rect(base_x, base_y + (h + gap) * 2, w, h),
            "quit": pygame.Rect(base_x, base_y + (h + gap) * 3, w, h),
        }

    def draw_menu(self) -> None:
        self.screen.fill(BACKGROUND_COLOR)
        self.draw_text_center("Snake Game TSIS 4", 90)
        self.draw_text_center("Enter username:", 145, font=self.small_font)

        input_rect = pygame.Rect(WINDOW_WIDTH // 2 - 170, 170, 340, 42)
        pygame.draw.rect(self.screen, (35, 35, 45), input_rect, border_radius=6)
        pygame.draw.rect(self.screen, (120, 130, 200), input_rect, 2, border_radius=6)
        username_surface = self.font.render(self.username or "_", True, TEXT_COLOR)
        self.screen.blit(username_surface, (input_rect.x + 10, input_rect.y + 6))

        if self.menu_error:
            err = self.small_font.render(self.menu_error, True, (230, 90, 90))
            self.screen.blit(err, (WINDOW_WIDTH // 2 - err.get_width() // 2, 218))

        for key, rect in self.menu_buttons().items():
            self.draw_button(rect, key.capitalize())

        hint = self.small_font.render("Type username and click Play", True, (170, 180, 210))
        self.screen.blit(hint, (WINDOW_WIDTH // 2 - hint.get_width() // 2, 520))

    def draw_grid(self) -> None:
        if not self.settings["grid_overlay"]:
            return
        for x in range(0, WINDOW_WIDTH, CELL_SIZE):
            pygame.draw.line(self.screen, GRID_COLOR, (x, 0), (x, WINDOW_HEIGHT))
        for y in range(0, WINDOW_HEIGHT, CELL_SIZE):
            pygame.draw.line(self.screen, GRID_COLOR, (0, y), (WINDOW_WIDTH, y))

    def draw_game(self) -> None:
        self.screen.fill(BACKGROUND_COLOR)
        self.draw_grid()

        pygame.draw.rect(self.screen, BORDER_COLOR, (0, 0, WINDOW_WIDTH, WINDOW_HEIGHT), 3)

        for block in self.obstacles:
            rect = pygame.Rect(block[0] * CELL_SIZE, block[1] * CELL_SIZE, CELL_SIZE, CELL_SIZE)
            pygame.draw.rect(self.screen, OBSTACLE_COLOR, rect)

        for index, segment in enumerate(self.snake):
            rect = pygame.Rect(segment[0] * CELL_SIZE, segment[1] * CELL_SIZE, CELL_SIZE, CELL_SIZE)
            color = tuple(self.settings["snake_color"]) if index == 0 else tuple(
                max(0, c - 35) for c in self.settings["snake_color"]
            )
            pygame.draw.rect(self.screen, color, rect)

        normal_rect = pygame.Rect(
            self.normal_food.pos[0] * CELL_SIZE,
            self.normal_food.pos[1] * CELL_SIZE,
            CELL_SIZE,
            CELL_SIZE,
        )
        pygame.draw.rect(self.screen, FOOD_COLOR, normal_rect)

        if self.poison_food is not None:
            poison_rect = pygame.Rect(
                self.poison_food[0] * CELL_SIZE,
                self.poison_food[1] * CELL_SIZE,
                CELL_SIZE,
                CELL_SIZE,
            )
            pygame.draw.rect(self.screen, POISON_COLOR, poison_rect)

        if self.field_power_up:
            p = self.field_power_up
            power_color = {
                PowerUpType.SPEED: (90, 180, 255),
                PowerUpType.SLOW: (80, 110, 220),
                PowerUpType.SHIELD: (255, 215, 70),
            }[p.kind]
            rect = pygame.Rect(p.pos[0] * CELL_SIZE, p.pos[1] * CELL_SIZE, CELL_SIZE, CELL_SIZE)
            pygame.draw.rect(self.screen, power_color, rect)

        status = f"Score: {self.score}   Level: {self.level}   Personal best: {self.personal_best}"
        status_surface = self.small_font.render(status, True, TEXT_COLOR)
        self.screen.blit(status_surface, (12, 10))

        effect_text = "Shield: ON" if self.shield_active else ""
        if self.active_power_effect_until:
            sec_left = max(0, (self.active_power_effect_until - pygame.time.get_ticks()) // 1000)
            effect_text = f"Temp effect: {sec_left}s"
        if effect_text:
            effect_surface = self.small_font.render(effect_text, True, (245, 210, 120))
            self.screen.blit(effect_surface, (12, 34))

    def game_over_buttons(self) -> dict[str, pygame.Rect]:
        w, h = 220, 44
        return {
            "retry": pygame.Rect(WINDOW_WIDTH // 2 - 240, 390, w, h),
            "menu": pygame.Rect(WINDOW_WIDTH // 2 + 20, 390, w, h),
        }

    def draw_game_over(self) -> None:
        self.screen.fill(BACKGROUND_COLOR)
        self.draw_text_center("Game Over", 170, color=(240, 90, 90))
        self.draw_text_center(f"Final score: {self.final_score}", 230, font=self.small_font)
        self.draw_text_center(f"Level reached: {self.final_level}", 262, font=self.small_font)
        self.draw_text_center(f"Personal best: {self.personal_best}", 294, font=self.small_font)

        buttons = self.game_over_buttons()
        self.draw_button(buttons["retry"], "Retry")
        self.draw_button(buttons["menu"], "Main Menu")

    def draw_leaderboard(self) -> None:
        self.screen.fill(BACKGROUND_COLOR)
        self.draw_text_center("Top 10 Leaderboard", 70)

        headers = ["#", "Username", "Score", "Level", "Date"]
        header_x = [120, 220, 460, 580, 700]
        for i, title in enumerate(headers):
            label = self.small_font.render(title, True, (170, 190, 250))
            self.screen.blit(label, (header_x[i], 120))

        y = 160
        if not self.leaderboard_rows:
            text = self.small_font.render("No entries yet (or DB unavailable)", True, TEXT_COLOR)
            self.screen.blit(text, (WINDOW_WIDTH // 2 - text.get_width() // 2, y))
        else:
            for idx, row in enumerate(self.leaderboard_rows, start=1):
                items = [
                    str(idx),
                    row.username,
                    str(row.score),
                    str(row.level_reached),
                    row.played_at.strftime("%Y-%m-%d"),
                ]
                for i, val in enumerate(items):
                    cell = self.small_font.render(val, True, TEXT_COLOR)
                    self.screen.blit(cell, (header_x[i], y))
                y += 36

        back_rect = pygame.Rect(WINDOW_WIDTH // 2 - 90, 620, 180, 44)
        self.draw_button(back_rect, "Back")
        self.leaderboard_back_button = back_rect

    def settings_buttons(self) -> dict[str, pygame.Rect]:
        return {
            "toggle_grid": pygame.Rect(220, 210, 460, 44),
            "toggle_sound": pygame.Rect(220, 280, 460, 44),
            "snake_color": pygame.Rect(220, 350, 460, 44),
            "save_back": pygame.Rect(WINDOW_WIDTH // 2 - 110, 450, 220, 44),
        }

    def draw_settings(self) -> None:
        self.screen.fill(BACKGROUND_COLOR)
        self.draw_text_center("Settings", 100)

        buttons = self.settings_buttons()
        self.draw_button(buttons["toggle_grid"], f"Grid: {'ON' if self.settings['grid_overlay'] else 'OFF'}")
        self.draw_button(buttons["toggle_sound"], f"Sound: {'ON' if self.settings['sound'] else 'OFF'}")
        self.draw_button(buttons["snake_color"], "Snake color: click to cycle")
        self.draw_button(buttons["save_back"], "Save & Back")

        color_preview = pygame.Rect(WINDOW_WIDTH // 2 - 40, 405, 80, 26)
        pygame.draw.rect(self.screen, tuple(self.settings["snake_color"]), color_preview)
        pygame.draw.rect(self.screen, (200, 200, 220), color_preview, 2)

    def handle_menu_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_BACKSPACE:
                self.username = self.username[:-1]
            elif event.key == pygame.K_RETURN:
                self.start_game_from_menu()
            elif event.unicode.isprintable() and len(self.username) < 20:
                self.username += event.unicode
            return

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            pos = event.pos
            buttons = self.menu_buttons()
            if buttons["play"].collidepoint(pos):
                self.start_game_from_menu()
            elif buttons["leaderboard"].collidepoint(pos):
                self.leaderboard_rows = self.db.get_top_10() if self.db.available else []
                self.state = ScreenState.LEADERBOARD
            elif buttons["settings"].collidepoint(pos):
                self.state = ScreenState.SETTINGS
            elif buttons["quit"].collidepoint(pos):
                self.running = False

    def start_game_from_menu(self) -> None:
        if not self.username.strip():
            self.menu_error = "Username is required."
            return
        self.menu_error = ""
        self.reset_game()
        self.personal_best = self.db.get_personal_best(self.username.strip()) if self.db.available else 0
        self.username = self.username.strip()
        self.state = ScreenState.GAME

    def handle_game_event(self, event: pygame.event.Event) -> None:
        if event.type != pygame.KEYDOWN:
            return
        if event.key == pygame.K_ESCAPE:
            self.state = ScreenState.MENU
            return

        requested = self.direction
        if event.key in (pygame.K_UP, pygame.K_w):
            requested = (0, -1)
        elif event.key in (pygame.K_DOWN, pygame.K_s):
            requested = (0, 1)
        elif event.key in (pygame.K_LEFT, pygame.K_a):
            requested = (-1, 0)
        elif event.key in (pygame.K_RIGHT, pygame.K_d):
            requested = (1, 0)

        if requested != (-self.direction[0], -self.direction[1]):
            self.next_direction = requested

    def handle_game_over_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            pos = event.pos
            buttons = self.game_over_buttons()
            if buttons["retry"].collidepoint(pos):
                self.reset_game()
                self.state = ScreenState.GAME
            elif buttons["menu"].collidepoint(pos):
                self.state = ScreenState.MENU

    def handle_leaderboard_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.leaderboard_back_button.collidepoint(event.pos):
                self.state = ScreenState.MENU

    def handle_settings_event(self, event: pygame.event.Event) -> None:
        if event.type != pygame.MOUSEBUTTONDOWN or event.button != 1:
            return

        pos = event.pos
        buttons = self.settings_buttons()
        if buttons["toggle_grid"].collidepoint(pos):
            self.settings["grid_overlay"] = not self.settings["grid_overlay"]
        elif buttons["toggle_sound"].collidepoint(pos):
            self.settings["sound"] = not self.settings["sound"]
        elif buttons["snake_color"].collidepoint(pos):
            current = tuple(self.settings["snake_color"])
            idx = self.available_colors.index(current) if current in self.available_colors else 0
            next_idx = (idx + 1) % len(self.available_colors)
            self.settings["snake_color"] = list(self.available_colors[next_idx])
        elif buttons["save_back"].collidepoint(pos):
            self.save_settings()
            self.state = ScreenState.MENU

    def handle_events(self) -> None:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                continue
            if self.state == ScreenState.MENU:
                self.handle_menu_event(event)
            elif self.state == ScreenState.GAME:
                self.handle_game_event(event)
            elif self.state == ScreenState.GAME_OVER:
                self.handle_game_over_event(event)
            elif self.state == ScreenState.LEADERBOARD:
                self.handle_leaderboard_event(event)
            elif self.state == ScreenState.SETTINGS:
                self.handle_settings_event(event)

    def render(self) -> None:
        if self.state == ScreenState.MENU:
            self.draw_menu()
        elif self.state == ScreenState.GAME:
            self.draw_game()
        elif self.state == ScreenState.GAME_OVER:
            self.draw_game_over()
        elif self.state == ScreenState.LEADERBOARD:
            self.draw_leaderboard()
        elif self.state == ScreenState.SETTINGS:
            self.draw_settings()
        pygame.display.flip()

    def run(self) -> None:
        while self.running:
            self.handle_events()
            if self.state == ScreenState.GAME:
                self.update_game()
            self.render()
            self.clock.tick(60)
        pygame.quit()

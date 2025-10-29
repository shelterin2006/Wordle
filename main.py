import pygame
import math
import random
import json

pygame.init()
pygame.font.init()
SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 800
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (106, 170, 100)
YELLOW = (201, 180, 88)
LIGHT_GRAY = (211, 211, 211)
DARK_GRAY = (120, 124, 126)
MID_GRAY = (119, 119, 119)
bg_image = pygame.image.load('background_image.jpg')
LETTER_FONT = pygame.font.Font("font/Poppins-Regular.ttf", size=50)
NOTIFICATION_FONT = pygame.font.Font("font/Helvetica.ttf", size=27)
MESSAGE_FONT = pygame.font.Font("font/Helvetica.ttf", size=40)
SMALL_MESSAGE_FONT = pygame.font.Font("font/Helvetica.ttf", size=20)
UI_FONT = pygame.font.Font("font/Helvetica.ttf", size=22)
is_flipping_row = False
WORD_LENGTH = 5
MAX_GUESSES = 6
MAX_GACHA_SPINS = 4
SQUARE_SIZE = 75
CORNER_RADIUS = 8
SQUARE_MARGIN = 10
GRID_WIDTH = (WORD_LENGTH * SQUARE_SIZE) + ((WORD_LENGTH - 1) * SQUARE_MARGIN)
GRID_TOP_MARGIN = 150
PLAYER_GRID_LEFT_MARGIN = (SCREEN_WIDTH / 2 - GRID_WIDTH) // 2
GACHA_GRID_LEFT_MARGIN = SCREEN_WIDTH / 2 + (SCREEN_WIDTH / 2 - GRID_WIDTH) // 2

WORD_LIST = json.loads(open("wordle.json").read())
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Wordle")


def get_random_word():
    return random.choice(WORD_LIST)

def get_feedback(guess, secret_word):
    guess = guess.lower()
    secret_word = secret_word.lower()
    feedback = [DARK_GRAY] * WORD_LENGTH
    secret_counts = {}
    for char in secret_word:
        secret_counts[char] = secret_counts.get(char, 0) + 1
    for i in range(WORD_LENGTH):
        if guess[i] == secret_word[i]:
            feedback[i] = GREEN
            secret_counts[guess[i]] -= 1
    for i in range(WORD_LENGTH):
        if feedback[i] != GREEN:
            char = guess[i]
            if char in secret_counts and secret_counts[char] > 0:
                feedback[i] = YELLOW
                secret_counts[char] -= 1
    return feedback


class Tile:
    def __init__(self, letter, x, y):
        self.shake = None
        self.pop = None
        self.colors = None
        self.flip = None
        self.letter = letter.upper()
        self.x = x
        self.y = y
        self.rect = pygame.Rect(self.x, self.y, SQUARE_SIZE, SQUARE_SIZE)
        self.reset()

    def get_letter(self):
        return self.letter

    def set_letter(self, letter):
        self.letter = letter.upper()
        self.colors["border"] = LIGHT_GRAY if self.letter == "" else MID_GRAY

    def reset(self):
        self.letter = ""
        self.colors = {"bg": WHITE, "text": BLACK, "border": LIGHT_GRAY}
        self.flip = {"is_active": False, "angle": 0, "speed": 700, "delay": 0, "target_color": None}
        self.pop = {"is_active": False, "scale": 1.0, "speed": 0.1, "direction": 1, "max_scale": 1.15}
        self.shake = {"is_active": False, "timer": 0, "offset": 0.0, "magnitude": 5, "speed": 50}

    def start_shake(self):
        if not self.flip["is_active"]: self.shake["is_active"] = True; self.shake["timer"] = 0.4

    def start_flip(self, target_color, delay):
        self.flip["is_active"] = True
        self.flip["target_color"] = target_color
        self.flip["delay"] = delay

    def start_popping(self):
        if not self.pop["is_active"]: self.pop["is_active"] = True; self.pop["scale"] = 1.0; self.pop["direction"] = 1

    def update(self, dt):
        self.upShake(dt); self.upPop(dt); self.upFlip(dt)

    def upShake(self, dt):
        if self.shake["is_active"]:
            self.shake["timer"] -= dt
            if self.shake["timer"] <= 0:
                self.shake["is_active"] = False; self.shake["offset"] = 0
            else:
                self.shake["offset"] = self.shake["magnitude"] * math.sin(self.shake["timer"] * self.shake["speed"])
    def upPop(self, dt):
        if self.pop["is_active"]:
            self.pop["scale"] += self.pop["speed"] * self.pop["direction"] * (dt * 60)
            if self.pop["scale"] >= self.pop["max_scale"]: self.pop["scale"] = self.pop["max_scale"]; self.pop[
                "direction"] = -1
            if self.pop["scale"] <= 1.0 and self.pop["direction"] == -1: self.pop["scale"] = 1.0; self.pop[
                "is_active"] = False

    def upFlip(self, dt):
        if self.flip["is_active"]:
            if self.flip["delay"] > 0: self.flip["delay"] -= dt; return
            self.flip["angle"] += self.flip["speed"] * dt
            if self.flip["angle"] >= 90 and self.colors["bg"] != self.flip["target_color"]:
                self.colors["bg"] = self.flip["target_color"]
                if self.colors["bg"] in [GREEN, YELLOW, DARK_GRAY]: self.colors["text"] = WHITE
            if self.flip["angle"] >= 180: self.flip["angle"] = 180; self.flip["is_active"] = False

    def draw(self, surface):
        base_surface = pygame.Surface((SQUARE_SIZE, SQUARE_SIZE), pygame.SRCALPHA)
        base_rect = base_surface.get_rect()
        pygame.draw.rect(base_surface, self.colors["bg"], base_rect, border_radius=CORNER_RADIUS)
        pygame.draw.rect(base_surface, self.colors["border"], base_rect, 2, border_radius=CORNER_RADIUS)
        if self.letter:
            text_surface = LETTER_FONT.render(self.letter, True, self.colors["text"])
            text_rect = text_surface.get_rect(center=base_rect.center)
            base_surface.blit(text_surface, text_rect)
        drawable_surface = base_surface
        drawable_rect = self.rect.copy()
        if self.pop["is_active"]:
            scaled_size = int(SQUARE_SIZE * self.pop["scale"])
            drawable_surface = pygame.transform.scale(drawable_surface, (scaled_size, scaled_size))
            drawable_rect = drawable_surface.get_rect(center=self.rect.center)
        if self.flip["is_active"]:
            scale_y = abs(math.cos(math.radians(self.flip["angle"])))
            new_height = max(1, int(drawable_rect.height * scale_y))
            drawable_surface = pygame.transform.scale(drawable_surface, (drawable_rect.width, new_height))
            drawable_rect = drawable_surface.get_rect(center=self.rect.center)
        if self.shake["is_active"]: drawable_rect.x += self.shake["offset"]
        surface.blit(drawable_surface, drawable_rect)


def draw_message(message):
    text_surface_main = MESSAGE_FONT.render(message, True, BLACK)
    text_rect_main = text_surface_main.get_rect(center=(SCREEN_WIDTH / 2, SCREEN_HEIGHT - 60))
    screen.blit(text_surface_main, text_rect_main)
    replay_surface = SMALL_MESSAGE_FONT.render("Press any key to play again", True, DARK_GRAY)
    replay_rect = replay_surface.get_rect(center=(text_rect_main.centerx, text_rect_main.bottom + 20))
    screen.blit(replay_surface, replay_rect)


def draw_notification(message):
    if not message: return
    text_surface = NOTIFICATION_FONT.render(message, True, WHITE)
    bg_rect = text_surface.get_rect(center=(SCREEN_WIDTH / 2, 80))
    bg_rect.inflate_ip(20, 10)
    pygame.draw.rect(screen, DARK_GRAY, bg_rect, border_radius=5)
    screen.blit(text_surface, text_surface.get_rect(center=bg_rect.center))

def draw_ui(guesses_left, spins_left):
    player_title = UI_FONT.render(f"Your Guesses: {guesses_left}", True, BLACK)
    player_title_rect = player_title.get_rect(center=(PLAYER_GRID_LEFT_MARGIN + GRID_WIDTH / 2, GRID_TOP_MARGIN - 40))
    screen.blit(player_title, player_title_rect)

    gacha_title = UI_FONT.render(f"Gacha Hints: {spins_left}", True, BLACK)
    gacha_title_rect = gacha_title.get_rect(center=(GACHA_GRID_LEFT_MARGIN + GRID_WIDTH / 2, GRID_TOP_MARGIN - 40))
    screen.blit(gacha_title, gacha_title_rect)

def main():
    secret_word = get_random_word()
    guesses_remaining = MAX_GUESSES
    gacha_spins_remaining = MAX_GACHA_SPINS
    current_row = 0
    current_column = 0
    gacha_result_row = 0
    global is_flipping_row
    global bg_image
    game_over = False
    message = ""
    player_matrix = []
    for row in range(MAX_GUESSES):
        row_tiles = []
        for col in range(WORD_LENGTH):
            x = PLAYER_GRID_LEFT_MARGIN + col * (SQUARE_SIZE + SQUARE_MARGIN)
            y = GRID_TOP_MARGIN + row * (SQUARE_SIZE + SQUARE_MARGIN)
            row_tiles.append(Tile("", x, y))
        player_matrix.append(row_tiles)
    gacha_matrix = []
    for row in range(MAX_GACHA_SPINS):
        row_tiles = []
        for col in range(WORD_LENGTH):
            x = GACHA_GRID_LEFT_MARGIN + col * (SQUARE_SIZE + SQUARE_MARGIN)
            y = GRID_TOP_MARGIN + row * (SQUARE_SIZE + SQUARE_MARGIN)
            row_tiles.append(Tile("", x, y))
        gacha_matrix.append(row_tiles)

    running = True
    clock = pygame.time.Clock()
    notification = ""
    notification_timer = 0.0
    original_icon = pygame.image.load('logo.png').convert_alpha()
    w, h = original_icon.get_size()
    icon_surf = pygame.Surface((w, h), pygame.SRCALPHA)
    border_radius = int(min(w, h) * 0.225)  # ví dụ dùng 22.5% như macOS
    pygame.draw.rect(icon_surf, (255, 255, 255, 255), (0, 0, w, h), border_radius=border_radius)
    icon_surf.blit(original_icon, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    pygame.display.set_icon(icon_surf)
    while running:
        dt = clock.tick(60) / 1000.0
        dt = min(dt, 0.1)
        if notification_timer > 0:
            notification_timer -= dt
            if notification_timer <= 0: notification = ""
        for event in pygame.event.get():
            if event.type == pygame.QUIT: running = False; pygame.quit(); return
            if game_over:
                if event.type == pygame.KEYDOWN: main()
                continue
            if not is_flipping_row:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        if current_column == WORD_LENGTH:
                            guess_str = "".join(
                                [player_matrix[current_row][i].get_letter() for i in range(WORD_LENGTH)]).lower()
                            print(guess_str, secret_word)
                            if guess_str not in WORD_LIST:
                                for tile in player_matrix[current_row]: tile.start_shake()
                                notification = "Not in word list"
                                notification_timer = 1.0
                            else:
                                guesses_remaining -= 1
                                if guess_str == secret_word:
                                    feedback = get_feedback(guess_str, secret_word)
                                    for col in range(WORD_LENGTH):
                                        player_matrix[current_row][col].start_flip(feedback[col], 0)
                                    is_flipping_row = True
                                else:
                                    if guesses_remaining == 0:
                                        game_over = True
                                        message = f"Out of guesses! Word was: {secret_word.upper()}"
                                    else:
                                        feedback = [DARK_GRAY] * WORD_LENGTH
                                        for col in range(WORD_LENGTH):
                                            player_matrix[current_row][col].start_flip(feedback[col], 0)
                                        is_flipping_row = True
                                        current_row += 1
                                        current_column = 0
                    elif event.key == pygame.K_BACKSPACE:
                        if current_column > 0:
                            current_column -= 1
                            player_matrix[current_row][current_column].set_letter("")
                    elif event.key == pygame.K_SPACE:
                        if gacha_spins_remaining > 0 and gacha_result_row < MAX_GACHA_SPINS:
                            gacha_spins_remaining -= 1
                            random_word = get_random_word()
                            feedback = get_feedback(random_word, secret_word)
                            for col in range(WORD_LENGTH):
                                tile = gacha_matrix[gacha_result_row][col]
                                tile.set_letter(random_word[col])
                                tile.start_flip(feedback[col], col * 0.2)
                            gacha_result_row += 1
                            is_flipping_row = True
                        else:
                            notification = "No gacha spins left!"
                            notification_timer = 1.0
                    elif current_column < WORD_LENGTH and event.unicode.isalpha():
                        tile = player_matrix[current_row][current_column]
                        tile.set_letter(event.unicode)
                        tile.start_popping()
                        current_column += 1
        any_tile_is_flipping = False
        for matrix_to_update in [player_matrix, gacha_matrix]:
            for row in matrix_to_update:
                for tile in row:
                    tile.update(dt)
                    if tile.flip["is_active"]: any_tile_is_flipping = True
        if is_flipping_row and not any_tile_is_flipping:
            is_flipping_row = False
            guess_str = "".join([player_matrix[current_row][i].get_letter() for i in range(WORD_LENGTH)]).lower()
            if guess_str == secret_word:
                game_over = True
                message = f"You got it! Word was {secret_word.upper()}"
        screen.fill(WHITE)
        bg_image_scaled = pygame.transform.scale(bg_image, (SCREEN_WIDTH, SCREEN_HEIGHT))
        screen.blit(bg_image_scaled, (0, 0))
        title_surface = MESSAGE_FONT.render("Wordle: Gacha Edition", True, BLACK)
        title_rect = title_surface.get_rect(center=(SCREEN_WIDTH / 2, 40))
        screen.blit(title_surface, title_rect)
        draw_ui(guesses_remaining, gacha_spins_remaining)
        for row in gacha_matrix:
            for tile in row: tile.draw(screen)
        for row in player_matrix:
            for tile in row: tile.draw(screen)
        draw_notification(notification)
        if game_over: draw_message(message)
        pygame.display.flip()

if __name__ == "__main__":
    main()
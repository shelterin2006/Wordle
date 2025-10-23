import asyncio
import pygame
import math
import random
import json

pygame.init()
pygame.font.init()
SCREEN_WIDTH = 620
SCREEN_HEIGHT = 750
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (106, 170, 100)
YELLOW = (201, 180, 88)
LIGHT_GRAY = (211, 211, 211)
DARK_GRAY = (120, 124, 126)
MID_GRAY = (119, 119, 119)
LETTER_FONT = pygame.font.Font("font/Poppins-Regular.ttf", size=60)
NOTIFICATION_FONT = pygame.font.Font("font/Helvetica.ttf", size=27)
MESSAGE_FONT = pygame.font.Font("font/Helvetica.ttf", size=40)
SMALL_MESSAGE_FONT = pygame.font.Font("font/Helvetica.ttf", size=20)
is_flipping_row = False
WORD_LENGTH = 5
MAX_GUESSES = 6
SQUARE_SIZE = 80
CORNER_RADIUS = 8
SQUARE_MARGIN = 10
GRID_TOP_MARGIN = 100
GRID_LEFT_MARGIN = (SCREEN_WIDTH - (WORD_LENGTH * SQUARE_SIZE + (WORD_LENGTH - 1) * SQUARE_MARGIN)) // 2
WORD_LIST = json.loads(open("wordle.json").read())
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Wordle with Pygame")

# Get a random word from the word list
def get_random_word():
    return random.choice(WORD_LIST)

# Calculate feedback colors for each letter in the guess
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

# Tile class representing each letter square in the game
class Tile:
    # Initialize a tile with letter, position and default properties
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

    # Get the current letter in the tile
    def get_letter(self):
        return self.letter

    # Set the letter and update border color
    def set_letter(self, letter):
        self.letter = letter.upper()
        if self.letter == "":
            self.colors["border"] = LIGHT_GRAY
        else:
            self.colors["border"] = MID_GRAY

    # Reset tile to initial state
    def reset(self):
        self.letter = ""
        self.colors = {
            "bg": WHITE,
            "text": BLACK,
            "border": LIGHT_GRAY
        }
        self.flip = {
            "is_active": False,
            "angle": 0,
            "speed": 700,
            "delay": 0,
            "target_color": None
        }
        self.pop = {
            "is_active": False,
            "scale": 1.0,
            "speed": 0.1,
            "direction": 1,
            "max_scale": 1.15
        }
        self.shake = {
            "is_active": False,
            "timer": 0,
            "offset": 0.0,
            "magnitude": 5,
            "speed": 50
        }

    # Start shake animation for invalid input
    def start_shake(self):
        if not self.flip["is_active"]:
            self.shake["is_active"] = True
            self.shake["timer"] = 0.4

    # Start flip animation with target color and delay
    def start_flip(self, target_color, delay):
        self.flip["is_active"] = True
        self.flip["target_color"] = target_color
        self.flip["delay"] = delay

    # Start pop animation when letter is entered
    def start_popping(self):
        if not self.pop["is_active"]:
            self.pop["is_active"] = True
            self.pop["scale"] = 1.0
            self.pop["direction"] = 1

    def update(self, dt):
        self.upShake(dt)
        self.upPop(dt)
        self.upFlip(dt)

    # Update shake animation
    def upShake(self, dt):
        if self.shake["is_active"]:
            self.shake["timer"] -= dt
            if self.shake["timer"] <= 0:
                self.shake["is_active"] = False
                self.shake["offset"] = 0
            else:
                self.shake["offset"] = self.shake["magnitude"] * math.sin(self.shake["timer"] * self.shake["speed"])

    # Update pop animation
    def upPop(self, dt):
        if self.pop["is_active"]:
            self.pop["scale"] += self.pop["speed"] * self.pop["direction"] * (dt * 60)
            if self.pop["scale"] >= self.pop["max_scale"]:
                self.pop["scale"] = self.pop["max_scale"]
                self.pop["direction"] = -1
            if self.pop["scale"] <= 1.0 and self.pop["direction"] == -1:
                self.pop["scale"] = 1.0
                self.pop["is_active"] = False

    # Update flip animation
    def upFlip(self, dt):
        if self.flip["is_active"]:
            if self.flip["delay"] > 0:
                self.flip["delay"] -= dt
                return

            self.flip["angle"] += self.flip["speed"] * dt  # <-- SỬ DỤNG TỐC ĐỘ RIÊNG

            if self.flip["angle"] >= 90 and self.colors["bg"] != self.flip["target_color"]:
                self.colors["bg"] = self.flip["target_color"]
                if self.colors["bg"] in [GREEN, YELLOW, DARK_GRAY]:
                    self.colors["text"] = WHITE

            if self.flip["angle"] >= 180:
                self.flip["angle"] = 180
                self.flip["is_active"] = False

    # Draw the tile with all animations applied
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

        if self.shake["is_active"]:
            drawable_rect.x += self.shake["offset"]

        surface.blit(drawable_surface, drawable_rect)


# Draw game over message and replay instruction
def draw_message(message):
    text_surface_main = MESSAGE_FONT.render(message, True, BLACK)
    text_rect_main = text_surface_main.get_rect(center=(SCREEN_WIDTH / 2, SCREEN_HEIGHT - 80))
    screen.blit(text_surface_main, text_rect_main)
    replay_surface = SMALL_MESSAGE_FONT.render("Press any key to play again", True, DARK_GRAY)
    replay_rect = replay_surface.get_rect(center=(text_rect_main.centerx, text_rect_main.bottom + 20))
    screen.blit(replay_surface, replay_rect)


# Draw notification message in center of screen
def draw_notification(message):
    if not message:
        return
    text_surface = NOTIFICATION_FONT.render(message, True, WHITE)
    bg_rect = text_surface.get_rect(center=(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2))
    bg_rect.inflate_ip(20, 10)
    pygame.draw.rect(screen, DARK_GRAY, bg_rect, border_radius=5)
    screen.blit(text_surface, text_surface.get_rect(center=bg_rect.center))

# Main game loop and logic
async def main():
    secret_word = get_random_word()
    feedbacks = [[WHITE] * WORD_LENGTH for _ in range(MAX_GUESSES)]
    current_row = 0
    current_column = 0
    global is_flipping_row
    game_over = False
    message = ""
    matrix = []
    for row in range(MAX_GUESSES):
        row_tiles = []
        for col in range(WORD_LENGTH):
            x = GRID_LEFT_MARGIN + col * (SQUARE_SIZE + SQUARE_MARGIN)
            y = GRID_TOP_MARGIN + row * (SQUARE_SIZE + SQUARE_MARGIN)
            row_tiles.append(Tile("", x, y))
        matrix.append(row_tiles)

    running = True
    clock = pygame.time.Clock()
    notification = ""
    notification_timer = 0.0
    while running:
        dt = clock.tick(60) / 1000.0
        dt = min(dt, 0.1)
        if notification_timer > 0:
            notification_timer -= dt
            if notification_timer <= 0:
                notification = ""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                pygame.quit()
            if game_over and event.type == pygame.KEYDOWN:
                game_over = False
                secret_word = get_random_word()
                for row in matrix:
                    for tile in row:
                        tile.reset()
                current_column = 0
                current_row = 0
                continue
            if not game_over and event.type == pygame.KEYDOWN and not is_flipping_row:
                if event.key == pygame.K_RETURN:
                    if current_column == WORD_LENGTH:
                        guess_str = "".join([matrix[current_row][i].get_letter() for i in range(WORD_LENGTH)]).lower()
                        feedbacks[current_row] = get_feedback(guess_str, secret_word)
                        print(guess_str, secret_word)
                        if guess_str not in WORD_LIST:
                            for tile in matrix[current_row]:
                                tile.start_shake()
                            notification = "Not in word list"
                            notification_timer = 1.0
                        else:
                            delay_increment = 0.2
                            for col in range(WORD_LENGTH):
                                tile = matrix[current_row][col]
                                target_color = feedbacks[current_row][col]
                                tile.start_flip(target_color, col * delay_increment)
                            is_flipping_row = True

                elif event.key == pygame.K_BACKSPACE:
                    if current_column > 0:
                        matrix[current_row][current_column - 1].set_letter("")
                        current_column -= 1
                elif current_column < WORD_LENGTH and event.unicode.isalpha():
                    matrix[current_row][current_column].set_letter(event.unicode)
                    matrix[current_row][current_column].start_popping()
                    current_column += 1
        all_flipped_in_row = True
        for row_idx, row in enumerate(matrix):
            for tile in row:
                tile.update(dt)
                if row_idx == current_row and is_flipping_row and tile.flip["is_active"]:
                    all_flipped_in_row = False

        if is_flipping_row and all_flipped_in_row:
            is_flipping_row = False
            guess_str = "".join([matrix[current_row][i].get_letter() for i in range(WORD_LENGTH)]).lower()

            if guess_str == secret_word:
                message = f"You got it! The word was {secret_word.upper()}"
                game_over = True
            elif current_row == MAX_GUESSES - 1:
                message = f"So close! The word was: {secret_word.upper()}"
                game_over = True
            else:
                current_row += 1
                current_column = 0

        screen.fill(WHITE)
        title_surface = MESSAGE_FONT.render("Wordle Game", True, BLACK)
        title_rect = title_surface.get_rect(center=(SCREEN_WIDTH / 2, 50))
        screen.blit(title_surface, title_rect)
        for row in matrix:
            for tile in row:
                tile.draw(screen)

        draw_notification(notification)
        if game_over:
            draw_message(message)

        pygame.display.flip()
        await asyncio.sleep(0)


if __name__ == "__main__":
    asyncio.run(main())

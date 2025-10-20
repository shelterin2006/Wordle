import time

import pygame
import random
import sys
import os
import json
# --- Khởi tạo Pygame ---
pygame.init()
pygame.font.init()

# --- Các hằng số ---
# Kích thước màn hình
SCREEN_WIDTH = 600
SCREEN_HEIGHT = 700

# Màu sắc (RGB)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (106, 170, 100)
YELLOW = (201, 180, 88)
LIGHT_GRAY = (211, 211, 211)  # Màu viền ô
DARK_GRAY = (120, 124, 126)  # Màu chữ cái đã đoán sai

# Font chữ
LETTER_FONT = pygame.font.SysFont("helvetica", 60)
MESSAGE_FONT = pygame.font.SysFont("helvetica", 40)

# Cấu hình trò chơi
WORD_LENGTH = 5
MAX_GUESSES = 6

# Cấu hình lưới
SQUARE_SIZE = 80
SQUARE_MARGIN = 10
GRID_TOP_MARGIN = 100
GRID_LEFT_MARGIN = (SCREEN_WIDTH - (WORD_LENGTH * SQUARE_SIZE + (WORD_LENGTH - 1) * SQUARE_MARGIN)) // 2

# Danh sách từ (bạn có thể mở rộng danh sách này hoặc tải từ một tệp)
WORD_LIST = json.loads(open("wordle.json").read())

# --- Thiết lập màn hình ---
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Wordle with Pygame")

def get_random_word():
    """Chọn một từ ngẫu nhiên từ danh sách."""
    return random.choice(WORD_LIST)

def get_feedback(guess, secret_word):
    """
    Tính toán phản hồi cho một lần đoán.
    Trả về một danh sách các màu: GREEN, YELLOW, hoặc DARK_GRAY.
    """
    feedback = [None] * WORD_LENGTH
    secret_word_list = list(secret_word)
    guess_list = list(guess)

    # Lượt 1: Tìm các chữ cái đúng vị trí (GREEN)
    for i in range(WORD_LENGTH):
        if guess_list[i] == secret_word_list[i]:
            feedback[i] = GREEN
            secret_word_list[i] = None  # Đánh dấu đã dùng
            guess_list[i] = None  # Đánh dấu đã dùng

    # Lượt 2: Tìm các chữ cái đúng nhưng sai vị trí (YELLOW)
    for i in range(WORD_LENGTH):
        if guess_list[i] is not None:
            if guess_list[i] in secret_word_list:
                feedback[i] = YELLOW
                secret_word_list[secret_word_list.index(guess_list[i])] = None  # Đánh dấu đã dùng
            else:
                feedback[i] = DARK_GRAY

    return feedback


import pygame
import math


class Tile:
    def __init__(self, letter, x, y):
        self.letter = letter.upper()
        self.x = x
        self.y = y
        self.rect = pygame.Rect(self.x, self.y, SQUARE_SIZE, SQUARE_SIZE)
        # Trạng thái ban đầu
        self.color = WHITE
        self.text_color = BLACK
        self.border_color = LIGHT_GRAY
        # Trạng thái hoạt hình
        self.is_flipping = False
        self.flip_angle = 0  # Góc lật, từ 0 đến 180
        self.target_color = None
    def start_flip(self, target_color):
        self.is_flipping = True
        self.target_color = target_color
    def update(self):
        if self.is_flipping:
            # Tăng góc lật, tốc độ có thể điều chỉnh
            self.flip_angle += 8
            # Giai đoạn 1 kết thúc (lật được nửa đường)
            if self.flip_angle >= 90 and self.color != self.target_color:
                self.color = self.target_color
                # Nếu màu nền là màu đậm, đổi chữ thành màu trắng
                if self.color in [GREEN, YELLOW, DARK_GRAY]:
                    self.text_color = WHITE

            # Hoàn thành lật
            if self.flip_angle >= 180:
                self.flip_angle = 180
                self.is_flipping = False

    def draw(self, surface):
        if not self.is_flipping:
            pygame.draw.rect(surface, self.color, self.rect)
            pygame.draw.rect(surface, self.border_color, self.rect, 2)
            if self.letter:
                text_surface = LETTER_FONT.render(self.letter, True, self.text_color)
                text_rect = text_surface.get_rect(center=self.rect.center)
                surface.blit(text_surface, text_rect)
            return
        temp_surface = pygame.Surface((SQUARE_SIZE, SQUARE_SIZE), pygame.SRCALPHA)
        temp_rect = temp_surface.get_rect()

        # Vẽ nền và viền lên canvas phụ
        pygame.draw.rect(temp_surface, self.color, temp_rect)
        pygame.draw.rect(temp_surface, self.border_color, temp_rect, 2)

        # Vẽ chữ lên canvas phụ
        if self.letter:
            text_surface = LETTER_FONT.render(self.letter, True, self.text_color)
            text_rect = text_surface.get_rect(center=temp_rect.center)
            temp_surface.blit(text_surface, text_rect)

        # 2. BIẾN ĐỔI CANVAS PHỤ ĐÓ
        # Tính toán tỷ lệ co giãn chiều cao dựa trên góc lật
        # math.cos tạo ra một đường cong mượt mà từ 1 -> 0 -> -1 -> 0 -> 1
        # abs() để đảm bảo tỷ lệ luôn dương
        scale_y = abs(math.cos(math.radians(self.flip_angle)))

        # Co giãn canvas phụ theo chiều dọc
        scaled_surface = pygame.transform.scale(temp_surface, (SQUARE_SIZE, int(SQUARE_SIZE * scale_y)))
        scaled_rect = scaled_surface.get_rect(center=self.rect.center)

        # 3. "DÁN" KẾT QUẢ LÊN MÀN HÌNH CHÍNH
        surface.blit(scaled_surface, scaled_rect)

def draw_grid(guesses, feedbacks, current_guess, current_row):


def draw_message(message):
    """Hiển thị thông báo ở cuối màn hình."""
    text_surface = MESSAGE_FONT.render(message, True, BLACK)
    text_rect = text_surface.get_rect(center=(SCREEN_WIDTH / 2, SCREEN_HEIGHT - 50))
    screen.blit(text_surface, text_rect)

def main():
    """Vòng lặp chính của trò chơi."""
    secret_word = get_random_word()
    guesses = [""] * MAX_GUESSES
    feedbacks = [[None] * WORD_LENGTH for _ in range(MAX_GUESSES)]
    current_guess = []
    current_row = 0
    game_over = False
    message = ""

    grid = []
    for row in range(MAX_GUESSES):
        row_tiles = []
        for col in range(WORD_LENGTH):
            x = GRID_LEFT_MARGIN + col * (SQUARE_SIZE + SQUARE_MARGIN)
            y = GRID_TOP_MARGIN + row * (SQUARE_SIZE + SQUARE_MARGIN)
            row_tiles.append(Tile("", x, y))
        grid.append(row_tiles)

    running = True
    while running:
        # --- Xử lý sự kiện ---
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                pygame.quit()
                sys.exit()

            if not game_over and event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:  # Phím Enter
                    if len(current_guess) == WORD_LENGTH:
                        guess_str = "".join(current_guess)
                        guesses[current_row] = guess_str
                        feedbacks[current_row] = get_feedback(guess_str, secret_word)

                        if guess_str == secret_word:
                            message = f"Chính xác! Từ đó là: {secret_word.upper()}"
                            game_over = True
                        else:
                            current_row += 1
                            current_guess = []
                            if current_row == MAX_GUESSES:
                                message = f"Bạn đã thua! Từ đó là: {secret_word.upper()}"
                                game_over = True

                elif event.key == pygame.K_BACKSPACE:  # Phím xóa
                    if len(current_guess) > 0:
                        current_guess.pop()

                elif len(current_guess) < WORD_LENGTH and event.unicode.isalpha():
                    current_guess.append(event.unicode.lower())

        # --- Vẽ màn hình ---
        screen.fill(WHITE)

        # Vẽ tiêu đề
        title_surface = MESSAGE_FONT.render("Wordle Game", True, BLACK)
        title_rect = title_surface.get_rect(center=(SCREEN_WIDTH / 2, 50))
        screen.blit(title_surface, title_rect)

        # Vẽ lưới
        draw_grid(guesses, feedbacks, current_guess, current_row)

        # Vẽ thông báo kết thúc trò chơi
        if game_over:
            draw_message(message)

        # Cập nhật màn hình
        pygame.display.flip()


if __name__ == "__main__":
    main()
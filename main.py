import time
from operator import truediv
import asyncio #web version
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
LETTER_FONT = pygame.font.Font("Poppins-Regular.ttf", 60)
MESSAGE_FONT = pygame.font.Font("Poppins-Regular.ttf", 40)

# Cấu hình trò chơi
WORD_LENGTH = 5
MAX_GUESSES = 6

# Cấu hình lưới
SQUARE_SIZE = 80
CORNER_RADIUS = 8
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
    Tính toán phản hồi Wordle chuẩn.
    """
    # Đảm bảo chữ thường
    guess = guess.lower()
    secret_word = secret_word.lower()

    # Khởi tạo
    feedback = [DARK_GRAY] * WORD_LENGTH

    # Tạo bản sao có thể sửa đổi của từ bí mật
    # Sử dụng dict để đếm tần suất chữ cái còn lại
    secret_counts = {}
    for char in secret_word:
        secret_counts[char] = secret_counts.get(char, 0) + 1

    # Lượt 1: Tìm GREEN
    # Đồng thời loại trừ các ký tự GREEN khỏi việc đếm YELLOW
    for i in range(WORD_LENGTH):
        if guess[i] == secret_word[i]:
            feedback[i] = GREEN
            secret_counts[guess[i]] -= 1 # Giảm số lần xuất hiện của ký tự này

    # Lượt 2: Tìm YELLOW (và những chữ cái còn lại là DARK_GRAY)
    for i in range(WORD_LENGTH):
        # Chỉ kiểm tra nếu chưa phải là GREEN
        if feedback[i] != GREEN:
            char = guess[i]
            # Nếu ký tự có trong từ bí mật VÀ số lần xuất hiện còn lại > 0
            if char in secret_counts and secret_counts[char] > 0:
                feedback[i] = YELLOW
                secret_counts[char] -= 1 # Giảm số lần xuất hiện này
            # KHÔNG cần else vì đã khởi tạo là DARK_GRAY

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
    def get_letter(self):
        return self.letter
    def get_x(self):
        return self.x
    def get_y(self):
        return self.y
    def set_letter(self, letter):
        self.letter = letter.upper()
    def start_flip(self, target_color):
        self.is_flipping = True
        self.target_color = target_color
    def update(self):
        if self.is_flipping:
            # Tăng góc lật, tốc độ có thể điều chỉnh
            self.flip_angle += 1.5
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

    def draw(self, surface, color):
        # --- Bước 1: Chuẩn bị một "canvas phụ" cho ô vuông ---
        temp_surface = pygame.Surface((self.rect.width, self.rect.height), pygame.SRCALPHA)

        # --- Bước 2: Vẽ tất cả các thành phần lên canvas phụ đó ---

        # Vẽ nền (sử dụng self.color đã được cập nhật) và viền
        # Cả hai lệnh vẽ đều cần có border_radius để khớp với nhau

        # 1. Vẽ nền với góc được bo tròn
        pygame.draw.rect(temp_surface, color, temp_surface.get_rect(),
                         border_radius=CORNER_RADIUS)  # <--- THÊM VÀO ĐÂY

        # 2. Vẽ viền với góc được bo tròn
        pygame.draw.rect(temp_surface, self.border_color, temp_surface.get_rect(), 2,
                         border_radius=CORNER_RADIUS)  # <--- VÀ Ở ĐÂY

        # Vẽ chữ nếu có (phần này không thay đổi)
        if self.letter:
            text_surface = LETTER_FONT.render(self.letter, True, self.text_color)
            text_rect = text_surface.get_rect(center=temp_surface.get_rect().center)
            temp_surface.blit(text_surface, text_rect)

        # --- Bước 3: Quyết định cách "dán" canvas phụ lên màn hình chính ---
        drawable_surface = temp_surface
        drawable_rect = self.rect

        # Nếu đang trong hiệu ứng lật (phần này không thay đổi)
        if self.is_flipping:
            scale_y = abs(math.cos(math.radians(self.flip_angle)))
            new_height = max(1, int(self.rect.height * scale_y))
            drawable_surface = pygame.transform.scale(temp_surface, (self.rect.width, new_height))
            drawable_rect = drawable_surface.get_rect(center=self.rect.center)

        # Cuối cùng, "dán" kết quả lên màn hình chính
        surface.blit(drawable_surface, drawable_rect)

rowFip = 0
colFlip = 10
FlipAnimation = False
def flip(feedbacks, current_guess, current_row, matrix):
    global rowFip
    global colFlip
    global FlipAnimation
    matrix[rowFip][colFlip].update()
    if not matrix[rowFip][colFlip].is_flipping:
        colFlip += 1
        if colFlip != WORD_LENGTH:
            matrix[rowFip][colFlip].start_flip(feedbacks[rowFip][colFlip])

def draw_grid(feedbacks, current_guess, current_row, matrix):
    global FlipAnimation
    if colFlip == WORD_LENGTH:
        FlipAnimation = False
    for i in range(MAX_GUESSES):
        for j in range(WORD_LENGTH):
            if i == rowFip and j == colFlip:
                flip(feedbacks, current_guess, i, matrix)
            color = LIGHT_GRAY
            if feedbacks[i][j]:
                color = feedbacks[i][j]
            matrix[i][j].draw(screen, color)

def draw_message(message):
    """Hiển thị thông báo ở cuối màn hình."""
    text_surface = MESSAGE_FONT.render(message, True, BLACK)
    text_rect = text_surface.get_rect(center=(SCREEN_WIDTH / 2, SCREEN_HEIGHT - 50))
    screen.blit(text_surface, text_rect)

async def main():
    """Vòng lặp chính của trò chơi."""
    secret_word = get_random_word()
    guesses = [""] * MAX_GUESSES
    feedbacks = [[None] * WORD_LENGTH for _ in range(MAX_GUESSES)]
    current_guess = []
    current_row = 0
    current_column = 0
    global rowFip
    global colFlip
    global FlipAnimation
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
    while running:
        # --- Xử lý sự kiện ---
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                pygame.quit()
                sys.exit()
            if not game_over and event.type == pygame.KEYDOWN and not FlipAnimation:
                if event.key == pygame.K_RETURN:  # Phím Enter
                    FlipAnimation = True
                    rowFip = current_row
                    colFlip = 0
                    if current_column == WORD_LENGTH:
                        guess_str = ""
                        for i in range(WORD_LENGTH):
                            guess_str += matrix[current_row][i].get_letter().lower()
                        print(guess_str, secret_word)
                        feedbacks[current_row] = get_feedback(guess_str, secret_word)
                        matrix[rowFip][colFlip].start_flip(feedbacks[rowFip][colFlip])

                        if guess_str == secret_word:
                            message = f"Chính xác! Từ đó là: {secret_word.upper()}"
                            game_over = True
                        else:
                            current_row += 1
                            current_column = 0
                            if current_row == MAX_GUESSES:
                                message = f"Bạn đã thua! Từ đó là: {secret_word.upper()}"
                                game_over = True

                elif event.key == pygame.K_BACKSPACE:  # Phím xóa
                    if current_column > 0:
                        matrix[current_row][current_column - 1].set_letter("")
                        current_column -= 1
                elif current_column < WORD_LENGTH and event.unicode.isalpha():
                    matrix[current_row][current_column].set_letter(event.unicode);
                    current_column += 1

        # --- Vẽ màn hình ---
        screen.fill(WHITE)

        # Vẽ tiêu đề
        title_surface = MESSAGE_FONT.render("Wordle Game", True, BLACK)
        title_rect = title_surface.get_rect(center=(SCREEN_WIDTH / 2, 50))
        screen.blit(title_surface, title_rect)

        # Vẽ lưới
        draw_grid(feedbacks, current_guess, current_row, matrix)

        # Vẽ thông báo kết thúc trò chơi
        if game_over:
            draw_message(message)

        # Cập nhật màn hình
        pygame.display.flip()
        await asyncio.sleep(0)


if __name__ == "__main__":
    asyncio.run(main())
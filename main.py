import asyncio #web version
import pygame
import math
import random
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
WORD_LIST = json.loads(open("wordle.json").read())

# --- Thiết lập màn hình ---
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Wordle with Pygame")

def get_random_word():
    """Chọn một từ ngẫu nhiên từ danh sách."""
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
            secret_counts[guess[i]] -= 1 # Giảm số lần xuất hiện của ký tự này
    for i in range(WORD_LENGTH):
        # Chỉ kiểm tra nếu chưa phải là GREEN
        if feedback[i] != GREEN:
            char = guess[i]
            # Nếu ký tự có trong từ bí mật VÀ số lần xuất hiện còn lại > 0
            if char in secret_counts and secret_counts[char] > 0:
                feedback[i] = YELLOW
                secret_counts[char] -= 1 # Giảm số lần xuất hiện này
    return feedback

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
        self.flip_speed = 0.5  # Tốc độ lật
        self.flip_delay = 0  # Thời gian chờ trước khi bắt đầu lật
        # --- THÊM THUỘC TÍNH MỚI CHO HIỆU ỨNG POP ---
        self.is_popping = False
        self.pop_scale = 1.0  # Tỷ lệ phóng to ban đầu
        self.pop_speed = 0.005  # Tốc độ phóng to/thu nhỏ
        self.pop_direction = 1  # 1: Đang phóng to, -1: Đang thu nhỏ
        self.pop_max = 1.3

    def get_letter(self):
        return self.letter
    def get_x(self):
        return self.x
    def get_y(self):
        return self.y
    def set_letter(self, letter):
        self.letter = letter.upper()
    def start_flip(self, target_color, delay):
        self.is_flipping = True
        self.target_color = target_color
        self.flip_delay = delay # Set thời gian chờ
    def start_popping(self):
        self.is_popping = True
        self.pop_scale = 1.0  # Tỷ lệ phóng to ban đầu
        self.pop_speed = 0.005  # Tốc độ phóng to/thu nhỏ
        self.pop_direction = 1  # 1: Đang phóng to, -1: Đang thu nhỏ
        self.pop_max = 1.3
    def upPop(self):
        if self.is_popping:
            self.pop_scale += self.pop_speed * self.pop_direction
            if self.pop_scale >= self.pop_max:
                self.pop_scale = self.pop_max
                self.pop_direction = -1  # Bắt đầu thu nhỏ

            # Kết thúc hiệu ứng khi đã thu về kích thước ban đầu
            if self.pop_scale <= 1.0 and self.pop_direction == -1:
                self.is_popping = False
    def upFlip(self):
        if self.is_flipping:
            # Nếu còn thời gian chờ, giảm nó đi và không làm gì cả
            if self.flip_delay > 0:
                self.flip_delay -= 1
                return
            self.flip_angle += self.flip_speed
            # Giai đoạn 1 kết thúc (lật được nửa đường)
            if self.flip_angle >= 90 and self.color != self.target_color:
                self.color = self.target_color
                # Nếu màu nền là màu đậm, đổi chữ thành màu trắng
                if self.color in [GREEN, YELLOW, DARK_GRAY]:
                    self.text_color = WHITE
            if self.flip_angle >= 180:
                self.flip_angle = 180
                self.is_flipping = False
    def update(self):
        self.upPop()
        self.upFlip()

    def draw(self, surface, color):
        base_surface = pygame.Surface((SQUARE_SIZE, SQUARE_SIZE), pygame.SRCALPHA)
        base_rect = base_surface.get_rect()
        pygame.draw.rect(base_surface, self.color, base_rect, border_radius=CORNER_RADIUS)
        pygame.draw.rect(base_surface, self.border_color, base_rect, 2, border_radius=CORNER_RADIUS)
        if self.letter:
            text_surface = LETTER_FONT.render(self.letter, True, self.text_color)
            text_rect = text_surface.get_rect(center=base_rect.center)
            base_surface.blit(text_surface, text_rect)
        # ====================================================================
        # BƯỚC 2: ÁP DỤNG CÁC HIỆU ỨNG BIẾN ĐỔI LÊN CANVAS ĐÓ
        # ====================================================================

        # Bắt đầu với canvas gốc và vị trí gốc
        drawable_surface = base_surface
        drawable_rect = self.rect.copy()  # Dùng copy để không thay đổi rect gốc

        # --- Áp dụng hiệu ứng Pop (Phóng to/Thu nhỏ) ---
        if self.is_popping:
            scaled_width = int(SQUARE_SIZE * self.pop_scale)
            scaled_height = int(SQUARE_SIZE * self.pop_scale)
            # Biến đổi surface hiện tại (có thể đã được lật hoặc chưa)
            drawable_surface = pygame.transform.scale(drawable_surface, (scaled_width, scaled_height))
            # Căn giữa lại sau khi phóng to
            drawable_rect = drawable_surface.get_rect(center=self.rect.center)

        # --- Áp dụng hiệu ứng Flip (Lật) ---
        if self.is_flipping:
            scale_y = abs(math.cos(math.radians(self.flip_angle)))
            new_height = max(1, int(drawable_rect.height * scale_y))  # Dùng chiều cao hiện tại

            # Biến đổi surface hiện tại (có thể đã được pop hoặc chưa)
            drawable_surface = pygame.transform.scale(drawable_surface, (drawable_rect.width, new_height))

            # Căn giữa lại sau khi lật
            drawable_rect = drawable_surface.get_rect(center=self.rect.center)

        # ====================================================================
        # BƯỚC 3: "DÁN" KẾT QUẢ CUỐI CÙNG LÊN MÀN HÌNH CHÍNH
        # ====================================================================
        surface.blit(drawable_surface, drawable_rect)

is_flipping_row = False

def draw_message(message):
    """Hiển thị thông báo ở cuối màn hình."""
    text_surface = MESSAGE_FONT.render(message, True, BLACK)
    text_rect = text_surface.get_rect(center=(SCREEN_WIDTH / 2, SCREEN_HEIGHT - 50))
    screen.blit(text_surface, text_rect)

async def main():
    secret_word = get_random_word()
    feedbacks = [[None] * WORD_LENGTH for _ in range(MAX_GUESSES)]
    current_row = 0
    current_column = 0
    global is_flipping_row
    game_over = False

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
            if not game_over and event.type == pygame.KEYDOWN and not is_flipping_row:
                if event.key == pygame.K_RETURN:
                    if current_column == WORD_LENGTH:
                        guess_str = "".join([matrix[current_row][i].get_letter() for i in range(WORD_LENGTH)]).lower()
                        feedbacks[current_row] = get_feedback(guess_str, secret_word)
                        print(guess_str, secret_word)
                        delay_increment = 60
                        for col in range(WORD_LENGTH):
                            tile = matrix[current_row][col]
                            target_color = feedbacks[current_row][col]
                            # Gọi start_flip với độ trễ tăng dần cho mỗi ô
                            tile.start_flip(target_color, col * delay_increment)
                        is_flipping_row = True  # Bật cờ báo hiệu animation đang chạy

                elif event.key == pygame.K_BACKSPACE:  # Phím xóa
                    if current_column > 0:
                        matrix[current_row][current_column - 1].set_letter("")
                        current_column -= 1
                elif current_column < WORD_LENGTH and event.unicode.isalpha():
                    matrix[current_row][current_column].set_letter(event.unicode)
                    matrix[current_row][current_column].start_popping()
                    current_column += 1
        if is_flipping_row:
            # Kiểm tra xem tất cả các ô trong hàng đã lật xong chưa
            all_flipped = True
            for tile in matrix[current_row]:
                tile.update()  # Mỗi ô tự cập nhật trạng thái lật của nó
                if tile.is_flipping:
                    all_flipped = False  # Nếu còn 1 ô đang lật thì chưa xong

            if all_flipped:
                is_flipping_row = False  # Tắt cờ animation
                guess_str = "".join([matrix[current_row][i].get_letter() for i in range(WORD_LENGTH)]).lower()
                if guess_str == secret_word:
                    message = f"Chính xác! Từ đó là: {secret_word.upper()}"
                    game_over = True
                else:
                    current_row += 1
                    current_column = 0
                    if current_row == MAX_GUESSES:
                        message = f"Bạn đã thua! Từ đó là: {secret_word.upper()}"
                        game_over = True

        for row in matrix:
            for tile in row:
                tile.update()

        # --- Vẽ màn hình ---
        screen.fill(WHITE)

        # Vẽ tiêu đề
        title_surface = MESSAGE_FONT.render("Wordle Game", True, BLACK)
        title_rect = title_surface.get_rect(center=(SCREEN_WIDTH / 2, 50))
        screen.blit(title_surface, title_rect)

        # Vẽ lưới (HÀM MỚI, ĐƠN GIẢN HƠN)
        for row in range(MAX_GUESSES):
            for col in range(WORD_LENGTH):
                matrix[row][col].draw(screen, matrix[row][col].color)
        # Vẽ thông báo kết thúc trò chơi
        if game_over:
            draw_message(";")
        pygame.display.flip()
        await asyncio.sleep(0)


if __name__ == "__main__":
    asyncio.run(main())
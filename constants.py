import json
import pygame
WORD_LENGTH = 5
MAX_GUESSES = 6
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
SQUARE_SIZE = 80
CORNER_RADIUS = 8
SQUARE_MARGIN = 10
GRID_TOP_MARGIN = 100
GRID_LEFT_MARGIN = (SCREEN_WIDTH - (WORD_LENGTH * SQUARE_SIZE + (WORD_LENGTH - 1) * SQUARE_MARGIN)) // 2
WORD_LIST = json.loads(open("wordle.json").read())
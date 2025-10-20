
import sys, math, random, time
import pygame

# ==============================
# Wordle+ Pygame Polished UI
# ==============================
# - Dark neon theme, soft gradients, rounded tiles
# - Animations: pop, shake (invalid), flip reveal
# - On-screen keyboard with state colors
# - Basic Wordle logic (5-letter word, 6 rows)
#
# Controls:
#  - Type letters (A-Z)
#  - Backspace to delete
#  - Enter to submit guess
#  - R to restart
#
# NOTE: Replace TARGET_WORD and evaluate_guess() with your own logic or loader for full game.

# --------------- CONFIG / THEME ---------------
WIDTH, HEIGHT = 600, 800
FPS = 60

# Colors (RGB)
BG_TOP = (27, 36, 64)      # #1b2440
BG_BOTTOM = (11, 15, 23)   # #0b0f17
TEXT = (230, 237, 247)     # #e6edf7

CORRECT_1 = (105, 224, 126)
CORRECT_2 = (69, 184, 90)
PRESENT_1 = (255, 216, 106)
PRESENT_2 = (202, 167, 63)
ABSENT_1  = (61, 75, 106)
ABSENT_2  = (42, 52, 74)

TILE_BORDER = (44, 58, 90) # #2c3a5a

# Layout
TILE_SIZE = 64
TILE_RADIUS = 12
TILE_GAP = 10
ROWS = 6
COLS = 5

BOARD_TOP = 120
BOARD_LEFT = (WIDTH - (COLS*TILE_SIZE + (COLS-1)*TILE_GAP)) // 2

KEY_W = 40
KEY_H = 52
KEY_GAP = 8

# Font sizes
FS_TILE = 36
FS_UI = 20
FS_MSG = 18

# --------------- UTILITIES ---------------
def lerp(a, b, t): return a + (b - a) * t

def ease_out_back(t, s=1.70158):
    t -= 1.0
    return (t*t*((s+1)*t + s) + 1)

def ease_in_out_cubic(t):
    if t < 0.5:
        return 4*t*t*t
    else:
        f = (2*t - 2)
        return 0.5*f*f*f + 1

def rounded_rect(surface, rect, color, radius):
    x, y, w, h = rect
    # Pygame 2 has draw.rect with border_radius
    pygame.draw.rect(surface, color, rect, border_radius=radius)

def gradient_rect(surface, rect, c1, c2, vertical=True, radius=0):
    # Draw a vertical gradient rounded rectangle
    x, y, w, h = rect
    steps = max(1, h if vertical else w)
    for i in range(steps):
        t = i / (steps - 1) if steps > 1 else 0
        r = int(lerp(c1[0], c2[0], t))
        g = int(lerp(c1[1], c2[1], t))
        b = int(lerp(c1[2], c2[2], t))
        if vertical:
            pygame.draw.rect(surface, (r,g,b), (x, y+i, w, 1))
        else:
            pygame.draw.rect(surface, (r,g,b), (x+i, y, 1, h))
    # mask for rounded corners
    if radius > 0:
        mask_surf = pygame.Surface((w, h), pygame.SRCALPHA)
        pygame.draw.rect(mask_surf, (0,0,0,0), (0,0,w,h))
        pygame.draw.rect(mask_surf, (0,0,0,255), (0,0,w,h), border_radius=radius)
        surface.blit(mask_surf, (x,y), special_flags=pygame.BLEND_RGBA_MIN)

def draw_glow(surface, center, radius, color, alpha=90):
    glow = pygame.Surface((radius*2, radius*2), pygame.SRCALPHA)
    pygame.draw.circle(glow, (*color, alpha), (radius, radius), radius)
    surface.blit(glow, (center[0]-radius, center[1]-radius), special_flags=pygame.BLEND_RGBA_ADD)

# --------------- GAME LOGIC ---------------
# Basic word list for demo (ALL CAPS, 5 letters). Replace with your own list.
WORDS = ["ROBOT","LASER","PIXEL","EARTH","LIGHT","MUSIC","TREND","FRAME","CYBER","CLOUD","RIVER","MANGO","STONE","BLADE","STARS","NINJA","SUSHI","MAGIC","PLANT","TOUCH","SMILE","SHINE","BRAIN","SOLAR"]
TARGET_WORD = random.choice(WORDS)

def evaluate_guess(guess, target):
    # Returns statuses per char: 'correct', 'present', 'absent'
    # Standard Wordle evaluation with accounting for duplicate letters.
    result = ['absent']*len(guess)
    target_counts = {}
    for ch in target:
        target_counts[ch] = target_counts.get(ch, 0) + 1
    # First pass: corrects
    for i, ch in enumerate(guess):
        if target[i] == ch:
            result[i] = 'correct'
            target_counts[ch] -= 1
    # Second pass: presents
    for i, ch in enumerate(guess):
        if result[i] == 'correct': continue
        if target_counts.get(ch, 0) > 0:
            result[i] = 'present'
            target_counts[ch] -= 1
    return result

# --------------- UI CLASSES ---------------
class Tile:
    def __init__(self, x, y, size=TILE_SIZE):
        self.x, self.y, self.size = x, y, size
        self.letter = ''
        self.state = None      # None | 'correct' | 'present' | 'absent'
        self.flip_t = 0.0      # 0..1 while flipping
        self.pop_t = 0.0       # 0..1 while popping
        self.revealed = False

    def set_letter(self, ch):
        self.letter = ch
        self.trigger_pop()

    def clear(self):
        self.letter = ''
        self.state = None
        self.flip_t = 0
        self.pop_t = 0
        self.revealed = False

    def trigger_pop(self):
        self.pop_t = 1.0

    def trigger_flip(self):
        self.flip_t = 1.0

    def update(self, dt):
        if self.pop_t > 0:
            self.pop_t = max(0.0, self.pop_t - dt*3.6)  # fast
        if self.flip_t > 0:
            self.flip_t = max(0.0, self.flip_t - dt*2.5)

    def draw(self, surf, font):
        # Compute animations
        # Pop scale
        pop_scale = 1.0
        if self.pop_t > 0:
            e = ease_out_back(1.0 - self.pop_t)
            pop_scale = lerp(0.92, 1.06, e)

        # Flip (simulate rotateX via scaleY)
        flip_scale_y = 1.0
        if self.flip_t > 0:
            e = ease_in_out_cubic(1.0 - self.flip_t)  # 0->1 progression
            # 0..0.5 shrink to 0, 0.5..1 expand back
            if e < 0.5:
                flip_scale_y = lerp(1.0, 0.0, e*2)
            else:
                flip_scale_y = lerp(0.0, 1.0, (e-0.5)*2)

        w = int(self.size * pop_scale)
        h = int(self.size * pop_scale * flip_scale_y)
        cx = self.x + self.size//2
        cy = self.y + self.size//2
        draw_x = cx - w//2
        draw_y = cy - h//2

        # Choose background gradient by state
        if self.state == 'correct':
            c1, c2 = CORRECT_1, CORRECT_2
        elif self.state == 'present':
            c1, c2 = PRESENT_1, PRESENT_2
        elif self.state == 'absent':
            c1, c2 = ABSENT_1, ABSENT_2
        else:
            c1, c2 = (26,37,66), (16,26,48)  # idle tile gradient

        if h > 0:
            gradient_rect(surf, (draw_x, draw_y, w, h), c1, c2, vertical=True, radius=TILE_RADIUS)
            pygame.draw.rect(surf, TILE_BORDER, (draw_x, draw_y, w, h), width=1, border_radius=TILE_RADIUS)

        # Draw letter (only when "front" side visible)
        if flip_scale_y > 0.15 and self.letter:
            text_surf = font.render(self.letter, True, TEXT)
            text_rect = text_surf.get_rect(center=(cx, cy))
            surf.blit(text_surf, text_rect)

class KeyboardKey:
    def __init__(self, label, x, y, w=KEY_W, h=KEY_H):
        self.label = label
        self.rect = pygame.Rect(x,y,w,h)
        self.state = None # None|'correct'|'present'|'absent'
        self.pressed = False

    def draw(self, surf, font):
        if self.state == 'correct':
            c1, c2 = CORRECT_1, CORRECT_2
            fg = (7,34,15)
        elif self.state == 'present':
            c1, c2 = PRESENT_1, PRESENT_2
            fg = (31,22,4)
        elif self.state == 'absent':
            c1, c2 = ABSENT_1, ABSENT_2
            fg = (207,216,234)
        else:
            c1, c2 = (27,36,64), (18,26,46)
            fg = TEXT
        gradient_rect(surf, self.rect, c1, c2, vertical=True, radius=10)
        pygame.draw.rect(surf, (42,54,87), self.rect, 1, border_radius=10)
        label_surf = font.render(self.label, True, fg)
        surf.blit(label_surf, label_surf.get_rect(center=self.rect.center))

# --------------- MAIN APP ---------------
class WordlePlus:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption("Wordle+ (Pygame Skin)")
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        self.clock = pygame.time.Clock()
        self.font_tile = pygame.font.SysFont("poppins,inter,arial", FS_TILE, bold=True)
        self.font_ui = pygame.font.SysFont("inter,arial", FS_UI, bold=True)
        self.font_msg = pygame.font.SysFont("inter,arial", FS_MSG)

        self.reset()

    def reset(self):
        self.target = TARGET_WORD
        self.rows = []
        for r in range(ROWS):
            row = []
            for c in range(COLS):
                x = BOARD_LEFT + c*(TILE_SIZE + TILE_GAP)
                y = BOARD_TOP  + r*(TILE_SIZE + TILE_GAP)
                row.append(Tile(x,y))
            self.rows.append(row)

        self.cur_row = 0
        self.cur_col = 0
        self.game_over = False
        self.win = False
        self.invalid_timer = 0.0
        self.message = "Type letters, Enter to submit. Press R to restart."
        self.keyboard = self.build_keyboard()

    def build_keyboard(self):
        rows = ["QWERTYUIOP","ASDFGHJKL","⌫ZXCVBNM⏎"]
        x = (WIDTH - (10*KEY_W + 9*KEY_GAP))//2
        kb = []
        # Row 1
        y = 520
        curx = x
        for ch in rows[0]:
            kb.append(KeyboardKey(ch, curx, y))
            curx += KEY_W + KEY_GAP
        # Row 2
        y += KEY_H + 8
        curx = x + 14
        for ch in rows[1]:
            kb.append(KeyboardKey(ch, curx, y))
            curx += KEY_W + KEY_GAP
        # Row 3
        y += KEY_H + 8
        curx = x - 30
        for ch in rows[2]:
            w = 90 if ch in ["⏎","⌫"] else KEY_W
            kb.append(KeyboardKey(ch, curx, y, w=w))
            curx += w + KEY_GAP
        return kb

    def find_key(self, label):
        for k in self.keyboard:
            if k.label == label:
                return k
        return None

    def update_key_state(self, ch, state):
        # Upgrade priority: absent < present < correct
        rank = {'absent':0,'present':1,'correct':2}
        for key in self.keyboard:
            if key.label == ch.upper():
                cur = key.state
                if cur is None or rank[state] > rank.get(cur, -1):
                    key.state = state

    def type_letter(self, ch):
        if self.game_over: return
        if self.cur_col < COLS and ch.isalpha():
            tile = self.rows[self.cur_row][self.cur_col]
            tile.set_letter(ch.upper())
            self.cur_col += 1

    def backspace(self):
        if self.game_over: return
        if self.cur_col > 0:
            self.cur_col -= 1
            tile = self.rows[self.cur_row][self.cur_col]
            tile.clear()

    def submit(self):
        if self.game_over: return
        # If row not full -> invalid
        row_tiles = self.rows[self.cur_row]
        guess = ''.join([t.letter for t in row_tiles])
        if len(guess) != COLS or not guess.isalpha():
            self.invalid()
            self.message = "Not enough letters."
            return
        # Optional: dictionary check
        # if guess not in WORDS: invalid
        # For demo, accept any 5-letter guess
        statuses = evaluate_guess(guess, self.target)
        # Animate flip reveal
        for i, t in enumerate(row_tiles):
            t.state = statuses[i]
        self.animate_reveal(row_tiles, statuses)

        # Update keyboard state
        for i, ch in enumerate(guess):
            self.update_key_state(ch, statuses[i])

        if guess == self.target:
            self.game_over = True
            self.win = True
            self.message = "Great! Press R to play again."
        else:
            self.cur_row += 1
            self.cur_col = 0
            if self.cur_row >= ROWS:
                self.game_over = True
                self.win = False
                self.message = f"Answer: {self.target}. Press R to retry."

    def invalid(self):
        self.invalid_timer = 0.45  # seconds

    def animate_reveal(self, row_tiles, statuses):
        # Trigger staggered flip
        for i, tile in enumerate(row_tiles):
            # small delay per tile for stagger; we'll manage via flip_t usage
            tile.flip_t = 1.0 + i*0.07

    def draw_background(self):
        # Vertical gradient background
        for i in range(HEIGHT):
            t = i / (HEIGHT-1)
            r = int(lerp(BG_TOP[0], BG_BOTTOM[0], t))
            g = int(lerp(BG_TOP[1], BG_BOTTOM[1], t))
            b = int(lerp(BG_TOP[2], BG_BOTTOM[2], t))
            pygame.draw.line(self.screen, (r,g,b), (0,i), (WIDTH,i))
        # Subtle glow behind board
        draw_glow(self.screen, (WIDTH//2, 240), 180, (90, 140, 255), alpha=28)

    def draw_topbar(self):
        title = self.font_ui.render("WORDLE+", True, (219, 231, 255,))
        self.screen.blit(title, title.get_rect(center=(WIDTH//2, 50)))

    def draw_board(self, dt):
        # Shake if invalid
        offset_x = 0
        if self.invalid_timer > 0:
            t = 1.0 - (self.invalid_timer / 0.45)
            # shake amplitude 4px
            offset_x = int(math.sin(t*math.pi*10) * 4)
            self.invalid_timer -= dt

        for r, row in enumerate(self.rows):
            for c, tile in enumerate(row):
                ox = offset_x if r == self.cur_row else 0
                # update per-tile animation
                tile.update(dt)
                # temp translate for shake
                oldx = tile.x
                tile.x += ox
                tile.draw(self.screen, self.font_tile)
                tile.x = oldx

    def draw_keyboard(self):
        for key in self.keyboard:
            key.draw(self.screen, self.font_ui)

    def draw_message(self):
        if self.message:
            surf = self.font_msg.render(self.message, True, (159,179,209))
            self.screen.blit(surf, surf.get_rect(center=(WIDTH//2, 480)))

    def loop(self):
        while True:
            dt = self.clock.tick(FPS)/1000.0
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit(); sys.exit(0)
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        pygame.quit(); sys.exit(0)
                    if event.key == pygame.K_r:
                        self.reset()
                    if event.key == pygame.K_RETURN:
                        self.submit()
                    elif event.key == pygame.K_BACKSPACE:
                        self.backspace()
                    else:
                        ch = event.unicode
                        if ch and ch.isalpha():
                            self.type_letter(ch)
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    mx,my = event.pos
                    for key in self.keyboard:
                        if key.rect.collidepoint(mx,my):
                            if key.label == "⏎":
                                self.submit()
                            elif key.label == "⌫":
                                self.backspace()
                            else:
                                self.type_letter(key.label)

            self.draw_background()
            self.draw_topbar()
            self.draw_board(dt)
            self.draw_message()
            self.draw_keyboard()

            pygame.display.flip()

if __name__ == "__main__":
    app = WordlePlus()
    app.loop()

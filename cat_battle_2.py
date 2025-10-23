"""
Cat Battle - 可愛卡通貓咪大戰 (單人 + 擴充版)

執行：
1) pip install pygame
2) python cat_battle.py

"""

import pygame
import sys
import random
import json
import os
import platform

pygame.init()

# 視窗設定
WIDTH, HEIGHT = 800, 600
FPS = 60
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("貓咪大戰 Cat Battle")
clock = pygame.time.Clock()

# 字型設定（跨平台中文支援）
sys_font = "Microsoft JhengHei"
if platform.system() == "Darwin":
    sys_font = "PingFang TC"
elif platform.system() == "Linux":
    sys_font = "Noto Sans CJK TC"
FONT = pygame.font.SysFont(sys_font, 36)
BIGFONT = pygame.font.SysFont(sys_font, 56)

# 顏色
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
SKY = (200, 230, 255)
GROUND = (200, 240, 200)
BUTTON_BG = (240, 240, 240)
BUTTON_BORDER = (180, 180, 180)

# 音效與背景音樂
try:
    pygame.mixer.init()
    hit_sound = pygame.mixer.Sound(pygame.mixer.Sound(file=None))  # placeholder
    win_sound = pygame.mixer.Sound(pygame.mixer.Sound(file=None))
    lose_sound = pygame.mixer.Sound(pygame.mixer.Sound(file=None))
except Exception:
    hit_sound = win_sound = lose_sound = None

# 若有背景音樂檔可替換下行檔案名
try:
    pygame.mixer.music.load(pygame.mixer.Sound(file=None))
    pygame.mixer.music.play(-1)
except Exception:
    pass

# 遊戲資料
score = 0
selected_index = 0
cats = []
CAT_PROFILES = [
    ("橘子", (255, 160, 60), 6, 4, 5),
    ("雪球", (240, 240, 255), 4, 6, 4),
    ("墨墨", (60, 60, 60), 5, 5, 6),
]

# 高分紀錄檔案
SCORE_FILE = "scores.json"
def load_high_score():
    if os.path.exists(SCORE_FILE):
        with open(SCORE_FILE, 'r', encoding='utf-8') as f:
            return json.load(f).get('highscore', 0)
    return 0

def save_high_score(val):
    with open(SCORE_FILE, 'w', encoding='utf-8') as f:
        json.dump({'highscore': val}, f)

highscore = load_high_score()

# 生成貓咪表情幀

def create_cat_surface(size, base_color, mood='normal'):
    w, h = size
    surf = pygame.Surface((w, h), pygame.SRCALPHA)
    body_rect = pygame.Rect(w*0.12, h*0.28, w*0.76, h*0.52)
    pygame.draw.ellipse(surf, base_color, body_rect)
    face_rect = pygame.Rect(w*0.22, h*0.06, w*0.56, h*0.44)
    pygame.draw.ellipse(surf, base_color, face_rect)
    left_ear = [(w*0.28, h*0.08), (w*0.36, h*0.02), (w*0.32, h*0.18)]
    right_ear = [(w*0.72, h*0.08), (w*0.64, h*0.02), (w*0.68, h*0.18)]
    pygame.draw.polygon(surf, base_color, left_ear)
    pygame.draw.polygon(surf, base_color, right_ear)
    inner_color = (255, 200, 220)
    pygame.draw.polygon(surf, inner_color, [(w*0.31, h*0.07), (w*0.34, h*0.03), (w*0.33, h*0.14)])
    pygame.draw.polygon(surf, inner_color, [(w*0.69, h*0.07), (w*0.66, h*0.03), (w*0.67, h*0.14)])
    eye_w, eye_h = int(w*0.09), int(h*0.12)
    left_eye = pygame.Rect(w*0.35, h*0.18, eye_w, eye_h)
    right_eye = pygame.Rect(w*0.56, h*0.18, eye_w, eye_h)
    eye_color = (20,20,20)

    if mood == 'happy':
        pygame.draw.arc(surf, eye_color, left_eye, 0, 3.14, 3)
        pygame.draw.arc(surf, eye_color, right_eye, 0, 3.14, 3)
    elif mood == 'angry':
        pygame.draw.line(surf, eye_color, (left_eye.x, left_eye.y), (left_eye.x+eye_w, left_eye.y+eye_h), 3)
        pygame.draw.line(surf, eye_color, (right_eye.x+eye_w, right_eye.y), (right_eye.x, right_eye.y+eye_h), 3)
    else:
        pygame.draw.ellipse(surf, (255,255,255), left_eye)
        pygame.draw.ellipse(surf, (255,255,255), right_eye)
        pygame.draw.ellipse(surf, eye_color, (left_eye.x+eye_w*0.28, left_eye.y+eye_h*0.22, eye_w*0.35, eye_h*0.55))
        pygame.draw.ellipse(surf, eye_color, (right_eye.x+eye_w*0.28, right_eye.y+eye_h*0.22, eye_w*0.35, eye_h*0.55))

    pygame.draw.circle(surf, (255,100,140), (int(w*0.5), int(h*0.30)), int(w*0.03))
    pygame.draw.line(surf, (140,40,40), (w*0.47, h*0.35), (w*0.53, h*0.35), 3)
    return surf

for name, color, atk, df, sp in CAT_PROFILES:
    cats.append({
        'name': name,
        'color': color,
        'atk': atk,
        'def': df,
        'spd': sp,
        'surfaces': {
            'normal': create_cat_surface((220,220), color, 'normal'),
            'happy': create_cat_surface((220,220), color, 'happy'),
            'angry': create_cat_surface((220,220), color, 'angry'),
        }
    })

# 背景

def draw_background(surface):
    surface.fill(SKY)
    pygame.draw.rect(surface, GROUND, (0, HEIGHT*0.6, WIDTH, HEIGHT*0.4))
    pygame.draw.circle(surface, (255, 230, 120), (WIDTH-80, 80), 40)

# 按鈕
class Button:
    def __init__(self, rect, text):
        self.rect = pygame.Rect(rect)
        self.text = text
    def draw(self, surf, hover=False):
        pygame.draw.rect(surf, BUTTON_BG, self.rect)
        pygame.draw.rect(surf, BUTTON_BORDER, self.rect, 2)
        label = FONT.render(self.text, True, BLACK)
        surf.blit(label, (self.rect.centerx - label.get_width()/2, self.rect.centery - label.get_height()/2))
    def is_hover(self, pos):
        return self.rect.collidepoint(pos)

fight_button = Button((WIDTH//2 - 60, HEIGHT - 90, 120, 50), "FIGHT!")
left_button = Button((60, HEIGHT - 90, 80, 50), "< 左")
right_button = Button((WIDTH-140, HEIGHT - 90, 80, 50), "右 >")

# 狀態變數
animating = False
anim_timer = 0
anim_duration = 60
player_pos = pygame.Vector2(WIDTH*0.25, HEIGHT*0.5)
enemy_pos = pygame.Vector2(WIDTH*0.75, HEIGHT*0.5)
player_offset = pygame.Vector2(0,0)
enemy_offset = pygame.Vector2(0,0)

# 敵人生成

def generate_enemy():
    template = random.choice(CAT_PROFILES)
    name, color, atk, df, sp = template
    surfset = {
        'normal': create_cat_surface((200,200), color, 'normal'),
        'angry': create_cat_surface((200,200), color, 'angry'),
        'happy': create_cat_surface((200,200), color, 'happy'),
    }
    return {'name': name+" (野貓)", 'color': color, 'atk': atk, 'def': df, 'spd': sp, 'surfaces': surfset}

current_enemy = generate_enemy()

# 戰鬥邏輯

def resolve_battle(player, enemy):
    player_power = player['atk']*1.5 + player['def'] + player['spd']
    enemy_power = enemy['atk']*1.5 + enemy['def'] + enemy['spd']
    player_roll = player_power + random.uniform(0,10)
    enemy_roll = enemy_power + random.uniform(0,10)
    if player_roll > enemy_roll:
        return 'player'
    elif enemy_roll > player_roll:
        return 'enemy'
    else:
        return random.choice(['player','enemy'])

# 主迴圈
running = True
result_text = ""
result_timer = 0
RESULT_DISPLAY_TIME = 120
player_mood = 'normal'
enemy_mood = 'normal'

while running:
    dt = clock.tick(FPS)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mx,my = event.pos
            if left_button.is_hover((mx,my)):
                selected_index = (selected_index - 1) % len(cats)
            elif right_button.is_hover((mx,my)):
                selected_index = (selected_index + 1) % len(cats)
            elif fight_button.is_hover((mx,my)) and not animating:
                animating = True
                anim_timer = 0
                player_mood = 'angry'
                enemy_mood = 'angry'
                current_enemy = generate_enemy()
                winner = resolve_battle(cats[selected_index], current_enemy)
                if winner == 'player':
                    score += 1
                    if score > highscore:
                        highscore = score
                        save_high_score(highscore)
                    result_text = '勝利！你的貓贏了！'
                    player_mood = 'happy'
                    enemy_mood = 'normal'
                else:
                    result_text = '失敗...野貓贏了。'
                    player_mood = 'normal'
                    enemy_mood = 'happy'
                result_timer = RESULT_DISPLAY_TIME
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT:
                selected_index = (selected_index - 1) % len(cats)
            elif event.key == pygame.K_RIGHT:
                selected_index = (selected_index + 1) % len(cats)
            elif event.key == pygame.K_SPACE and not animating:
                animating = True
                anim_timer = 0
                player_mood = 'angry'
                enemy_mood = 'angry'
                current_enemy = generate_enemy()
                winner = resolve_battle(cats[selected_index], current_enemy)
                if winner == 'player':
                    score += 1
                    if score > highscore:
                        highscore = score
                        save_high_score(highscore)
                    result_text = '勝利！你的貓贏了！'
                    player_mood = 'happy'
                    enemy_mood = 'normal'
                else:
                    result_text = '失敗...野貓贏了。'
                    player_mood = 'normal'
                    enemy_mood = 'happy'
                result_timer = RESULT_DISPLAY_TIME

    if animating:
        anim_timer += 1
        t = anim_timer / anim_duration
        if t>1: t=1
        player_offset.x = 100*(1-(1-t)**2)
        enemy_offset.x = -100*(1-(1-t)**2)
        if anim_timer >= anim_duration:
            animating = False
            player_offset.xy = (0,0)
            enemy_offset.xy = (0,0)

    draw_background(screen)
    player = cats[selected_index]
    pimg = player['surfaces'][player_mood]
    eimg = current_enemy['surfaces'][enemy_mood]
    screen.blit(pimg, (int(player_pos.x - pimg.get_width()/2 + player_offset.x), int(player_pos.y - pimg.get_height()/2)))
    screen.blit(eimg, (int(enemy_pos.x - eimg.get_width()/2 + enemy_offset.x), int(enemy_pos.y - eimg.get_height()/2)))

    selector_y = HEIGHT - 170
    gap = 240
    start_x = WIDTH//2 - gap
    for i, c in enumerate(cats):
        thumb = pygame.transform.smoothscale(c['surfaces']['normal'], (120,120))
        x = start_x + i*gap
        screen.blit(thumb, (x, selector_y))
        name_label = FONT.render(c['name'], True, BLACK)
        screen.blit(name_label, (x+60-name_label.get_width()/2, selector_y+120+6))
        rect = pygame.Rect(x, selector_y, 120, 120)
        pygame.draw.rect(screen, (255,150,50) if i==selected_index else (100,100,100), rect, 3)

    mx,my = pygame.mouse.get_pos()
    left_button.draw(screen, left_button.is_hover((mx,my)))
    right_button.draw(screen, right_button.is_hover((mx,my)))
    fight_button.draw(screen, fight_button.is_hover((mx,my)))

    score_label = BIGFONT.render(f"得分: {score}", True, BLACK)
    hs_label = FONT.render(f"最高分: {highscore}", True, BLACK)
    screen.blit(score_label, (20, 20))
    screen.blit(hs_label, (20, 70))

    if result_timer>0:
        result_surf = BIGFONT.render(result_text, True, BLACK)
        screen.blit(result_surf, (WIDTH//2 - result_surf.get_width()/2, 120))
        result_timer -= 1

    hint = FONT.render("← → 選擇貓 / 空白鍵或按 FIGHT 開始戰鬥", True, BLACK)
    screen.blit(hint, (WIDTH//2 - hint.get_width()/2, HEIGHT - 40))

    pygame.display.flip()

pygame.quit()
sys.exit()
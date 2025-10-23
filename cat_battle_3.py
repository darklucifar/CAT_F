"""
商城版本
"""
import pygame
import random
import sys
import platform

pygame.init()

# ===================== 字型設定 =====================
# 字型設定（跨平台中文支援）
sys_font = "Microsoft JhengHei"
if platform.system() == "Darwin":
    sys_font = "PingFang TC"
elif platform.system() == "Linux":
    sys_font = "Noto Sans CJK TC"

FONT = pygame.font.SysFont(sys_font, 36)
BIGFONT = pygame.font.SysFont(sys_font, 56)

# ===================== 顏色與畫面 =====================
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 100, 100)
GREEN = (100, 255, 100)
BLUE = (100, 100, 255)
GRAY = (200, 200, 200)

WIDTH, HEIGHT = 800, 650
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("貓咪大戰：強化商店版")

clock = pygame.time.Clock()

# ===================== 貓咪資料 =====================
class Cat:
    def __init__(self, name, color):
        self.name = name
        self.color = color
        self.attack = random.randint(3, 6)
        self.defense = random.randint(2, 5)
        self.speed = random.randint(2, 5)
        self.temp_boost = 0

    def draw(self, x, y):
        pygame.draw.circle(screen, self.color, (x, y), 60)
        label = FONT.render(self.name, True, BLACK)
        screen.blit(label, (x - label.get_width() // 2, y + 70))

cats = [
    Cat("橘子", (255, 200, 100)),
    Cat("雪球", (240, 240, 255)),
    Cat("墨墨", (80, 80, 120))
]

selected_cat_index = 0
score = 0

# ===================== 商店資料 =====================
shop_items = [
    {"name": "攻擊力 +1", "price": 3, "effect": "attack"},
    {"name": "防禦力 +1", "price": 3, "effect": "defense"},
    {"name": "速度 +1", "price": 3, "effect": "speed"},
    {"name": "必勝咬 (下場戰鬥攻+5)", "price": 5, "effect": "boost"},
    {"name": "治療藥水", "price": 4, "effect": "heal"},
    {"name": "超級能量包 (全屬+1)", "price": 8, "effect": "all"}
]

# ===================== 遊戲狀態 =====================
game_state = "menu"  # menu, battle, shop
battle_result = ""

# ===================== 輔助函式 =====================
def draw_text_center(text, font, color, y):
    label = font.render(text, True, color)
    screen.blit(label, (WIDTH // 2 - label.get_width() // 2, y))

def battle(cat):
    global score, battle_result
    enemy_power = random.randint(3, 10)
    power = cat.attack + cat.temp_boost + random.randint(-2, 2)
    cat.temp_boost = 0  # 清除臨時加成

    if power >= enemy_power:
        score += 1
        battle_result = f"勝利！獲得 1 分（目前 {score} 分）"
    else:
        battle_result = f"失敗！敵方太強啦～"


def buy_item(cat, item):
    global score, battle_result
    if score < item["price"]:
        battle_result = "金額不足！"
        return

    score -= item["price"]
    eff = item["effect"]

    if eff == "attack":
        cat.attack += 1
        battle_result = f"購買成功！{cat.name} 攻擊力 +1"
    elif eff == "defense":
        cat.defense += 1
        battle_result = f"購買成功！{cat.name} 防禦力 +1"
    elif eff == "speed":
        cat.speed += 1
        battle_result = f"購買成功！{cat.name} 速度 +1"
    elif eff == "boost":
        cat.temp_boost = 5
        battle_result = f"{cat.name} 下場戰鬥攻擊 +5！"
    elif eff == "heal":
        battle_result = f"{cat.name} 恢復活力！"
    elif eff == "all":
        cat.attack += 1
        cat.defense += 1
        cat.speed += 1
        battle_result = f"{cat.name} 全面強化！(攻防速 +1)"


# ===================== 主迴圈 =====================
while True:
    screen.fill(WHITE)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == pygame.KEYDOWN:
            if game_state == "menu":
                if event.key == pygame.K_LEFT:
                    selected_cat_index = (selected_cat_index - 1) % len(cats)
                elif event.key == pygame.K_RIGHT:
                    selected_cat_index = (selected_cat_index + 1) % len(cats)
                elif event.key == pygame.K_SPACE:
                    battle(cats[selected_cat_index])
                elif event.key == pygame.K_s:
                    game_state = "shop"
            elif game_state == "shop":
                if event.key == pygame.K_m:
                    game_state = "menu"

        elif event.type == pygame.MOUSEBUTTONDOWN:
            x, y = event.pos
            if game_state == "menu":
                # 點擊戰鬥區域
                if WIDTH//2 - 100 < x < WIDTH//2 + 100 and 450 < y < 500:
                    battle(cats[selected_cat_index])
                # 點擊商店
                if WIDTH//2 - 100 < x < WIDTH//2 + 100 and 520 < y < 570:
                    game_state = "shop"
            elif game_state == "shop":
                # 點擊商品
                for i, item in enumerate(shop_items):
                    bx, by = 200, 150 + i * 60
                    if bx < x < bx + 400 and by < y < by + 50:
                        buy_item(cats[selected_cat_index], item)

    # ===================== 畫面顯示 =====================
    if game_state == "menu":
        draw_text_center("貓咪大戰 - Game ", BIGFONT, BLACK, 40)

        cat = cats[selected_cat_index]
        cat.draw(WIDTH // 2, HEIGHT // 2 - 50)

        stats = f"攻:{cat.attack} 防:{cat.defense} 速:{cat.speed}"
        draw_text_center(stats, FONT, BLACK, 380)

        pygame.draw.rect(screen, GREEN, (WIDTH//2 - 100, 450, 200, 50))
        draw_text_center("開始戰鬥 (Space)", FONT, BLACK, 460)

        pygame.draw.rect(screen, BLUE, (WIDTH//2 - 100, 520, 200, 50))
        draw_text_center("商店 (S)", FONT, WHITE, 530)

        draw_text_center(f"分數: {score}", FONT, BLACK, 580)

        if battle_result:
            draw_text_center(battle_result, FONT, RED, 420)

    elif game_state == "shop":
        draw_text_center("商店-SHOP", BIGFONT, BLACK, 40)
        draw_text_center(f"分數: {score}", FONT, BLACK, 100)

        for i, item in enumerate(shop_items):
            pygame.draw.rect(screen, GRAY, (200, 150 + i * 60, 400, 50))
            label = FONT.render(f"{item['name']} (${item['price']})", True, BLACK)
            screen.blit(label, (220, 160 + i * 60))

        draw_text_center("按 M 返回主畫面", FONT, BLUE, 520)

        if battle_result:
            draw_text_center(battle_result, FONT, RED, 560)

    pygame.display.flip()
    clock.tick(60)

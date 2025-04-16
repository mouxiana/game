import pygame
import random
import math
import sys
import os
from pygame.locals import *

# === Score System ===
def read_highscores():
    try:
        with open("highscores.txt", "r") as f:
            return sorted([int(line.strip()) for line in f], reverse=True)[:3]
    except:
        return [0, 0, 0]

def save_highscores(score):
    scores = read_highscores() + [score]
    with open("highscores.txt", "w") as f:
        for s in sorted(scores, reverse=True)[:3]:
            f.write(f"{s}\n")

# === Game Initialization ===
if getattr(sys, 'frozen', False):
    base_dir = sys._MEIPASS  
else:
    base_dir = os.path.dirname(os.path.abspath(__file__))

pygame.init()
pygame.mixer.init()

WIDTH, HEIGHT = 1280, 720
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Flying Shooter")

# === Game Entities ===
class Bullet:
    def __init__(self, x, y, angle=90, is_player=False):
        self.rect = pygame.Rect(x-4, y-4, 8, 8)
        self.speed = 8
        self.color = (0, 0, 255) if is_player else (255, 0, 0)
        self.angle = math.radians(angle)

    def update(self):
        self.rect.x += math.cos(self.angle) * self.speed
        self.rect.y += math.sin(self.angle) * self.speed

class Enemy:
    def __init__(self, enemy_type):
        self.type = enemy_type
        if enemy_type == "C":
            self.image = enemy_c_img
            self.hp = 3
        else:
            self.image = enemy_a_img if enemy_type == "A" else enemy_b_img
            self.hp = 1 if enemy_type == "A" else 2
        self.rect = self.image.get_rect()
        self.rect.x = random.randint(50, WIDTH-50)
        self.rect.y = -self.rect.height
        self.shoot_timer = 0

# === Resource Loading ===
def load_resource(file, size=None):
    path = os.path.join(base_dir, "assets", file)
    try:
        img = pygame.image.load(path).convert_alpha()
        return pygame.transform.smoothscale(img, size) if size else img
    except Exception as e:
        print(f"Failed to load: {path}") 
        return pygame.Surface((100,100))

player_img = load_resource("0.png", (50, 100))
enemy_a_img = load_resource("11.png", (50, 70))
enemy_b_img = load_resource("12.png", (60, 90))
enemy_c_img = load_resource("13.png", (70, 100))
bg_img = load_resource("2.png", (WIDTH, HEIGHT))

# === Audio Setup ===
try:
    pygame.mixer.music.load(os.path.join(base_dir, "assets", "bgm.ogg"))
    pygame.mixer.music.set_volume(0.5)
    pygame.mixer.music.play(-1)
except Exception as e:
    print(f"Music error: {str(e)}")

# === Game State ===
player_rect = player_img.get_rect(center=(WIDTH//2, HEIGHT-100))
player_speed = 8
player_hp = 3
score = 0
enemies = []
player_bullets = []
enemy_bullets = []
clock = pygame.time.Clock()
running = True
game_over = False

# === Button Class ===
class Button:
    def __init__(self, text, x, y, width=200, height=50):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.font = pygame.font.Font(None, 36)  # Use default font
        self.color = (70, 130, 180)
        self.hover_color = (100, 150, 200)
    
    def draw(self, surface):
        mouse_pos = pygame.mouse.get_pos()
        color = self.hover_color if self.rect.collidepoint(mouse_pos) else self.color
        pygame.draw.rect(surface, color, self.rect)
        text_surf = self.font.render(self.text, True, (255,255,255))
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)

# === Game Over Screen ===
def game_over_screen():
    save_highscores(score)
    highscores = read_highscores()
    
    # Create buttons
    again_btn = Button("Play Again", WIDTH//2 - 220, HEIGHT//2 + 100)
    exit_btn = Button("Exit Game", WIDTH//2 + 20, HEIGHT//2 + 100)
    
    # Safe font initialization
    font = pygame.font.Font(None, 48)  # Use default font
    
    while True:
        # Handle events
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            if event.type == MOUSEBUTTONDOWN:
                if again_btn.rect.collidepoint(event.pos):
                    return True
                if exit_btn.rect.collidepoint(event.pos):
                    pygame.quit()
                    sys.exit()
        
        # Draw everything
        screen.fill((0,0,0))
        
        # Score display
        current_text = font.render(f"Final Score: {score}", True, (255,255,255))
        current_rect = current_text.get_rect(center=(WIDTH//2, HEIGHT//2 - 100))
        screen.blit(current_text, current_rect)
        
        # High scores
        hs_y = HEIGHT//2 - 30
        for i, hs in enumerate(highscores[:3]):
            hs_text = font.render(f"Top {i+1}: {hs}", True, (200,200,200))
            screen.blit(hs_text, (WIDTH//2 - 80, hs_y + i*50))
        
        # Buttons
        again_btn.draw(screen)
        exit_btn.draw(screen)
        pygame.display.flip()
        clock.tick(60)

# === Main Game Loop ===
while running:
    dt = clock.tick(60) / 1000
    
    # Event handling
    for event in pygame.event.get():
        if event.type == QUIT:
            running = False
    
    if not game_over:
        # Player movement
        keys = pygame.key.get_pressed()
        original_x, original_y = player_rect.x, player_rect.y
        
        if keys[K_a] and player_rect.left > 0:
            player_rect.x -= int(player_speed * dt * 60)
        if keys[K_d] and player_rect.right < WIDTH:
            player_rect.x += int(player_speed * dt * 60)
        if keys[K_w] and player_rect.top > 0:
            player_rect.y -= int(player_speed * dt * 60)
        if keys[K_s] and player_rect.bottom < HEIGHT:
            player_rect.y += int(player_speed * dt * 60)
        
        # Diagonal movement correction
        if (original_x != player_rect.x) and (original_y != player_rect.y):
            move_x = player_rect.x - original_x
            move_y = player_rect.y - original_y
            player_rect.x = original_x + move_x * 0.7071
            player_rect.y = original_y + move_y * 0.7071
        
        # Auto-shooting
        if pygame.time.get_ticks() % 15 == 0:
            player_bullets.append(Bullet(player_rect.centerx, player_rect.top, 90, True))
        
        # Enemy spawning
        if random.random() < 0.02 + (score * 0.0001):
            rand = random.randint(1, 10)
            enemy_type = "C" if rand == 1 else "B" if 2 <= rand <=4 else "A"
            enemies.append(Enemy(enemy_type))
    
    # Rendering
    screen.blit(bg_img, (0,0))
    
    # Bullet handling
    for bullet in player_bullets[:]:
        bullet.rect.y -= bullet.speed
        remove = False
        
        if bullet.rect.bottom < 0:
            remove = True
        else:
            for enemy in enemies[:]:
                if bullet.rect.colliderect(enemy.rect):
                    enemy.hp -= 1
                    remove = True
                    if enemy.hp <= 0:
                        if enemy.type == "C":
                            # Spawn two B enemies
                            left_b = Enemy("B")
                            left_b.rect.center = (enemy.rect.centerx-50, enemy.rect.centery)
                            enemies.append(left_b)
                            right_b = Enemy("B")
                            right_b.rect.center = (enemy.rect.centerx+50, enemy.rect.centery)
                            enemies.append(right_b)
                        score += 3 if enemy.type == "C" else (1 if enemy.type == "A" else 2)
                        enemies.remove(enemy)
        if remove and bullet in player_bullets:
            player_bullets.remove(bullet)
    
    # Enemy logic
    for enemy in enemies[:]:
        enemy.rect.y += 3
        
        if enemy.type == "B":
            enemy.shoot_timer += dt
            if enemy.shoot_timer >= 2:
                dx = player_rect.centerx - enemy.rect.centerx
                dy = player_rect.centery - enemy.rect.centery
                base_angle = math.degrees(math.atan2(dy, dx))
                
                for angle_offset in [-15, 0, 15]:
                    bullet = Bullet(enemy.rect.centerx, enemy.rect.bottom, base_angle + angle_offset)
                    enemy_bullets.append(bullet)
                enemy.shoot_timer = 0
        
        if player_rect.colliderect(enemy.rect):
            player_hp -= 1 if enemy.type == "A" else 2
            enemies.remove(enemy)
    
    # Enemy bullets
    for bullet in enemy_bullets[:]:
        bullet.update()
        if bullet.rect.colliderect(player_rect):
            player_hp -= 1
            enemy_bullets.remove(bullet)
        elif not screen.get_rect().colliderect(bullet.rect):
            enemy_bullets.remove(bullet)
    
    # Draw game objects
    screen.blit(player_img, player_rect)
    for enemy in enemies:
        screen.blit(enemy.image, enemy.rect)
    for bullet in player_bullets:
        pygame.draw.circle(screen, bullet.color, bullet.rect.center, 4)
    for bullet in enemy_bullets:
        pygame.draw.circle(screen, bullet.color, bullet.rect.center, 4)
    
    # HUD Display
    font = pygame.font.Font(None, 36)
    screen.blit(font.render(f"HP: {player_hp}", True, (255,255,255)), (10,10))
    screen.blit(font.render(f"Score: {score}", True, (255,255,255)), (WIDTH-150,10))
    
    pygame.display.flip()
    
    # Game over check
    if player_hp <= 0:
        game_over = True
        pygame.mixer.music.stop()
        if game_over_screen():  # Restart game
            # Reset game state
            player_hp = 3
            score = 0
            enemies.clear()
            player_bullets.clear()
            enemy_bullets.clear()
            player_rect.center = (WIDTH//2, HEIGHT-100)
            game_over = False
            pygame.mixer.music.play(-1)

pygame.quit()
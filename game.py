import pygame
import random
import math
import sys
import os
from pygame.locals import *

if getattr(sys, 'frozen', False):
    base_dir = sys._MEIPASS  
else:
    base_dir = os.path.dirname(os.path.abspath(__file__))

pygame.init()
pygame.mixer.init()

WIDTH, HEIGHT = 1280, 720
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("飞姬大作战")

base_dir = os.path.dirname(os.path.abspath(__file__))

class Bullet:
    def __init__(self, x, y, angle=90, is_player=False):
        self.rect = pygame.Rect(x-4, y-4, 8, 8)
        self.speed = 8
        self.color = (255, 0, 0)  
        self.angle = math.radians(angle)  

    def update(self):
        self.rect.x += math.cos(self.angle) * self.speed
        self.rect.y += math.sin(self.angle) * self.speed

class Enemy:
    def __init__(self, enemy_type):
        self.type = enemy_type
        self.image = enemy_a_img if enemy_type == "A" else enemy_b_img
        self.rect = self.image.get_rect()
        self.rect.x = random.randint(50, WIDTH-50)
        self.rect.y = -self.rect.height
        self.hp = 1 if enemy_type == "A" else 2
        self.shoot_timer = 0

def handle_movement(dt):
    keys = pygame.key.get_pressed()
    original_x = player_rect.x
    original_y = player_rect.y
    
    if keys[K_a] and player_rect.left > 0:
        player_rect.x -= int(player_speed * dt * 60)
    if keys[K_d] and player_rect.right < WIDTH:
        player_rect.x += int(player_speed * dt * 60)
    if keys[K_w] and player_rect.top > 0:
        player_rect.y -= int(player_speed * dt * 60)
    if keys[K_s] and player_rect.bottom < HEIGHT:
        player_rect.y += int(player_speed * dt * 60)
    
    if (original_x != player_rect.x) and (original_y != player_rect.y):
        move_x = player_rect.x - original_x
        move_y = player_rect.y - original_y
        player_rect.x = original_x + move_x * 0.7071
        player_rect.y = original_y + move_y * 0.7071


def load_resource(file, size=None):
    path = os.path.join(base_dir, "assets", file)
    try:
        img = pygame.image.load(path).convert_alpha()
        return pygame.transform.smoothscale(img, size) if size else img
    except Exception as e:
        print(f"资源加载失败：{path}")  
        return pygame.Surface((100,100))


player_img = load_resource("0.png", (60, 80))
enemy_a_img = load_resource("11.png", (50, 70))
enemy_b_img = load_resource("12.png", (60, 90))
bg_img = load_resource("2.png", (WIDTH, HEIGHT))


try:
    bgm_path = os.path.join(base_dir, "assets", "bgm.ogg")
    pygame.mixer.music.load(bgm_path)
    pygame.mixer.music.set_volume(0.5)
    pygame.mixer.music.play(-1)
except Exception as e:
    print(f"背景音乐错误：{str(e)} - 路径：{bgm_path}")


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

def game_over_screen():
    screen.fill((0,0,0))
    font = pygame.font.Font(None, 48)
    text = font.render(f"游戏结束！得分：{score}", True, (255,255,255))
    screen.blit(text, text.get_rect(center=(WIDTH//2, HEIGHT//2)))
    pygame.display.flip()
    pygame.time.wait(3000)

while running:
    dt = clock.tick(60) / 1000
    

    for event in pygame.event.get():
        if event.type == QUIT:
            running = False

    if not game_over:
        handle_movement(dt)
        

        if pygame.time.get_ticks() % 15 == 0:
            player_bullets.append(Bullet(player_rect.centerx, player_rect.top, 90, True))


        if random.random() < 0.02 + (score * 0.0001):
            enemies.append(Enemy("B") if random.randint(1,4) == 1 else Enemy("A"))


    screen.blit(bg_img, (0,0))
    

    for bullet in player_bullets[:]:
        bullet.rect.y -= bullet.speed
        if bullet.rect.bottom < 0:
            player_bullets.remove(bullet)
        else:
            for enemy in enemies[:]:
                if bullet.rect.colliderect(enemy.rect):
                    enemy.hp -= 1
                    player_bullets.remove(bullet)
                    if enemy.hp <= 0:
                        enemies.remove(enemy)
                        score += 1 if enemy.type == "A" else 2


    for enemy in enemies[:]:
        enemy.rect.y += 3
        
        if enemy.type == "B":
            enemy.shoot_timer += dt
            if enemy.shoot_timer >= 2:

                dx = player_rect.centerx - enemy.rect.centerx
                dy = player_rect.centery - enemy.rect.centery
                base_angle = math.degrees(math.atan2(dy, dx))
                

                for angle_offset in [-15, 0, 15]:
                    bullet = Bullet(
                        enemy.rect.centerx,
                        enemy.rect.bottom,
                        base_angle + angle_offset
                    )
                    enemy_bullets.append(bullet)
                enemy.shoot_timer = 0


        if player_rect.colliderect(enemy.rect):
            player_hp -= 1 if enemy.type == "A" else 2
            enemies.remove(enemy)


    for bullet in enemy_bullets[:]:
        bullet.update()
        if bullet.rect.colliderect(player_rect):
            player_hp -= 1
            enemy_bullets.remove(bullet)
        elif not screen.get_rect().colliderect(bullet.rect):
            enemy_bullets.remove(bullet)


    screen.blit(player_img, player_rect)
    for enemy in enemies:
        screen.blit(enemy.image, enemy.rect)
    for bullet in player_bullets:
        pygame.draw.circle(screen, (0,0,255), bullet.rect.center, 4)
    for bullet in enemy_bullets:
        pygame.draw.circle(screen, (255,0,0), bullet.rect.center, 4)
    

    font = pygame.font.Font(None, 36)
    screen.blit(font.render(f"HP: {player_hp}", True, (255,255,255)), (10,10))
    screen.blit(font.render(f"Score: {score}", True, (255,255,255)), (WIDTH-150,10))
    
    pygame.display.flip()


    if player_hp <= 0:
        game_over = True
        pygame.mixer.music.stop()
        game_over_screen()
        running = False

pygame.quit()
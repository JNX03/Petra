import pygame
import cv2
import torch
import numpy as np
from ultralytics import YOLO
import requests
from io import BytesIO
import sys
import random
import time

pygame.init()

SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Underwater Object Detection Game")
clock = pygame.time.Clock()
FPS = 30

def load_image(url, size=None):
    response = requests.get(url)
    image = pygame.image.load(BytesIO(response.content)).convert_alpha()
    if size:
        image = pygame.transform.scale(image, size)
    return image

player_url = "https://firebasestorage.googleapis.com/v0/b/gcxsys.appspot.com/o/f2.png?alt=media&token=a01aa678-4437-4408-8479-e69ddb05c7f3"
coil_url = "https://firebasestorage.googleapis.com/v0/b/gcxsys.appspot.com/o/image.png?alt=media&token=e7cd5083-7d87-466b-9296-8d171014f6be"
background_url = "https://firebasestorage.googleapis.com/v0/b/gcxsys.appspot.com/o/DALLE_2024-10-02_11.02.21_-_A_cartoon-style_background_image_resembling_an_underwater_scene_with_light_aqua-green_tones._The_top_section_has_simplified_exaggerated_wave_patterns.webp?alt=media&token=f290632a-10ad-461e-9622-7ed49ccc7999"
speed_boost_url = "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcRTP_BimSKRnc-Z93BUPZQ6EHf99-PG4HxqnQ&s"
magnet_url = "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcTT-MUVL0ITqUSJOqOahlPlOLyaF-H3hEgiHg&s"
x2_url = "https://www.shutterstock.com/image-illustration/x2-3d-rendering-on-white-260nw-1467989987.jpg"
bomb_url = "https://images.rawpixel.com/image_png_800/czNmcy1wcml2YXRlL3Jhd3BpeGVsX2ltYWdlcy93ZWJzaXRlX2NvbnRlbnQvam9iNjc4LTE0Ni1wLWwxNjRweGtuLnBuZw.png"
boss_image_url = "https://firebasestorage.googleapis.com/v0/b/gcxsys.appspot.com/o/image-removebg-preview%20(63).png?alt=media&token=d83eab77-3b43-49e4-8a12-1906986e2e72"

try:
    player_img = load_image(player_url, size=(128, 128))
    coil_img = load_image(coil_url, size=(64, 64))
    background_img = load_image(background_url, size=(SCREEN_WIDTH, SCREEN_HEIGHT))
    speed_boost_img = load_image(speed_boost_url, size=(64, 64))
    magnet_img = load_image(magnet_url, size=(64, 64))
    x2_img = load_image(x2_url, size=(64, 64))
    bomb_img = load_image(bomb_url, size=(64, 64))
    boss_img = load_image(boss_image_url, size=(200, 200))
except:
    pygame.quit()
    sys.exit()

player_rect = player_img.get_rect(center=(SCREEN_WIDTH // 4, SCREEN_HEIGHT // 2))
player_speed = 3

def draw_text(text, size, color, x, y):
    font = pygame.font.Font(None, size)
    text_surface = font.render(text, True, color)
    screen.blit(text_surface, (x, y))

def start_menu():
    start_button = pygame.Rect(SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 - 50, 200, 100)
    running = True
    while running:
        screen.fill((0, 105, 148))
        draw_text("Underwater Object Game", 50, (255, 255, 255), SCREEN_WIDTH // 2 - 200, SCREEN_HEIGHT // 2 - 150)
        pygame.draw.rect(screen, (255, 255, 255), start_button)
        draw_text("Start", 36, (0, 0, 0), start_button.x + 50, start_button.y + 25)
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if start_button.collidepoint(event.pos):
                    return

def pause_menu():
    resume_button = pygame.Rect(SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2, 200, 100)
    paused = True
    while paused:
        screen.fill((50, 50, 50))
        draw_text("Paused", 80, (255, 255, 255), SCREEN_WIDTH // 2 - 150, SCREEN_HEIGHT // 2 - 150)
        pygame.draw.rect(screen, (255, 255, 255), resume_button)
        draw_text("Resume", 36, (0, 0, 0), resume_button.x + 50, resume_button.y + 25)
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if resume_button.collidepoint(event.pos):
                    paused = False

def game_over_screen(score):
    restart_button = pygame.Rect(SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2, 200, 100)
    running = True
    while running:
        screen.fill((0, 0, 0))
        draw_text("Game Over", 80, (255, 0, 0), SCREEN_WIDTH // 2 - 200, SCREEN_HEIGHT // 2 - 150)
        draw_text(f"Score: {score}", 50, (255, 255, 255), SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 - 50)
        pygame.draw.rect(screen, (255, 255, 255), restart_button)
        draw_text("Restart", 36, (0, 0, 0), restart_button.x + 50, restart_button.y + 25)
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if restart_button.collidepoint(event.pos):
                    return True
        return False

def spawn_coil():
    coil_rect = coil_img.get_rect(topleft=(SCREEN_WIDTH + random.randint(0, 200), random.randint(SCREEN_HEIGHT // 4, SCREEN_HEIGHT - 64)))
    return coil_rect

def spawn_bomb():
    bomb_rect = bomb_img.get_rect(topleft=(SCREEN_WIDTH + random.randint(0, 200), random.randint(SCREEN_HEIGHT // 4, SCREEN_HEIGHT - 64)))
    return bomb_rect

def spawn_power_up():
    power_up_type = random.choice(["speed_boost", "magnet", "x2"])
    power_up_img = {"speed_boost": speed_boost_img, "magnet": magnet_img, "x2": x2_img}[power_up_type]
    power_up_rect = power_up_img.get_rect(topleft=(SCREEN_WIDTH + random.randint(0, 400), random.randint(SCREEN_HEIGHT // 4, SCREEN_HEIGHT - 64)))
    return power_up_type, power_up_img, power_up_rect, time.time()

def boss_fight():
    boss_rect = boss_img.get_rect(center=(SCREEN_WIDTH - 150, SCREEN_HEIGHT // 2))
    player_rect.center = (SCREEN_WIDTH // 4, SCREEN_HEIGHT // 2)
    shots_fired = 0
    shot_img = pygame.Surface((10, 10))
    shot_img.fill((255, 0, 0))
    shot_rects = []
    running = True

    while running:
        clock.tick(FPS)
        screen.fill((0, 105, 148))
        screen.blit(boss_img, boss_rect)
        screen.blit(player_img, player_rect)

        draw_text(f"Shots Fired: {shots_fired}/25", 36, (255, 255, 255), 10, 10)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pause_menu()
        
        keys = pygame.key.get_pressed()
        if keys[pygame.K_UP]:
            shot_rect = shot_img.get_rect(center=(player_rect.centerx + 50, player_rect.centery))
            shot_rects.append(shot_rect)

        for shot in shot_rects:
            shot.x += 10
            if shot.colliderect(boss_rect):
                shot_rects.remove(shot)
                shots_fired += 1
                if shots_fired >= 25:
                    running = False
            elif shot.x > SCREEN_WIDTH:
                shot_rects.remove(shot)

        for shot in shot_rects:
            screen.blit(shot_img, shot)

        pygame.display.flip()

def game_loop(camera_index):
    try:
        model = YOLO("best.pt")
    except:
        pygame.quit()
        sys.exit()

    cap = cv2.VideoCapture(camera_index)
    if not cap.isOpened():
        pygame.quit()
        sys.exit()

    previous_positions = {}
    target_labels = ["green", "blue", "orange"]
    score = 0
    coils = []
    bombs = []
    power_ups = []
    speed_boost_active = False
    magnet_active = False
    x2_active = False
    power_up_timer = 0
    power_up_name = ""
    background_x = 0
    background_speed = 1
    coil_spawn_timer = 0
    bomb_spawn_timer = 0
    power_up_spawn_timer = 0
    in_boss_fight = False
    running = True

    while running:
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pause_menu()

        if in_boss_fight:
            boss_fight()
            in_boss_fight = False
            continue

        ret, frame = cap.read()
        if not ret:
            break

        frame = cv2.resize(frame, (SCREEN_WIDTH, SCREEN_HEIGHT))
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        results = model(frame_rgb)
        detections = results[0].boxes.data.tolist()
        current_positions = {}
        object_detected = False

        for det in detections:
            x1, y1, x2, y2, conf, cls = det
            label = model.names[int(cls)]
            if label in target_labels:
                center_x = int((x1 + x2) / 2)
                center_y = int((y1 + y2) / 2)
                current_positions[int(cls)] = (center_x, center_y)
                object_detected = True
                if int(cls) in previous_positions:
                    prev_x, prev_y = previous_positions[int(cls)]
                    delta_y = center_y - prev_y
                    if delta_y < -5:
                        player_rect.y += player_speed
                    elif delta_y > 5:
                        player_rect.y -= player_speed
                cv2.rectangle(frame, (int(x1), int(y1)), (int(x2), int(y2)), (0, 255, 0), 2)
                cv2.putText(frame, label, (int(x1), int(y1) - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (36, 255, 12), 2)

        if not object_detected:
            player_rect.y -= player_speed * 2

        previous_positions = current_positions.copy()
        player_rect.y = max(SCREEN_HEIGHT // 4, min(player_rect.y, SCREEN_HEIGHT - player_rect.height))

        for coil_rect in coils:
            coil_rect.x -= player_speed
            if player_rect.colliderect(coil_rect):
                score += 2 if x2_active else 1
                coils.remove(coil_rect)

        for bomb_rect in bombs:
            bomb_rect.x -= player_speed
            if player_rect.colliderect(bomb_rect):
                running = False

        for power_up_type, power_up_img, power_up_rect, spawn_time in power_ups:
            power_up_rect.x -= player_speed
            if player_rect.colliderect(power_up_rect):
                if power_up_type == "speed_boost":
                    speed_boost_active = True
                    power_up_name = "Speed Boost"
                elif power_up_type == "magnet":
                    magnet_active = True
                    power_up_name = "Magnet"
                elif power_up_type == "x2":
                    x2_active = True
                    power_up_name = "X2"
                power_up_timer = 300
                power_ups.remove((power_up_type, power_up_img, power_up_rect, spawn_time))

        if power_up_timer > 0:
            power_up_timer -= 1
        else:
            speed_boost_active = magnet_active = x2_active = False
            power_up_name = ""

        if coil_spawn_timer <= 0 and len(coils) < 5:
            coils.append(spawn_coil())
            coil_spawn_timer = random.randint(60, 180)

        if bomb_spawn_timer <= 0 and len(bombs) < 3:
            bombs.append(spawn_bomb())
            bomb_spawn_timer = random.randint(120, 300)

        if power_up_spawn_timer <= 0 and len(power_ups) < 2:
            power_ups.append(spawn_power_up())
            power_up_spawn_timer = random.randint(300, 600)

        coil_spawn_timer -= 1
        bomb_spawn_timer -= 1
        power_up_spawn_timer -= 1

        if score >= 5 and not in_boss_fight:
            coils.clear()
            bombs.clear()
            power_ups.clear()
            in_boss_fight = True

        background_x -= background_speed
        if background_x <= -SCREEN_WIDTH:
            background_x = 0

        screen.blit(background_img, (background_x, 0))
        screen.blit(background_img, (background_x + SCREEN_WIDTH, 0))

        for coil_rect in coils:
            screen.blit(coil_img, coil_rect)

        for power_up_type, power_up_img, power_up_rect, _ in power_ups:
            screen.blit(power_up_img, power_up_rect)

        for bomb_rect in bombs:
            screen.blit(bomb_img, bomb_rect)

        screen.blit(player_img, player_rect)
        draw_text(f"Score: {score}", 36, (255, 255, 255), 10, 10)
        if power_up_name:
            draw_text(f"Power-Up: {power_up_name} - Timer: {power_up_timer//FPS} s", 36, (255, 255, 0), 10, 50)

        pygame.display.flip()

    cap.release()
    if game_over_screen(score):
        main()
    else:
        pygame.quit()

def main():
    start_menu()
    camera_index = 0
    if camera_index == -1:
        pygame.quit()
        sys.exit()

    while True:
        game_loop(camera_index)

main()

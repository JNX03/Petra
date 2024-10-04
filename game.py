import pygame
import cv2
import torch
import numpy as np
from ultralytics import YOLO
import requests
from io import BytesIO
import sys
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

player_url = "https://cdn.discordapp.com/attachments/754347629604896898/1290896745999372360/f2.png?ex=66fe20c7&is=66fccf47&hm=3f194fb7164b655da4bf6bdf28b4e43fbda5813df3890e1d2f22c25fb92cca8b&"
coil_url = "https://cdn.discordapp.com/attachments/754347629604896898/1290897191858077768/image.png?ex=66fe2132&is=66fccfb2&hm=7a1f710133672cbfbb186b0d449b475be101fe783b0564ff017e4ca4062557dd&"
background_url = "https://cdn.discordapp.com/attachments/754347629604896898/1290896777662169139/DALLE_2024-10-02_11.02.21_-_A_cartoon-style_background_image_resembling_an_underwater_scene_with_light_aqua-green_tones._The_top_section_has_simplified_exaggerated_wave_patterns.webp?ex=66fe20cf&is=66fccf4f&hm=5c2f37a63bedffc192cad337db21da1e2a3eaf446e37d90806fcdc587df02c10&"

try:
    player_img = load_image(player_url, size=(64, 64))
    coil_img = load_image(coil_url, size=(32, 32))
    background_img = load_image(background_url, size=(SCREEN_WIDTH, SCREEN_HEIGHT))
except:
    pygame.quit()
    sys.exit()

player_rect = player_img.get_rect(center=(SCREEN_WIDTH // 4, SCREEN_HEIGHT // 2))
player_speed = 3

def auto_detect_camera():
    for index in range(10):
        cap = cv2.VideoCapture(index)
        if cap.read()[0]:
            cap.release()
            return index
    return -1

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
    base_image_taken = False
    base_image = None

    coil_rect = coil_img.get_rect(topleft=(SCREEN_WIDTH, np.random.randint(SCREEN_HEIGHT // 4, SCREEN_HEIGHT - 32)))

    background_x = 0
    background_speed = 1

    running = True
    while running:
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        ret, frame = cap.read()
        if not ret:
            break

        frame = cv2.resize(frame, (SCREEN_WIDTH, SCREEN_HEIGHT))
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        if not base_image_taken:
            base_image = frame_rgb.copy()
            base_image_taken = True

        results = model(frame_rgb)
        detections = results[0].boxes.data.tolist()
        current_positions = {}
        debug_label = ""
        direction = ""
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
                        if label == "green":
                            player_rect.y += player_speed
                        elif label == "orange":
                            player_rect.y += player_speed * 2
                        elif label == "blue":
                            player_rect.y += player_speed * 3
                        direction = "down"
                    elif delta_y > 5:
                        if label == "green":
                            player_rect.y -= player_speed
                        elif label == "orange":
                            player_rect.y -= player_speed * 2
                        elif label == "blue":
                            player_rect.y -= player_speed * 3
                        direction = "up"
                    debug_label = label
                cv2.rectangle(frame, (int(x1), int(y1)), (int(x2), int(y2)), (0, 255, 0), 2)
                cv2.putText(frame, label, (int(x1), int(y1) - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (36, 255, 12), 2)

        if not object_detected:
            player_rect.y -= player_speed // 2

        previous_positions = current_positions.copy()
        player_rect.y = max(SCREEN_HEIGHT // 4, min(player_rect.y, SCREEN_HEIGHT - player_rect.height))

        if player_rect.colliderect(coil_rect):
            score += 1
            coil_rect.x = SCREEN_WIDTH
            coil_rect.y = np.random.randint(SCREEN_HEIGHT // 4, SCREEN_HEIGHT - 32)

        coil_rect.x -= player_speed
        if coil_rect.right < 0:
            coil_rect.x = SCREEN_WIDTH
            coil_rect.y = np.random.randint(SCREEN_HEIGHT // 4, SCREEN_HEIGHT - 32)

        background_x -= background_speed
        if background_x <= -SCREEN_WIDTH:
            background_x = 0

        screen.blit(background_img, (background_x, 0))
        screen.blit(background_img, (background_x + SCREEN_WIDTH, 0))
        screen.blit(coil_img, coil_rect)
        screen.blit(player_img, player_rect)

        draw_text(f"Score: {score}", 36, (255, 255, 255), 10, 10)
        debug_text = f"Label: {debug_label} | Direction: {direction}"
        draw_text(debug_text, 36, (255, 255, 255), 10, 50)

        pygame.display.flip()

    cap.release()
    pygame.quit()

def main():
    start_menu()
    camera_index = auto_detect_camera()
    if camera_index == -1:
        print("No camera found.")
        pygame.quit()
        sys.exit()

    while True:
        game_loop(camera_index)

main()

import pygame
import math
import sys
from PIL import Image, ImageDraw, ImageFont
import json
import random

pygame.init()

# Screen setup
WIDTH, HEIGHT = 1280,800
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Sanskrit Word Game")

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (100, 149, 237)
GREEN = (34, 177, 76)
RED = (200, 50, 50)
GRAY = (220, 220, 220)

#Score
points=0 

# Load Devanagari font
FONT_PATH = "NotoSansDevanagari-Regular.ttf"
sentence_font = ImageFont.truetype(FONT_PATH, 36)
letter_font = ImageFont.truetype(FONT_PATH, 40)
result_font = ImageFont.truetype(FONT_PATH, 40)

# Button setup
button_rect = pygame.Rect(WIDTH//2 - 60, HEIGHT - 150, 120, 50)
show_next = False 

with open("dataset.json", "r", encoding="utf-8") as f:
    sentences = json.load(f)

# Game Data
current_index = 0 
question = sentences[current_index]

sentence = question["sanskrit_sentence"].replace(question["missing_word"], "______")
correct_word = question["missing_word"]
letters = question["syllables"] + question["distractors"]
indices = list(range(len(letters)))

# Shuffle the indices
random.shuffle(indices)

# Rearrange letters according to shuffled indices
letters = [letters[i] for i in indices]

# Circle setup
circle_radius = 200
center_x, center_y = WIDTH // 2, HEIGHT // 2 + 50
letter_positions = []
angle_step = 2 * math.pi / len(letters)

for i, letter in enumerate(letters):
    angle = i * angle_step
    x = center_x + circle_radius * math.cos(angle)
    y = center_y + circle_radius * math.sin(angle)
    letter_positions.append((x, y))

# Game state
selected_indices = []
result_text = ""

def render_text(text, font, color=(0, 0, 0)):
    # Create a temporary image
    img = Image.new("RGBA", (800, 100), (255, 255, 255, 0))
    draw = ImageDraw.Draw(img)
    draw.text((0, 0), text, font=font, fill=color)
    bbox = img.getbbox()
    if bbox:
        img = img.crop(bbox)  # trim extra space

    mode = img.mode
    size = img.size
    data = img.tobytes()
    return pygame.image.fromstring(data, size, mode)

def draw_navbar():
    # Navbar background
    pygame.draw.rect(screen, (30, 30, 60), (0, 0, WIDTH, 60))

    # Question number
    q_text = f"प्रश्न: {current_index+1}/{len(sentences)}"
    q_surface = render_text(q_text, sentence_font, WHITE)
    screen.blit(q_surface, (20, 15))

    # Points
    points_text = f"अंक: {points}"
    points_surface = render_text(points_text, sentence_font, WHITE)
    screen.blit(points_surface, (WIDTH//2 - 50, 15))

    level_rect=render_text("स्तर 1",sentence_font,WHITE).get_rect(topleft=(WIDTH//2 + 200,15))
    pygame.draw.rect(screen,(80,80,180),level_rect.inflate(20,10),border_radius=8)
    screen.blit(render_text("स्तर 1",sentence_font,WHITE),level_rect)

    # Concept button
    concept_text = "सिद्धान्त"
    concept_surface = render_text(concept_text, sentence_font, WHITE)
    concept_rect = concept_surface.get_rect(topright=(WIDTH-20, 15))
    pygame.draw.rect(screen, (80, 80, 180), concept_rect.inflate(20, 10), border_radius=8)
    screen.blit(concept_surface, concept_rect)

def draw_game():
    screen.fill(WHITE)
    draw_navbar()
    # Draw sentence
    sentence_surface = render_text(sentence, sentence_font, BLACK)
    sentence_rect = sentence_surface.get_rect(center=(WIDTH // 2, 100))
    screen.blit(sentence_surface, sentence_rect)

    # Draw letters in circle
    for i, (x, y) in enumerate(letter_positions):
        result_color = BLUE if i in selected_indices else GRAY
        pygame.draw.circle(screen, result_color, (int(x), int(y)), 50)

        letter_surface = render_text(letters[i], letter_font, BLACK)
        rect = letter_surface.get_rect(center=(x, y))
        screen.blit(letter_surface, rect)

    # Draw connecting lines
    if len(selected_indices) > 1:
        for j in range(len(selected_indices) - 1):
            x1, y1 = letter_positions[selected_indices[j]]
            x2, y2 = letter_positions[selected_indices[j + 1]]
            pygame.draw.line(screen, RED, (x1, y1), (x2, y2), 4)

    # Draw result
    if result_text:
        result_color = GREEN if result_text == "उचित" else RED
        result_surface = render_text(result_text, result_font, result_color)
        result_rect = result_surface.get_rect(center=(WIDTH // 2, HEIGHT - 50))
        screen.blit(result_surface, result_rect)

        # Draw "Next" button only after answer
        if show_next:
            # Position the button just below the result
            button_rect.center = (WIDTH//2, HEIGHT - 100)
            pygame.draw.rect(screen, BLUE, button_rect, border_radius=10)

            button_surface = render_text("आगे", sentence_font, WHITE)
            button_rect_text = button_surface.get_rect(center=button_rect.center)
            screen.blit(button_surface, button_rect_text)

    pygame.display.flip()



def check_word():
    global result_text, show_next

    chosen = "".join([letters[i] for i in selected_indices])
    if chosen == correct_word:
        global points
        result_text = "उचित"
        points+=10
        show_next = True 
    else:
        result_text = "अनुचित"
        show_next = False  
        selected_indices.clear()  



def get_clicked_letter(mouse_pos):
    for i, (x, y) in enumerate(letter_positions):
        if math.hypot(mouse_pos[0] - x, mouse_pos[1] - y) < 50:
            return i
    return None

def load_next_question():
    global current_index, question, sentence, correct_word, letters, letter_positions, selected_indices, result_text, show_next

    current_index += 1
    print("DEBUG: current_index =", current_index, "total =", len(sentences))

    question = sentences[current_index]
    sentence = question["sanskrit_sentence"].replace(question["missing_word"], "______")
    correct_word = question["missing_word"]
    letters = question["syllables"] + question["distractors"]
    random.shuffle(letters)

    # Reset state
    selected_indices = []
    result_text = ""
    show_next = False

    # Recalculate positions
    letter_positions.clear()
    angle_step = 2 * math.pi / len(letters)
    for i, letter in enumerate(letters):
        angle = i * angle_step
        x = center_x + circle_radius * math.cos(angle)
        y = center_y + circle_radius * math.sin(angle)
        letter_positions.append((x, y))


# Main loop
running = True
while running:
    draw_game()
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.MOUSEBUTTONDOWN:
            # If user clicks a letter (only when not waiting for next)
            idx = get_clicked_letter(event.pos)
            if idx is not None and idx not in selected_indices:
                selected_indices.append(idx)

            # If user clicks the "आगे" button
            if show_next and button_rect.collidepoint(event.pos):
                load_next_question()



        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:  # Check word
                check_word()
            elif event.key == pygame.K_BACKSPACE:  # Reset selection
                selected_indices = []
                result_text = ""



pygame.quit()
sys.exit()

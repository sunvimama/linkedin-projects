import pygame
import sys
import time

pygame.init()
width, height = 800, 500
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("Elastic Collision Simulator")
clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 30)

# Input box class
class InputBox:
    def __init__(self, x, y, w, h, text=''):
        self.rect = pygame.Rect(x, y, w, h)
        self.color = (0, 0, 0)
        self.text = text
        self.txt_surface = font.render(text, True, self.color)
        self.active = False
        self.cursor_visible = True
        self.cursor_timer = 0

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            self.active = self.rect.collidepoint(event.pos)
        if event.type == pygame.KEYDOWN and self.active:
            if event.key == pygame.K_RETURN:
                self.active = False
            elif event.key == pygame.K_BACKSPACE:
                self.text = self.text[:-1]
            else:
                self.text += event.unicode
            self.txt_surface = font.render(self.text, True, self.color)

    def update(self):
        self.cursor_timer += clock.get_time()
        if self.cursor_timer >= 500:
            self.cursor_timer = 0
            self.cursor_visible = not self.cursor_visible

    def draw(self, screen):
        # Highlight active box
        if self.active:
            pygame.draw.rect(screen, (255, 255, 150), self.rect)  # Light yellow
        else:
            pygame.draw.rect(screen, (220, 220, 220), self.rect)  # Light gray

        pygame.draw.rect(screen, self.color, self.rect, 2)
        screen.blit(self.txt_surface, (self.rect.x + 5, self.rect.y + 5))

        if self.active and self.cursor_visible:
            cursor_x = self.rect.x + 5 + self.txt_surface.get_width() + 2
            cursor_y = self.rect.y + 5
            pygame.draw.line(screen, (0, 0, 0), (cursor_x, cursor_y), (cursor_x, cursor_y + self.txt_surface.get_height()), 2)

    def get_value(self):
        try:
            return float(self.text)
        except ValueError:
            return 0

# Physics calculation
def elastic_collision(vx1, vx2, m1, m2):
    u1 = vx1 / scale
    u2 = vx2 / scale
    v1 = ((m1 - m2) / (m1 + m2)) * u1 + ((2 * m2) / (m1 + m2)) * u2
    v2 = ((2 * m1) / (m1 + m2)) * u1 + ((m2 - m1) / (m1 + m2)) * u2
    return v1 * scale, v2 * scale

# Input screen
def input_screen():
    input_boxes = [
        InputBox(300, 80, 140, 32, '2'),   # m1
        InputBox(300, 130, 140, 32, '3'),   # u1
        InputBox(300, 180, 140, 32, '1'),   # m2
        InputBox(300, 230, 140, 32, '-2'),  # u2
    ]
    labels = ['Mass 1 (kg):', 'Velocity 1 (m/s):', 'Mass 2 (kg):', 'Velocity 2 (m/s):']
    start_button = pygame.Rect(320, 300, 160, 40)

    while True:
        screen.fill((255, 255, 255))

        for i, label in enumerate(labels):
            label_color = (0, 0, 0)
            if input_boxes[i].active:
                label_color = (200, 0, 0)
            screen.blit(font.render(label, True, label_color), (150, 90 + i * 50))
            input_boxes[i].draw(screen)

        pygame.draw.rect(screen, (0, 200, 0), start_button)
        screen.blit(font.render("Start Simulation", True, (255, 255, 255)), (start_button.x + 10, start_button.y + 10))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            for box in input_boxes:
                box.handle_event(event)
            if event.type == pygame.MOUSEBUTTONDOWN and start_button.collidepoint(event.pos):
                return [box.get_value() for box in input_boxes]

        for box in input_boxes:
            box.update()

        pygame.display.flip()
        clock.tick(30)

# === Run input screen ===
m1, u1, m2, u2 = input_screen()

# === Start simulation ===
x1, x2 = 200, 600
scale = 60
radius = 20
vx1, vx2 = u1 * scale, u2 * scale
y = height // 2
last_collision_time = 0
collision_cooldown = 0.2

def draw_simulation():
    u1_display = vx1 / scale
    u2_display = vx2 / scale
    info = [
        f"Mass 1: {m1} kg   |   Mass 2: {m2} kg",
        f"Velocity 1: {u1_display:.2f} m/s   |   Velocity 2: {u2_display:.2f} m/s",
    ]
    for i, text in enumerate(info):
        screen.blit(font.render(text, True, (0, 0, 0)), (20, 20 + i * 30))

# Simulation loop
running = True
while running:
    dt = clock.tick(60) / 1000
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    x1 += vx1 * dt
    x2 += vx2 * dt
    current_time = time.time()

    if abs(x1 - x2) <= 2 * radius and (current_time - last_collision_time) > collision_cooldown:
        if (vx1 - vx2) * (x1 - x2) < 0:
            vx1, vx2 = elastic_collision(vx1, vx2, m1, m2)
            last_collision_time = current_time

    if x1 - radius <= 0 or x1 + radius >= width:
        vx1 = -vx1
    if x2 - radius <= 0 or x2 + radius >= width:
        vx2 = -vx2

    screen.fill((255, 255, 255))
    pygame.draw.rect(screen, (0, 0, 0), (0, 0, width, height), 3)
    pygame.draw.circle(screen, (255, 0, 0), (int(x1), y), radius)
    pygame.draw.circle(screen, (0, 0, 255), (int(x2), y), radius)
    draw_simulation()
    pygame.display.flip()

pygame.quit()
sys.exit()

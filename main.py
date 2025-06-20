import pygame
import sys
import random


pygame.init()

WIDTH, HEIGHT = 800, 600
PADDLE_WIDTH, PADDLE_HEIGHT = 100, 15
BALL_RADIUS = 10
BRICK_WIDTH, BRICK_HEIGHT = 75, 30
FPS = 60
BUTTON_WIDTH, BUTTON_HEIGHT = 200, 50

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
COLORS = [RED, GREEN, BLUE]


def load_texture(path, size=None):
    try:
        texture = pygame.image.load(path)
        if size:
            texture = pygame.transform.scale(texture, size)
        return texture
    except:
        print(f"Не удалось загрузить текстуру: {path}")
        surf = pygame.Surface((size if size else (50, 50)))
        surf.fill((random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)))
        return surf


screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Арканоид")
clock = pygame.time.Clock()

font_large = pygame.font.SysFont("Arial", 50)
font_medium = pygame.font.SysFont("Arial", 30)
font_small = pygame.font.SysFont("Arial", 24)

class Button:
    def __init__(self, x, y, width, height, text, color, hover_color):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.hover_color = hover_color
        self.is_hovered = False

    def draw(self):
        color = self.hover_color if self.is_hovered else self.color
        pygame.draw.rect(screen, color, self.rect, border_radius=10)
        pygame.draw.rect(screen, WHITE, self.rect, 2, border_radius=10)

        text_surface = font_medium.render(self.text, True, WHITE)
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)

    def check_hover(self, mouse_pos):
        self.is_hovered = self.rect.collidepoint(mouse_pos)
        return self.is_hovered

    def is_clicked(self, mouse_pos, mouse_click):
        return self.rect.collidepoint(mouse_pos) and mouse_click

class Paddle:
    def __init__(self):
        self.width = PADDLE_WIDTH
        self.height = PADDLE_HEIGHT
        self.x = WIDTH // 2 - self.width // 2
        self.y = HEIGHT - 50
        self.speed = 8
        self.texture = None

    def set_texture(self, texture_path):
        self.texture = load_texture(texture_path, (self.width, self.height))

    def draw(self):
        if self.texture:
            screen.blit(self.texture, (self.x, self.y))
        else:
            pygame.draw.rect(screen, WHITE, (self.x, self.y, self.width, self.height))

    def move(self, direction):
        if direction == "left" and self.x > 0:
            self.x -= self.speed
        if direction == "right" and self.x < WIDTH - self.width:
            self.x += self.speed


class Ball:
    def __init__(self):
        self.reset()
        self.texture = None

    def set_texture(self, texture_path):
        diameter = BALL_RADIUS * 2
        self.texture = load_texture(texture_path, (diameter, diameter))

    def reset(self):
        self.radius = BALL_RADIUS
        self.x = WIDTH // 2
        self.y = HEIGHT // 2
        self.dx = 4 * random.choice([-1, 1])
        self.dy = -4
        self.lost = False

    def draw(self):
        if self.texture:
            screen.blit(self.texture, (self.x - self.radius, self.y - self.radius))
        else:
            pygame.draw.circle(screen, WHITE, (int(self.x), int(self.y)), self.radius)

    def move(self):
        self.x += self.dx
        self.y += self.dy

        if self.x <= self.radius or self.x >= WIDTH - self.radius:
            self.dx *= -1
        if self.y <= self.radius:
            self.dy *= -1

        if self.y >= HEIGHT:
            self.lost = True

    def collide_paddle(self, paddle):
        if (paddle.x <= self.x <= paddle.x + paddle.width and
                paddle.y <= self.y + self.radius <= paddle.y + paddle.height):
            # Меняем только вертикальное направление, горизонтальное оставляем как было
            self.dy *= -1

    def collide_brick(self, bricks):
        hit_brick = None
        for brick in bricks:
            if brick.visible and (brick.x <= self.x <= brick.x + brick.width and
                                  brick.y <= self.y <= brick.y + brick.height):
                hit_brick = brick
                break

        if hit_brick:
            if (self.x < hit_brick.x and self.dx > 0) or (self.x > hit_brick.x + hit_brick.width and self.dx < 0):
                self.dx *= -1
            else:
                self.dy *= -1
            return hit_brick
        return None


class Brick:
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.width = BRICK_WIDTH
        self.height = BRICK_HEIGHT
        self.color = color
        self.visible = True

    def draw(self):
        if self.visible:
            pygame.draw.rect(screen, self.color, (self.x, self.y, self.width, self.height))


def create_bricks():
    bricks = []
    for row in range(5):
        for col in range(WIDTH // BRICK_WIDTH):
            brick = Brick(col * BRICK_WIDTH, row * BRICK_HEIGHT + 50, random.choice(COLORS))
            bricks.append(brick)
    return bricks


def draw_text(text, font, color, x, y):
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect(center=(x, y))
    screen.blit(text_surface, text_rect)


# Основные игровые объекты
paddle = Paddle()
ball = Ball()
bricks = create_bricks()
score = 0
lives = 3

# Загрузка текстур
paddle.set_texture("paddle_texture.png")
ball.set_texture("ball_texture.png")

# Кнопки
start_button = Button(WIDTH // 2 - BUTTON_WIDTH // 2, HEIGHT // 2, BUTTON_WIDTH, BUTTON_HEIGHT, "Играть", BLACK, BLUE)
restart_button = Button(WIDTH // 2 - BUTTON_WIDTH // 2, HEIGHT // 2 + 100, BUTTON_WIDTH, BUTTON_HEIGHT,
                        "Начать сначала", BLACK, BLUE)

game_state = "start"

running = True
while running:
    mouse_pos = pygame.mouse.get_pos()
    mouse_click = False

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                mouse_click = True

    screen.fill(BLACK)

    if game_state == "start":
        draw_text("АРКАНОИД", font_large, WHITE, WIDTH // 2, HEIGHT // 2 - 100)
        start_button.check_hover(mouse_pos)
        start_button.draw()

        if start_button.is_clicked(mouse_pos, mouse_click):
            game_state = "game"

    elif game_state == "game":
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            paddle.move("left")
        if keys[pygame.K_RIGHT]:
            paddle.move("right")

        ball.move()

        ball.collide_paddle(paddle)

        hit_brick = ball.collide_brick(bricks)
        if hit_brick:
            hit_brick.visible = False
            score += 10

        if ball.lost:
            lives -= 1
            if lives <= 0:
                game_state = "game_over"
            else:
                ball.reset()

        if all(not brick.visible for brick in bricks):
            game_state = "win"

        paddle.draw()
        ball.draw()
        for brick in bricks:
            brick.draw()

        draw_text(f"Счет: {score}", font_small, WHITE, 70, 20)
        draw_text(f"Жизни: {lives}", font_small, WHITE, WIDTH - 70, 20)

    elif game_state == "game_over":
        draw_text("ИГРА ОКОНЧЕНА", font_large, RED, WIDTH // 2, HEIGHT // 2 - 50)
        draw_text(f"Ваш счет: {score}", font_medium, WHITE, WIDTH // 2, HEIGHT // 2 + 20)
        restart_button.check_hover(mouse_pos)
        restart_button.draw()

        if restart_button.is_clicked(mouse_pos, mouse_click):
            bricks = create_bricks()
            ball.reset()
            paddle = Paddle()
            score = 0
            lives = 3
            game_state = "game"

    elif game_state == "win":
        draw_text("ПОБЕДА!", font_large, GREEN, WIDTH // 2, HEIGHT // 2 - 50)
        draw_text(f"Ваш счет: {score}", font_medium, WHITE, WIDTH // 2, HEIGHT // 2 + 20)
        restart_button.check_hover(mouse_pos)
        restart_button.draw()

        if restart_button.is_clicked(mouse_pos, mouse_click):
            bricks = create_bricks()
            ball.reset()
            paddle = Paddle()
            score = 0
            lives = 3
            game_state = "game"

    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
sys.exit()
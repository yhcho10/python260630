import pygame
import sys
import random
from enum import Enum

# Pygame 초기화
pygame.init()

# 게임 설정
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
FPS = 60

# 색상 정의
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
YELLOW = (255, 255, 0)
CYAN = (0, 255, 255)
MAGENTA = (255, 0, 255)
ORANGE = (255, 165, 0)
PURPLE = (128, 0, 128)

class Block(pygame.sprite.Sprite):
    """블럭 클래스"""
    def __init__(self, x, y, width, height, color):
        super().__init__()
        self.rect = pygame.Rect(x, y, width, height)
        self.color = color
        self.image = pygame.Surface((width, height))
        self.image.fill(color)
    
    def draw(self, surface):
        pygame.draw.rect(surface, self.color, self.rect)
        pygame.draw.rect(surface, WHITE, self.rect, 2)

class Paddle(pygame.sprite.Sprite):
    """패들 클래스"""
    def __init__(self, x, y, width, height):
        super().__init__()
        self.rect = pygame.Rect(x, y, width, height)
        self.width = width
        self.height = height
        self.speed = 7
    
    def update(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and self.rect.left > 0:
            self.rect.x -= self.speed
        if keys[pygame.K_RIGHT] and self.rect.right < WINDOW_WIDTH:
            self.rect.x += self.speed
    
    def draw(self, surface):
        pygame.draw.rect(surface, BLUE, self.rect)

class Ball(pygame.sprite.Sprite):
    """공 클래스"""
    def __init__(self, x, y, radius):
        super().__init__()
        self.x = x
        self.y = y
        self.radius = radius
        self.speed_x = 4 * random.choice([-1, 1])
        self.speed_y = -4
    
    def update(self):
        self.x += self.speed_x
        self.y += self.speed_y
        
        # 벽에 충돌
        if self.x - self.radius < 0 or self.x + self.radius > WINDOW_WIDTH:
            self.speed_x = -self.speed_x
        
        if self.y - self.radius < 0:
            self.speed_y = -self.speed_y
    
    def draw(self, surface):
        pygame.draw.circle(surface, RED, (int(self.x), int(self.y)), self.radius)
    
    def get_rect(self):
        return pygame.Rect(self.x - self.radius, self.y - self.radius, 
                          self.radius * 2, self.radius * 2)

class BlockGame:
    """블럭깨기 게임 메인 클래스"""
    def __init__(self):
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("블럭깨기 게임")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 36)
        self.large_font = pygame.font.Font(None, 72)
        
        self.paddle = Paddle(WINDOW_WIDTH // 2 - 150, WINDOW_HEIGHT - 50, 300, 15)
        self.ball = Ball(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2, 6)
        self.blocks = pygame.sprite.Group()
        self.score = 0
        self.game_over = False
        self.won = False
        
        self.create_blocks()
    
    def create_blocks(self):
        """블럭 생성"""
        block_width = 75
        block_height = 20
        colors = [RED, ORANGE, YELLOW, GREEN, CYAN, BLUE, MAGENTA, PURPLE]
        
        for row in range(5):
            for col in range(10):
                x = col * (block_width + 5) + 10
                y = row * (block_height + 5) + 30
                color = colors[row % len(colors)]
                block = Block(x, y, block_width, block_height, color)
                self.blocks.add(block)
    
    def check_collisions(self):
        """충돌 감지"""
        # 패들과 공의 충돌
        ball_rect = self.ball.get_rect()
        if ball_rect.colliderect(self.paddle.rect):
            self.ball.speed_y = -self.ball.speed_y
            # 패들의 위치에 따라 공의 x 속도 조정
            paddle_center = self.paddle.rect.centerx
            ball_center = self.ball.x
            distance = ball_center - paddle_center
            self.ball.speed_x += distance / 50
        
        # 블럭과 공의 충돌
        hit_blocks = []
        for block in self.blocks:
            if ball_rect.colliderect(block.rect):
                hit_blocks.append(block)
                self.score += 10
        
        for block in hit_blocks:
            self.blocks.remove(block)
            self.ball.speed_y = -self.ball.speed_y
    
    def update(self):
        """게임 업데이트"""
        if not self.game_over and not self.won:
            self.paddle.update()
            self.ball.update()
            self.check_collisions()
            
            # 공이 아래로 떨어짐
            if self.ball.y > WINDOW_HEIGHT:
                self.game_over = True
            
            # 모든 블럭 제거됨
            if len(self.blocks) == 0:
                self.won = True
    
    def draw(self):
        """게임 화면 그리기"""
        self.screen.fill(BLACK)
        
        # 점수 표시
        score_text = self.font.render(f"Score: {self.score}", True, WHITE)
        self.screen.blit(score_text, (10, 10))
        
        # 게임 오브젝트 그리기
        self.paddle.draw(self.screen)
        self.ball.draw(self.screen)
        
        for block in self.blocks:
            block.draw(self.screen)
        
        # 게임 오버
        if self.game_over:
            game_over_text = self.large_font.render("GAME OVER", True, RED)
            restart_text = self.font.render("R: 다시시작 | Q: 종료", True, WHITE)
            text_rect = game_over_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2))
            restart_rect = restart_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 60))
            self.screen.blit(game_over_text, text_rect)
            self.screen.blit(restart_text, restart_rect)
        
        # 게임 승리
        if self.won:
            won_text = self.large_font.render("YOU WIN!", True, GREEN)
            restart_text = self.font.render("R: 다시시작 | Q: 종료", True, WHITE)
            text_rect = won_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2))
            restart_rect = restart_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 60))
            self.screen.blit(won_text, text_rect)
            self.screen.blit(restart_text, restart_rect)
        
        pygame.display.flip()
    
    def reset(self):
        """게임 초기화"""
        self.paddle = Paddle(WINDOW_WIDTH // 2 - 150, WINDOW_HEIGHT - 50, 300, 15)
        self.ball = Ball(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2, 6)
        self.blocks.empty()
        self.score = 0
        self.game_over = False
        self.won = False
        self.create_blocks()
    
    def run(self):
        """게임 실행"""
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_q:
                        running = False
                    if event.key == pygame.K_r and (self.game_over or self.won):
                        self.reset()
            
            self.update()
            self.draw()
            self.clock.tick(FPS)
        
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    game = BlockGame()
    game.run()

import pygame
import random
import math

# Initialize Pygame
pygame.init()

# Game Constants
SCREEN_WIDTH = 400
SCREEN_HEIGHT = 600
FPS = 60

# Physics Constants
GRAVITY = 0.6          # Acceleration downward (pixels/frame²)
FLAP_STRENGTH = -12    # Upward velocity when flapping (pixels/frame)
PIPE_GAP = 120         # Space between pipes (pixels)
PIPE_WIDTH = 60
PIPE_SPEED = 4         # Horizontal velocity of pipes (pixels/frame)
BIRD_RADIUS = 15

# Colors
WHITE = (255, 255, 255)
BLUE = (135, 206, 235)
GREEN = (34, 139, 34)
BLACK = (0, 0, 0)
GOLD = (255, 215, 0)

# Setup Display
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Flappy Bird - Physics Project")
clock = pygame.time.Clock()
font = pygame.font.Font(None, 36)
large_font = pygame.font.Font(None, 72)

class Bird:
    """Bird object with physics properties"""
    def __init__(self):
        self.x = 60
        self.y = 300
        self.radius = BIRD_RADIUS
        self.velocity = 0      # pixels/frame (positive = downward)
        self.color = GOLD
    
    def update(self):
        """Update bird physics: apply gravity and update position"""
        # Apply gravity (constant acceleration)
        self.velocity += GRAVITY
        
        # Update position (kinematics: y = y₀ + v*t + 0.5*a*t²)
        # Since t=1 frame: y = y₀ + v + 0.5*a
        self.y += self.velocity
    
    def flap(self):
        """Apply upward impulse (simulates muscle force)"""
        self.velocity = FLAP_STRENGTH
    
    def draw(self, surface):
        """Draw bird as circle with eye"""
        pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), self.radius)
        # Eye
        pygame.draw.circle(surface, BLACK, (int(self.x + 5), int(self.y - 5)), 3)
    
    def check_collision(self, pipes):
        """Check collision with pipes and ground"""
        # Ground collision
        if self.y + self.radius >= SCREEN_HEIGHT:
            return True
        
        # Ceiling collision
        if self.y - self.radius <= 0:
            return True
        
        # Pipe collision (circle to rectangle)
        for pipe in pipes:
            # Check if bird's x-range overlaps with pipe's x-range
            if self.x + self.radius > pipe['x'] and self.x - self.radius < pipe['x'] + PIPE_WIDTH:
                # Check collision with top pipe
                if self.y - self.radius < pipe['top_height']:
                    return True
                # Check collision with bottom pipe
                if self.y + self.radius > pipe['bottom_y']:
                    return True
        
        return False

class Pipe:
    """Pipe obstacle"""
    def __init__(self, x):
        self.x = x
        min_height = 50
        max_height = SCREEN_HEIGHT - PIPE_GAP - 50
        self.top_height = random.uniform(min_height, max_height)
        self.bottom_y = self.top_height + PIPE_GAP
        self.passed = False
    
    def update(self):
        """Move pipe left"""
        self.x -= PIPE_SPEED
    
    def draw(self, surface):
        """Draw top and bottom pipes"""
        # Top pipe
        pygame.draw.rect(surface, GREEN, (self.x, 0, PIPE_WIDTH, self.top_height))
        pygame.draw.rect(surface, (26, 107, 26), (self.x, 0, PIPE_WIDTH, self.top_height), 2)
        
        # Bottom pipe
        bottom_height = SCREEN_HEIGHT - self.bottom_y
        pygame.draw.rect(surface, GREEN, (self.x, self.bottom_y, PIPE_WIDTH, bottom_height))
        pygame.draw.rect(surface, (26, 107, 26), (self.x, self.bottom_y, PIPE_WIDTH, bottom_height), 2)
    
    def is_offscreen(self):
        """Check if pipe has moved off screen"""
        return self.x + PIPE_WIDTH < 0

class Game:
    """Main game logic"""
    def __init__(self):
        self.bird = Bird()
        self.pipes = []
        self.score = 0
        self.game_running = True
        self.game_over = False
        self.frame_count = 0
        
        # Generate first pipe
        self.pipes.append(Pipe(SCREEN_WIDTH))
    
    def handle_events(self):
        """Handle user input"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    if not self.game_over:
                        self.bird.flap()
                    else:
                        self.reset()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if not self.game_over:
                    self.bird.flap()
                else:
                    self.reset()
        return True
    
    def update(self):
        """Update game state"""
        if self.game_over:
            return
        
        self.frame_count += 1
        
        # Update bird physics
        self.bird.update()
        
        # Update pipes
        for pipe in self.pipes:
            pipe.update()
            
            # Score when passing pipe
            if not pipe.passed and pipe.x + PIPE_WIDTH < self.bird.x:
                pipe.passed = True
                self.score += 1
        
        # Remove off-screen pipes
        self.pipes = [p for p in self.pipes if not p.is_offscreen()]
        
        # Generate new pipe if needed
        if len(self.pipes) == 0 or self.pipes[-1].x < SCREEN_WIDTH - 200:
            self.pipes.append(Pipe(SCREEN_WIDTH))
        
        # Check collision
        if self.bird.check_collision(self.pipes):
            self.game_over = True
    
    def reset(self):
        """Reset game"""
        self.bird = Bird()
        self.pipes = [Pipe(SCREEN_WIDTH)]
        self.score = 0
        self.game_over = False
        self.frame_count = 0
    
    def draw(self):
        """Draw game state"""
        # Background gradient (simple version)
        for y in range(SCREEN_HEIGHT):
            # Gradient from light blue to lighter blue
            ratio = y / SCREEN_HEIGHT
            r = int(135 + (224 - 135) * ratio)
            g = int(206 + (240 - 206) * ratio)
            b = int(235)
            pygame.draw.line(screen, (r, g, b), (0, y), (SCREEN_WIDTH, y))
        
        # Draw pipes
        for pipe in self.pipes:
            pipe.draw(screen)
        
        # Draw bird
        self.bird.draw(screen)
        
        # Draw score
        score_text = font.render(f"Score: {self.score}", True, BLACK)
        score_bg = pygame.Surface((150, 50))
        score_bg.set_alpha(180)
        score_bg.fill(WHITE)
        screen.blit(score_bg, (10, 10))
        screen.blit(score_text, (20, 20))
        
        # Draw game over screen
        if self.game_over:
            # Semi-transparent overlay
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            overlay.set_alpha(200)
            overlay.fill(BLACK)
            screen.blit(overlay, (0, 0))
            
            # Game over text
            game_over_text = large_font.render("Game Over!", True, WHITE)
            final_score_text = font.render(f"Final Score: {self.score}", True, WHITE)
            
            # Physics note
            physics_note = ""
            if self.score > 5:
                physics_note = f"Gravity: {GRAVITY} px/frame²"
            elif self.score > 0:
                physics_note = "You felt the acceleration of gravity!"
            else:
                physics_note = "Flap to escape gravity!"
            physics_text = font.render(physics_note, True, (200, 200, 255))
            
            restart_text = font.render("Click or Press SPACE to restart", True, (200, 255, 200))
            
            # Center text
            screen.blit(game_over_text, (SCREEN_WIDTH//2 - game_over_text.get_width()//2, 100))
            screen.blit(final_score_text, (SCREEN_WIDTH//2 - final_score_text.get_width()//2, 200))
            screen.blit(physics_text, (SCREEN_WIDTH//2 - physics_text.get_width()//2, 280))
            screen.blit(restart_text, (SCREEN_WIDTH//2 - restart_text.get_width()//2, 380))
        
        # Instructions
        instruction_text = font.render("Click or SPACE to flap", True, BLACK)
        instr_bg = pygame.Surface((instruction_text.get_width() + 20, 40))
        instr_bg.set_alpha(180)
        instr_bg.fill(WHITE)
        screen.blit(instr_bg, (10, SCREEN_HEIGHT - 50))
        screen.blit(instruction_text, (20, SCREEN_HEIGHT - 40))
        
        pygame.display.flip()

def main():
    """Main game loop"""
    game = Game()
    running = True
    
    while running:
        running = game.handle_events()
        game.update()
        game.draw()
        clock.tick(FPS)
    
    pygame.quit()

if __name__ == "__main__":
    print("Flappy Bird - Physics Project")
    print(f"Physics Constants:")
    print(f"  Gravity: {GRAVITY} px/frame²")
    print(f"  Flap strength: {FLAP_STRENGTH} px/frame")
    print(f"  Pipe gap: {PIPE_GAP} pixels")
    print(f"  Pipe speed: {PIPE_SPEED} px/frame")
    print("\nClick or press SPACE to flap!")
    print("Controls: Click mouse or press SPACE")
    
    main()
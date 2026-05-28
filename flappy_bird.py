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
GRAVITY = 0.6
FLAP_STRENGTH = -12
PIPE_GAP = 300
PIPE_WIDTH = 60
PIPE_SPEED = 4
BIRD_RADIUS = 15

# Game States
STATE_MAIN_MENU = "MAIN_MENU"
STATE_INPUT_SELECT = "INPUT_SELECT"
STATE_LOADING = "LOADING"
STATE_PLAYING = "PLAYING"
STATE_GAME_OVER = "GAME_OVER"
STATE_SETTINGS = "SETTINGS"
STATE_CREDITS = "CREDITS"

# Input Methods
INPUT_CLICK = "CLICK"
INPUT_SPACE = "SPACE"
INPUT_ARROW = "ARROW"
INPUT_ALL = "ALL 3"

# Colors
WHITE = (255, 255, 255)
BLUE = (135, 206, 235)
GREEN = (34, 139, 34)
BLACK = (0, 0, 0)
GOLD = (255, 215, 0)
YELLOW = (255, 255, 0)
DARK_GRAY = (100, 100, 100)
LIGHT_GREEN = (0, 150, 0)
DARK_BLUE = (25, 25, 112)
ORANGE = (255, 165, 0)

# Setup Display
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Flappy Bird - Physics Project")
clock = pygame.time.Clock()
font = pygame.font.Font(None, 36)
large_font = pygame.font.Font(None, 72)
small_font = pygame.font.Font(None, 24)
title_font = pygame.font.Font(None, 90)
huge_title_font = pygame.font.Font(None, 75)
button_font = pygame.font.Font(None, 32)
tiny_font = pygame.font.Font(None, 18)

# Physics tips for loading screen
PHYSICS_TIPS = [
    "Gravity: 10 m/s² downward",
    "Kinematics: y = yi + v*t + ½at²",
    "Momentum: Mass × Velocity",
    "Energy: Potential + Kinetic",
    "Kinetic Energy: ½mv²",
    "Potential Energy: mgh",
    "Impulse: Force × Time",
    "Work: Force × Distance",
    "Power: Work / Time",
    "Newton's 2nd Law: F = ma",
    "Weight: Force due to Gravity",
    "Acceleration: Change in Velocity",
    "Velocity: Change in Position",
    "Newton's 1st Law: Objects in motion stay in motion",
    "Elastic Collision: Momentum & Energy Conserved",
    "Inelastic Collision: Momentum Conserved",
    "Centripetal Force: mv²/r",
    "Friction: Opposes Motion",
    "Terminal Velocity: Max speed under gravity",
    "Escape Velocity: Speed to escape gravity",
]

class AnimatedBird:
    """Bird with wings and animation"""
    def __init__(self, x, y, weight=1.0):
        self.x = x
        self.y = y
        self.radius = BIRD_RADIUS
        self.velocity = 0
        self.color = GOLD
        self.wing_angle = 0
        self.wing_flap_speed = 0.15
        self.eye_blink = 0
        self.weight = weight

    def update(self):
        """Update bird physics"""
        self.velocity += GRAVITY
        self.y += self.velocity
        self.wing_angle += self.wing_flap_speed

    def animate_idle(self):
        """Gentle idle animation for menu"""
        self.wing_angle += 0.08
        self.y += math.sin(self.wing_angle * 0.5) * 0.3

    def flap(self):
        """Apply upward impulse - affected by weight"""
        self.velocity = FLAP_STRENGTH / self.weight
    
    def draw(self, surface, animated=False):
        """Draw detailed bird with wings and eye"""
        # Body (main circle)
        pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), self.radius)
        
        # Wing animation
        wing_offset = math.sin(self.wing_angle) * 8
        
        # Left wing
        wing_left_x = int(self.x - self.radius + 3)
        wing_left_y = int(self.y - 2)
        wing_points_left = [
            (wing_left_x, wing_left_y),
            (wing_left_x - 10, wing_left_y - wing_offset),
            (wing_left_x - 8, wing_left_y + 6)
        ]
        pygame.draw.polygon(surface, ORANGE, wing_points_left)
        
        # Right wing
        wing_right_x = int(self.x + self.radius - 3)
        wing_right_y = int(self.y - 2)
        wing_points_right = [
            (wing_right_x, wing_right_y),
            (wing_right_x + 10, wing_right_y - wing_offset),
            (wing_right_x + 8, wing_right_y + 6)
        ]
        pygame.draw.polygon(surface, ORANGE, wing_points_right)
        
        # Eye (with blinking)
        eye_x = int(self.x + 5)
        eye_y = int(self.y - 5)
        
        self.eye_blink = (self.eye_blink + 0.05) % (2 * math.pi)
        eye_size = max(1, int(3 * abs(math.cos(self.eye_blink))))
        
        pygame.draw.circle(surface, BLACK, (eye_x, eye_y), eye_size)
        
        # Beak
        beak_x = int(self.x + self.radius + 2)
        beak_y = int(self.y)
        pygame.draw.polygon(surface, ORANGE, [
            (beak_x, beak_y - 2),
            (beak_x + 6, beak_y),
            (beak_x, beak_y + 2)
        ])
    
    def check_collision(self, pipes):
        """Check collision with pipes and ground"""
        if self.y + self.radius >= SCREEN_HEIGHT:
            return True
        if self.y - self.radius <= 0:
            return True
        
        for pipe in pipes:
            if self.x + self.radius > pipe.x and self.x - self.radius < pipe.x + PIPE_WIDTH:
                if self.y - self.radius < pipe.top_height:
                    return True
                if self.y + self.radius > pipe.bottom_y:
                    return True
        
        return False

class Pipe:
    """Pipe obstacle"""
    def __init__(self, x, gap=PIPE_GAP):
        self.x = x
        min_height = 50
        max_height = SCREEN_HEIGHT - gap - 40
        self.top_height = random.uniform(min_height, max_height)
        self.bottom_y = self.top_height + gap
        self.passed = False
    
    def update(self):
        self.x -= PIPE_SPEED
    
    def draw(self, surface):
        pygame.draw.rect(surface, GREEN, (self.x, 0, PIPE_WIDTH, self.top_height))
        pygame.draw.rect(surface, (26, 107, 26), (self.x, 0, PIPE_WIDTH, self.top_height), 2)
        
        bottom_height = SCREEN_HEIGHT - self.bottom_y
        pygame.draw.rect(surface, GREEN, (self.x, self.bottom_y, PIPE_WIDTH, bottom_height))
        pygame.draw.rect(surface, (26, 107, 26), (self.x, self.bottom_y, PIPE_WIDTH, bottom_height), 2)
    
    def is_offscreen(self):
        return self.x + PIPE_WIDTH < 0

class Button:
    """Clickable button"""
    def __init__(self, x, y, width, height, text, color=(100, 100, 100)):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.hover = False
    
    def draw(self, surface):
        color = tuple(min(c + 30, 255) for c in self.color) if self.hover else self.color
        pygame.draw.rect(surface, color, self.rect, border_radius=8)
        pygame.draw.rect(surface, WHITE, self.rect, 2, border_radius=8)
        
        text_render = button_font.render(self.text, True, WHITE)
        text_rect = text_render.get_rect(center=self.rect.center)
        surface.blit(text_render, text_rect)
    
    def is_clicked(self, pos):
        return self.rect.collidepoint(pos)
    
    def update_hover(self, pos):
        self.hover = self.rect.collidepoint(pos)

class Game:
    """Main game logic"""
    def __init__(self):
        self.bird = AnimatedBird(60, 300)
        self.pipes = []
        self.score = 0
        self.game_running = True
        self.frame_count = 0
        self.menu_frame_count = 0  # Track frames for menu animations

        # Game State
        self.state = STATE_MAIN_MENU
        self.input_method = None
        self.loading_progress = 0
        self.loading_timer = 0
        self.current_tip = 0  # Track current physics tip
        self.game_over_tip = ""  # Random tip displayed on game over
        self.music_enabled = True
        self.brightness = 100  # 0-100
        self.bird_weight = 1.5  # Bird weight for physics (1.0 = normal, higher = harder)
        self.dragging_slider = False
        self.dragging_weight_slider = False
        
        # Audio system
        self.music_loaded = False
        self.collision_sound = None
        try:
            pygame.mixer.init(frequency=22050, size=-16, channels=1, buffer=512)
            if pygame.mixer.get_init():
                # Generate collision sound first
                self.collision_sound = self.generate_collision_sound()

                try:
                    pygame.mixer.music.load("background_music.mp3")
                    pygame.mixer.music.set_volume(0.5)
                    self.music_loaded = True
                    pygame.mixer.music.play(-1)
                except pygame.error:
                    pass
                except Exception:
                    pass
        except Exception:
            pass
        
        # Buttons
        self.play_button = Button(100, 300, 200, 50, "PLAY", (25, 100, 200))
        self.credits_button = Button(100, 380, 200, 50, "CREDITS", (200, 100, 25))
        self.settings_button = Button(100, 460, 200, 50, "SETTINGS", (100, 100, 100))
        self.back_button = Button(20, 20, 80, 40, "BACK", (100, 100, 100))
        self.play_again_button = Button(50, 450, 150, 50, "PLAY AGAIN", (0, 150, 0))
        self.exit_menu_button = Button(220, 450, 150, 50, "EXIT TO MENU", (200, 50, 50))
        
        # Input selection buttons
        self.input_buttons = [
            Button(50, 170, 300, 60, "CLICK", (0, 120, 200)),
            Button(50, 270, 300, 60, "SPACE BAR", (200, 120, 0)),
            Button(50, 370, 300, 60, "ARROW KEYS", (200, 0, 120)),
            Button(50, 470, 300, 60, "ALL 3", (150, 0, 150)),
        ]
        
        # Pipes
        self.pipes.append(Pipe(SCREEN_WIDTH))

    def generate_collision_sound(self):
        """Generate a retro game over sound (descending pitch)"""
        try:
            sample_rate = 22050
            duration = 0.6  # 600ms 
            frames = int(sample_rate * duration)

            # Generate descending pitch (classic game over sound)
            samples = []
            start_freq = 800
            end_freq = 200

            for i in range(frames):
                # Linear frequency
                progress = i / frames
                current_freq = start_freq - (start_freq - end_freq) * progress

                angle = 2 * math.pi * current_freq * i / sample_rate
                # Add amplitude envelope (fade out)
                envelope = (1 - progress) * 0.5
                sample = int(32767 * envelope * math.sin(angle))
                # Store as 16-bit
                samples.extend([sample & 0xFF, (sample >> 8) & 0xFF])

            # Create pygame sound
            sound = pygame.mixer.Sound(buffer=bytes(samples))
            return sound
        except Exception as e:
            return None

    def play_collision_sound(self):
        """Play collision sound effect"""
        try:
            if self.collision_sound and pygame.mixer.get_init():
                self.collision_sound.set_volume(0.7)
                self.collision_sound.play()
        except Exception:
            pass

    def handle_events(self):
        """Handle user input"""
        mouse_pos = pygame.mouse.get_pos()
        
        # Update button hovers
        self.play_button.update_hover(mouse_pos)
        self.credits_button.update_hover(mouse_pos)
        self.settings_button.update_hover(mouse_pos)
        self.back_button.update_hover(mouse_pos)
        self.play_again_button.update_hover(mouse_pos)
        self.exit_menu_button.update_hover(mouse_pos)
        for btn in self.input_buttons:
            btn.update_hover(mouse_pos)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if self.state in [STATE_SETTINGS, STATE_CREDITS, STATE_INPUT_SELECT]:
                        self.state = STATE_MAIN_MENU
                    elif self.state == STATE_GAME_OVER:
                        self.reset()

                # Z key to skip loading screen
                if event.key == pygame.K_z and self.state == STATE_LOADING:
                    self.state = STATE_PLAYING
                    self.loading_timer = 0
                    self.loading_progress = 0

                if self.state == STATE_INPUT_SELECT:
                    if event.key == pygame.K_1:
                        self.input_method = INPUT_CLICK
                        self.start_loading()
                    elif event.key == pygame.K_2:
                        self.input_method = INPUT_SPACE
                        self.start_loading()
                    elif event.key == pygame.K_3:
                        self.input_method = INPUT_ARROW
                        self.start_loading()
                    elif event.key == pygame.K_4:
                        self.input_method = INPUT_ALL
                        self.start_loading()
                
                elif self.state == STATE_PLAYING:
                    if self.input_method in [INPUT_SPACE, INPUT_ALL] and event.key == pygame.K_SPACE:
                        self.bird.flap()
                    elif self.input_method in [INPUT_ARROW, INPUT_ALL] and event.key in [pygame.K_UP, pygame.K_w]:
                        self.bird.flap()
                
                elif self.state == STATE_GAME_OVER:
                    if event.key == pygame.K_SPACE:
                        # SPACE = Play Again (loop with same input)
                        self.start_loading()
                
                elif self.state == STATE_SETTINGS:
                    if event.key == pygame.K_m:
                        self.music_enabled = not self.music_enabled
                        if self.music_loaded:
                            if self.music_enabled:
                                pygame.mixer.music.unpause()
                            else:
                                pygame.mixer.music.pause()
            
            if event.type == pygame.MOUSEBUTTONDOWN:
                if self.state == STATE_MAIN_MENU:
                    if self.play_button.is_clicked(mouse_pos):
                        self.state = STATE_INPUT_SELECT
                    elif self.credits_button.is_clicked(mouse_pos):
                        self.state = STATE_CREDITS
                    elif self.settings_button.is_clicked(mouse_pos):
                        self.state = STATE_SETTINGS
                
                elif self.state == STATE_INPUT_SELECT:
                    for i, btn in enumerate(self.input_buttons):
                        if btn.is_clicked(mouse_pos):
                            if i == 0:
                                self.input_method = INPUT_CLICK
                            elif i == 1:
                                self.input_method = INPUT_SPACE
                            elif i == 2:
                                self.input_method = INPUT_ARROW
                            elif i == 3:
                                self.input_method = INPUT_ALL
                            self.start_loading()
                
                elif self.state == STATE_PLAYING:
                    if self.input_method in [INPUT_CLICK, INPUT_ALL]:
                        self.bird.flap()
                
                elif self.state in [STATE_SETTINGS, STATE_CREDITS]:
                    if self.back_button.is_clicked(mouse_pos):
                        self.state = STATE_MAIN_MENU
                    elif self.state == STATE_SETTINGS:
                        # Music button
                        if hasattr(self, 'music_button_rect') and self.music_button_rect.collidepoint(mouse_pos):
                            self.music_enabled = not self.music_enabled
                            if self.music_loaded:
                                if self.music_enabled:
                                    pygame.mixer.music.unpause()
                                else:
                                    pygame.mixer.music.pause()
                        # Brightness slider
                        elif hasattr(self, 'slider_rect') and self.slider_rect.collidepoint(mouse_pos):
                            self.dragging_slider = True
                            self.update_brightness_from_mouse(mouse_pos)
                        # Weight slider
                        elif hasattr(self, 'weight_slider_rect') and self.weight_slider_rect.collidepoint(mouse_pos):
                            self.dragging_weight_slider = True
                            self.update_weight_from_mouse(mouse_pos)
                
                elif self.state == STATE_GAME_OVER:
                    if self.play_again_button.is_clicked(mouse_pos):
                        # Loop the game with same input method
                        self.start_loading()
                    elif self.exit_menu_button.is_clicked(mouse_pos):
                        # Exit to main menu
                        self.reset()
            
            if event.type == pygame.MOUSEBUTTONUP:
                self.dragging_slider = False
                self.dragging_weight_slider = False

            if event.type == pygame.MOUSEMOTION:
                if self.dragging_slider and self.state == STATE_SETTINGS:
                    self.update_brightness_from_mouse(event.pos)
                if self.dragging_weight_slider and self.state == STATE_SETTINGS:
                    self.update_weight_from_mouse(event.pos)
        
        return True
    
    def update_brightness_from_mouse(self, mouse_pos):
        """Update brightness based on mouse position"""
        if hasattr(self, 'slider_rect'):
            slider_x = self.slider_rect.x
            slider_width = self.slider_rect.width
            mouse_x = mouse_pos[0]
            self.brightness = int(100 * (mouse_x - slider_x) / slider_width)
            self.brightness = max(0, min(100, self.brightness))

    def update_weight_from_mouse(self, mouse_pos):
        """Update bird weight based on mouse position (1.0 to 3.0)"""
        if hasattr(self, 'weight_slider_rect'):
            slider_x = self.weight_slider_rect.x
            slider_width = self.weight_slider_rect.width
            mouse_x = mouse_pos[0]
            # Weight from 1.0 to 3.0
            self.bird_weight = 1.0 + (2.0 * (mouse_x - slider_x) / slider_width)
            self.bird_weight = max(1.0, min(3.0, self.bird_weight))
    
    def start_loading(self):
        """Start the loading state"""
        # Reset bird and pipes for new game
        self.bird = AnimatedBird(60, 300, weight=self.bird_weight)
        self.pipes = [Pipe(SCREEN_WIDTH)]
        self.score = 0
        self.frame_count = 0
        # Don't reset input_method - keep the same one
        self.state = STATE_LOADING
        self.loading_timer = 0
        self.loading_progress = 0
        # Randomize which tip to start with
        self.current_tip = random.randint(0, len(PHYSICS_TIPS) - 1)
    
    def update(self):
        """Update game state"""
        # Always increment frame counters
        self.menu_frame_count += 1
        
        if self.state == STATE_MAIN_MENU:
            self.frame_count = self.menu_frame_count
            self.bird.animate_idle()
        
        elif self.state == STATE_LOADING:
            self.loading_timer += 1
            # 8 seconds = 480 frames at 60 FPS
            self.loading_progress = min(100, (self.loading_timer / 480) * 100)
            if self.loading_progress >= 100:
                self.state = STATE_PLAYING
                self.loading_timer = 0
                self.loading_progress = 0
        
        elif self.state == STATE_PLAYING:
            self.frame_count += 1
            self.bird.update()

            for pipe in self.pipes:
                pipe.update()
                if not pipe.passed and pipe.x + PIPE_WIDTH < self.bird.x:
                    pipe.passed = True
                    self.score += 1

            self.pipes = [p for p in self.pipes if not p.is_offscreen()]

            if len(self.pipes) == 0 or self.pipes[-1].x < SCREEN_WIDTH - 200:
                self.pipes.append(Pipe(SCREEN_WIDTH, gap=self.get_pipe_gap()))

            if self.bird.check_collision(self.pipes):
                self.play_collision_sound()
                self.game_over_tip = random.choice(PHYSICS_TIPS)  # Random tip for game over
                self.state = STATE_GAME_OVER
    
    def get_pipe_gap(self):
        """Calculate pipe gap based on score - decreases by 20 every 3 points, minimum 120"""
        gap = PIPE_GAP - (self.score // 3) * 20
        return max(120, gap)

    def reset(self):
        """Reset game"""
        self.bird = AnimatedBird(60, 300, weight=self.bird_weight)
        self.pipes = [Pipe(SCREEN_WIDTH)]
        self.score = 0
        self.frame_count = 0
        self.state = STATE_MAIN_MENU
        self.input_method = None
    
    def draw_background(self):
        """Draw sky gradient"""
        for y in range(SCREEN_HEIGHT):
            ratio = y / SCREEN_HEIGHT
            r = int(135 + (224 - 135) * ratio)
            g = int(206 + (240 - 206) * ratio)
            b = int(235)
            pygame.draw.line(screen, (r, g, b), (0, y), (SCREEN_WIDTH, y))
    
    def draw_grass(self):
        """Draw grass at the bottom of the screen"""
        grass_height = 40
        grass_y = SCREEN_HEIGHT - grass_height
        
        # Grass green color
        grass_color = (34, 180, 34)
        pygame.draw.rect(screen, grass_color, (0, grass_y, SCREEN_WIDTH, grass_height))
        
        # Add grass texture with lines
        for x in range(0, SCREEN_WIDTH, 15):
            pygame.draw.line(screen, (20, 140, 20), (x, grass_y), (x + 10, grass_y + grass_height), 2)
    
    def draw_static_pipes(self):
        """Draw pipes on menu screen"""
        pygame.draw.rect(screen, GREEN, (SCREEN_WIDTH - 10 - PIPE_WIDTH, 280, PIPE_WIDTH, 280))
        pygame.draw.rect(screen, (26, 107, 26), (SCREEN_WIDTH - 10 - PIPE_WIDTH, 280, PIPE_WIDTH, 280), 2)
    
    def draw_main_menu(self):
        """Draw main menu"""
        self.draw_background()
        self.draw_static_pipes()
        self.draw_grass()
        
        # Calculate bob animation for text
        bob_offset = math.sin(self.frame_count * 0.05) * 15
        
        # Title - yellow and bobbing
        title = huge_title_font.render("FLAPPY BIRD", True, YELLOW)
        screen.blit(title, (SCREEN_WIDTH//2 - title.get_width()//2, 30 + bob_offset))
        
        # Subtitle - yellow and bobbing
        subtitle = font.render("Physics Project", True, YELLOW)
        screen.blit(subtitle, (SCREEN_WIDTH//2 - subtitle.get_width()//2, 105 + bob_offset))
        
        mouse_pos = pygame.mouse.get_pos()
        bird_target_y = 250

        if self.play_button.rect.collidepoint(mouse_pos):
            bird_target_y = self.play_button.rect.centery
        elif self.credits_button.rect.collidepoint(mouse_pos):
            bird_target_y = self.credits_button.rect.centery
        elif self.settings_button.rect.collidepoint(mouse_pos):
            bird_target_y = self.settings_button.rect.centery

        if self.bird.y < bird_target_y - 5:
            self.bird.y += 5
        elif self.bird.y > bird_target_y + 5:
            self.bird.y -= 5
        else:
            self.bird.y = bird_target_y

        self.bird.x = 60
        self.bird.draw(screen, animated=True)

        self.play_button.draw(screen)
        self.credits_button.draw(screen)
        self.settings_button.draw(screen)
    
    def draw_input_select(self):
        """Draw input selection screen"""
        self.draw_background()
        self.draw_grass()

        title = font.render("Choose Your Input", True, BLACK)
        screen.blit(title, (SCREEN_WIDTH//2 - title.get_width()//2, 40))

        subtitle = small_font.render("Press 1, 2, 3, or 4", True, DARK_GRAY)
        screen.blit(subtitle, (SCREEN_WIDTH//2 - subtitle.get_width()//2, 90))

        for i, btn in enumerate(self.input_buttons):
            btn.draw(screen)
            hint_text = tiny_font.render(f"Press {i+1}", True, WHITE)
            hint_rect = hint_text.get_rect(topleft=(btn.rect.x + 10, btn.rect.y + 5))
            screen.blit(hint_text, hint_rect)
    
    def draw_loading(self):
        """Draw loading screen with physics concepts"""
        self.draw_background()
        self.draw_grass()
        
        title = large_font.render("Loading...", True, BLACK)
        screen.blit(title, (SCREEN_WIDTH//2 - title.get_width()//2, 60))
        
        # Progress bar
        bar_width = 300
        bar_height = 20
        bar_x = (SCREEN_WIDTH - bar_width) // 2
        bar_y = 150
        
        pygame.draw.rect(screen, DARK_GRAY, (bar_x, bar_y, bar_width, bar_height), 2)
        pygame.draw.rect(screen, LIGHT_GREEN, (bar_x, bar_y, int(bar_width * self.loading_progress / 100), bar_height))
        
        progress_text = small_font.render(f"{int(self.loading_progress)}%", True, BLACK)
        screen.blit(progress_text, (SCREEN_WIDTH//2 - progress_text.get_width()//2, bar_y + 30))

        tip_change_interval = 90
        tip_index = (self.loading_timer // tip_change_interval) % len(PHYSICS_TIPS)
        actual_tip_index = (self.current_tip + tip_index) % len(PHYSICS_TIPS)
        physics_tip = PHYSICS_TIPS[actual_tip_index]

        tip_text = small_font.render(physics_tip, True, BLACK)
        screen.blit(tip_text, (SCREEN_WIDTH//2 - tip_text.get_width()//2, 250))

        input_text = f"Input: {self.input_method}"
        input_render = small_font.render(input_text, True, BLACK)
        screen.blit(input_render, (SCREEN_WIDTH//2 - input_render.get_width()//2, 330))

        info_text = tiny_font.render("Get ready to play!", True, DARK_GRAY)
        screen.blit(info_text, (SCREEN_WIDTH//2 - info_text.get_width()//2, 390))
    
    def draw_playing(self):
        """Draw game playing screen"""
        self.draw_background()

        for pipe in self.pipes:
            pipe.draw(screen)

        self.draw_grass()
        self.bird.draw(screen)

        score_text = font.render(f"Score: {self.score}", True, BLACK)
        score_bg = pygame.Surface((150, 50))
        score_bg.set_alpha(180)
        score_bg.fill(WHITE)
        screen.blit(score_bg, (10, 10))
        screen.blit(score_text, (20, 20))

        input_text = ""
        if self.input_method == INPUT_CLICK:
            input_text = "Click to flap"
        elif self.input_method == INPUT_SPACE:
            input_text = "SPACE to flap"
        elif self.input_method == INPUT_ARROW:
            input_text = "Arrow UP to flap"
        elif self.input_method == INPUT_ALL:
            input_text = "Click/SPACE/Arrow to flap"

        hint = small_font.render(input_text, True, BLACK)
        hint_bg = pygame.Surface((hint.get_width() + 10, 30))
        hint_bg.set_alpha(180)
        hint_bg.fill(WHITE)
        screen.blit(hint_bg, (10, SCREEN_HEIGHT - 40))
        screen.blit(hint, (15, SCREEN_HEIGHT - 35))
    
    def draw_game_over(self):
        """Draw game over screen"""
        self.draw_background()
        self.draw_grass()

        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(200)
        overlay.fill(BLACK)
        screen.blit(overlay, (0, 0))

        game_over_text = large_font.render("Game Over!", True, WHITE)
        final_score_text = font.render(f"Final Score: {self.score}", True, WHITE)
        weight_text = small_font.render(f"Bird Weight: {self.bird_weight:.1f}x", True, (200, 255, 200))

        screen.blit(game_over_text, (SCREEN_WIDTH//2 - game_over_text.get_width()//2, 80))
        screen.blit(final_score_text, (SCREEN_WIDTH//2 - final_score_text.get_width()//2, 160))
        screen.blit(weight_text, (SCREEN_WIDTH//2 - weight_text.get_width()//2, 210))

        if self.game_over_tip:
            tip_text = small_font.render(self.game_over_tip, True, (200, 255, 200))
            screen.blit(tip_text, (SCREEN_WIDTH//2 - tip_text.get_width()//2, 270))

        self.play_again_button.draw(screen)

        exit_color = tuple(min(c + 30, 255) for c in self.exit_menu_button.color) if self.exit_menu_button.hover else self.exit_menu_button.color
        pygame.draw.rect(screen, exit_color, self.exit_menu_button.rect, border_radius=8)
        pygame.draw.rect(screen, WHITE, self.exit_menu_button.rect, 2, border_radius=8)

        exit_text_render = small_font.render("EXIT TO MENU", True, WHITE)
        exit_text_rect = exit_text_render.get_rect(center=self.exit_menu_button.rect.center)
        screen.blit(exit_text_render, exit_text_rect)
    
    def draw_settings(self):
        """Draw settings menu"""
        self.draw_background()
        self.draw_grass()

        self.back_button.draw(screen)

        title = font.render("Settings", True, BLACK)
        screen.blit(title, (SCREEN_WIDTH//2 - title.get_width()//2, 50))

        music_status = "ON" if self.music_enabled else "OFF"
        music_text = small_font.render(f"Music: {music_status}", True, BLACK)
        screen.blit(music_text, (SCREEN_WIDTH//2 - music_text.get_width()//2, 110))
        music_hint = tiny_font.render("(Click or press M)", True, DARK_GRAY)
        screen.blit(music_hint, (SCREEN_WIDTH//2 - music_hint.get_width()//2, 135))

        music_button_color = (0, 150, 0) if self.music_enabled else (150, 0, 0)
        pygame.draw.rect(screen, music_button_color, (120, 165, 160, 40), border_radius=8)
        pygame.draw.rect(screen, WHITE, (120, 165, 160, 40), 2, border_radius=8)
        music_button_text = small_font.render("Toggle", True, WHITE)
        music_button_text_rect = music_button_text.get_rect(center=(200, 185))
        screen.blit(music_button_text, music_button_text_rect)

        brightness_text = small_font.render(f"Brightness: {self.brightness}%", True, BLACK)
        screen.blit(brightness_text, (SCREEN_WIDTH//2 - brightness_text.get_width()//2, 230))

        slider_x = 50
        slider_y = 270
        slider_width = 300
        slider_height = 20

        pygame.draw.rect(screen, DARK_GRAY, (slider_x, slider_y, slider_width, slider_height), 2)
        pygame.draw.rect(screen, LIGHT_GREEN, (slider_x, slider_y, int(slider_width * self.brightness / 100), slider_height))

        knob_x = slider_x + int(slider_width * self.brightness / 100)
        pygame.draw.circle(screen, WHITE, (knob_x, slider_y + slider_height // 2), 12)
        pygame.draw.circle(screen, BLACK, (knob_x, slider_y + slider_height // 2), 12, 2)

        weight_text = small_font.render(f"Bird Weight: {self.bird_weight:.1f}x", True, BLACK)
        screen.blit(weight_text, (SCREEN_WIDTH//2 - weight_text.get_width()//2, 320))
        weight_hint = tiny_font.render("(Higher = More clicks needed)", True, DARK_GRAY)
        screen.blit(weight_hint, (SCREEN_WIDTH//2 - weight_hint.get_width()//2, 345))

        weight_slider_x = 50
        weight_slider_y = 375
        weight_slider_width = 300
        weight_slider_height = 20

        pygame.draw.rect(screen, DARK_GRAY, (weight_slider_x, weight_slider_y, weight_slider_width, weight_slider_height), 2)
        weight_progress = (self.bird_weight - 1.0) / 2.0
        pygame.draw.rect(screen, (200, 100, 255), (weight_slider_x, weight_slider_y, int(weight_slider_width * weight_progress), weight_slider_height))

        weight_knob_x = weight_slider_x + int(weight_slider_width * weight_progress)
        pygame.draw.circle(screen, WHITE, (weight_knob_x, weight_slider_y + weight_slider_height // 2), 12)
        pygame.draw.circle(screen, BLACK, (weight_knob_x, weight_slider_y + weight_slider_height // 2), 12, 2)

        # Instructions
        instructions = [
            "Drag sliders to adjust settings",
            "M - Toggle Music | ESC - Go Back"
        ]

        y_offset = 440
        for instruction in instructions:
            text = tiny_font.render(instruction, True, DARK_GRAY)
            screen.blit(text, (SCREEN_WIDTH//2 - text.get_width()//2, y_offset))
            y_offset += 25

        # Store slider bounds for click detection
        self.slider_rect = pygame.Rect(slider_x - 15, slider_y - 15, slider_width + 30, slider_height + 30)
        self.weight_slider_rect = pygame.Rect(weight_slider_x - 15, weight_slider_y - 15, weight_slider_width + 30, weight_slider_height + 30)
        self.music_button_rect = pygame.Rect(120, 165, 160, 40)
    
    def draw_credits(self):
        """Draw credits"""
        self.draw_background()
        self.draw_grass()

        self.back_button.draw(screen)

        title = font.render("Credits", True, BLACK)
        screen.blit(title, (SCREEN_WIDTH//2 - title.get_width()//2, 80))

        credits = [
            "Flappy Bird Physics Project",
            "",
            "Created by Srikar Muthyala",
            "",
            "Physics Concepts:",
            "• Constant Acceleration (Gravity)",
            "• Kinematic Equations of Motion",
            "• Energy Conservation (Kinetic + Potential)",
            "• Impulse and Momentum",
            "",
            "AP Physics C Final Project"
        ]

        y_offset = 160
        for line in credits:
            if line.startswith("•"):
                text = small_font.render(line, True, DARK_GRAY)
            elif line == "":
                y_offset += 10
                continue
            else:
                text = small_font.render(line, True, BLACK)

            screen.blit(text, (SCREEN_WIDTH//2 - text.get_width()//2, y_offset))
            y_offset += 28
    
    def apply_brightness_overlay(self):
        """Apply brightness overlay to adjust screen brightness"""
        if self.brightness < 100:
            # Darken the screen
            darken_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            darken_surface.set_alpha(int(255 * (1 - self.brightness / 100)))
            darken_surface.fill(BLACK)
            screen.blit(darken_surface, (0, 0))
        elif self.brightness > 100:
            # Brighten the screen
            brighten_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            brighten_surface.set_alpha(int(255 * ((self.brightness - 100) / 100)))
            brighten_surface.fill(WHITE)
            screen.blit(brighten_surface, (0, 0))

    def draw(self):
        """Draw based on current game state"""
        if self.state == STATE_MAIN_MENU:
            self.draw_main_menu()
        elif self.state == STATE_INPUT_SELECT:
            self.draw_input_select()
        elif self.state == STATE_LOADING:
            self.draw_loading()
        elif self.state == STATE_PLAYING:
            self.draw_playing()
        elif self.state == STATE_GAME_OVER:
            self.draw_game_over()
        elif self.state == STATE_SETTINGS:
            self.draw_settings()
        elif self.state == STATE_CREDITS:
            self.draw_credits()

        # Apply brightness overlay last
        self.apply_brightness_overlay()

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
    main()
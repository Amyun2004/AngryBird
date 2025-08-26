"""
ui.py - User interface, HUD, and visual effects
"""

import pygame
import random
from constants import *


class UI:
    """Handles all UI elements and display"""
    
    def __init__(self, screen):
        self.screen = screen
        self.font_small = pygame.font.Font(None, 24)
        self.font_medium = pygame.font.Font(None, 36)
        self.font_large = pygame.font.Font(None, 72)
        self.font_xlarge = pygame.font.Font(None, 96)
        
    def draw_background(self):
        """Draw the game background with gradient sky"""
        # Sky gradient
        for i in range(WIN_HEIGHT - GROUND_HEIGHT):
            ratio = i / (WIN_HEIGHT - GROUND_HEIGHT)
            r = int(135 + ratio * 50)
            g = int(206 + ratio * 30)
            b = int(235 - ratio * 50)
            pygame.draw.line(self.screen, (r, g, b), (0, i), (WIN_WIDTH, i))
        
        # Add some clouds
        self._draw_clouds()
        
        # Ground
        pygame.draw.rect(self.screen, GROUND_COLOR, 
                        (0, WIN_HEIGHT - GROUND_HEIGHT, WIN_WIDTH, GROUND_HEIGHT))
        
        # Grass with variation
        self._draw_grass()
        
    def _draw_clouds(self):
        """Draw decorative clouds"""
        cloud_positions = [(200, 100), (500, 80), (800, 120), (1000, 90)]
        for x, y in cloud_positions:
            # Simple cloud made of circles
            pygame.draw.circle(self.screen, (255, 255, 255, 200), (x, y), 25)
            pygame.draw.circle(self.screen, (255, 255, 255, 200), (x + 20, y), 30)
            pygame.draw.circle(self.screen, (255, 255, 255, 200), (x + 40, y), 25)
            pygame.draw.circle(self.screen, (255, 255, 255, 200), (x + 15, y - 15), 20)
            pygame.draw.circle(self.screen, (255, 255, 255, 200), (x + 25, y - 10), 22)
    
    def _draw_grass(self):
        """Draw animated grass"""
        grass_height = 10
        for i in range(0, WIN_WIDTH, 3):
            height_variation = random.randint(-3, 3)
            # Darker grass in back
            pygame.draw.line(self.screen, (24, 100, 24), 
                           (i, WIN_HEIGHT - GROUND_HEIGHT),
                           (i + random.randint(-2, 2), 
                            WIN_HEIGHT - GROUND_HEIGHT - grass_height - height_variation - 2), 2)
            # Lighter grass in front
            pygame.draw.line(self.screen, GRASS_COLOR, 
                           (i, WIN_HEIGHT - GROUND_HEIGHT),
                           (i + random.randint(-1, 1), 
                            WIN_HEIGHT - GROUND_HEIGHT - grass_height - height_variation), 2)
    
    def draw_hud(self, score, birds_left, pigs_left, level_num=1):
        """Draw the heads-up display"""
        # Semi-transparent background for HUD
        hud_surface = pygame.Surface((250, 150))
        hud_surface.set_alpha(200)
        hud_surface.fill((50, 50, 50))
        self.screen.blit(hud_surface, (20, 20))
        
        # Level
        level_text = self.font_medium.render(f"Level {level_num}", True, WHITE)
        self.screen.blit(level_text, (30, 30))
        
        # Score with icon
        score_text = self.font_small.render(f"Score: {score:,}", True, YELLOW)
        self.screen.blit(score_text, (30, 70))
        
        # Birds remaining with bird icon
        bird_icon_pos = (30, 100)
        pygame.draw.circle(self.screen, RED, bird_icon_pos, 8)
        pygame.draw.circle(self.screen, BLACK, bird_icon_pos, 8, 2)
        birds_text = self.font_small.render(f" x {birds_left}", True, WHITE)
        self.screen.blit(birds_text, (45, 93))
        
        # Pigs remaining with pig icon
        pig_icon_pos = (130, 100)
        pygame.draw.circle(self.screen, PIG_COLOR, pig_icon_pos, 8)
        pygame.draw.circle(self.screen, BLACK, pig_icon_pos, 8, 2)
        pigs_text = self.font_small.render(f" x {pigs_left}", True, WHITE)
        self.screen.blit(pigs_text, (145, 93))
        
    def draw_game_over(self, victory, score, level_num):
        """Draw game over screen"""
        # Dark overlay
        overlay = pygame.Surface((WIN_WIDTH, WIN_HEIGHT))
        overlay.set_alpha(180)
        overlay.fill(BLACK)
        self.screen.blit(overlay, (0, 0))
        
        if victory:
            # Victory message
            title = self.font_xlarge.render("VICTORY!", True, GOLD)
            title_rect = title.get_rect(center=(WIN_WIDTH // 2, WIN_HEIGHT // 2 - 100))
            self.screen.blit(title, title_rect)
            
            # Stars based on score
            stars = 3 if score > 3000 else 2 if score > 1500 else 1
            star_y = WIN_HEIGHT // 2 - 20
            for i in range(stars):
                self._draw_star(WIN_WIDTH // 2 - 60 + i * 60, star_y, 25, GOLD)
            
        else:
            # Defeat message
            title = self.font_xlarge.render("GAME OVER", True, RED)
            title_rect = title.get_rect(center=(WIN_WIDTH // 2, WIN_HEIGHT // 2 - 100))
            self.screen.blit(title, title_rect)
            
            message = self.font_medium.render("Try Again!", True, WHITE)
            msg_rect = message.get_rect(center=(WIN_WIDTH // 2, WIN_HEIGHT // 2 - 40))
            self.screen.blit(message, msg_rect)
        
        # Score display
        score_text = self.font_large.render(f"Score: {score:,}", True, WHITE)
        score_rect = score_text.get_rect(center=(WIN_WIDTH // 2, WIN_HEIGHT // 2 + 40))
        self.screen.blit(score_text, score_rect)
        
        # Instructions
        inst_text = self.font_medium.render("Press SPACE to continue or ESC to exit", True, YELLOW)
        inst_rect = inst_text.get_rect(center=(WIN_WIDTH // 2, WIN_HEIGHT // 2 + 120))
        self.screen.blit(inst_text, inst_rect)
    
    def draw_level_intro(self, level_num, level_name):
        """Draw level introduction screen"""
        # Background
        self.draw_background()
        
        # Dark overlay
        overlay = pygame.Surface((WIN_WIDTH, WIN_HEIGHT))
        overlay.set_alpha(100)
        overlay.fill(BLACK)
        self.screen.blit(overlay, (0, 0))
        
        # Level number
        level_text = self.font_xlarge.render(f"LEVEL {level_num}", True, WHITE)
        level_rect = level_text.get_rect(center=(WIN_WIDTH // 2, WIN_HEIGHT // 2 - 50))
        self.screen.blit(level_text, level_rect)
        
        # Level name
        name_text = self.font_large.render(level_name, True, YELLOW)
        name_rect = name_text.get_rect(center=(WIN_WIDTH // 2, WIN_HEIGHT // 2 + 20))
        self.screen.blit(name_text, name_rect)
        
        # Instructions
        inst_text = self.font_medium.render("Click to Start", True, WHITE)
        inst_rect = inst_text.get_rect(center=(WIN_WIDTH // 2, WIN_HEIGHT // 2 + 80))
        self.screen.blit(inst_text, inst_rect)
    
    def _draw_star(self, x, y, size, color):
        """Draw a star shape"""
        import math
        points = []
        for i in range(10):
            angle = math.pi * i / 5
            if i % 2 == 0:
                radius = size
            else:
                radius = size * 0.5
            px = x + radius * math.cos(angle - math.pi / 2)
            py = y + radius * math.sin(angle - math.pi / 2)
            points.append((px, py))
        pygame.draw.polygon(self.screen, color, points)
        pygame.draw.polygon(self.screen, BLACK, points, 2)
    
    def draw_menu(self):
        """Draw main menu"""
        # Background
        self.draw_background()
        
        # Title
        title = self.font_xlarge.render("ANGRY BIRDS", True, RED)
        title_rect = title.get_rect(center=(WIN_WIDTH // 2, 150))
        self.screen.blit(title, title_rect)
        
        subtitle = self.font_medium.render("Pymunk Physics Edition", True, WHITE)
        sub_rect = subtitle.get_rect(center=(WIN_WIDTH // 2, 200))
        self.screen.blit(subtitle, sub_rect)
        
        # Menu options
        options = [
            "1. Start Game",
            "2. Select Level",
            "3. Instructions",
            "ESC. Exit"
        ]
        
        y_start = 300
        for i, option in enumerate(options):
            color = YELLOW if i == 0 else WHITE
            text = self.font_large.render(option, True, color)
            text_rect = text.get_rect(center=(WIN_WIDTH // 2, y_start + i * 60))
            self.screen.blit(text, text_rect)
    
    def draw_instructions(self):
        """Draw instructions screen"""
        # Background
        self.draw_background()
        
        # Dark overlay
        overlay = pygame.Surface((WIN_WIDTH, WIN_HEIGHT))
        overlay.set_alpha(150)
        overlay.fill(BLACK)
        self.screen.blit(overlay, (0, 0))
        
        # Title
        title = self.font_large.render("HOW TO PLAY", True, YELLOW)
        title_rect = title.get_rect(center=(WIN_WIDTH // 2, 100))
        self.screen.blit(title, title_rect)
        
        # Instructions
        instructions = [
            "1. Click and drag the bird in the slingshot to aim",
            "2. Release to launch the bird",
            "3. Destroy all pigs to win the level",
            "4. Use different materials' weaknesses:",
            "   - Ice: Very fragile, easy to break",
            "   - Wood: Medium strength",
            "   - Stone: Strong but heavy",
            "   - Metal: Very strong and heavy",
            "",
            "Tips:",
            "- Aim for structural weak points",
            "- Use falling blocks to crush pigs",
            "- Different birds have different abilities",
            "",
            "Press SPACE to return to menu"
        ]
        
        y_start = 180
        for i, line in enumerate(instructions):
            if line.startswith("   "):
                color = LIGHTBLUE
                size = self.font_small
            elif line.startswith("Tips:"):
                color = GREEN
                size = self.font_medium
            elif line == "":
                continue
            else:
                color = WHITE
                size = self.font_small
                
            text = size.render(line, True, color)
            text_rect = text.get_rect(center=(WIN_WIDTH // 2, y_start + i * 25))
            self.screen.blit(text, text_rect)
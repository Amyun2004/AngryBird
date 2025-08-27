"""
ui.py - User interface, HUD, and visual effects
Enhanced with combo display and better visual feedback
"""

import pygame
import random
import math
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
    
    def draw_background_to_surface(self, surface):
        """Draw the game background to a specific surface for camera/shake effects"""
        # Sky gradient
        for i in range(WIN_HEIGHT - GROUND_HEIGHT):
            ratio = i / (WIN_HEIGHT - GROUND_HEIGHT)
            r = int(135 + ratio * 50)
            g = int(206 + ratio * 30)
            b = int(235 - ratio * 50)
            pygame.draw.line(surface, (r, g, b), (0, i), (surface.get_width(), i))
        
        # Ground
        pygame.draw.rect(surface, GROUND_COLOR, 
                        (0, WIN_HEIGHT - GROUND_HEIGHT, surface.get_width(), GROUND_HEIGHT))
        
        # Grass
        grass_height = 10
        for i in range(0, surface.get_width(), 3):
            height_variation = random.randint(-3, 3)
            pygame.draw.line(surface, GRASS_COLOR, 
                           (i, WIN_HEIGHT - GROUND_HEIGHT),
                           (i + random.randint(-1, 1), 
                            WIN_HEIGHT - GROUND_HEIGHT - grass_height - height_variation), 2)
        
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
    
    def draw_hud(self, score, birds_left, pigs_left, level_num=1, combo_text=""):
        """Draw the heads-up display with combo indicator"""
        # Semi-transparent background for HUD
        hud_surface = pygame.Surface((250, 150))
        hud_surface.set_alpha(200)
        hud_surface.fill((50, 50, 50))
        self.screen.blit(hud_surface, (20, 20))
        
        # Level
        level_text = self.font_medium.render(f"Level {level_num}", True, WHITE)
        self.screen.blit(level_text, (30, 30))
        
        # Score with combo multiplier
        if combo_text:
            # Score in yellow
            score_text = self.font_small.render(f"Score: {score:,}", True, YELLOW)
            self.screen.blit(score_text, (30, 70))
            
            # Combo in orange/red for emphasis
            combo_render = self.font_small.render(combo_text, True, ORANGE)
            combo_x = 30 + score_text.get_width() + 5
            self.screen.blit(combo_render, (combo_x, 70))
            
            # Add a pulsing effect indicator
            if float(combo_text.replace(' x', '')) >= 2.0:
                pygame.draw.circle(self.screen, ORANGE, (240, 80), 5)
                pygame.draw.circle(self.screen, YELLOW, (240, 80), 3)
        else:
            # Normal score display
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
        
        # Draw controls hint
        hint_text = self.font_small.render("P: Pause | ESC: Menu", True, (200, 200, 200))
        self.screen.blit(hint_text, (30, 130))
    
    def draw_game_over(self, victory, score, level_num):
        """Draw game over screen with star rating"""
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
            
            # Star rating based on score - Logic Point 8
            stars = self._calculate_stars(score, level_num)
            star_y = WIN_HEIGHT // 2 - 20
            for i in range(3):
                if i < stars:
                    self._draw_star(WIN_WIDTH // 2 - 60 + i * 60, star_y, 25, GOLD)
                else:
                    self._draw_star(WIN_WIDTH // 2 - 60 + i * 60, star_y, 25, GRAY)
            
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
    
    def _calculate_stars(self, score, level_num):
        """Calculate star rating based on score and level"""
        # Different thresholds per level
        thresholds = {
            1: (1000, 2000, 3000),
            2: (2000, 3500, 5000),
            3: (2500, 4000, 6000),
            4: (3000, 5000, 7000)
        }
        
        level_thresholds = thresholds.get(level_num, (2000, 4000, 6000))
        
        if score >= level_thresholds[2]:
            return 3
        elif score >= level_thresholds[1]:
            return 2
        elif score >= level_thresholds[0]:
            return 1
        else:
            return 0
    
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
        
        # Tips based on level
        tips = {
            1: "Tip: Aim for the base of structures!",
            2: "Tip: Ice breaks easily - use it to your advantage!",
            3: "Tip: Stone is tough - aim for weak points!",
            4: "Tip: Chain reactions score big points!"
        }
        
        tip_text = self.font_small.render(tips.get(level_num, "Good luck!"), True, (200, 255, 200))
        tip_rect = tip_text.get_rect(center=(WIN_WIDTH // 2, WIN_HEIGHT // 2 + 120))
        self.screen.blit(tip_text, tip_rect)
    
    def _draw_star(self, x, y, size, color):
        """Draw a star shape"""
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
        
        # Title with shadow effect
        shadow = self.font_xlarge.render("ANGRY BIRDS", True, (50, 0, 0))
        shadow_rect = shadow.get_rect(center=(WIN_WIDTH // 2 + 3, 153))
        self.screen.blit(shadow, shadow_rect)
        
        title = self.font_xlarge.render("ANGRY BIRDS", True, RED)
        title_rect = title.get_rect(center=(WIN_WIDTH // 2, 150))
        self.screen.blit(title, title_rect)
        
        subtitle = self.font_medium.render("Pymunk Physics Edition", True, WHITE)
        sub_rect = subtitle.get_rect(center=(WIN_WIDTH // 2, 200))
        self.screen.blit(subtitle, sub_rect)
        
        # Menu options with hover effect simulation
        options = [
            ("1. Start Game", YELLOW),
            ("2. Select Level", WHITE),
            ("3. Instructions", WHITE),
            ("ESC. Exit", WHITE)
        ]
        
        y_start = 300
        for i, (option, color) in enumerate(options):
            # Draw option with background
            text = self.font_large.render(option, True, color)
            text_rect = text.get_rect(center=(WIN_WIDTH // 2, y_start + i * 60))
            
            # Subtle background for options
            if i == 0:  # Highlight first option
                bg_rect = pygame.Rect(text_rect.x - 10, text_rect.y - 5, 
                                     text_rect.width + 20, text_rect.height + 10)
                pygame.draw.rect(self.screen, (50, 50, 50), bg_rect, border_radius=5)
                pygame.draw.rect(self.screen, color, bg_rect, 2, border_radius=5)
            
            self.screen.blit(text, text_rect)
    
    def draw_instructions(self):
        """Draw instructions screen with enhanced tips"""
        # Background
        self.draw_background()
        
        # Dark overlay
        overlay = pygame.Surface((WIN_WIDTH, WIN_HEIGHT))
        overlay.set_alpha(150)
        overlay.fill(BLACK)
        self.screen.blit(overlay, (0, 0))
        
        # Title
        title = self.font_large.render("HOW TO PLAY", True, YELLOW)
        title_rect = title.get_rect(center=(WIN_WIDTH // 2, 80))
        self.screen.blit(title, title_rect)
        
        # Instructions grouped by category
        instructions = [
            ("CONTROLS:", YELLOW, self.font_medium),
            ("• Click and drag bird to aim", WHITE, self.font_small),
            ("• Release to launch", WHITE, self.font_small),
            ("• Press P to pause", WHITE, self.font_small),
            ("", WHITE, self.font_small),
            ("OBJECTIVES:", GREEN, self.font_medium),
            ("• Destroy all pigs to win", WHITE, self.font_small),
            ("• Score points by breaking blocks", WHITE, self.font_small),
            ("• Chain reactions give combo bonuses!", ORANGE, self.font_small),
            ("", WHITE, self.font_small),
            ("MATERIALS:", LIGHTBLUE, self.font_medium),
            ("• Ice: Very fragile (3x damage)", (150, 220, 230), self.font_small),
            ("• Wood: Medium strength", (139, 90, 43), self.font_small),
            ("• Stone: Strong (half damage)", (105, 105, 105), self.font_small),
            ("• Metal: Very strong (1/3 damage)", (70, 70, 70), self.font_small),
            ("", WHITE, self.font_small),
            ("BIRD TYPES:", RED, self.font_medium),
            ("• Red: Balanced all-rounder", RED, self.font_small),
            ("• Yellow: Extra damage (especially vs wood)", YELLOW, self.font_small),
            ("• Blue: Small but fast", BLUE, self.font_small),
            ("", WHITE, self.font_small),
            ("Press SPACE or ESC to return", WHITE, self.font_medium)
        ]
        
        y_start = 140
        line_spacing = 22
        
        for line, color, font in instructions:
            if line == "":
                y_start += line_spacing // 2
                continue
                
            text = font.render(line, True, color)
            
            # Left align for bullet points, center for headers
            if line.startswith("•"):
                text_rect = text.get_rect(left=350, centery=y_start)
            else:
                text_rect = text.get_rect(center=(WIN_WIDTH // 2, y_start))
                
            self.screen.blit(text, text_rect)
            
            # Adjust spacing based on font size
            if font == self.font_medium:
                y_start += line_spacing + 8
            else:
                y_start += line_spacing
    
    def draw_pause_screen(self):
        """Draw pause screen with options"""
        # Semi-transparent overlay
        overlay = pygame.Surface((WIN_WIDTH, WIN_HEIGHT))
        overlay.set_alpha(180)
        overlay.fill(BLACK)
        self.screen.blit(overlay, (0, 0))
        
        # Pause text
        pause_text = self.font_xlarge.render("PAUSED", True, WHITE)
        pause_rect = pause_text.get_rect(center=(WIN_WIDTH // 2, WIN_HEIGHT // 2 - 50))
        self.screen.blit(pause_text, pause_rect)
        
        # Options
        options = [
            "P - Resume Game",
            "R - Restart Level",
            "ESC - Main Menu"
        ]
        
        y_start = WIN_HEIGHT // 2 + 20
        for option in options:
            text = self.font_medium.render(option, True, YELLOW)
            text_rect = text.get_rect(center=(WIN_WIDTH // 2, y_start))
            self.screen.blit(text, text_rect)
            y_start += 40
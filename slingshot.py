"""
slingshot.py - Slingshot class for launching birds
"""

import pygame
import math
from constants import *


class Slingshot:
    """Slingshot for launching birds"""
    
    def __init__(self):
        # Position the anchors at the fork tips (where the Y arms are)
        self.fork_y = WIN_HEIGHT - 150  # Y position of the fork tips
        self.anchor_left = (SLINGSHOT_X - 25, self.fork_y)
        self.anchor_right = (SLINGSHOT_X + 25, self.fork_y)
        self.loaded_bird = None
        self.pull_pos = None
        self.trajectory_points = []
        
    def load_bird(self, bird):
        """Load a bird into the slingshot"""
        if bird is None:
            return
            
        self.loaded_bird = bird
        # Position bird at the center of the fork (between the Y arms)
        if hasattr(bird, 'body'):
            bird.body.position = SLINGSHOT_X, (self.fork_y)
        self.pull_pos = None
        self.trajectory_points = []
        
    def pull(self, mouse_pos):
        """Pull the slingshot with mouse"""
        if self.loaded_bird and not self.loaded_bird.launched:
            # Calculate distance from slingshot center
            dx = SLINGSHOT_X - mouse_pos[0]
            dy = self.fork_y - mouse_pos[1]
            distance = math.hypot(dx, dy)
            
            # Limit stretch distance
            if distance > MAX_STRETCH:
                scale = MAX_STRETCH / distance
                self.pull_pos = (
                    SLINGSHOT_X - dx * scale, 
                    self.fork_y - dy * scale
                )
            else:
                self.pull_pos = mouse_pos
                
            # Update bird position
            self.loaded_bird.body.position = self.pull_pos
            
            # Update trajectory preview
            self._calculate_trajectory()
            
    def release(self):
        """Release the bird"""
        if self.loaded_bird and self.pull_pos and not self.loaded_bird.launched:
            # Calculate launch velocity based on pull from fork position
            dx = SLINGSHOT_X - self.pull_pos[0]
            dy = self.fork_y - self.pull_pos[1]
            
            # Validate values
            if not (math.isfinite(dx) and math.isfinite(dy)):
                dx, dy = 10, -10  # Default safe values
            
            # Prevent zero velocity
            if abs(dx) < 1 and abs(dy) < 1:
                dx, dy = 10, -10
            
            velocity = (dx * LAUNCH_POWER, dy * LAUNCH_POWER)
            self.loaded_bird.launch(velocity)
            
            # Clear the loaded bird reference
            self.loaded_bird = None
            self.pull_pos = None
            self.trajectory_points = []
            
    def _calculate_trajectory(self):
        """Calculate trajectory preview points"""
        self.trajectory_points = []
        if not self.pull_pos or not self.loaded_bird:
            return
            
        # Calculate initial velocity based on pull from fork position
        dx = SLINGSHOT_X - self.pull_pos[0]
        dy = self.fork_y - self.pull_pos[1]
        vx = dx * LAUNCH_POWER
        vy = dy * LAUNCH_POWER
        
        # Simulate trajectory
        x, y = self.pull_pos
        dt = 0.02
        gravity = 981  # Match physics engine gravity
        
        for _ in range(50):
            x += vx * dt
            y += vy * dt
            vy += gravity * dt
            
            if y > WIN_HEIGHT - GROUND_HEIGHT or x < 0 or x > WIN_WIDTH:
                break
                
            self.trajectory_points.append((int(x), int(y)))
            
    def get_pull_strength(self):
        """Get current pull strength as percentage"""
        if not self.pull_pos:
            return 0
            
        dx = SLINGSHOT_X - self.pull_pos[0]
        dy = self.fork_y - self.pull_pos[1]
        distance = math.hypot(dx, dy)
        return min(distance / MAX_STRETCH, 1.0)
        
    def draw(self, screen):
        """Draw the slingshot"""
        # Draw slingshot structure
        # Base
        base_rect = pygame.Rect(SLINGSHOT_X - 5, WIN_HEIGHT - 100, 10, 60)
        pygame.draw.rect(screen, BROWN, base_rect)
        pygame.draw.rect(screen, BLACK, base_rect, 2)
        
        # Arms
        pygame.draw.line(screen, BROWN, 
                        (SLINGSHOT_X, WIN_HEIGHT - 100), 
                        (SLINGSHOT_X - 25, WIN_HEIGHT - 150), 5)
        pygame.draw.line(screen, BROWN, 
                        (SLINGSHOT_X, WIN_HEIGHT - 100), 
                        (SLINGSHOT_X + 25, WIN_HEIGHT - 150), 5)
        
        # Draw fork tips
        pygame.draw.circle(screen, BROWN, 
                          (SLINGSHOT_X - 25, WIN_HEIGHT - 150), 4)
        pygame.draw.circle(screen, BROWN, 
                          (SLINGSHOT_X + 25, WIN_HEIGHT - 150), 4)
        
        # Draw trajectory preview
        for i, point in enumerate(self.trajectory_points):
            if i % 3 == 0:  # Dotted line effect
                # Fade out dots over distance
                alpha = 255 - (i * 5)
                if alpha > 0:
                    pygame.draw.circle(screen, WHITE, point, 2)
        
        # Draw elastic bands if loaded
        if self.pull_pos and self.loaded_bird and not self.loaded_bird.launched:
            # Back band (behind bird)
            pygame.draw.line(screen, (50, 30, 10), 
                           self.anchor_left, self.anchor_right, 3)
            
            # Front bands (to bird)
            pygame.draw.line(screen, BLACK, self.anchor_left, self.pull_pos, 3)
            pygame.draw.line(screen, BLACK, self.anchor_right, self.pull_pos, 3)
            
            # Draw power indicator
            strength = self.get_pull_strength()
            if strength > 0:
                # Power bar position
                bar_x = SLINGSHOT_X - 40
                bar_y = WIN_HEIGHT - 200
                bar_width = 10
                bar_height = 50
                
                # Background
                pygame.draw.rect(screen, (50, 50, 50), 
                               (bar_x, bar_y, bar_width, bar_height))
                
                # Power level (color changes with strength)
                if strength < 0.5:
                    color = GREEN
                elif strength < 0.8:
                    color = YELLOW
                else:
                    color = RED
                    
                fill_height = int(bar_height * strength)
                pygame.draw.rect(screen, color,
                               (bar_x, bar_y + bar_height - fill_height, 
                                bar_width, fill_height))
                
                # Border
                pygame.draw.rect(screen, BLACK,
                               (bar_x, bar_y, bar_width, bar_height), 2)
"""
slingshot.py - Real slingshot mechanics
Pull back to shoot forward, just like a real slingshot
"""

import pygame
import math
from constants import *


class Slingshot:
    """Realistic slingshot for launching birds"""
    
    def __init__(self):
        # Slingshot position
        self.x = SLINGSHOT_X
        self.y = WIN_HEIGHT - 125  # Higher up for better angle
        
        # Fork positions (where the rubber bands attach)
        self.left_fork = (self.x - 20, self.y - 25)
        self.right_fork = (self.x + 20, self.y - 25)
        
        # Rest position (where bird sits initially)
        self.rest_x = self.x
        self.rest_y = self.y
        
        # Current state
        self.loaded_bird = None
        self.is_pulling = False
        self.pull_x = self.rest_x
        self.pull_y = self.rest_y
        
        # Trajectory preview
        self.trajectory_points = []
        
        # Constraints
        self.max_stretch = MAX_STRETCH
        
    def load_bird(self, bird):
        """Load a bird into the slingshot"""
        if bird is None:
            return
            
        self.loaded_bird = bird
        # Position bird at rest position
        if hasattr(bird, 'body'):
            bird.body.position = self.rest_x, self.rest_y
        
        self.is_pulling = False
        self.pull_x = self.rest_x
        self.pull_y = self.rest_y
        self.trajectory_points = []
        
    def pull(self, mouse_pos):
        """Pull the slingshot - like pulling a real slingshot back"""
        if not self.loaded_bird or self.loaded_bird.launched:
            return
            
        mouse_x, mouse_y = mouse_pos
        
        # Calculate pull vector from rest position
        dx = mouse_x - self.rest_x
        dy = mouse_y - self.rest_y
        
        # Limit pull to behind slingshot (can't pull forward)
        # For a real slingshot, you pull BACK (left) and DOWN
        if dx > 0:  # Don't allow pulling to the right of rest position
            dx = 0
            
        # Calculate distance
        distance = math.hypot(dx, dy)
        
        # Limit maximum stretch
        if distance > self.max_stretch:
            scale = self.max_stretch / distance
            dx *= scale
            dy *= scale
            distance = self.max_stretch
        
        # Update pull position
        self.pull_x = self.rest_x + dx
        self.pull_y = self.rest_y + dy
        self.is_pulling = True
        
        # Move bird to pull position
        if hasattr(self.loaded_bird, 'body'):
            self.loaded_bird.body.position = self.pull_x, self.pull_y
        
        # Calculate trajectory
        self._calculate_trajectory()
        
    def release(self):
        """Release the bird"""
        if not self.loaded_bird or not self.is_pulling or self.loaded_bird.launched:
            return
            
        # Calculate launch velocity
        # Velocity is opposite of pull direction (like releasing a real slingshot)
        dx = self.rest_x - self.pull_x  # How far we pulled back
        dy = self.rest_y - self.pull_y  # How far we pulled down
        
        # Make sure we have some velocity
        if abs(dx) < 5 and abs(dy) < 5:
            dx = 10
            dy = -10
        
        # Scale velocity by launch power
        velocity_x = dx * LAUNCH_POWER
        velocity_y = dy * LAUNCH_POWER
        
        # Launch the bird
        self.loaded_bird.launch((velocity_x, velocity_y))
        
        # Reset slingshot
        self.loaded_bird = None
        self.is_pulling = False
        self.pull_x = self.rest_x
        self.pull_y = self.rest_y
        self.trajectory_points = []
        
    def _calculate_trajectory(self):
        """Calculate trajectory preview"""
        self.trajectory_points = []
        
        if not self.is_pulling:
            return
            
        # Initial velocity (same calculation as release)
        vx = (self.rest_x - self.pull_x) * LAUNCH_POWER
        vy = (self.rest_y - self.pull_y) * LAUNCH_POWER
        
        # Start from current pull position
        x = self.pull_x
        y = self.pull_y
        
        # Physics simulation
        dt = 0.02
        gravity = 981
        
        # Calculate trajectory points
        for i in range(60):
            # Update position
            x += vx * dt
            y += vy * dt
            
            # Apply gravity
            vy += gravity * dt
            
            # Apply air resistance
            vx *= 0.99
            vy *= 0.99
            
            # Stop if we hit the ground or go off screen
            if y > WIN_HEIGHT - GROUND_HEIGHT or x > WIN_WIDTH or x < 0:
                break
                
            # Store point for drawing
            self.trajectory_points.append((int(x), int(y)))
            
    def get_power(self):
        """Get current pull power as percentage"""
        if not self.is_pulling:
            return 0
            
        dx = self.rest_x - self.pull_x
        dy = self.rest_y - self.pull_y
        distance = math.hypot(dx, dy)
        return min(distance / self.max_stretch, 1.0)
        
    def draw(self, screen):
        """Draw the slingshot"""
        # Draw slingshot frame
        # Base
        base_rect = pygame.Rect(self.x - 4, self.y, 8, 60)
        pygame.draw.rect(screen, BROWN, base_rect)
        pygame.draw.rect(screen, BLACK, base_rect, 2)
        
        # Left fork arm
        pygame.draw.line(screen, BROWN, 
                        (self.x, self.y), 
                        self.left_fork, 6)
        pygame.draw.line(screen, BLACK, 
                        (self.x, self.y), 
                        self.left_fork, 2)
        
        # Right fork arm  
        pygame.draw.line(screen, BROWN, 
                        (self.x, self.y), 
                        self.right_fork, 6)
        pygame.draw.line(screen, BLACK, 
                        (self.x, self.y), 
                        self.right_fork, 2)
        
        # Fork tips
        pygame.draw.circle(screen, BROWN, self.left_fork, 4)
        pygame.draw.circle(screen, BLACK, self.left_fork, 4, 2)
        pygame.draw.circle(screen, BROWN, self.right_fork, 4)
        pygame.draw.circle(screen, BLACK, self.right_fork, 4, 2)
        
        # Draw trajectory preview (dotted line)
        if self.trajectory_points:
            for i, (x, y) in enumerate(self.trajectory_points):
                if i % 3 == 0:  # Every 3rd point for dotted effect
                    # Fade out dots over distance
                    alpha = 1.0 - (i / len(self.trajectory_points))
                    size = int(3 * alpha) + 1
                    color = (255, 255 - int(100 * alpha), 0)  # Yellow to white
                    pygame.draw.circle(screen, color, (x, y), size)
        
        # Draw rubber bands when pulling
        if self.is_pulling and self.loaded_bird and not self.loaded_bird.launched:
            # Rubber band thickness based on stretch
            power = self.get_power()
            thickness = max(2, int(5 - power * 3))
            
            # Back band (connects the two forks behind the bird)
            if power < 0.1:  # Only show when not stretched much
                pygame.draw.line(screen, (50, 30, 10), 
                               self.left_fork, self.right_fork, thickness)
            
            # Left rubber band (from left fork to bird)
            pygame.draw.line(screen, (60, 40, 20), 
                           self.left_fork, 
                           (self.pull_x, self.pull_y), 
                           thickness)
            pygame.draw.line(screen, BLACK, 
                           self.left_fork, 
                           (self.pull_x, self.pull_y), 
                           max(1, thickness - 2))
            
            # Right rubber band (from right fork to bird)
            pygame.draw.line(screen, (60, 40, 20), 
                           self.right_fork, 
                           (self.pull_x, self.pull_y), 
                           thickness)
            pygame.draw.line(screen, BLACK, 
                           self.right_fork, 
                           (self.pull_x, self.pull_y), 
                           max(1, thickness - 2))
            
            # Draw power indicator
            self._draw_power_meter(screen)
            
    def _draw_power_meter(self, screen):
        """Draw a power meter showing pull strength"""
        power = self.get_power()
        if power <= 0:
            return
            
        # Position for power meter
        meter_x = self.x - 60
        meter_y = self.y - 80
        meter_width = 10
        meter_height = 50
        
        # Background
        pygame.draw.rect(screen, (100, 100, 100), 
                       (meter_x, meter_y, meter_width, meter_height))
        
        # Power fill
        fill_height = int(meter_height * power)
        
        # Color based on power
        if power < 0.3:
            color = GREEN
        elif power < 0.6:
            color = YELLOW
        elif power < 0.8:
            color = ORANGE
        else:
            color = RED
            
        pygame.draw.rect(screen, color,
                       (meter_x, meter_y + meter_height - fill_height, 
                        meter_width, fill_height))
        
        # Border
        pygame.draw.rect(screen, BLACK,
                       (meter_x, meter_y, meter_width, meter_height), 2)
        
        # Power percentage
        font = pygame.font.Font(None, 20)
        text = font.render(f"{int(power * 100)}%", True, WHITE)
        screen.blit(text, (meter_x - 10, meter_y - 20))
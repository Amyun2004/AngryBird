"""
effects.py - Visual effects for impacts, explosions, and damage
"""

import pygame
import random
import math
from constants import *


class Particle:
    """Single particle for effects"""
    
    def __init__(self, x, y, vx, vy, color, size, lifetime):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.color = color
        self.size = size
        self.lifetime = lifetime
        self.max_lifetime = lifetime
        self.gravity = 500  # Gravity effect on particles
        
    def update(self, dt):
        """Update particle position and lifetime"""
        self.x += self.vx * dt
        self.y += self.vy * dt
        self.vy += self.gravity * dt  # Apply gravity
        self.lifetime -= dt
        
        # Fade out
        self.size *= 0.98
        
    def draw(self, screen):
        """Draw the particle"""
        if self.lifetime > 0:
            # Calculate alpha based on lifetime
            alpha = self.lifetime / self.max_lifetime
            # Draw with fading effect
            pos = (int(self.x), int(self.y))
            size = max(1, int(self.size))
            
            # Create a surface for the particle with alpha
            particle_surface = pygame.Surface((size * 2, size * 2), pygame.SRCALPHA)
            color_with_alpha = (*self.color, int(255 * alpha))
            pygame.draw.circle(particle_surface, color_with_alpha, (size, size), size)
            screen.blit(particle_surface, (pos[0] - size, pos[1] - size))
    
    def is_alive(self):
        """Check if particle should still exist"""
        return self.lifetime > 0 and self.size > 0.5


class DamageNumber:
    """Floating damage numbers"""
    
    def __init__(self, x, y, damage, color=RED):
        self.x = x
        self.y = y
        self.damage = int(damage)
        self.color = color
        self.lifetime = 1.0
        self.vy = -100  # Float upward
        self.font = pygame.font.Font(None, 24)
        
    def update(self, dt):
        """Update position"""
        self.y += self.vy * dt
        self.vy += 200 * dt  # Slow down floating
        self.lifetime -= dt
        
    def draw(self, screen):
        """Draw damage number"""
        if self.lifetime > 0:
            alpha = self.lifetime
            text = self.font.render(f"-{self.damage}", True, self.color)
            text_rect = text.get_rect(center=(int(self.x), int(self.y)))
            
            # Create surface with alpha for fading
            text_surface = pygame.Surface(text.get_size(), pygame.SRCALPHA)
            text_surface.set_alpha(int(255 * alpha))
            text_surface.blit(text, (0, 0))
            screen.blit(text_surface, text_rect)
    
    def is_alive(self):
        """Check if still visible"""
        return self.lifetime > 0


class EffectsManager:
    """Manages all visual effects"""
    
    def __init__(self):
        self.particles = []
        self.damage_numbers = []
        self.screen_shake = 0
        self.screen_shake_intensity = 0
        
    def create_impact_effect(self, x, y, intensity="normal"):
        """Create impact particles"""
        if intensity == "normal":
            particle_count = 10
            speed = 200
            colors = [WHITE, GRAY, YELLOW]
        elif intensity == "strong":
            particle_count = 20
            speed = 300
            colors = [ORANGE, YELLOW, RED]
        elif intensity == "destroy":
            particle_count = 30
            speed = 400
            colors = [ORANGE, RED, YELLOW, WHITE]
        else:
            particle_count = 5
            speed = 100
            colors = [WHITE, GRAY]
        
        for _ in range(particle_count):
            angle = random.uniform(0, 2 * math.pi)
            velocity = random.uniform(speed * 0.5, speed)
            vx = math.cos(angle) * velocity
            vy = math.sin(angle) * velocity
            color = random.choice(colors)
            size = random.uniform(2, 6)
            lifetime = random.uniform(0.3, 0.8)
            
            self.particles.append(Particle(x, y, vx, vy, color, size, lifetime))
    
    def create_destruction_effect(self, x, y, material):
        """Create destruction effect based on material"""
        if material == "wood":
            # Wood splinters
            colors = [WOOD_COLOR, BROWN, (139, 90, 43)]
            particle_count = 15
        elif material == "stone":
            # Stone debris
            colors = [STONE_COLOR, GRAY, DARK_GRAY]
            particle_count = 20
        elif material == "ice":
            # Ice shards
            colors = [ICE_COLOR, WHITE, LIGHTBLUE]
            particle_count = 25
        elif material == "metal":
            # Metal sparks
            colors = [METAL_COLOR, WHITE, YELLOW]
            particle_count = 10
        else:
            colors = [GRAY, WHITE]
            particle_count = 10
        
        for _ in range(particle_count):
            angle = random.uniform(0, 2 * math.pi)
            velocity = random.uniform(100, 300)
            vx = math.cos(angle) * velocity
            vy = math.sin(angle) * velocity - 100  # Bias upward
            color = random.choice(colors)
            size = random.uniform(3, 8)
            lifetime = random.uniform(0.5, 1.2)
            
            self.particles.append(Particle(x, y, vx, vy, color, size, lifetime))
    
    def create_pig_hit_effect(self, x, y, eliminated=False):
        """Create effect when pig is hit"""
        if eliminated:
            # Big poof effect
            for _ in range(25):
                angle = random.uniform(0, 2 * math.pi)
                velocity = random.uniform(150, 350)
                vx = math.cos(angle) * velocity
                vy = math.sin(angle) * velocity
                color = random.choice([PIG_COLOR, WHITE, GREEN])
                size = random.uniform(4, 10)
                lifetime = random.uniform(0.4, 1.0)
                
                self.particles.append(Particle(x, y, vx, vy, color, size, lifetime))
            
            # Add screen shake for elimination
            self.add_screen_shake(10, 0.3)
        else:
            # Small hit effect
            for _ in range(8):
                angle = random.uniform(0, 2 * math.pi)
                velocity = random.uniform(50, 150)
                vx = math.cos(angle) * velocity
                vy = math.sin(angle) * velocity
                color = random.choice([RED, YELLOW])
                size = random.uniform(2, 4)
                lifetime = random.uniform(0.2, 0.5)
                
                self.particles.append(Particle(x, y, vx, vy, color, size, lifetime))
    
    def add_damage_number(self, x, y, damage, color=RED):
        """Add floating damage number"""
        if damage > 0:
            self.damage_numbers.append(DamageNumber(x, y - 20, damage, color))
    
    def add_screen_shake(self, intensity, duration):
        """Add screen shake effect"""
        self.screen_shake = duration
        self.screen_shake_intensity = intensity
    
    def update(self, dt):
        """Update all effects"""
        # Update particles
        for particle in self.particles[:]:
            particle.update(dt)
            if not particle.is_alive():
                self.particles.remove(particle)
        
        # Update damage numbers
        for num in self.damage_numbers[:]:
            num.update(dt)
            if not num.is_alive():
                self.damage_numbers.remove(num)
        
        # Update screen shake
        if self.screen_shake > 0:
            self.screen_shake -= dt
            if self.screen_shake <= 0:
                self.screen_shake = 0
                self.screen_shake_intensity = 0
    
    def draw(self, screen):
        """Draw all effects"""
        # Draw particles
        for particle in self.particles:
            particle.draw(screen)
        
        # Draw damage numbers
        for num in self.damage_numbers:
            num.draw(screen)
    
    def get_screen_offset(self):
        """Get current screen shake offset"""
        if self.screen_shake > 0:
            offset_x = random.randint(-self.screen_shake_intensity, self.screen_shake_intensity)
            offset_y = random.randint(-self.screen_shake_intensity, self.screen_shake_intensity)
            return offset_x, offset_y
        return 0, 0
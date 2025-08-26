"""
entities.py - Game entities including Birds, Pigs, and Blocks
"""

import pygame
import pymunk
import math
from physics_engine import (
    BIRD_CATEGORY, PIG_CATEGORY, BLOCK_CATEGORY,
    COLLISION_TYPE_BIRD, COLLISION_TYPE_PIG, COLLISION_TYPE_BLOCK
)
from constants import *


class Bird:
    """Angry bird that can be launched from slingshot"""
    
    def __init__(self, space, x, y, radius=12, mass=5, color=RED, bird_type="red"):
        self.radius = radius
        self.mass = mass
        self.color = color
        self.bird_type = bird_type
        self.launched = False
        self.space = space
        
        # Create physics body
        moment = pymunk.moment_for_circle(mass, 0, radius)
        self.body = pymunk.Body(mass, moment, body_type=pymunk.Body.DYNAMIC)
        self.body.position = x, y
        self.shape = pymunk.Circle(self.body, radius)
        self.shape.elasticity = 0.4
        self.shape.friction = 0.5
        self.shape.collision_type = COLLISION_TYPE_BIRD
        self.shape.filter = pymunk.ShapeFilter(categories=BIRD_CATEGORY)
        
        space.add(self.body, self.shape)
        
    def launch(self, velocity):
        """Launch the bird with given velocity"""
        if not self.launched:
            # Validate velocity
            vx, vy = velocity
            if not (math.isfinite(vx) and math.isfinite(vy)):
                vx, vy = 100, -100  # Default safe velocity
            
            # Clamp velocity to reasonable limits
            max_velocity = 2000
            vx = max(-max_velocity, min(vx, max_velocity))
            vy = max(-max_velocity, min(vy, max_velocity))
            
            self.body.velocity = vx, vy
            self.launched = True
            
    def is_stopped(self):
        """True only when the launched bird is essentially resting on the ground."""
        if not self.launched:
            return False

        vel = self.body.velocity.length
        # Treat as "on ground" when the bird is at/near ground level
        on_ground = self.body.position.y >= (WIN_HEIGHT - GROUND_HEIGHT - self.radius - 2)

        # Require both: very slow *and* on the ground
        return vel < 5 and on_ground           
    def draw(self, screen):
        """Draw the bird"""
        # Check for valid position
        x, y = self.body.position.x, self.body.position.y
        
        # Handle NaN or invalid positions
        if not (math.isfinite(x) and math.isfinite(y)):
            x, y = 100, 100  # Default safe position
            self.body.position = x, y
        
        # Clamp to screen bounds
        x = max(0, min(x, 1200))
        y = max(0, min(y, 700))
        
        pos = int(x), int(y)
        
        # Main body
        pygame.draw.circle(screen, self.color, pos, self.radius)
        pygame.draw.circle(screen, BLACK, pos, self.radius, 2)
        
        # Draw features based on bird type
        if self.bird_type == "red":
            # Eye
            eye_pos = (pos[0] + 5, pos[1] - 3)
            pygame.draw.circle(screen, WHITE, eye_pos, 3)
            pygame.draw.circle(screen, BLACK, eye_pos, 2)
            
            # Beak
            beak_points = [
                (pos[0] + self.radius, pos[1]),
                (pos[0] + self.radius + 5, pos[1] - 2),
                (pos[0] + self.radius + 5, pos[1] + 2)
            ]
            pygame.draw.polygon(screen, YELLOW, beak_points)
            
        elif self.bird_type == "yellow":
            # Triangular shape effect
            eye_pos = (pos[0] + 3, pos[1] - 3)
            pygame.draw.circle(screen, WHITE, eye_pos, 4)
            pygame.draw.circle(screen, BLACK, eye_pos, 2)
            
            # Bigger beak
            beak_points = [
                (pos[0] + self.radius, pos[1]),
                (pos[0] + self.radius + 7, pos[1] - 3),
                (pos[0] + self.radius + 7, pos[1] + 3)
            ]
            pygame.draw.polygon(screen, ORANGE, beak_points)
            
        elif self.bird_type == "blue":
            # Smaller eye for blue bird
            eye_pos = (pos[0] + 3, pos[1] - 2)
            pygame.draw.circle(screen, WHITE, eye_pos, 2)
            pygame.draw.circle(screen, BLACK, eye_pos, 1)
            
    def remove(self):
        """Remove bird from physics space"""
        self.space.remove(self.body, self.shape)


class Pig:
    """Enemy pig that needs to be defeated"""
    
    def __init__(self, space, x, y, radius=15, health=100, pig_type="normal"):
        self.radius = radius
        self.max_health = health
        self.health = health
        self.space = space
        self.dead = False
        self.pig_type = pig_type
        
        # Different pig types
        if pig_type == "helmet":
            self.max_health = 150
            self.health = 150
            mass = 3
        elif pig_type == "king":
            self.radius = 20
            self.max_health = 200
            self.health = 200
            mass = 4
        else:
            mass = 2
        
        # Create physics body
        moment = pymunk.moment_for_circle(mass, 0, radius)
        self.body = pymunk.Body(mass, moment)
        self.body.position = x, y
        self.shape = pymunk.Circle(self.body, radius)
        self.shape.elasticity = 0.3
        self.shape.friction = 0.5
        self.shape.collision_type = COLLISION_TYPE_PIG
        self.shape.filter = pymunk.ShapeFilter(categories=PIG_CATEGORY)
        
        space.add(self.body, self.shape)
        
    def take_damage(self, damage):
        """Apply damage to the pig"""
        if self.dead:
            return False
            
        self.health -= damage
        if self.health <= 0 and not self.dead:
            self.dead = True
            self.space.remove(self.body, self.shape)
            return True  # Pig eliminated
        return False  # Pig still alive
        
    def draw(self, screen):
        """Draw the pig"""
        if not self.dead:
            # Check for valid position
            x, y = self.body.position.x, self.body.position.y
            
            # Handle NaN or invalid positions
            if not (math.isfinite(x) and math.isfinite(y)):
                return  # Skip drawing if position is invalid
            
            pos = int(x), int(y)
            
            # Body color based on health
            if self.health > self.max_health * 0.7:
                color = PIG_COLOR
            elif self.health > self.max_health * 0.3:
                color = (120, 200, 120)  # Damaged
            else:
                color = (100, 180, 100)  # Heavily damaged
            
            # Draw main body
            pygame.draw.circle(screen, color, pos, self.radius)
            pygame.draw.circle(screen, BLACK, pos, self.radius, 2)
            
            # Draw pig type specific features
            if self.pig_type == "helmet":
                # Draw helmet
                helmet_rect = pygame.Rect(
                    pos[0] - self.radius + 2, 
                    pos[1] - self.radius - 2,
                    (self.radius - 2) * 2, 
                    self.radius
                )
                pygame.draw.ellipse(screen, GRAY, helmet_rect)
                pygame.draw.ellipse(screen, BLACK, helmet_rect, 2)
                
            elif self.pig_type == "king":
                # Draw crown
                crown_points = [
                    (pos[0] - 10, pos[1] - self.radius),
                    (pos[0] - 10, pos[1] - self.radius - 8),
                    (pos[0] - 5, pos[1] - self.radius - 5),
                    (pos[0], pos[1] - self.radius - 10),
                    (pos[0] + 5, pos[1] - self.radius - 5),
                    (pos[0] + 10, pos[1] - self.radius - 8),
                    (pos[0] + 10, pos[1] - self.radius)
                ]
                pygame.draw.polygon(screen, GOLD, crown_points)
                pygame.draw.polygon(screen, BLACK, crown_points, 2)
            
            # Draw snout
            snout_pos = (pos[0], pos[1] + 3)
            pygame.draw.ellipse(screen, (114, 208, 114), 
                              (snout_pos[0] - 6, snout_pos[1] - 4, 12, 8))
            # Nostrils
            pygame.draw.circle(screen, BLACK, (snout_pos[0] - 2, snout_pos[1]), 1)
            pygame.draw.circle(screen, BLACK, (snout_pos[0] + 2, snout_pos[1]), 1)
            
            # Draw eyes
            eye_left = (pos[0] - 5, pos[1] - 5)
            eye_right = (pos[0] + 5, pos[1] - 5)
            pygame.draw.circle(screen, WHITE, eye_left, 3)
            pygame.draw.circle(screen, WHITE, eye_right, 3)
            pygame.draw.circle(screen, BLACK, eye_left, 2)
            pygame.draw.circle(screen, BLACK, eye_right, 2)
            
            # Draw health bar if damaged
            if self.health < self.max_health:
                bar_width = 30
                bar_height = 4
                bar_x = pos[0] - bar_width // 2
                bar_y = pos[1] - self.radius - 10
                
                # Background (red)
                pygame.draw.rect(screen, RED, (bar_x, bar_y, bar_width, bar_height))
                # Health (green)
                health_percentage = self.health / self.max_health
                pygame.draw.rect(screen, GREEN, 
                               (bar_x, bar_y, bar_width * health_percentage, bar_height))
                # Border
                pygame.draw.rect(screen, BLACK, (bar_x, bar_y, bar_width, bar_height), 1)


class Block:
    """Building block that can be destroyed"""
    
    def __init__(self, space, x, y, width, height, material="wood"):
        self.width = width
        self.height = height
        self.material = material
        self.space = space
        self.destroyed = False
        
        # Material properties
        materials = {
            "wood": {
                "mass": 0.5,
                "health": 70,
                "color": WOOD_COLOR,
                "elasticity": 0.4
            },
            "stone": {
                "mass": 2,
                "health": 150,
                "color": STONE_COLOR,
                "elasticity": 0.5
            },
            "ice": {
                "mass": 0.3,
                "health": 30,
                "color": ICE_COLOR,
                "elasticity": 0.3
            },
            "metal": {
                "mass": 3,
                "health": 250,
                "color": METAL_COLOR,
                "elasticity": 0.6
            }
        }
        
        props = materials.get(material, materials["wood"])
        self.mass = props["mass"]
        self.max_health = props["health"]
        self.color = props["color"]
        self.original_color = props["color"]
        elasticity = props["elasticity"]
        
        self.health = self.max_health
        
        # Create physics body
        moment = pymunk.moment_for_box(self.mass, (width, height))
        self.body = pymunk.Body(self.mass, moment)
        self.body.position = x + width/2, y + height/2
        
        # Create shape
        vertices = [
            (-width/2, -height/2), 
            (width/2, -height/2), 
            (width/2, height/2), 
            (-width/2, height/2)
        ]
        self.shape = pymunk.Poly(self.body, vertices)
        self.shape.elasticity = elasticity
        self.shape.friction = 0.5
        self.shape.collision_type = COLLISION_TYPE_BLOCK
        self.shape.filter = pymunk.ShapeFilter(categories=BLOCK_CATEGORY)
        
        space.add(self.body, self.shape)
        
    def take_damage(self, damage):
        """Apply damage to the block"""
        if self.destroyed:
            return False
            
        self.health -= damage
        
        # Update color based on damage
        if self.health < self.max_health * 0.5:
            # Darken when damaged
            self.color = tuple(max(0, c - 50) for c in self.original_color)
        
        if self.health <= 0:
            self.destroyed = True
            self.space.remove(self.body, self.shape)
            return True  # Block destroyed
        return False  # Block still intact
        
    def draw(self, screen):
        """Draw the block"""
        if not self.destroyed:
            # Check for valid position
            x, y = self.body.position.x, self.body.position.y
            angle = self.body.angle
            
            # Handle NaN or invalid positions
            if not (math.isfinite(x) and math.isfinite(y) and math.isfinite(angle)):
                return  # Skip drawing if position is invalid
            
            # Get the vertices in world coordinates
            vertices = []
            for v in self.shape.get_vertices():
                vx = x + v.rotated(angle).x
                vy = y + v.rotated(angle).y
                if math.isfinite(vx) and math.isfinite(vy):
                    vertices.append((int(vx), int(vy)))
            
            if len(vertices) < 3:
                return  # Not enough valid vertices to draw
            
            # Draw the block
            pygame.draw.polygon(screen, self.color, vertices)
            pygame.draw.polygon(screen, BLACK, vertices, 2)
            
            # Draw material-specific textures
            if self.material == "wood" and len(vertices) >= 4:
                # Wood grain lines
                for i in range(1, 3):
                    start_x = vertices[0][0] + (vertices[1][0] - vertices[0][0]) * i / 3
                    start_y = vertices[0][1] + (vertices[1][1] - vertices[0][1]) * i / 3
                    end_x = vertices[3][0] + (vertices[2][0] - vertices[3][0]) * i / 3
                    end_y = vertices[3][1] + (vertices[2][1] - vertices[3][1]) * i / 3
                    pygame.draw.line(screen, BROWN, (start_x, start_y), (end_x, end_y), 1)
                    
            elif self.material == "stone" and len(vertices) >= 4:
                # Stone cracks when damaged
                if self.health < self.max_health * 0.7:
                    center_x = sum(v[0] for v in vertices) // 4
                    center_y = sum(v[1] for v in vertices) // 4
                    # Draw crack lines
                    pygame.draw.line(screen, DARK_GRAY, 
                                   vertices[0], (center_x, center_y), 1)
                    pygame.draw.line(screen, DARK_GRAY, 
                                   vertices[2], (center_x, center_y), 1)
                    
            elif self.material == "ice":
                # Ice transparency effect (lighter center)
                if len(vertices) >= 4:
                    inner_vertices = []
                    center_x = sum(v[0] for v in vertices) // 4
                    center_y = sum(v[1] for v in vertices) // 4
                    for v in vertices:
                        inner_x = v[0] + (center_x - v[0]) * 0.3
                        inner_y = v[1] + (center_y - v[1]) * 0.3
                        inner_vertices.append((inner_x, inner_y))
                    pygame.draw.polygon(screen, (200, 240, 245), inner_vertices)
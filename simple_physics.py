"""
simple_physics.py - Simplified physics engine for compatibility
This is an alternative if your pymunk version has issues with collision handlers
"""

import pymunk
import math

# Physics constants
GRAVITY = 981  # pixels/s^2
ELASTICITY_GROUND = 0.6
FRICTION_GROUND = 1.0
ELASTICITY_WALL = 0.6

# Collision categories for filtering
BIRD_CATEGORY = 0x0001
PIG_CATEGORY = 0x0002
BLOCK_CATEGORY = 0x0004
GROUND_CATEGORY = 0x0008

# Collision types
COLLISION_TYPE_BIRD = 1
COLLISION_TYPE_PIG = 2
COLLISION_TYPE_BLOCK = 3
COLLISION_TYPE_GROUND = 4


class SimplePhysicsEngine:
    """Simplified physics engine with manual collision detection"""
    
    def __init__(self, width, height, ground_height):
        self.space = pymunk.Space()
        self.space.gravity = (0, GRAVITY)
        self.width = width
        self.height = height
        self.ground_height = ground_height
        
        # Score tracking
        self.score_earned = 0
        
        # Object references for collision checking
        self.pigs = []
        self.blocks = []
        self.birds = []
        
        # Setup boundaries
        self._create_boundaries()
        
        # Collision tracking
        self.previous_contacts = set()
        
    def _create_boundaries(self):
        """Create ground and walls"""
        # Create static body for boundaries
        ground_body = pymunk.Body(body_type=pymunk.Body.STATIC)
        
        # Ground
        ground_shape = pymunk.Segment(
            ground_body, 
            (0, self.height - self.ground_height), 
            (self.width, self.height - self.ground_height), 
            5
        )
        ground_shape.elasticity = ELASTICITY_GROUND
        ground_shape.friction = FRICTION_GROUND
        ground_shape.collision_type = COLLISION_TYPE_GROUND
        
        # Walls
        left_wall = pymunk.Segment(ground_body, (0, 0), (0, self.height), 5)
        right_wall = pymunk.Segment(ground_body, (self.width, 0), (self.width, self.height), 5)
        left_wall.elasticity = ELASTICITY_WALL
        right_wall.elasticity = ELASTICITY_WALL
        
        self.space.add(ground_body, ground_shape, left_wall, right_wall)
    
    def setup_collision_handlers(self, pigs, blocks):
        """Store references to game objects for collision detection"""
        self.pigs = pigs
        self.blocks = blocks
        
    def step(self, dt):
        """Advance physics simulation and check collisions"""
        # Step physics
        self.space.step(dt)
        
        # Manual collision detection
        self._check_collisions()
    
    def _check_collisions(self):
        """Manually check for collisions between objects"""
        current_contacts = set()
        
        # Check bird-pig collisions
        for bird in self.birds:
            if not hasattr(bird, 'body'):
                continue
                
            for pig in self.pigs:
                if pig.dead:
                    continue
                    
                # Calculate distance between centers
                dx = bird.body.position.x - pig.body.position.x
                dy = bird.body.position.y - pig.body.position.y
                distance = math.sqrt(dx * dx + dy * dy)
                
                # Check if colliding (circle-circle collision)
                if distance < bird.radius + pig.radius:
                    contact_key = (id(bird), id(pig), 'bird_pig')
                    current_contacts.add(contact_key)
                    
                    # Only process new collisions
                    if contact_key not in self.previous_contacts:
                        # Calculate impact based on bird velocity
                        velocity = math.sqrt(
                            bird.body.velocity.x ** 2 + 
                            bird.body.velocity.y ** 2
                        )
                        damage = min(velocity / 20, 50)
                        
                        if pig.take_damage(damage):
                            self.score_earned += 500  # Pig eliminated
                        else:
                            self.score_earned += 10  # Pig hit
        
        # Check bird-block collisions
        for bird in self.birds:
            if not hasattr(bird, 'body'):
                continue
                
            for block in self.blocks:
                if block.destroyed:
                    continue
                
                # Simple AABB check for bird-block
                bird_x, bird_y = bird.body.position.x, bird.body.position.y
                block_x, block_y = block.body.position.x, block.body.position.y
                
                # Get block bounds (approximation)
                half_width = block.width / 2
                half_height = block.height / 2
                
                # Check if bird circle intersects block rectangle
                closest_x = max(block_x - half_width, 
                               min(bird_x, block_x + half_width))
                closest_y = max(block_y - half_height, 
                               min(bird_y, block_y + half_height))
                
                distance = math.sqrt(
                    (bird_x - closest_x) ** 2 + 
                    (bird_y - closest_y) ** 2
                )
                
                if distance < bird.radius:
                    contact_key = (id(bird), id(block), 'bird_block')
                    current_contacts.add(contact_key)
                    
                    if contact_key not in self.previous_contacts:
                        velocity = math.sqrt(
                            bird.body.velocity.x ** 2 + 
                            bird.body.velocity.y ** 2
                        )
                        damage = min(velocity / 40, 30)
                        
                        if block.take_damage(damage):
                            self.score_earned += 100  # Block destroyed
                        else:
                            self.score_earned += 5  # Block hit
        
        # Check block-pig collisions (falling blocks)
        for block in self.blocks:
            if block.destroyed:
                continue
                
            for pig in self.pigs:
                if pig.dead:
                    continue
                
                # Get block center
                block_x, block_y = block.body.position.x, block.body.position.y
                pig_x, pig_y = pig.body.position.x, pig.body.position.y
                
                # Simple distance check
                dx = block_x - pig_x
                dy = block_y - pig_y
                distance = math.sqrt(dx * dx + dy * dy)
                
                # Rough collision check
                if distance < (block.width + block.height) / 4 + pig.radius:
                    contact_key = (id(block), id(pig), 'block_pig')
                    current_contacts.add(contact_key)
                    
                    if contact_key not in self.previous_contacts:
                        # Check if block is falling
                        if abs(block.body.velocity.y) > 50:
                            damage = min(abs(block.body.velocity.y) / 10, 40)
                            
                            if pig.take_damage(damage):
                                self.score_earned += 300  # Pig crushed
        
        # Update previous contacts
        self.previous_contacts = current_contacts
    
    def add_bird(self, bird):
        """Register a bird for collision detection"""
        if bird not in self.birds:
            self.birds.append(bird)
    
    def remove_bird(self, bird):
        """Remove a bird from collision detection"""
        if bird in self.birds:
            self.birds.remove(bird)
    
    def get_and_reset_score(self):
        """Get earned score and reset counter"""
        score = self.score_earned
        self.score_earned = 0
        return score
    
    def remove_body(self, body, shape):
        """Safely remove a body and shape from the space"""
        try:
            self.space.remove(body, shape)
        except:
            pass  # Already removed
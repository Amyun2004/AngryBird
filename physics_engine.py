"""
enhanced_physics_engine.py - Enhanced physics with realistic damage and destruction
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

# Enhanced damage multipliers
DAMAGE_MULTIPLIERS = {
    "red": 1.0,      # Balanced bird
    "yellow": 1.8,   # Yellow birds are powerful against wood
    "blue": 0.6,     # Blue birds do less damage but good against ice
}

# Material properties with more realistic values
MATERIAL_PROPERTIES = {
    "ice": {
        "damage_resistance": 0.2,   # Ice is very fragile
        "mass_multiplier": 0.3,     # Light
        "stability_threshold": 15,   # Breaks easily
        "chain_damage_multiplier": 1.5  # Shatters and spreads damage
    },
    "wood": {
        "damage_resistance": 1.0,   # Standard resistance
        "mass_multiplier": 0.5,     # Medium weight
        "stability_threshold": 35,   # Moderate stability
        "chain_damage_multiplier": 1.0
    },
    "stone": {
        "damage_resistance": 2.5,   # Strong material
        "mass_multiplier": 2.0,     # Heavy
        "stability_threshold": 60,   # Very stable
        "chain_damage_multiplier": 0.8
    },
    "metal": {
        "damage_resistance": 4.0,   # Very strong
        "mass_multiplier": 3.0,     # Very heavy
        "stability_threshold": 80,   # Extremely stable
        "chain_damage_multiplier": 0.5
    }
}

# Score values with more nuanced scoring
SCORE_VALUES = {
    "bird_hit_pig": 10,
    "pig_damaged": 100,
    "pig_eliminated": 5000,
    "pig_crushed": 3000,
    "pig_fall_damage": 2000,
    "block_damaged": 50,
    "block_destroyed": 500,
    "block_shattered": 1000,  # Bonus for complete destruction
    "chain_reaction": 250,     # Bonus for causing chain reactions
    "structure_collapsed": 2000,  # Bonus for major collapses
}


class EnhancedPhysicsEngine:
    """Enhanced physics engine with realistic damage and scoring"""
    
    def __init__(self, width, height, ground_height):
        self.space = pymunk.Space()
        self.space.gravity = (0, GRAVITY)
        self.space.damping = 0.95  # Add some air resistance
        self.width = width
        self.height = height
        self.ground_height = ground_height
        
        # Score tracking
        self.score_earned = 0
        self.combo_multiplier = 1.0
        self.combo_timer = 0
        
        # Object references
        self.pigs = []
        self.blocks = []
        self.birds = []
        
        # Collision tracking
        self.collision_events = []
        self.previous_velocities = {}
        self.structural_integrity = {}
        self.chain_reaction_timer = 0
        
        # Setup boundaries
        self._create_boundaries()
        
    def _create_boundaries(self):
        """Create ground and walls with proper physics"""
        ground_body = pymunk.Body(body_type=pymunk.Body.STATIC)
        
        # Ground with proper thickness for stability
        ground_shape = pymunk.Segment(
            ground_body, 
            (0, self.height - self.ground_height), 
            (self.width, self.height - self.ground_height), 
            5
        )
        ground_shape.elasticity = ELASTICITY_GROUND
        ground_shape.friction = FRICTION_GROUND
        ground_shape.collision_type = COLLISION_TYPE_GROUND
        ground_shape.filter = pymunk.ShapeFilter(categories=GROUND_CATEGORY)
        
        # Walls
        left_wall = pymunk.Segment(ground_body, (0, 0), (0, self.height), 5)
        right_wall = pymunk.Segment(ground_body, (self.width, 0), (self.width, self.height), 5)
        left_wall.elasticity = ELASTICITY_WALL
        right_wall.elasticity = ELASTICITY_WALL
        
        self.space.add(ground_body, ground_shape, left_wall, right_wall)
    
    def calculate_impact_force(self, arbiter, mass1, mass2):
        """Calculate realistic impact force from collision"""
        # Get impulse from collision
        impulse = arbiter.total_impulse.length
        
        # Calculate relative velocity at impact
        if hasattr(arbiter, 'contact_point_set'):
            points = arbiter.contact_point_set.points
            if points:
                # Use actual collision normal and distance
                normal = arbiter.contact_point_set.normal
                distance = points[0].distance if points[0].distance > 0 else 0.1
                
                # Impact force considers both impulse and penetration
                force = (impulse / (1 + distance)) * (1 + abs(normal.y) * 0.5)
            else:
                force = impulse
        else:
            force = impulse
        
        # Scale by combined mass for more realistic physics
        total_mass = mass1 + mass2
        force = force * (2 * mass1 * mass2) / (total_mass * total_mass)
        
        return force
    
    def calculate_damage(self, force, material_resistance, impact_type="direct"):
        """Calculate damage with material properties"""
        # Base damage from force
        base_damage = math.sqrt(force) / 10
        
        # Apply material resistance
        damage = base_damage / material_resistance
        
        # Different impact types have different effectiveness
        if impact_type == "crush":
            damage *= 1.5  # Crushing damage is more effective
        elif impact_type == "shear":
            damage *= 1.2  # Sideways impacts
        elif impact_type == "chain":
            damage *= 0.8  # Chain reaction damage is reduced
        
        # Apply combo multiplier for chain reactions
        damage *= self.combo_multiplier
        
        return min(damage, 100)  # Cap at 100 damage
    
    def check_structural_stability(self, block):
        """Check if a block's removal causes structural collapse"""
        if not hasattr(block, 'body'):
            return []
        
        # Find blocks that are supported by this block
        supported_blocks = []
        block_x = block.body.position.x
        block_y = block.body.position.y
        
        for other_block in self.blocks:
            if other_block == block or other_block.destroyed:
                continue
            
            other_x = other_block.body.position.x
            other_y = other_block.body.position.y
            
            # Check if other block is above and nearby
            if other_y < block_y - 20:  # Above
                if abs(other_x - block_x) < block.width:  # Horizontally aligned
                    supported_blocks.append(other_block)
        
        return supported_blocks
    
    def trigger_chain_reaction(self, origin_pos, force, radius=100):
        """Trigger chain reaction damage in an area"""
        chain_damaged = []
        
        for block in self.blocks:
            if block.destroyed:
                continue
            
            # Calculate distance from origin
            dx = block.body.position.x - origin_pos[0]
            dy = block.body.position.y - origin_pos[1]
            distance = math.sqrt(dx * dx + dy * dy)
            
            if distance < radius:
                # Damage falls off with distance
                distance_factor = 1 - (distance / radius)
                chain_damage = force * distance_factor * 0.3
                
                # Apply material's chain reaction susceptibility
                material_props = MATERIAL_PROPERTIES.get(block.material, MATERIAL_PROPERTIES["wood"])
                chain_damage *= material_props["chain_damage_multiplier"]
                
                if block.take_damage(chain_damage):
                    chain_damaged.append(block)
                    self.score_earned += SCORE_VALUES["chain_reaction"]
        
        return chain_damaged
    
    def setup_collision_handlers(self, pigs, blocks):
        """Setup enhanced collision handlers"""
        self.pigs = pigs
        self.blocks = blocks
        
        def bird_pig_collision(arbiter, space, data):
            bird_shape, pig_shape = arbiter.shapes
            
            # Find bird for damage calculation
            bird = None
            for b in self.birds:
                if hasattr(b, 'shape') and b.shape == bird_shape:
                    bird = b
                    break
            
            if not bird:
                return True
            
            # Find pig
            pig = None
            for p in self.pigs:
                if p.shape == pig_shape:
                    pig = p
                    break
            
            if not pig:
                return True
            
            # Calculate impact force
            force = self.calculate_impact_force(arbiter, bird.mass, 2)
            
            # Get bird damage multiplier
            bird_multiplier = DAMAGE_MULTIPLIERS.get(bird.bird_type, 1.0)
            
            # Calculate damage
            damage = self.calculate_damage(force * bird_multiplier, 1.0, "direct")
            
            # Special pig resistances
            if pig.pig_type == "helmet":
                damage *= 0.5  # Helmets provide protection
            elif pig.pig_type == "king":
                damage *= 0.7  # Kings are tougher
            
            # Apply damage
            if pig.take_damage(damage):
                self.score_earned += SCORE_VALUES["pig_eliminated"]
                self.collision_events.append(("pig_eliminated", pig.body.position))
                # Start combo
                self.combo_multiplier = min(self.combo_multiplier + 0.2, 3.0)
                self.combo_timer = 60  # 1 second at 60 FPS
            else:
                self.score_earned += SCORE_VALUES["bird_hit_pig"]
                self.collision_events.append(("pig_hit", pig.body.position))
            
            return True
        
        def bird_block_collision(arbiter, space, data):
            bird_shape, block_shape = arbiter.shapes
            
            # Find objects
            bird = None
            for b in self.birds:
                if hasattr(b, 'shape') and b.shape == bird_shape:
                    bird = b
                    break
            
            block = None
            for bl in self.blocks:
                if bl.shape == block_shape:
                    block = bl
                    break
            
            if not bird or not block:
                return True
            
            # Calculate impact force
            force = self.calculate_impact_force(arbiter, bird.mass, block.mass)
            
            # Get bird and material multipliers
            bird_multiplier = DAMAGE_MULTIPLIERS.get(bird.bird_type, 1.0)
            
            # Special interactions
            if bird.bird_type == "yellow" and block.material == "wood":
                bird_multiplier *= 2.0  # Yellow birds demolish wood
            elif bird.bird_type == "blue" and block.material == "ice":
                bird_multiplier *= 2.5  # Blue birds shatter ice
            
            # Get material resistance
            material_props = MATERIAL_PROPERTIES.get(block.material, MATERIAL_PROPERTIES["wood"])
            resistance = material_props["damage_resistance"]
            
            # Calculate damage
            damage = self.calculate_damage(force * bird_multiplier, resistance, "direct")
            
            # Check for structural weakness
            if damage > material_props["stability_threshold"]:
                # Structural failure - extra damage
                damage *= 1.5
                supported = self.check_structural_stability(block)
                if supported:
                    self.score_earned += SCORE_VALUES["structure_collapsed"]
                    # Damage supported blocks
                    for sup_block in supported:
                        sup_block.take_damage(20)
            
            # Apply damage
            if block.take_damage(damage):
                self.score_earned += SCORE_VALUES["block_destroyed"]
                self.collision_events.append(("block_destroyed", block.body.position))
                
                # Trigger chain reaction for certain materials
                if block.material in ["ice", "wood"]:
                    self.trigger_chain_reaction(
                        (block.body.position.x, block.body.position.y),
                        force * 0.5,
                        radius=80 if block.material == "ice" else 60
                    )
                
                # Combo bonus
                self.combo_multiplier = min(self.combo_multiplier + 0.1, 3.0)
                self.combo_timer = 60
            else:
                self.score_earned += SCORE_VALUES["block_damaged"]
                self.collision_events.append(("block_hit", block.body.position))
            
            return True
        
        def block_pig_collision(arbiter, space, data):
            block_shape, pig_shape = arbiter.shapes
            
            # Find objects
            block = None
            for bl in self.blocks:
                if bl.shape == block_shape:
                    block = bl
                    break
            
            pig = None
            for p in self.pigs:
                if p.shape == pig_shape:
                    pig = p
                    break
            
            if not block or not pig:
                return True
            
            # Calculate crushing force
            force = self.calculate_impact_force(arbiter, block.mass, 2)
            
            # Falling blocks do more damage
            if block.body.velocity.y > 50:
                impact_type = "crush"
                force *= 1.5 + (block.body.velocity.y / 200)
            else:
                impact_type = "direct"
            
            # Heavy materials crush better
            material_props = MATERIAL_PROPERTIES.get(block.material, MATERIAL_PROPERTIES["wood"])
            force *= material_props["mass_multiplier"]
            
            damage = self.calculate_damage(force, 0.8, impact_type)
            
            if pig.take_damage(damage):
                self.score_earned += SCORE_VALUES["pig_crushed"]
                self.collision_events.append(("pig_crushed", pig.body.position))
                self.combo_multiplier = min(self.combo_multiplier + 0.3, 3.0)
                self.combo_timer = 60
            else:
                self.score_earned += SCORE_VALUES["pig_damaged"]
            
            return True
        
        def block_block_collision(arbiter, space, data):
            """Enhanced block-to-block collisions with realistic physics"""
            block1_shape, block2_shape = arbiter.shapes
            
            blocks_involved = []
            for block in self.blocks:
                if block.shape in [block1_shape, block2_shape]:
                    blocks_involved.append(block)
            
            if len(blocks_involved) < 2:
                return True
            
            block1, block2 = blocks_involved[0], blocks_involved[1]
            
            # Calculate collision force
            force = self.calculate_impact_force(arbiter, block1.mass, block2.mass)
            
            # Both blocks take damage based on material
            for block, other in [(block1, block2), (block2, block1)]:
                material_props = MATERIAL_PROPERTIES.get(block.material, MATERIAL_PROPERTIES["wood"])
                other_props = MATERIAL_PROPERTIES.get(other.material, MATERIAL_PROPERTIES["wood"])
                
                # Harder materials damage softer ones more
                hardness_factor = other_props["damage_resistance"] / material_props["damage_resistance"]
                
                damage = self.calculate_damage(
                    force * hardness_factor * 0.3,
                    material_props["damage_resistance"],
                    "shear"
                )
                
                # Ice shatters on impact
                if block.material == "ice" and force > 500:
                    damage *= 3
                
                if block.take_damage(damage):
                    self.score_earned += SCORE_VALUES["block_destroyed"] // 2
                    self.collision_events.append(("block_collapsed", block.body.position))
            
            return True
        
        def pig_ground_collision(arbiter, space, data):
            """Pigs take realistic fall damage"""
            pig_shape, ground_shape = arbiter.shapes
            
            for pig in self.pigs:
                if pig.shape == pig_shape:
                    # Check fall velocity
                    fall_speed = abs(pig.body.velocity.y)
                    
                    # Damage threshold based on pig type
                    threshold = 250
                    if pig.pig_type == "helmet":
                        threshold = 350  # Helmets protect from falls
                    elif pig.pig_type == "king":
                        threshold = 300
                    
                    if fall_speed > threshold:
                        damage = (fall_speed - threshold) / 5
                        
                        if pig.take_damage(damage):
                            self.score_earned += SCORE_VALUES["pig_fall_damage"]
                            self.collision_events.append(("pig_fell", pig.body.position))
                    break
            
            return True
        
        def block_ground_collision(arbiter, space, data):
            """Blocks can shatter from high falls"""
            block_shape, ground_shape = arbiter.shapes
            
            for block in self.blocks:
                if block.shape == block_shape:
                    fall_speed = abs(block.body.velocity.y)
                    material_props = MATERIAL_PROPERTIES.get(block.material, MATERIAL_PROPERTIES["wood"])
                    
                    # Different materials have different fall damage thresholds
                    thresholds = {
                        "ice": 200,    # Ice shatters easily
                        "wood": 400,   # Wood can splinter
                        "stone": 600,  # Stone is durable
                        "metal": 800   # Metal is very durable
                    }
                    
                    threshold = thresholds.get(block.material, 400)
                    
                    if fall_speed > threshold:
                        # Damage increases with speed and decreases with resistance
                        damage = ((fall_speed - threshold) / 10) / material_props["damage_resistance"]
                        
                        # Ice completely shatters on hard impact
                        if block.material == "ice":
                            damage *= 5
                            
                            if block.take_damage(damage):
                                self.score_earned += SCORE_VALUES["block_shattered"]
                                self.collision_events.append(("block_shattered", block.body.position))
                                # Ice explosion effect
                                self.trigger_chain_reaction(
                                    (block.body.position.x, block.body.position.y),
                                    fall_speed * 0.2,
                                    radius=100
                                )
                        else:
                            if block.take_damage(damage):
                                self.score_earned += SCORE_VALUES["block_destroyed"] // 2
                                self.collision_events.append(("block_shattered", block.body.position))
                    break
            
            return True
        
        # Register all collision handlers
        try:
            # Bird-Pig
            handler = self.space.add_collision_handler(COLLISION_TYPE_BIRD, COLLISION_TYPE_PIG)
            handler.post_solve = bird_pig_collision
            
            # Bird-Block
            handler = self.space.add_collision_handler(COLLISION_TYPE_BIRD, COLLISION_TYPE_BLOCK)
            handler.post_solve = bird_block_collision
            
            # Block-Pig
            handler = self.space.add_collision_handler(COLLISION_TYPE_BLOCK, COLLISION_TYPE_PIG)
            handler.post_solve = block_pig_collision
            
            # Block-Block
            handler = self.space.add_collision_handler(COLLISION_TYPE_BLOCK, COLLISION_TYPE_BLOCK)
            handler.post_solve = block_block_collision
            
            # Pig-Ground
            handler = self.space.add_collision_handler(COLLISION_TYPE_PIG, COLLISION_TYPE_GROUND)
            handler.post_solve = pig_ground_collision
            
            # Block-Ground
            handler = self.space.add_collision_handler(COLLISION_TYPE_BLOCK, COLLISION_TYPE_GROUND)
            handler.post_solve = block_ground_collision
            
        except AttributeError:
            print("Warning: Collision handlers not supported, using fallback")
            # Fallback handled in simple_physics.py
    
    def add_bird(self, bird):
        """Register a bird for physics tracking"""
        if bird not in self.birds:
            self.birds.append(bird)
    
    def remove_bird(self, bird):
        """Remove a bird from physics tracking"""
        if bird in self.birds:
            self.birds.remove(bird)
    
    def step(self, dt):
        """Advance physics simulation with enhanced features"""
        # Clear events from last frame
        self.collision_events = []
        
        # Update combo timer
        if self.combo_timer > 0:
            self.combo_timer -= 1
            if self.combo_timer == 0:
                self.combo_multiplier = 1.0
        
        # Store velocities for next frame
        for block in self.blocks:
            if not block.destroyed and hasattr(block, 'body'):
                self.previous_velocities[id(block)] = block.body.velocity
        
        # Step physics
        self.space.step(dt)
        
        # Check for unstable structures
        self._check_structural_integrity()
    
    def _check_structural_integrity(self):
        """Check for unstable structures that should collapse"""
        for block in self.blocks:
            if block.destroyed or not hasattr(block, 'body'):
                continue
            
            # Check if block is tilting too much
            angle = abs(block.body.angle)
            if angle > math.pi / 4:  # More than 45 degrees
                # Tilted blocks are unstable
                material_props = MATERIAL_PROPERTIES.get(block.material, MATERIAL_PROPERTIES["wood"])
                if angle > math.pi / 3:  # More than 60 degrees
                    block.take_damage(10 / material_props["damage_resistance"])
    
    def get_and_reset_score(self):
        """Get earned score with combo multiplier and reset"""
        final_score = int(self.score_earned * self.combo_multiplier)
        self.score_earned = 0
        return final_score
    
    def get_collision_events(self):
        """Get collision events for visual effects"""
        events = self.collision_events[:]
        self.collision_events = []
        return events
    
    def get_combo_info(self):
        """Get current combo multiplier for UI display"""
        if self.combo_timer > 0:
            return self.combo_multiplier
        return 1.0
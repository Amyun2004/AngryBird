"""
physics_engine.py - Enhanced physics engine with better collision and damage system
Fixed sleeping bodies issue
"""

import pymunk
import pymunk.pygame_util
import math

# Physics constants - Logic Point 5
GRAVITY = 981  # pixels/s^2
ELASTICITY_GROUND = 0.6
FRICTION_GROUND = 1.0
ELASTICITY_WALL = 0.6
AIR_DRAG = 0.99  # Logic Point 5: Optional air drag

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

# Damage multipliers - Logic Point 5
DAMAGE_MULTIPLIERS = {
    "red": 1.0,
    "yellow": 1.5,  # Yellow birds do more damage
    "blue": 0.7,    # Blue birds do less damage individually
}

# Material damage resistance - Logic Point 6
MATERIAL_DAMAGE_RESISTANCE = {
    "ice": 0.3,     # Ice takes 3x damage
    "wood": 1.0,    # Normal damage
    "stone": 2.0,   # Stone takes half damage
    "metal": 3.0,   # Metal takes 1/3 damage
}


class PhysicsEngine:
    """Manages the Pymunk physics space with enhanced collision handling"""
    
    def __init__(self, width, height, ground_height):
        self.space = pymunk.Space()
        self.space.gravity = (0, GRAVITY)
        self.width = width
        self.height = height
        self.ground_height = ground_height
        
        # IMPORTANT: Disable automatic sleeping to prevent the error
        # We'll handle performance optimization differently
        self.space.sleep_time_threshold = float('inf')  # Disable automatic sleeping
        
        # Score tracking for collision callbacks
        self.score_earned = 0
        
        # Tracking for chain reactions - Logic Point 7
        self.collision_events = []
        self.damage_accumulator = {}  # Track damage per frame
        self.last_damage_time = {}    # Prevent micro-collision spam
        
        # Setup boundaries
        self._create_boundaries()
        
        # Collision handling flags
        self.manual_collisions = False
        self.pigs = []
        self.blocks = []
        self.birds = []
        
    def _create_boundaries(self):
        """Create ground and walls with proper physics properties"""
        # Create static body for boundaries
        ground_body = pymunk.Body(body_type=pymunk.Body.STATIC)
        
        # Ground - Logic Point 5
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
        
        # Walls with proper elasticity
        left_wall = pymunk.Segment(ground_body, (0, 0), (0, self.height), 5)
        right_wall = pymunk.Segment(ground_body, (self.width, 0), (self.width, self.height), 5)
        left_wall.elasticity = ELASTICITY_WALL
        right_wall.elasticity = ELASTICITY_WALL
        left_wall.friction = 0.5
        right_wall.friction = 0.5
        
        self.space.add(ground_body, ground_shape, left_wall, right_wall)
        
    def setup_collision_handlers(self, pigs, blocks, birds=None):
        """Setup enhanced collision handlers between different object types"""
        
        # Store references for collision callbacks
        self.pigs = pigs
        self.blocks = blocks
        self.birds = birds if birds else []
        
        def calculate_impact_damage(arbiter, mass1, mass2, multiplier=1.0):
            """Calculate damage based on impact physics - Logic Point 5"""
            # Get relative velocity and impulse
            if hasattr(arbiter, 'total_impulse'):
                impulse = arbiter.total_impulse.length
            else:
                impulse = 100  # Default if not available
            
            if impulse > 0:
                # Kinetic energy based damage with mass consideration
                relative_mass = (mass1 * mass2) / (mass1 + mass2) if mass2 > 0 else mass1
                base_damage = (impulse / 20) * math.sqrt(relative_mass)
                
                # Apply multiplier and cap
                damage = min(base_damage * multiplier, 100)
                
                # Minimum damage threshold
                if damage < 5:
                    damage = 5
                    
                return damage
            return 10  # Default minimum damage
        
        def should_apply_damage(obj_id, current_time=0):
            """Check if damage should be applied (cooldown for micro-collisions) - Logic Point 15"""
            # Simplified - always allow damage for now to ensure it works
            return True
        
        def bird_pig_collision(arbiter, space, data):
            """Enhanced bird-pig collision with proper damage calculation"""
            bird_shape, pig_shape = arbiter.shapes
            
            # Find the pig object
            pig = None
            for p in self.pigs:
                if p.shape == pig_shape:
                    pig = p
                    break
            
            if not pig or pig.dead:
                return True
            
            # Calculate impact force
            if hasattr(arbiter, 'total_impulse'):
                impulse = arbiter.total_impulse.length
            else:
                impulse = 100  # Default impulse if not available
            
            # Base damage calculation
            damage = max(20, impulse / 10)  # Minimum 20 damage
            
            # Apply pig type modifiers
            if pig.pig_type == "helmet":
                damage *= 0.7
            elif pig.pig_type == "king":
                damage *= 0.8
            
            print(f"Bird-Pig collision! Impulse: {impulse}, Damage: {damage}")
            
            if pig.take_damage(damage):
                self.score_earned += 500  # Pig eliminated
                self.collision_events.append(("pig_eliminated", pig.body.position))
                print(f"PIG ELIMINATED! +500 points")
            else:
                self.score_earned += 10  # Pig hit
                self.collision_events.append(("pig_hit", pig.body.position))
                print(f"Pig hit! +10 points")
            
            return True
        
        def bird_block_collision(arbiter, space, data):
            """Enhanced bird-block collision with material consideration"""
            bird_shape, block_shape = arbiter.shapes
            
            # Find the block object
            block = None
            for bl in self.blocks:
                if bl.shape == block_shape:
                    block = bl
                    break
            
            if not block or block.destroyed:
                return True
            
            # Calculate impact force
            if hasattr(arbiter, 'total_impulse'):
                impulse = arbiter.total_impulse.length
            else:
                impulse = 80  # Default impulse
            
            # Base damage calculation
            damage = max(15, impulse / 15)  # Minimum 15 damage
            
            # Apply material resistance
            material_resistance = MATERIAL_DAMAGE_RESISTANCE.get(block.material, 1.0)
            damage = damage / material_resistance
            
            print(f"Bird-Block collision! Material: {block.material}, Damage: {damage}")
            
            if block.take_damage(damage):
                self.score_earned += 100  # Block destroyed
                self.collision_events.append(("block_destroyed", block.body.position))
                print(f"BLOCK DESTROYED! +100 points")
            else:
                self.score_earned += 5  # Block hit
                self.collision_events.append(("block_hit", block.body.position))
                print(f"Block hit! +5 points")
            
            return True
        
        def block_pig_collision(arbiter, space, data):
            """Falling blocks do extra damage - Logic Point 7"""
            block_shape, pig_shape = arbiter.shapes
            
            # Find the block for mass calculation
            block_mass = 1
            block_velocity = 0
            for block in self.blocks:
                if block.shape == block_shape:
                    block_mass = block.mass
                    block_velocity = abs(block.body.velocity.y)
                    break
            
            # Find the pig object
            for pig in self.pigs:
                if pig.shape == pig_shape:
                    if should_apply_damage(id(pig)):
                        # Falling blocks do more damage based on velocity and mass
                        damage = calculate_impact_damage(arbiter, block_mass, 2, 1.2)
                        
                        # Extra damage if block is falling from height - Logic Point 7
                        if block_velocity > 100:
                            damage *= 1.5 + (block_velocity / 500)  # Scale with fall speed
                        
                        if damage > 0:
                            if pig.take_damage(damage):
                                self.score_earned += 300  # Pig crushed
                                self.collision_events.append(("pig_crushed", pig.body.position))
                    break
            return True
        
        def block_block_collision(arbiter, space, data):
            """Blocks damage each other on impact - Logic Point 6"""
            block1_shape, block2_shape = arbiter.shapes
            
            for block in self.blocks:
                if block.shape in [block1_shape, block2_shape]:
                    # Get the other block's mass for damage calculation
                    other_mass = 1
                    for other_block in self.blocks:
                        if other_block.shape != block.shape and other_block.shape in [block1_shape, block2_shape]:
                            other_mass = other_block.mass
                            break
                    
                    if should_apply_damage(id(block)):
                        # Materials take different damage from collisions - Logic Point 6
                        material_resistance = MATERIAL_DAMAGE_RESISTANCE.get(block.material, 1.0)
                        damage = calculate_impact_damage(arbiter, block.mass, other_mass, 0.5)
                        damage = damage / material_resistance
                        
                        # Ice blocks are extra fragile to impacts - Logic Point 6
                        if block.material == "ice":
                            damage *= 2
                        
                        if damage > 0:
                            if block.take_damage(damage):
                                self.score_earned += 50
                                self.collision_events.append(("block_collapsed", block.body.position))
            return True
        
        def pig_ground_collision(arbiter, space, data):
            """Pigs take fall damage when hitting ground hard - Logic Point 7"""
            pig_shape, ground_shape = arbiter.shapes
            
            for pig in self.pigs:
                if pig.shape == pig_shape:
                    if should_apply_damage(id(pig)):
                        # Check fall velocity
                        fall_speed = abs(pig.body.velocity.y)
                        if fall_speed > 300:  # Falling fast enough to take damage
                            damage = (fall_speed - 300) / 10
                            
                            # Heavier pigs take more fall damage
                            if pig.pig_type == "king":
                                damage *= 1.2
                            
                            if damage > 0:
                                if pig.take_damage(damage):
                                    self.score_earned += 200  # Fall damage elimination
                                    self.collision_events.append(("pig_fell", pig.body.position))
                    break
            return True
        
        def block_ground_collision(arbiter, space, data):
            """Blocks can shatter from falling - Logic Point 6"""
            block_shape, ground_shape = arbiter.shapes
            
            for block in self.blocks:
                if block.shape == block_shape:
                    if should_apply_damage(id(block)):
                        # Check fall velocity
                        fall_speed = abs(block.body.velocity.y)
                        if fall_speed > 400:  # Falling very fast
                            material_resistance = MATERIAL_DAMAGE_RESISTANCE.get(block.material, 1.0)
                            damage = (fall_speed - 400) / (5 * material_resistance)
                            
                            # Ice shatters easily from falls - Logic Point 6
                            if block.material == "ice" and fall_speed > 250:
                                damage *= 3
                            
                            if damage > 0:
                                if block.take_damage(damage):
                                    self.score_earned += 25
                                    self.collision_events.append(("block_shattered", block.body.position))
                    break
            return True
        
        # Register collision handlers
        try:
            # Bird-Pig collisions
            handler = self.space.add_collision_handler(
                COLLISION_TYPE_BIRD, COLLISION_TYPE_PIG
            )
            handler.pre_solve = bird_pig_collision
            
            # Bird-Block collisions
            handler = self.space.add_collision_handler(
                COLLISION_TYPE_BIRD, COLLISION_TYPE_BLOCK
            )
            handler.pre_solve = bird_block_collision
            
            # Block-Pig collisions
            handler = self.space.add_collision_handler(
                COLLISION_TYPE_BLOCK, COLLISION_TYPE_PIG
            )
            handler.pre_solve = block_pig_collision
            
            # Block-Block collisions
            handler = self.space.add_collision_handler(
                COLLISION_TYPE_BLOCK, COLLISION_TYPE_BLOCK
            )
            handler.pre_solve = block_block_collision
            
            # Pig-Ground collisions (fall damage)
            handler = self.space.add_collision_handler(
                COLLISION_TYPE_PIG, COLLISION_TYPE_GROUND
            )
            handler.pre_solve = pig_ground_collision
            
            # Block-Ground collisions (shatter on impact)
            handler = self.space.add_collision_handler(
                COLLISION_TYPE_BLOCK, COLLISION_TYPE_GROUND
            )
            handler.pre_solve = block_ground_collision
            
            print("Collision handlers registered successfully!")
            
        except AttributeError as e:
            # Fallback for older pymunk versions
            print(f"Warning: Could not register collision handlers: {e}")
            print("Using fallback collision detection")
            self.manual_collisions = True
    
    def add_bird(self, bird):
        """Register a bird for tracking"""
        if bird not in self.birds:
            self.birds.append(bird)
    
    def remove_bird(self, bird):
        """Remove a bird from tracking"""
        if bird in self.birds:
            self.birds.remove(bird)
    
    def step(self, dt):
        """Advance physics simulation with proper timestep"""
        # Clear collision events from last frame
        self.collision_events = []
        
        # Apply air drag to flying birds
        for bird in self.birds[:]:  # Use slice to avoid modification issues
            if hasattr(bird, 'body') and bird.launched:
                try:
                    bird.body.velocity = (
                        bird.body.velocity.x * AIR_DRAG,
                        bird.body.velocity.y * AIR_DRAG
                    )
                except:
                    pass
        
        # Step physics with error handling
        try:
            self.space.step(dt)
        except Exception as e:
            print(f"Physics step error: {e}")
            return
        
        # Manual collision detection as backup (disabled by default)
        if self.manual_collisions:
            self._check_manual_collisions()
        
        # Manual velocity damping for performance
        self._apply_velocity_damping()
    
    def _check_manual_collisions(self):
        """Manual collision detection between birds, pigs, and blocks"""
        # Limit iterations to prevent infinite loops
        max_checks = 100
        checks = 0
        
        # Check bird-pig collisions
        for bird in self.birds[:]:  # Use slice to avoid modification issues
            if checks > max_checks:
                break
            checks += 1
            
            if not hasattr(bird, 'body'):
                continue
                
            try:
                bird_pos = bird.body.position
                bird_vel = bird.body.velocity.length
            except:
                continue
            
            # Only check if bird is moving fast enough
            if bird_vel < 50:
                continue
            
            for pig in self.pigs[:]:  # Use slice
                if pig.dead:
                    continue
                    
                try:
                    pig_pos = pig.body.position
                    distance = math.sqrt((bird_pos.x - pig_pos.x)**2 + (bird_pos.y - pig_pos.y)**2)
                except:
                    continue
                
                # Check if colliding
                if distance < (bird.radius + pig.radius):
                    # Calculate damage based on velocity
                    damage = min(100, bird_vel / 5)
                    
                    # Apply pig type modifiers
                    if pig.pig_type == "helmet":
                        damage *= 0.7
                    elif pig.pig_type == "king":
                        damage *= 0.8
                    
                    if damage > 10:  # Minimum damage threshold
                        print(f"MANUAL HIT: Bird hit pig for {damage:.1f} damage!")
                        
                        if pig.take_damage(damage):
                            self.score_earned += 500
                            self.collision_events.append(("pig_eliminated", pig_pos))
                        else:
                            self.score_earned += 10
                            self.collision_events.append(("pig_hit", pig_pos))
                        
                        # Reduce bird velocity after hit
                        bird.body.velocity = (bird.body.velocity.x * 0.5, bird.body.velocity.y * 0.5)
                        break  # Only one collision per frame
            
            # Check bird-block collisions
            for block in self.blocks[:]:  # Use slice
                if block.destroyed:
                    continue
                
                try:
                    block_pos = block.body.position
                    
                    # Simple distance check to block center
                    dx = abs(bird_pos.x - block_pos.x)
                    dy = abs(bird_pos.y - block_pos.y)
                except:
                    continue
                
                # Check if within block bounds
                if dx < (block.width/2 + bird.radius) and dy < (block.height/2 + bird.radius):
                    # Calculate damage
                    damage = min(80, bird_vel / 8)
                    
                    # Apply material resistance
                    material_resistance = MATERIAL_DAMAGE_RESISTANCE.get(block.material, 1.0)
                    damage = damage / material_resistance
                    
                    if damage > 5:  # Minimum damage threshold
                        print(f"MANUAL HIT: Bird hit {block.material} block for {damage:.1f} damage!")
                        
                        if block.take_damage(damage):
                            self.score_earned += 100
                            self.collision_events.append(("block_destroyed", block_pos))
                        else:
                            self.score_earned += 5
                            self.collision_events.append(("block_hit", block_pos))
                        
                        # Reduce bird velocity after hit
                        bird.body.velocity = (bird.body.velocity.x * 0.7, bird.body.velocity.y * 0.7)
                        break  # Only one collision per frame
        
    def _apply_velocity_damping(self):
        """Apply velocity damping to slow objects for performance"""
        VELOCITY_THRESHOLD = 5  # Units per second
        DAMPING_FACTOR = 0.95
        
        for body in self.space.bodies:
            if body.body_type == pymunk.Body.DYNAMIC:
                velocity = body.velocity.length
                
                # Apply damping to very slow objects
                if velocity < VELOCITY_THRESHOLD and velocity > 0:
                    body.velocity = (
                        body.velocity.x * DAMPING_FACTOR,
                        body.velocity.y * DAMPING_FACTOR
                    )
                    
                    # Also damp angular velocity
                    if hasattr(body, 'angular_velocity'):
                        body.angular_velocity *= DAMPING_FACTOR
    
    def get_and_reset_score(self):
        """Get earned score and reset counter"""
        score = self.score_earned
        self.score_earned = 0
        return score
    
    def get_collision_events(self):
        """Get collision events for visual effects"""
        events = self.collision_events[:]
        self.collision_events = []
        return events
        
    def remove_body(self, body, shape):
        """Safely remove a body and shape from the space"""
        try:
            self.space.remove(body, shape)
            # Clean up tracking
            body_id = id(body)
            if body_id in self.last_damage_time:
                del self.last_damage_time[body_id]
        except:
            pass
"""
main.py - Main game file for Angry Birds with Pymunk physics
Fixed level loading and bird selection issues
"""

import pygame
import sys
from enum import Enum
import math

# Import game modules
from constants import *
try:
    from physics_engine import PhysicsEngine
except Exception as e:
    print(f"Warning: Standard physics engine failed: {e}")
    print("Using simplified physics engine instead")
    from simple_physics import SimplePhysicsEngine as PhysicsEngine
from entities import Bird, Pig, Block
from slingshot import Slingshot
from levels import LevelBuilder
from ui import UI
from effects import EffectsManager


class GameState(Enum):
    """Game state enumeration"""
    MENU = 1
    PLAYING = 2
    PAUSED = 3
    LEVEL_INTRO = 4
    GAME_OVER = 5
    INSTRUCTIONS = 6
    LEVEL_SELECT = 7


class BirdState(Enum):
    """Bird lifecycle states - Logic Point 4"""
    IDLE = 1
    AIMING = 2
    IN_FLIGHT = 3
    COLLIDING = 4
    SPENT = 5


class AngryBirdsGame:
    """Main game class with enhanced game logic"""
    
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT))
        pygame.display.set_caption("Angry Birds - Pymunk Physics Edition")
        self.clock = pygame.time.Clock()
        
        # Game components
        self.ui = UI(self.screen)
        self.physics = None
        self.slingshot = Slingshot()
        self.effects = EffectsManager()
        
        # Game state
        self.state = GameState.MENU
        self.running = True
        self.current_level = 1
        self.score = 0
        self.total_score = 0
        self.combo_timer = 0  # Logic Point 8: Combo system
        self.combo_multiplier = 1
        
        # Level objects
        self.blocks = []
        self.pigs = []
        self.birds = []
        self.current_bird = None
        self.launched_birds = []
        
        # Input state - Logic Point 3: Enhanced drag handling
        self.dragging = False
        self.mouse_pressed = False
        self.drag_start_pos = None
        self.bird_state = BirdState.IDLE
        
        # Bird loading control
        self.reload_timer = 0
        self.reload_delay = 30  # frames to wait before loading next bird
        
        # Camera system - Logic Point 10
        self.camera_x = 0
        self.camera_y = 0
        self.camera_target_x = 0
        self.camera_target_y = 0
        self.camera_lerp_speed = 0.1
        self.auto_pan_timer = 0
        
        # Physics settling - Logic Point 6
        self.pre_settle_frames = 60  # Let structures settle on level start
        self.settling_counter = 0
        
        # Performance tracking - Logic Point 11
        self.frame_accumulator = 0
        self.physics_dt = 1/60.0
        
    def reset_level(self, level_num=None):
        """Reset the current level with improved structure settling"""
        if level_num:
            self.current_level = level_num
            
        # Reset score and combo
        self.score = 0
        self.combo_timer = 0
        self.combo_multiplier = 1
        
        # Create new physics space
        self.physics = PhysicsEngine(WIN_WIDTH, WIN_HEIGHT, GROUND_HEIGHT)
        
        # Clear existing objects
        self.blocks = []
        self.pigs = []
        self.birds = []
        self.launched_birds = []
        self.current_bird = None
        self.reload_timer = 0
        self.bird_state = BirdState.IDLE
        
        # Create the actual level (not debug level)
        self.blocks, self.pigs = LevelBuilder.create_level(
            self.physics.space, self.current_level
        )
        
        # Setup collision handlers
        self.physics.setup_collision_handlers(self.pigs, self.blocks, self.birds)
        
        # Create birds based on level (only once!)
        bird_types = LevelBuilder.get_bird_lineup(self.current_level)
        for i, bird_type in enumerate(bird_types):
            if bird_type == "yellow":
                color = YELLOW
                radius = 14
                mass = 6
            elif bird_type == "blue":
                color = BLUE
                radius = 8
                mass = 3
            else:  # red
                color = RED
                radius = 12
                mass = 5
                
            bird = Bird(self.physics.space, 50 + i * 30, WIN_HEIGHT - 80, 
                    radius=radius, mass=mass, color=color, bird_type=bird_type)
            self.birds.append(bird)
        
        # Pre-settle the structure - Logic Point 6
        self.settling_counter = self.pre_settle_frames
        for _ in range(30):  # Quick pre-settle
            self.physics.step(self.physics_dt)
        
        # Load first bird
        if self.birds:
            self.current_bird = self.birds.pop(0)
            self.slingshot.load_bird(self.current_bird)
            self.bird_state = BirdState.IDLE
        
        # Reset camera
        self.camera_x = 0
        self.camera_y = 0
        self.camera_target_x = 0
        self.camera_target_y = 0
    
    def handle_events(self):
        """Handle pygame events with improved input logic"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if self.state == GameState.PLAYING:
                        self.state = GameState.MENU
                    elif self.state in [GameState.INSTRUCTIONS, GameState.LEVEL_SELECT]:
                        self.state = GameState.MENU
                    else:
                        self.running = False
                        
                elif event.key == pygame.K_SPACE:
                    if self.state == GameState.GAME_OVER:
                        if self.check_victory():
                            # Next level
                            self.current_level += 1
                            if self.current_level > 4:
                                self.current_level = 1
                            self.state = GameState.LEVEL_INTRO
                        else:
                            # Retry level
                            self.reset_level()
                            self.state = GameState.PLAYING
                    elif self.state == GameState.INSTRUCTIONS:
                        self.state = GameState.MENU
                        
                elif event.key == pygame.K_p and self.state == GameState.PLAYING:
                    self.state = GameState.PAUSED
                    
                elif event.key == pygame.K_p and self.state == GameState.PAUSED:
                    self.state = GameState.PLAYING
                    
                # Menu navigation
                elif self.state == GameState.MENU:
                    if event.key == pygame.K_1:
                        self.current_level = 1
                        self.total_score = 0
                        self.state = GameState.LEVEL_INTRO
                    elif event.key == pygame.K_2:
                        self.state = GameState.LEVEL_SELECT
                    elif event.key == pygame.K_3:
                        self.state = GameState.INSTRUCTIONS
                        
                # Level selection
                elif self.state == GameState.LEVEL_SELECT:
                    if pygame.K_1 <= event.key <= pygame.K_4:
                        self.current_level = event.key - pygame.K_0
                        self.state = GameState.LEVEL_INTRO
                        
            elif event.type == pygame.MOUSEBUTTONDOWN:
                self.mouse_pressed = True
                
                if self.state == GameState.PLAYING:
                    if self.current_bird and self.bird_state == BirdState.IDLE:
                        # Check if clicking near slingshot area (made more generous)
                        mouse_pos = pygame.mouse.get_pos()
                        
                        # Check if clicking near the slingshot area (not just the bird)
                        # The slingshot is at SLINGSHOT_X (150) and fork_y (550)
                        slingshot_x = SLINGSHOT_X
                        slingshot_y = WIN_HEIGHT - 150  # fork_y position
                        
                        # More generous click area around slingshot
                        distance_to_slingshot = math.hypot(
                            mouse_pos[0] - slingshot_x, 
                            mouse_pos[1] - slingshot_y
                        )
                        
                        # Also check distance to bird if it exists
                        if hasattr(self.current_bird, 'body'):
                            bird_x, bird_y = self.current_bird.body.position.x, self.current_bird.body.position.y
                            distance_to_bird = math.hypot(
                                mouse_pos[0] - bird_x, 
                                mouse_pos[1] - bird_y
                            )
                        else:
                            distance_to_bird = float('inf')
                        
                        # Allow dragging if clicking near slingshot OR bird
                        if distance_to_slingshot < 100 or distance_to_bird < 50:
                            self.dragging = True
                            self.drag_start_pos = mouse_pos
                            self.bird_state = BirdState.AIMING
                            print(f"Started dragging from {mouse_pos}")  # Debug
                            
                elif self.state == GameState.LEVEL_INTRO:
                    self.reset_level()
                    self.state = GameState.PLAYING
                    
            elif event.type == pygame.MOUSEBUTTONUP:
                self.mouse_pressed = False
                
                if self.state == GameState.PLAYING:
                    if self.dragging and self.current_bird and self.bird_state == BirdState.AIMING:
                        # Release the bird - Logic Point 4
                        print("Releasing bird!")  # Debug
                        self.slingshot.release()
                        self.launched_birds.append(self.current_bird)
                        self.bird_state = BirdState.IN_FLIGHT
                        
                        # CRITICAL: Add bird to physics tracking so collisions work
                        self.physics.add_bird(self.current_bird)
                        print(f"Added bird to physics. Total tracked birds: {len(self.physics.birds)}")
                        
                        # Clear current bird and set reload timer
                        self.current_bird = None
                        self.dragging = False
                        self.reload_timer = self.reload_delay
                        
                        # Don't follow bird with camera - keep view static
                        # self.auto_pan_timer = 180  # Disabled camera following
                            
    def update(self, dt):
        """Update game logic with enhanced physics and scoring"""
        if self.state != GameState.PLAYING:
            return
        
        # Continue settling if needed - Logic Point 6
        if self.settling_counter > 0:
            self.settling_counter -= 1
            self.physics.step(self.physics_dt)
            return
            
        # Fixed timestep physics with accumulator - Logic Point 11
        self.frame_accumulator += dt
        physics_steps = 0
        max_steps = 3  # Prevent spiral of death
        
        while self.frame_accumulator >= self.physics_dt and physics_steps < max_steps:
            # Update physics
            self.physics.step(self.physics_dt)
            self.frame_accumulator -= self.physics_dt
            physics_steps += 1
        
        # Add score from collisions with combo system - Logic Point 8
        score_gained = self.physics.get_and_reset_score()
        if score_gained > 0:
            # Apply combo multiplier
            actual_score = int(score_gained * self.combo_multiplier)
            self.score += actual_score
            
            # Increase combo if scoring rapidly
            if self.combo_timer > 0:
                self.combo_multiplier = min(self.combo_multiplier + 0.5, 3.0)
            else:
                self.combo_multiplier = 1.0
            
            self.combo_timer = 60  # 1 second combo window
        
        # Update combo timer
        if self.combo_timer > 0:
            self.combo_timer -= 1
            if self.combo_timer == 0:
                self.combo_multiplier = 1.0
        
        # Process collision events for effects
        if hasattr(self.physics, 'get_collision_events'):
            events = self.physics.get_collision_events()
            for event_type, position in events:
                x, y = position.x, position.y
                
                if event_type == "pig_eliminated":
                    self.effects.create_pig_hit_effect(x, y, eliminated=True)
                    self.effects.add_damage_number(x, y, int(500 * self.combo_multiplier), GOLD)
                elif event_type == "pig_hit":
                    self.effects.create_pig_hit_effect(x, y, eliminated=False)
                    self.effects.add_damage_number(x, y, int(10 * self.combo_multiplier), YELLOW)
                elif event_type == "pig_crushed":
                    self.effects.create_pig_hit_effect(x, y, eliminated=True)
                    self.effects.add_damage_number(x, y, int(300 * self.combo_multiplier), ORANGE)
                elif event_type == "block_destroyed":
                    # Find block material for effect
                    material = "wood"
                    for block in self.blocks:
                        if block.destroyed and abs(block.body.position.x - x) < 5:
                            material = block.material
                            break
                    self.effects.create_destruction_effect(x, y, material)
                    self.effects.add_damage_number(x, y, int(100 * self.combo_multiplier), GREEN)
                elif event_type == "block_hit":
                    self.effects.create_impact_effect(x, y, "normal")
                elif event_type == "block_collapsed":
                    self.effects.create_impact_effect(x, y, "strong")
                    self.effects.add_damage_number(x, y, int(50 * self.combo_multiplier), YELLOW)
                elif event_type == "block_shattered":
                    self.effects.create_impact_effect(x, y, "destroy")
                    self.effects.add_damage_number(x, y, int(25 * self.combo_multiplier), LIGHTBLUE)
        
        # Update effects
        self.effects.update(dt)
        
        # Update slingshot dragging with improved handling - Logic Point 3
        if self.dragging and self.current_bird and self.bird_state == BirdState.AIMING:
            mouse_pos = pygame.mouse.get_pos()
            self.slingshot.pull(mouse_pos)
        
        # Update camera - Logic Point 10
        self.update_camera()
        
        # Update reload timer
        if self.reload_timer > 0:
            self.reload_timer -= 1
        
        # Check for stopped birds and remove them - Logic Point 4
        for bird in self.launched_birds[:]:
            if bird.is_stopped():
                # Add bonus for leftover bird momentum
                if hasattr(bird.body, 'velocity'):
                    remaining_energy = bird.body.velocity.length
                    if remaining_energy > 10:
                        bonus = int(remaining_energy)
                        self.score += bonus
                        self.effects.add_damage_number(
                            bird.body.position.x, 
                            bird.body.position.y - 20, 
                            bonus, 
                            BLUE
                        )
                
                # Remove bird from physics tracking
                if hasattr(self.physics, 'remove_bird'):
                    self.physics.remove_bird(bird)
                bird.remove()
                self.launched_birds.remove(bird)
        
        # Load next bird if conditions are met - Logic Point 2
        if (not self.current_bird and 
            self.birds and 
            self.reload_timer == 0 and
            not self.dragging and
            not self.mouse_pressed):
            
            # Check if it's safe to load (no bird actively moving near slingshot)
            safe_to_load = True
            for bird in self.launched_birds:
                if hasattr(bird, 'body'):
                    # Check if bird is still moving significantly
                    vel = bird.body.velocity.length
                    if vel > 50:  # Bird is still moving fast
                        bx, by = bird.body.position.x, bird.body.position.y
                        # Only block if the moving bird is near the slingshot
                        if bx < 300:  # Near the left side where slingshot is
                            safe_to_load = False
                            break
            
            if safe_to_load:
                self.current_bird = self.birds.pop(0)
                self.slingshot.load_bird(self.current_bird)
                self.bird_state = BirdState.IDLE
                # Pan camera back to slingshot
                self.camera_target_x = 0
                self.camera_target_y = 0
        
        # Check victory/defeat conditions - Logic Point 2
        if self.check_victory():
            # Add bonus for remaining birds - Logic Point 8
            bird_bonus = len(self.birds) * 1000
            if self.current_bird:
                bird_bonus += 1000
            self.score += bird_bonus
            
            self.total_score += self.score
            self.state = GameState.GAME_OVER
        elif self.check_defeat():
            self.state = GameState.GAME_OVER
    
    def update_camera(self):
        """Update camera position - DISABLED for single-screen gameplay"""
        # Camera is disabled - everything stays on one screen
        self.camera_x = 0
        self.camera_y = 0
        self.camera_target_x = 0
        self.camera_target_y = 0
    
    def check_victory(self):
        """Check if all pigs are defeated"""
        return all(pig.dead for pig in self.pigs)
    
    def check_defeat(self):
        """Check if no birds left and pigs remain"""
        no_birds = not self.current_bird and not self.birds and not self.launched_birds
        pigs_remain = any(not pig.dead for pig in self.pigs)
        return no_birds and pigs_remain
    
    def draw(self):
        """Draw everything with camera offset"""
        # Clear screen
        self.screen.fill(WHITE)
        
        # Draw based on game state
        if self.state == GameState.MENU:
            self.ui.draw_menu()
            
        elif self.state == GameState.INSTRUCTIONS:
            self.ui.draw_instructions()
            
        elif self.state == GameState.LEVEL_SELECT:
            self.draw_level_select()
            
        elif self.state == GameState.LEVEL_INTRO:
            level_name = LEVEL_CONFIGS.get(self.current_level, {}).get("name", "Custom Level")
            self.ui.draw_level_intro(self.current_level, level_name)
            
        elif self.state in [GameState.PLAYING, GameState.PAUSED]:
            # Apply screen shake if active
            offset_x, offset_y = self.effects.get_screen_offset()
            
            # Add camera offset - Logic Point 10
            offset_x -= int(self.camera_x)
            offset_y -= int(self.camera_y)
            
            if offset_x != 0 or offset_y != 0:
                # Create a temporary surface for transformations
                temp_surface = pygame.Surface((WIN_WIDTH + abs(offset_x) * 2, WIN_HEIGHT + abs(offset_y) * 2))
                temp_surface.fill(WHITE)
                
                # Adjust drawing positions for camera
                draw_offset = (abs(offset_x), abs(offset_y))
                
                # Draw everything to temp surface with offset
                self.ui.draw_background_to_surface(temp_surface)
                
                # Draw with camera offset
                self.draw_game_world(temp_surface, draw_offset)
                
                # Blit transformed surface to screen
                self.screen.blit(temp_surface, (offset_x, offset_y))
            else:
                # Normal drawing without shake/camera
                self.ui.draw_background()
                self.draw_game_world(self.screen, (0, 0))
            
            # Draw HUD (always on top, no shake/camera) - Logic Point 2
            birds_left = len(self.birds) + (1 if self.current_bird else 0)
            pigs_left = sum(1 for pig in self.pigs if not pig.dead)
            
            # Show combo multiplier if active - Logic Point 8
            display_score = self.score + self.total_score
            if self.combo_multiplier > 1:
                combo_text = f" x{self.combo_multiplier:.1f}"
            else:
                combo_text = ""
            
            self.ui.draw_hud(display_score, birds_left, 
                           pigs_left, self.current_level, combo_text)
            
            # Draw pause overlay
            if self.state == GameState.PAUSED:
                self.draw_pause_overlay()
                
        elif self.state == GameState.GAME_OVER:
            # Draw game world in background
            self.ui.draw_background()
            
            # Draw game over screen with star rating - Logic Point 8
            self.ui.draw_game_over(self.check_victory(), 
                                  self.score + self.total_score, 
                                  self.current_level)
        
        # Update display
        pygame.display.flip()
    
    def draw_game_world(self, surface, offset):
        """Draw all game objects with offset"""
        ox, oy = offset
        
        # Draw slingshot
        self.slingshot.draw(surface)
        
        # Draw blocks
        for block in self.blocks:
            block.draw(surface)
        
        # Draw pigs
        for pig in self.pigs:
            pig.draw(surface)
        
        # Draw birds
        for bird in self.launched_birds:
            bird.draw(surface)

        if self.current_bird:
            self.current_bird.draw(surface)
        for bird in self.birds:
            bird.draw(surface)
        
        # Draw ground line
        pygame.draw.line(surface, BLACK, 
                       (ox, WIN_HEIGHT - GROUND_HEIGHT + oy), 
                       (WIN_WIDTH + ox, WIN_HEIGHT - GROUND_HEIGHT + oy), 3)
        
        # Draw effects
        self.effects.draw(surface)

    def draw_level_select(self):
        """Draw level selection screen"""
        self.ui.draw_background()
        
        # Title
        title = self.ui.font_xlarge.render("SELECT LEVEL", True, WHITE)
        title_rect = title.get_rect(center=(WIN_WIDTH // 2, 100))
        self.screen.blit(title, title_rect)
        
        # Level buttons
        levels = [
            (1, "Getting Started", (400, 250)),
            (2, "Ice Palace", (800, 250)),
            (3, "Stone Stronghold", (400, 400)),
            (4, "Complex Castle", (800, 400))
        ]
        
        for level_num, level_name, pos in levels:
            # Button background
            button_rect = pygame.Rect(pos[0] - 120, pos[1] - 40, 240, 80)
            pygame.draw.rect(self.screen, (50, 50, 50), button_rect)
            pygame.draw.rect(self.screen, YELLOW, button_rect, 3)
            
            # Level number
            num_text = self.ui.font_large.render(f"{level_num}", True, YELLOW)
            num_rect = num_text.get_rect(center=(pos[0], pos[1] - 10))
            self.screen.blit(num_text, num_rect)
            
            # Level name
            name_text = self.ui.font_small.render(level_name, True, WHITE)
            name_rect = name_text.get_rect(center=(pos[0], pos[1] + 20))
            self.screen.blit(name_text, name_rect)
        
        # Instructions
        inst_text = self.ui.font_medium.render("Press 1-4 to select level, ESC to return", True, WHITE)
        inst_rect = inst_text.get_rect(center=(WIN_WIDTH // 2, WIN_HEIGHT - 50))
        self.screen.blit(inst_text, inst_rect)
    
    def draw_pause_overlay(self):
        """Draw pause overlay"""
        # Semi-transparent overlay
        overlay = pygame.Surface((WIN_WIDTH, WIN_HEIGHT))
        overlay.set_alpha(128)
        overlay.fill(BLACK)
        self.screen.blit(overlay, (0, 0))
        
        # Pause text
        pause_text = self.ui.font_xlarge.render("PAUSED", True, WHITE)
        pause_rect = pause_text.get_rect(center=(WIN_WIDTH // 2, WIN_HEIGHT // 2))
        self.screen.blit(pause_text, pause_rect)
        
        # Instructions
        inst_text = self.ui.font_medium.render("Press P to Resume", True, YELLOW)
        inst_rect = inst_text.get_rect(center=(WIN_WIDTH // 2, WIN_HEIGHT // 2 + 60))
        self.screen.blit(inst_text, inst_rect)
    
    def run(self):
        """Main game loop with fixed timestep - Logic Point 11"""
        try:
            while self.running:
                dt = self.clock.tick(FPS) / 1000.0
                
                self.handle_events()
                self.update(dt)
                self.draw()

        except Exception as e:
            print("--- A CRASH OCCURRED ---")
            import traceback
            traceback.print_exc()
            # Add a pause so you can read the error
            input("Press Enter to close...") 
            pygame.quit()
            sys.exit()

        pygame.quit()
        sys.exit()


def main():
    """Entry point"""
    game = AngryBirdsGame()
    game.run()


if __name__ == "__main__":
    main()
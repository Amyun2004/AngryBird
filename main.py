"""
main.py - Main game file for Angry Birds with Pymunk physics
"""

import pygame
import sys
from enum import Enum

# Import game modules
from constants import *
try:
    from physics_engine import EnhancedPhysicsEngine as PhysicsEngine
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


class AngryBirdsGame:
    """Main game class"""
    
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
        
        # Level objects
        self.blocks = []
        self.pigs = []
        self.birds = []
        self.current_bird = None
        self.launched_birds = []
        
        # Input state
        self.dragging = False
        self.mouse_pressed = False
        
        # Bird loading control
        self.reload_timer = 0
        self.reload_delay = 30  # frames to wait before loading next bird (0.5 seconds at 60 FPS)
        
    def reset_level(self, level_num=None):
        """Reset the current level"""
        if level_num:
            self.current_level = level_num
            
        # Reset score for this level
        self.score = 0
        
        # Create new physics space
        self.physics = PhysicsEngine(WIN_WIDTH, WIN_HEIGHT, GROUND_HEIGHT)
        
        # Clear existing objects
        self.blocks = []
        self.pigs = []
        self.birds = []
        self.launched_birds = []
        self.current_bird = None
        self.reload_timer = 0
        
        # Create level
        self.blocks, self.pigs = LevelBuilder.create_level(
            self.physics.space, self.current_level
        )
        
        # Setup collision handlers
        self.physics.setup_collision_handlers(self.pigs, self.blocks)
        
        # Create birds based on level
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
        
        # Load first bird
        if self.birds:
            self.current_bird = self.birds.pop(0)
            self.slingshot.load_bird(self.current_bird)
    
    def handle_events(self):
        """Handle pygame events"""
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
                    if self.current_bird and not self.current_bird.launched:
                        self.dragging = True
                elif self.state == GameState.LEVEL_INTRO:
                    self.reset_level()
                    self.state = GameState.PLAYING
                    
            elif event.type == pygame.MOUSEBUTTONUP:
                self.mouse_pressed = False
                
                if self.state == GameState.PLAYING:
                    if self.dragging and self.current_bird and not self.current_bird.launched:
                        # Release the bird
                        self.slingshot.release()
                        self.launched_birds.append(self.current_bird)
                        
                        # Add bird to physics tracking
                        if hasattr(self.physics, 'add_bird'):
                            self.physics.add_bird(self.current_bird)
                        else:
                            self.physics.birds.append(self.current_bird)
                        
                        # Clear current bird and set reload timer
                        self.current_bird = None
                        self.dragging = False
                        self.reload_timer = self.reload_delay
                            
    def update(self, dt):
        """Update game logic"""
        if self.state != GameState.PLAYING:
            return
            
        # Update physics
        self.physics.step(dt)
        
        # Add score from collisions
        score_gained = self.physics.get_and_reset_score()
        self.score += score_gained
        
        # Process collision events for effects
        if hasattr(self.physics, 'get_collision_events'):
            events = self.physics.get_collision_events()
            for event_type, position in events:
                x, y = position.x, position.y
                
                if event_type == "pig_eliminated":
                    self.effects.create_pig_hit_effect(x, y, eliminated=True)
                    self.effects.add_damage_number(x, y, 500, GOLD)
                elif event_type == "pig_hit":
                    self.effects.create_pig_hit_effect(x, y, eliminated=False)
                    self.effects.add_damage_number(x, y, 10, YELLOW)
                elif event_type == "pig_crushed":
                    self.effects.create_pig_hit_effect(x, y, eliminated=True)
                    self.effects.add_damage_number(x, y, 300, ORANGE)
                elif event_type == "block_destroyed":
                    # Find block material for effect
                    material = "wood"
                    for block in self.blocks:
                        if block.destroyed and abs(block.body.position.x - x) < 5:
                            material = block.material
                            break
                    self.effects.create_destruction_effect(x, y, material)
                    self.effects.add_damage_number(x, y, 100, GREEN)
                elif event_type == "block_hit":
                    self.effects.create_impact_effect(x, y, "normal")
                elif event_type == "block_collapsed":
                    self.effects.create_impact_effect(x, y, "strong")
                    self.effects.add_damage_number(x, y, 50, YELLOW)
                elif event_type == "block_shattered":
                    self.effects.create_impact_effect(x, y, "destroy")
                    self.effects.add_damage_number(x, y, 25, LIGHTBLUE)
        
        # Update effects
        self.effects.update(dt)
        
        # Update slingshot dragging
        if self.dragging and self.current_bird:
            mouse_pos = pygame.mouse.get_pos()
            self.slingshot.pull(mouse_pos)
        
        # Update reload timer
        if self.reload_timer > 0:
            self.reload_timer -= 1
        
        # Check for stopped birds and remove them
        for bird in self.launched_birds[:]:
            if bird.is_stopped():
                # Remove bird from physics tracking if using simple physics
                if hasattr(self.physics, 'remove_bird'):
                    self.physics.remove_bird(bird)
                bird.remove()
                self.launched_birds.remove(bird)
        
        # Load next bird if conditions are met
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
        
        # Check victory/defeat conditions
        if self.check_victory():
            self.total_score += self.score
            self.state = GameState.GAME_OVER
        elif self.check_defeat():
            self.state = GameState.GAME_OVER.y
                        # Only block if the moving bird is near the slingshot
            if bx < 300:  # Near the left side where slingshot is
                safe_to_load = False
                
            
            if safe_to_load:
                self.current_bird = self.birds.pop(0)
                self.slingshot.load_bird(self.current_bird)
        
        # Check victory/defeat conditions
        if self.check_victory():
            self.total_score += self.score
            self.state = GameState.GAME_OVER
        elif self.check_defeat():
            self.state = GameState.GAME_OVER
    
    def check_victory(self):
        """Check if all pigs are defeated"""
        return all(pig.dead for pig in self.pigs)
    
    def check_defeat(self):
        """Check if no birds left and pigs remain"""
        no_birds = not self.current_bird and not self.birds and not self.launched_birds
        pigs_remain = any(not pig.dead for pig in self.pigs)
        return no_birds and pigs_remain
    
    def draw(self):
        """Draw everything"""
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
            if offset_x != 0 or offset_y != 0:
                # Create a temporary surface for shaking
                temp_surface = pygame.Surface((WIN_WIDTH, WIN_HEIGHT))
                temp_surface.fill(WHITE)
                
                # Draw everything to temp surface
                self.ui.draw_background_to_surface(temp_surface)
                self.slingshot.draw(temp_surface)
                
                # Draw blocks
                for block in self.blocks:
                    block.draw(temp_surface)
                
                # Draw pigs
                for pig in self.pigs:
                    pig.draw(temp_surface)
                
                # Draw birds
                if self.current_bird:
                    self.current_bird.draw(temp_surface)
                for bird in self.launched_birds:
                    bird.draw(temp_surface)
                for bird in self.birds:
                    bird.draw(temp_surface)
                
                # Draw ground line
                pygame.draw.line(temp_surface, BLACK, 
                               (0, WIN_HEIGHT - GROUND_HEIGHT), 
                               (WIN_WIDTH, WIN_HEIGHT - GROUND_HEIGHT), 3)
                
                # Draw effects
                self.effects.draw(temp_surface)
                
                # Blit shaken surface to screen
                self.screen.blit(temp_surface, (offset_x, offset_y))
            else:
                # Normal drawing without shake
                # Draw game world
                self.ui.draw_background()
                
                # Draw slingshot
                self.slingshot.draw(self.screen)
                
                # Draw blocks
                for block in self.blocks:
                    block.draw(self.screen)
                
                # Draw pigs
                for pig in self.pigs:
                    pig.draw(self.screen)
                
                # Draw birds
                if self.current_bird:
                    self.current_bird.draw(self.screen)
                for bird in self.launched_birds:
                    bird.draw(self.screen)
                for bird in self.birds:
                    bird.draw(self.screen)
                
                # Draw ground line
                pygame.draw.line(self.screen, BLACK, 
                               (0, WIN_HEIGHT - GROUND_HEIGHT), 
                               (WIN_WIDTH, WIN_HEIGHT - GROUND_HEIGHT), 3)
                
                # Draw effects
                self.effects.draw(self.screen)
            
            # Draw HUD (always on top, no shake)
            birds_left = len(self.birds) + (1 if self.current_bird else 0)
            pigs_left = sum(1 for pig in self.pigs if not pig.dead)
            self.ui.draw_hud(self.score + self.total_score, birds_left, 
                           pigs_left, self.current_level)
            
            # Draw pause overlay
            if self.state == GameState.PAUSED:
                self.draw_pause_overlay()
                
        elif self.state == GameState.GAME_OVER:
            # Draw game world in background
            self.ui.draw_background()
            
            # Draw game over screen
            self.ui.draw_game_over(self.check_victory(), 
                                  self.score + self.total_score, 
                                  self.current_level)
        
        # Update display
        pygame.display.flip()
    
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
        """Main game loop"""
        while self.running:
            dt = self.clock.tick(FPS) / 1000.0
            
            self.handle_events()
            self.update(dt)
            self.draw()
        
        pygame.quit()
        sys.exit()


def main():
    """Entry point"""
    game = AngryBirdsGame()
    game.run()


if __name__ == "__main__":
    main()
"""
levels.py - Level builder with different castle configurations
"""

from entities import Block, Pig
from constants import *


class LevelBuilder:
    """Builds different level configurations"""
    
    @staticmethod
    def create_debug_level(space):
        """A minimal level for debugging with just one block and one pig."""
        blocks = []
        pigs = []
        
        # Add one single block
        blocks.append(Block(space, 800, WIN_HEIGHT - GROUND_HEIGHT - 40, 40, 40, "wood"))
        
        # Add one single pig
        pigs.append(Pig(space, 900, WIN_HEIGHT - GROUND_HEIGHT - 20))
        
        return blocks, pigs
    
    @staticmethod
    def create_level(space, level_num=1):
        """Create a level based on level number"""
        if level_num == 1:
            return LevelBuilder.create_simple_castle(space)
        elif level_num == 2:
            return LevelBuilder.create_ice_fortress(space)
        elif level_num == 3:
            return LevelBuilder.create_stone_castle(space)
        else:
            return LevelBuilder.create_complex_castle(space)
    
    @staticmethod
    def create_simple_castle(space):
        """Create a simple castle for beginners"""
        blocks = []
        pigs = []
        x_start = 700
        ground_y = WIN_HEIGHT - GROUND_HEIGHT
        
        # Foundation
        blocks.append(Block(space, x_start, ground_y - 40, 40, 40, "wood"))
        blocks.append(Block(space, x_start + 120, ground_y - 40, 40, 40, "wood"))
        
        # Walls
        blocks.append(Block(space, x_start, ground_y - 140, 20, 100, "wood"))
        blocks.append(Block(space, x_start + 140, ground_y - 140, 20, 100, "wood"))
        
        # Roof
        blocks.append(Block(space, x_start - 10, ground_y - 150, 180, 20, "wood"))
        
        # Pig
        pigs.append(Pig(space, x_start + 80, ground_y - 180, pig_type="normal"))
        
        return blocks, pigs
    
    @staticmethod
    def create_ice_fortress(space):
        """Create a fortress made primarily of ice"""
        blocks = []
        pigs = []
        x_start = 650
        ground_y = WIN_HEIGHT - GROUND_HEIGHT
        
        # Ice foundation
        for i in range(4):
            blocks.append(Block(space, x_start + i * 50, ground_y - 30, 45, 30, "ice"))
        
        # Ice walls - first floor
        blocks.append(Block(space, x_start - 10, ground_y - 130, 20, 100, "ice"))
        blocks.append(Block(space, x_start + 190, ground_y - 130, 20, 100, "ice"))
        
        # Platform
        blocks.append(Block(space, x_start - 20, ground_y - 140, 240, 15, "wood"))
        
        # Second floor ice walls
        blocks.append(Block(space, x_start + 20, ground_y - 240, 20, 100, "ice"))
        blocks.append(Block(space, x_start + 160, ground_y - 240, 20, 100, "ice"))
        
        # Top platform
        blocks.append(Block(space, x_start + 10, ground_y - 250, 180, 15, "ice"))
        
        # Decorative ice blocks
        blocks.append(Block(space, x_start + 50, ground_y - 290, 30, 40, "ice"))
        blocks.append(Block(space, x_start + 120, ground_y - 290, 30, 40, "ice"))
        
        # Add pigs
        pigs.append(Pig(space, x_start + 100, ground_y - 170, pig_type="normal"))
        pigs.append(Pig(space, x_start + 100, ground_y - 280, pig_type="helmet"))
        
        return blocks, pigs
    
    @staticmethod
    def create_stone_castle(space):
        """Create a strong stone castle"""
        blocks = []
        pigs = []
        x_start = 700
        ground_y = WIN_HEIGHT - GROUND_HEIGHT
        
        # Stone foundation - very strong
        blocks.append(Block(space, x_start - 20, ground_y - 50, 60, 50, "stone"))
        blocks.append(Block(space, x_start + 160, ground_y - 50, 60, 50, "stone"))
        
        # Stone pillars
        blocks.append(Block(space, x_start - 10, ground_y - 200, 30, 150, "stone"))
        blocks.append(Block(space, x_start + 180, ground_y - 200, 30, 150, "stone"))
        
        # Wood interior
        blocks.append(Block(space, x_start + 40, ground_y - 100, 20, 100, "wood"))
        blocks.append(Block(space, x_start + 140, ground_y - 100, 20, 100, "wood"))
        
        # Platforms
        blocks.append(Block(space, x_start - 20, ground_y - 210, 250, 20, "stone"))
        blocks.append(Block(space, x_start + 20, ground_y - 110, 160, 15, "wood"))
        
        # Upper structure
        blocks.append(Block(space, x_start + 50, ground_y - 280, 20, 70, "wood"))
        blocks.append(Block(space, x_start + 130, ground_y - 280, 20, 70, "wood"))
        blocks.append(Block(space, x_start + 40, ground_y - 290, 120, 15, "stone"))
        
        # Add pigs - including a king pig
        pigs.append(Pig(space, x_start + 100, ground_y - 140, pig_type="normal"))
        pigs.append(Pig(space, x_start + 90, ground_y - 240, pig_type="king"))
        pigs.append(Pig(space, x_start + 110, ground_y - 320, pig_type="helmet"))
        
        return blocks, pigs
    
    @staticmethod
    def create_complex_castle(space):
        """Create a complex multi-material castle"""
        blocks = []
        pigs = []
        x_start = 650
        ground_y = WIN_HEIGHT - GROUND_HEIGHT
        
        # Mixed foundation
        blocks.append(Block(space, x_start, ground_y - 40, 40, 40, "stone"))
        blocks.append(Block(space, x_start + 60, ground_y - 40, 40, 40, "metal"))
        blocks.append(Block(space, x_start + 120, ground_y - 40, 40, 40, "metal"))
        blocks.append(Block(space, x_start + 180, ground_y - 40, 40, 40, "stone"))
        
        # First floor - mixed materials
        blocks.append(Block(space, x_start - 10, ground_y - 160, 25, 120, "stone"))
        blocks.append(Block(space, x_start + 205, ground_y - 160, 25, 120, "stone"))
        
        # Interior walls
        blocks.append(Block(space, x_start + 50, ground_y - 120, 20, 80, "wood"))
        blocks.append(Block(space, x_start + 150, ground_y - 120, 20, 80, "wood"))
        
        # First platform
        blocks.append(Block(space, x_start - 20, ground_y - 170, 260, 20, "metal"))
        
        # Second floor
        blocks.append(Block(space, x_start + 20, ground_y - 270, 20, 100, "wood"))
        blocks.append(Block(space, x_start + 180, ground_y - 270, 20, 100, "wood"))
        blocks.append(Block(space, x_start + 100, ground_y - 250, 20, 80, "ice"))
        
        # Second platform
        blocks.append(Block(space, x_start + 10, ground_y - 280, 200, 15, "stone"))
        
        # Top structure
        blocks.append(Block(space, x_start + 60, ground_y - 350, 20, 70, "ice"))
        blocks.append(Block(space, x_start + 140, ground_y - 350, 20, 70, "ice"))
        blocks.append(Block(space, x_start + 50, ground_y - 360, 120, 12, "wood"))
        
        # Decorative elements
        blocks.append(Block(space, x_start + 85, ground_y - 390, 30, 30, "ice"))
        blocks.append(Block(space, x_start + 105, ground_y - 420, 20, 20, "wood"))
        
        # Add various pig types
        pigs.append(Pig(space, x_start + 110, ground_y - 80, pig_type="normal"))
        pigs.append(Pig(space, x_start + 100, ground_y - 200, pig_type="helmet"))
        pigs.append(Pig(space, x_start + 110, ground_y - 310, pig_type="king"))
        pigs.append(Pig(space, x_start + 60, ground_y - 200, pig_type="normal"))
        
        return blocks, pigs
    
    @staticmethod
    def get_bird_lineup(level_num):
        """Get the birds available for a level"""
        lineups = {
            1: ["red", "red", "red"],
            2: ["red", "yellow", "red", "blue"],
            3: ["red", "yellow", "yellow", "red", "blue"],
            4: ["yellow", "red", "blue", "yellow", "red", "blue"]
        }
        return lineups.get(level_num, ["red"] * 5)
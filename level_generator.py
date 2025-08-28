"""
level_generator.py - AI-powered dynamic level generation with difficulty rating
Generates unique castle structures using LLM APIs
"""

import json
import random
import hashlib
import os
from typing import List, Dict, Tuple, Optional
import math

# Import configuration
try:
    from config import *
except ImportError:
    # Default configuration if config.py doesn't exist
    OPENAI_API_KEY = None
    GEMINI_API_KEY = None
    LEVEL_GENERATOR_PROVIDER = "local"
    DIFFICULTY_RANGES = {
        1: (200, 600),
        2: (500, 900),
        3: (800, 1300),
        4: (1200, 1800),
        5: (1600, 2000),
    }

# For API calls - you can switch between providers
try:
    import openai
except ImportError:
    openai = None
    print("OpenAI not installed. Run: pip install openai")

try:
    import google.generativeai as genai
except ImportError:
    genai = None
    print("Google Generative AI not installed. Run: pip install google-generativeai")

from entities import Block, Pig
from constants import *


class DifficultyCalculator:
    """Calculate difficulty using ELO-like rating system"""
    
    @staticmethod
    def calculate_structure_difficulty(blocks: List[Dict], pigs: List[Dict]) -> float:
        """
        Calculate difficulty score based on structure properties
        Returns a score from 0-2000 (like chess ELO)
        """
        score = 1000  # Base score
        
        # Factor 1: Total structure health
        total_health = 0
        for block in blocks:
            material_health = {
                "ice": 30,
                "wood": 70,
                "stone": 150,
                "metal": 250
            }
            total_health += material_health.get(block["material"], 70)
        
        # Add health score (0-300 points)
        score += min(300, total_health / 10)
        
        # Factor 2: Pig protection level
        for pig in pigs:
            # Check how well protected each pig is
            pig_y = pig["y"]
            protection_score = 0
            
            # Count blocks above and around pig
            for block in blocks:
                if block["y"] < pig_y:  # Block is above pig
                    protection_score += 10
                if abs(block["x"] - pig["x"]) < 100:  # Block is near pig
                    protection_score += 5
            
            # Special pig types add difficulty
            if pig["type"] == "helmet":
                score += 50
            elif pig["type"] == "king":
                score += 100
                
            score += min(100, protection_score)
        
        # Factor 3: Structure height (taller = harder)
        if blocks:
            max_height = max(WIN_HEIGHT - b["y"] for b in blocks)
            score += min(200, max_height)
        
        # Factor 4: Material composition
        material_scores = {"ice": 0, "wood": 1, "stone": 2, "metal": 3}
        avg_material_score = sum(material_scores.get(b["material"], 1) for b in blocks) / max(len(blocks), 1)
        score += avg_material_score * 100
        
        # Factor 5: Structural complexity (number of blocks)
        score += min(200, len(blocks) * 10)
        
        return min(2000, max(200, score))  # Clamp between 200-2000


class LevelGenerator:
    """Generate unique levels using LLM APIs"""
    
    def __init__(self, api_key: Optional[str] = None, provider: str = "openai"):
        """
        Initialize with API credentials
        provider: "openai", "gemini", or "local" (no API, rule-based)
        """
        self.provider = provider
        self.api_key = api_key or os.getenv(f"{provider.upper()}_API_KEY")
        
        if provider == "openai" and openai:
            openai.api_key = self.api_key
        elif provider == "gemini" and genai:
            genai.configure(api_key=self.api_key)
        
        # Cache for generated structures
        self.structure_cache = {}
        
        # Difficulty ranges for each level
        self.level_difficulty_ranges = {
            1: (200, 600),    # Easy
            2: (500, 900),    # Medium-Easy
            3: (800, 1300),   # Medium-Hard
            4: (1200, 1800),  # Hard
            5: (1600, 2000),  # Expert
        }
    
    def generate_structure(self, level_num: int, seed: Optional[str] = None) -> Tuple[List[Dict], List[Dict]]:
        """
        Generate a unique structure for the given level
        Returns: (blocks, pigs) as lists of dictionaries
        """
        # Generate seed for uniqueness
        if seed is None:
            seed = f"{level_num}_{random.randint(0, 999999)}"
        
        # Check cache
        cache_key = f"{level_num}_{seed}"
        if cache_key in self.structure_cache:
            return self.structure_cache[cache_key]
        
        # Get difficulty range for this level
        min_diff, max_diff = self.level_difficulty_ranges.get(level_num, (500, 1000))
        target_difficulty = random.randint(min_diff, max_diff)
        
        # Generate structure based on provider
        if self.provider == "openai" and openai:
            structure = self._generate_with_openai(level_num, target_difficulty, seed)
        elif self.provider == "gemini" and genai:
            structure = self._generate_with_gemini(level_num, target_difficulty, seed)
        else:
            # Fallback to rule-based generation
            structure = self._generate_rule_based(level_num, target_difficulty, seed)
        
        # Validate and adjust difficulty
        blocks, pigs = structure
        actual_difficulty = DifficultyCalculator.calculate_structure_difficulty(blocks, pigs)
        
        # If difficulty is too far off, adjust
        if abs(actual_difficulty - target_difficulty) > 300:
            blocks, pigs = self._adjust_difficulty(blocks, pigs, target_difficulty)
        
        # Cache the result
        self.structure_cache[cache_key] = (blocks, pigs)
        
        return blocks, pigs
    
    def _generate_with_openai(self, level_num: int, target_difficulty: float, seed: str) -> Tuple[List[Dict], List[Dict]]:
        """Generate structure using OpenAI API"""
        if not openai:
            return self._generate_rule_based(level_num, target_difficulty, seed)
        
        prompt = self._create_llm_prompt(level_num, target_difficulty)
        
        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a level designer for Angry Birds. Generate castle structures as JSON."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.8,
                max_tokens=1000
            )
            
            result = response.choices[0].message.content
            return self._parse_llm_response(result)
            
        except Exception as e:
            print(f"OpenAI API error: {e}")
            return self._generate_rule_based(level_num, target_difficulty, seed)
    
    def _generate_with_gemini(self, level_num: int, target_difficulty: float, seed: str) -> Tuple[List[Dict], List[Dict]]:
        """Generate structure using Google Gemini API"""
        if not genai:
            return self._generate_rule_based(level_num, target_difficulty, seed)
        
        prompt = self._create_llm_prompt(level_num, target_difficulty)
        
        try:
            model = genai.GenerativeModel('gemini-pro')
            response = model.generate_content(prompt)
            return self._parse_llm_response(response.text)
            
        except Exception as e:
            print(f"Gemini API error: {e}")
            return self._generate_rule_based(level_num, target_difficulty, seed)
    
    def _create_llm_prompt(self, level_num: int, target_difficulty: float) -> str:
        """Create prompt for LLM to generate structure"""
        materials = {
            1: ["wood", "ice"],
            2: ["wood", "ice", "stone"],
            3: ["wood", "stone", "metal"],
            4: ["stone", "metal", "ice"],
            5: ["metal", "stone", "wood"]
        }
        
        available_materials = materials.get(level_num, ["wood", "stone"])
        
        prompt = f"""Generate an Angry Birds castle structure with these requirements:
        
Level: {level_num}
Target Difficulty Score: {target_difficulty} (scale 200-2000, like chess ELO)
Available Materials: {', '.join(available_materials)}
Play Area: x=650-950, y=350-650 (y=650 is ground level)

Generate a JSON structure with:
1. "blocks": Array of blocks, each with:
   - "x": x position (650-950)
   - "y": y position (350-650, lower = higher up)
   - "width": block width (20-80)
   - "height": block height (20-100)
   - "material": one of {available_materials}

2. "pigs": Array of pigs (1-4 pigs based on level), each with:
   - "x": x position
   - "y": y position
   - "type": "normal", "helmet", or "king" (higher levels can have special types)

Requirements:
- Structures should be physically stable
- Pigs should be protected but not impossible to hit
- Use {len(available_materials)*5} to {len(available_materials)*8} blocks
- Create interesting, unique layouts (towers, bridges, rooms, etc.)
- Higher difficulty = more protection, stronger materials, complex layouts

Return ONLY valid JSON, no other text."""
        
        return prompt
    
    def _parse_llm_response(self, response: str) -> Tuple[List[Dict], List[Dict]]:
        """Parse LLM response to extract structure data"""
        try:
            # Try to extract JSON from response
            import re
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                data = json.loads(json_match.group())
                blocks = data.get("blocks", [])
                pigs = data.get("pigs", [])
                
                # Validate and fix positions
                for block in blocks:
                    block["x"] = max(650, min(950, block.get("x", 800)))
                    block["y"] = max(350, min(650, block.get("y", 500)))
                    block["width"] = max(20, min(80, block.get("width", 40)))
                    block["height"] = max(20, min(100, block.get("height", 40)))
                
                for pig in pigs:
                    pig["x"] = max(650, min(950, pig.get("x", 800)))
                    pig["y"] = max(350, min(640, pig.get("y", 500)))
                
                return blocks, pigs
                
        except (json.JSONDecodeError, AttributeError) as e:
            print(f"Failed to parse LLM response: {e}")
        
        # Fallback to rule-based if parsing fails
        return self._generate_rule_based(1, 500, "fallback")
    
    def _generate_rule_based(self, level_num: int, target_difficulty: float, seed: str) -> Tuple[List[Dict], List[Dict]]:
        """Rule-based structure generation (fallback when no API available)"""
        random.seed(seed)  # Ensure uniqueness but reproducibility
        
        blocks = []
        pigs = []
        
        x_start = 700
        ground_y = WIN_HEIGHT - GROUND_HEIGHT
        
        # Determine materials based on difficulty
        if target_difficulty < 600:
            materials = ["wood", "ice"]
            pig_types = ["normal"]
        elif target_difficulty < 1000:
            materials = ["wood", "stone", "ice"]
            pig_types = ["normal", "helmet"]
        elif target_difficulty < 1400:
            materials = ["stone", "wood", "metal"]
            pig_types = ["normal", "helmet", "king"]
        else:
            materials = ["metal", "stone"]
            pig_types = ["helmet", "king"]
        
        # Generate random structure patterns
        pattern = random.choice(["tower", "pyramid", "fortress", "bridge", "complex"])
        
        if pattern == "tower":
            # Tall tower structure
            floors = random.randint(2, 4)
            for floor in range(floors):
                y_pos = ground_y - 40 - floor * 100
                
                # Pillars
                blocks.append({
                    "x": x_start,
                    "y": y_pos - 60,
                    "width": 20,
                    "height": 100,
                    "material": random.choice(materials)
                })
                blocks.append({
                    "x": x_start + 140,
                    "y": y_pos - 60,
                    "width": 20,
                    "height": 100,
                    "material": random.choice(materials)
                })
                
                # Platform
                blocks.append({
                    "x": x_start - 10,
                    "y": y_pos - 70,
                    "width": 180,
                    "height": 20,
                    "material": random.choice(materials)
                })
                
                # Add pig on some floors
                if floor % 2 == 0 or floor == floors - 1:
                    pigs.append({
                        "x": x_start + 80,
                        "y": y_pos - 90,
                        "type": random.choice(pig_types)
                    })
        
        elif pattern == "pyramid":
            # Pyramid structure
            levels = random.randint(3, 5)
            for level in range(levels):
                width = (levels - level) * 2
                for i in range(width):
                    blocks.append({
                        "x": x_start + level * 20 + i * 40,
                        "y": ground_y - 40 - level * 40,
                        "width": 40,
                        "height": 40,
                        "material": random.choice(materials)
                    })
            
            # Place pigs
            pigs.append({
                "x": x_start + levels * 40,
                "y": ground_y - 40 - levels * 40 - 20,
                "type": random.choice(pig_types)
            })
        
        elif pattern == "fortress":
            # Castle-like fortress
            # Walls
            for i in range(2):
                blocks.append({
                    "x": x_start + i * 200,
                    "y": ground_y - 140,
                    "width": 30,
                    "height": 140,
                    "material": random.choice(materials)
                })
            
            # Roof/platforms
            blocks.append({
                "x": x_start - 10,
                "y": ground_y - 150,
                "width": 240,
                "height": 20,
                "material": random.choice(materials)
            })
            
            # Internal structures
            for i in range(random.randint(2, 4)):
                blocks.append({
                    "x": x_start + 40 + i * 40,
                    "y": ground_y - random.randint(40, 120),
                    "width": random.randint(20, 40),
                    "height": random.randint(20, 80),
                    "material": random.choice(materials)
                })
            
            # Place pigs
            for i in range(min(3, 1 + level_num // 2)):
                pigs.append({
                    "x": x_start + 50 + i * 60,
                    "y": ground_y - 60,
                    "type": random.choice(pig_types)
                })
        
        elif pattern == "bridge":
            # Bridge structure with gaps
            # Support pillars
            for i in range(3):
                blocks.append({
                    "x": x_start + i * 80,
                    "y": ground_y - 60,
                    "width": 20,
                    "height": 60,
                    "material": random.choice(materials)
                })
            
            # Bridge spans
            for i in range(2):
                blocks.append({
                    "x": x_start + i * 80,
                    "y": ground_y - 70,
                    "width": 100,
                    "height": 15,
                    "material": random.choice(materials)
                })
            
            # Upper structure
            blocks.append({
                "x": x_start + 60,
                "y": ground_y - 120,
                "width": 80,
                "height": 50,
                "material": random.choice(materials)
            })
            
            # Pigs
            pigs.append({
                "x": x_start + 100,
                "y": ground_y - 90,
                "type": random.choice(pig_types)
            })
        
        else:  # complex
            # Random complex structure
            num_blocks = random.randint(8, 15)
            for _ in range(num_blocks):
                blocks.append({
                    "x": x_start + random.randint(-50, 200),
                    "y": ground_y - random.randint(40, 200),
                    "width": random.randint(20, 60),
                    "height": random.randint(20, 80),
                    "material": random.choice(materials)
                })
            
            # Place pigs randomly but safely
            num_pigs = min(4, 1 + level_num // 2)
            for _ in range(num_pigs):
                pigs.append({
                    "x": x_start + random.randint(20, 180),
                    "y": ground_y - random.randint(60, 150),
                    "type": random.choice(pig_types)
                })
        
        return blocks, pigs
    
    def _adjust_difficulty(self, blocks: List[Dict], pigs: List[Dict], target_difficulty: float) -> Tuple[List[Dict], List[Dict]]:
        """Adjust structure to match target difficulty"""
        current_difficulty = DifficultyCalculator.calculate_structure_difficulty(blocks, pigs)
        
        if current_difficulty < target_difficulty - 200:
            # Make harder: add blocks or upgrade materials
            material_upgrade = {"ice": "wood", "wood": "stone", "stone": "metal"}
            for block in random.sample(blocks, min(3, len(blocks))):
                if block["material"] in material_upgrade:
                    block["material"] = material_upgrade[block["material"]]
        
        elif current_difficulty > target_difficulty + 200:
            # Make easier: downgrade materials or remove blocks
            material_downgrade = {"metal": "stone", "stone": "wood", "wood": "ice"}
            for block in random.sample(blocks, min(3, len(blocks))):
                if block["material"] in material_downgrade:
                    block["material"] = material_downgrade[block["material"]]
        
        return blocks, pigs
    
    def create_level_from_structure(self, space, structure_data: Tuple[List[Dict], List[Dict]]) -> Tuple[List, List]:
        """Convert structure data to actual game objects"""
        blocks_data, pigs_data = structure_data
        blocks = []
        pigs = []
        
        # Create blocks
        for block_data in blocks_data:
            block = Block(
                space,
                block_data["x"],
                block_data["y"],
                block_data["width"],
                block_data["height"],
                block_data["material"]
            )
            blocks.append(block)
        
        # Create pigs
        for pig_data in pigs_data:
            pig = Pig(
                space,
                pig_data["x"],
                pig_data["y"],
                pig_type=pig_data["type"]
            )
            pigs.append(pig)
        
        return blocks, pigs


# Singleton instance for easy access
_generator_instance = None

def get_level_generator(api_key: Optional[str] = None, provider: str = "local") -> LevelGenerator:
    """Get or create the level generator instance"""
    global _generator_instance
    if _generator_instance is None:
        _generator_instance = LevelGenerator(api_key, provider)
    return _generator_instance
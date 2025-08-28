"""
config.py - Configuration for API keys and settings
"""

# API Configuration
# Set your API keys here or use environment variables

# OpenAI API Key (for GPT-3.5/GPT-4)
# Get your key from: https://platform.openai.com/api-keys
OPENAI_API_KEY = None  # Replace with "your-openai-api-key" or set OPENAI_API_KEY env variable

# Google Gemini API Key
# Get your key from: https://makersuite.google.com/app/apikey
GEMINI_API_KEY = None  # Replace with "your-gemini-api-key" or set GEMINI_API_KEY env variable

# Choose your preferred provider:
# - "local": No API, uses rule-based generation (FREE, works offline)
# - "openai": Uses OpenAI GPT models (requires API key and credits)
# - "gemini": Uses Google Gemini (requires API key, has free tier)
LEVEL_GENERATOR_PROVIDER = "local"  # Change to "openai" or "gemini" when you have API keys

# Generation settings
CACHE_GENERATED_LEVELS = True  # Cache levels to avoid repeated API calls
MAX_GENERATION_ATTEMPTS = 3  # Max attempts if generation fails
USE_DIFFICULTY_SCALING = True  # Scale difficulty based on player performance

# Difficulty settings
DIFFICULTY_RANGES = {
    1: (200, 600),    # Level 1: Easy structures
    2: (500, 900),    # Level 2: Medium-Easy
    3: (800, 1300),   # Level 3: Medium-Hard
    4: (1200, 1800),  # Level 4: Hard
    5: (1600, 2000),  # Level 5: Expert
}

# Structure generation preferences
STRUCTURE_PATTERNS = [
    "tower",      # Vertical structures
    "pyramid",    # Triangular arrangements
    "fortress",   # Castle-like structures
    "bridge",     # Horizontal with supports
    "complex",    # Random complex arrangements
    "bunker",     # Low, heavily protected
    "spiral",     # Spiral/circular patterns
]

# Material availability per level
MATERIALS_BY_LEVEL = {
    1: ["wood", "ice"],
    2: ["wood", "ice", "stone"],
    3: ["wood", "stone", "metal"],
    4: ["stone", "metal", "ice"],
    5: ["metal", "stone", "wood"],
}

# Pig types by level
PIG_TYPES_BY_LEVEL = {
    1: ["normal"],
    2: ["normal", "normal", "helmet"],
    3: ["normal", "helmet", "king"],
    4: ["helmet", "helmet", "king"],
    5: ["helmet", "king", "king"],
}
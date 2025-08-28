# Angry Birds – Pymunk Physics Edition 🎯🐦

A Python re-creation of **Angry Birds**, built with **Pygame** for rendering and **Pymunk** for physics simulation.  
Features **dynamic castles**, **multiple bird types**, **special pig types**, combo scoring, particle effects, and even **AI-powered level generation**.

---

## 🚀 Features
- **Realistic Physics**  
  Powered by [Pymunk](http://www.pymunk.org/) with enhanced collision handling.  
- **Bird Types**  
  - 🟥 Red: Balanced  
  - 🟨 Yellow: Extra speed & damage  
  - 🔵 Blue: Smaller but faster  
- **Pig Types**  
  - Normal  
  - Helmet (extra health)  
  - King (boss pig)  
- **Destructible Blocks**  
  Wood, Stone, Ice, and Metal, each with different strength and resistance.  
- **Dynamic Structures**  
  - Hand-crafted castles (`levels.py`)  
  - AI-generated castles with difficulty rating (`level_generator.py`)  
- **Visual Effects**  
  Explosions, particles, screen shake, floating damage numbers.  
- **Scoring System**  
  Combos, bonuses for leftover birds, star ratings.  
- **Game States**  
  Menu, Level Select, Instructions, Pause, Level Intro, Victory/Defeat.

---

## 🖼️ Screens & UI
- Gradient sky with clouds & animated grass  
- HUD with score, pigs & birds left, combo indicator  
- Level intro & tips per level  
- Game Over screen with **star ratings**  

---

## 📂 Project Structure
```
.
├── constants.py       # Game constants (window, colors, level configs, scoring)
├── config.py          # API settings for OpenAI / Gemini (optional for AI levels)
├── effects.py         # Particles, damage numbers, screen shake
├── entities.py        # Birds, Pigs, Blocks with health & visuals
├── levels.py          # Stable handcrafted castle layouts
├── level_generator.py # AI-powered or rule-based structure generator
├── physics_engine.py  # Enhanced Pymunk physics with collisions/damage
├── simple_physics.py  # Fallback physics engine (manual collision detection)
├── slingshot.py       # Realistic slingshot mechanics
├── ui.py              # HUD, menus, backgrounds, overlays
├── main.py            # Game loop, states, camera, score logic
├── test_setup.py      # Verify Pymunk, pygame, and imports
```

---

## ⚙️ Requirements
- Python **3.10+**
- [Pygame](https://www.pygame.org/)  
- [Pymunk](http://www.pymunk.org/en/latest/)  
- Optional (for AI level generation):  
  - `openai`  
  - `google-generativeai`

Install dependencies:
```bash
pip install pygame pymunk openai google-generativeai
```

---

## ▶️ Running the Game
1. Run the setup test to confirm your environment:
   ```bash
   python test_setup.py
   ```
   If everything passes ✅, continue.
2. Start the game:
   ```bash
   python main.py
   ```

---

## 🎮 Controls
- **Mouse** → Click, drag, and release to launch a bird  
- **P** → Pause / Resume  
- **R** → Restart level  
- **ESC** → Menu / Exit  
- **SPACE** → Continue after victory/defeat  

---

## 🔮 AI Level Generation
- Configure `config.py` with your API key(s):  
  - `OPENAI_API_KEY = "your-key"`  
  - or `GEMINI_API_KEY = "your-key"`  
- Set provider:
  ```python
  LEVEL_GENERATOR_PROVIDER = "openai"  # or "gemini" / "local"
  ```
- The generator will create **unique castles each run** at the same difficulty rating.

---

## 🏗️ Future Improvements
- Bird special abilities (split blue bird, speed dash yellow, etc.)  
- More AI-generated patterns (spirals, moving blocks, traps)  
- Multiplayer / online scoreboards  
- Mobile-friendly build  

---

"""
test_setup.py - Test script to verify Pymunk installation and compatibility
"""

import sys
import pygame
import pymunk

def test_pymunk():
    """Test Pymunk functionality"""
    print(f"Python version: {sys.version}")
    print(f"Pygame version: {pygame.version.ver}")
    print(f"Pymunk version: {pymunk.version}")
    
    # Test basic pymunk functionality
    try:
        space = pymunk.Space()
        space.gravity = (0, 981)
        
        # Test body creation
        body = pymunk.Body(1, pymunk.moment_for_circle(1, 0, 10))
        body.position = 100, 100
        
        # Test shape creation
        shape = pymunk.Circle(body, 10)
        shape.elasticity = 0.5
        
        space.add(body, shape)
        
        # Test stepping
        space.step(1/60)
        
        print("✓ Basic Pymunk functionality: OK")
        
        # Test collision handlers
        try:
            handler = space.add_collision_handler(1, 2)
            print("✓ Collision handlers (new style): OK")
        except AttributeError:
            print("✗ Collision handlers (new style): Not supported")
            try:
                space.add_default_collision_handler()
                print("✓ Default collision handler: OK")
            except:
                print("✗ Default collision handler: Not supported")
                print("  Will use manual collision detection")
        
        # Test position access
        x, y = body.position.x, body.position.y
        print(f"✓ Position access: OK (x={x}, y={y})")
        
        # Test velocity
        body.velocity = (100, -100)
        vx, vy = body.velocity.x, body.velocity.y
        print(f"✓ Velocity access: OK (vx={vx}, vy={vy})")
        
        print("\n✅ All tests passed! Pymunk is working correctly.")
        return True
        
    except Exception as e:
        print(f"\n❌ Error during testing: {e}")
        print("\nPlease try reinstalling Pymunk:")
        print("  pip uninstall pymunk")
        print("  pip install pymunk")
        return False

def test_imports():
    """Test if all game modules can be imported"""
    print("\nTesting game module imports...")
    
    modules = [
        'constants',
        'slingshot',
        'levels',
        'ui',
        'entities',
        'physics_engine',
        'simple_physics',
        'main'
    ]
    
    failed = []
    for module in modules:
        try:
            __import__(module)
            print(f"✓ {module}.py: OK")
        except ImportError as e:
            print(f"✗ {module}.py: Failed - {e}")
            failed.append(module)
    
    if failed:
        print(f"\n❌ Some modules failed to import: {', '.join(failed)}")
        print("Make sure all files are in the same directory.")
        return False
    else:
        print("\n✅ All modules imported successfully!")
        return True

if __name__ == "__main__":
    print("=" * 50)
    print("Angry Birds Pymunk - Setup Test")
    print("=" * 50)
    
    pymunk_ok = test_pymunk()
    imports_ok = test_imports()
    
    print("\n" + "=" * 50)
    if pymunk_ok and imports_ok:
        print("✅ Everything is working! You can run the game with:")
        print("   python main.py")
    else:
        print("❌ Some issues were found. Please fix them before running the game.")
    print("=" * 50)
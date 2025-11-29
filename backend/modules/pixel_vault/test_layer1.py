"""
Quick test script for PixelVault Layer 1 (Password Protection)
"""

from PIL import Image
import numpy as np
import sys
import os

# Add module path
sys.path.insert(0, os.path.dirname(__file__))

from main_copy import PixelVault

def create_test_image(filename="test_image.png", size=(100, 100)):
    """Create a simple test image"""
    img_array = np.random.randint(0, 256, (size[1], size[0], 3), dtype=np.uint8)
    img = Image.fromarray(img_array)
    img.save(filename)
    print(f"✓ Created test image: {filename}")
    return filename

def test_basic_encoding():
    """Test basic encoding without password"""
    print("\n" + "="*60)
    print("TEST 1: Basic Encoding (No Password)")
    print("="*60)
    
    vault = PixelVault()
    img_path = create_test_image()
    message = "Hello, this is a test message!"
    output = "test_encoded_plain.png"
    
    # Encode
    success = vault.encode_message(img_path, message, output)
    
    # Decode
    if success:
        decoded = vault.decode_message(output)
        
        if decoded == message:
            print("✅ TEST PASSED: Message encoded and decoded successfully!")
        else:
            print("❌ TEST FAILED: Decoded message doesn't match!")
            print(f"Expected: {message}")
            print(f"Got: {decoded}")
    
    # Cleanup
    os.remove(img_path)
    if os.path.exists(output):
        os.remove(output)

def test_password_encoding():
    """Test encoding with password"""
    print("\n" + "="*60)
    print("TEST 2: Password-Protected Encoding")
    print("="*60)
    
    vault = PixelVault()
    img_path = create_test_image()
    message = "This is a secret message! 🔐"
    password = "SuperSecret123"
    output = "test_encoded_encrypted.png"
    
    # Encode with password
    success = vault.encode_message(img_path, message, output, password=password)
    
    # Decode with correct password
    if success:
        decoded = vault.decode_message(output, password=password)
        
        if decoded == message:
            print("✅ TEST PASSED: Encrypted message decoded successfully!")
        else:
            print("❌ TEST FAILED: Decoded message doesn't match!")
    
    # Cleanup
    os.remove(img_path)
    if os.path.exists(output):
        os.remove(output)

def test_wrong_password():
    """Test decoding with wrong password"""
    print("\n" + "="*60)
    print("TEST 3: Wrong Password Detection")
    print("="*60)
    
    vault = PixelVault()
    img_path = create_test_image()
    message = "Another secret!"
    correct_password = "RightPassword"
    wrong_password = "WrongPassword"
    output = "test_encoded_wrong_pass.png"
    
    # Encode with password
    vault.encode_message(img_path, message, output, password=correct_password)
    
    # Try to decode with wrong password
    print("\nTrying to decode with wrong password...")
    decoded = vault.decode_message(output, password=wrong_password)
    
    if decoded is None:
        print("✅ TEST PASSED: Wrong password correctly rejected!")
    else:
        print("❌ TEST FAILED: Wrong password was accepted!")
    
    # Cleanup
    os.remove(img_path)
    if os.path.exists(output):
        os.remove(output)

def test_no_password_on_encrypted():
    """Test decoding encrypted message without password"""
    print("\n" + "="*60)
    print("TEST 4: Missing Password Detection")
    print("="*60)
    
    vault = PixelVault()
    img_path = create_test_image()
    message = "Encrypted content"
    password = "MyPassword"
    output = "test_encoded_no_pass.png"
    
    # Encode with password
    vault.encode_message(img_path, message, output, password=password)
    
    # Try to decode without password
    print("\nTrying to decode encrypted message without password...")
    decoded = vault.decode_message(output)
    
    if decoded is None:
        print("✅ TEST PASSED: Missing password correctly detected!")
    else:
        print("❌ TEST FAILED: Encrypted message decoded without password!")
    
    # Cleanup
    os.remove(img_path)
    if os.path.exists(output):
        os.remove(output)

if __name__ == "__main__":
    print("\n" + "⭐"*30)
    print("PixelVault Layer 1 - Password Protection Tests")
    print("⭐"*30)
    
    try:
        test_basic_encoding()
        test_password_encoding()
        test_wrong_password()
        test_no_password_on_encrypted()
        
        print("\n" + "="*60)
        print("🎉 ALL TESTS COMPLETED!")
        print("="*60)
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()

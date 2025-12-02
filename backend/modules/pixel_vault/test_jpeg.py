"""
Test suite for JPEGVault - JPEG steganography module
Tests DCT-based encoding/decoding with and without encryption
"""

from PIL import Image
import numpy as np
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

try:
    from jpeg_vault import JPEGVault, JPEGIO_AVAILABLE
except ImportError as e:
    print(f"Error importing jpeg_vault: {e}")
    print("Make sure jpegio is installed: pip install jpegio")
    sys.exit(1)


def create_test_jpeg(filename="test_jpeg.jpg", size=(200, 200), quality=90):
    """Create a test JPEG image"""
    # Create random image
    img_array = np.random.randint(0, 256, (size[1], size[0], 3), dtype=np.uint8)
    img = Image.fromarray(img_array)
    img.save(filename, "JPEG", quality=quality)
    print(f" Created test JPEG: {filename}")
    return filename


def test_jpeg_capacity():
    """Test JPEG capacity calculation"""
    print("\n" + "="*60)
    print("TEST 1: JPEG Capacity Analysis")
    print("="*60)
    
    if not JPEGIO_AVAILABLE:
        print("  SKIPPED: jpegio not available")
        return False
    
    vault = JPEGVault()
    jpeg_path = create_test_jpeg()
    
    capacity = vault.get_capacity(jpeg_path)
    
    if 'error' not in capacity:
        print(f" Image size: {capacity['image_size']}")
        print(f" Total capacity: {capacity['total_bytes']} bytes")
        print(f" Usable capacity: {capacity['usable_bytes']} bytes")
        print(" TEST PASSED: Capacity calculated successfully!")
        
        # Cleanup
        os.remove(jpeg_path)
        return True
    else:
        print(f" Error: {capacity['error']}")
        os.remove(jpeg_path)
        return False


def test_jpeg_plain_encoding():
    """Test basic JPEG encoding without encryption"""
    print("\n" + "="*60)
    print("TEST 2: JPEG Plain Text Encoding")
    print("="*60)
    
    if not JPEGIO_AVAILABLE:
        print("  SKIPPED: jpegio not available")
        return False
    
    vault = JPEGVault()
    jpeg_path = create_test_jpeg(quality=95)
    message = "Hello from JPEG steganography!"
    output = "test_encoded_plain.jpg"
    
    # Encode
    result = vault.encode_message(jpeg_path, message, output)
    
    if result['success']:
        # Decode
        decode_result = vault.decode_message(output)
        
        if decode_result['success'] and decode_result['message'] == message:
            print(" TEST PASSED: Message encoded and decoded successfully!")
            
            # Cleanup
            os.remove(jpeg_path)
            os.remove(output)
            return True
        else:
            print(f" TEST FAILED: Decoding failed or message mismatch")
            print(f"Expected: {message}")
            print(f"Got: {decode_result.get('message', 'ERROR')}")
            os.remove(jpeg_path)
            if os.path.exists(output):
                os.remove(output)
            return False
    else:
        print(f" TEST FAILED: Encoding failed - {result['error']}")
        os.remove(jpeg_path)
        return False


def test_jpeg_encrypted_encoding():
    """Test JPEG encoding with password protection"""
    print("\n" + "="*60)
    print("TEST 3: JPEG Encrypted Encoding")
    print("="*60)
    
    if not JPEGIO_AVAILABLE:
        print("  SKIPPED: jpegio not available")
        return False
    
    vault = JPEGVault()
    jpeg_path = create_test_jpeg(quality=95)
    message = "Secret JPEG data! "
    password = "TestPass123"
    output = "test_encoded_encrypted.jpg"
    
    # Encode with password
    result = vault.encode_message(jpeg_path, message, output, password=password)
    
    if result['success']:
        # Decode with correct password
        decode_result = vault.decode_message(output, password=password)
        
        if decode_result['success'] and decode_result['message'] == message:
            print(" TEST PASSED: Encrypted JPEG message decoded successfully!")
            
            # Cleanup
            os.remove(jpeg_path)
            os.remove(output)
            return True
        else:
            print(f" TEST FAILED: Decryption failed")
            os.remove(jpeg_path)
            if os.path.exists(output):
                os.remove(output)
            return False
    else:
        print(f" TEST FAILED: Encoding failed - {result['error']}")
        os.remove(jpeg_path)
        return False


def test_jpeg_wrong_password():
    """Test wrong password detection"""
    print("\n" + "="*60)
    print("TEST 4: JPEG Wrong Password Detection")
    print("="*60)
    
    if not JPEGIO_AVAILABLE:
        print("  SKIPPED: jpegio not available")
        return False
    
    vault = JPEGVault()
    jpeg_path = create_test_jpeg(quality=95)
    message = "Protected message"
    correct_password = "RightPass"
    wrong_password = "WrongPass"
    output = "test_wrong_pass.jpg"
    
    # Encode with password
    vault.encode_message(jpeg_path, message, output, password=correct_password)
    
    # Try to decode with wrong password
    print("\nTrying to decode with wrong password...")
    decode_result = vault.decode_message(output, password=wrong_password)
    
    if not decode_result['success']:
        print(" TEST PASSED: Wrong password correctly rejected!")
        
        # Cleanup
        os.remove(jpeg_path)
        os.remove(output)
        return True
    else:
        print(" TEST FAILED: Wrong password was accepted!")
        os.remove(jpeg_path)
        os.remove(output)
        return False


def test_jpeg_capacity_limit():
    """Test message size limit detection"""
    print("\n" + "="*60)
    print("TEST 5: JPEG Capacity Limit")
    print("="*60)
    
    if not JPEGIO_AVAILABLE:
        print("  SKIPPED: jpegio not available")
        return False
    
    vault = JPEGVault()
    jpeg_path = create_test_jpeg(size=(50, 50), quality=90)  # Small image
    
    # Get capacity
    cap = vault.get_capacity(jpeg_path)
    
    if 'error' in cap:
        print(f" Error getting capacity: {cap['error']}")
        os.remove(jpeg_path)
        return False
    
    # Try to encode message larger than capacity
    huge_message = "X" * (cap['usable_bytes'] + 100)
    output = "test_overflow.jpg"
    
    print(f"\nImage capacity: {cap['usable_bytes']} bytes")
    print(f"Attempting message: {len(huge_message)} bytes")
    
    result = vault.encode_message(jpeg_path, huge_message, output)
    
    if not result['success'] and 'too large' in result['error'].lower():
        print(" TEST PASSED: Capacity limit correctly detected!")
        
        # Cleanup
        os.remove(jpeg_path)
        return True
    else:
        print(" TEST FAILED: Capacity limit not detected!")
        os.remove(jpeg_path)
        if os.path.exists(output):
            os.remove(output)
        return False


if __name__ == "__main__":
    print("JPEGVault - JPEG Steganography Tests")
    
    if not JPEGIO_AVAILABLE:
        print("\n jpegio library not installed!")
        print("Install with: pip install jpegio")
        print("\nNote: jpegio requires libjpeg development headers")
        print("Ubuntu/Debian: sudo apt-get install libjpeg-dev")
        print("macOS: brew install jpeg")
        sys.exit(1)
    
    tests = [
        test_jpeg_capacity,
        test_jpeg_plain_encoding,
        test_jpeg_encrypted_encoding,
        test_jpeg_wrong_password,
        test_jpeg_capacity_limit
    ]
    
    passed = 0
    failed = 0
    
    for test_func in tests:
        try:
            if test_func():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"\n TEST ERROR: {e}")
            import traceback
            traceback.print_exc()
            failed += 1
    
    print("\n" + "="*60)
    print(f" TEST SUMMARY: {passed} passed, {failed} failed")
    print("="*60)
    
    if failed == 0:
        print(" All tests passed!")
    else:
        print(f"  {failed} test(s) failed")

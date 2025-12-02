"""
PixelVault Demo Script
Demonstrates encoding and decoding messages
"""

from PIL import Image
import numpy as np


def create_sample_image(filename="sample_image.png", size=(800, 600)):
    """Create a sample image for testing"""
    # Create a gradient image for testing
    img_array = np.zeros((size[1], size[0], 3), dtype=np.uint8)
    
    for y in range(size[1]):
        for x in range(size[0]):
            img_array[y, x] = [
                int(255 * x / size[0]),  # Red gradient
                int(255 * y / size[1]),  # Green gradient
                128                       # Constant blue
            ]
    
    img = Image.fromarray(img_array)
    img.save(filename)
    print(f"✓ Sample image created: {filename}")
    return filename


def demo_basic_usage():
    """Demonstrate basic encoding and decoding"""
    from pixelvault_main import PixelVault
    
    print("\n" + "=" * 60)
    print("DEMO: Basic Steganography Usage")
    print("=" * 60)
    
    vault = PixelVault()
    
    # Create sample image
    print("\n1. Creating sample image...")
    sample_img = create_sample_image()
    
    # Encode a message
    print("\n2. Encoding secret message...")
    secret_message = "This is a secret message hidden in the image! "
    encoded_img = "encoded_image.png"
    
    success = vault.encode_message(sample_img, secret_message, encoded_img)
    
    if success:
        # Decode the message
        print("\n3. Decoding message from encoded image...")
        decoded_message = vault.decode_message(encoded_img)
        
        print("\n4. Verification:")
        print(f"   Original:  '{secret_message}'")
        print(f"   Decoded:   '{decoded_message}'")
        print(f"   Match:     {secret_message == decoded_message}")


def demo_capacity_check():
    """Demonstrate capacity checking"""
    from pixelvault_main import PixelVault
    
    print("\n" + "=" * 60)
    print("DEMO: Image Capacity Analysis")
    print("=" * 60)
    
    vault = PixelVault()
    
    # Test different image sizes
    sizes = [(100, 100), (500, 500), (1000, 1000), (1920, 1080)]
    
    print("\nImage Size      | Pixels    | Max Characters | Pages (A4)")
    print("-" * 60)
    
    for width, height in sizes:
        img_array = np.random.randint(0, 256, (height, width, 3), dtype=np.uint8)
        img = Image.fromarray(img_array)
        temp_file = f"temp_{width}x{height}.png"
        img.save(temp_file)
        
        capacity = vault.get_image_capacity(temp_file)
        pages = capacity / 3000  # Rough estimate: 3000 chars per page
        
        print(f"{width}x{height:<9} | {width*height:<9} | {capacity:<14} | ~{pages:.1f}")
        
        # Clean up
        import os
        os.remove(temp_file)


def demo_visual_comparison():
    """Create visual comparison of original vs encoded images"""
    from pixelvault_main import PixelVault
    
    print("\n" + "=" * 60)
    print("DEMO: Visual Comparison (Original vs Encoded)")
    print("=" * 60)
    
    vault = PixelVault()
    
    # Create a colorful test image
    print("\nCreating test image with color patterns...")
    img_array = np.zeros((400, 600, 3), dtype=np.uint8)
    
    # Create colored sections
    img_array[:200, :300] = [255, 0, 0]    # Red
    img_array[:200, 300:] = [0, 255, 0]    # Green
    img_array[200:, :300] = [0, 0, 255]    # Blue
    img_array[200:, 300:] = [255, 255, 0]  # Yellow
    
    original = Image.fromarray(img_array)
    original.save("original.png")
    
    # Encode a long message
    long_message = "A" * 1000  # 1000 characters
    vault.encode_message("original.png", long_message, "encoded_comparison.png")
    
    print("\n✓ Files created:")
    print("  - original.png (original image)")
    print("  - encoded_comparison.png (with hidden message)")
    print("\nNote: The images should look nearly identical to the human eye!")
    print("The differences are in the least significant bits only.")


def demo_error_handling():
    """Demonstrate error handling"""
    from pixelvault_main import PixelVault
    
    print("\n" + "=" * 60)
    print("DEMO: Error Handling")
    print("=" * 60)
    
    vault = PixelVault()
    
    print("\n1. Testing with non-existent file...")
    vault.decode_message("nonexistent.png")
    
    print("\n2. Testing message too large for image...")
    # Create tiny image
    tiny_img = np.ones((10, 10, 3), dtype=np.uint8) * 128
    Image.fromarray(tiny_img).save("tiny.png")
    
    huge_message = "X" * 1000
    vault.encode_message("tiny.png", huge_message, "output.png")
    
    # Clean up
    import os
    os.remove("tiny.png")


def run_all_demos():
    """Run all demonstration scripts"""
    print("=" * 60)
    print("         PixelVault Complete Demonstration")
    print("=" * 60)
    
    demos = [
        ("Basic Usage", demo_basic_usage),
        ("Capacity Check", demo_capacity_check),
        ("Visual Comparison", demo_visual_comparison),
        ("Error Handling", demo_error_handling)
    ]
    
    for name, demo_func in demos:
        try:
            demo_func()
            input(f"\nPress Enter to continue to next demo...")
        except KeyboardInterrupt:
            print("\n\nDemo interrupted by user.")
            break
        except Exception as e:
            print(f"\nError in {name} demo: {e}")
    
    print("\n" + "=" * 60)
    print("All demos completed!")
    print("=" * 60)


if __name__ == "__main__":
    run_all_demos()
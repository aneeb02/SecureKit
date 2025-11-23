"""
PixelVault: Steganography-based Security Module
Hides and retrieves secret messages within images using LSB technique
"""

from PIL import Image
import numpy as np
import os


class PixelVault:
    """Main class for encoding and decoding messages in images"""
    
    def __init__(self):
        self.delimiter = "<<END>>"  # Marks the end of hidden message
        
    def text_to_binary(self, text):
        """Convert text to binary string"""
        binary = ''.join(format(ord(char), '08b') for char in text)
        return binary
    
    def binary_to_text(self, binary):
        """Convert binary string back to text"""
        text = ''
        for i in range(0, len(binary), 8):
            byte = binary[i:i+8]
            if len(byte) == 8:
                text += chr(int(byte, 2))
        return text
    
    def encode_message(self, image_path, message, output_path):
        """
        Encode a secret message into an image
        
        Args:
            image_path: Path to the cover image
            message: Secret message to hide
            output_path: Path to save the encoded image
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Load image
            img = Image.open(image_path)
            img = img.convert('RGB')  # Ensure RGB format
            img_array = np.array(img)
            
            # Add delimiter to know where message ends
            full_message = message + self.delimiter
            binary_message = self.text_to_binary(full_message)
            
            # Check if image can hold the message
            max_bytes = img_array.shape[0] * img_array.shape[1] * 3  # RGB channels
            required_bytes = len(binary_message)
            
            if required_bytes > max_bytes:
                print(f"Error: Message too large for this image!")
                print(f"Image can hold {max_bytes} bits, message needs {required_bytes} bits")
                return False
            
            # Flatten image array for easier manipulation
            flat_img = img_array.flatten()
            
            # Encode message into LSBs
            data_index = 0
            for i in range(len(binary_message)):
                # Modify LSB of pixel value
                flat_img[i] = (flat_img[i] & 0xFE) | int(binary_message[i])
            
            # Reshape back to original dimensions
            encoded_array = flat_img.reshape(img_array.shape)
            
            # Save encoded image
            encoded_img = Image.fromarray(encoded_array.astype('uint8'))
            encoded_img.save(output_path, 'PNG')  # Use PNG to avoid lossy compression
            
            print(f"✓ Message successfully encoded!")
            print(f"✓ Encoded image saved to: {output_path}")
            print(f"✓ Message length: {len(message)} characters")
            print(f"✓ Bits used: {len(binary_message)} / {max_bytes}")
            
            return True
            
        except FileNotFoundError:
            print(f"Error: Image file '{image_path}' not found!")
            return False
        except Exception as e:
            print(f"Error encoding message: {e}")
            return False
    
    def decode_message(self, image_path):
        """
        Decode a hidden message from an image
        
        Args:
            image_path: Path to the encoded image
            
        Returns:
            str: The hidden message, or None if decoding fails
        """
        try:
            # Load image
            img = Image.open(image_path)
            img = img.convert('RGB')
            img_array = np.array(img)
            
            # Flatten image array
            flat_img = img_array.flatten()
            
            # Extract LSBs
            binary_message = ''
            for pixel_value in flat_img:
                binary_message += str(pixel_value & 1)  # Get LSB
            
            # Convert binary to text in chunks
            message = ''
            for i in range(0, len(binary_message), 8):
                byte = binary_message[i:i+8]
                if len(byte) == 8:
                    char = chr(int(byte, 2))
                    message += char
                    
                    # Check if we've reached the delimiter
                    if message.endswith(self.delimiter):
                        # Remove delimiter and return message
                        message = message[:-len(self.delimiter)]
                        print(f"✓ Message successfully decoded!")
                        print(f"✓ Message length: {len(message)} characters")
                        return message
            
            print("Warning: No valid message found or delimiter missing")
            return None
            
        except FileNotFoundError:
            print(f"Error: Image file '{image_path}' not found!")
            return None
        except Exception as e:
            print(f"Error decoding message: {e}")
            return None
    
    def get_image_capacity(self, image_path):
        """
        Calculate how many characters can be hidden in an image
        
        Args:
            image_path: Path to the image
            
        Returns:
            int: Maximum characters that can be hidden
        """
        try:
            img = Image.open(image_path)
            img_array = np.array(img)
            
            # Each pixel has 3 channels (RGB), each can hold 1 bit
            # Each character needs 8 bits
            total_bits = img_array.shape[0] * img_array.shape[1] * 3
            max_chars = (total_bits // 8) - len(self.delimiter)
            
            return max_chars
        except Exception as e:
            print(f"Error calculating capacity: {e}")
            return 0


def main():
    """Main function with interactive menu"""
    vault = PixelVault()
    
    print("=" * 60)
    print("           PixelVault - Steganography Security Tool")
    print("=" * 60)
    print()
    
    while True:
        print("\nOptions:")
        print("1. Encode a message into an image")
        print("2. Decode a message from an image")
        print("3. Check image capacity")
        print("4. Exit")
        print()
        
        choice = input("Select an option (1-4): ").strip()
        
        if choice == '1':
            print("\n--- Encode Message ---")
            image_path = input("Enter cover image path: ").strip()
            
            if not os.path.exists(image_path):
                print("Error: Image file not found!")
                continue
            
            # Check capacity first
            capacity = vault.get_image_capacity(image_path)
            print(f"This image can hide up to {capacity} characters")
            
            message = input("Enter secret message: ").strip()
            
            if len(message) > capacity:
                print(f"Error: Message too long! Maximum is {capacity} characters")
                continue
            
            output_path = input("Enter output image path (e.g., encoded.png): ").strip()
            
            vault.encode_message(image_path, message, output_path)
            
        elif choice == '2':
            print("\n--- Decode Message ---")
            image_path = input("Enter encoded image path: ").strip()
            
            message = vault.decode_message(image_path)
            
            if message:
                print("\n" + "=" * 60)
                print("Hidden Message:")
                print("-" * 60)
                print(message)
                print("=" * 60)
            
        elif choice == '3':
            print("\n--- Check Image Capacity ---")
            image_path = input("Enter image path: ").strip()
            
            capacity = vault.get_image_capacity(image_path)
            if capacity > 0:
                print(f"\n✓ This image can hide up to {capacity} characters")
                print(f"✓ Approximately {capacity // 100} average sentences")
            
        elif choice == '4':
            print("\nExiting PixelVault. Stay secure! 🔒")
            break
            
        else:
            print("Invalid option. Please try again.")


if __name__ == "__main__":
    main()
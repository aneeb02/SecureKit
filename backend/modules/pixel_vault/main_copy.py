"""
PixelVault: Steganography-based Security Module
Hides and retrieves secret messages within images using LSB technique
Extended with Layer 1: Password Protection (AES-256 encryption)
"""

from PIL import Image
import numpy as np
import os
import secrets
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import padding, hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC


class PixelVault:
    """Main class for encoding and decoding messages in images with optional encryption"""
    
    def __init__(self):
        self.delimiter = "<<END>>"  # Marks the end of hidden message
        self.version = "1.0"  # Version tracking
        
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
    
    # ==================== Security Layer (Layer 1) ====================
    
    def _derive_key(self, password, salt):
        """
        Derive encryption key from password using PBKDF2
        
        Args:
            password: User password (string)
            salt: Random salt bytes (16 bytes)
            
        Returns:
            bytes: 32-byte encryption key for AES-256
        """
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),  # Use SHA-256 hash
            length=32,  # 256-bit key for AES-256
            salt=salt,
            iterations=100000,  # OWASP recommended minimum
            backend=default_backend()
        )
        return kdf.derive(password.encode())
    
    def _encrypt(self, data, password):
        """
        Encrypt data using AES-256-CBC
        
        Args:
            data: Data to encrypt (bytes)
            password: Password for encryption (string)
            
        Returns:
            bytes: Encrypted data with salt and IV prepended
        """
        # Generate random salt (16 bytes) and IV (16 bytes)
        salt = secrets.token_bytes(16)
        iv = secrets.token_bytes(16)
        
        # Derive encryption key from password
        key = self._derive_key(password, salt)
        
        # Pad data to AES block size (16 bytes / 128 bits)
        padder = padding.PKCS7(128).padder()
        padded_data = padder.update(data) + padder.finalize()
        
        # Encrypt using AES-256-CBC
        cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
        encryptor = cipher.encryptor()
        encrypted = encryptor.update(padded_data) + encryptor.finalize()
        
        # Return: [salt(16)] + [iv(16)] + [encrypted_data]
        return salt + iv + encrypted
    
    def _decrypt(self, encrypted_data, password):
        """
        Decrypt data using AES-256-CBC
        
        Args:
            encrypted_data: Encrypted data with salt and IV prepended (bytes)
            password: Password for decryption (string)
            
        Returns:
            bytes: Decrypted data
        """
        # Extract salt (first 16 bytes) and IV (next 16 bytes)
        salt = encrypted_data[:16]
        iv = encrypted_data[16:32]
        encrypted = encrypted_data[32:]
        
        # Derive the same key from password
        key = self._derive_key(password, salt)
        
        # Decrypt using AES-256-CBC
        cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
        decryptor = cipher.decryptor()
        padded_data = decryptor.update(encrypted) + decryptor.finalize()
        
        # Remove padding
        unpadder = padding.PKCS7(128).unpadder()
        data = unpadder.update(padded_data) + unpadder.finalize()
        
        return data
    
    # ==================== Metadata Layer ====================
    
    def _create_metadata(self, encrypted):
        """
        Create metadata header to track encoding options
        
        Args:
            encrypted: Whether data is encrypted (bool)
            
        Returns:
            str: Metadata string (e.g., "PV:1.0:E|" or "PV:1.0:P|")
        """
        flag = "E" if encrypted else "P"  # E=Encrypted, P=Plain
        return f"PV:{self.version}:{flag}|"
    
    def _parse_metadata(self, data_str):
        """
        Parse metadata header from decoded data
        
        Args:
            data_str: Decoded data string
            
        Returns:
            dict: {encrypted: bool, message: str} or None if no metadata
        """
        if data_str.startswith("PV:"):
            try:
                # Format: "PV:1.0:E|message" or "PV:1.0:P|message"
                parts = data_str.split('|', 1)
                if len(parts) == 2:
                    header = parts[0]  # "PV:1.0:E"
                    message = parts[1]  # Actual message
                    
                    flag = header.split(':')[2]  # Extract flag
                    encrypted = (flag == "E")
                    
                    return {'encrypted': encrypted, 'message': message}
            except:
                pass
        return None
    
    # ==================== Core LSB Methods ====================
    
    def encode_message(self, image_path, message, output_path, password=None):
        """
        Encode a secret message into an image with optional password protection
        
        Args:
            image_path: Path to the cover image
            message: Secret message to hide
            output_path: Path to save the encoded image
            password: Optional password for AES-256 encryption
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Load image
            img = Image.open(image_path)
            img = img.convert('RGB')  # Ensure RGB format
            img_array = np.array(img)
            
            # Prepare data: convert message to bytes
            data = message.encode('utf-8')
            
            # Encrypt if password provided
            if password:
                data = self._encrypt(data, password)
                print(f"🔐 Message encrypted with AES-256")
            
            # Add metadata header
            metadata = self._create_metadata(encrypted=bool(password))
            full_message = metadata + data.decode('latin1') + self.delimiter
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
    
    def decode_message(self, image_path, password=None):
        """
        Decode a hidden message from an image with optional decryption
        
        Args:
            image_path: Path to the encoded image
            password: Optional password if message was encrypted
            
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
                        # Remove delimiter
                        message = message[:-len(self.delimiter)]
                        
                        # Parse metadata
                        metadata = self._parse_metadata(message)
                        
                        if metadata:
                            # Has metadata - extract actual message
                            message_data = metadata['message']
                            is_encrypted = metadata['encrypted']
                            
                            if is_encrypted:
                                if password is None:
                                    print("❌ Error: This message is encrypted. Password required!")
                                    return None
                                
                                try:
                                    # Decrypt the message
                                    encrypted_bytes = message_data.encode('latin1')
                                    decrypted_bytes = self._decrypt(encrypted_bytes, password)
                                    message = decrypted_bytes.decode('utf-8')
                                    print(f"🔓 Message decrypted successfully")
                                except Exception as e:
                                    print(f"❌ Decryption failed: Wrong password or corrupted data")
                                    return None
                            else:
                                # Plain text message
                                message = message_data.encode('latin1').decode('utf-8')
                        
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
    print("     PixelVault - Steganography Security Tool")
    print("     Layer 1: Password Protection Enabled")
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
            
            # Ask for password protection
            use_password = input("Encrypt with password? (y/n): ").strip().lower() == 'y'
            password = None
            if use_password:
                password = input("Enter password: ").strip()
                if not password:
                    print("Warning: Empty password, encoding without encryption")
                    password = None
            
            output_path = input("Enter output image path (e.g., encoded.png): ").strip()
            
            vault.encode_message(image_path, message, output_path, password=password)
            
        elif choice == '2':
            print("\n--- Decode Message ---")
            image_path = input("Enter encoded image path: ").strip()
            
            # Ask if password protected
            use_password = input("Is message password-protected? (y/n): ").strip().lower() == 'y'
            password = None
            if use_password:
                password = input("Enter password: ").strip()
            
            message = vault.decode_message(image_path, password=password)
            
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

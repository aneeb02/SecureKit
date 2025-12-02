"""
JPEGVault: JPEG-specific Steganography Module
Hides and retrieves secret messages within JPEG images using DCT coefficient modification
Works with Layer 1 encryption from PixelVault
"""

import numpy as np
import os
import secrets
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import padding, hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

try:
    import jpegio as jio
    JPEGIO_AVAILABLE = True
except ImportError:
    JPEGIO_AVAILABLE = False
    print("Warning: jpegio not installed. JPEG steganography unavailable.")
    print("Install with: pip install jpegio")


class JPEGVault:
    """JPEG steganography using DCT coefficient modification"""
    
    def __init__(self):
        self.delimiter = "<<JPEG_END>>"
        self.version = "1.0"
        
        if not JPEGIO_AVAILABLE:
            raise ImportError("jpegio library required. Install with: pip install jpegio")
    
    # ==================== Security Layer (Reused from PixelVault) ====================
    
    def _derive_key(self, password, salt):
        """Derive encryption key from password using PBKDF2"""
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
            backend=default_backend()
        )
        return kdf.derive(password.encode())
    
    def _encrypt(self, data, password):
        """Encrypt data using AES-256-CBC"""
        salt = secrets.token_bytes(16)
        iv = secrets.token_bytes(16)
        key = self._derive_key(password, salt)
        
        padder = padding.PKCS7(128).padder()
        padded_data = padder.update(data) + padder.finalize()
        
        cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
        encryptor = cipher.encryptor()
        encrypted = encryptor.update(padded_data) + encryptor.finalize()
        
        return salt + iv + encrypted
    
    def _decrypt(self, encrypted_data, password):
        """Decrypt data using AES-256-CBC"""
        salt = encrypted_data[:16]
        iv = encrypted_data[16:32]
        encrypted = encrypted_data[32:]
        
        key = self._derive_key(password, salt)
        
        cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
        decryptor = cipher.decryptor()
        padded_data = decryptor.update(encrypted) + decryptor.finalize()
        
        unpadder = padding.PKCS7(128).unpadder()
        data = unpadder.update(padded_data) + unpadder.finalize()
        
        return data
    
    # ==================== Metadata Layer ====================
    
    def _create_metadata(self, encrypted):
        """Create metadata header"""
        flag = "E" if encrypted else "P"
        return f"JPG:{self.version}:{flag}|"
    
    def _parse_metadata(self, data_bytes):
        """Parse metadata from decoded bytes"""
        try:
            data_str = data_bytes.decode('utf-8', errors='ignore')
            if data_str.startswith("JPG:"):
                parts = data_str.split('|', 1)
                if len(parts) == 2:
                    header = parts[0]
                    message = parts[1]
                    flag = header.split(':')[2]
                    encrypted = (flag == "E")
                    return {'encrypted': encrypted, 'message': message.encode('utf-8')}
        except:
            pass
        return None
    
    # ==================== DCT Coefficient Methods ====================
    
    def _get_embeddable_coefficients(self, dct_array):
        """
        Get list of non-zero DCT coefficients that can hold data
        
        Returns:
            list of (block_row, block_col, coef_row, coef_col, value) tuples
        """
        embeddable = []
        
        # Iterate through 8x8 DCT blocks
        block_h, block_w = dct_array.shape[0] // 8, dct_array.shape[1] // 8
        
        for block_y in range(block_h):
            for block_x in range(block_w):
                # Get 8x8 block
                block = dct_array[block_y*8:(block_y+1)*8, block_x*8:(block_x+1)*8]
                
                # Skip DC coefficient (top-left), use AC coefficients
                for i in range(8):
                    for j in range(8):
                        if i == 0 and j == 0:  # Skip DC coefficient
                            continue
                        
                        coef = block[i, j]
                        if coef != 0:  # Only use non-zero coefficients
                            embeddable.append((block_y, block_x, i, j, coef))
        
        return embeddable
    
    def _embed_in_dct(self, dct_array, binary_data):
        """Embed binary data in DCT coefficients"""
        embeddable = self._get_embeddable_coefficients(dct_array)
        
        if len(binary_data) > len(embeddable):
            raise ValueError(f"Message too large! Can embed {len(embeddable)} bits, need {len(binary_data)}")
        
        # Modify LSB of coefficients
        for bit_idx, bit in enumerate(binary_data):
            block_y, block_x, coef_y, coef_x, _ = embeddable[bit_idx]
            
            # Calculate absolute position
            abs_y = block_y * 8 + coef_y
            abs_x = block_x * 8 + coef_x
            
            # Modify LSB
            current = dct_array[abs_y, abs_x]
            dct_array[abs_y, abs_x] = (current & ~1) | int(bit)
        
        return dct_array
    
    def _extract_from_dct(self, dct_array, num_bits):
        """Extract binary data from DCT coefficients"""
        embeddable = self._get_embeddable_coefficients(dct_array)
        
        if num_bits > len(embeddable):
            num_bits = len(embeddable)
        
        binary_data = ''
        for i in range(num_bits):
            block_y, block_x, coef_y, coef_x, _ = embeddable[i]
            abs_y = block_y * 8 + coef_y
            abs_x = block_x * 8 + coef_x
            binary_data += str(dct_array[abs_y, abs_x] & 1)
        
        return binary_data
    
    # ==================== Main Encode/Decode Methods ====================
    
    def encode_message(self, jpeg_path, message, output_path, password=None):
        """
        Encode a message into a JPEG image using DCT coefficients
        
        Args:
            jpeg_path: Path to input JPEG image
            message: Secret message to hide
            output_path: Path to save encoded JPEG
            password: Optional password for encryption
            
        Returns:
            dict: Status and metadata
        """
        try:
            # Read JPEG and get DCT coefficients
            jpeg_obj = jio.read(jpeg_path)
            
            # Use Y (luminance) component - most robust
            dct_y = jpeg_obj.coef_arrays[0].copy()
            
            # Prepare message
            data = message.encode('utf-8')
            
            if password:
                data = self._encrypt(data, password)
                print("Message encrypted with AES-256")
            
            # Add metadata and delimiter
            metadata = self._create_metadata(encrypted=bool(password))
            full_data = (metadata.encode('utf-8') + data + 
                        self.delimiter.encode('utf-8'))
            
            # Convert to binary
            binary = ''.join(format(byte, '08b') for byte in full_data)
            
            # Calculate capacity
            embeddable_coeffs = self._get_embeddable_coefficients(dct_y)
            capacity_bits = len(embeddable_coeffs)
            capacity_bytes = capacity_bits // 8
            
            print(f"JPEG Capacity is: {capacity_bytes} bytes ({capacity_bits} bits)")
            print(f"Message size is: {len(full_data)} bytes ({len(binary)} bits)")
            
            if len(binary) > capacity_bits:
                return {
                    'success': False,
                    'error': f'Message too large! Capacity: {capacity_bytes} bytes, needed: {len(full_data)} bytes'
                }
            
            # Embed data in DCT coefficients
            dct_y = self._embed_in_dct(dct_y, binary)
            
            # Write modified DCT back
            jpeg_obj.coef_arrays[0] = dct_y
            jio.write(jpeg_obj, output_path)
            
            print(f" Message successfully encoded in JPEG!")
            print(f" Output: {output_path}")
            print(f" Capacity used: {len(binary)/capacity_bits*100:.1f}%")
            
            return {
                'success': True,
                'output': output_path,
                'message_size': len(message),
                'encoded_size': len(full_data),
                'capacity_used': f"{len(binary)/capacity_bits*100:.1f}%",
                'encrypted': bool(password)
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def decode_message(self, jpeg_path, password=None):
        """
        Decode a message from a JPEG image
        
        Args:
            jpeg_path: Path to encoded JPEG image
            password: Optional password for decryption
            
        Returns:
            dict: Status and decoded message
        """
        try:
            # Read JPEG DCT coefficients
            jpeg_obj = jio.read(jpeg_path)
            dct_y = jpeg_obj.coef_arrays[0]
            
            # Extract all possible bits
            capacity = len(self._get_embeddable_coefficients(dct_y))
            binary = self._extract_from_dct(dct_y, capacity)
            
            # Convert to bytes
            all_bytes = bytearray()
            for i in range(0, len(binary), 8):
                if i + 8 <= len(binary):
                    all_bytes.append(int(binary[i:i+8], 2))
            
            # Find delimiter
            delimiter_bytes = self.delimiter.encode('utf-8')
            if delimiter_bytes not in all_bytes:
                return {'success': False, 'error': 'No valid message found (delimiter missing)'}
            
            # Extract message up to delimiter
            delimiter_pos = all_bytes.find(delimiter_bytes)
            message_bytes = bytes(all_bytes[:delimiter_pos])
            
            # Parse metadata
            metadata = self._parse_metadata(message_bytes)
            
            if metadata:
                is_encrypted = metadata['encrypted']
                data = metadata['message']
                
                # Remove metadata header from data
                # Format: "JPG:1.0:E|actual_data"
                header_end = message_bytes.find(b'|') + 1
                data = message_bytes[header_end:delimiter_pos]
                
                if is_encrypted:
                    if password is None:
                        print("Error: Message is encrypted. Password required!")
                        return {'success': False, 'error': 'Password required'}
                    
                    try:
                        data = self._decrypt(data, password)
                        print("Message decrypted successfully")
                    except Exception as e:
                        print("Decryption failed: Wrong password or corrupted data")
                        return {'success': False, 'error': 'Decryption failed'}
                
                message = data.decode('utf-8')
            else:
                # No metadata - treat as raw message
                message = message_bytes.decode('utf-8', errors='ignore')
            
            print(f" Message decoded from JPEG!")
            print(f" Length: {len(message)} characters")
            
            return {
                'success': True,
                'message': message,
                'length': len(message),
                'encrypted': metadata['encrypted'] if metadata else False
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def get_capacity(self, jpeg_path):
        """
        Calculate how much data can be hidden in a JPEG
        
        Returns:
            dict: Capacity information
        """
        try:
            jpeg_obj = jio.read(jpeg_path)
            dct_y = jpeg_obj.coef_arrays[0]
            
            embeddable = self._get_embeddable_coefficients(dct_y)
            capacity_bits = len(embeddable)
            capacity_bytes = capacity_bits // 8
            
            # Account for metadata and delimiter overhead
            overhead = len(self._create_metadata(False).encode()) + len(self.delimiter.encode())
            usable_bytes = capacity_bytes - overhead
            
            return {
                'total_bits': capacity_bits,
                'total_bytes': capacity_bytes,
                'usable_bytes': usable_bytes,
                'overhead_bytes': overhead,
                'image_size': f"{dct_y.shape[1]}x{dct_y.shape[0]}"
            }
            
        except Exception as e:
            return {'error': str(e)}
            


def main():
    """Interactive CLI for JPEG steganography"""
    vault = JPEGVault()
    
    print("=" * 60)
    print("     JPEGVault - JPEG Steganography Tool")
    print("     DCT Coefficient Modification")
    print("=" * 60)
    print()
    
    while True:
        print("\nOptions:")
        print("1. Encode message in JPEG")
        print("2. Decode message from JPEG")
        print("3. Check JPEG capacity")
        print("4. Exit")
        print()
        
        choice = input("Select option (1-4): ").strip()
        
        if choice == '1':
            print("\n--- Encode Message ---")
            jpeg_path = input("JPEG image path: ").strip()
            
            if not os.path.exists(jpeg_path):
                print("Error: File not found!")
                continue
            
            # Check capacity
            cap = vault.get_capacity(jpeg_path)
            if 'error' in cap:
                print(f"Error: {cap['error']}")
                continue
            
            print(f"JPEG capacity: {cap['usable_bytes']} usable bytes")
            
            message = input("Secret message: ").strip()
            
            use_password = input("Encrypt with password? (y/n): ").strip().lower() == 'y'
            password = None
            if use_password:
                password = input("Password: ").strip()
            
            output = input("Output JPEG path: ").strip()
            
            result = vault.encode_message(jpeg_path, message, output, password)
            if not result['success']:
                print(f"Error: {result['error']}")
        
        elif choice == '2':
            print("\n--- Decode Message ---")
            jpeg_path = input("Encoded JPEG path: ").strip()
            
            use_password = input("Password-protected? (y/n): ").strip().lower() == 'y'
            password = None
            if use_password:
                password = input("Password: ").strip()
            
            result = vault.decode_message(jpeg_path, password)
            
            if result['success']:
                print("\n" + "=" * 60)
                print("Hidden Message:")
                print("-" * 60)
                print(result['message'])
                print("=" * 60)
            else:
                print(f"Error: {result['error']}")
        
        elif choice == '3':
            print("\n--- Check Capacity ---")
            jpeg_path = input("JPEG path: ").strip()
            
            cap = vault.get_capacity(jpeg_path)
            if 'error' not in cap:
                print(f"\n JPEG Analysis:")
                print(f"  Image size: {cap['image_size']}")
                print(f"  Total capacity: {cap['total_bytes']} bytes")
                print(f"  Usable capacity: {cap['usable_bytes']} bytes")
                print(f"  Overhead: {cap['overhead_bytes']} bytes")
            else:
                print(f"Error: {cap['error']}")
        
        elif choice == '4':
            print("\nExiting JPEGVault. Stay secure! ")
            break
        
        else:
            print("Invalid option!")


if __name__ == "__main__":
    main()

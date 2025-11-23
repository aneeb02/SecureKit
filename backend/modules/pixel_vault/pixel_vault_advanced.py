"""
PixelVault Enhanced: Advanced Steganography Security Module
Features: Encryption, Compression, File Hiding, Multiple Methods
"""

from PIL import Image
import numpy as np
import os
import hashlib
import zlib
import base64
import secrets
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC


class PixelVaultEnhanced:
    """Enhanced steganography with encryption and advanced features"""
    
    def __init__(self):
        self.delimiter = "<<PIXELVAULT_END>>"
        self.file_header = "<<PIXELVAULT_FILE>>"
        self.version = "2.0"
        
    # ==================== Encryption Methods ====================
    
    def _derive_key(self, password, salt):
        """Derive encryption key from password using PBKDF2"""
        kdf = PBKDF2HMAC(
            algorithm=hashlib.sha256(),
            length=32,
            salt=salt,
            iterations=100000,
            backend=default_backend()
        )
        return kdf.derive(password.encode())
    
    def encrypt_data(self, data, password):
        """
        Encrypt data using AES-256-CBC
        
        Args:
            data: Data to encrypt (bytes)
            password: Password for encryption
            
        Returns:
            bytes: Encrypted data with salt and IV prepended
        """
        # Generate random salt and IV
        salt = secrets.token_bytes(16)
        iv = secrets.token_bytes(16)
        
        # Derive key from password
        key = self._derive_key(password, salt)
        
        # Pad data to AES block size (16 bytes)
        padder = padding.PKCS7(128).padder()
        padded_data = padder.update(data) + padder.finalize()
        
        # Encrypt
        cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
        encryptor = cipher.encryptor()
        encrypted = encryptor.update(padded_data) + encryptor.finalize()
        
        # Prepend salt and IV to encrypted data
        return salt + iv + encrypted
    
    def decrypt_data(self, encrypted_data, password):
        """
        Decrypt data using AES-256-CBC
        
        Args:
            encrypted_data: Encrypted data with salt and IV
            password: Password for decryption
            
        Returns:
            bytes: Decrypted data
        """
        # Extract salt, IV, and encrypted data
        salt = encrypted_data[:16]
        iv = encrypted_data[16:32]
        encrypted = encrypted_data[32:]
        
        # Derive key from password
        key = self._derive_key(password, salt)
        
        # Decrypt
        cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
        decryptor = cipher.decryptor()
        padded_data = decryptor.update(encrypted) + decryptor.finalize()
        
        # Unpad
        unpadder = padding.PKCS7(128).unpadder()
        data = unpadder.update(padded_data) + unpadder.finalize()
        
        return data
    
    # ==================== Compression Methods ====================
    
    def compress_data(self, data):
        """Compress data using zlib"""
        return zlib.compress(data, level=9)
    
    def decompress_data(self, compressed_data):
        """Decompress data using zlib"""
        return zlib.decompress(compressed_data)
    
    # ==================== Encoding Methods ====================
    
    def encode_lsb_sequential(self, image_array, data_bits):
        """Standard LSB encoding (sequential)"""
        flat_img = image_array.flatten().copy()
        
        for i in range(len(data_bits)):
            flat_img[i] = (flat_img[i] & 0xFE) | int(data_bits[i])
        
        return flat_img.reshape(image_array.shape)
    
    def encode_lsb_random(self, image_array, data_bits, seed):
        """LSB encoding with pseudo-random positioning"""
        flat_img = image_array.flatten().copy()
        
        # Generate pseudo-random indices
        np.random.seed(seed)
        indices = np.random.permutation(len(flat_img))[:len(data_bits)]
        
        for i, idx in enumerate(indices):
            flat_img[idx] = (flat_img[idx] & 0xFE) | int(data_bits[i])
        
        return flat_img.reshape(image_array.shape)
    
    def decode_lsb_sequential(self, image_array, num_bits):
        """Standard LSB decoding (sequential)"""
        flat_img = image_array.flatten()
        bits = ''.join(str(flat_img[i] & 1) for i in range(num_bits))
        return bits
    
    def decode_lsb_random(self, image_array, num_bits, seed):
        """LSB decoding with pseudo-random positioning"""
        flat_img = image_array.flatten()
        
        # Generate same pseudo-random indices
        np.random.seed(seed)
        indices = np.random.permutation(len(flat_img))[:num_bits]
        
        bits = ''.join(str(flat_img[idx] & 1) for idx in indices)
        return bits
    
    # ==================== Main Encode/Decode Methods ====================
    
    def encode_message(self, image_path, message, output_path, password=None, 
                      compress=True, method='sequential', seed=None):
        """
        Enhanced message encoding with encryption and compression
        
        Args:
            image_path: Path to cover image
            message: Secret message to hide
            output_path: Path to save encoded image
            password: Optional password for encryption
            compress: Whether to compress the message
            method: 'sequential' or 'random' encoding
            seed: Seed for random method (auto-generated if None)
            
        Returns:
            dict: Status and metadata
        """
        try:
            # Load image
            img = Image.open(image_path).convert('RGB')
            img_array = np.array(img)
            
            # Prepare data
            data = message.encode('utf-8')
            
            # Compress if requested
            if compress:
                data = self.compress_data(data)
                print(f"✓ Compressed: {len(message.encode())} → {len(data)} bytes")
            
            # Encrypt if password provided
            if password:
                data = self.encrypt_data(data, password)
                print(f"✓ Encrypted with AES-256")
            
            # Add metadata header
            metadata = f"v{self.version}|c{int(compress)}|e{int(bool(password))}|"
            if method == 'random':
                seed = seed or secrets.randbelow(2**31)
                metadata += f"r{seed}|"
            else:
                metadata += "s|"
            
            full_data = metadata.encode() + b'|DATA|' + data + self.delimiter.encode()
            
            # Convert to binary
            data_bits = ''.join(format(byte, '08b') for byte in full_data)
            
            # Check capacity
            max_bits = img_array.size
            if len(data_bits) > max_bits:
                return {
                    'success': False,
                    'error': f'Message too large: {len(data_bits)} bits needed, {max_bits} available'
                }
            
            # Encode based on method
            if method == 'random':
                encoded_array = self.encode_lsb_random(img_array, data_bits, seed)
            else:
                encoded_array = self.encode_lsb_sequential(img_array, data_bits)
            
            # Save
            encoded_img = Image.fromarray(encoded_array.astype('uint8'))
            encoded_img.save(output_path, 'PNG')
            
            result = {
                'success': True,
                'output': output_path,
                'original_size': len(message),
                'encoded_size': len(data),
                'bits_used': len(data_bits),
                'capacity_used': f"{100 * len(data_bits) / max_bits:.2f}%",
                'encrypted': bool(password),
                'compressed': compress,
                'method': method
            }
            
            if method == 'random':
                result['seed'] = seed
                print(f"⚠️  SAVE THIS SEED: {seed} (required for decoding!)")
            
            return result
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def decode_message(self, image_path, password=None, seed=None):
        """
        Enhanced message decoding with decryption and decompression
        
        Args:
            image_path: Path to encoded image
            password: Password if encrypted
            seed: Seed if random method used
            
        Returns:
            dict: Status and decoded message
        """
        try:
            # Load image
            img = Image.open(image_path).convert('RGB')
            img_array = np.array(img)
            
            # Try to read metadata (first 1000 bits should contain it)
            initial_bits = self.decode_lsb_sequential(img_array, 1000)
            
            # Convert to bytes to find metadata
            initial_bytes = bytes(int(initial_bits[i:i+8], 2) for i in range(0, len(initial_bits), 8))
            
            # Parse metadata
            try:
                metadata_str = initial_bytes.decode('utf-8', errors='ignore')
                if '|DATA|' in metadata_str:
                    metadata_part = metadata_str.split('|DATA|')[0]
                    parts = metadata_part.split('|')
                    
                    version = parts[0].replace('v', '')
                    compressed = parts[1] == 'c1'
                    encrypted = parts[2] == 'e1'
                    method_info = parts[3]
                    
                    if method_info.startswith('r'):
                        method = 'random'
                        detected_seed = int(method_info[1:])
                        if seed is None:
                            seed = detected_seed
                    else:
                        method = 'sequential'
                    
                    print(f"✓ Detected: v{version}, {'encrypted' if encrypted else 'plain'}, "
                          f"{'compressed' if compressed else 'uncompressed'}, {method}")
                else:
                    # Fallback to sequential
                    method = 'sequential'
                    compressed = False
                    encrypted = False
            except:
                method = 'sequential'
                compressed = False
                encrypted = False
            
            # Decode all data
            if method == 'random':
                if seed is None:
                    return {'success': False, 'error': 'Seed required for random method'}
                all_bits = self.decode_lsb_random(img_array, img_array.size, seed)
            else:
                all_bits = self.decode_lsb_sequential(img_array, img_array.size)
            
            # Convert to bytes and find delimiter
            all_bytes = bytes(int(all_bits[i:i+8], 2) for i in range(0, len(all_bits), 8))
            
            delimiter_bytes = self.delimiter.encode()
            if delimiter_bytes in all_bytes:
                data_end = all_bytes.index(delimiter_bytes)
                
                # Extract data (skip metadata header)
                if b'|DATA|' in all_bytes[:data_end]:
                    data_start = all_bytes.index(b'|DATA|') + 6
                    data = all_bytes[data_start:data_end]
                else:
                    data = all_bytes[:data_end]
                
                # Decrypt if needed
                if encrypted:
                    if password is None:
                        return {'success': False, 'error': 'Password required'}
                    try:
                        data = self.decrypt_data(data, password)
                        print(f"✓ Decrypted successfully")
                    except:
                        return {'success': False, 'error': 'Wrong password or corrupted data'}
                
                # Decompress if needed
                if compressed:
                    data = self.decompress_data(data)
                    print(f"✓ Decompressed successfully")
                
                message = data.decode('utf-8')
                
                return {
                    'success': True,
                    'message': message,
                    'length': len(message),
                    'encrypted': encrypted,
                    'compressed': compressed,
                    'method': method
                }
            else:
                return {'success': False, 'error': 'No valid message found'}
                
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    # ==================== File Hiding Methods ====================
    
    def encode_file(self, image_path, file_path, output_path, password=None, compress=True):
        """
        Hide an entire file inside an image
        
        Args:
            image_path: Path to cover image
            file_path: Path to file to hide
            output_path: Path to save encoded image
            password: Optional password
            compress: Whether to compress
            
        Returns:
            dict: Status and metadata
        """
        try:
            # Read file
            with open(file_path, 'rb') as f:
                file_data = f.read()
            
            filename = os.path.basename(file_path)
            
            # Create file package: filename_length|filename|file_data
            filename_bytes = filename.encode('utf-8')
            package = len(filename_bytes).to_bytes(2, 'big') + filename_bytes + file_data
            
            # Add file header
            package = self.file_header.encode() + package
            
            print(f"✓ Preparing file: {filename} ({len(file_data)} bytes)")
            
            # Compress if requested
            if compress:
                package = self.compress_data(package)
                print(f"✓ Compressed: {len(file_data)} → {len(package)} bytes")
            
            # Encrypt if password provided
            if password:
                package = self.encrypt_data(package, password)
                print(f"✓ Encrypted with AES-256")
            
            # Use encode_message infrastructure
            result = self.encode_message(
                image_path,
                package.decode('latin1'),  # Treat as text temporarily
                output_path,
                password=None,  # Already encrypted
                compress=False,  # Already compressed
                method='sequential'
            )
            
            if result['success']:
                result['file_hidden'] = filename
                result['file_size'] = len(file_data)
            
            return result
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def decode_file(self, image_path, output_dir, password=None):
        """
        Extract hidden file from image
        
        Args:
            image_path: Path to encoded image
            output_dir: Directory to save extracted file
            password: Password if encrypted
            
        Returns:
            dict: Status and file info
        """
        try:
            # Decode as message first
            result = self.decode_message(image_path, password)
            
            if not result['success']:
                return result
            
            # Convert message back to bytes
            data = result['message'].encode('latin1')
            
            # Check for file header
            if not data.startswith(self.file_header.encode()):
                return {'success': False, 'error': 'Not a file-encoded image'}
            
            # Parse file package
            data = data[len(self.file_header):]
            filename_length = int.from_bytes(data[:2], 'big')
            filename = data[2:2+filename_length].decode('utf-8')
            file_data = data[2+filename_length:]
            
            # Save file
            os.makedirs(output_dir, exist_ok=True)
            output_path = os.path.join(output_dir, filename)
            
            with open(output_path, 'wb') as f:
                f.write(file_data)
            
            return {
                'success': True,
                'filename': filename,
                'output_path': output_path,
                'file_size': len(file_data)
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    # ==================== Analysis Methods ====================
    
    def analyze_image(self, image_path):
        """
        Analyze image for steganography capacity and characteristics
        
        Returns:
            dict: Image analysis results
        """
        try:
            img = Image.open(image_path).convert('RGB')
            img_array = np.array(img)
            
            # Calculate statistics
            total_pixels = img_array.shape[0] * img_array.shape[1]
            total_bits = total_pixels * 3
            max_chars = (total_bits // 8) - 100  # Reserve for metadata
            max_kb = max_chars / 1024
            
            # LSB analysis (check for anomalies)
            flat = img_array.flatten()
            lsb_distribution = np.bincount(flat & 1, minlength=2)
            lsb_ratio = lsb_distribution[1] / len(flat) if len(flat) > 0 else 0
            
            # Ideal ratio is ~0.5, significant deviation might indicate hidden data
            suspicious = abs(lsb_ratio - 0.5) > 0.05
            
            return {
                'dimensions': f"{img_array.shape[1]}x{img_array.shape[0]}",
                'pixels': total_pixels,
                'max_chars': max_chars,
                'max_kb': f"{max_kb:.2f} KB",
                'lsb_ratio': f"{lsb_ratio:.4f}",
                'suspicious': suspicious,
                'suspicion_level': 'High' if suspicious else 'Low'
            }
            
        except Exception as e:
            return {'error': str(e)}


def main():
    """Interactive CLI for PixelVault Enhanced"""
    vault = PixelVaultEnhanced()
    
    print("=" * 70)
    print("     PixelVault Enhanced - Advanced Steganography Security Tool")
    print("=" * 70)
    print()
    
    while True:
        print("\n🔐 Main Menu:")
        print("1. Encode message (with encryption)")
        print("2. Decode message")
        print("3. Hide file in image")
        print("4. Extract file from image")
        print("5. Analyze image")
        print("6. Exit")
        print()
        
        choice = input("Select option (1-6): ").strip()
        
        if choice == '1':
            print("\n--- Encode Message ---")
            image_path = input("Cover image path: ").strip()
            message = input("Secret message: ").strip()
            
            use_password = input("Use password? (y/n): ").strip().lower() == 'y'
            password = input("Enter password: ").strip() if use_password else None
            
            use_compress = input("Compress message? (y/n): ").strip().lower() == 'y'
            
            method = input("Method (sequential/random): ").strip().lower()
            if method not in ['sequential', 'random']:
                method = 'sequential'
            
            output_path = input("Output image path: ").strip()
            
            result = vault.encode_message(
                image_path, message, output_path,
                password=password, compress=use_compress, method=method
            )
            
            if result['success']:
                print(f"\n✓ Success!")
                print(f"  Output: {result['output']}")
                print(f"  Capacity used: {result['capacity_used']}")
                if 'seed' in result:
                    print(f"  ⚠️  SEED: {result['seed']} (SAVE THIS!)")
            else:
                print(f"\n✗ Error: {result['error']}")
        
        elif choice == '2':
            print("\n--- Decode Message ---")
            image_path = input("Encoded image path: ").strip()
            
            use_password = input("Password protected? (y/n): ").strip().lower() == 'y'
            password = input("Enter password: ").strip() if use_password else None
            
            use_seed = input("Random method used? (y/n): ").strip().lower() == 'y'
            seed = int(input("Enter seed: ").strip()) if use_seed else None
            
            result = vault.decode_message(image_path, password=password, seed=seed)
            
            if result['success']:
                print(f"\n✓ Message decoded!")
                print(f"\n{'='*60}")
                print(result['message'])
                print('='*60)
            else:
                print(f"\n✗ Error: {result['error']}")
        
        elif choice == '3':
            print("\n--- Hide File ---")
            image_path = input("Cover image path: ").strip()
            file_path = input("File to hide: ").strip()
            output_path = input("Output image path: ").strip()
            
            use_password = input("Use password? (y/n): ").strip().lower() == 'y'
            password = input("Enter password: ").strip() if use_password else None
            
            result = vault.encode_file(image_path, file_path, output_path, password=password)
            
            if result['success']:
                print(f"\n✓ File hidden successfully!")
                print(f"  File: {result['file_hidden']}")
                print(f"  Size: {result['file_size']} bytes")
            else:
                print(f"\n✗ Error: {result['error']}")
        
        elif choice == '4':
            print("\n--- Extract File ---")
            image_path = input("Encoded image path: ").strip()
            output_dir = input("Output directory: ").strip()
            
            use_password = input("Password protected? (y/n): ").strip().lower() == 'y'
            password = input("Enter password: ").strip() if use_password else None
            
            result = vault.decode_file(image_path, output_dir, password=password)
            
            if result['success']:
                print(f"\n✓ File extracted!")
                print(f"  File: {result['filename']}")
                print(f"  Saved to: {result['output_path']}")
            else:
                print(f"\n✗ Error: {result['error']}")
        
        elif choice == '5':
            print("\n--- Analyze Image ---")
            image_path = input("Image path: ").strip()
            
            result = vault.analyze_image(image_path)
            
            if 'error' not in result:
                print(f"\n📊 Image Analysis:")
                print(f"  Dimensions: {result['dimensions']}")
                print(f"  Pixels: {result['pixels']:,}")
                print(f"  Capacity: {result['max_chars']:,} characters ({result['max_kb']})")
                print(f"  LSB Ratio: {result['lsb_ratio']}")
                print(f"  Suspicion: {result['suspicion_level']}")
            else:
                print(f"\n✗ Error: {result['error']}")
        
        elif choice == '6':
            print("\nExiting PixelVault Enhanced. Stay secure! 🔒")
            break


if __name__ == "__main__":
    main()
# JPEGVault - JPEG Steganography Module

## Overview

`JPEGVault` provides steganography for JPEG images using **DCT (Discrete Cosine Transform) coefficient modification**. Unlike traditional LSB pixel modification (which fails on JPEG due to lossy compression), this approach directly modifies the frequency domain coefficients.

## Why DCT Coefficients?

### The Problem with LSB on JPEG

```python
#  This FAILS with JPEG:
modify_pixel_LSB(image)  # Pixel change
save_as_JPEG(image)      # Compression destroys changes!
```

### DCT Solution

```python
#  This WORKS:
dct_coeffs = read_jpeg_dct(image)  # Get frequency coefficients
modify_dct_LSB(dct_coeffs)         # Change coefficient LSBs
write_jpeg_dct(dct_coeffs)         # Data survives recompression!
```

## Features

- **AES-256 encryption** (same as PixelVault Layer 1)
- 📊 **Capacity analysis** - Check before encoding
- 🎯 **AC coefficient targeting** - Skips DC, uses robust ACs
- 🔍 **Auto-detection** - Metadata tracks encryption status
- ⚡ **Quality preservation** - Minimal visual impact

## Installation

```bash
pip install jpegio

# Note: Requires libjpeg development headers
# Ubuntu/Debian: sudo apt-get install libjpeg-dev
# macOS: brew install jpeg
```

## Usage

### Basic Encoding

```python
from jpeg_vault import JPEGVault

vault = JPEGVault()

# Encode message
vault.encode_message(
    "photo.jpg",
    "Secret message",
    "stego.jpg"
)

# Decode message
result = vault.decode_message("stego.jpg")
print(result['message'])  # "Secret message"
```

### With Encryption

```python
# Encode with password
vault.encode_message(
    "photo.jpg",
    "Top secret data",
    "stego.jpg",
    password="MyPassword123"
)

# Decode with password
result = vault.decode_message("stego.jpg", password="MyPassword123")
```

### Check Capacity

```python
capacity = vault.get_capacity("photo.jpg")
print(f"Can hide: {capacity['usable_bytes']} bytes")
```

## How It Works

### 1. DCT Coefficient Extraction

```
JPEG Image → 8x8 Blocks → DCT Coefficients
                           ↓
              [DC, AC1, AC2, AC3, ...]
```

### 2. Embeddable Coefficient Selection

- **Skip DC coefficient** (block average - too visible)
- **Use AC coefficients** (high-frequency details)
- **Filter zero coefficients** (preserve compression)

### 3. LSB Modification

```
Original coefficient: 127 (01111111₂)
Message bit: 0
Modified:  126 (01111110₂)  ← LSB changed
```

### 4. Survival Through Re-compression

DCT coefficients are quantized, not pixels  
 LSB changes survive JPEG save/load cycles  
 Data persists even after quality adjustments

## API Reference

### `encode_message(jpeg_path, message, output_path, password=None)`

Encode a message in a JPEG image.

**Returns:**

```python
{
    'success': True,
    'output': 'stego.jpg',
    'message_size': 50,
    'encoded_size': 82,  # With encryption overhead
    'capacity_used': '12.5%',
    'encrypted': True
}
```

### `decode_message(jpeg_path, password=None)`

Decode a message from a JPEG image.

**Returns:**

```python
{
    'success': True,
    'message': 'Secret data',
    'length': 11,
    'encrypted': True
}
```

### `get_capacity(jpeg_path)`

Calculate JPEG steganography capacity.

**Returns:**

```python
{
    'total_bits': 48000,
    'total_bytes': 6000,
    'usable_bytes': 5975,  # After overhead
    'overhead_bytes': 25,
    'image_size': '640x480'
}
```

## Comparison: PNG vs JPEG

| Feature     | PixelVault (PNG) | JPEGVault (JPEG)    |
| ----------- | ---------------- | ------------------- |
| Method      | Pixel LSB        | DCT Coefficient LSB |
| Compression | Lossless         | Lossy-resistant     |
| Capacity    | High             | Medium              |
| Complexity  | Low              | Medium              |
| Speed       | Fast             | Moderate            |
| Visibility  | Invisible        | Invisible           |

## Technical Details

### DCT Block Structure

```
8x8 Block:
┌─────────┬───────────────┐
│   DC    │  AC (horizontal)
├─────────┼───────────────┤
│ AC      │  AC (diagonal)
│ (vert)  │  AC (high-freq)
└─────────┴───────────────┘

Embeddable: AC coefficients only (non-zero)
```

### Metadata Format

```
JPG:1.0:E|<encrypted_data><<JPEG_END>>
│   │   │
│   │   └─ Flag (E=Encrypted, P=Plain)
│   └───── Version
└───────── Format marker
```

### Security

- **Encryption:** AES-256-CBC
- **Key Derivation:** PBKDF2 (100K iterations, SHA-256)
- **Salt:** 16 random bytes
- **IV:** 16 random bytes

## Limitations

1. **Quality dependency:** Lower JPEG quality = less capacity
2. **Re-compression risk:** Saving with different quality may corrupt data
3. **Size overhead:** Encryption adds ~32 bytes
4. **Library dependency:** Requires jpegio (C extension)

## Testing

```bash
python test_jpeg.py
```

Tests include:

- Capacity calculation
- Plain text encoding/decoding
- Encrypted encoding/decoding
- Wrong password detection
- Size limit validation

## License & Credits

Uses `jpegio` library for DCT coefficient access.  
Encryption layer compatible with PixelVault Layer 1.

---

**Status:** Production-ready for JPEG steganography!

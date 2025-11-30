

import os
from main_copy import PixelVault
from PIL import Image
import math
def upscale_cover_to_fit(cover_path: str, required_bits: int) -> str:
    """
    Upscale the cover image so that it can hold at least required_bits bits.
    Returns the path to the new upscaled image.
    """
    # 3 embeddable bits per pixel (R,G,B)
    pixels_needed = math.ceil(required_bits / 3)
    side = math.ceil(math.sqrt(pixels_needed))

    print(f"\n[Auto-upscale] Need at least {required_bits} bits.")
    print(f"[Auto-upscale] Targeting ~{pixels_needed} pixels (~{side}x{side}).")

    img = Image.open(cover_path).convert("RGB")
    upscaled = img.resize((side, side), Image.LANCZOS)

    base, ext = os.path.splitext(cover_path)
    upscaled_path = f"{base}_upscaled_{side}x{side}.png"
    upscaled.save(upscaled_path, "PNG")

    print(f"[Auto-upscale] Upscaled cover saved as: {upscaled_path}")
    return upscaled_path



def print_header():
    print("=" * 60)
    print("      PixelVault - Manual File Steganography Tester")
    print("=" * 60)
    print("This tool lets you:")
    print("  1) Hide a SECRET image inside a COVER image")
    print("  2) Extract a hidden file from a stego image\n")


def prompt_path(prompt_text: str) -> str:
    while True:
        path = input(prompt_text).strip().strip('"').strip("'")
        if os.path.exists(path):
            return path
        print(f" Path not found: {path}")
        retry = input("  Try again? (y/n): ").strip().lower()
        if retry != "y":
            return None


def encode_flow(vault: PixelVault):
    print("\n--- ENCODE: Hide secret image inside cover image ---")

    cover_path = prompt_path("Enter COVER image path (PNG/JPEG): ")
    if not cover_path:
        print("Aborting encode.")
        return

    secret_path = prompt_path("Enter SECRET image (or any file) to hide: ")
    if not secret_path:
        print("Aborting encode.")
        return

    output_path = input("Enter OUTPUT image path (e.g., stego.png): ").strip()
    if not output_path:
        output_path = "stego.png"
        print(f"  Using default output path: {output_path}")

    use_password = input("Encrypt hidden file with password? (y/n): ").strip().lower() == "y"
    password = None
    if use_password:
        password = input("Enter password: ").strip()
        if not password:
            print("Empty password entered, encoding WITHOUT encryption.")
            password = None

    print("\nEncoding, please wait...")
    success = vault.encode_file(
        image_path=cover_path,
        file_path=secret_path,
        output_path=output_path,
        password=password,
    )

    if success:
        print("\nENCODE SUCCESS")
        print(f"  Cover image : {cover_path}")
        print(f"  Secret file : {secret_path}")
        print(f"  Stego image : {output_path}")
        return

    # If we reach here, encode_file returned False (most often: cover too small)
    print("\nENCODE FAILED.")
    retry = input(
        "Cover image might be too small. Auto-upscale cover and retry? (y/n): "
    ).strip().lower()

    if retry != "y":
        print("Skipping auto-upscale.")
        return

    # 1) Compute how many bits the file actually needs (with metadata + optional encryption)
    required_bits = vault.estimate_bits_for_file(secret_path, password=password)

    # 2) Compute current capacity (for info)
    current_capacity = vault.get_image_capacity_bits(cover_path)
    print(f"[Info] Current capacity: {current_capacity} bits")
    print(f"[Info] Required bits   : {required_bits} bits")

    if required_bits <= current_capacity:
        print(
            "Note: required bits <= current capacity – failure may be due to another error."
        )

    # 3) Upscale cover to just big enough to fit
    upscaled_cover = upscale_cover_to_fit(cover_path, required_bits)

    # 4) Retry encoding with upscaled cover
    print("\nRetrying encoding with upscaled cover...")
    success2 = vault.encode_file(
        image_path=upscaled_cover,
        file_path=secret_path,
        output_path=output_path,
        password=password,
    )

    if success2:
        print("\nENCODE SUCCESS (after auto-upscale)")
        print(f"  Original cover : {cover_path}")
        print(f"  Upscaled cover : {upscaled_cover}")
        print(f"  Secret file    : {secret_path}")
        print(f"  Stego image    : {output_path}")
    else:
        print("\nENCODE FAILED again – see errors above.")



def decode_flow(vault: PixelVault):
    print("\n--- DECODE: Extract hidden file from stego image ---")

    stego_path = prompt_path("Enter STEGO image path: ")
    if not stego_path:
        print("Aborting decode.")
        return

    output_dir = input("Enter OUTPUT directory for recovered file (default: ./recovered): ").strip()
    if not output_dir:
        output_dir = "./recovered"

    use_password = input("Was the file encrypted with a password? (y/n): ").strip().lower() == "y"
    password = None
    if use_password:
        password = input("Enter password: ").strip()

    print("\nDecoding, please wait...")
    result_path = vault.decode_file(
        image_path=stego_path,
        password=password,
        output_dir=output_dir,
    )

    if result_path:
        print("\n DECODE SUCCESS")
        print(f"  Recovered file saved to: {result_path}")
    else:
        print("\nDECODE FAILED, check console logs above for details.")


def main():
    print_header()
    vault = PixelVault()

    while True:
        print("\nOptions:")
        print("  1. Encode (hide secret image/file inside cover image)")
        print("  2. Decode (extract hidden file from stego image)")
        print("  3. Exit")

        choice = input("\nSelect an option (1-3): ").strip()

        if choice == "1":
            encode_flow(vault)
        elif choice == "2":
            decode_flow(vault)
        elif choice == "3":
            print("\nExiting manual tester.")
            break
        else:
            print("Invalid option, please choose 1, 2, or 3.")


if __name__ == "__main__":
    main()

from fastapi import APIRouter

router = APIRouter()

@router.post("/encode")
async def encode_message(message: str, image_path: str = None):
    # TODO: implement encode using steg_encode.py
    return {
        "success": True,
        "message": "Steganography encode placeholder"
    }

@router.post("/decode")
async def decode_message(image_path: str):
    # TODO: implement decode using steg_decode.py
    return {
        "success": True,
        "message": "Steganography decode placeholder"
    }

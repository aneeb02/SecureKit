from pyzbar.pyzbar import decode
import cv2
import numpy as np

def decode_qr_from_bytes(file_bytes):
    npimg = np.frombuffer(file_bytes, np.uint8)
    img = cv2.imdecode(npimg, cv2.IMREAD_COLOR)

    decoded = decode(img)
    if not decoded:
        return None
    
    return decoded[0].data.decode("utf-8")

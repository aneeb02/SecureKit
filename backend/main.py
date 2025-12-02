from fastapi import FastAPI

# Import routers
from modules.qr_shield.router import router as qr_router
from modules.phishy_wishy.router import router as phishing_router
from modules.pixel_vault.router import router as pixel_router

app = FastAPI(
    title="SecureKit API",
    description="Security Toolkit with QRShield, PhishyWishy, and PixelVault",
    version="1.0.0"
)

app.include_router(qr_router, prefix="/qrshield", tags=["QR Shield"])
app.include_router(phishing_router, prefix="/phishywishy", tags=["Phishy Wishy"])
app.include_router(pixel_router, prefix="/pixelvault", tags=["Pixel Vault"])


@app.get("/")
def root():
    return {"message": "SecureKit Backend Running"}
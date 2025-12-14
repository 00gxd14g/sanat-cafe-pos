from __future__ import annotations

import base64
from pathlib import Path

from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding
from fastapi import APIRouter, HTTPException
from fastapi.responses import PlainTextResponse

from app.core.config import settings

router = APIRouter(prefix="/api/qz", tags=["qz"])


def _load_private_key():
    key_path = Path(settings.qz_private_key_path)
    if not key_path.exists():
        raise HTTPException(status_code=500, detail=f"Missing private key: {key_path}")
    try:
        return serialization.load_pem_private_key(key_path.read_bytes(), password=None)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to load private key: {e}")


@router.get("/cert", response_class=PlainTextResponse)
def qz_cert():
    cert_path = Path(settings.qz_public_cert_path)
    if not cert_path.exists():
        raise HTTPException(status_code=500, detail=f"Missing public certificate: {cert_path}")
    return cert_path.read_text(encoding="utf-8", errors="replace")


@router.post("/sign")
def qz_sign(payload: dict):
    to_sign = (payload or {}).get("toSign", "")
    if not isinstance(to_sign, str) or not to_sign:
        raise HTTPException(status_code=400, detail="toSign is required")

    private_key = _load_private_key()
    sig = private_key.sign(to_sign.encode("utf-8"), padding.PKCS1v15(), hashes.SHA256())
    return {"signature": base64.b64encode(sig).decode("ascii")}


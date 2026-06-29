import os
from pathlib import Path
import cloudinary
import cloudinary.uploader

_config_applied = False


def _load_dotenv():
    """Load .env file manually (no dependency needed)"""
    env_path = Path(__file__).resolve().parent / ".env"
    if not env_path.exists():
        return

    with open(env_path, "r") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue

            if "=" in line:
                key, value = line.split("=", 1)
                os.environ[key.strip()] = value.strip()


def _configure_cloudinary():
    global _config_applied

    if _config_applied:
        return True

    _load_dotenv()

    cloud_name = os.getenv("CLOUDINARY_CLOUD_NAME")
    api_key = os.getenv("CLOUDINARY_API_KEY")
    api_secret = os.getenv("CLOUDINARY_API_SECRET")

    if cloud_name and api_key and api_secret:
        cloudinary.config(
            cloud_name=cloud_name,
            api_key=api_key,
            api_secret=api_secret,
            secure=True
        )
        _config_applied = True
        return True

    return False

def is_cloudinary_configured():
    return _configure_cloudinary()


def upload_to_cloudinary(file):
    if not is_cloudinary_configured():
        raise Exception("Cloudinary not configured")

    result = cloudinary.uploader.upload(file)
    return result["secure_url"]
from pathlib import Path

# Model configuration
MODEL_PATH = "best.pt"

# Upload directory
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

# Static files directory
STATIC_DIR = Path("static")
STATIC_DIR.mkdir(exist_ok=True)
